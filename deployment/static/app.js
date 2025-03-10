// app.js - UI Enhancements for Job Recommendation System

document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const mobileMenuBtn = document.querySelector('.mobile-menu-button');
    const mobileMenu = document.querySelector('.mobile-menu');
    const sidebar = document.querySelector('.sidebar');
    const mobileSidebarBtn = document.querySelector('.mobile-menu-btn');
    
    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', function() {
            mobileMenu.classList.toggle('active');
        });
    }
    
    if (mobileSidebarBtn && sidebar) {
        mobileSidebarBtn.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
    }
    
    // Flash message auto-dismiss
    const flashMessages = document.querySelectorAll('.flash');
    flashMessages.forEach(message => {
        // Add close button
        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '&times;';
        closeBtn.className = 'close-flash';
        closeBtn.style.position = 'absolute';
        closeBtn.style.right = '10px';
        closeBtn.style.top = '50%';
        closeBtn.style.transform = 'translateY(-50%)';
        closeBtn.style.background = 'none';
        closeBtn.style.border = 'none';
        closeBtn.style.fontSize = '1.2rem';
        closeBtn.style.cursor = 'pointer';
        closeBtn.style.color = 'inherit';
        
        message.style.position = 'relative';
        message.appendChild(closeBtn);
        
        closeBtn.addEventListener('click', () => {
            dismissFlashMessage(message);
        });
        
        // Auto dismiss after 5 seconds
        setTimeout(() => {
            dismissFlashMessage(message);
        }, 5000);
    });
    
    function dismissFlashMessage(message) {
        message.style.opacity = '0';
        message.style.transform = 'translateX(20px)';
        setTimeout(() => {
            message.style.display = 'none';
        }, 500);
    }
    
    // Form validation with visual feedback
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.style.borderColor = '#ef4444';
                    
                    // Add error message if not exists
                    const errorMsg = field.parentNode.querySelector('.error-msg');
                    if (!errorMsg) {
                        const msg = document.createElement('p');
                        msg.className = 'error-msg';
                        msg.style.color = '#ef4444';
                        msg.style.fontSize = '0.75rem';
                        msg.style.marginTop = '0.25rem';
                        msg.innerHTML = '<i class="fas fa-exclamation-circle"></i> This field is required';
                        field.parentNode.insertBefore(msg, field.nextSibling);
                    }
                } else {
                    field.style.borderColor = '#d1d5db';
                    const errorMsg = field.parentNode.querySelector('.error-msg');
                    if (errorMsg) errorMsg.remove();
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                
                // Shake form
                form.classList.add('shake');
                setTimeout(() => {
                    form.classList.remove('shake');
                }, 500);
            } else {
                // Add loading indicator to submit button
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    const originalText = submitBtn.innerHTML;
                    submitBtn.innerHTML = '<span class="loading"></span> Processing...';
                    submitBtn.disabled = true;
                    
                    // Reset button after 3 seconds (in case form submission fails)
                    setTimeout(() => {
                        if (submitBtn.disabled) {
                            submitBtn.innerHTML = originalText;
                            submitBtn.disabled = false;
                        }
                    }, 3000);
                }
            }
        });
    });
    
    // Job items hover effect
    const jobItems = document.querySelectorAll('.job-item, .course-list li');
    jobItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 10px 15px rgba(0, 0, 0, 0.1)';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 2px 5px rgba(0, 0, 0, 0.05)';
        });
    });
    
    // Popup functionality
    const openPopupBtns = document.querySelectorAll('.open-popup');
    const closePopupBtns = document.querySelectorAll('.close-popup');
    const popups = document.querySelectorAll('.popup');
    
    openPopupBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const popupId = this.getAttribute('data-popup');
            const popup = document.getElementById(popupId);
            if (popup) {
                popup.classList.add('active');
                
                // Prevent body scrolling when popup is open
                document.body.style.overflow = 'hidden';
            }
        });
    });
    
    function closePopups() {
        popups.forEach(popup => {
            popup.classList.remove('active');
        });
        
        // Re-enable body scrolling
        document.body.style.overflow = '';
    }
    
    closePopupBtns.forEach(btn => {
        btn.addEventListener('click', closePopups);
    });
    
    // Close popup when clicking outside
    popups.forEach(popup => {
        popup.addEventListener('click', function(e) {
            if (e.target === this) {
                closePopups();
            }
        });
    });
    
    // Close popup with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closePopups();
        }
    });
    
    // Add animation to inputs on login/signup forms
    const authForms = document.querySelector('.login-container form');
    if (authForms) {
        const inputs = authForms.querySelectorAll('input');
        inputs.forEach((input, index) => {
            input.style.opacity = '0';
            input.style.transform = 'translateY(10px)';
            setTimeout(() => {
                input.style.transition = 'all 0.3s ease';
                input.style.opacity = '1';
                input.style.transform = 'translateY(0)';
            }, 300 + (index * 100));
        });
    }
    
    // Add tooltips functionality
    const tooltips = document.querySelectorAll('.tooltip');
    tooltips.forEach(tooltip => {
        const text = tooltip.getAttribute('data-tooltip');
        if (text) {
            const tooltipEl = document.createElement('span');
            tooltipEl.className = 'tooltip-text';
            tooltipEl.textContent = text;
            tooltip.appendChild(tooltipEl);
        }
    });
    
    // Save job button animation and confirmation
    const saveButtons = document.querySelectorAll('.save-button');
    saveButtons.forEach(button => {
        if (!button.classList.contains('bg-red-500')) { // Not a remove button
            button.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Create a small popup notification
                const notification = document.createElement('div');
                notification.className = 'popup-notification';
                notification.style.position = 'fixed';
                notification.style.bottom = '20px';
                notification.style.right = '20px';
                notification.style.backgroundColor = '#10b981';
                notification.style.color = 'white';
                notification.style.padding = '10px 20px';
                notification.style.borderRadius = '5px';
                notification.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
                notification.style.zIndex = '9999';
                notification.style.transform = 'translateY(20px)';
                notification.style.opacity = '0';
                notification.style.transition = 'all 0.3s ease';
                notification.innerHTML = '<i class="fas fa-check-circle mr-2"></i> Job saved successfully!';
                
                document.body.appendChild(notification);
                
                // Show notification
                setTimeout(() => {
                    notification.style.transform = 'translateY(0)';
                    notification.style.opacity = '1';
                }, 100);
                
                // Submit the form after animation
                setTimeout(() => {
                    button.closest('form').submit();
                }, 600);
                
                // Hide notification after a few seconds
                setTimeout(() => {
                    notification.style.transform = 'translateY(20px)';
                    notification.style.opacity = '0';
                    setTimeout(() => {
                        notification.remove();
                    }, 300);
                }, 3000);
            });
        }
    });
    
    // Animated counters for statistics
    const counters = document.querySelectorAll('.counter');
    counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-target'));
        const duration = 2000; // 2 seconds
        const step = 50; // Update every 50ms
        const increment = target / (duration / step);
        let current = 0;
        
        const updateCounter = () => {
            current += increment;
            if (current < target) {
                counter.textContent = Math.ceil(current);
                setTimeout(updateCounter, step);
            } else {
                counter.textContent = target;
            }
        };
        
        updateCounter();
    });
    
    // Add scroll reveal animation
    const revealElements = document.querySelectorAll('.reveal-on-scroll');
    
    function checkReveal() {
        const windowHeight = window.innerHeight;
        const revealPoint = 150;
        
        revealElements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            if (elementTop < windowHeight - revealPoint) {
                element.classList.add('revealed');
            }
        });
    }
    
    // Initialize scroll reveal
    window.addEventListener('scroll', checkReveal);
    checkReveal(); // Check on page load
});