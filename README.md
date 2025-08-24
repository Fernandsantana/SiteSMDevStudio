# SM Dev Studio - Site Institucional

Site institucional responsivo da SM Dev Studio, especializada em desenvolvimento de sistemas personalizados.

## 🚀 Funcionalidades

- **Design Responsivo**: Otimizado para todos os dispositivos
- **Animações Suaves**: Transições e efeitos visuais modernos
- **Formulário de Contato**: Sistema de envio de emails funcional
- **Performance Otimizada**: Carregamento rápido e eficiente
- **SEO Otimizado**: Meta tags e estrutura para melhor indexação

## 📧 Sistema de Email - Solução Simples

### ✅ **Funciona Imediatamente - Sem Configuração!**

O formulário de contato usa uma solução **super simples** que funciona em qualquer dispositivo:

1. **Usuário preenche o formulário**
2. **Cliente de email abre automaticamente** com dados pré-preenchidos
3. **Usuário clica em enviar** no seu email
4. **Email chega na caixa de entrada** normalmente

### 🎯 **Como Funciona**

- **Sem backend** necessário
- **Sem configuração** complexa
- **Funciona em todos os dispositivos**
- **Usa o cliente de email padrão** do usuário

### 📱 **Experiência do Usuário**

1. Preenche nome, telefone e descrição do projeto
2. Clica em "Enviar Mensagem"
3. Cliente de email abre automaticamente com:
   - **Para**: contato@smdevstudio.com.br
   - **Assunto**: Novo Projeto - [Nome]
   - **Mensagem**: Dados formatados do projeto
4. Usuário revisa e envia
5. Email chega normalmente na caixa de entrada

### 🔧 **Vantagens**

- ✅ **Zero configuração** necessária
- ✅ **Funciona imediatamente**
- ✅ **Sem dependências externas**
- ✅ **Sem limites de envio**
- ✅ **Sem spam/junk mail**
- ✅ **Usuário tem controle total**

### 📧 **Formato do Email**

```
Para: contato@smdevstudio.com.br
Assunto: Novo Projeto - [Nome do Cliente]

Olá SM Dev Studio!

Recebi um novo projeto através do site:

Nome: [Nome do Cliente]
Telefone: [Telefone]

Descrição do Projeto:
[Descrição detalhada do projeto]

Aguardo retorno!
```

### 🚀 **Alternativas Futuras**

Se quiser uma solução mais avançada no futuro:

1. **Formspree** - Para envio automático
2. **EmailJS** - Para templates personalizados
3. **Backend próprio** - Para controle total

Mas a solução atual é **perfeita** para a maioria dos casos!

## 📱 Sistema de Contato - WhatsApp

### ✅ **Contato Direto e Simples**

O site agora usa **WhatsApp** como método principal de contato:

1. **Botão CTA no Hero**: Direciona para WhatsApp com mensagem pré-preenchida
2. **Seção de Contato**: Card dedicado com botão WhatsApp e dicas
3. **Footer**: Mantém email apenas para referência

### 🎯 **Como Funciona**

- **Clique no botão WhatsApp** em qualquer lugar do site
- **WhatsApp Web/App abre** automaticamente
- **Mensagem pré-preenchida** com texto personalizado
- **Conversa direta** com a equipe

### 📱 **Experiência do Usuário**

1. Usuário clica em "Solicitar Orçamento" ou "Iniciar Conversa"
2. WhatsApp abre automaticamente com mensagem:
   ```
   "Olá! Gostaria de saber mais sobre os serviços da SM Dev Studio."
   ```
3. Usuário pode personalizar a mensagem
4. Conversa direta com atendimento

### 🔧 **Vantagens**

- ✅ **Contato instantâneo** via WhatsApp
- ✅ **Sem formulários** complexos
- ✅ **Conversa natural** e direta
- ✅ **Funciona em todos os dispositivos**
- ✅ **Mensagens pré-preenchidas** para facilitar
- ✅ **Email mantido** apenas no rodapé

### 💬 **Mensagens Pré-preenchidas**

- **Hero Section**: "Olá! Gostaria de solicitar um orçamento para meu projeto."
- **Seção Contato**: "Olá! Gostaria de saber mais sobre os serviços da SM Dev Studio."

### 📧 **Email no Rodapé**

O email `contato@smdevstudio.com.br` permanece apenas no rodapé para:
- **Referência** de contato
- **Profissionalismo** do site
- **Contato alternativo** se necessário

### 🚀 **Configuração**

Para alterar o número ou mensagens:

```javascript
// Em config.js
form: {
    whatsapp: {
        number: '5511990102690', // Seu número
        message: 'Sua mensagem personalizada'
    }
}
```

## 🛠️ Estrutura do Projeto

```
SMDevStudio/
├── index.html          # Página principal
├── styles.css          # Estilos principais
├── styles-sections.css # Estilos das seções
├── script.js           # JavaScript principal
├── config.js           # Configurações do site
└── README.md           # Este arquivo
```

## 📱 Responsividade

O site é totalmente responsivo e funciona em:
- 📱 **Mobile**: 360px - 768px
- 📱 **Tablet**: 768px - 1024px
- 💻 **Desktop**: 1024px+

## 🎨 Personalização

### Cores e Estilo
As cores principais estão definidas em `styles.css`:

```css
:root {
    --primary-purple: #8b5cf6;
    --electric-blue: #06b6d4;
    --neon-green: #10b981;
    /* ... outras cores */
}
```

### Conteúdo
Edite as informações da empresa em `config.js`:

```javascript
company: {
    name: 'SM Dev Studio',
    email: 'contato@smdevstudio.com.br',
    phone: '(11) 99010-2690',
    // ... outras informações
}
```

## 🚀 Deploy

### GitHub Pages
1. Faça push para o repositório
2. Vá em Settings > Pages
3. Selecione "Deploy from a branch"
4. Escolha a branch "main"

### Outros Hostings
- **Netlify**: Arraste a pasta para o Netlify
- **Vercel**: Conecte o repositório
- **Hostinger**: Faça upload via FTP

## 🔧 Manutenção

### Atualizar Informações
- **Empresa**: Edite `config.js` > `company`
- **Serviços**: Edite `config.js` > `services`
- **Tecnologias**: Edite `config.js` > `technologies`

### Adicionar Novas Seções
1. Adicione o HTML em `index.html`
2. Crie os estilos em `styles-sections.css`
3. Adicione animações se necessário

## 📊 Analytics e Monitoramento

O site inclui:
- Tracking de envios de formulário
- Monitoramento de erros
- Analytics básico (configurável)

## 🐛 Solução de Problemas

### Email não chega
1. ✅ Verificar se o Formspree/EmailJS está configurado
2. ✅ Verificar se a URL está correta
3. ✅ Verificar spam/junk mail
4. ✅ Testar com email diferente

### Site não carrega
1. ✅ Verificar se todos os arquivos estão presentes
2. ✅ Verificar console do navegador
3. ✅ Verificar se o servidor está funcionando

### Responsividade quebrada
1. ✅ Verificar CSS mobile
2. ✅ Testar em diferentes dispositivos
3. ✅ Verificar viewport meta tag

## 📞 Suporte

Para suporte técnico:
- **Email**: contato@smdevstudio.com.br
- **WhatsApp**: (11) 99010-2690

## 📄 Licença

Este projeto é propriedade da SM Dev Studio. Todos os direitos reservados.

---

**Desenvolvido com ❤️ pela SM Dev Studio**
