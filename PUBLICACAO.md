# Publicação do site e integrações de backup

Estado D158 conferido em 20/10/2026 às 21:17 Brasília: entrada independente ativa e Malu
saudável com mesmas imagens/dados. Site `.com` HTTPS 200 e www 302; `.com.br` apontado
em 20/10 à noite (ver abaixo). Matheo publicado em 21/10 em `matheo.smdevstudio.com` (DNS-only, mesma borda). AAAA antigos removidos com confirmação; A `.com` na VPS,
DNS-only. Em 20/10 às 22:02 Brasília, `.com.br` e www apontados à VPS em DNS-only com confirmação
de Fernando; certificados emitidos pela borda e os quatro nomes aprovados no aceite público (HTTPS,
redirects com caminho/consulta, 404, cabeçalhos, seis páginas de integração). Proxy/Full strict e
OAuth durável pendentes. Roteiro e evidências: `../appmatheo/docs/continuidade-publicacao.md`.
Sem push, contratação ou upgrade.

## Destino e limites

Destino aprovado para preparação local: VPS existente, com serviço estático e entrada independente dos ciclos de publicação das aplicações. Domínio principal `https://smdevstudio.com`; `.com.br` e aliases `www` encaminham para ele preservando caminho e consulta. A antiga hospedagem PHP/HTML não foi encontrada ativa.

Em 20/10/2026, Fernando aprovou preparar e depois iniciar o plano Cloudflare para SM e Matheo, preservando Malu. O [plano de DNS/CDN, HTTPS, aceite e retorno](infra/CLOUDFLARE.md) contém os critérios da configuração; a delegação `.com` é a primeira alteração aplicada.

O `.com` foi delegado à Cloudflare Free, com A na VPS e www CNAME DNS-only; AAAA antigo removido; o redirect antigo Hostinger ainda não foi removido. A zona `.com.br` já usa Cloudflare Free com proxy e origem antiga; SSL Full e zero Page Rules observados. Exportações de ambas as zonas preservadas. Conferir demais regras antes do apontamento, preservando registros de e-mail/verificação.

Configuração local: [serviço do site](infra/compose.yaml), [servidor estático](infra/Caddyfile), [fragmento HTTPS](infra/smdevstudio.caddy) e [overlay da entrada independente](infra/compose.borda-adicional.yaml). Não instalar no frontend do Malu nem ocupar 80/443 antes da janela específica. O ensaio local usa `compose.ensaio.yaml`, que não deve ir para a composição de produção.

A separação da entrada pública foi aplicada na D158, com retorno da primeira tentativa e sucesso da segunda. Não repetir a troca inicial; seguir o estado e os gates restantes no documento de continuidade do Matheo.

## Conteúdo público e pacote

A página comercial mantém seu conteúdo separado. As integrações ficam em URLs diretas, sem menu comercial e com `noindex,follow`; são públicas, não privadas. Não bloquear sua leitura por login ou robots.txt, pois precisam estar acessíveis ao Google.

| Aplicativo | Página inicial | Privacidade | Termos |
| --- | --- | --- | --- |
| Backups Malu | `/integracoes/backups-malu/index.html` | `/integracoes/backups-malu/privacidade.html` | `/integracoes/backups-malu/termos.html` |
| Backups Matheo | `/integracoes/backups-matheo/index.html` | `/integracoes/backups-matheo/privacidade.html` | `/integracoes/backups-matheo/termos.html` |

Executar `python scripts/empacotar.py --destino E:/SMDevStudio-publicacao` gera uma pasta nova, sem sobrescrever candidatas anteriores. O ZIP contém somente 13 arquivos aprovados por lista explícita. Manifesto SHA256, hash do ZIP e roteiro ficam fora do ZIP. Validar novamente após qualquer edição.

Publicar SOMENTE o conteúdo de `site-publico.zip` em uma raiz exclusiva do site. Nunca enviar o repositório inteiro, `.git`, scripts, documentos, backups ou credenciais. Não usar o servidor Python de prévia em produção. Nenhum arquivo do pacote configura banco, aplicação, OAuth ou servidor automaticamente.

## Antes da janela

1. Confirmar destino, acesso autorizado, domínio principal e e-mail ativo de suporte nos dois projetos Google. O site usa WhatsApp e o e-mail de privacidade `privacidade@smdevstudio.com.br`; não inventar outros endereços.
2. Revisar identificação do responsável e correspondência dos avisos com a operação real. Confirmar retenção e proteção dos tokens em repouso antes de classificar a integração como pronta para produção; ACL local não comprova criptografia em repouso.
3. Exportar zonas dos dois domínios, capturar redirecionamentos, SSL, proxy/CDN, TTL e nameservers em guarda privada. Registrar versão anterior do site e raiz de publicação. Não alterar registros de aplicações ou e-mail.
4. Conferir DNS autoritativo de cada domínio. Registrador e operador de DNS podem ser diferentes. Nunca redefinir a zona ou importar uma zona genérica. A migração planejada de nameservers do `.com` segue exclusivamente as fases e controles DNSSEC do plano Cloudflare.
5. Preparar hospedagem exclusiva e testar o ZIP em endereço de prévia, com recursos, navegação, status 404 real e cabeçalhos. Não criar wildcard para subdomínios.
6. Guardar um site anterior funcional ou uma página de manutenção estática validada como retorno. O antigo redirecionamento para uma origem com erro 525 não é recuperação funcional.

