# Arquitetura

## Fluxo executável

Browser → Next `/api/*` → FastAPI → SQLAlchemy (SQLite local/PostgreSQL Compose) → executor → subprocesso Python → artefato privado → download autorizado.

A API cria um UUID e vincula ao SHA-256 de um cookie aleatório HttpOnly. O cookie bruto não é persistido. Arquivos recebem nomes gerados e ficam em `<DATA_DIR>/<uuid>/input`, artefatos em `output`. Um manifesto controlado pelo servidor mantém a ordem escolhida. Nenhum nome de arquivo do cliente é usado como caminho.

`run_engine(slug, files, options, out, progress)` é o contrato dos motores substituíveis. A função retorna nome do artefato, bytes originais/finais e avisos. O runner impõe limites de CPU/memória/arquivo, publica progresso das etapas e verifica PDFs resultantes antes da conclusão. Uma falha não publica um resultado. Múltiplos artefatos viram ZIP com nomes controlados.

## Estados

`created → uploading → ready → queued → processing → completed | failed`.

Upload inválido volta a `created`/`ready`. Cancelamento está disponível antes do processamento (`cancelled`). Tarefas com TTL vencido passam a `expired` e perdem os arquivos. Exclusão manual remove tarefa e diretório. Download só funciona em `completed`, pelo proprietário e antes de expirar. Não se promete cancelamento de processos em execução.

No modo local, ThreadPoolExecutor coordena até dois subprocessos. No Compose, a API publica Celery/Redis e workers separados executam; a rede de processamento é interna, sem saída externa normal. PostgreSQL guarda metadados. Não se guardam opções/senhas no banco; em Celery, opções passam na mensagem transitória do broker. A expiração não depende da visita do usuário: lifespan da API e scheduler realizam varreduras periódicas.

## Contratos HTTP

- `GET /api/session`: estabelece cookie anônimo.
- `GET /api/tools`: catálogo e disponibilidade de motores.
- `POST /api/tasks`: `{tool}`.
- `POST /api/tasks/{id}/upload`: multipart `files`.
- `POST /api/tasks/{id}/execute`: `{options}`.
- `GET /api/tasks/{id}`: estado, progresso e resultado.
- `GET /api/tasks/{id}/input/{key}`: original privado para visualização.
- `GET /api/tasks/{id}/download`: resultado privado com Content-Disposition.
- `GET /api/tasks`: histórico do proprietário.
- `POST /api/tasks/{id}/cancel`: cancelamento antes de executar.
- `DELETE /api/tasks/{id}`: exclusão autorizada.

Configurações são enviadas com a execução, sem endpoint separado de rascunho. Erros usam códigos HTTP e detalhes sem caminhos internos.

## Fronteiras atuais

Não existe login com conta, multitenancy empresarial, cobrança, créditos IA, OAuth, administração, workflows ou adaptador S3. Não há migrações Alembic: a primeira versão cria tabelas com SQLAlchemy; mudanças de esquema exigem migrações antes de uso duradouro. A sessão anônima concede acesso a quem possuir o cookie.

Não há transação distribuída entre banco e Redis. Falha ao publicar ou reinício durante processamento pode deixar uma tarefa pendente; recuperação automática/idempotência é trabalho futuro. Não anunciar disponibilidade de produção sem testar esses casos e a capacidade operacional.

Componentes usam tokens CSS centralizados; biblioteca UI compartilhada é reservada para extração futura. PDF.js renderiza até as primeiras 50 páginas e tem zoom, seleção em ferramentas compatíveis e ordenação com arraste/setas em Organizar. O catálogo é comum ao backend e frontend. `API_URL` deve estar definido no **build** do Next porque rewrites são compilados.

## Adaptador GitHub Pages

`NEXT_PUBLIC_PROCESSING_MODE=browser` seleciona export estático com `NEXT_PUBLIC_BASE_PATH` e desabilita rewrites. O frontend usa `browser-tasks.ts` (IndexedDB, estados/TTL, blobs de resultados) e `browser-engine.ts` (pdf-lib/PDF.js/JSZip/docx). Nenhum upload é enviado à rede. `browser-pptx.ts` gera PPTX visual a partir de um modelo original; não contém texto editável. Esse modo tem 20 motores; proteção, desbloqueio e reparo do backend não são habilitados nele. Engines executam no thread principal com pausas entre etapas, não em sandbox de worker. Desempenho de documentos grandes depende do dispositivo.
