/* ==========================================================================
   Button Components JavaScript
   ========================================================================== */

// Button component functionality
window.ButtonComponents = {
  // Initialize button components
  init: function() {
    this.initLoadingButtons();
    this.initCopyButtons();
    this.initConfirmButtons();
    this.initFloatingButtons();
  },
  
  // Loading button functionality
  initLoadingButtons: function() {
    document.addEventListener('click', function(e) {
      const button = e.target.closest('.btn-loading');
      if (button) {
        button.classList.add('loading');
        button.disabled = true;
        
        // Auto-remove loading state after action completes
        setTimeout(() => {
          button.classList.remove('loading');
          button.disabled = false;
        }, 2000);
      }
    });
  },
  
  // Copy button functionality
  initCopyButtons: function() {
    document.addEventListener('click', function(e) {
      const button = e.target.closest('.btn-copy');
      if (button) {
        const textToCopy = button.getAttribute('data-copy') || button.textContent.trim();
        
        ValidoAI.utils.copyToClipboard(textToCopy).then(() => {
          // Show success feedback
          const originalText = button.innerHTML;
          button.innerHTML = '<i class="fas fa-check"></i> Copied!';
          button.classList.add('btn-success');
          
          setTimeout(() => {
            button.innerHTML = originalText;
            button.classList.remove('btn-success');
          }, 2000);
        }).catch(() => {
          // Show error feedback
          const originalText = button.innerHTML;
          button.innerHTML = '<i class="fas fa-times"></i> Failed!';
          button.classList.add('btn-danger');
          
          setTimeout(() => {
            button.innerHTML = originalText;
            button.classList.remove('btn-danger');
          }, 2000);
        });
      }
    });
  },
  
  // Confirm button functionality
  initConfirmButtons: function() {
    document.addEventListener('click', function(e) {
      const button = e.target.closest('.btn-confirm');
      if (button) {
        const message = button.getAttribute('data-confirm') || 'Are you sure?';
        const action = button.getAttribute('data-action');
        
        if (confirm(message)) {
          if (action === 'submit') {
            const form = button.closest('form');
            if (form) form.submit();
          } else if (action === 'navigate') {
            const href = button.getAttribute('href');
            if (href) window.location.href = href;
          } else if (action === 'function') {
            const functionName = button.getAttribute('data-function');
            if (window[functionName]) {
              window[functionName]();
            }
          }
        }
      }
    });
  },
  
  // Floating action button functionality
  initFloatingButtons: function() {
    const fabButtons = document.querySelectorAll('.btn-fab');
    
    fabButtons.forEach(button => {
      // Add scroll behavior
      let lastScrollTop = 0;
      window.addEventListener('scroll', ValidoAI.utils.throttle(() => {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        if (scrollTop > lastScrollTop && scrollTop > 100) {
          // Scrolling down - hide FAB
          button.style.transform = 'translateY(100px)';
          button.style.opacity = '0';
        } else {
          // Scrolling up - show FAB
          button.style.transform = 'translateY(0)';
          button.style.opacity = '1';
        }
        
        lastScrollTop = scrollTop;
      }, 100));
      
      // Add click animation
      button.addEventListener('click', function() {
        this.style.transform = 'scale(0.9)';
        setTimeout(() => {
          this.style.transform = 'scale(1)';
        }, 150);
      });
    });
  },
  
  // Button group functionality
  initButtonGroups: function() {
    const buttonGroups = document.querySelectorAll('.btn-group');
    
    buttonGroups.forEach(group => {
      const buttons = group.querySelectorAll('.btn');
      
      buttons.forEach(button => {
        button.addEventListener('click', function() {
          // Remove active class from all buttons in group
          buttons.forEach(btn => btn.classList.remove('active'));
          // Add active class to clicked button
          this.classList.add('active');
        });
      });
    });
  },
  
  // Toggle button functionality
  initToggleButtons: function() {
    document.addEventListener('click', function(e) {
      const button = e.target.closest('.btn-toggle');
      if (button) {
        const target = button.getAttribute('data-target');
        const toggleClass = button.getAttribute('data-toggle') || 'active';
        
        // Toggle button state
        button.classList.toggle(toggleClass);
        
        // Toggle target element
        if (target) {
          const targetElement = document.querySelector(target);
          if (targetElement) {
            targetElement.classList.toggle(toggleClass);
          }
        }
        
        // Trigger custom event
        button.dispatchEvent(new CustomEvent('toggle', {
          detail: {
            active: button.classList.contains(toggleClass),
            target: target
          }
        }));
      }
    });
  },
  
  // Progress button functionality
  initProgressButtons: function() {
    document.addEventListener('click', function(e) {
      const button = e.target.closest('.btn-progress');
      if (button) {
        const duration = parseInt(button.getAttribute('data-duration')) || 3000;
        const progress = button.querySelector('.btn-progress-bar');
        
        if (progress) {
          button.classList.add('loading');
          button.disabled = true;
          
          // Animate progress bar
          progress.style.width = '0%';
          progress.style.transition = `width ${duration}ms ease-in-out`;
          
          setTimeout(() => {
            progress.style.width = '100%';
          }, 10);
          
          // Complete after duration
          setTimeout(() => {
            button.classList.remove('loading');
            button.disabled = false;
            progress.style.width = '0%';
          }, duration);
        }
      }
    });
  }
};

// Initialize button components when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  ButtonComponents.init();
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ButtonComponents;
}
