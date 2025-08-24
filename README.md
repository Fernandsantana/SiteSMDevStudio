# SM Dev Studio - Site Institucional

Site institucional responsivo da SM Dev Studio, especializada em desenvolvimento de sistemas personalizados.

## 🚀 Funcionalidades

- **Design Responsivo**: Otimizado para todos os dispositivos
- **Animações Suaves**: Transições e efeitos visuais modernos
- **Formulário de Contato**: Sistema de envio de emails funcional
- **Performance Otimizada**: Carregamento rápido e eficiente
- **SEO Otimizado**: Meta tags e estrutura para melhor indexação

## 📧 Configuração do Sistema de Email

### ⚠️ IMPORTANTE: Configurar Email Antes de Usar

O formulário de contato precisa ser configurado para funcionar. Escolha uma das opções abaixo:

### Opção 1: Formspree (Recomendado - Mais Simples)

1. **Criar conta no Formspree**:
   - Acesse [formspree.io](https://formspree.io)
   - Crie uma conta gratuita
   - Crie um novo formulário

2. **Configurar no código**:
   - Abra `config.js`
   - Localize a seção `form.email.formspree`
   - Substitua `'https://formspree.io/f/xpzgqjqj'` pela sua URL do Formspree

```javascript
formspree: {
    enabled: true,
    endpoint: 'https://formspree.io/f/SUA_URL_AQUI', // SUA URL DO FORMSPREE
    redirect: false
}
```

3. **Testar**:
   - Envie um email de teste
   - Verifique se chegou na caixa de entrada

### Opção 2: EmailJS (Alternativo)

1. **Criar conta no EmailJS**:
   - Acesse [emailjs.com](https://emailjs.com)
   - Crie uma conta gratuita
   - Configure um serviço de email (Gmail, Outlook, etc.)
   - Crie um template de email

2. **Configurar no código**:
   - Abra `config.js`
   - Localize a seção `form.email.emailjs`
   - Substitua os valores pelos seus:

```javascript
emailjs: {
    enabled: true, // Mudar para true
    serviceId: 'SEU_SERVICE_ID',
    templateId: 'SEU_TEMPLATE_ID',
    userId: 'SEU_USER_ID'
}
```

3. **Ativar EmailJS**:
   - No `config.js`, mude `formspree.enabled: false`
   - Mude `emailjs.enabled: true`

### Opção 3: Backend Próprio (Avançado)

Se você tem um servidor próprio, pode implementar um endpoint `/api/send-email`:

1. **Configurar backend**:
   - Implemente o endpoint no seu servidor
   - Configure autenticação e validação

2. **Ativar no código**:
   - No `config.js`, mude `backend.enabled: true`
   - Configure o endpoint correto

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
