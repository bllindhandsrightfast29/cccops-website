// Triple C Consulting - Interactive Elements

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Navbar background on scroll
let lastScrollTop = 0;
const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', () => {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

    if (scrollTop > 100) {
        navbar.style.background = 'rgba(10, 14, 39, 0.98)';
        navbar.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.5)';
    } else {
        navbar.style.background = 'rgba(10, 14, 39, 0.95)';
        navbar.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.3)';
    }

    lastScrollTop = scrollTop;
});

// Intersection Observer for fade-in animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Apply fade-in to capability cards
document.querySelectorAll('.capability-card, .solution-card').forEach((card, index) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(30px)';
    card.style.transition = `opacity 0.6s ease ${index * 0.1}s, transform 0.6s ease ${index * 0.1}s`;
    observer.observe(card);
});

// Mobile menu toggle (for future responsive menu)
const createMobileMenu = () => {
    const navLinks = document.querySelector('.nav-links');
    const navbar = document.querySelector('.navbar .container');

    // Only create mobile menu on small screens
    if (window.innerWidth <= 768) {
        const menuButton = document.createElement('button');
        menuButton.classList.add('mobile-menu-toggle');
        menuButton.innerHTML = '☰';
        menuButton.style.cssText = `
            display: block;
            background: none;
            border: none;
            color: var(--accent-color);
            font-size: 1.8rem;
            cursor: pointer;
            padding: 0.5rem;
        `;

        menuButton.addEventListener('click', () => {
            navLinks.classList.toggle('mobile-active');
        });

        // Check if button doesn't already exist
        if (!document.querySelector('.mobile-menu-toggle')) {
            navbar.appendChild(menuButton);
        }
    }
};

// Parallax effect for hero section
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const hero = document.querySelector('.hero-content');
    if (hero) {
        hero.style.transform = `translateY(${scrolled * 0.5}px)`;
        hero.style.opacity = 1 - (scrolled / 600);
    }
});

// Console easter egg
console.log('%c⬢ Triple C Consulting', 'color: #00d4ff; font-size: 24px; font-weight: bold;');
console.log('%cTactical Technology Integration & Mission Support', 'color: #7b2cbf; font-size: 14px;');
console.log('%cLooking for developers? Contact us at info@cccops.com', 'color: #b0b8c4; font-size: 12px;');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    createMobileMenu();
});

// Window resize handler
window.addEventListener('resize', () => {
    createMobileMenu();
});
