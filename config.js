// ===== CONFIGURAÇÕES DO SITE =====
const SITE_CONFIG = {
    // Informações da empresa
    company: {
        name: 'SM Dev Studio',
        tagline: 'O sistema que se molda ao Seu Negócio!',
        description: 'Desenvolvemos soluções tecnológicas personalizadas que se adaptam ao seu jeito de trabalhar.',
        email: 'contato@smdevstudio.com.br',
        phone: '(11) 99010-2690',
        whatsapp: '5511990102690',
        address: 'São Paulo, SP - Brasil',
        workingHours: 'Segunda a Sexta: 9h às 18h'
    },

    // Redes sociais
    social: {
        whatsapp: 'https://wa.me/5511990102690',
        email: 'contato@smdevstudio.com.br'
    },

    // Estatísticas da empresa
    stats: {
        projects: 14,
        technologies: 8,
        customization: 100,
        responseTime: 24
    },

    // Serviços oferecidos
    services: [
        {
            id: 'web',
            title: 'Desenvolvimento Web',
            description: 'Aplicações web modernas, responsivas e escaláveis com as melhores práticas de desenvolvimento.',
            icon: 'fas fa-laptop-code',
            features: ['Sites institucionais', 'E-commerce', 'Sistemas web complexos'],
            color: 'purple'
        },
        {
            id: 'mobile',
            title: 'Apps Mobile',
            description: 'Aplicativos nativos e híbridos para Android e iOS com foco em experiência do usuário.',
            icon: 'fas fa-mobile-alt',
            features: ['Apps nativos', 'Apps híbridos', 'PWA (Progressive Web Apps)'],
            color: 'pink'
        },

        {
            id: 'cloud',
            title: 'Soluções em Nuvem',
            description: 'Arquiteturas escaláveis, seguras e de alta disponibilidade na nuvem.',
            icon: 'fas fa-cloud',
            features: ['Migração para nuvem', 'Arquitetura serverless', 'DevOps e CI/CD'],
            color: 'green'
        }
    ],

    // Tecnologias utilizadas
    technologies: [
        { name: 'Python', icon: 'fab fa-python', color: '#3776ab' },
        { name: 'C# .NET', icon: 'fab fa-microsoft', color: '#512bd4' },
        { name: 'Angular', icon: 'fab fa-angular', color: '#dd0031' },
        { name: 'React', icon: 'fab fa-react', color: '#61dafb' },
        { name: 'JavaScript', icon: 'fab fa-js-square', color: '#f7df1e' },
        { name: 'Node.js', icon: 'fab fa-node-js', color: '#339933' },
        { name: 'SQL Server', icon: 'fas fa-database', color: '#cc2927' },
        { name: 'PostgreSQL', icon: 'fas fa-database', color: '#336791' }
    ],

    // Diferenciais da empresa
    features: [
        {
            title: 'Personalização Total',
            description: 'Sistemas desenvolvidos especificamente para suas necessidades e processos',
            icon: 'fas fa-magic',
            color: 'purple'
        },
        {
            title: 'Alta Performance',
            description: 'Soluções otimizadas para máxima eficiência e velocidade',
            icon: 'fas fa-rocket',
            color: 'blue'
        },
        {
            title: 'Segurança Garantida',
            description: 'Implementação das melhores práticas de segurança e proteção de dados',
            icon: 'fas fa-shield-alt',
            color: 'green'
        },
        {
            title: 'Suporte Contínuo',
            description: 'Acompanhamento completo do projeto e suporte técnico especializado',
            icon: 'fas fa-headset',
            color: 'pink'
        }
    ],

    // Sobre o projeto
    about: {
        title: 'Sobre Nosso Projeto',
        description: 'Somos uma empresa especializada em desenvolvimento de sistemas personalizados. Nossa missão é criar soluções tecnológicas que se adaptem perfeitamente ao seu negócio, oferecendo sistemas únicos e eficientes.',
        highlights: [
            'Sistemas 100% personalizados para sua empresa',
            'Desenvolvimento com tecnologias modernas e seguras',
            'Suporte completo durante e após a implementação',
            'Foco na experiência do usuário e usabilidade'
        ]
    },

    // Configurações de animação
    animations: {
        duration: 800,
        scrollThreshold: 0.1,
        particleCount: 50,
        statsAnimationDuration: 2000
    },

    // Configurações de formulário
    form: {
        requiredFields: ['name', 'phone', 'project'],
        placeholder: {
            name: 'Seu nome completo',
            phone: 'Seu telefone com DDD',
            project: 'Conte-nos sobre seu projeto, o que você precisa, funcionalidades desejadas, objetivos do sistema...'
        }
    },

    // Configurações de SEO
    seo: {
        title: 'SM Dev Studio - Sistemas que se Moldam ao seu Negócio',
        description: 'Desenvolvemos soluções tecnológicas personalizadas. O sistema se molda ao seu jeito de trabalhar.',
        keywords: 'desenvolvimento web, sistemas personalizados, aplicativos mobile, soluções em nuvem, SM Dev Studio',
        author: 'SM Dev Studio',
        ogImage: 'https://smdevstudio.com.br/og-image.jpg',
        twitterImage: 'https://smdevstudio.com.br/twitter-image.jpg'
    },

    // Configurações de cores (CSS Variables)
    colors: {
        primary: '#8b5cf6',
        secondary: '#06b6d4',
        accent: '#14f195',
        dark: '#0f172a',
        light: '#e2e8f0',
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b'
    },

    // Configurações de performance
    performance: {
        preloadFonts: true,
        preloadImages: true,
        enableServiceWorker: true,
        enableAnalytics: false,
        enableHotjar: false
    }
};

