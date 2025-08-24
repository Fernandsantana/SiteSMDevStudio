// ===== CONFIGURAÇÕES GLOBAIS =====
const CONFIG = {
    animationDuration: 800,
    scrollThreshold: 0.1,
    particleCount: 50,
    statsAnimationDuration: 2000
};

// ===== UTILITÁRIOS =====
const utils = {
    // Debounce para otimizar performance
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Throttle para scroll events
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    // Verificar se elemento está visível
    isElementInViewport(el) {
        const rect = el.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    },

    // Animar número gradualmente
    animateNumber(element, target, duration = 2000) {
        const start = 0;
        const increment = target / (duration / 16);
        let current = start;

        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            element.textContent = Math.floor(current) + (target === 100 ? '%' : '+');
        }, 16);
    }
};

// ===== GESTÃO DE ESTADO =====
class AppState {
    constructor() {
        this.isLoading = true;
        this.isNavOpen = false;
        this.currentSection = '';
        this.animationsTriggered = new Set();
    }

    setLoading(loading) {
        this.isLoading = loading;
        document.body.classList.toggle('loading', loading);
    }

    setNavOpen(open) {
        this.isNavOpen = open;
        document.body.classList.toggle('nav-open', open);
    }

    setCurrentSection(section) {
        this.currentSection = section;
        this.updateActiveNavLink();
    }

    updateActiveNavLink() {
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        const activeLink = document.querySelector(`[href="#${this.currentSection}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
    }
}

const appState = new AppState();

// ===== INICIALIZAÇÃO =====
class App {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initLoadingScreen();
        this.initNavigation();
        this.initScrollAnimations();
        this.initStatsAnimation();
        this.initParticles();
        this.initSmoothScrolling();
        this.initIntersectionObserver();
    }

    // ===== LOADING SCREEN =====
    initLoadingScreen() {
        const loadingOverlay = document.getElementById('loadingOverlay');
        
        window.addEventListener('load', () => {
            setTimeout(() => {
                loadingOverlay.classList.add('hidden');
                appState.setLoading(false);
                
                // Iniciar animações após carregamento
                setTimeout(() => {
                    this.startInitialAnimations();
                }, 500);
            }, 1500);
        });
    }

    startInitialAnimations() {
        // Animar elementos do hero
        const heroElements = document.querySelectorAll('.hero-title, .hero-tagline, .hero-subtitle, .hero-cta');
        heroElements.forEach((el, index) => {
            setTimeout(() => {
                el.style.animation = 'slideInUp 1s ease-out forwards';
            }, index * 200);
        });
    }

    // ===== NAVEGAÇÃO =====
    initNavigation() {
        const navbar = document.getElementById('navbar');
        const navToggle = document.getElementById('navToggle');
        const navMenu = document.getElementById('navMenu');
        const navLinks = document.querySelectorAll('.nav-link');

        // Toggle menu mobile
        navToggle.addEventListener('click', () => {
            appState.setNavOpen(!appState.isNavOpen);
            navToggle.classList.toggle('active');
            navMenu.classList.toggle('active');
        });

        // Fechar menu ao clicar em link
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                appState.setNavOpen(false);
                navToggle.classList.remove('active');
                navMenu.classList.remove('active');
            });
        });

        // Navbar scroll effect
        const handleScroll = utils.throttle(() => {
            if (window.scrollY > 100) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        }, 100);

        window.addEventListener('scroll', handleScroll);
    }

    // ===== ANIMAÇÕES DE SCROLL =====
    initScrollAnimations() {
        const observerOptions = {
            threshold: CONFIG.scrollThreshold,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                    
                    // Animar números das estatísticas
                    if (entry.target.classList.contains('stat-item')) {
                        const numberElement = entry.target.querySelector('.stat-number');
                        const target = parseInt(numberElement.dataset.target);
                        utils.animateNumber(numberElement, target, CONFIG.statsAnimationDuration);
                    }
                }
            });
        }, observerOptions);

        // Observar elementos com animação
        document.querySelectorAll('[data-aos]').forEach(el => {
            observer.observe(el);
        });
    }

    // ===== ANIMAÇÃO DE ESTATÍSTICAS =====
    initStatsAnimation() {
        const statsSection = document.querySelector('.stats-section');
        const statItems = document.querySelectorAll('.stat-item');

        const statsObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !appState.animationsTriggered.has('stats')) {
                    appState.animationsTriggered.add('stats');
                    
                    statItems.forEach((item, index) => {
                        setTimeout(() => {
                            const numberElement = item.querySelector('.stat-number');
                            const target = parseInt(numberElement.dataset.target);
                            utils.animateNumber(numberElement, target, CONFIG.statsAnimationDuration);
                        }, index * 200);
                    });
                }
            });
        }, { threshold: 0.5 });

        statsObserver.observe(statsSection);
    }

    // ===== SISTEMA DE PARTÍCULAS =====
    initParticles() {
        const particlesContainer = document.getElementById('particlesContainer');
        
        for (let i = 0; i < CONFIG.particleCount; i++) {
            this.createParticle(particlesContainer);
        }
    }

    createParticle(container) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        
        const size = Math.random() * 4 + 2;
        const x = Math.random() * window.innerWidth;
        const y = Math.random() * window.innerHeight;
        const duration = Math.random() * 3000 + 2000;
        const delay = Math.random() * 2000;
        
        particle.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            background: linear-gradient(45deg, #8b5cf6, #06b6d4);
            border-radius: 50%;
            left: ${x}px;
            top: ${y}px;
            opacity: ${Math.random() * 0.5 + 0.1};
            pointer-events: none;
            z-index: 1;
            animation: particleFloat ${duration}ms ease-in-out infinite;
            animation-delay: ${delay}ms;
        `;
        
        container.appendChild(particle);
    }

    // ===== SCROLL SUAVE =====
    initSmoothScrolling() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    const offsetTop = target.offsetTop - 80; // Ajuste para navbar
                    window.scrollTo({
                        top: offsetTop,
                        behavior: 'smooth'
                    });
                }
            });
        });
    }

    // ===== INTERSECTION OBSERVER =====
    initIntersectionObserver() {
        const sections = document.querySelectorAll('section[id]');
        
        const sectionObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const sectionId = entry.target.id;
                    appState.setCurrentSection(sectionId);
                }
            });
        }, { threshold: 0.3 });

        sections.forEach(section => {
            sectionObserver.observe(section);
        });
    }

    // ===== EVENT LISTENERS =====
    setupEventListeners() {
        // Resize handler
        window.addEventListener('resize', utils.debounce(() => {
            this.handleResize();
        }, 250));

        // Scroll handler
        window.addEventListener('scroll', utils.throttle(() => {
            this.handleScroll();
        }, 100));

        // Floating buttons
        document.querySelectorAll('.floating-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.addClickEffect(e.target);
            });
        });

        // Service cards
        document.querySelectorAll('.service-card').forEach((card, index) => {
            card.addEventListener('mouseenter', () => {
                this.animateServiceCard(card, index);
            });
        });

        // Tech items
        document.querySelectorAll('.tech-item').forEach(item => {
            item.addEventListener('mouseenter', () => {
                this.animateTechItem(item);
            });
        });
    }

    handleResize() {
        // Recalcular posições de partículas
        const particles = document.querySelectorAll('.particle');
        particles.forEach(particle => {
            const x = Math.random() * window.innerWidth;
            const y = Math.random() * window.innerHeight;
            particle.style.left = x + 'px';
            particle.style.top = y + 'px';
        });
    }

    handleScroll() {
        // Atualizar posição do scroll indicator
        const scrollIndicator = document.querySelector('.hero-scroll-indicator');
        if (scrollIndicator) {
            const scrollPercent = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
            scrollIndicator.style.opacity = Math.max(0, 1 - scrollPercent / 20);
        }
    }

    addClickEffect(element) {
        element.style.transform = 'scale(0.95)';
        setTimeout(() => {
            element.style.transform = '';
        }, 150);
    }

    animateServiceCard(card, index) {
        const icon = card.querySelector('.service-icon');
        icon.style.animation = 'none';
        setTimeout(() => {
            icon.style.animation = `iconFloat 2s ease-in-out infinite, pulse 1s ease-in-out`;
        }, 10);
    }

    animateTechItem(item) {
        const icon = item.querySelector('i');
        icon.style.animation = 'pulse 0.5s ease-in-out';
        setTimeout(() => {
            icon.style.animation = '';
        }, 500);
    }
}

