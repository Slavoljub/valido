// Footer Modal Functionality
document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize all modals
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        new bootstrap.Modal(modal);
    });

    // Add hover effects to footer links
    const footerLinks = document.querySelectorAll('footer a[data-bs-toggle="modal"]');
    footerLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.transition = 'transform 0.2s ease';
        });
        
        link.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Add click tracking for analytics (optional)
    footerLinks.forEach(link => {
        link.addEventListener('click', function() {
            const modalTarget = this.getAttribute('data-bs-target');
            console.log(`Footer modal opened: ${modalTarget}`);
            
            // You can add analytics tracking here
            // Example: gtag('event', 'modal_open', { 'modal_name': modalTarget });
        });
    });

    // Enhance modal content loading
    const modalTriggers = {
        '#simulacijaModal': function() {
            // Add any dynamic content loading for simulation modal
            console.log('Simulation modal loaded');
        },
        '#dokumentiModal': function() {
            // Add any dynamic content loading for documents modal
            console.log('Documents modal loaded');
        },
        '#aiKomentariModal': function() {
            // Add any dynamic content loading for AI comments modal
            console.log('AI Comments modal loaded');
        },
        '#propisiModal': function() {
            // Add any dynamic content loading for regulations modal
            console.log('Regulations modal loaded');
        },
        '#solutionsModal': function() {
            // Add any dynamic content loading for solutions modal
            console.log('Solutions modal loaded');
        },
        '#contactModal': function() {
            // Add any dynamic content loading for contact modal
            console.log('Contact modal loaded');
        },
        '#legalModal': function() {
            // Add any dynamic content loading for legal modal
            console.log('Legal modal loaded');
        }
    };

    // Execute modal-specific functions when modals are shown
    Object.keys(modalTriggers).forEach(modalId => {
        const modal = document.querySelector(modalId);
        if (modal) {
            modal.addEventListener('shown.bs.modal', function() {
                const trigger = modalTriggers[modalId];
                if (trigger) trigger();
            });
        }
    });

    // Add keyboard navigation support
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                const modalInstance = bootstrap.Modal.getInstance(openModal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            }
        }
    });

    // Add smooth scrolling for modal links that go to full pages
    const modalPageLinks = document.querySelectorAll('.modal a[href^="/"]');
    modalPageLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Close modal before navigating
            const modal = this.closest('.modal');
            if (modal) {
                const modalInstance = bootstrap.Modal.getInstance(modal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            }
        });
    });

    // Add loading states for modal buttons
    const modalButtons = document.querySelectorAll('.modal .btn');
    modalButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (this.classList.contains('btn-primary') && !this.classList.contains('btn-close')) {
                // Add loading state for primary buttons
                const originalText = this.innerHTML;
                this.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Učitavanje...';
                this.disabled = true;
                
                // Reset after a short delay (simulate loading)
                setTimeout(() => {
                    this.innerHTML = originalText;
                    this.disabled = false;
                }, 1000);
            }
        });
    });

    // Add tooltips to modal cards
    const modalCards = document.querySelectorAll('.modal .card');
    modalCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
            this.style.transform = 'translateY(-2px)';
            this.style.transition = 'all 0.3s ease';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.boxShadow = '';
            this.style.transform = '';
        });
    });

    // Add accessibility improvements
    const modalCloseButtons = document.querySelectorAll('.modal .btn-close');
    modalCloseButtons.forEach(button => {
        button.setAttribute('aria-label', 'Zatvori modal');
    });

    // Add focus management for modals
    modals.forEach(modal => {
        modal.addEventListener('shown.bs.modal', function() {
            // Focus on first focusable element
            const firstFocusable = this.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
            if (firstFocusable) {
                firstFocusable.focus();
            }
        });
    });

    console.log('Footer modals initialized successfully');
});
