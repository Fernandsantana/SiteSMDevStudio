# DNS, TLS e proxy do site

Orientação para alterações autorizadas do site. Conferir configuração real; não repetir
migrações históricas. Site canônico: https://smdevstudio.com. Preservar aliases, caminhos e
consulta. Procedimento da aplicação: [PUBLICACAO.md](../PUBLICACAO.md).

## Antes de mudar

Guardar privadamente exportação da zona, regras, nameservers, DS/DNSSEC e CAA. Conferir origem,
certificados, registros web/e-mail, TTL, retorno e impacto na infraestrutura compartilhada.
Proteger acesso com MFA/recuperação; não registrar IPs de acesso ou credenciais neste documento.
Não confiar apenas na importação automática.

Preservar MX, SPF, DKIM, DMARC, verificações e subdomínios fora do escopo. Correio permanece
DNS-only; não inventar MX para domínio que só envia. Não publicar AAAA sem origem IPv6 validada.
DNSSEC incompatível com nameservers causa falha: coordenar DS conforme procedimento do provedor,
mantendo retorno possível. Separar mudança de delegação, apontamento e ativação do proxy.

## TLS, cache e cliente real

Full (strict) exige certificado válido na origem e certificado de borda pronto; nunca Flexible.
Preferir certificado público na origem que permita retorno DNS-only quando seguro. Conferir
renovação ACME, CAA e desafios HTTP sem interferência. Evitar redirects em múltiplas camadas.
Respeitar cache da origem: HTML/CSS/JS sem hash precisam de revalidação. Não aplicar Cache
Everything ou TTL forçado às APIs. Formulário, webhook e respostas privadas não são cacheáveis.
Não impor challenge interativo ao webhook ou páginas públicas das integrações.
Exceções de proteção devem ser estreitas e verificadas.

Confiar só nos proxies do caminho real: validar origem dos cabeçalhos, sanitizar IP encaminhado
e testar falsificação/rate limit. Não alterar firewall/proxies globais para resolver regra do site.
HSTS/includeSubDomains exige HTTPS válido nos subdomínios abrangidos; não habilitar preload
como efeito colateral.

## Aceite e retorno

Conferir HTTPS, redirects preservando URL, conteúdo, MIME, 404 real, cabeçalhos/cache e testes
próprios do formulário/webhook. DNS observado não comprova renovação futura. Verificar
resolvedores independentes e propagação após mudanças autorizadas.
Reverter só registros/regras afetados, preservando zona e serviços alheios. DNS-only exige
origem funcional/segura; retorno de nameservers exige zona antiga e DS compatíveis.
Propagação não é instantânea. Conteúdo retorna pela release anterior; não restaurar bancos,
remover volumes ou usar purge global para desfazer DNS/cache.
