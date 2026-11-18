"""Site local e endpoint de contato. Sem dependências externas ou gravação de mensagens."""
import argparse
import getpass
import hashlib
import html
import json
import os
from pathlib import Path
import re
import smtplib
import ssl
import socket
import threading
import time
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
TO = 'contato@smdevstudio.com.br'
PUBLIC = {'index.html', 'privacidade.html', 'termos.html', '404.html', 'styles.css', 'script.js',
          'assets/logo-sm.png', 'assets/logo-sm-web.webp'} | {
    f'integracoes/backups-{app}/{page}.html' for app in ('matheo', 'malu')
    for page in ('index', 'privacidade', 'termos')}
TYPES = {'.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8',
         '.js': 'text/javascript; charset=utf-8', '.png': 'image/png', '.webp': 'image/webp'}
CSP = "default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self'; font-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'"


def validate(data):
    if not isinstance(data, dict):
        raise ValueError('Dados inválidos')
    result = {}
    for key, minimum, maximum in [('name', 2, 100), ('email', 3, 254), ('company', 0, 120), ('message', 10, 5000)]:
        value = data.get(key, '')
        if not isinstance(value, str):
            raise ValueError('Dados inválidos')
        value = value.strip()
        if not minimum <= len(value) <= maximum or '\x00' in value:
            raise ValueError('Confira os campos e os limites do formulário')
        if key != 'message' and any(c in value for c in '\r\n'):
            raise ValueError('Campo inválido')
        result[key] = value
    if not re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?\.[A-Za-z]{2,63}", result['email']):
        raise ValueError('Informe um e-mail válido')
    return result


def smtp_password():
    secret_path = os.environ.get('SMTP_PASSWORD_FILE')
    if secret_path:
        value = Path(secret_path).read_text(encoding='utf-8').rstrip('\r\n')
    else:
        value = os.environ.get('SMTP_PASSWORD', '')
    if not value:
        raise RuntimeError('SMTP não configurado')
    return value


def trusted_peer(peer, configured):
    if not configured:
        return False
    if peer == configured:
        return True
    try:
        return peer in {item[4][0] for item in socket.getaddrinfo(configured, None)}
    except OSError:
        return False


def send_mail(data):
    password = smtp_password()
    username = os.environ.get('SMTP_USER', TO)
    if not password:
        raise RuntimeError('SMTP não configurado')
    message = EmailMessage()
    message['From'] = f'SM Dev Studio <{username}>'
    message['To'] = TO  # O visitante nunca escolhe o destino ou o remetente SMTP
    message['Reply-To'] = data['email']
    message['Subject'] = 'Novo contato pelo site SM Dev Studio'
    message['Date'] = formatdate(localtime=False, usegmt=True)
    message['Message-ID'] = make_msgid(domain='smdevstudio.com.br')
    message.set_content(f"Nome: {data['name']}\nE-mail: {data['email']}\nEmpresa: {data['company'] or 'Não informada'}\n\n{data['message']}\n")
    with smtplib.SMTP_SSL('smtp.hostinger.com', 465, timeout=15, context=ssl.create_default_context()) as smtp:
        smtp.login(username, password)
        smtp.send_message(message)


class ContactServer(ThreadingHTTPServer):
    daemon_threads = True
    def __init__(self, address, *, preview=False, serve_static=True, origins=(), trusted_proxy='', sender=send_mail):
        super().__init__(address, Handler)
        self.preview, self.serve_static = preview, serve_static
        self.origins, self.trusted_proxy, self.sender = set(origins), trusted_proxy, sender
        self.guard = threading.Lock()
        self.rates, self.deliveries = {}, {}
        self.workers = threading.BoundedSemaphore(16)

    def process_request(self, request, address):
        if not self.workers.acquire(blocking=False):
            request.close()
            return
        try:
            super().process_request(request, address)
        except Exception:
            self.workers.release()
            raise

    def process_request_thread(self, request, address):
        try:
            super().process_request_thread(request, address)
        finally:
            self.workers.release()


