#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
command -v docker >/dev/null 2>&1 || { echo 'Docker não encontrado. Instale Docker Desktop ou Docker Engine com Compose v2.' >&2; exit 1; }
docker compose version >/dev/null
if [ ! -f .env ]; then
  command -v python3 >/dev/null 2>&1 || { echo 'Python 3 é necessário para criar a configuração inicial, ou copie .env.example para .env e defina POSTGRES_PASSWORD.' >&2; exit 1; }
  python3 - <<'PY'
from pathlib import Path
import secrets
value=Path('.env.example').read_text().replace('POSTGRES_PASSWORD=\n','POSTGRES_PASSWORD='+secrets.token_urlsafe(32)+'\n')
p=Path('.env');p.write_text(value);p.chmod(0o600)
PY
fi
docker compose up --build -d --wait --wait-timeout 180
printf '%s\n' 'NoirPDF pronto: http://localhost:3000' 'Para encerrar: docker compose down'
