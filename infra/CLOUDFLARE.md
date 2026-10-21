# Cloudflare para SM Dev Studio e Matheo

Janela D158 autorizada em 20/10/2026. Estado às 21:17 Brasília: `.com` delegado à Cloudflare
Free, A na VPS DNS-only, www CNAME DNS-only, HTTPS 200/302. AAAA antigos dos dois domínios
removidos com confirmação. `.com.br` apontado à VPS em DNS-only às 22:02 Brasília; certificados
emitidos e aceite público aprovado nos quatro nomes; proxy/Full strict pendentes de decisão.
Borda independente já instalada; Malu saudável, DNS e aplicação preservados. Matheo não publicado.
Sequência retomada com autorização; apontamento `.com.br` concluído. Ver o [documento de continuidade](../../appmatheo/docs/continuidade-publicacao.md)
no repositório irmão appmatheo.

## Estado observado e destino

Exportações anteriores das duas zonas estão preservadas em guarda privada. `.com.br` tinha SSL
Full, zero Page Rules, zero Redirect Rules e nenhuma Workers Route; isso não audita todas as regras.
Full strict/Universal SSL final ainda exigem conferência. Registros de e-mail/verificação/FTP foram
preservados. Redirect antigo Hostinger não foi removido. Não refazer delegação ou exclusões concluídas.
Fonte do plano DNS/CDN; [publicação e OAuth](../PUBLICACAO.md).

Destino: as duas zonas SM na Cloudflare; registrador permanece Hostinger. Site principal `.com`;
aliases redirecionados pela borda Caddy já preparada, sem duplicar regras de redirect na CDN.
Matheo usa `matheo.smdevstudio.com`, com ciclo de publicação separado. Não criar wildcard.

| Zona | Nome | Tipo / conteúdo a preencher na janela | Estado final |
| --- | --- | --- | --- |
| smdevstudio.com | @ | A / IPv4 da VPS conferido em guarda privada | Proxied, TTL Auto |
| smdevstudio.com | www | CNAME / smdevstudio.com | Proxied, TTL Auto |
| smdevstudio.com | matheo | A / IPv4 da VPS, só após piloto liberado | Proxied, TTL Auto |
| smdevstudio.com.br | @ | A / IPv4 da VPS conferido | Proxied, TTL Auto |
| smdevstudio.com.br | www | CNAME / smdevstudio.com.br | Proxied, TTL Auto |

Não publicar AAAA de origem sem IPv6 validado; retirar o AAAA web antigo na janela de apontamento.
IPv6 de visitantes na Cloudflare não exige AAAA na origem. Preservar demais registros ao migrar:
MX, SPF, DKIM, DMARC, CAA, TXT Google e subdomínios. Limpeza de legados é tarefa separada.
Não usar esta tabela como importação completa de zona: ela descreve somente os registros web.

## Configuração candidata no painel

- SSL/TLS: Full (strict), somente com certificado válido na origem e Universal SSL ativo cobrindo
  os hosts. Preferir certificado público do Caddy, permitindo retorno DNS-only. Não usar Flexible.
- HTTPS e aliases: Caddy conserva HTTPS e redireciona aliases para `.com` com 302 na validação,
  preservando caminho/consulta. Tornar permanente só após aceite. Sem redirect global para apex.
- Não ativar HSTS includeSubDomains/preload, Rocket Loader, Cache Everything, Workers, Access,
  desafios globais de bots ou regras experimentais nesta primeira configuração.
- Cache Rules, zona `.com`: expressão `(http.host eq "matheo.smdevstudio.com")`, ação
  **Cache eligibility: Bypass cache**. Aplicar após qualquer regra geral concorrente e conferir
  precedência. Bypass cobre API, arquivos, HTML, service worker, manifesto e imagens privadas.
- Site e aliases: manter cache padrão respeitando os cabeçalhos da origem, sem forçar Edge TTL;
  Browser Cache TTL respeita origem. A candidata estática usa `Cache-Control: no-cache`.
  Ganhos de cache podem ser avaliados depois com nomes de assets versionados; não forçar agora.
- Bypass da CDN não controla cache do navegador/service worker. Conferir `no-store` das respostas
  privadas na aplicação e invalidação do PWA. Não alterar regras de sessão/permissões por causa da CDN.
- Não desabilitar proteções padrão indiscriminadamente. Conferir eventos de segurança nos testes;
  exceções futuras devem ser estreitas e justificadas, sem liberar toda a API por conveniência.

## Pré-requisitos da origem

O proxy público atual pertence ao Malu. Não adicionar SM/Matheo nesse container. A entrada
independente candidata em `appmatheo/infra/convivencia` ainda depende da janela própria, pausa,
backup recuperável, coordenação de jobs e retorno descritos em `appmatheo/docs/operacao.md`.
Usar `compose.yaml` e `smdevstudio.caddy` desta pasta para o site; overlay de borda só em cópia
revisada da entrada independente. O override `compose.ensaio.yaml` é exclusivamente local.
Não substituir o Caddyfile inteiro nem executar `compose down` global. Borda com admin off exige
recriação controlada, não presumir reload; trocar conteúdo estático recria só o serviço do site.

