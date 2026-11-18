"""Empacota apenas os arquivos públicos e verifica links e integridade."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from datetime import datetime, timezone
import hashlib, json, zipfile, argparse

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ['index.html', 'privacidade.html', 'termos.html', '404.html', 'styles.css', 'script.js', 'assets/logo-sm.png', 'assets/logo-sm-web.webp'] + [f'integracoes/backups-{product}/{page}.html' for product in ('malu', 'matheo') for page in ('index', 'privacidade', 'termos')]
PRIVATE = ['server/contact.py', 'server/test_contact.py', 'server/Dockerfile', 'server/.dockerignore',
           'server/email_events.py', 'server/test_email_events.py',
           'server/email_events_http.py', 'server/test_email_events_http.py', 'server/Dockerfile.events',
           'scripts/coletar-eventos-email.py',
           'infra/compose.yaml', 'infra/Caddyfile', 'infra/Dockerfile', 'infra/runtime.env.example',
           'infra/compose.events.yaml', 'infra/email-events-monitor.service', 'infra/email-events-monitor.timer',
           'infra/caddy/go.mod', 'infra/caddy/go.sum', 'infra/caddy/main.go', '.dockerignore',
           'CONTATO.md', 'PUBLICACAO.md', 'infra/CLOUDFLARE.md', 'scripts/validar_containers.py']

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.refs = []; self.ids = set()
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs: self.ids.add(attrs['id'])
        self.refs.extend(attrs[k] for k in ('href', 'src') if k in attrs)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--destino', type=Path, required=True)
    args = parser.parse_args()
    destination = args.destino.resolve()
    if destination == ROOT or ROOT in destination.parents:
        raise SystemExit('Use um destino fora do repositório para evitar publicação de artefatos.')
    pages = {}
    for name in PUBLIC:
        path = ROOT / name
        if not path.is_file() or path.is_symlink(): raise SystemExit(f'Fonte inválida: {name}')
        if path.suffix == '.html':
            page = Page(); page.feed(path.read_text(encoding='utf-8')); pages[name] = page
    for name, page in pages.items():
        for ref in page.refs:
            url = urlsplit(ref)
            if url.scheme or url.netloc: continue
            target = (ROOT / url.path.lstrip('/') if url.path.startswith('/') else ROOT / Path(name).parent / unquote(url.path)) if url.path else ROOT / name
            relative = target.resolve().relative_to(ROOT).as_posix()
            if relative not in PUBLIC: raise SystemExit(f'Link fora do pacote em {name}: {ref}')
            if url.fragment and url.fragment not in pages.get(relative, Page()).ids: raise SystemExit(f'Âncora inválida: {ref}')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    out = destination / ('candidata-' + stamp); out.mkdir(parents=True, exist_ok=False)
    archive = out / 'site-publico.zip'
    manifest = {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in PUBLIC}
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED) as z:
        for name in PUBLIC: z.write(ROOT/name, name)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert set(z.namelist()) == set(PUBLIC)
        assert all(hashlib.sha256(z.read(n)).hexdigest() == sha for n,sha in manifest.items())
    service = out / 'servico-contato.zip'
    service_manifest = {}
    with zipfile.ZipFile(service, 'x', zipfile.ZIP_DEFLATED) as z:
        for name in PRIVATE:
            path = ROOT / name
            if not path.is_file() or path.is_symlink(): raise SystemExit(f'Fonte inválida: {name}')
            service_manifest[name] = hashlib.sha256(path.read_bytes()).hexdigest()
            z.write(path, name)
    with zipfile.ZipFile(service) as z:
        assert z.testzip() is None and set(z.namelist()) == set(PRIVATE)
        assert all(hashlib.sha256(z.read(n)).hexdigest() == sha for n, sha in service_manifest.items())
    (out/'manifesto.json').write_text(json.dumps({'estado':'candidata local com SMTP; não publicada; segredo de produção não incluído','publico':manifest,'servico_privado':service_manifest},ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in (archive, service)),encoding='ascii')
    (out/'PUBLICACAO.md').write_bytes((ROOT/'PUBLICACAO.md').read_bytes())
    (out/'CONTATO.md').write_bytes((ROOT/'CONTATO.md').read_bytes())
    print(f'Pacote conferido: {archive}\n{len(PUBLIC)} arquivos públicos; links e hashes válidos.')

if __name__ == '__main__': main()
