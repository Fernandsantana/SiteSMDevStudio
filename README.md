# SM Dev Studio — site institucional

Apresentação comercial de software sob medida, centrada no contexto da operação e de quem usa.
Contatos públicos: WhatsApp e o e-mail de privacidade `privacidade@smdevstudio.com.br`.
Rodapé de todas as páginas identifica razão social, CNPJ, cidade e e-mail (Decreto 7.962/2013). Sem catálogo de produtos próprios ou depoimentos fictícios.
As interfaces são conceituais; essa definição fica nos termos, sem legenda na apresentação.
Os termos descrevem avaliação de viabilidade, planejamento, proposta com prazo e investimento,
aprovação formal e avaliação de mudanças. A privacidade explica o uso dos dados nessa avaliação.
Não usar travessões no conteúdo público. A ilustração de integração utiliza a logo oficial.

## Estrutura e identidade

- `index.html`: proposta de valor, possibilidades, processo e contato.
- `privacidade.html` e `termos.html`: exclusivamente o site institucional.
- `assets/logo-sm.png`: logo oficial fornecida pelo titular, preservada sem alteração.
- `styles.css`: paleta rosa/violeta da marca, layouts responsivos e animações CSS/SVG.
- `script.js`: menu móvel, carrossel e avanço automático.

HTML, CSS e JavaScript nativos, sem build, dependências de execução, fontes externas, analytics
ou cookies. Conteúdo e links funcionam sem JavaScript. Movimento respeita redução de animação
no sistema. Carrossel tem setas, teclado e rolagem por toque; avanço automático a cada 6,5 segundos
quando visível, suspenso durante leitura com mouse/foco e toque. Botão "Pausar animações"
(aria-pressed, só na página inicial) pausa ticker, órbitas, flutuações e o avanço automático;
a escolha não é guardada no navegador. Não envia mensagens automaticamente.

## Prévia e validação

Execute `python -m http.server 5180 --bind 127.0.0.1` nesta pasta e abra
http://127.0.0.1:5180/index.html. Servidor apenas para prévia; não expor o repositório na internet.
Conferidos navegação, menu, carrossel, páginas internas e ausência de transbordamento em larguras
móveis de 320/390 px e desktop. Sem erros JavaScript observados na navegação verificada.

Referências visuais: [Work & Co](https://www.work.co/), [Clay](https://clay.global/about)
e [Linear](https://linear.app/). Orientam hierarquia, concisão e apresentação visual; sem cópia
 de ativos ou evidência de aumento de conversão desta versão.

## Manutenção e publicação

Manter cabeçalho, rodapé e contatos consistentes nas três páginas. Nenhum segredo, token, dado
 de cliente ou arquivo de backup deve entrar neste repositório público. Ativos antigos preservados.
Nenhum commit, push, alteração de DNS ou publicação realizado nesta preparação.
Antes de publicar: revisar política e identificação do responsável, conferir WhatsApp, HTTPS,
redirecionamento entre domínios e configuração de logs/retenção da hospedagem.
As políticas comerciais permanecem separadas. A documentação pública própria de cada integração
fica em `integracoes/backups-malu/` e `integracoes/backups-matheo/`, sem entrada no menu comercial.
As seis páginas reaproveitam a identidade visual e detalham finalidade, acesso ao Drive, retenção,
revogação e recuperação, sem expor credenciais ou arquivos. São públicas com noindex, não privadas.

## Candidata para publicação

D146: `infra/Dockerfile` recompila Caddy com Go e dependências fixados, reaproveitando a receita
validada do Matheo com fontes próprias neste repositório; não depende do serviço Matheo em execução.
Build: `docker build -f infra/Dockerfile -t smdevstudio-site:d146 .`.
Definir `SM_SITE_IMAGE` com o ID completo conferido após build/load; Compose não baixa imagens.
Não usar novamente o digest antigo do Caddy. Imagem local candidata arquivada junto ao Matheo em
`E:/appmatheo/candidatas/d146-imagens`, sem substituir a prévia existente.
Ensaio isolado: 13 arquivos públicos idênticos, cabeçalhos, quatro recusas 404 e POST 405.
Trivy: zero HIGH/CRITICAL; um aviso OpenPGP, pacote impedido pelo teste de dependências do build.
Janela D147 local integrada ao Matheo aprovada com esta imagem, quatro trocas, site disponível
durante a pausa do Matheo e retorno para página sintética. Pacote em
`E:/appmatheo/candidatas/d147-20261020`, com site/imagem separados dos dados da aplicação.
Prévia existente preservada; sem deploy. Resultado não valida DNS/CDN ou certificado público.

O [roteiro de publicação e retorno](PUBLICACAO.md) registra a leitura da Hostinger, as pendências
da VPS, DNS/HTTPS e OAuth. O `.com` tem DNS Hostinger e redirect antigo para `.com.br`;
o `.com.br` usa DNS Cloudflare. Não foi encontrada hospedagem PHP/HTML separada disponível.

`python scripts/empacotar.py --destino E:/SMDevStudio-publicacao` valida links locais/âncoras,
empacota uma lista explícita de 13 arquivos e confere CRC e SHA256. Cada execução cria candidata
nova fora da raiz pública, com manifesto/hash e cópia do roteiro separados do ZIP.
`404.html` deve ser configurada na hospedagem para responder HTTP 404, não apenas servida como 200.
Publicar só o ZIP público, após autorização da janela na VPS aprovada. Preparação local não habilita OAuth,
não configura criptografia de tokens e não ativa rotina recorrente. Nenhum projeto de aplicação,
servidor, DNS ou serviço pago foi alterado durante essa preparação.

## Plano Cloudflare local

[Configuração e roteiro seguro](infra/CLOUDFLARE.md): zonas SM, site e Matheo no plano Free,
Malu preservado. Inclui DNSSEC, TLS na origem, bypass integral de cache do piloto, testes
e retorno por fase. A confiança dos cabeçalhos entre Cloudflare, borda e API ainda exige
ensaio específico antes do proxy do Matheo. Preparação não configura contas nem serviços.
