"""Publica somente o estado agregado no contrato do monitor operacional existente."""
import json
import os
from pathlib import Path
import subprocess
import time


def main():
    destination = Path('/var/lib/entrada-produtos/monitor/eventos-email.json')
    result = {'situacao': 'Falha', 'instante': time.time()}
    try:
        response = subprocess.run([
            'docker', 'exec', 'smdevstudio-site-email-events-1', 'python', '-c',
            "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8082/_summary',timeout=5).read().decode())",
        ], capture_output=True, text=True, timeout=15, check=True)
        summary = json.loads(response.stdout)
        unresolved = summary['unresolved_by_type']
        if not all(type(value) is int and value >= 0 for value in unresolved.values()):
            raise ValueError('Invalid summary')
        result['situacao'] = 'Ok' if not any(unresolved.values()) else 'Falha'
        result['eventosPendentes'] = sum(unresolved.values())
    except (OSError, subprocess.SubprocessError, ValueError, KeyError, TypeError):
        pass
    temporary = destination.with_suffix('.tmp')
    temporary.write_text(json.dumps(result), encoding='utf-8')
    temporary.chmod(0o600)
    os.replace(temporary, destination)


if __name__ == '__main__':
    main()
