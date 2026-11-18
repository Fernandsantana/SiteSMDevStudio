# Contato SMTP e eventos de e-mail

O formulário envia à caixa fixa `contato@smdevstudio.com.br`, também usada como remetente;
Reply-To contém o endereço informado pelo visitante. Nenhuma credencial fica no navegador.
Não há serviço de formulário externo nem envio automático. Procedimento em [PUBLICACAO.md](PUBLICACAO.md).

## Revisar sem enviar

Com Python 3.11 ou posterior, na raiz:

```sh
python server/contact.py --preview --port 5185
```

Abrir http://127.0.0.1:5185/index.html#contato. Prévia informa que não envia e preserva campos;
não expor o repositório à internet.

## Envio local autorizado

```sh
python server/contact.py --smtp --port 5185
```

PowerShell: `scripts/iniciar-contato.ps1` abre prévia; `-Enviar` habilita envio.
Inserir credencial no prompt oculto; permanece apenas na memória. Nunca no chat/código/frontend.
Sessão de webmail não fornece automaticamente senha SMTP. O transporte usa
`smtp.hostinger.com:465`, TLS e certificado validado. Falha preserva campos. Aceitação SMTP
permite sucesso, mas recebimento na caixa principal exige conferência. Não repetir envios
sem necessidade; usar senha de aplicativo se exigida pela autenticação do provedor.

## Verificação automatizada

```sh
python -m unittest discover -s server -p 'test_*.py' -v
node --check script.js
python scripts/validar_containers.py
```

Unitários substituem SMTP e não enviam. Cobrem destino, Reply-To, validação, origem, honeypot,
tamanho/frequência, repetição, falhas, prévia, sem JS, segredo e proxy. Ensaio Docker usa
projeto exclusivo, arquivos públicos, segredos fictícios e SMTP sem saída de rede.
Requer imagens locais `smdevstudio-site:local-final`, `smdevstudio-contact:local-final`
e `smdevstudio-email-events:local-vps`; construir segundo PUBLICACAO com essas tags.
Confere também assinatura/deduplicação do webhook.

Critérios: página/health 200; métodos indevidos 405; origem indevida 403; formulário inválido
400; corpo excessivo 413; arquivos privados 404. Conferir Caddy, UID/permissões, integridade
dos pacotes e saúde dos três componentes. Ensaios fictícios não validam credencial real,
TLS público, DNS, recebimento SMTP ou provedor remoto.

## Limites e privacidade

Produção exige `SMTP_PASSWORD_FILE`, origens HTTPS explícitas e backend sem porta pública.
Proxy sobrescreve X-Contact-IP; `CONTACT_TRUSTED_PROXY` corresponde à cadeia verificada.
Proteção no gateway complementa honeypot e limites conforme tráfego observado.
Nunca servir `server/`, `.env`, configuração ou segredos como arquivos estáticos.

Limites de implementação: cinco tentativas por origem de rede em dez minutos, cinquenta
globais, dezesseis conexões, corpo até 24 KiB e mensagem até 5.000 caracteres.
Deduplicação em memória até uma hora; reinício limpa o estado. Falha após aceitação SMTP
deixa resultado incerto; não prometer entrega única. O serviço não persiste mensagens;
o recebimento segue a política da caixa de e-mail.

## Eventos de entrega Resend

`email-events`, overlay `infra/compose.events.yaml`, sem porta publicada nem saída de internet.
Valida assinatura Svix sobre corpo original, janela de cinco minutos, limite de 256 KiB e
deduplicação pelo identificador do webhook. Segredo separado do SMTP. SQLite guarda metadados
mínimos, sem corpo/assunto/destinatário, até dez mil eventos ou noventa dias; limpeza na chegada
de eventos. Resumo cobre 24 horas.

`scripts/coletar-eventos-email.py` e `infra/email-events-monitor.*` coletam o resumo.
Falha de coleta ou último evento problemático gera falha; entrega posterior resolve atraso.
Não alterar automaticamente cadastros, convites ou estados de negócio. Sem rastreamento de
abertura/clique. Entrega confirmada não garante classificação fora do spam.
Testar assinatura ausente/adulterada/expirada, repetição, persistência e resumo inacessível
externamente; não divulgar payloads ou identificadores reais.

## Recuperação e decisões futuras

Configuração/segredos exigem guarda cifrada recuperável, separada da release, conforme PUBLICACAO.
Existência de credencial não autoriza novos acessos. Healthcheck não substitui teste de entrega;
backup não substitui restauração. Guardar evidências e autorizações técnicas privadamente.

Conferir SPF/DKIM/DMARC e relatórios no DNS atual. Endurecer DMARC após observar remetentes
legítimos, sem SPF duplicado ou rejeição indiscriminada. Não habilitar outro recebimento para
disputar o domínio da caixa. Endereço inválido exige confirmação do titular; não corrigir
domínio ou reenviar automaticamente. Quotas/planos comerciais não são fixados neste documento.