Antes do proxy Matheo, ensaiar Cloudflare -> borda -> API: HTTPS, IP real e rate limit.
A API atual confia em proxy cadastrado com um salto. Não ampliar redes confiáveis nem confiar
cegamente em CF-Connecting-IP/X-Forwarded-For. A borda precisa validar a origem Cloudflare e
normalizar o cabeçalho para o contrato da API; teste contra cabeçalhos forjados é condição de liberação.
A candidata D141 do Matheo foi ensaiada localmente com TLS e 48 verificações; consultar
`appmatheo/scripts/ensaio-proxy/README.md`. Emissão/renovação pública e tráfego CDN real continuam
pendentes da janela. A preparação não instala a cadeia no servidor. Não aplicar trusted proxies globais que mudem a interpretação do tráfego Malu.
Não restringir firewall global a IPs Cloudflare: Malu permanece com acesso direto à mesma VPS.

## Janela futura, separada por fases

1. Obter autorização específica. Exportar zonas/regras/nameservers/DS-DNSSEC/CAA em guarda privada,
   registrar saúde Malu, backup e rollback. Proteger conta Cloudflare com MFA e recuperação guardada.
2. Criar zona `.com` Free e reproduzir a zona completa conferida, inicialmente DNS-only preservando
   destinos existentes. Não confiar só no scan automático. Não tocar na delegação `.com.br`.
3. Conferir DNSSEC: se houver DS antigo no registrador, remover na janela e aguardar expiração antes
   da troca de nameservers pelo procedimento do provedor. DS incompatível causa SERVFAIL.
   Delegar `.com` aos nameservers realmente atribuídos; verificar autoritativos e dois resolvedores.
   Manter zona antiga disponível. Após estabilidade, ativar DNSSEC Cloudflare e cadastrar seu novo DS.
4. Só com origem pronta e transição independente aprovada, remover o redirect antigo `.com` -> `.com.br`,
   apontar web A/AAAA coerentes e validar emissão/renovação ACME do Caddy. Separar mudança DNS de proxy.
   DNS-only temporário requer origem pública saudável; não expor piloto inacabado. Verificar CAA e
   HTTP-01 acessível; o proxy pode impedir TLS-ALPN-01. Não adotar token/plugin DNS sem necessidade.
5. Ativar proxy do site só com TLS origem e certificado Cloudflare prontos. Aplicar Full (strict).
   Testar site e aliases. Em fase posterior, com fluxos do piloto liberados, repetir para Matheo,
   preparando a regra bypass antes de ativar seu proxy. Não criar DNS Matheo antecipadamente.
6. Verificar renovação ACME com HTTP-01 passando pela CDN, sem desafios/redirecionamentos interferentes.
   Registrar evidência e monitorar erros TLS/5xx e saúde Malu antes/depois de cada fase.

## Aceite e retorno

- Site: HTTPS sem exceção nos quatro hosts, redirects sem ciclo preservando URL, seis páginas OAuth
  acessíveis sem challenge/login, CSS/logo/JS, 404 real e cabeçalhos. Não há validação pública feita.
- Matheo: login/saída, recuperação manual, bloqueio do negócio, isolamento entre perfis, upload,
  atualização/instalação PWA e conexões persistentes se utilizadas. Repetir resposta autenticada
  com dois usuários: nunca HIT/STALE/UPDATING nem dados cruzados; BYPASS ou DYNAMIC são esperados.
- Ensaiar retorno DNS-only com certificado público válido. Se proxy falhar, desativar somente o proxy
  do hostname afetado após confirmar origem segura. Se regra falhar, reverter só essa regra.
- Conteúdo: voltar release exclusiva e invalidar URLs afetadas, sem purge geral da zona compartilhada.
  Não restaurar banco para desfazer DNS/CDN; preservar escritas ocorridas após publicação.
- Delegação: rollback de nameservers exige zona antiga válida e DS compatível (ou retirada segura do
  DS novo antes do retorno). Propagação não é instantânea; guardar instruções/valores anteriores.
- Origem antiga SM com 525 não é retorno funcional: usar release anterior ou manutenção validada.
  Retorno da borda compartilhada segue roteiro próprio; qualquer regressão Malu interrompe a janela.

## Fontes e limites

Revisão documental local; nenhuma regra aplicada ou certificado emitido. Modelo não é payload de API.
[Migração DNS](https://developers.cloudflare.com/dns/zone-setups/full-setup/setup/),
[DNSSEC](https://developers.cloudflare.com/dns/dnssec/),
[Full strict](https://developers.cloudflare.com/ssl/origin-configuration/ssl-modes/full-strict/),
[Cache Rules](https://developers.cloudflare.com/cache/how-to/cache-rules/settings/).
