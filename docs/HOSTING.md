# Hospedagem: GitHub Pages + opção gratuita com servidor

Repositório: https://github.com/net010bet-blip/noirpdf

## Dois modos do mesmo projeto

| Modo | Motores | Onde os documentos ficam | Limites |
|---|---|---|---|
| GitHub Pages | 20 engines JavaScript locais | IndexedDB no dispositivo | Sem Python/OCR/Office/criptografia; memória do navegador |
| Servidor (Docker/Render) | 31 motores locais + 2 via provedor IA | Diretório temporário privado por sessão | Também não completa as 33 ferramentas; precisa de hospedagem e endurecimento antes de tráfego público |

A URL esperada para Pages é `https://net010bet-blip.github.io/noirpdf/`. URL esperada não significa deploy aprovado: confirmar em Actions/Settings > Pages e abrir a página antes de anunciar publicação.

## GitHub Pages

O workflow `.github/workflows/pages.yml` instala dependências, audita npm, executa Pytest, gera o site estático, testa todos os 20 motores no navegador e confere os 20 artefatos antes de publicar. Configure Settings > Pages > Source = GitHub Actions. O deploy usa somente GITHUB_TOKEN efêmero do runner, sem token salvo no código.

No modo Pages, proteção/desbloqueio/reparo que dependem do motor Python são identificados como indisponíveis. Os novos motores do backend também exigem a versão com servidor; IA requer provedor configurado. Nenhum documento é enviado ao GitHub ou ao Render pelo modo local. Favoritos e tema ficam no localStorage, resultados temporários em IndexedDB. Fechar a aba interrompe tarefas em andamento; ao retornar elas são marcadas como interrompidas. TTL é verificado na consulta/reabertura e a cada minuto enquanto a página está aberta. O navegador fechado não executa um serviço de limpeza.

Para reproduzir o build e os testes:

```bash
NEXT_PUBLIC_PROCESSING_MODE=browser NEXT_PUBLIC_BASE_PATH=/noirpdf npm run build
mkdir -p /tmp/noir-pages/noirpdf
cp -a apps/web/out/. /tmp/noir-pages/noirpdf/
python -m http.server 4173 --directory /tmp/noir-pages
# Em outro terminal:
PAGES_TEST_URL=http://localhost:4173/noirpdf npx playwright test --config playwright.pages.config.ts
.venv/bin/python scripts/check_browser_outputs.py
```

## Render gratuito: precisa de ativação pela conta do proprietário

[Configurar deploy no Render](https://render.com/deploy?repo=https://github.com/net010bet-blip/noirpdf)

O arquivo `render.yaml` solicita explicitamente `plan: free`, sem banco/disco pagos. `infra/render.Dockerfile` prepara Next e FastAPI no mesmo serviço/origem. `infra/start-render.py` supervisiona ambos, usa a porta fornecida pelo Render e aplica a origem pública à verificação CSRF. Não é necessário fornecer tokens no repositório.

1. Abra o link, crie/entre em sua conta Render e autorize acesso ao repositório.
2. Revise que o serviço usa o plano **Free** e confirme a criação no Render.
3. Aguarde build/deploy; confira logs e URL real fornecida pelo provedor.
4. Teste upload, junção, download, senha, exclusão e reinício nessa URL. Ainda não foi feito um deploy remoto Render nesta entrega.

O plano gratuito pode suspender serviços ociosos, ter partida lenta, poucos recursos e armazenamento efêmero. Reinícios descartam arquivos e histórico do servidor. Documentos pesados podem exceder a memória disponível, mesmo dentro dos limites do formulário. Preços/disponibilidade/requisitos de cadastro são definidos pelo provedor; não há promessa de capacidade ilimitada ou gratuidade permanente. Não configuramos upgrades pagos automáticos.

OCR, Office, HTML enviado, tabelas, PDF/A-2b e redação rasterizada foram integrados/testados nesta atualização do ZIP. IA requer provedor configurado. Edição completa, contas e outros módulos avançados permanecem limitados/ausentes. Não se promete equivalência completa com iLovePDF. Antes de liberar uploads públicos não confiáveis no servidor, resolver os itens de SECURITY.md (proxy/quotas, isolamento e recuperação de jobs).

## Sites: publicação verificada da versão browser

Versão navegador publicada com sucesso em https://noirpdf-net010bet.net-010-bet.chatgpt.site. A publicação foi confirmada pelo serviço Sites; acesso inicial privado, restrito à conta proprietária. As 20 ferramentas browser passaram em 21 E2E antes da publicação. Esta hospedagem não executa Python: os motores avançados do ZIP precisam da stack com servidor. Nenhum deploy completo Render foi ativado nesta sessão.
