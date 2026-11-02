# syntax=docker/dockerfile:1
FROM node:22-bookworm-slim AS web
WORKDIR /app
COPY package.json package-lock.json ./
COPY apps/web/package.json apps/web/package.json
RUN npm ci --cache /tmp/npm-cache && rm -rf /tmp/npm-cache
COPY apps/web ./apps/web
COPY packages ./packages
ENV API_URL=http://127.0.0.1:8000 NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM python:3.12-slim
# Server mode uses local Python PDF engines. Additional OCR/Office engines
# must be integrated and tested before being enabled in the catalog.
RUN apt-get update && apt-get install -y --no-install-recommends libstdc++6 ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=web /usr/local/bin/node /usr/local/bin/node
WORKDIR /app
COPY services/api/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY --from=web /app/node_modules ./node_modules
COPY --from=web /app/apps/web ./apps/web
COPY --from=web /app/packages ./packages
COPY services ./services
COPY infra/start-render.py ./infra/start-render.py
RUN groupadd -g 10001 noir && useradd -u 10001 -g noir noir && chown -R noir:noir /app/apps/web/.next
USER noir
ENV DATA_DIR=/tmp/noirpdf API_URL=http://127.0.0.1:8000 COOKIE_SECURE=true EXECUTOR=local MAX_CONCURRENT_TASKS=1 NEXT_TELEMETRY_DISABLED=1
CMD ["python","infra/start-render.py"]
