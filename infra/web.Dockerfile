# syntax=docker/dockerfile:1
FROM node:22-bookworm-slim
WORKDIR /app
COPY package.json package-lock.json ./
COPY apps/web/package.json apps/web/package.json
RUN --mount=type=secret,id=proxy_ca if [ -f /run/secrets/proxy_ca ]; then NODE_EXTRA_CA_CERTS=/run/secrets/proxy_ca npm ci; else npm ci; fi
COPY apps/web ./apps/web
COPY packages ./packages
ENV API_URL=http://api:8000
RUN npm run build
USER node
EXPOSE 3000
CMD ["npm","run","start","-w","apps/web"]
