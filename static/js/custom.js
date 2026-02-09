/**
 * ============================================
 * MediBook - Custom JavaScript
 * ============================================
 */

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('🏥 MediBook initialized');

    // Initialize all components
    initDarkMode();
    initTooltips();
    initScrollAnimations();
    initFormValidation();
    initNotifications();
});

/**
 * Dark Mode Toggle
 */
function initDarkMode() {
    // Check for saved preference or default to light mode
    const isDarkMode = localStorage.getItem('darkMode') === 'true';
    
    if (isDarkMode) {
        document.documentElement.classList.add('dark');
    } else {
        document.documentElement.classList.remove('dark');
    }
    
    // Update icons on page load
    updateDarkModeIcons(isDarkMode);
}

function updateDarkModeIcons(isDark) {
    // Desktop icons
    const moonIcon = document.getElementById('moonIcon');
    const sunIcon = document.getElementById('sunIcon');
    
    // Mobile icons
    const moonIconMobile = document.getElementById('moonIconMobile');
    const sunIconMobile = document.getElementById('sunIconMobile');
    
    if (isDark) {
        moonIcon?.classList.add('hidden');
        sunIcon?.classList.remove('hidden');
        moonIconMobile?.classList.add('hidden');
        sunIconMobile?.classList.remove('hidden');
    } else {
        moonIcon?.classList.remove('hidden');
        sunIcon?.classList.add('hidden');
        moonIconMobile?.classList.remove('hidden');
        sunIconMobile?.classList.add('hidden');
    }
}

/**
 * Tooltips
 */
function initTooltips() {
    const tooltipTriggers = document.querySelectorAll('[data-tooltip]');

    tooltipTriggers.forEach(trigger => {
        trigger.addEventListener('mouseenter', function() {
            showTooltip(this);
        });

        trigger.addEventListener('mouseleave', function() {
            hideTooltip();
        });
    });
}

function showTooltip(element) {
    const text = element.dataset.tooltip;
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip fixed z-50 px-3 py-2 text-sm bg-gray-900 text-white rounded-lg shadow-lg';
    tooltip.textContent = text;
    tooltip.id = 'active-tooltip';

    document.body.appendChild(tooltip);

    // Position tooltip
    const rect = element.getBoundingClientRect();
    tooltip.style.top = `${rect.top - tooltip.offsetHeight - 8}px`;
    tooltip.style.left = `${rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2)}px`;

    // Animate in
    setTimeout(() => {
        tooltip.style.opacity = '1';
        tooltip.style.transform = 'translateY(0)';
    }, 10);
}

function hideTooltip() {
    const tooltip = document.getElementById('active-tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

/**
 * Scroll Animations
 */
function initScrollAnimations() {
    const animatedElements = document.querySelectorAll('[data-animate]');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const animation = entry.target.dataset.animate;
                entry.target.classList.add(`animate-${animation}`);
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    animatedElements.forEach(el => observer.observe(el));
}

/**
 * Form Validation
 */
function initFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');

    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                showNotification('Please fill in all required fields', 'error');
            }
        });

        // Real-time validation
        const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateInput(this);
            });
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');

    inputs.forEach(input => {
        if (!validateInput(input)) {
            isValid = false;
        }
    });

    return isValid;
}

function validateInput(input) {
    const value = input.value.trim();
    const type = input.type;
    let isValid = true;
    let errorMessage = '';

    // Check if empty
    if (!value) {
        isValid = false;
        errorMessage = 'This field is required';
    }

    // Email validation
    else if (type === 'email') {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            errorMessage = 'Please enter a valid email address';
        }
    }

    // Phone validation
    else if (input.name === 'phone') {
        const phoneRegex = /^[\d\s\-\+\(\)]+$/;
        if (!phoneRegex.test(value) || value.length < 10) {
            isValid = false;
            errorMessage = 'Please enter a valid phone number';
        }
    }

    // Password validation
    else if (type === 'password' && input.name === 'password1') {
        if (value.length < 8) {
            isValid = false;
            errorMessage = 'Password must be at least 8 characters';
        }
    }

    // Show/hide error
    showInputError(input, isValid, errorMessage);

    return isValid;
}

function showInputError(input, isValid, message) {
    // Remove existing error
    const existingError = input.parentElement.querySelector('.input-error');
    if (existingError) {
        existingError.remove();
    }

    // Update input style
    if (isValid) {
        input.classList.remove('border-red-500', 'focus:ring-red-500');
        input.classList.add('border-gray-300', 'focus:ring-purple-500');
    } else {
        input.classList.remove('border-gray-300', 'focus:ring-purple-500');
        input.classList.add('border-red-500', 'focus:ring-red-500');

        // Add error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'input-error text-red-500 text-sm mt-1';
        errorDiv.textContent = message;
        input.parentElement.appendChild(errorDiv);
    }
}

