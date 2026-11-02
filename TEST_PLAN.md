# Plano e evidências de testes

Esta atualização cobre processamento real e recuperação de erros. Fixtures são sintéticas; não são resultados usados pela aplicação. Não há prova de fidelidade perfeita com todos os documentos.

## Verificação desta atualização

- **61 testes Python aprovados**, com programas reais instalados neste ambiente: LibreOffice 25.2.3.2, OCRmyPDF 16.7, Tesseract por/eng/spa, Ghostscript, veraPDF 1.30.3 e Chromium via Playwright. Há um aviso de depreciação do TestClient/Starlette, sem falha.
- Core: contagem/ordem/rotação/recorte, texto inserido e extraído, AES-256, senha incorreta, AcroForms, arquivos ZIP/JPG, DOCX editável e PPTX visual.
- Novos motores: Word/PPTX/XLSX convertidos de verdade e reabertos; OCR em três idiomas com texto reconhecido; tabela para células numéricas; proteção contra fórmula XLSX; PDF/A validado por veraPDF; caso não conforme não publicado; redação com ausência de texto/anexos e inspeção de pixels negros na área original; HTML com JavaScript e recursos locais/remotos bloqueados, confirmado por servidor HTTP de captura sem requisições.
- API: upload/execução/download/exclusão, acesso cruzado, formato renomeado falso, origens indevidas, expiração, estados, tarefa duplicada, fila indisponível sem ficar queued, banco indisponível com 503 seguro e healthcheck. Validação de upload executa em subprocesso com limites.
- Dois testes HTTP de IA usam stub **explicitamente apenas para contrato**, sem pretender avaliar um modelo. Testam endpoint/payload de integração. Falta de configuração e URL com credenciais são rejeitadas.
- **Dois testes opcionais com IA real**, em `tests/live_provider.py`: Qwen2.5-1.5B-Instruct GGUF Q4_K_M em llama-cpp-python 0.3.36, via endpoint local OpenAI-compatible. Resumo e tradução para português preservaram Ana, orçamento e 120 dólares no documento de teste. Não constituem benchmark de precisão ou validação de documentos complexos.
- **Nove E2E básicos** de interface/mesclagem/miniaturas e quatro resoluções; **onze E2E avançados** definidos para oito ferramentas, recuperação de conexão, resposta indevida de proxy e IA não configurada. Resultados de execução na entrega; testes de rede usam interrupção controlada apenas no teste, sem fallback simulado na aplicação.
- **Dois E2E com IA real** verificam execução pelo frontend/API/worker, texto na tela, cópia para clipboard e download. O servidor de modelo usa inferência real, não respostas pré-escritas.
- **21 E2E do modo estático** verificam 20 motores browser, seus downloads, histórico após reload e resoluções. Reexecutados separadamente do modo servidor.
- `scripts/check-advanced-outputs.py` reabre os oito arquivos baixados: conteúdo Office, páginas, OCR pesquisável, XLSX numérico e redação sem texto. `scripts/check_browser_outputs.py` reabre os 20 resultados browser.
- Build Next/TypeScript nos modos servidor e export estático. `npm audit` sem vulnerabilidades reportadas na árvore consultada. Isso não é auditoria de binários, imagens ou pentest.
- Compose base e perfil IA passam em `docker compose config --quiet`. Scripts shell passam em `sh -n`.
- O script versionado de instalação veraPDF foi executado e conferiu SHA-256/versão. **As imagens Docker completas atualizadas e a stack Compose integral não foram construídas/executadas nesta atualização.** O ambiente anterior encontrou falta de espaço no daemon. Conversões e supervisor Next+API foram executados nativamente.
- O iniciador Windows não foi executado aqui (ambiente Linux). O perfil Ollama e o script de pull são configuração de implantação; a inferência real foi testada com o mesmo modelo base via llama.cpp, não com o daemon Ollama.

## Reproduzir

```bash
.venv/bin/python -m pytest -q
npm ci
npm audit
npm run build
# API e frontend ativos:
E2E_BASE_URL=http://localhost:4200 npx playwright test --config playwright.config.ts
E2E_BASE_URL=http://localhost:4200 npx playwright test --config playwright.advanced.config.ts
.venv/bin/python scripts/check-advanced-outputs.py
```

Testes de binários são pulados se ausentes; um skip não equivale a motor verificado. Para reproduzir o conjunto completo, instale programas/idiomas e configure `VERAPDF_BIN`, `HTML_ENABLED` e Chromium. Na sessão restrita foi permitido acesso a sockets de loopback e registries para executar serviços/testes; isso não altera o aplicativo.

## Provedor real opcional

Com provedor e modelo reais ativos, sem credenciais no código:

```bash
RUN_LIVE_AI_TESTS=1 AI_BASE_URL=http://127.0.0.1:8099/v1 AI_MODEL=qwen-local \
  .venv/bin/python -m pytest tests/live_provider.py -q -s
# API iniciada com o mesmo provedor; frontend em localhost:4200:
RUN_LIVE_AI_TESTS=1 E2E_BASE_URL=http://localhost:4200 \
  npx playwright test --config playwright.ai.config.ts
```

`scripts/run-local-llama.py` é um gateway loopback de desenvolvimento opcional, requer instalação separada de llama-cpp-python e um modelo GGUF obtido legitimamente. Não é um servidor público de produção e não baixa um modelo automaticamente. Para uso cotidiano, prefira a opção Ollama documentada. Configure limite de entrada compatível com o contexto do modelo. Nenhum modelo ou chave é incluído no ZIP.

## Limites da cobertura

Faltam corpus Office complexo, fontes não latinas, OCR com ground truth/medição de erro, regressão visual com baseline/métricas, layouts com tabelas sem bordas e avaliação extensa de resumo/tradução. Qualidade de IA pode variar e precisa de revisão humana. Não há promessa de tradução fiel de contratos ou de precisão legal/médica.

Faltam fuzzing, carga distribuída, partições de rede, quotas de disco, recuperação idempotente de broker/worker após crashes, pentest e auditoria WCAG completa. Screenshots e ausência de overflow são verificações de layout, não certificação de acessibilidade. Consulte SECURITY.md. Nenhum teste garante que qualquer rede/provedor/hardware nunca falhará; a aplicação deve diagnosticar e recusar resultados inválidos.

## Publicação verificada

Sites confirmou sucesso da versão browser em https://noirpdf-net010bet.net-010-bet.chatgpt.site. Acesso inicial privado. O preview estático antigo deixou de responder; a rodada inicial de regressão falhou na navegação, sem executar motores. Após reiniciar o preview com logs em arquivo, os 21 testes passaram no build raiz destinado ao Sites e os 20 artefatos foram reabertos. Nenhum resultado anterior foi contado como nova aprovação da rodada que falhou. O serviço nativo confirmou publicação; não há QA pós-login na URL privada nesta sessão.
