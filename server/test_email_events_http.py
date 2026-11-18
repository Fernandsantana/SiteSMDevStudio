import base64
import hashlib
import hmac
import http.client
import json
import socket
import tempfile
import threading
import unittest
from pathlib import Path

try:
    from .email_events import EmailEventReceiver
    from .email_events_http import BoundedThreadingHTTPServer, EmailEventsHandler
except ImportError:
    try:
        from server.email_events import EmailEventReceiver
        from server.email_events_http import BoundedThreadingHTTPServer, EmailEventsHandler
    except ImportError:
        from email_events import EmailEventReceiver
        from email_events_http import BoundedThreadingHTTPServer, EmailEventsHandler


class EmailEventsHTTPTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.now = 1_800_000_000
        self.key = b"http test signing key"
        self.secret = "whsec_" + base64.b64encode(self.key).decode()
        self.receiver = EmailEventReceiver(self.secret, Path(self.temp.name) / "events.sqlite3",
                                           clock=lambda: self.now)
        self.server = BoundedThreadingHTTPServer(("127.0.0.1", 0), EmailEventsHandler,
                                                receiver=self.receiver, max_workers=2)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.close_server)
        self.address = self.server.server_address
        self.body = json.dumps({"type": "email.bounced", "created_at": "2026-10-23T12:00:00Z",
                                "data": {"email_id": "mail_http", "from": "service@smdevstudio.com",
                                         "to": ["private@example.net"], "subject": "SECRET"}},
                               separators=(",", ":")).encode()
        self.webhook_headers = self.signed_headers(self.body)

    def close_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def signed_headers(self, body, *, message_id="msg_http", timestamp=None):
        timestamp = str(self.now if timestamp is None else timestamp)
        signed = message_id.encode() + b"." + timestamp.encode() + b"." + body
        signature = base64.b64encode(hmac.new(self.key, signed, hashlib.sha256).digest()).decode()
        return {"Svix-Id": message_id, "Svix-Timestamp": timestamp,
                "Svix-Signature": "v1," + signature}

    def request(self, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection(*self.address, timeout=3)
        connection.request(method, path, body=body, headers=headers or {})
        response = connection.getresponse()
        result = response.status, response.read(), dict(response.getheaders())
        connection.close()
        return result

    def post_headers(self, body, signature_headers=None):
        return {"Content-Type": "application/json", **(signature_headers or self.signed_headers(body))}

    def test_health_and_private_aggregate_summary(self):
        self.assertEqual(self.request("GET", "/_health")[0], 200)
        self.assertEqual(self.request("POST", "/api/email-events/resend", self.body,
                                      self.post_headers(self.body))[0], 200)
        status, body, _ = self.request("GET", "/_summary")
        summary = json.loads(body)
        self.assertEqual(status, 200)
        self.assertEqual(summary["total"], 1)
        for private_value in ("mail_http", "private@example.net", "SECRET", "service@smdevstudio.com"):
            self.assertNotIn(private_value, body.decode())

    def test_signed_delivery_is_idempotent_and_invalid_signature_rejected(self):
        headers = self.post_headers(self.body, self.webhook_headers)
        self.assertEqual(self.request("POST", "/api/email-events/resend", self.body, headers)[0], 200)
        self.assertEqual(self.request("POST", "/api/email-events/resend", self.body, headers)[0], 200)
        bad_headers = dict(headers)
        bad_headers["Svix-Signature"] = "v1,AAAA"
        self.assertEqual(self.request("POST", "/api/email-events/resend", self.body, bad_headers)[0], 400)
        self.assertEqual(self.receiver.summary()["total"], 1)

    def test_rejects_wrong_mime_and_transfer_encoding(self):
        wrong_type = {**self.post_headers(self.body), "Content-Type": "text/plain"}
        self.assertEqual(self.request("POST", "/api/email-events/resend", self.body, wrong_type)[0], 415)
        chunked = {**self.post_headers(self.body), "Transfer-Encoding": "chunked"}
        self.assertEqual(self.request("POST", "/api/email-events/resend", self.body, chunked)[0], 400)

        duplicate_mime = socket.create_connection(self.address, timeout=3)
        duplicate_mime.sendall(b"POST /api/email-events/resend HTTP/1.1\r\nHost: localhost\r\n"
                               b"Content-Type: application/json\r\nContent-Type: text/plain\r\n"
                               b"Content-Length: 2\r\nConnection: close\r\n\r\n{}")
        response = duplicate_mime.recv(512)
        duplicate_mime.close()
        self.assertIn(b"415", response)

    def test_rejects_duplicate_content_length_and_short_body(self):
        duplicate = socket.create_connection(self.address, timeout=3)
        duplicate.sendall(b"POST /api/email-events/resend HTTP/1.1\r\nHost: localhost\r\n"
                          b"Content-Type: application/json\r\nContent-Length: 1\r\nContent-Length: 1\r\n"
                          b"Connection: close\r\n\r\nx")
        response = duplicate.recv(512)
        duplicate.close()
        self.assertIn(b"400", response)

        invalid = socket.create_connection(self.address, timeout=3)
        invalid.sendall(b"POST /api/email-events/resend HTTP/1.1\r\nHost: localhost\r\n"
                        b"Content-Type: application/json\r\nContent-Length: 1x\r\n"
                        b"Connection: close\r\n\r\nx")
        response = invalid.recv(512)
        invalid.close()
        self.assertIn(b"400", response)

        short = socket.create_connection(self.address, timeout=3)
        short.sendall(b"POST /api/email-events/resend HTTP/1.1\r\nHost: localhost\r\n"
                      b"Content-Type: application/json\r\nContent-Length: 50\r\nConnection: close\r\n\r\n{}")
        short.shutdown(socket.SHUT_WR)
        response = short.recv(512)
        short.close()
        self.assertIn(b"400", response)


if __name__ == "__main__":
    unittest.main()
