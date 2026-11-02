# Matriz de funcionalidades

Status por escopo integral solicitado. **Limitada** significa que o subconjunto descrito processa arquivos e possui teste de motor; não significa ferramenta completa. Todas as 33 rotas têm motores integrados. 31 ferramentas usam motores locais; duas de IA exigem um provedor configurado. Nenhuma função da aplicação é cobrada, mas um provedor externo pode cobrar suas próprias APIs.

| # | Ferramenta | Status | Escopo e limitações |
|---|---|---|---|
| 1 | Juntar PDF | testada | Múltiplos PDFs, ordem por arraste/setas; preservação básica de páginas e orientação. Não valida todas as estruturas especiais e assinaturas digitais. |
| 2 | Dividir PDF | limitada | Intervalo e grupos a cada N páginas com ZIP; sem limite por tamanho, múltiplos intervalos independentes ou unir intervalos configurável. |
| 3 | Remover páginas | limitada | Intervalos ou miniaturas (primeiras 50), valida exclusão total. |
| 4 | Extrair páginas | limitada | Seleção por intervalo/miniaturas em PDF único; sem modo de arquivos separados. |
| 5 | Organizar PDF | limitada | Ordem numérica e arraste das primeiras 50 miniaturas de um PDF; sem adicionar páginas de outros PDFs, rotação/exclusão combinadas ou seleção múltipla em lote. |
| 6 | Digitalizar para PDF | limitada | Upload de imagens com ordem e margem para PDF A4. Sem captura de câmera dedicada, perspectiva ou pareamento QR. |
| 7 | Comprimir PDF | limitada | Compressão de streams e deduplicação de objetos, sem perda; sem três níveis ou reamostragem de imagens. Exibe bytes antes/depois. |
| 8 | Reparar PDF | limitada | Tentativa de leitura permissiva e reescrita; sem diagnóstico estrutural completo ou relatório de recuperação parcial. |
| 9 | OCR PDF | limitada | OCRmyPDF/Tesseract real em por/eng/spa, PDFs e imagens, camada pesquisável. Idiomas e binários precisam estar instalados; baixa resolução, manuscritos e páginas complexas exigem revisão. |
| 10 | JPG para PDF | limitada | JPG/PNG/WebP ordenados em PDF único A4 com margem; opções Carta/original/paisagem e saída separada não expostas na UI. |
| 11 | Word para PDF | limitada | DOCX para PDF real por LibreOffice, inclusive múltiplos arquivos/ZIP. Sem DOC binário; macros e referências externas recusadas. Fontes e quebras podem variar. |
| 12 | PowerPoint para PDF | limitada | PPTX para PDF real por LibreOffice, slides como páginas. Referências externas/macros recusadas; fontes, efeitos e layout dependem do motor. |
| 13 | Excel para PDF | limitada | XLSX para PDF real por LibreOffice, área de impressão do arquivo. Revise escala, colunas cortadas no original, gráficos e fontes. Sem editor de áreas de impressão. |
| 14 | HTML para PDF | limitada | HTML UTF-8 enviado, impressão Chromium, papel/orientação/margens. JavaScript e recursos externos/file bloqueados. URL remota não é aceita; isolamento de produção depende do container. |
| 15 | PDF para JPG | limitada | Renderiza páginas selecionadas e entrega JPG/ZIP. Sem extração de imagens incorporadas ou qualidade configurável na UI. |
| 16 | PDF para Word | limitada | Texto extraído em parágrafos DOCX editáveis; sem reconstrução de tabelas, imagens, layout ou OCR. |
| 17 | PDF para PowerPoint | limitada | Modo visual com páginas como imagens em slides A4. Sem modo editável; proporções podem ser ajustadas. |
| 18 | PDF para Excel | limitada | pdfplumber detecta tabelas digitais e exporta XLSX com células reais, números e abas/consolidação. Fórmulas do texto são gravadas como texto. Sem OCR automático ou editor de detecção. |
| 19 | PDF para PDF/A | limitada | Perfil PDF/A-2b por Ghostscript, validado pelo veraPDF antes de publicar. Relatório JSON com SHA-256. Sem outros perfis; resultado não conforme é recusado. |
| 20 | Rodar PDF | limitada | 90/180/270 graus, todas ou selecionadas; prévia mostra original, não simula resultado antes da execução. |
| 21 | Números de página | limitada | Seleção e números iniciando em 1, rodapé central. Sem posições personalizadas, cor, capa ou espelhamento na UI. |
| 22 | Marca d’água | limitada | Texto diagonal central 25%, acima do conteúdo e intervalo. Sem imagem/mosaico/posição/opacidade configuráveis. |
| 23 | Recortar PDF | limitada | Margem uniforme em pontos, intervalo. Sem retângulo visual. CropBox não remove conteúdo subjacente. |
| 24 | Editar PDF | limitada | Inserção persistente de texto em posição fixa. Sem edição real de texto existente, objetos arrastáveis, imagens, comentários ou undo/redo. |
| 25 | Formulários PDF | limitada | Preenchimento AcroForm existente por nomes/JSON, com valores preservados. Sem criação/editor visual de campos. |
| 26 | Desbloquear PDF | limitada | Descriptografia com senha conhecida. Sem quebra de senha; sem classificação detalhada de abertura/permissões na UI. |
| 27 | Proteger PDF | limitada | Criptografia AES-256, mínimo 8 caracteres. Sem configuração de permissões na UI. |
| 28 | Assinar PDF | limitada | Assinatura visual digitada em posição fixa. Sem desenho/imagem/PKI, solicitação, signatários ou auditoria. |
| 29 | Ocultar informações | limitada | Expressões literais buscadas e cobertas nos pixels, seguidas de PDF novo sem conteúdo original, texto, campos ou anexos. Rasteriza todas as páginas e verifica ausência de texto. Exige páginas sem rotação/recorte; sem editor de áreas ou regex. |
| 30 | Comparar PDF | limitada | Dois PDFs, diff textual exportado como TXT. Sem visualização lado a lado, sincronização ou diferença por pixels. |
| 31 | Resumir PDF com IA | limitada | Integração real OpenAI-compatible para provedor configurado, incluindo Ollama local opcional. Resumo curto/médio/longo e idioma; saída TXT, visualização e cópia. Desativada sem configuração; testes de contrato não substituem avaliação de modelo. |
| 32 | Traduzir PDF com IA | limitada | Tradução via provedor configurado e idioma de destino, saída TXT com visualização/cópia. Sem OCR automático, reconstrução de layout ou PDF traduzido. Resposta truncada não é publicada. Desativada sem configuração. |
| 33 | PDF para Markdown | limitada | Texto extraído com marcadores de página em .md. Sem reconstrução semântica de títulos, tabelas, listas ou imagens/OCR. |

## Recursos transversais

Implementados: catálogo/busca/categorias, favoritos locais, tema local, upload, ordenação de arquivos, prévia PDF.js com zoom (primeiras 50 páginas), tarefas/progresso, erros, ZIP, histórico anônimo, download, exclusão, expiração e cancelamento antes da execução.

Não implementados: contas/login, idioma além de pt-BR, preferências sincronizadas, workflows encadeados, OAuth Drive/Dropbox, S3/MinIO, créditos de IA, cobrança, planos, assinatura por solicitação e painel administrativo. Não há botões de integração ou cobrança sem função.

Há testes de motor e E2E para junção e para as oito ferramentas locais acrescentadas nesta entrega, incluindo download e verificação dos artefatos. As funções de IA têm testes de integração separados. A matriz não promete fidelidade perfeita com documentos reais.

## Disponibilidade por hospedagem

A tabela descreve o backend Python completo desta entrega. No build estático para GitHub Pages, 20 ferramentas têm adaptadores locais. As demais mostram “Requer servidor”. A versão com servidor verifica a instalação de motores e a configuração de IA antes de habilitar a execução. Consulte docs/HOSTING.md e docs/ADVANCED_ENGINES.md.
