import json
import os
import threading
import unittest
import tempfile
from pathlib import Path
from http.client import HTTPConnection
from unittest.mock import patch
from urllib.parse import urlencode

from contact import ContactServer, TO, send_mail, validate, smtp_password, trusted_peer

DATA = dict(name='Teste local', email='teste@example.com', company='', message='Mensagem de teste local', requestId='teste-1')


class ContactTests(unittest.TestCase):
    def test_secret_file_precedes_environment_and_preserves_spaces(self):
        with tempfile.TemporaryDirectory() as folder:
            secret = Path(folder) / 'smtp.secret'
            secret.write_text(' fake password \n', encoding='utf-8')
            with patch.dict(os.environ, {'SMTP_PASSWORD_FILE': str(secret), 'SMTP_PASSWORD': 'wrong'}):
                self.assertEqual(smtp_password(), ' fake password ')
                secret.write_text('', encoding='utf-8')
                with self.assertRaises(RuntimeError):
                    smtp_password()

    def test_proxy_trust_is_explicit(self):
        self.assertFalse(trusted_peer('127.0.0.1', ''))
        self.assertTrue(trusted_peer('127.0.0.1', '127.0.0.1'))
        with patch('contact.socket.getaddrinfo', return_value=[(2, 1, 6, '', ('172.20.0.2', 0))]):
            self.assertTrue(trusted_peer('172.20.0.2', 'web'))
            self.assertFalse(trusted_peer('172.20.0.3', 'web'))

    def setUp(self):
        self.sent = []
        self.server = ContactServer(('127.0.0.1', 0), origins=['http://localhost'], sender=self.sent.append)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def request(self, data=None, origin='http://localhost', path='/api/contact', method='POST', form=False):
        conn = HTTPConnection('127.0.0.1', self.server.server_port, timeout=3)
        body = urlencode(data) if form else json.dumps(DATA if data is None else data)
        conn.request(method, path, body.encode(), {'Origin': origin, 'Accept': 'text/html' if form else 'application/json', 'Content-Type': 'application/x-www-form-urlencoded' if form else 'application/json'})
        response = conn.getresponse()
        result = response.status, response.read().decode()
        conn.close()
        return result

    def test_success_and_duplicate_do_not_send_twice(self):
        self.assertEqual(self.request()[0], 200)
        self.assertEqual(self.request()[0], 200)
        self.assertEqual(len(self.sent), 1)

    def test_invalid_data_and_header_injection(self):
        for changes in ({'name': 'x'}, {'email': 'a@example.com\r\nBcc: x@example.com'}, {'message': 'curta'}, {'email': 'invalido'}):
            self.assertEqual(self.request(DATA | changes)[0], 400)
        self.assertFalse(self.sent)

    def test_wrong_origin(self):
        self.assertEqual(self.request(origin='https://outro.example')[0], 403)
        self.assertFalse(self.sent)

    def test_trap(self):
        self.assertEqual(self.request(DATA | {'website': 'spam'})[0], 400)
        self.assertFalse(self.sent)

    def test_large_request(self):
        self.assertEqual(self.request(DATA | {'message': 'a' * 25000})[0], 413)

    def test_rate_limit(self):
        for i in range(5):
            self.assertEqual(self.request(DATA | {'requestId': str(i)})[0], 200)
        self.assertEqual(self.request(DATA | {'requestId': 'six'})[0], 429)

    def test_delivery_failure_is_not_success(self):
        def fail(_):
            raise RuntimeError('sensitive error')
        self.server.sender = fail
        status, body = self.request()
        self.assertEqual(status, 503)
        self.assertNotIn('sensitive', body)

    def test_preview_never_sends(self):
        self.server.preview = True
        status, body = self.request()
        self.assertEqual(status, 200)
        self.assertTrue(json.loads(body)['preview'])
        self.assertFalse(self.sent)

    def test_no_javascript_submission(self):
        status, body = self.request(DATA, form=True)
        self.assertEqual(status, 200)
        self.assertIn('Mensagem enviada!', body)
        self.assertEqual(len(self.sent), 1)

    def test_private_files_are_not_served(self):
        for path in ('/.env', '/server/contact.py', '/README.md', '/../README.md'):
            self.assertEqual(self.request(path=path, method='GET')[0], 404)
        self.assertEqual(self.request(path='/index.html', method='GET')[0], 200)

    @patch.dict(os.environ, {'SMTP_PASSWORD': 'fake-local-test', 'SMTP_USER': TO})
    @patch('contact.smtplib.SMTP_SSL')
    def test_smtp_destination_and_reply_to(self, smtp):
        send_mail(validate(DATA | {'to': 'other@example.com'}))
        message = smtp.return_value.__enter__.return_value.send_message.call_args.args[0]
        self.assertEqual(message['To'], TO)
        self.assertEqual(message['Reply-To'], DATA['email'])
        self.assertIn(TO, message['From'])


if __name__ == '__main__':
    unittest.main()