// ===== CSS ADICIONAL DINÂMICO =====
const dynamicStyles = `
    @keyframes particleFloat {
        0%, 100% {
            transform: translateY(0px) translateX(0px);
            opacity: 0.1;
        }
        50% {
            transform: translateY(-100px) translateX(50px);
            opacity: 0.5;
        }
    }

    .notification-content {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .notification-close {
        background: none;
        border: none;
        color: white;
        cursor: pointer;
        padding: 0.25rem;
        margin-left: 1rem;
        opacity: 0.7;
        transition: opacity 0.2s ease;
    }

    .notification-close:hover {
        opacity: 1;
    }

    .particle {
        position: absolute;
        pointer-events: none;
        z-index: 1;
    }
`;

// Adicionar estilos dinâmicos
const styleSheet = document.createElement('style');
styleSheet.textContent = dynamicStyles;
document.head.appendChild(styleSheet);

// ===== INICIALIZAR APLICAÇÃO =====
document.addEventListener('DOMContentLoaded', () => {
    new App();
});

// ===== PERFORMANCE OPTIMIZATIONS =====
// Preload critical resources
const preloadResources = () => {
    const criticalImages = [
        '/favicon.ico',
        '/apple-touch-icon.png'
    ];
    
    criticalImages.forEach(src => {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.as = 'image';
        link.href = src;
        document.head.appendChild(link);
    });
};

// Service Worker registration (se disponível)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}

// ===== ANALYTICS E MONITORAMENTO =====
class Analytics {
    static trackEvent(eventName, data = {}) {
        // Implementar tracking de eventos
        console.log('Event tracked:', eventName, data);
        
        // Google Analytics 4 (se configurado)
        if (typeof gtag !== 'undefined') {
            gtag('event', eventName, data);
        }
    }

    static trackPageView(page) {
        this.trackEvent('page_view', { page });
    }

    static trackFormSubmission(formType) {
        this.trackEvent('form_submit', { form_type: formType });
    }

    static trackScroll(depth) {
        this.trackEvent('scroll', { depth });
    }
}

// ===== ERROR HANDLING =====
window.addEventListener('error', (e) => {
    console.error('Global error:', e.error);
    // Enviar para serviço de monitoramento
});

window.addEventListener('unhandledrejection', (e) => {
    console.error('Unhandled promise rejection:', e.reason);
    // Enviar para serviço de monitoramento
});

// ===== EXPORTAR PARA USO GLOBAL =====
window.SMDevStudio = {
    appState,
    utils,
    Analytics
};
