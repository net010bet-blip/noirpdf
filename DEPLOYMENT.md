# Deploy

## Compose

Use Docker Engine com Compose v2, pelo menos 6 GiB de RAM e volume suficiente para documentos. Configure `.env` (nunca versionado): senha PostgreSQL própria, `PUBLIC_ORIGIN` exata, TTL e `COOKIE_SECURE=true` em HTTPS. Suba com `docker compose up --build -d`. Apenas web:3000 é exposto; API conversa com Redis/PostgreSQL na rede interna. O worker não recebe acesso à rede externa pelo Compose.

O Dockerfile web define `API_URL=http://api:8000` antes do build. Para outra topologia, altere o build; configurar apenas no runtime não recompila rewrites Next. A imagem API funciona como API, worker ou scheduler com comandos distintos.

Reverse proxy (Nginx/Caddy/Traefik) deve terminar TLS, redirecionar HTTP, aplicar HSTS conforme domínio, limitar uploads a 100 MiB, impor timeout de upload e impedir exposição dos serviços internos. Configure corpo no proxy, inclusive requests chunked. Não publique diretamente a porta 3000 sem esses controles em ambiente público.

Volumes: `documents` (UID/GID 10001), `database` (PostgreSQL). Não copie dados temporários para imagens ou repositório. Redis tem persistência desligada. TLS interno e armazenamento criptografado são responsabilidade da infraestrutura quando necessários. Não há MinIO/S3 ativo nesta versão.

## Proxy e certificados em builds

Em ambientes com CA privada, use segredo BuildKit, sem desabilitar TLS:

```bash
docker build --secret id=proxy_ca,src=/caminho/ca-bundle.pem -f infra/api.Dockerfile -t noirpdf-api .
docker build --secret id=proxy_ca,src=/caminho/ca-bundle.pem -f infra/web.Dockerfile -t noirpdf-web .
```

Dockerfiles reconhecem o segredo opcional para pip/npm; nenhum certificado ou segredo é copiado ao artefato final. Compose padrão usa a cadeia pública do sistema; acrescente `build.secrets` se o ambiente precisar de CA privada. Nunca inclua senha em build args.

## Checklist operacional restante

Testar smoke upload→fila→processamento→download→expiração no domínio final, isolamento de rede e reinício de workers. Validar restauração PostgreSQL, quotas de disco e retenção de backups. Adicionar migrações, supervisão/alertas para jobs presos, idempotência e monitoramento de profundidade da fila. Não há endpoint administrativo nem painel de saúde completo.

A validação desta entrega inclui build da API e configuração Compose; o estado dos testes de stack completa está em TEST_PLAN.md. Não declarar deploy público concluído com base apenas no YAML.
