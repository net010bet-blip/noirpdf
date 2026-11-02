# NoirPDF

Utilitários PDF em português, identidade própria preta/violeta e tema claro opcional. Código independente, sem copiar ativos ou código do iLovePDF. Funções disponíveis não têm planos premium ou cobrança pelo aplicativo.

**ZIP atualizado:** 33 rotas com motores integrados, sendo **31 ferramentas com processamento local no servidor** e **duas de IA dependentes de provedor configurado**. Os escopos reduzidos e opções ainda ausentes estão em [FEATURE_MATRIX.md](FEATURE_MATRIX.md). Isso não é equivalência completa com iLovePDF.

## Iniciar

Use Docker Desktop/Engine com Compose v2 e a porta 3000 livre. Primeira instalação requer rede para baixar dependências.

- **Windows:** inicie Docker Desktop e execute `iniciar-noirpdf.cmd`.
- **Linux/macOS:** execute `sh scripts/start.sh`.
- **Manual:** copie `.env.example` para `.env`, defina senha própria em `POSTGRES_PASSWORD` e rode `docker compose up --build -d --wait --wait-timeout 180`.

Abra **http://localhost:3000** depois dos healthchecks. Os scripts criam uma senha aleatória sem exibi-la se `.env` não existir. Encerrar: `docker compose down`. Logs: `docker compose logs --tail 100`.

A stack inclui Next.js, FastAPI, PostgreSQL, Redis, Celery worker e scheduler, além dos programas necessários às novas conversões. [Instalação e limitações dos motores](docs/ADVANCED_ENGINES.md).

## Novas ferramentas

OCR real por/eng/spa, Word/PowerPoint/Excel para PDF por LibreOffice, HTML para PDF por Chromium isolado de recursos externos, PDF para Excel com células reais, PDF/A-2b validado pelo veraPDF e ocultação permanente com PDF reconstruído. Resumo e tradução usam um provedor OpenAI-compatible configurável; Ollama local é uma opção gratuita. Sem provedor, essas rotas ficam explicitamente desativadas.

Conversão HTML aceita arquivo, não URL. Ocultação rasteriza e perde texto pesquisável. Tradução produz texto, sem reconstrução de layout. Existem outras limitações relevantes por ferramenta: leia a matriz.

## Desenvolvimento nativo (Linux, Python 3.12+, Node 22+)

```bash
python -m venv .venv
.venv/bin/pip install -r services/api/requirements.txt
npm ci
# Terminal 1, na raiz:
.venv/bin/uvicorn services.api.main:app --host 127.0.0.1 --port 8000 --no-access-log
# Terminal 2, na raiz:
npm run dev
```

Motores avançados exigem programas de sistema e configuração; `python -m services.api.doctor` mostra o estado. A instalação dos pacotes Python não instala LibreOffice, idiomas OCR, Chromium ou veraPDF. Para esses recursos, prefira Docker ou consulte ADVANCED_ENGINES.md. SQLite e subprocessos limitados são usados no modo nativo. API: http://127.0.0.1:8000/docs. O browser usa a mesma origem Next em `/api`, sem CORS aberto.

## IA opcional sem API paga

Depois de iniciar a stack, `sh scripts/enable-local-ai.sh` configura Ollama local e baixa o modelo opcional (~2 GiB). Não baixa modelos nem usa créditos pagos por padrão. Hardware e recursos de inferência ainda são necessários. Leia os limites e os testes em [ADVANCED_ENGINES.md](docs/ADVANCED_ENGINES.md).

## Testes

```bash
.venv/bin/python -m pytest -q
npm run build
npx playwright install chromium
# Com API e frontend ativos:
npm run test:e2e
# Com motores avançados configurados e servidor em localhost:4200:
npx playwright test --config playwright.advanced.config.ts
.venv/bin/python scripts/check-advanced-outputs.py
```

[TEST_PLAN.md](TEST_PLAN.md) registra resultados, cobertura e limites. Testes de binários podem ser pulados quando o motor não estiver instalado: não conte skips como verificações aprovadas. Fixtures são sintéticas, não resultados usados pela aplicação.

## Hospedagem

A versão navegador foi publicada em https://noirpdf-net010bet.net-010-bet.chatgpt.site, inicialmente privada à conta proprietária. Tem 20 ferramentas locais. A versão completa deste ZIP exige servidor para Office/OCR/PDF-A e provedor configurado para IA.

O [repositório GitHub](https://github.com/net010bet-blip/noirpdf) e este ZIP contêm o código desta atualização. GitHub Pages só executa os 20 adaptadores JavaScript e não substitui a versão com servidor. As demais rotas exibem “Requer servidor”. Consulte [HOSTING.md](docs/HOSTING.md) e [DEPLOYMENT.md](DEPLOYMENT.md). Configuração Render está incluída, mas o plano gratuito pode não ter memória suficiente para todas as conversões e não é apropriado para um modelo de IA grande.

## Segurança e arquitetura

Arquivos privados por sessão, UUIDs, validação de formato, limites de upload, subprocessos/timeout, acesso autorizado aos resultados e limpeza por TTL. Histórico usa cookie anônimo, não uma conta com login. Favoritos/tema são locais. Limites padrão: 20 arquivos, 50 MiB/arquivo, 100 MiB/requisição, 500 páginas/PDF, 1 hora de retenção. Python/HTML/Office rodam no servidor; não use o modo de desenvolvimento para exposição pública sem os controles de [SECURITY.md](SECURITY.md).

`apps/web`, `services/api`, `services/worker`, `packages/shared`, `infra`, `tests`, `docs` e `scripts`. Engines substituíveis, catálogo comum e separação frontend/backend. CSS com tokens próprios e Lucide, PDF.js, sem dependências UI sem uso. O ZIP não contém `.env`, senhas, banco, uploads ou dependências instaladas.

Documentação: [ARCHITECTURE.md](ARCHITECTURE.md), [FEATURE_MATRIX.md](FEATURE_MATRIX.md), [SECURITY.md](SECURITY.md), [DEPLOYMENT.md](DEPLOYMENT.md), [TEST_PLAN.md](TEST_PLAN.md), [licenças](docs/LICENSES.md).
