# Plano e evidências de testes

Os testes usam documentos sintéticos determinísticos; não constituem prova de fidelidade perfeita com todos os PDFs nem aprovação para produção pública.

## Executado nesta entrega

- Pytest: **39 testes aprovados** (34 motores/validação e 5 API). PDF resultante reaberto, contagem/ordem/rotação/recorte verificadas; texto das sobreposições extraído. AES-256 aberto com senha conhecida; falha com senha errada; AcroForm mantém valor. JPGs são decodificados, ZIPs abertos, DOCX lido pelo python-docx e PPTX pelo python-pptx. Diff textual inclui modificação real. Word/Markdown/comparação rejeitam documentos sem texto extraível em vez de publicar resultados vazios como conversões bem-sucedidas.
- API: criação→upload de dois PDFs→execução em subprocesso→poll→download→verificação de texto e ordem→exclusão. Acesso cruzado a tarefa/input/download bloqueado; conteúdo não-PDF rejeitado; Origin indevido bloqueado; acesso sem sessão rejeitado; estados inválidos, execução duplicada, limpeza por TTL e nomes com traversal exercitados.
- Build Next.js: compilação de produção, TypeScript e geração da home + 33 rotas aprovados.
- Playwright: catálogo nas larguras 375, 768, 1280 e 1920 sem overflow horizontal, busca, favoritos, alternância de tema, junção real com download e motor indisponível explícito. Seleção por miniatura e ordenação acessível de páginas também aprovadas: **9 testes E2E passaram**.
- Screenshots: `artifacts/catalog-*.png` (gerados na execução e incluídos como evidência na distribuição ZIP).
- Configuração Compose: `docker compose config --quiet` validada com senha de teste transitória.
- Imagem Docker API construída com sucesso. O build Docker web encontrou `no space left on device` no daemon durante a criação da camada de build; **não houve validação da stack Compose completa**. O build local do frontend passou. A falha de infraestrutura não foi contada como teste aprovado.
- Auditoria npm: versão PostCSS transitiva vulnerável identificada; Next atualizado para 16.4.3 (PostCSS transitivo corrigido); novo audit/build realizados. Resultado final em `docs/DELIVERY.md`.

A suíte registra um aviso de depreciação do TestClient/Starlette; não é falha. As versões estão fixadas para evitar upgrade major inadvertido.

## Reproduzir

```bash
.venv/bin/python -m pytest -q
npm ci
npm audit
npm run build
# Inicie API e frontend conforme README antes do E2E.
npx playwright install chromium
npm run test:e2e
```

Em ambientes restritos, permitir sockets de loopback para TestClient/servidores e acesso aos registries para instalação. Se o cache padrão não for gravável, use `npm --cache /tmp/noir-npm-cache ...` e `PLAYWRIGHT_BROWSERS_PATH=/tmp/noir-browsers`. Isso é configuração do ambiente, não alteração da aplicação.

## Cobertura ainda necessária

Corpus com fontes não latinas, tabelas complexas, PDFs assinados, tags de acessibilidade, formulários diversos, anexos, arquivos parcialmente corrompidos e imagens grandes. Regressão visual com métricas entre renderizações, OCR com ground truth e Office com referências de layout ainda não existem. Compressão tem teste de validade, sem promessa de ganho mínimo ou benchmark de legibilidade.

Adicionar fuzzing, upload chunked/volumétrico, quotas de disco, carga simultânea, falhas banco/broker, reinício e tarefas presas, expiração durante download, corrida upload/execute/delete, WCAG com leitor de tela e axe. Screenshots verificam layout manualmente e ausência de overflow, não são baseline automatizada de regressão visual. Não há Vitest instalado apenas para testar funções que já têm cobertura de integração; regras frontend extraídas posteriormente deverão ter testes unitários próprios.
