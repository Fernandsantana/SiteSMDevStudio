"""Privacy-preserving Resend webhook receiver using the Svix v1 signature."""
from __future__ import annotations

import base64
import binascii
from contextlib import contextmanager
import hashlib
import hmac
import json
import os
import re
import sqlite3
import time
from datetime import datetime, timezone
from email.utils import parseaddr
from pathlib import Path
from typing import Callable, Mapping

EVENT_TYPES = frozenset({"delivered", "bounced", "delivery_delayed", "complained", "failed"})
DEFAULT_SENDER_DOMAINS = frozenset({"smdevstudio.com", "appmalu.com"})
RETENTION_SECONDS = 90 * 24 * 60 * 60
MAX_EVENTS = 10_000
DEFAULT_MAX_BODY_BYTES = 256 * 1024


class EmailEventReceiver:
    """Verify signatures and store only bounded, allowlisted event metadata.

    ``process(raw_body, headers)`` returns an HTTP ``(status, JSON-payload)`` pair.
    """

    def __init__(self, secret: str, database_path: str | os.PathLike[str], *,
                 allowed_sender_domains=DEFAULT_SENDER_DOMAINS,
                 max_body_bytes: int = DEFAULT_MAX_BODY_BYTES,
                 clock: Callable[[], float] = time.time):
        if not isinstance(secret, str) or not secret.startswith("whsec_"):
            raise ValueError("Webhook secret must use the whsec_ format")
        try:
            encoded_key = secret[6:].replace("-", "+").replace("_", "/")
            encoded_key += "=" * (-len(encoded_key) % 4)
            key = base64.b64decode(encoded_key, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ValueError("Invalid webhook secret encoding") from exc
        if not key:
            raise ValueError("Webhook secret cannot be empty")
        if type(max_body_bytes) is not int or max_body_bytes <= 0:
            raise ValueError("max_body_bytes must be positive")
        domains = frozenset(str(domain).strip().lower().rstrip(".") for domain in allowed_sender_domains)
        if not domains:
            raise ValueError("At least one sender domain is required")
        self._key = key
        self._database_path = str(database_path)
        self._allowed_sender_domains = domains
        self._max_body_bytes = max_body_bytes
        self._clock = clock
        self._initialize()

    def _connect(self, *, readonly: bool = False):
        if readonly:
            uri = Path(self._database_path).resolve().as_uri() + "?mode=ro"
            return sqlite3.connect(uri, uri=True, timeout=5, isolation_level=None)
        return sqlite3.connect(self._database_path, timeout=5, isolation_level=None)

    @contextmanager
    def _database(self, *, readonly: bool = False):
        db = self._connect(readonly=readonly)
        try:
            yield db
        finally:
            db.close()

    def _initialize(self):
        path = Path(self._database_path)
        if self._database_path != ":memory:":
            path.parent.mkdir(parents=True, exist_ok=True)
        with self._database() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("""CREATE TABLE IF NOT EXISTS email_events (
                webhook_id TEXT PRIMARY KEY,
                event_id TEXT NOT NULL,
                email_id TEXT NOT NULL,
                event_type TEXT NOT NULL CHECK(event_type IN
                    ('delivered','bounced','delivery_delayed','complained','failed')),
                event_at TEXT NOT NULL,
                sender_domain TEXT NOT NULL,
                received_at INTEGER NOT NULL
            )""")
            db.execute("CREATE INDEX IF NOT EXISTS email_events_received ON email_events(received_at)")

    @staticmethod
    def _headers(headers: Mapping[str, str]) -> dict[str, str]:
        try:
            return {str(key).lower(): str(value) for key, value in headers.items()}
        except (AttributeError, TypeError):
            return {}

    def _valid_signature(self, body: bytes, headers: Mapping[str, str], now: float) -> bool:
        normalized = self._headers(headers)
        # Resend's documented Svix headers are the defaults. Svix also supports
        # webhook-* aliases for endpoints configured with white-labeled headers.
        message_id = normalized.get("svix-id") or normalized.get("webhook-id", "")
        timestamp = normalized.get("svix-timestamp") or normalized.get("webhook-timestamp", "")
        signatures = normalized.get("svix-signature") or normalized.get("webhook-signature", "")
        if not message_id or len(message_id) > 200 or not re.fullmatch(r"[A-Za-z0-9_.:-]+", message_id):
            return False
        if not re.fullmatch(r"[0-9]{1,12}", timestamp):
            return False
        if abs(now - int(timestamp)) > 300:
            return False
        if not signatures or len(signatures) > 4096:
            return False
        signed = message_id.encode() + b"." + timestamp.encode("ascii") + b"." + body
        expected = hmac.new(self._key, signed, hashlib.sha256).digest()
        matched = False
        for item in signatures.split():
            version, separator, encoded = item.partition(",")
            if version != "v1" or not separator:
                continue
            try:
                candidate = base64.b64decode(encoded, validate=True)
            except (binascii.Error, ValueError):
                candidate = b""
            matched |= hmac.compare_digest(expected, candidate)
        return matched

    @staticmethod
    def _event_time(value) -> str | None:
        if not isinstance(value, str) or len(value) > 64:
            return None
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                return None
            return parsed.astimezone(timezone.utc).isoformat(timespec="auto")
        except (ValueError, OverflowError):
            return None

    def process(self, body: bytes, headers: Mapping[str, str]) -> tuple[int, dict[str, object]]:
        """Validate one untouched HTTP body and return a generic response."""
        if not isinstance(body, bytes):
            return 400, {"ok": False}
        if len(body) > self._max_body_bytes:
            return 413, {"ok": False}
        now = self._clock()
        if not self._valid_signature(body, headers, now):
            return 400, {"ok": False}
        try:
            event = json.loads(body.decode("utf-8"))
            if not isinstance(event, dict) or not isinstance(event.get("data"), dict):
                raise ValueError
            data = event["data"]
            email_id, kind = data.get("email_id"), event.get("type")
            if not all(isinstance(v, str) and 1 <= len(v) <= 200 for v in (email_id, kind)):
                raise ValueError
            payload_id = event.get("id")
            if payload_id is not None and (not isinstance(payload_id, str) or not 1 <= len(payload_id) <= 200):
                raise ValueError
            event_id = payload_id or (self._headers(headers).get("svix-id") or
                                      self._headers(headers).get("webhook-id"))
            kind = kind.removeprefix("email.")
            if kind not in EVENT_TYPES:
                return 200, {"ok": True}
            event_at = self._event_time(event.get("created_at"))
            sender = data.get("from")
            if event_at is None or not isinstance(sender, str) or len(sender) > 512:
                raise ValueError
            _, address = parseaddr(sender)
            if "@" not in address:
                return 200, {"ok": True}
            domain = address.rsplit("@", 1)[1].rstrip(".").lower()
            if domain not in self._allowed_sender_domains:
                return 200, {"ok": True}
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError, TypeError, RecursionError):
            return 400, {"ok": False}

        normalized_headers = self._headers(headers)
        webhook_id = normalized_headers.get("svix-id") or normalized_headers["webhook-id"]
        received = int(now)
        try:
            with self._database() as db:
                db.execute("BEGIN IMMEDIATE")
                db.execute("DELETE FROM email_events WHERE received_at < ?", (received - RETENTION_SECONDS,))
                db.execute("""INSERT OR IGNORE INTO email_events
                    (webhook_id,event_id,email_id,event_type,event_at,sender_domain,received_at)
                    VALUES (?,?,?,?,?,?,?)""",
                    (webhook_id, event_id, email_id, kind, event_at, domain, received))
                db.execute("""DELETE FROM email_events WHERE webhook_id IN
                    (SELECT webhook_id FROM email_events ORDER BY received_at DESC, webhook_id DESC
                     LIMIT -1 OFFSET ?)""", (MAX_EVENTS,))
                db.commit()
        except sqlite3.Error:
            return 500, {"ok": False}
        return 200, {"ok": True}

    def summary(self, *, since_seconds: int = 86_400) -> dict[str, object]:
        """Return aggregate counts and latest time without event or address IDs."""
        if type(since_seconds) is not int or since_seconds < 0:
            raise ValueError("since_seconds must be a non-negative integer")
        cutoff = int(self._clock()) - since_seconds
        with self._database(readonly=True) as db:
            rows = db.execute("""SELECT event_type, COUNT(*) AS count, MAX(event_at) AS latest_at
                FROM email_events WHERE received_at >= ? GROUP BY event_type""", (cutoff,)).fetchall()
            current_rows = db.execute("""SELECT email_id, event_type FROM email_events
                WHERE received_at >= ?
                ORDER BY event_at DESC, webhook_id DESC""", (cutoff,)).fetchall()
        counts = {kind: 0 for kind in sorted(EVENT_TYPES)}
        unresolved = {kind: 0 for kind in sorted(EVENT_TYPES)}
        latest = None
        total = 0
        for kind, count, latest_at in rows:
            counts[kind] = count
            total += count
            if latest_at and (latest is None or latest_at > latest):
                latest = latest_at
        seen_email_ids = set()
        unresolved_types = {"bounced", "complained", "delivery_delayed", "failed"}
        for email_id, event_type in current_rows:
            if email_id in seen_email_ids:
                continue
            seen_email_ids.add(email_id)
            if event_type in unresolved_types:
                unresolved[event_type] += 1
        return {"window_seconds": since_seconds, "total": total, "by_type": counts,
                "unresolved_by_type": unresolved, "latest_at": latest}
