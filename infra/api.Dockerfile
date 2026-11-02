# syntax=docker/dockerfile:1
FROM python:3.12-slim
WORKDIR /app
COPY services/api/requirements.txt /tmp/requirements.txt
COPY scripts/install-system-engines.sh scripts/install-verapdf.sh ./scripts/
RUN --mount=type=secret,id=proxy_ca if [ -f /run/secrets/proxy_ca ]; then export CURL_CA_BUNDLE=/run/secrets/proxy_ca; fi; sh scripts/install-system-engines.sh
RUN --mount=type=secret,id=proxy_ca if [ -f /run/secrets/proxy_ca ]; then PIP_CERT=/run/secrets/proxy_ca pip install --no-cache-dir -r /tmp/requirements.txt; else pip install --no-cache-dir -r /tmp/requirements.txt; fi
RUN groupadd -g 10001 noir && useradd -u 10001 -g noir noir && mkdir /data && chown noir:noir /data
COPY --chown=noir:noir services ./services
COPY --chown=noir:noir packages/shared ./packages/shared
USER noir
ENV DATA_DIR=/data PYTHONDONTWRITEBYTECODE=1 VERAPDF_BIN=/opt/verapdf/verapdf CHROMIUM_BIN=/usr/bin/chromium HTML_ENABLED=true HTML_CHROMIUM_SANDBOX=false GSETTINGS_BACKEND=memory SAL_USE_VCLPLUGIN=svp
CMD ["uvicorn","services.api.main:app","--host","0.0.0.0","--port","8000","--no-access-log"]
