# syntax=docker/dockerfile:1
FROM python:3.12-slim
WORKDIR /app
COPY services/api/requirements.txt /tmp/requirements.txt
RUN --mount=type=secret,id=proxy_ca if [ -f /run/secrets/proxy_ca ]; then PIP_CERT=/run/secrets/proxy_ca pip install --no-cache-dir -r /tmp/requirements.txt; else pip install --no-cache-dir -r /tmp/requirements.txt; fi
RUN groupadd -g 10001 noir && useradd -u 10001 -g noir noir && mkdir /data && chown noir:noir /data
COPY services ./services
COPY packages/shared ./packages/shared
USER noir
ENV DATA_DIR=/data PYTHONDONTWRITEBYTECODE=1
CMD ["uvicorn","services.api.main:app","--host","0.0.0.0","--port","8000","--no-access-log"]
