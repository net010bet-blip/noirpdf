# syntax=docker/dockerfile:1
FROM node:22-bookworm-slim
WORKDIR /app
RUN chown node:node /app
USER node
COPY --chown=node:node package.json package-lock.json ./
COPY --chown=node:node apps/web/package.json apps/web/package.json
RUN --mount=type=secret,id=proxy_ca,mode=0444 if [ -f /run/secrets/proxy_ca ]; then NODE_EXTRA_CA_CERTS=/run/secrets/proxy_ca npm ci --cache /tmp/noir-npm; else npm ci --cache /tmp/noir-npm; fi
COPY --chown=node:node apps/web ./apps/web
COPY --chown=node:node packages ./packages
ENV API_URL=http://api:8000 NEXT_TELEMETRY_DISABLED=1
RUN npm run build
EXPOSE 3000
CMD ["npm","run","start","-w","apps/web"]