## Plano de DNS e HTTPS (aplicar somente após autorização)

1. Se necessário, reduzir TTL somente dos registros web afetados e aguardar o TTL anterior antes da troca. Reconsultar os registros imediatamente antes de editar.
2. Preparar certificados válidos para cada hostname que receber HTTPS, inclusive aliases de redirecionamento. Confirmar CAA, mecanismo de validação e renovação. Não desativar validação TLS para contornar 525. Com CDN, validar também certificado e nome da origem.
3. Remover/substituir o redirecionamento antigo `.com` para `.com.br` na mesma janela coordenada. Apontar apenas apex/www dos domínios institucionais conforme instruções do destino escolhido. Tratar A e AAAA juntos: não deixar IPv6 apontando para a origem antiga. Não alterar `matheo`, outros subdomínios, MX, TXT ou a zona appmalu.
4. Colocar o site na raiz exclusiva. Redirecionar HTTP para HTTPS. Testar `.com` como principal e só então configurar `.com.br`/www para ele, sem ciclo. Usar redirecionamento temporário na validação e permanente após o aceite, pois navegadores podem guardar 301.
5. Configurar 404 para responder HTTP 404 com `404.html`; não fazer fallback de qualquer caminho para index. Bloquear listagem de diretórios/arquivos ocultos e servir somente arquivos públicos.
6. Aplicar e testar `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin` e proteção contra enquadramento. CSP deve permitir apenas os recursos locais necessários; conferir primeiro os atributos style existentes antes de endurecer style-src. HSTS está ativo na borda com `max-age=31536000; includeSubDomains` (commit e404446, intencional): todos os subdomínios precisam servir HTTPS válido. Preload não está aplicado. Cache curto/revalidação para HTML, CSS e JS sem hash no nome.
7. Validar HTTPS sem exceções, IPv4/IPv6 quando publicado, ausência de loops, página comercial, seis páginas OAuth, logo, CSS/JS, WhatsApp e 404. Conferir saúde externa das aplicações antes/depois. Qualquer regressão interrompe a janela.

## Retorno

- Problema de conteúdo: voltar à versão anterior guardada na raiz exclusiva; invalidar somente o cache do site. Não restaurar bancos nem volumes de aplicações.
- Problema de DNS/certificado: restaurar somente os registros e redirecionamentos alterados a partir da captura prévia, respeitando TTL/caches. Nunca usar reset de zona. Restauração de DNS não é instantânea.
- Se o estado antigo já era quebrado, manter a página estática de manutenção previamente testada em vez de declarar o erro anterior como sucesso. Não emitir novos consentimentos OAuth até as páginas estarem válidas.
- Na VPS aprovada, retorno da entrada compartilhada precisa de roteiro próprio validado e autorização. Este roteiro institucional não autoriza reiniciar o Malu nem substituir seu proxy.

## Depois do site válido: Google e recuperação

1. Conferir os dois projetos próprios de backup existentes. Não alterar o projeto Google usado pelo sistema original, não criar novos clientes e não ampliar `drive.file` por conveniência.
2. Preencher cada conjunto de URLs acima com o domínio HTTPS válido. Conferir nome do aplicativo, contato de suporte ativo, domínio autorizado e propriedade no Search Console quando exigida. Cadastro de TXT, se necessário, deve ser aditivo e explicitamente autorizado.
3. Verificar a elegibilidade para dispensa de revisão por uso pessoal. Publicar o status OAuth e verificar/publicar branding são passos distintos; seguir o estado real do console sem prometer aprovação.
4. Após sair de Testing, renovar autorização no navegador suportado do Google, preservando a identidade dos clientes e destinos. Conferir escopo e proteção dos tokens sem expor seus valores.
5. Fazer envio com nome novo, download, SHA256 e restauração isolada por produto; validar recuperação com o material de custódia disponível. Não sobrescrever nem apagar acervo. Manter cópias no E:.
6. Só então definir recorrência, detecção de backup ausente e alerta de falha. Publicar o site não ativa backups recorrentes nem coleta um backup novo da VPS.

Fontes: [OAuth](https://developers.google.com/identity/protocols/oauth2/policies), [branding](https://developers.google.com/identity/protocols/oauth2/production-readiness/brand-verification), [dados de APIs](https://developers.google.com/terms/api-services-user-data-policy), [tokens](https://developers.google.com/identity/protocols/oauth2#expiration).
