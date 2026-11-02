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
RUN groupadd -g 10001 noir && useradd -u 10001 -g noir noir
# Full local engines. The free hosting tier may lack memory for large jobs.
WORKDIR /app
COPY scripts/install-system-engines.sh scripts/install-verapdf.sh ./scripts/
RUN sh scripts/install-system-engines.sh
COPY --from=web /usr/local/bin/node /usr/local/bin/node
WORKDIR /app
COPY services/api/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY --from=web --chown=noir:noir /app/node_modules ./node_modules
COPY --from=web --chown=noir:noir /app/apps/web ./apps/web
COPY --from=web --chown=noir:noir /app/packages ./packages
COPY --chown=noir:noir services ./services
COPY --chown=noir:noir infra/start-render.py ./infra/start-render.py
USER noir
ENV VERAPDF_BIN=/opt/verapdf/verapdf CHROMIUM_BIN=/usr/bin/chromium HTML_ENABLED=true HTML_CHROMIUM_SANDBOX=false GSETTINGS_BACKEND=memory SAL_USE_VCLPLUGIN=svp
ENV DATA_DIR=/tmp/noirpdf API_URL=http://127.0.0.1:8000 COOKIE_SECURE=true EXECUTOR=local MAX_CONCURRENT_TASKS=1 NEXT_TELEMETRY_DISABLED=1
CMD ["python","infra/start-render.py"]
