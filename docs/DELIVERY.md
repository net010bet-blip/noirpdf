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

## Atualização do ZIP: dez ferramentas que não tinham motor

Acrescentados `services/api/advanced.py`, `uploads.py`, `doctor.py`, validação isolada em `services/worker/validate.py`, opções contextuais em `AdvancedOptions.tsx`, healthchecks, controles de conexão/reconexão e inicialização com espera da API. Catálogo agora possui motores para as 33 rotas: 31 locais e dois dependentes de provedor IA.

Oito motores novos têm testes reais de conversão e E2E com download: OCR por/eng/spa, três Office→PDF, HTML enviado→PDF, tabelas→XLSX, PDF/A-2b validado e redação permanente rasterizada. As duas rotas IA também foram verificadas com um modelo local real Qwen2.5-1.5B, sem API paga, além dos testes de contrato; não há modelo embutido nem ativação automática.

Incluídos scripts de instalação/inicialização, entrada Windows, perfil Ollama opcional e documentação de escopo/conexão. Foram verificados 61 testes Python, E2E de interface/motores, dois testes diretos de modelo real e dois E2E de modelo real. Consulte TEST_PLAN.md para execuções, skips, comandos e limites. O novo conjunto completo de imagens Docker e o iniciador Windows não foram executados aqui; não são contados como testes aprovados. As alterações desta atualização são entregues no ZIP, sem afirmar novo deploy remoto.

As opções não implementadas de ferramentas anteriores (editor completo, captura/QR, workflows, contas, PKI etc.) continuam explícitas na matriz. Novos motores têm escopos reduzidos declarados: HTML sem URL, PDF/A-2b apenas, redação com rasterização, Office moderno sem referências externas, IA em texto sem reconstrução de layout. Não é conclusão da especificação integral nem promessa de ausência total de falhas de infraestrutura.

## Resultado da publicação Sites

A versão browser foi publicada com status succeeded em https://noirpdf-net010bet.net-010-bet.chatgpt.site, com acesso inicial privado à proprietária/ao proprietário. Site ID appgprj_6ae8094c2be08191b11ecb0067485b7e; versão df90bade04c08191a2e449a20764d75f; commit de origem e3905021f0925faab1dd44155a3003c95ed7f944. Vinte ferramentas browser/21 E2E foram aprovados no preview local dessa publicação. A confirmação de deploy veio da API nativa; a autenticação privada impede teste HTTP anônimo do conteúdo. O modo completo com Python não foi hospedado remotamente.
