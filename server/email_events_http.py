"""Bounded HTTP adapter for the isolated Resend email event receiver."""
from __future__ import annotations

import json
import os
import re
import socket
import sqlite3
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Mapping

try:  # Works both as ``python email_events_http.py`` in the image and as a package.
    from .email_events import DEFAULT_MAX_BODY_BYTES, EmailEventReceiver
except ImportError:
    from email_events import DEFAULT_MAX_BODY_BYTES, EmailEventReceiver

WEBHOOK_PATH = "/api/email-events/resend"
MAX_WORKERS = 16
REQUEST_TIMEOUT_SECONDS = 10


class BoundedThreadingHTTPServer(ThreadingHTTPServer):
    """Threading server with a hard cap on active request handler threads."""

    daemon_threads = True
    block_on_close = True
    request_queue_size = 32

    def __init__(self, server_address, handler_class, *, receiver: EmailEventReceiver,
                 max_workers: int = MAX_WORKERS):
        if type(max_workers) is not int or max_workers < 1:
            raise ValueError("max_workers must be a positive integer")
        self.receiver = receiver
        self._worker_slots = threading.BoundedSemaphore(max_workers)
        super().__init__(server_address, handler_class)

    def process_request(self, request, client_address):
        if not self._worker_slots.acquire(blocking=False):
            try:
                request.settimeout(1)
                request.sendall(b"HTTP/1.1 503 Service Unavailable\r\nContent-Length: 0\r\nConnection: close\r\n\r\n")
            except OSError:
                pass
            finally:
                self.shutdown_request(request)
            return
        try:
            super().process_request(request, client_address)
        except Exception:
            self._worker_slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self._worker_slots.release()

    def handle_error(self, request, client_address):
        # Request bodies, header values, and client supplied data must not reach logs.
        return


class EmailEventsHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "EmailEvents"
    sys_version = ""

    def setup(self):
        super().setup()
        self.connection.settimeout(REQUEST_TIMEOUT_SECONDS)

    def log_message(self, format, *args):
        # Suppress default request-line logging, which can contain attacker input.
        return

    def send_error(self, code, message=None, explain=None):
        # BaseHTTPRequestHandler may echo malformed request details in its HTML.
        self._respond(code, {"ok": False})

    def _respond(self, status: int, payload: Mapping[str, object] | None = None):
        body = b"" if payload is None else json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response_only(status)
        if payload is not None:
            self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "close")
        self.end_headers()
        if body:
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError, socket.timeout):
                pass
        self.close_connection = True

    def do_GET(self):
        if self.path == "/_health":
            self._respond(200, {"ok": True})
        elif self.path == "/_summary":
            try:
                self._respond(200, self.server.receiver.summary())
            except (OSError, sqlite3.Error, ValueError):
                self._respond(503, {"ok": False})
        else:
            self._respond(404, {"ok": False})

    def do_POST(self):
        if self.path != WEBHOOK_PATH:
            self._respond(404, {"ok": False})
            return
        if self.headers.get_all("Transfer-Encoding"):
            self._respond(400, {"ok": False})
            return
        lengths = self.headers.get_all("Content-Length")
        if not lengths or len(lengths) != 1 or not re.fullmatch(r"[0-9]{1,12}", lengths[0].strip()):
            self._respond(400, {"ok": False})
            return
        body_length = int(lengths[0])
        if body_length > DEFAULT_MAX_BODY_BYTES:
            self._respond(413, {"ok": False})
            return
        content_types = self.headers.get_all("Content-Type")
        if not content_types or len(content_types) != 1:
            self._respond(415, {"ok": False})
            return
        content_type = content_types[0].split(";", 1)[0].strip().lower()
        if content_type != "application/json":
            self._respond(415, {"ok": False})
            return
        try:
            body = self.rfile.read(body_length)
        except (OSError, socket.timeout):
            self._respond(400, {"ok": False})
            return
        if len(body) != body_length:
            self._respond(400, {"ok": False})
            return
        try:
            status, payload = self.server.receiver.process(body, self.headers)
        except Exception:
            # Do not log or echo parser, SQLite, payload, or header errors.
            status, payload = 500, {"ok": False}
        self._respond(status, payload)

    def do_PUT(self):
        self._respond(405, {"ok": False})

    do_PATCH = do_PUT
    do_DELETE = do_PUT
    do_OPTIONS = do_PUT


def _required_path(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is required")
    return value


def build_receiver_from_environment() -> EmailEventReceiver:
    secret_path = Path(_required_path("EMAIL_EVENTS_SECRET_FILE"))
    secret = secret_path.read_text(encoding="utf-8").rstrip("\r\n")
    database_path = _required_path("EMAIL_EVENTS_DB")
    return EmailEventReceiver(secret, database_path, max_body_bytes=DEFAULT_MAX_BODY_BYTES)


def serve(receiver: EmailEventReceiver, *, bind: str = "127.0.0.1", port: int = 8082):
    server = BoundedThreadingHTTPServer((bind, port), EmailEventsHandler, receiver=receiver)
    try:
        server.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main():
    receiver = build_receiver_from_environment()
    bind = os.environ.get("EMAIL_EVENTS_BIND", "127.0.0.1")
    try:
        port = int(os.environ.get("EMAIL_EVENTS_PORT", "8082"))
    except ValueError as exc:
        raise RuntimeError("EMAIL_EVENTS_PORT must be an integer") from exc
    if not 1 <= port <= 65535:
        raise RuntimeError("EMAIL_EVENTS_PORT must be between 1 and 65535")
    serve(receiver, bind=bind, port=port)


if __name__ == "__main__":
    main()
