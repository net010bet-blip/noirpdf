# Motores acrescentados e execução

Esta entrega integra as dez ferramentas que não tinham motor. Oito funcionam com programas locais instalados; resumo e tradução requerem um provedor de IA real. Integração não significa cumprimento de todas as opções avançadas da especificação: consulte FEATURE_MATRIX.md.

## Iniciar a versão completa

Recomendado: Docker Desktop/Engine com Compose v2, 8 GiB ou mais de RAM, porta 3000 livre e espaço para imagens/programas. Na primeira instalação, registries e repositórios Debian precisam estar acessíveis.

- Windows: inicie Docker Desktop e execute `iniciar-noirpdf.cmd` na pasta extraída. O script gera uma senha de banco aleatória se `.env` não existir, aguarda os healthchecks e só então abre o navegador. O script Windows não foi executado neste ambiente Linux.
- Linux/macOS: `sh scripts/start.sh`. Ele gera `.env` se necessário, constrói a stack e aguarda os healthchecks. Depois abra http://localhost:3000.
- Configuração manual: copie `.env.example`, defina `POSTGRES_PASSWORD` e execute `docker compose up --build -d --wait --wait-timeout 180`.

Nenhuma senha é exibida ou incluída no ZIP. Mantenha `.env` privado. Para parar: `docker compose down`. Para diagnosticar: `docker compose logs --tail 100`. Não apague volumes para resolver uma conexão sem antes conferir o conteúdo.

Os Dockerfiles instalam LibreOffice, OCRmyPDF, Tesseract por/eng/spa, Ghostscript, Java, Chromium e veraPDF. O instalador veraPDF 1.30.3 usa URL versionada e SHA-256 verificado. O ZIP contém código/configuração, não esses binários. `python -m services.api.doctor --strict` informa motores ausentes sem revelar credenciais. Em produção com TLS, configure a origem exata e cookie Secure.

## Instalação nativa Linux

Instale os requisitos Python fixados e os programas de sistema. O script `scripts/install-system-engines.sh` é destinado ao Docker ou a um host Debian/Ubuntu administrado com permissão para apt. Não o execute como root em um computador sem revisar as alterações. Native Windows não é suportado pelo runner Unix; use Docker Desktop.

Variáveis opcionais: `LIBREOFFICE_BIN`, `OCRMYPDF_BIN`, `TESSERACT_BIN`, `GS_BIN`, `VERAPDF_BIN`, `PDFA_ICC_PROFILE`, `CHROMIUM_BIN`. `HTML_ENABLED=true` é necessário para ativar HTML. O sandbox do Chromium é habilitado por padrão no modo nativo; alguns hosts não o suportam. A configuração `HTML_CHROMIUM_SANDBOX=false` é usada apenas no container isolado desta entrega; não representa uma sandbox por tarefa completa.

A API e o frontend precisam usar a mesma origem pública. Next encaminha `/api` à API configurada em `API_URL` no build. Não habilite CORS indiscriminadamente para encobrir um endereço incorreto. Nunca abra o frontend no modo servidor esperando que o GitHub Pages execute Python.

## Escopo e qualidade

