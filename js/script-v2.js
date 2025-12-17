// Triple C Consulting - Enterprise Website JavaScript v2

document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');

    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            navLinks.classList.toggle('active');
            this.classList.toggle('active');
        });
    }

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const headerOffset = 80;
                const elementPosition = target.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });

                // Close mobile menu if open
                if (navLinks.classList.contains('active')) {
                    navLinks.classList.remove('active');
                    mobileMenuBtn.classList.remove('active');
                }
            }
        });
    });

    // Navbar background change on scroll
    const navbar = document.querySelector('.navbar');
    let lastScroll = 0;

    window.addEventListener('scroll', function() {
        const currentScroll = window.pageYOffset;

        if (currentScroll > 100) {
            navbar.style.background = 'rgba(10, 14, 23, 0.98)';
            navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.3)';
        } else {
            navbar.style.background = 'rgba(10, 14, 23, 0.95)';
            navbar.style.boxShadow = 'none';
        }

        lastScroll = currentScroll;
    });

    // Intersection Observer for fade-in animations
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe all cards and sections
    const animateElements = document.querySelectorAll(
        '.domain-card, .capability-card, .solution-card, .performance-card, .compliance-item, .stat-item'
    );

    animateElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });

    // Add visible class styles
    const style = document.createElement('style');
    style.textContent = `
        .visible {
            opacity: 1 !important;
            transform: translateY(0) !important;
        }
    `;
    document.head.appendChild(style);

    // Counter animation for stats
    const statsSection = document.querySelector('.stats-banner');
    let statsAnimated = false;

    const animateStats = () => {
        if (statsAnimated) return;

        const statNumbers = document.querySelectorAll('.stat-number');
        statNumbers.forEach(stat => {
            const finalValue = stat.textContent;
            const numericValue = parseInt(finalValue.replace(/\D/g, ''));
            const suffix = finalValue.replace(/[0-9]/g, '');

            if (numericValue) {
                let current = 0;
                const increment = numericValue / 30;
                const timer = setInterval(() => {
                    current += increment;
                    if (current >= numericValue) {
                        stat.textContent = finalValue;
                        clearInterval(timer);
                    } else {
                        stat.textContent = Math.floor(current) + suffix;
                    }
                }, 50);
            }
        });

        statsAnimated = true;
    };

    // Observe stats section
    const statsObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateStats();
                statsObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    if (statsSection) {
        statsObserver.observe(statsSection);
    }

    // Contact form API integration
    const contactForm = document.querySelector('.contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const name = document.getElementById('name').value.trim();
            const email = document.getElementById('email').value.trim();
            const organization = document.getElementById('organization').value.trim();
            const message = document.getElementById('message').value.trim();
            const honeypot = document.querySelector('input[name="_gotcha"]').value;

            // Client-side validation
            if (!name || !email || !message) {
                showFormMessage('Please fill in all required fields.', 'error');
                return;
            }

            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                showFormMessage('Please enter a valid email address.', 'error');
                return;
            }

            // Show loading state
            const submitButton = contactForm.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.textContent;
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner"></span> Sending...';

            try {
                // HelpDesk Pro API endpoint
                const apiUrl = 'https://helpdeskpro-oahd.onrender.com/api/public/contact';

                const response = await fetch(apiUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        name: name,
                        email: email,
                        organization: organization || '',
                        message: message,
                        honeypot: honeypot
                    })
                });

                const data = await response.json();

                if (data.success) {
                    // Success - show ticket number
                    let successMsg = data.message || 'Thank you for your message!';
                    if (data.ticket_number && data.ticket_number !== 'TKT-RECEIVED') {
                        successMsg += ` Your reference number is ${data.ticket_number}.`;
                    }
                    showFormMessage(successMsg, 'success');
                    contactForm.reset();

                    // Scroll to success message
                    const formMessage = document.getElementById('form-message');
                    if (formMessage) {
                        formMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                } else {
                    // Error from API
                    const errorMessage = data.error || 'An error occurred. Please try again.';
                    showFormMessage(errorMessage, 'error');
                }
            } catch (error) {
                console.error('Contact form error:', error);
                showFormMessage('Unable to send message. Please try again or contact us directly at consultingbytriplec@gmail.com', 'error');
            } finally {
                // Reset button
                submitButton.disabled = false;
                submitButton.textContent = originalButtonText;
            }
        });
    }

    // Helper function to show form messages
    function showFormMessage(message, type) {
        let messageDiv = document.getElementById('form-message');

        if (!messageDiv) {
            messageDiv = document.createElement('div');
            messageDiv.id = 'form-message';
            contactForm.appendChild(messageDiv);
        }

        messageDiv.textContent = message;
        messageDiv.className = `form-message ${type}`;
        messageDiv.style.display = 'block';

        // Add styles if not already present
        if (!document.getElementById('form-message-styles')) {
            const styles = document.createElement('style');
            styles.id = 'form-message-styles';
            styles.textContent = `
                .form-message {
                    margin-top: 20px;
                    padding: 16px 20px;
                    border-radius: 6px;
                    font-size: 15px;
                    line-height: 1.5;
                    animation: slideIn 0.3s ease;
                }
                .form-message.success {
                    background-color: #d1fae5;
                    color: #065f46;
                    border-left: 4px solid #10b981;
                }
                .form-message.error {
                    background-color: #fee2e2;
                    color: #991b1b;
                    border-left: 4px solid #ef4444;
                }
                .spinner {
                    display: inline-block;
                    width: 14px;
                    height: 14px;
                    border: 2px solid rgba(255, 255, 255, 0.3);
                    border-top-color: white;
                    border-radius: 50%;
                    animation: spin 0.6s linear infinite;
                    margin-right: 8px;
                }
                @keyframes spin {
                    to { transform: rotate(360deg); }
                }
                @keyframes slideIn {
                    from {
                        opacity: 0;
                        transform: translateY(-10px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
                button[type="submit"]:disabled {
                    opacity: 0.7;
                    cursor: not-allowed;
                }
            `;
            document.head.appendChild(styles);
        }

        // Auto-hide success messages after 8 seconds
        if (type === 'success') {
            setTimeout(() => {
                messageDiv.style.display = 'none';
            }, 8000);
        }
    }

    // Parallax effect for hero
    const hero = document.querySelector('.hero');
    if (hero) {
        window.addEventListener('scroll', function() {
            const scrolled = window.pageYOffset;
            const heroContent = document.querySelector('.hero-content');
            if (heroContent && scrolled < window.innerHeight) {
                heroContent.style.transform = `translateY(${scrolled * 0.3}px)`;
                heroContent.style.opacity = 1 - (scrolled / (window.innerHeight * 0.8));
            }
        });
    }

    // Active nav link highlighting
    const sections = document.querySelectorAll('section[id]');
    const navItems = document.querySelectorAll('.nav-links a');

    window.addEventListener('scroll', () => {
        let current = '';

        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (pageYOffset >= sectionTop - 200) {
                current = section.getAttribute('id');
            }
        });

        navItems.forEach(item => {
            item.classList.remove('active');
            if (item.getAttribute('href') === `#${current}`) {
                item.classList.add('active');
            }
        });
    });

    // Add active nav style
    const navStyle = document.createElement('style');
    navStyle.textContent = `
        .nav-links a.active {
            color: var(--accent-gold) !important;
        }
        .nav-links a.active::after {
            width: 100% !important;
        }
    `;
    document.head.appendChild(navStyle);

    console.log('Triple C Consulting website initialized');
});
