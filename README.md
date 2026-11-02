# NoirPDF

Código preparado para [GitHub](https://github.com/net010bet-blip/noirpdf). Publicação estática com motores locais e opção gratuita de servidor: consulte [HOSTING.md](docs/HOSTING.md).

[Configurar servidor gratuito no Render](https://render.com/deploy?repo=https://github.com/net010bet-blip/noirpdf) — requer sua conta e ativação; não significa que todas as 33 ferramentas estejam prontas.

Plataforma independente de utilitários PDF, em português, com tema escuro e opção clara. Todos os recursos entregues são gratuitos. Não é afiliada ao iLovePDF e não utiliza código ou ativos dele.

**Entrega incremental, não plataforma completa:** 33 ferramentas têm rotas; 23 têm motores com escopos descritos em [FEATURE_MATRIX.md](FEATURE_MATRIX.md). Não confunda motor disponível com cumprimento de todos os requisitos da ferramenta. OCR, Office, HTML, PDF/A, IA, redação permanente e outras funções avançadas ainda não estão operacionais.

## Execução local (Linux, Python 3.12+, Node 22+)

```bash
python -m venv .venv
.venv/bin/pip install -r services/api/requirements.txt
npm ci
# Terminal 1, na raiz do projeto:
.venv/bin/uvicorn services.api.main:app --host 127.0.0.1 --port 8000 --no-access-log
# Terminal 2, na raiz:
npm run dev
```

Abra **http://localhost:3000**. O modo local usa SQLite, armazenamento privado em `data/` e dois slots de subprocessos limitados; não requer serviços pagos. A API varre arquivos expirados a cada minuto enquanto estiver em execução. Ao desligar, a próxima inicialização retoma a exclusão. Não use este modo de desenvolvimento para uploads públicos não confiáveis.

Para produção local do frontend: `npm run build` e `npm run start -w apps/web`. A documentação OpenAPI está em http://127.0.0.1:8000/docs. O browser acessa somente `/api` na origem do frontend; Next faz o proxy à API.

## Docker Compose

```bash
cp .env.example .env
# Edite .env e defina POSTGRES_PASSWORD com um valor aleatório próprio.
docker compose up --build
```

Inclui Next.js, API FastAPI, PostgreSQL, Redis, Celery worker e scheduler; somente a porta 3000 é pública. Leia [DEPLOYMENT.md](DEPLOYMENT.md) para HTTPS, redes e validação do deploy. O armazenamento desta entrega é volume privado compartilhado, ainda sem adaptador S3/MinIO.

## Testes

```bash
.venv/bin/python -m pytest -q
npm run build
npx playwright install chromium
# Com API e frontend ativos em localhost:3000:
npm run test:e2e
```

Fixtures sintéticas estão em `tests/fixtures`. Screenshots e download E2E vão para `artifacts/`. Resultados e limites da verificação estão em [TEST_PLAN.md](TEST_PLAN.md).

## Uso

Escolha uma ferramenta disponível, selecione arquivos, confira a prévia e as opções, execute e baixe o resultado. Histórico é vinculado a cookie de sessão anônima, não a uma conta autenticada. Favoritos e tema são locais ao navegador. A maioria das ferramentas aceita um único PDF por tarefa; juntar aceita múltiplos e comparar exige dois. Imagens podem ser múltiplas. Intervalos usam `1-3,5`; índices começam em 1.

Uploads: 20 arquivos por tarefa, 50 MB por arquivo, 100 MB por requisição, 500 páginas por PDF. Processamento: 120 segundos de CPU, 180 de tempo total, 2 GiB de endereço virtual e 200 MiB por arquivo de saída. Limites podem causar erro em documentos complexos; eles não garantem equivalência visual em todos os PDFs.

## Estrutura e documentação

- `apps/web`: Next.js, React, TypeScript, CSS com tokens próprios, Lucide e PDF.js.
- `services/api`: endpoints, persistência, sessões e engines.
- `services/worker`: subprocesso limitado, Celery e expiração.
- `packages/shared`: catálogo tipado pelo consumo JSON.
- `infra`: imagens Docker; `compose.yaml` na raiz.
- `tests`: testes de documentos, API e Playwright.
- [ARCHITECTURE.md](ARCHITECTURE.md), [SECURITY.md](SECURITY.md), [FEATURE_MATRIX.md](FEATURE_MATRIX.md), [DEPLOYMENT.md](DEPLOYMENT.md), [TEST_PLAN.md](TEST_PLAN.md), [docs/LICENSES.md](docs/LICENSES.md).

CSS direto foi usado para manter esta primeira entrega enxuta; Tailwind/shadcn não foram adicionados apenas como dependências sem uso. A fonte é a pilha do sistema. Conversão Office, OCR e IA ficam explicitamente indisponíveis, sem botões falsos nem downloads demonstrativos.

## Próximas etapas

1. Completar organização visual de páginas, editor de recorte, opções de divisão e marca d’água; ampliar corpus de regressão e testes de corrupção.
2. Integrar OCR e LibreOffice em workers separados e medir qualidade; PDF/A somente com validador de conformidade.
3. Editor/formulários visuais, redação permanente verificável e comparação visual.
4. Contas reais, OAuth, fluxos encadeados, S3, auditoria, administração e provedor de IA opcional.

Não há cobrança, assinatura paga, limite premium ou promessa de plataforma finalizada nesta entrega.
