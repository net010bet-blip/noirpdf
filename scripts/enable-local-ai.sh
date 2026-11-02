#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
[ -f .env ] || { echo 'Execute scripts/start.sh primeiro para criar .env.' >&2; exit 1; }
echo 'Iniciando Ollama local. O modelo qwen2.5:1.5b será baixado (aproximadamente 1 GB). Reserve pelo menos 8 GB de RAM para o conjunto.'
docker compose -f compose.yaml -f infra/compose.ai.yaml --profile ai up -d --wait --wait-timeout 120 ollama
docker compose -f compose.yaml -f infra/compose.ai.yaml --profile ai exec -T ollama ollama pull qwen2.5:1.5b
python3 - <<'PY'
from pathlib import Path
p=Path('.env');rows=p.read_text().splitlines();updates={'AI_BASE_URL':'http://ollama:11434/v1','AI_MODEL':'qwen2.5:1.5b','AI_MAX_INPUT_CHARS':'12000','AI_MAX_OUTPUT_TOKENS':'2048'}
for k,v in updates.items():
 found=False
 for i,row in enumerate(rows):
  if row.startswith(k+'='):rows[i]=k+'='+v;found=True
 if not found:rows.append(k+'='+v)
p.write_text('\n'.join(rows)+'\n');p.chmod(0o600)
PY
docker compose -f compose.yaml -f infra/compose.ai.yaml --profile ai up -d --wait --wait-timeout 180 api worker scheduler web
echo 'Provedor local configurado. Teste um documento curto; velocidade e qualidade dependem do modelo e do computador.'
