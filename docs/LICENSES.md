# Dependências e licenças

Código próprio desenvolvido para NoirPDF, sem cópia de código/ativos do serviço de referência. Sem promessa de marca registrada disponível; verificar o nome antes de publicação comercial.

Licenças principais (confirmar arquivos LICENSE/NOTICE das versões fixadas ao redistribuir):

| Dependência | Licença | Uso |
|---|---|---|
| Next.js, React | MIT | Web |
| Lucide | ISC | Ícones |
| TypeScript | Apache-2.0 | Tipagem |
| PDF.js (pdfjs-dist) | Apache-2.0 | Visualização e worker local |
| FastAPI, Starlette, SQLAlchemy | MIT | API/persistência |
| pypdf | BSD-3-Clause | Manipulação PDF |
| ReportLab | BSD | Texto, imagens e sobreposições |
| Pillow | MIT-CMU/HPND | Imagens |
| pypdfium2 | Apache-2.0/BSD-3-Clause; PDFium e dependências têm notices próprios | Renderização |
| python-docx, python-pptx, openpyxl | MIT | Documentos editáveis/planilhas |
| Celery, Redis cliente | BSD/MIT | Filas |
| psycopg | LGPL-3.0 | PostgreSQL driver |
| cryptography | Apache-2.0/BSD | AES-256 |
| PostgreSQL | PostgreSQL License | Banco |
| Redis 7 | BSD-3-Clause (fixado na linha 7.0 abaixo) | Broker privado |
| Pytest | MIT | Testes |
| Playwright | Apache-2.0 | E2E |

`package-lock.json` fixa a árvore JavaScript. `services/api/requirements.txt` fixa as versões Python do ambiente testado, incluindo dependências transitivas e de testes. O worker PDF.js em `apps/web/public` vem de pdfjs-dist e preserva o cabeçalho de licença. Notices das bibliotecas devem acompanhar distribuições binárias. Não é uma opinião jurídica nem inventário exaustivo de todas as dependências transitivas.

PyMuPDF não foi adicionado; foi usado pypdf + PDFium. Tesseract/OCRmyPDF, Ghostscript, LibreOffice e veraPDF ainda não estão integrados, e nenhuma licença desses programas foi assumida como parte da distribuição atual.

Adaptador browser: pdf-lib (MIT), JSZip (MIT/GPLv3, utilizada opção MIT) e docx (MIT). O template PPTX é original, gerado por python-pptx com imagem branca própria, sem ativos de terceiros.
