# Segurança e privacidade

## Controles implementados

- UUIDs, cookie aleatório de 256 bits com HttpOnly/SameSite=Strict, opção Secure em HTTPS e verificação de proprietário em todos os endpoints de tarefas, originais e downloads.
- Arquivos fora do diretório público; chaves geradas, nomes de exibição limitados e normalizados. Downloads não aceitam caminhos arbitrários.
- MIME e assinatura/estrutura binária de PDF, JPG/PNG/WebP e OpenXML; HTML UTF-8 limitado. Validação em subprocesso com 8 s de CPU, 12 s de parede, 384 MiB de espaço virtual e dois slots, sem bloquear o event loop. Falhas não publicam resultados.
- 20 arquivos/tarefa, 50 MB/arquivo, limite declarado de corpo HTTP de 100 MB, limite de páginas, 30 tarefas ativas por sessão e 60 mutações/minuto/sessão.
- Subprocessos com limites de recursos e timeout. Worker Compose não root, sem capabilities, rede interna, memória/CPU e PIDs limitados.
- HTML enviado é renderizado pelo Chromium com JavaScript/service workers desativados e rotas de recursos externos/file abortadas. Entrada por URL não está habilitada. Isso não valida um conversor por URL: ele não existe nesta entrega.
- Comparação de Origin em mutações, sem CORS aberto, cookies não expostos ao JavaScript, nosniff, no-store e SameSite.
- Senhas não são colocadas na URL, banco, manifesto, mensagens de erro ou logs do aplicativo. São enviadas por stdin ao subprocesso. Mensagens Celery contêm opções em trânsito: Redis deve permanecer privado e sem persistência de payload.
- TLS deve terminar no reverse proxy de produção. TTL padrão de uma hora, exclusão manual autorizada e varredura automática a cada minuto enquanto serviços operam.

## Limites e ações antes de exposição pública

Esta entrega não é uma auditoria de segurança nem uma sandbox completa. A validação inicial já está em subprocesso limitado; a sandbox de filesystem por tarefa continua pendente. MIME/assinatura não detectam malware. PDFs podem conter scripts/anexos; operações gerais não sanitizam esses elementos. Não há antivírus/CDR. Restrinja exposição até testes de carga e documentos hostis.

O limite por Content-Length não substitui limite de corpo no reverse proxy: clientes podem enviar chunked; multipart pode ser recebido/spooled antes da validação de quantidade/tamanho. Imponha 100 MiB e timeout no proxy, quotas do volume e disco temporário. Limites de taxa são em memória por processo/sessão, não globais por IP; múltiplas sessões contornam esse limite. Produção exige rate limiting no gateway e Redis.

RLIMIT limita recursos, mas o subprocesso local herda acesso de filesystem e rede do usuário. Chromium e Java reservam grandes endereços virtuais: nesses dois motores o limite de 2 GiB de endereço virtual não é aplicado; a memória física deve ser limitada por cgroup/container. O Chromium sem sandbox interna só é configurado no container, que não equivale a isolamento completo por tarefa. No Compose, worker compartilha volume de todos os jobs; um exploit do parser poderia atingir outros arquivos. Para nível de isolamento por tarefa, criar containers efêmeros com apenas diretório do job montado, rede desabilitada, rootfs read-only e seccomp/AppArmor. Ainda não implementado.

Uma sessão anônima não é uma conta autenticada. Cookie roubado concede acesso. Não há recuperação, revogação por usuário ou autenticação administrativa. HTTP local não protege conteúdo em trânsito. Em produção use HTTPS, `COOKIE_SECURE=true` e origem exata. Não exponha FastAPI, PostgreSQL ou Redis à internet.

Arquivos expirados podem persistir até a próxima varredura ou retomada dos serviços. Exclusão de filesystem não promete apagamento físico seguro em SSDs/backups. Registros de tarefas expiradas permanecem como metadados mínimos. Planeje retenção também de banco, logs, broker e backups.

Recorte visual não é redação. Sobreposição de texto não substitui edição do texto original. Assinatura visual não é assinatura criptográfica. Restrições de permissões PDF dependem do leitor. Não há quebra de senha.

## Verificação

Testes exercitam leitura cruzada entre sessões, download prematuro, autenticação ausente, Origin indevido, upload binário inválido, estados, criptografia/descriptografia e intervalos. Não cobrem pentest, exploração de parsers, fuzzing, multipart malicioso ou estresse distribuído. Consulte TEST_PLAN.md.

## Modo local do GitHub Pages

Documentos não são enviados ao servidor; ficam em memória/IndexedDB do navegador. Quem tem acesso ao perfil do navegador tem acesso aos resultados até expirar/excluir. Não há isolamento entre contas do mesmo perfil nem criptografia local implementada. Resultados são removidos na próxima verificação de TTL; não há execução quando o navegador está fechado. IndexedDB depende de quota/permissões e pode falhar. Parsers JavaScript rodam no navegador, sem promessa de imunidade a arquivos maliciosos. O modo sem servidor mantém os motores ausentes desabilitados.

## Motores novos

Office rejeita macros, OLE ativo e referências externas antes de executar LibreOffice com perfil temporário e segurança de macro elevada. Isso não é um antivírus. XLSX extraído grava strings de fórmulas como texto. Redação rasteriza, cobre os pixels das ocorrências e reconstrói um PDF sem o conteúdo original; valida texto ausente e anexos ausentes. Requer revisão visual e páginas normalizadas. PDF/A só é publicado após validação veraPDF. A IA usa URL/modelo de configuração administrativa, sem endpoint controlado pelo documento, e não segue redirecionamentos. O texto vai ao provedor configurado; não há chamada paga por padrão. Respostas inválidas/truncadas são recusadas.

Queda de conexão recebe diagnóstico e reconexão explícitos. A fila falha de forma explícita se a publicação não for possível, e reinício do executor local marca tarefas interrompidas. Ainda não há recuperação idempotente completa de jobs após queda de worker/broker; não anunciar tolerância total a falhas.