// ===== FUNÇÕES DE CONFIGURAÇÃO =====
class ConfigManager {
    constructor() {
        this.config = SITE_CONFIG;
    }

    // Atualizar informações da empresa
    updateCompanyInfo(newInfo) {
        this.config.company = { ...this.config.company, ...newInfo };
        this.applyCompanyInfo();
    }

    // Atualizar estatísticas
    updateStats(newStats) {
        this.config.stats = { ...this.config.stats, ...newStats };
        this.applyStats();
    }

    // Atualizar serviços
    updateServices(newServices) {
        this.config.services = newServices;
        this.applyServices();
    }

    // Aplicar informações da empresa no DOM
    applyCompanyInfo() {
        const { company } = this.config;
        
        // Atualizar título e meta tags
        document.title = company.name + ' - ' + company.tagline;
        document.querySelector('meta[name="description"]').setAttribute('content', company.description);
        
        // Atualizar elementos do hero
        const logo = document.querySelector('.hero-title .logo');
        if (logo) logo.textContent = company.name;
        
        const tagline = document.querySelector('.hero-tagline');
        if (tagline) tagline.textContent = company.tagline;
        
        const subtitle = document.querySelector('.hero-subtitle');
        if (subtitle) subtitle.textContent = company.description;
        
        // Atualizar informações de contato
        const contactItems = document.querySelectorAll('.contact-item');
        contactItems.forEach(item => {
            const icon = item.querySelector('i');
            if (icon.classList.contains('fa-envelope')) {
                item.querySelector('p').textContent = company.email;
            } else if (icon.classList.contains('fa-whatsapp')) {
                item.querySelector('p').textContent = company.phone;
            } else if (icon.classList.contains('fa-clock')) {
                item.querySelector('p').textContent = company.workingHours;
            }
        });
    }

    // Aplicar estatísticas no DOM
    applyStats() {
        const { stats } = this.config;
        
        const statItems = document.querySelectorAll('.stat-item');
        statItems.forEach(item => {
            const label = item.querySelector('.stat-label').textContent.toLowerCase();
            const numberElement = item.querySelector('.stat-number');
            
            if (label.includes('projeto')) {
                numberElement.dataset.target = stats.projects;
                numberElement.textContent = '0';
            } else if (label.includes('tecnologia')) {
                numberElement.dataset.target = stats.technologies;
                numberElement.textContent = '0';
            } else if (label.includes('personalizado')) {
                numberElement.dataset.target = stats.customization;
                numberElement.textContent = '0';
            } else if (label.includes('resposta')) {
                numberElement.dataset.target = stats.responseTime;
                numberElement.textContent = '0';
            }
        });
    }

    // Aplicar serviços no DOM
    applyServices() {
        const { services } = this.config;
        
        const servicesGrid = document.querySelector('.services-grid');
        if (!servicesGrid) return;
        
        servicesGrid.innerHTML = '';
        
        services.forEach((service, index) => {
            const serviceCard = document.createElement('div');
            serviceCard.className = 'service-card';
            serviceCard.setAttribute('data-aos', 'fade-up');
            serviceCard.setAttribute('data-aos-delay', (index + 1) * 100);
            
            serviceCard.innerHTML = `
                <div class="service-icon">
                    <i class="${service.icon}"></i>
                </div>
                <h3>${service.title}</h3>
                <p>${service.description}</p>
                <ul class="service-features">
                    ${service.features.map(feature => `<li>${feature}</li>`).join('')}
                </ul>
            `;
            
            servicesGrid.appendChild(serviceCard);
        });
    }

    // Gerar CSS variables dinamicamente
    generateCSSVariables() {
        const { colors } = this.config;
        const root = document.documentElement;
        
        Object.entries(colors).forEach(([key, value]) => {
            root.style.setProperty(`--${key}`, value);
        });
    }

    // Inicializar configurações
    init() {
        this.applyCompanyInfo();
        this.applyStats();
        this.applyServices();
        this.generateCSSVariables();
    }
}

// ===== EXPORTAR CONFIGURAÇÕES =====
window.SITE_CONFIG = SITE_CONFIG;
window.ConfigManager = ConfigManager;

// ===== INICIALIZAR CONFIGURAÇÕES =====
document.addEventListener('DOMContentLoaded', () => {
    const configManager = new ConfigManager();
    configManager.init();
});

// ===== EXEMPLO DE USO =====
/*
// Para atualizar informações da empresa:
const configManager = new ConfigManager();
configManager.updateCompanyInfo({
    name: 'Nova Empresa',
    email: 'novo@email.com',
    phone: '(11) 99999-9999'
});

// Para atualizar estatísticas:
configManager.updateStats({
    projects: 20,
    technologies: 10
});

// Para atualizar serviços:
configManager.updateServices([
    {
        id: 'new-service',
        title: 'Novo Serviço',
        description: 'Descrição do novo serviço',
        icon: 'fas fa-star',
        features: ['Feature 1', 'Feature 2'],
        color: 'orange'
    }
]);
*/
