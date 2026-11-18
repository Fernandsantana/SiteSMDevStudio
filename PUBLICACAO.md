# Publicação e recuperação

Procedimento vigente para site, contato SMTP e eventos. Conferir configuração real e escopo
autorizado; este documento público não guarda acessos, inventários ou recibos. GitHub,
commit local e publicação são estados distintos; organizar documentos não publica o site.

## Pacotes e imagens

```sh
python scripts/empacotar.py --destino /caminho/privado/fora-do-repositorio
python -m unittest discover -s server -p 'test_*.py' -v
node --check script.js
docker build -f infra/Dockerfile -t smdevstudio-site:candidata .
docker build -f server/Dockerfile -t smdevstudio-contact:candidata server
docker build -f server/Dockerfile.events -t smdevstudio-email-events:candidata server
```

Empacotador cria candidata nova e verifica links/âncoras, CRC e SHA256. `site-publico.zip`
contém os 14 arquivos públicos; `servico-contato.zip` contém serviços/testes/configuração,
sem segredos, para extração fora da raiz servida. Manifesto e hashes ficam separados.
Conferir lista atual no script, arquitetura, IDs imutáveis e vulnerabilidades atuais das
imagens. Bases fixadas exigem atualização e novo ensaio. [Testes](CONTATO.md#verificação-automatizada).

## Configuração e segredos

Partir de `infra/runtime.env.example`, guardado fora do repositório. Definir `SM_SITE_IMAGE`,
`SM_CONTACT_IMAGE`, `SM_EMAIL_EVENTS_IMAGE`, release em `SM_RELEASE_DIR`, `CONTACT_ORIGINS`
HTTPS explícitas e `SM_TRUSTED_PROXY_CIDRS` restritos aos proxies verificados. Eventos exigem
`SM_EMAIL_EVENTS_DATA_DIR` precriado e gravável pelo UID 10001. Não sobrepor configuração real
com configuração de laboratório.

Provisionar `SM_SMTP_SECRET_FILE` e `SM_EMAIL_EVENTS_SECRET_FILE` separadamente, por entrada
oculta/gerenciador de segredos, fora da release/Git. Diretório root 0700; arquivos UID/GID
10001 e modo 0400, montados somente leitura no serviço correspondente. Compose respeita
permissões do arquivo no host; uid/mode no YAML não garante conversão. Nunca colocar valores
em argumentos, ambiente, logs, imagens, ZIPs ou documentação. Administrador host/Docker pode
ler o arquivo; Compose não cifra a origem.
Guardar cópia cifrada recuperável da configuração/segredos com chaves em custódia separada.
Rotação exige arquivo novo, remontagem e teste; preparar retorno antes de revogar credencial.
Não incluir segredos em backups comuns da release; verificar recuperação sem exibir valores.

## Rede, proxy e saúde

Contato/eventos não publicam portas. Contato precisa de saída SMTP TLS; eventos não precisa
de internet. Manter execução sem root, filesystem somente leitura, capabilities removidas,
limites de CPU/memória/processos/logs e dados SQLite.
Encaminhar `/api/contact` e `/api/email-events/resend` aos serviços respectivos. Sanitizar
X-Forwarded-For, sobrescrever X-Contact-IP e confiar só na cadeia verificada, nunca em todas
as redes privadas. SMTP valida certificado; webhook exige assinatura do corpo original.
Não impor challenge interativo ao provedor.
Conferir web/contact/email-events além de HTTPS. Saúde HTTP não comprova entrega. Healthchecks
Python usam timeout de 10 s e start period de 15 s, mantendo timeout HTTP de 2 s. Configuração
conferida em operação; não atribuir a ela uma causa de falha que não foi comprovada.

```sh
docker compose --env-file /caminho/privado/runtime.env -f infra/compose.yaml -f infra/compose.events.yaml config --quiet
```

## Aplicação e aceite

1. Preservar release, configuração, IDs e recuperação anteriores. Conferir hashes, segredos,
   permissões, SQLite, projeto Compose e redes realmente instalados.
2. Extrair somente ZIP público em nova release. Atualizar serviços necessários sob o mesmo
   projeto; evitar recriar gateway, mudar DNS ou afetar serviços alheios. Frontend, proxy e
   backends devem manter contrato compatível.
3. Conferir saúde por componente, HTTPS, redirects preservando URL, CSP, MIME, cache, 404 real,
   arquivos privados inacessíveis e páginas de integração sem login/challenge.
4. Testar contato desktop/celular/sem JS: validação, origem, tamanho, frequência e erros sem
   perda de campos. Quando autorizado, enviar um teste e conferir recebimento e Reply-To;
   aceitação SMTP não comprova chegada à caixa principal.
5. Conferir assinatura inválida recusada, deduplicação e resumo inacessível pela internet.
   Segredo fictício não comprova webhook real. Guardar resultados e retorno privadamente.
6. Só declarar publicada a versão conferida; regressão interrompe aplicação.

## Recuperação e limites

Voltar release, imagens e configuração compatíveis preservando SQLite/segredos. Não restaurar
bancos alheios nem remover volumes. Retorno de dados sobre eventos posteriores exige avaliação
de consistência. DNS/CDN seguem [roteiro próprio](infra/CLOUDFLARE.md), sem reset/purge global.
Controles SMTP em memória são por processo e se perdem no reinício: manter uma instância até
existir coordenação compartilhada. Falha após aceitação deixa resultado incerto; não prometer
entrega única. Monitor, backup e restore são verificações distintas. Publicar páginas de
integração não ativa OAuth/backups; exigem escopo e validação próprios, com permissões mínimas.