/**
 * Notifications
 */
function initNotifications() {
    // Auto-hide notifications after 5 seconds
    const notifications = document.querySelectorAll('.notification');
    notifications.forEach(notification => {
        setTimeout(() => {
            hideNotification(notification);
        }, 5000);

        // Close button
        const closeBtn = notification.querySelector('.notification-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                hideNotification(notification);
            });
        }
    });
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification fixed top-4 right-4 z-50 max-w-sm p-4 rounded-lg shadow-lg transform transition-all duration-300 translate-x-full`;

    // Type-specific styling
    const types = {
        success: 'bg-green-500 text-white',
        error: 'bg-red-500 text-white',
        warning: 'bg-yellow-500 text-white',
        info: 'bg-blue-500 text-white'
    };

    notification.className += ` ${types[type] || types.info}`;

    notification.innerHTML = `
        <div class="flex items-center justify-between">
            <span>${message}</span>
            <button class="notification-close ml-4 hover:opacity-75">
                <span class="iconify" data-icon="mdi:close"></span>
            </button>
        </div>
    `;

    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => {
        notification.classList.remove('translate-x-full');
    }, 10);

    // Auto remove after 5 seconds
    setTimeout(() => {
        hideNotification(notification);
    }, 5000);

    // Close button handler
    notification.querySelector('.notification-close').addEventListener('click', () => {
        hideNotification(notification);
    });
}

function hideNotification(notification) {
    notification.classList.add('translate-x-full', 'opacity-0');
    setTimeout(() => {
        notification.remove();
    }, 300);
}

/**
 * Confirm Dialog
 */
function confirmAction(message) {
    return new Promise((resolve) => {
        const confirmed = confirm(message);
        resolve(confirmed);
    });
}

/**
 * Copy to Clipboard
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Failed to copy:', err);
        showNotification('Failed to copy', 'error');
    });
}

/**
 * Format Currency
 */
function formatCurrency(amount, currency = 'SAR') {
    return new Intl.NumberFormat('ar-SA', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

/**
 * Format Date
 */
function formatDate(date, locale = 'ar-SA') {
    return new Intl.DateTimeFormat(locale, {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(new Date(date));
}

/**
 * Debounce Function
 */
function debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle Function
 */
function throttle(func, limit = 300) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Local Storage Helpers
 */
const storage = {
    get(key) {
        try {
            return JSON.parse(localStorage.getItem(key));
        } catch {
            return null;
        }
    },

    set(key, value) {
        localStorage.setItem(key, JSON.stringify(value));
    },

    remove(key) {
        localStorage.removeItem(key);
    },

    clear() {
        localStorage.clear();
    }
};

/**
 * HTMX Event Handlers
 */
document.body.addEventListener('htmx:afterSwap', function(event) {
    // Reinitialize components after HTMX swap
    initTooltips();
    initNotifications();
});

document.body.addEventListener('htmx:sendError', function(event) {
    showNotification('Network error. Please check your connection.', 'error');
});

document.body.addEventListener('htmx:responseError', function(event) {
    showNotification('Server error. Please try again later.', 'error');
});

/**
 * Smooth Scroll to Element
 */
function scrollToElement(elementId, offset = 80) {
    const element = document.getElementById(elementId);
    if (element) {
        const top = element.getBoundingClientRect().top + window.pageYOffset - offset;
        window.scrollTo({
            top: top,
            behavior: 'smooth'
        });
    }
}

/**
 * Image Lazy Loading
 */
function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');

    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                imageObserver.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));
}

/**
 * Mobile Menu Toggle
 */
function initMobileMenu() {
    const menuBtn = document.getElementById('mobile-menu-btn');
    const menu = document.getElementById('mobile-menu');

    if (menuBtn && menu) {
        menuBtn.addEventListener('click', function() {
            menu.classList.toggle('hidden');

            // Animate
            if (!menu.classList.contains('hidden')) {
                menu.classList.add('animate-slide-in-down');
            }
        });

        // Close on outside click
        document.addEventListener('click', function(e) {
            if (!menu.contains(e.target) && !menuBtn.contains(e.target)) {
                menu.classList.add('hidden');
            }
        });
    }
}

// Initialize mobile menu
initMobileMenu();

// Make functions globally available
window.MediBook = {
    showNotification,
    hideNotification,
    confirmAction,
    copyToClipboard,
    formatCurrency,
    formatDate,
    scrollToElement,
    storage
};
