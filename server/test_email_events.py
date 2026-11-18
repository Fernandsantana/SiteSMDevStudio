import base64
import hashlib
import hmac
import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

try:
    from .email_events import EmailEventReceiver
except ImportError:
    try:
        from server.email_events import EmailEventReceiver
    except ImportError:
        from email_events import EmailEventReceiver


class EmailEventReceiverTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.now = 1_800_000_000
        self.key = b"a test signing key"
        self.secret = "whsec_" + base64.b64encode(self.key).decode("ascii")
        self.db_path = Path(self.temp.name) / "events.sqlite3"
        self.receiver = EmailEventReceiver(self.secret, self.db_path, clock=lambda: self.now)
        self.payload = {
            "id": "evt_123", "type": "email.delivered", "created_at": "2026-10-23T12:00:00Z",
            "data": {"email_id": "mail_456", "from": "Malu <nao-responda@appmalu.com>",
                     "to": ["private@example.net"], "subject": "SECRET_SUBJECT", "text": "SECRET_BODY"},
        }
        self.body = json.dumps(self.payload, separators=(",", ":")).encode()

    def headers(self, *, stamp=None, message_id="msg_1", body=None, signature_extra=""):
        stamp = str(self.now if stamp is None else stamp)
        signed = message_id.encode() + b"." + stamp.encode() + b"." + (body or self.body)
        signature = base64.b64encode(hmac.new(self.key, signed, hashlib.sha256).digest()).decode()
        return {"Svix-Id": message_id, "Svix-Timestamp": stamp,
                "Svix-Signature": f"v1,{signature}{signature_extra}"}

    def test_valid_signature_persists_allowlisted_metadata_only(self):
        self.assertEqual(self.receiver.process(self.body, self.headers()), (200, {"ok": True}))
        self.assertEqual(self.receiver.summary()["by_type"]["delivered"], 1)
        with closing(sqlite3.connect(self.db_path)) as db:
            columns = {row[1] for row in db.execute("PRAGMA table_info(email_events)")}
            values = " ".join(str(value) for row in db.execute("SELECT * FROM email_events") for value in row)
        self.assertEqual(columns, {"webhook_id", "event_id", "email_id", "event_type", "event_at", "sender_domain", "received_at"})
        for private_value in ("private@example.net", "SECRET_SUBJECT", "SECRET_BODY", "nao-responda"):
            self.assertNotIn(private_value, values)
        self.assertIn("appmalu.com", values)

    def test_invalid_signature_and_expired_timestamp_are_rejected(self):
        bad = self.headers()
        bad["Svix-Signature"] = "v1,AAAA"
        self.assertEqual(self.receiver.process(self.body, bad)[0], 400)
        self.assertEqual(self.receiver.process(self.body, self.headers(stamp=self.now - 301))[0], 400)
        self.assertEqual(self.receiver.process(self.body, self.headers(stamp=self.now + 301))[0], 400)
        self.assertEqual(self.receiver.summary()["total"], 0)

    def test_standard_webhooks_aliases_are_supported(self):
        headers = self.headers()
        aliases = {key.replace("Svix", "Webhook"): value for key, value in headers.items()}
        self.assertEqual(self.receiver.process(self.body, aliases)[0], 200)

    def test_multiple_signatures_accept_any_valid_v1(self):
        headers = self.headers(signature_extra=" v1,AAAA v0,BBBB")
        self.assertEqual(self.receiver.process(self.body, headers)[0], 200)
        self.assertEqual(self.receiver.summary()["total"], 1)

    def test_webhook_id_is_deduplicated(self):
        self.receiver.process(self.body, self.headers())
        self.payload["id"] = "evt_different"
        second = json.dumps(self.payload, separators=(",", ":")).encode()
        self.assertEqual(self.receiver.process(second, self.headers(body=second))[0], 200)
        self.assertEqual(self.receiver.summary()["total"], 1)

    def record_event(self, email_id, kind, created_at, message_id):
        event = {"type": "email." + kind, "created_at": created_at,
                 "data": {"email_id": email_id, "from": "notify@appmalu.com"}}
        body = json.dumps(event, separators=(",", ":")).encode()
        return self.receiver.process(body, self.headers(message_id=message_id, body=body))

    def test_delayed_then_delivered_resolves_current_state_and_keeps_history(self):
        self.record_event("mail_resolved", "delivery_delayed", "2026-10-23T12:00:00.100Z", "msg_delay")
        self.record_event("mail_resolved", "delivered", "2026-10-23T12:00:01.200Z", "msg_delivered")
        summary = self.receiver.summary()
        self.assertEqual(summary["by_type"]["delivery_delayed"], 1)
        self.assertEqual(summary["by_type"]["delivered"], 1)
        self.assertEqual(summary["unresolved_by_type"]["delivery_delayed"], 0)
        self.assertEqual(summary["unresolved_by_type"]["delivered"], 0)
        self.assertNotIn("mail_resolved", json.dumps(summary))

    def test_event_time_order_beats_arrival_order_with_stable_ties(self):
        # The newer delivery arrives first. The older delay arrives later and
        # has a lexically greater webhook ID, so event time must decide state.
        self.record_event("mail_out_of_order", "delivered", "2026-10-23T12:00:00.456Z", "msg_a_new")
        self.record_event("mail_out_of_order", "delivery_delayed", "2026-10-23T12:00:00.123Z", "msg_z_old")
        summary = self.receiver.summary()
        self.assertEqual(summary["by_type"]["delivery_delayed"], 1)
        self.assertEqual(summary["unresolved_by_type"]["delivery_delayed"], 0)

        self.record_event("mail_tied", "delivered", "2026-10-23T12:00:00Z", "msg_tied_a")
        self.record_event("mail_tied", "delivery_delayed", "2026-10-23T12:00:00Z", "msg_tied_z")
        summary = self.receiver.summary()
        # Equal event times use webhook ID as a stable tie-breaker.
        self.assertEqual(summary["unresolved_by_type"]["delivery_delayed"], 1)

    def test_old_bounce_leaves_alert_window_and_recent_complaint_remains_a_problem(self):
        self.record_event("mail_bounced", "bounced", "2026-10-22T10:00:00Z", "msg_bounce")
        self.record_event("mail_complained", "delivered", "2026-10-23T10:00:00Z", "msg_delivery")
        self.record_event("mail_complained", "complained", "2026-10-23T10:01:00Z", "msg_complaint")
        self.now += 2 * 24 * 60 * 60
        summary = self.receiver.summary(since_seconds=3600)
        self.assertEqual(summary["total"], 0)
        self.assertEqual(summary["unresolved_by_type"]["bounced"], 0)
        self.assertEqual(summary["unresolved_by_type"]["complained"], 0)
        recent_summary = self.receiver.summary(since_seconds=3 * 24 * 60 * 60)
        self.assertEqual(recent_summary["unresolved_by_type"]["bounced"], 1)
        self.assertEqual(recent_summary["unresolved_by_type"]["complained"], 1)

    def test_body_limit(self):
        receiver = EmailEventReceiver(self.secret, Path(self.temp.name) / "small.sqlite3",
                                      max_body_bytes=4, clock=lambda: self.now)
        self.assertEqual(receiver.process(self.body, self.headers())[0], 413)

    def test_all_supported_event_types_accept_resend_payload_without_json_id(self):
        for index, kind in enumerate(("delivered", "bounced", "delivery_delayed", "complained", "failed")):
            event = {"type": "email." + kind, "created_at": "2026-10-23T12:00:00Z",
                     "data": {"email_id": f"mail_{index}", "from": "notify@smdevstudio.com",
                              "to": ["PII@example.net"], "subject": "PRIVATE"}}
            body = json.dumps(event, separators=(",", ":")).encode()
            headers = self.headers(message_id=f"msg_{index}", body=body)
            self.assertEqual(self.receiver.process(body, headers)[0], 200)
        summary = self.receiver.summary()
        self.assertEqual(summary["total"], 5)
        self.assertTrue(all(summary["by_type"][kind] == 1 for kind in
                            ("delivered", "bounced", "delivery_delayed", "complained", "failed")))
        with closing(sqlite3.connect(self.db_path)) as db:
            stored = " ".join(str(value) for row in db.execute("SELECT * FROM email_events") for value in row)
        self.assertNotIn("PII@example.net", stored)
        self.assertNotIn("PRIVATE", stored)

    def test_invalid_utf8_and_non_object_json_are_rejected(self):
        for body in (b"\\xff", b"[]", b"null", b"{bad json"):
            self.assertEqual(self.receiver.process(body, self.headers(body=body))[0], 400)

    def test_summary_connection_is_read_only(self):
        with self.receiver._database(readonly=True) as db:
            with self.assertRaises(sqlite3.OperationalError):
                db.execute("DELETE FROM email_events")

    def test_unpadded_whsec_secret_is_accepted(self):
        unpadded = "whsec_" + base64.b64encode(self.key).decode().rstrip("=")
        receiver = EmailEventReceiver(unpadded, Path(self.temp.name) / "unpadded.sqlite3",
                                      clock=lambda: self.now)
        self.assertEqual(receiver.process(self.body, self.headers())[0], 200)


if __name__ == "__main__":
    unittest.main()
