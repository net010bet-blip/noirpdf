# Entrega incremental 01 — NoirPDF

## Alterações e arquivos

Repositório iniciado do zero. Frontend em `apps/web` (Next 16.4.3/React/TypeScript, tokens de design, Lucide, PDF.js); catálogo comum em `packages/shared/catalog.json`; API SQLAlchemy e motores em `services/api`; execução limitada, tarefas Celery e limpeza em `services/worker`; Dockerfiles em `infra`, stack em `compose.yaml`; testes em `tests`; documentação na raiz e `docs`; empacotamento em `scripts/package.py`.

Interface própria preta/violeta com tema claro opcional, 33 rotas, categorias, pesquisa, favoritos, histórico anônimo, arquivos ordenáveis, preview, seleção de páginas, organização por miniaturas, progresso, erros e downloads reais. Nenhuma cobrança ou plano premium foi adicionado.

## Ferramentas funcionais, dentro do escopo documentado

Juntar, dividir, remover, extrair, organizar, digitalizar por imagens, comprimir streams/objetos, tentar reescrita estrutural, JPG para PDF, PDF para JPG, PDF para Word textual, PDF para PowerPoint visual, rodar, numerar, marca d’água textual, recortar por margem, inserir texto, preencher AcroForms existentes, desbloquear com senha conhecida, proteger AES-256, assinatura visual digitada, comparação textual e PDF para Markdown textual.

São **23 motores com testes**, não 23 ferramentas com todos os requisitos concluídos. A matriz classifica 22 como limitadas e a junção como testada. Os dez motores restantes estão indisponíveis de forma explícita, sem upload ou resultados simulados.

## Validação final

- `python -m pytest -q`: **39 aprovados**, um aviso de depreciação do TestClient.
- `npm run build`: **aprovado**, Next 16.4.3/Turbopack, TypeScript e 33 rotas de ferramenta.
- Playwright: **9 aprovados**, incluindo quatro resoluções, busca/favoritos/tema, junção com download, indisponibilidade explícita, seleção e organização por miniaturas.
- PDF baixado no E2E reaberto: duas páginas, texto e ordem conferidos.
- `npm audit`: **zero vulnerabilidades reportadas** na árvore verificada. Não equivale a auditoria de todos os binários/imagens ou pentest.
- `docker compose config --quiet`: aprovado.
- Docker API: imagem construída. Docker web: build interrompido por falta de espaço no daemon. Stack completa com PostgreSQL/Redis/Celery **não foi executada como conjunto**. Não há deploy público concluído.
- Screenshots de 375, 768, 1280 e 1920 px incluídos em `docs/evidence` do ZIP.
- ZIP: geração com lista de arquivos controlada, teste CRC e hash SHA-256. Sem `.env`, dados de sessões, uploads de usuários, banco, caches ou dependências instaladas.

## Limitações reais

Sem login/contas, OAuth, S3/MinIO, administração, workflows, cobrança ou IA integrada. Sem OCR/Office/HTML/PDF-A operacional, extração de tabelas para Excel ou redação permanente. Sem editor visual completo, solicitação de assinaturas ou PKI. Algumas operações usam parâmetros fixos ou opções numéricas; a prévia mostra o original e limita a renderização às primeiras 50 páginas. Histórico usa cookie de sessão.

Não há garantia de preservação de assinaturas digitais, tags, tabelas complexas ou layout em todas as entradas. Sem corpus de fidelidade Office/OCR. Parser de upload e isolamento por tarefa precisam de endurecimento antes de exposição pública. Falhas de infraestrutura/reinícios ainda podem deixar jobs pendentes. Consulte SECURITY.md e FEATURE_MATRIX.md.

## Próximo conjunto de implementação

Completar opções e editores visuais da fase 2; validar Compose em host com espaço suficiente; isolar validação por job e adicionar recuperação idempotente. Em seguida, OCR/LibreOffice com fixtures reais e métricas; PDF/A somente com validador. Depois edição avançada, redação verificável, contas, workflows e IA opcional.

## Atualização: publicação e opção gratuita

Código enviado para https://github.com/net010bet-blip/noirpdf. Acrescentado adaptador estático com 20 motores locais, IndexedDB, download de blobs, reabertura de histórico e expiração local. 21 E2E do modo estático passaram localmente e no GitHub; scripts/check_browser_outputs.py validou os 20 formatos/resultados reais. Audit npm voltou a zero vulnerabilidades após remover dependência transitiva vulnerável e gerar PPTX visual com template original.

Foram incluídos .github/workflows/pages.yml, playwright.pages.config.ts, render.yaml, infra/render.Dockerfile, infra/start-render.py e docs/HOSTING.md. O workflow publica somente depois dos testes. A integração permitiu push, mas recusou habilitar Pages (403); a primeira execução passou testes/build e parou em configure-pages com Pages não habilitado. Ativação pelo proprietário ainda necessária no momento desta atualização.

A configuração Next+API com supervisor do Render foi executada localmente e os nove E2E passaram. Não há conta Render conectada nem deploy remoto Render validado. A opção gratuita não completa funcionalidades pendentes nem garante recursos para documentos grandes. As 33 ferramentas completas continuam sendo trabalho em andamento.