class Handler(BaseHTTPRequestHandler):
    server_version = 'SMContact'
    sys_version = ''
    def setup(self):
        super().setup()
        self.connection.settimeout(20)

    def log_message(self, *_):
        pass  # Nunca registrar mensagem, senha, e-mail ou IP

    def respond(self, code, message, **extra):
        result = {'message': message, **extra}
        if 'application/json' in self.headers.get('Accept', ''):
            body = json.dumps(result, ensure_ascii=False).encode()
            mime = 'application/json; charset=utf-8'
        else:
            body = (f'<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                    f'<title>Contato · SM Dev Studio</title><link rel="stylesheet" href="/styles.css">'
                    f'<main class="shell section"><h1>Contato</h1><p role="status">{html.escape(message)}</p>'
                    '<p><a href="/index.html#contato">Voltar ao formulário</a></p>'
                    f'<p><a href="mailto:{TO}">{TO}</a></p></main></html>').encode()
            mime = 'text/html; charset=utf-8'
        self.output(code, body, mime)

    def output(self, code, body, mime):
        self.send_response(code)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', CSP)
        self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
        self.end_headers()
        if self.command != 'HEAD':
            self.wfile.write(body)

    def do_GET(self):
        path = unquote(urlsplit(self.path).path)
        if path == '/_health':
            return self.output(200, b'ok', 'text/plain')
        if not self.server.serve_static:
            return self.respond(404, 'Não encontrado')
        name = path.lstrip('/') or 'index.html'
        if name not in PUBLIC or not (ROOT / name).is_file():
            return self.output(404, (ROOT / '404.html').read_bytes(), TYPES['.html'])
        self.output(200, (ROOT / name).read_bytes(), TYPES[Path(name).suffix])

    do_HEAD = do_GET

    def do_POST(self):
        if urlsplit(self.path).path != '/api/contact':
            return self.respond(404, 'Não encontrado')
        origin = self.headers.get('Origin')
        referer = urlsplit(self.headers.get('Referer', ''))
        if not origin and referer.scheme and referer.netloc:
            origin = f'{referer.scheme}://{referer.netloc}'
        if origin not in self.server.origins:
            return self.respond(403, 'Origem não permitida')
        if self.headers.get('Transfer-Encoding'):
            return self.respond(400, 'Requisição inválida')
        try:
            length = int(self.headers.get('Content-Length', '0'))
        except ValueError:
            return self.respond(400, 'Requisição inválida')
        if not 0 < length <= 24576:
            return self.respond(413, 'Mensagem muito grande')
        mime = self.headers.get_content_type()
        if mime not in ('application/json', 'application/x-www-form-urlencoded'):
            return self.respond(415, 'Formato não suportado')
        try:
            raw = self.rfile.read(length).decode('utf-8')
            data = json.loads(raw) if mime == 'application/json' else {k: v[0] for k, v in parse_qs(raw, keep_blank_values=True, max_num_fields=12).items()}
            cleaned = validate(data)
            if data.get('website'):
                return self.respond(400, 'Não foi possível validar o formulário')
        except (ValueError, UnicodeError):
            return self.respond(400, 'Confira seu nome, e-mail e mensagem antes de enviar')
        peer = self.client_address[0]
        # Só confiar em cabeçalhos de IP quando vindos de um proxy explicitamente configurado
        ip = self.headers.get('X-Contact-IP', peer) if trusted_peer(peer, self.server.trusted_proxy) else peer
        identity = hashlib.sha256(ip.encode()).hexdigest()
        fingerprint = hashlib.sha256(json.dumps(cleaned, sort_keys=True).encode()).hexdigest()
        key = (identity, str(data.get('requestId', ''))[:100], fingerprint)
        now = time.monotonic()
        with self.server.guard:
            self.server.deliveries = {k: v for k, v in self.server.deliveries.items() if now - v[0] < 3600}
            self.server.rates = {k: [t for t in v if now - t < 600] for k, v in self.server.rates.items() if v and now - v[-1] < 600}
            previous = self.server.deliveries.get(key)
            if previous:
                if previous[1] == 'sent':
                    return self.respond(200, 'Mensagem enviada! Vamos responder pelo e-mail que você informou')
                return self.respond(409, 'Este envio ainda está sendo processado, aguarde um momento')
            attempts = self.server.rates.setdefault(identity, [])
            if len(attempts) >= 5 or sum(map(len, self.server.rates.values())) >= 50:
                return self.respond(429, 'Muitas tentativas, aguarde alguns minutos ou escreva diretamente por e-mail')
            attempts.append(now)
            if self.server.preview:
                return self.respond(200, 'Prévia local: formulário validado, nenhuma mensagem foi enviada', preview=True)
            self.server.deliveries[key] = (now, 'pending')
        try:
            self.server.sender(cleaned)
        except Exception:
            with self.server.guard:
                self.server.deliveries.pop(key, None)
            return self.respond(503, 'O envio está indisponível, tente novamente ou escreva para contato@smdevstudio.com.br')
        with self.server.guard:
            self.server.deliveries[key] = (now, 'sent')
        self.respond(200, 'Mensagem enviada! Vamos responder pelo e-mail que você informou')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5185)
    parser.add_argument('--bind', default='127.0.0.1')
    parser.add_argument('--preview', action='store_true', help='Valida sem enviar; resultado sempre identificado como prévia')
    parser.add_argument('--smtp', action='store_true', help='Solicita a senha em terminal, sem gravar')
    parser.add_argument('--api-only', action='store_true')
    args = parser.parse_args()
    if args.api_only:
        if args.preview or args.smtp:
            parser.error('Serviço de produção não aceita modos interativos ou de prévia')
        if not os.environ.get('SMTP_PASSWORD_FILE'):
            parser.error('Serviço de produção exige SMTP_PASSWORD_FILE')
        try:
            smtp_password()
        except (OSError, RuntimeError):
            parser.error('Segredo SMTP ausente, vazio ou inacessível')
        configured_origins = os.environ.get('CONTACT_ORIGINS', '').split(',')
        if not all(urlsplit(o).scheme == 'https' and urlsplit(o).netloc and urlsplit(o).path == '' for o in configured_origins):
            parser.error('CONTACT_ORIGINS deve conter origens HTTPS exatas, sem barra final')
    if args.preview and args.bind not in ('127.0.0.1', '::1'):
        parser.error('Prévia somente em loopback')
    if args.smtp:
        while True:
            password = getpass.getpass('Senha SMTP da caixa contato (não será salva): ')
            try:
                with smtplib.SMTP_SSL('smtp.hostinger.com', 465, timeout=15, context=ssl.create_default_context()) as smtp:
                    smtp.login(os.environ.get('SMTP_USER', TO), password)
            except smtplib.SMTPAuthenticationError as error:
                print(f'Autenticação recusada pela Hostinger (código {error.smtp_code}). Confira a credencial da caixa contato e tente novamente.', flush=True)
                continue
            except Exception as error:
                print(f'Não foi possível validar o SMTP ({type(error).__name__}). Tente novamente ou use Ctrl+C para encerrar.', flush=True)
                continue
            os.environ['SMTP_PASSWORD'] = password
            del password
            print('Autenticação SMTP confirmada pela Hostinger.', flush=True)
            break
    origins = os.environ.get('CONTACT_ORIGINS', f'http://127.0.0.1:{args.port},http://localhost:{args.port}').split(',')
    server = ContactServer((args.bind, args.port), preview=args.preview, serve_static=not args.api_only,
                           origins=origins, trusted_proxy=os.environ.get('CONTACT_TRUSTED_PROXY', ''))
    print(f'http://{args.bind}:{args.port} — ' + ('PRÉVIA SEM ENVIO' if args.preview else 'envio SMTP, exige credencial no servidor'), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
