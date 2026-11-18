"""Ensaio isolado local; usa segredo fictício e nunca solicita envio SMTP."""
import json
import base64
import hashlib
import hmac
import os
from pathlib import Path
import subprocess
import tempfile
import shutil
import time
import uuid
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from empacotar import PUBLIC

ROOT = Path(__file__).resolve().parents[1]
scratch = ROOT / '.local'
scratch.mkdir(exist_ok=True)


def run(*args, **kwargs):
    return subprocess.run(args, check=True, text=True, **kwargs)


if any(os.environ.get(key) for key in ('DOCKER_HOST', 'DOCKER_CONTEXT', 'COMPOSE_FILE', 'COMPOSE_PROJECT_NAME')):
    raise SystemExit('Remova overrides Docker/Compose antes do ensaio local.')
context = json.loads(run('docker', 'context', 'inspect', capture_output=True).stdout)[0]
if not context['Endpoints']['docker']['Host'].startswith(('npipe:', 'unix:')):
    raise SystemExit('O ensaio exige Docker local.')
project = 'smds-check-' + uuid.uuid4().hex[:12]

with tempfile.TemporaryDirectory(prefix='smtp-release-', dir=scratch) as folder:
    work = Path(folder)
    secret = work / 'dummy.secret'
    secret.write_text('TEST-ONLY-NOT-A-CREDENTIAL', encoding='utf-8')
    event_key = b'local-test-key-never-use-in-production'
    event_secret = work / 'events.secret'
    event_secret.write_text('whsec_' + base64.b64encode(event_key).decode())
    data = work / 'data'
    data.mkdir()
    public = work / 'public'
    for name in PUBLIC:
        target = public / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    override = work / 'override.json'
    override.write_text(json.dumps({
        'services': {'web': {'ports': ['127.0.0.1::8080'], 'networks': {'ensaio': {}}, 'healthcheck': {'interval': '2s'}},
                     'contact': {'healthcheck': {'interval': '2s'}},
                     'email-events': {'healthcheck': {'interval': '2s'}}},
        'networks': {'entrada': {'name': project + '-entrada'}, 'ensaio': {}, 'smtp_saida': {'internal': True}}
    }), encoding='utf-8')
    env = os.environ.copy()
    env.update(SM_SITE_IMAGE=run('docker', 'image', 'inspect', '--format', '{{.Id}}', 'smdevstudio-site:local-final', capture_output=True).stdout.strip(),
               SM_CONTACT_IMAGE=run('docker', 'image', 'inspect', '--format', '{{.Id}}', 'smdevstudio-contact:local-final', capture_output=True).stdout.strip(),
               SM_EMAIL_EVENTS_IMAGE=run('docker', 'image', 'inspect', '--format', '{{.Id}}', 'smdevstudio-email-events:local-vps', capture_output=True).stdout.strip(),
               SM_EMAIL_EVENTS_SECRET_FILE=str(event_secret), SM_EMAIL_EVENTS_DATA_DIR=str(data),
               SM_RELEASE_DIR=str(public), SM_SMTP_SECRET_FILE=str(secret),
               CONTACT_ORIGINS='https://smdevstudio.com.br', SM_TRUSTED_PROXY_CIDRS='127.0.0.1/32')
    compose = ['docker', 'compose', '-p', project, '-f', str(ROOT / 'infra/compose.yaml'),
               '-f', str(ROOT / 'infra/compose.events.yaml'), '-f', str(override)]
    def check(path, expected, method='GET', origin='https://smdevstudio.com.br', body=b'{}', headers=None):
        req = Request(base_url + path, data=body if method == 'POST' else None,
                      method=method, headers={'Origin': origin, 'Accept': 'application/json', 'Content-Type': 'application/json', **(headers or {})})
        try:
            response = urlopen(req, timeout=5)
        except HTTPError as error:
            response = error
        with response:
            assert response.status == expected, (path, response.status, expected)
            if path == '/index.html' and expected == 200:
                assert "connect-src 'self'" in response.headers['Content-Security-Policy']
                assert b'id="contact-form"' in response.read()
        print(f'OK {method} {path}: {expected}')
    try:
        run(*compose, 'config', '--quiet', env=env)
        run(*compose, 'up', '-d', '--wait', '--wait-timeout', '60', env=env)
        address = run(*compose, 'port', 'web', '8080', env=env, capture_output=True).stdout.strip()
        base_url = 'http://' + address
        check('/index.html', 200)
        check('/_health', 200)
        check('/api/contact', 405)
        check('/api/contact', 403, 'POST', origin='https://outro.example')
        check('/api/contact', 400, 'POST')
        check('/api/contact', 413, 'POST', body=b'x' * 25000)
        check('/index.html', 405, 'POST')
        for path in ('/.env', '/server/contact.py', '/run/secrets/smtp_password', '/infra/compose.yaml'):
            check(path, 404)
        check('/_summary', 404)
        check('/api/email-events/resend', 405)
        check('/api/email-events/resend', 400, 'POST')
        timestamp = str(int(time.time()))
        body = json.dumps({'type': 'email.delivered', 'created_at': '2026-11-18T12:00:00Z',
                           'data': {'email_id': 'local-fixture', 'from': 'teste@appmalu.com'}}).encode()
        signature = base64.b64encode(hmac.new(event_key, b'local-message.' + timestamp.encode() + b'.' + body, hashlib.sha256).digest()).decode()
        headers = {'svix-id': 'local-message', 'svix-timestamp': timestamp, 'svix-signature': 'v1,' + signature}
        check('/api/email-events/resend', 200, 'POST', body=body, headers=headers)
        check('/api/email-events/resend', 200, 'POST', body=body, headers=headers)
        run(*compose, 'exec', '-T', 'email-events', 'python', '-c',
            "import json,urllib.request; s=json.load(urllib.request.urlopen('http://127.0.0.1:8082/_summary')); assert s['total']==1 and s['by_type']['delivered']==1", env=env)
        run(*compose, 'exec', '-T', 'contact', 'python', '-c',
            "import os; from contact import smtp_password; assert os.getuid()==10001; assert 'SMTP_PASSWORD' not in os.environ; assert smtp_password()=='TEST-ONLY-NOT-A-CREDENTIAL'", env=env)
        print('OK segredo somente por arquivo e processo sem root; nenhum envio SMTP realizado')
    finally:
        run(*compose, 'down', '--remove-orphans', env=env)