- Office: DOCX, PPTX e XLSX OpenXML reais; múltiplos resultados em ZIP. Bibliotecas não trocam apenas a extensão. Arquivos com macros ou relacionamentos externos são recusados, inclusive hyperlinks externos. LibreOffice respeita o layout disponível, mas não garante equivalência com Microsoft Office. Colunas/áreas cortadas no arquivo original podem permanecer cortadas.
- OCR: Tesseract cria camada de texto via OCRmyPDF. Idiomas por, eng, spa e combinações. PDF com texto existente não é refeito desnecessariamente. Não há garantia para manuscritos ou imagens de baixa qualidade.
- HTML: somente arquivo UTF-8 autossuficiente, até 2 MiB. JavaScript, service workers e todos os pedidos de recursos externos/file são bloqueados. Recursos data URI podem ser incorporados. Conversão por URL não foi habilitada; não há promessa de proteção SSRF de uma função de URL inexistente.
- Excel: células reais com tabelas detectáveis por pdfplumber; formatos numéricos simples e brasileiros. Strings de fórmulas são preservadas como texto, sem execução. Identificadores com zeros à esquerda permanecem texto. OCR prévio para escaneados; tabelas sem bordas podem não ser detectadas.
- PDF/A: somente PDF/A-2b. Ghostscript gera candidato, veraPDF valida e apenas resultado conforme é disponibilizado. Relatório JSON inclui perfil, validador e hash do PDF. Não rotulamos um PDF comum como PDF/A.
- Ocultação: pesquisa literal de até 30 expressões, uma por linha. As áreas são cobertas na imagem e o PDF inteiro é reconstruído com pixels. A saída perde pesquisa, formulários e edição de texto. Texto, anexos, metadados/versões e camadas originais não são copiados. Páginas rotacionadas/recortadas são recusadas para evitar erro de coordenadas. Não substitui revisão visual humana nem implementa seleção de áreas/regex.

## IA gratuita opcional

Por padrão, não há provedor configurado e a interface não aceita arquivos nessas duas rotas. Isso evita erro de conexão e resultados simulados. Para usar Ollama local, após iniciar a stack:

```bash
sh scripts/enable-local-ai.sh
```

O script inicia um serviço opcional, baixa qwen2.5:1.5b (aproximadamente 1 GiB), configura `.env` e recria os serviços com o endereço interno. Reserve ao menos 8 GiB para o conjunto. Não há cobrança por API local, mas existem custos próprios de hardware/energia/download. O script de Ollama é uma opção de implantação; sua execução completa e a qualidade desse modelo específico não foram validadas nesta sessão.

Também é possível definir `AI_BASE_URL` (endpoint OpenAI-compatible terminando em `/v1`), `AI_MODEL` e, quando necessário, `AI_API_KEY`. Exemplo local: `http://ollama:11434/v1`. Um provedor externo pode cobrar; nunca há chamada a um provedor pago por padrão. Configuração do servidor é administrativa, nunca uma URL controlada pelos parâmetros do documento.

O texto extraído é enviado ao provedor configurado; a interface informa isso. Saída em TXT, visualização e cópia. Sem OCR automático ou reconstrução do layout traduzido. Limites padrão: 60.000 caracteres de entrada e 4096 tokens de saída. Respostas vazias, malformadas ou truncadas são recusadas. Disponibilidade do provedor, memória e tempo de inferência não podem ser garantidos pelo aplicativo.

## Conexões e falhas

A interface verifica sessão, histórico e motores antes de executar. API ausente produz aviso específico e botão Reconectar, sem fingir processamento. O polling não acumula requisições concorrentes quando a conexão cai. Uploads têm timeout separado; tarefas preservam estado para consulta após reconexão. Falha na publicação para Redis marca a tarefa como failed, em vez de deixá-la eternamente queued. Reinício do executor local marca operações interrompidas como falhas explícitas. O supervisor inicia o frontend apenas depois da resposta da API.

Isso trata falhas reais e reduz erros de configuração; não é uma promessa de que redes, dispositivos ou serviços externos nunca falharão.

## Evidência adicional de IA real

Além dos testes de contrato, esta entrega foi verificada com Qwen2.5-1.5B-Instruct GGUF Q4_K_M carregado de verdade por llama-cpp-python, em serviço local OpenAI-compatible. Houve teste de motor e de fluxo completo de ambas as rotas, incluindo texto em português, fatos básicos, cópia e download. O modelo não está no ZIP. Esses exemplos curtos não demonstram fidelidade de documentos complexos; a resposta deve ser revisada. A opção Ollama usa o mesmo modelo base, mas o daemon/profile não foi executado nesta sessão.

A configuração opcional de Ollama limita entrada a 12.000 caracteres e saída a 2048 tokens, com contexto de 8192. Para outros provedores, ajuste limites ao contexto real do modelo. Não assuma que todo modelo aceita o limite genérico de 60.000 caracteres.
