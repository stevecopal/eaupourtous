document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. GESTION DU MENU MOBILE (Icône Bars/Times) ---
    const menuBtn = document.getElementById('menuBtn');
    const mobileMenu = document.getElementById('mobileMenu');
    const menuIcon = menuBtn ? menuBtn.querySelector('i') : null;

    if (menuBtn && mobileMenu) {
        menuBtn.addEventListener('click', () => {
            const isHidden = mobileMenu.classList.toggle('hidden');
            
            if (menuIcon) {
                // Bascule entre l'icône burger et la croix
                menuIcon.classList.toggle('fa-bars', isHidden);
                menuIcon.classList.toggle('fa-times', !isHidden);
                
                // Petite animation de rotation
                menuIcon.classList.add('rotate-icon');
                setTimeout(() => menuIcon.classList.remove('rotate-icon'), 300);
            }
        });

        // Fermeture automatique au clic sur un lien (Ancre)
        mobileMenu.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                mobileMenu.classList.add('hidden');
                if (menuIcon) menuIcon.classList.replace('fa-times', 'fa-bars');
            });
        });
    }

    // --- 2. NAVBAR DYNAMIQUE AU SCROLL ---
    const navbar = document.getElementById('navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 20) {
            navbar.classList.add('shadow-lg', 'bg-white');
            navbar.classList.remove('bg-white/95');
        } else {
            navbar.classList.remove('shadow-lg');
            navbar.classList.add('bg-white/95');
        }
    });

    // --- 3. SCROLL FLUIDE (Fix pour les liens multilingues /fr/#accueil) ---
    document.querySelectorAll('a[href*="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            // On vérifie si le lien contient une ancre
            if (href.includes('#')) {
                const targetId = href.split('#')[1];
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    e.preventDefault();
                    const offsetTop = targetElement.getBoundingClientRect().top + window.pageYOffset - 85;
                    window.scrollTo({ top: offsetTop, behavior: 'smooth' });
                    
                    // Optionnel : fermer le menu mobile si ouvert
                    if (mobileMenu) mobileMenu.classList.add('hidden');
                }
            }
        });
    });

    // --- 4. ANIMATIONS AU SCROLL (Fade Up) ---
    const scrollObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                // On arrête d'observer une fois l'animation jouée
                scrollObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.15 });

    document.querySelectorAll('.fade-up').forEach(el => scrollObserver.observe(el));

    // --- 5. SLIDER HERO (Fondu enchaîné) ---
    const slides = document.querySelectorAll('#hero-slider .slider-img');
    if (slides.length > 1) {
        let currentSlide = 0;
        setInterval(() => {
            slides[currentSlide].classList.remove('active');
            currentSlide = (currentSlide + 1) % slides.length;
            slides[currentSlide].classList.add('active');
        }, 5000);
    }

    // --- 6. AUTO-DISPARITION DES MESSAGES DE CONTACT ---
    const alertMessages = document.querySelectorAll('.animate-fade-in');
    if (alertMessages.length > 0) {
        setTimeout(() => {
            alertMessages.forEach(msg => {
                msg.style.opacity = '0';
                msg.style.transform = 'translateY(-10px)';
                msg.style.transition = 'all 0.5s ease';
                setTimeout(() => msg.remove(), 500);
            });
        }, 6000); // 6 secondes de visibilité
    }
});