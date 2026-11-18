# SM Dev Studio — site institucional

Site em https://smdevstudio.com. Apresenta software sob medida; interfaces conceituais são
identificadas como demonstrações, sem depoimentos ou resultados inventados.
Contato: `contato@smdevstudio.com.br`; privacidade: `privacidade@smdevstudio.com.br`.
Contato SMTP e receptor de eventos estão implementados. Edição local/commit não significa
publicação nem atualização do GitHub.

## Estrutura e referências

- HTML, `styles.css`, `script.js`, `assets/`: frontend nativo, sem build ou dependências.
- `server/`: contato SMTP e eventos assinados; nunca servir como arquivos públicos.
- `infra/`, `scripts/`: configuração, validação e empacotamento.
- `integracoes/`: páginas públicas com noindex sobre backups; noindex não garante sigilo.

[CONTATO.md](CONTATO.md) define serviços/testes; [PUBLICACAO.md](PUBLICACAO.md) é o procedimento
único de publicação/recuperação; [Cloudflare](infra/CLOUDFLARE.md) cobre DNS/TLS/proxy/cache.

## Revisão local

```sh
python server/contact.py --preview --port 5185
python -m unittest discover -s server -p 'test_*.py' -v
node --check script.js
```

Abrir http://127.0.0.1:5185/index.html#contato. Prévia não envia; não expor o repositório.
Envio real exige credencial e escopo próprios. Não há lint/typecheck/build frontend.

## Conteúdo e design

Preservar logo original, paleta rosa/violeta, contatos e nome acessível da marca. Usar WebP
na exibição sem descartar a arte original. Cabeçalho/rodapé consistentes, identificação da
empresa e links legais. Não usar travessões no conteúdo público. Prazo, investimento e
mudanças dependem de avaliação/contratação; demonstrações não representam dados de clientes.

Conteúdo, links e formulário funcionam sem JavaScript. Preservar teclado, Escape/retorno de
foco, toque, rolagem vertical e alvos de pelo menos 44 px. Respeitar movimento reduzido,
pausa com aba oculta/fora da viewport e controle de pausa acessível.
Validar 320 px até desktop amplo, paisagem, contraste, menu, carrossel, comparador, módulos,
contato e páginas legais; conferir overflow/foco/erros JS. Emulação e Lighthouse local não
comprovam Safari/iOS físico, leitor de tela ou desempenho de campo.

## Manutenção

Repositório público: não incluir segredos, dados pessoais, acessos, configuração privada,
backups ou inventário de infraestrutura. Evidências ficam privadas, fora do Git.
Publicar só a lista pública do empacotador, nunca a pasta inteira. Nova edição pública exige
pacote validado novo. Não repetir roteiros antigos nem operar fora do escopo autorizado.
