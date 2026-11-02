# Segurança e privacidade

## Controles implementados

- UUIDs, cookie aleatório de 256 bits com HttpOnly/SameSite=Strict, opção Secure em HTTPS e verificação de proprietário em todos os endpoints de tarefas, originais e downloads.
- Arquivos fora do diretório público; chaves geradas, nomes de exibição limitados e normalizados. Downloads não aceitam caminhos arbitrários.
- Verificação de MIME, assinatura `%PDF-`, parser PDF ou decodificador de imagem; JPG/PNG/WebP permitidos. Falhas não são publicadas como resultados.
- 20 arquivos/tarefa, 50 MB/arquivo, limite declarado de corpo HTTP de 100 MB, limite de páginas, 30 tarefas ativas por sessão e 60 mutações/minuto/sessão.
- Subprocessos com limites de recursos e timeout. Worker Compose não root, sem capabilities, rede interna, memória/CPU e PIDs limitados.
- Nenhum motor HTML/URL ativado: não há fetch de URLs informadas pelo usuário. SSRF não é apresentado como recurso resolvido de um conversor ainda inexistente.
- Comparação de Origin em mutações, sem CORS aberto, cookies não expostos ao JavaScript, nosniff, no-store e SameSite.
- Senhas não são colocadas na URL, banco, manifesto, mensagens de erro ou logs do aplicativo. São enviadas por stdin ao subprocesso. Mensagens Celery contêm opções em trânsito: Redis deve permanecer privado e sem persistência de payload.
- TLS deve terminar no reverse proxy de produção. TTL padrão de uma hora, exclusão manual autorizada e varredura automática a cada minuto enquanto serviços operam.

## Limites e ações antes de exposição pública

Esta entrega não é uma auditoria de segurança nem uma sandbox completa. Parsers de upload na API ainda precisam de isolamento dedicado. MIME/assinatura não detectam malware. PDFs podem conter scripts/anexos; operações gerais não sanitizam esses elementos. Não há antivírus/CDR. Restrinja exposição até testes de carga e documentos hostis.

O limite por Content-Length não substitui limite de corpo no reverse proxy: clientes podem enviar chunked; multipart pode ser recebido/spooled antes da validação de quantidade/tamanho. Imponha 100 MiB e timeout no proxy, quotas do volume e disco temporário. Limites de taxa são em memória por processo/sessão, não globais por IP; múltiplas sessões contornam esse limite. Produção exige rate limiting no gateway e Redis.

RLIMIT limita recursos, mas o subprocesso local herda acesso de filesystem e rede do usuário. No Compose, worker compartilha volume de todos os jobs; um exploit do parser poderia atingir outros arquivos. Para nível de isolamento por tarefa, criar containers efêmeros com apenas diretório do job montado, rede desabilitada, rootfs read-only e seccomp/AppArmor. Ainda não implementado.

Uma sessão anônima não é uma conta autenticada. Cookie roubado concede acesso. Não há recuperação, revogação por usuário ou autenticação administrativa. HTTP local não protege conteúdo em trânsito. Em produção use HTTPS, `COOKIE_SECURE=true` e origem exata. Não exponha FastAPI, PostgreSQL ou Redis à internet.

Arquivos expirados podem persistir até a próxima varredura ou retomada dos serviços. Exclusão de filesystem não promete apagamento físico seguro em SSDs/backups. Registros de tarefas expiradas permanecem como metadados mínimos. Planeje retenção também de banco, logs, broker e backups.

Recorte visual não é redação. Sobreposição de texto não substitui edição do texto original. Assinatura visual não é assinatura criptográfica. Restrições de permissões PDF dependem do leitor. Não há quebra de senha.

## Verificação

Testes exercitam leitura cruzada entre sessões, download prematuro, autenticação ausente, Origin indevido, upload binário inválido, estados, criptografia/descriptografia e intervalos. Não cobrem pentest, exploração de parsers, fuzzing, multipart malicioso ou estresse distribuído. Consulte TEST_PLAN.md.

## Modo local do GitHub Pages

Documentos não são enviados ao servidor; ficam em memória/IndexedDB do navegador. Quem tem acesso ao perfil do navegador tem acesso aos resultados até expirar/excluir. Não há isolamento entre contas do mesmo perfil nem criptografia local implementada. Resultados são removidos na próxima verificação de TTL; não há execução quando o navegador está fechado. IndexedDB depende de quota/permissões e pode falhar. Parsers JavaScript rodam no navegador, sem promessa de imunidade a arquivos maliciosos. O modo sem servidor mantém os motores ausentes desabilitados.
