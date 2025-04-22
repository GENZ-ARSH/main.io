/**
 * GEN-Z LIBRARY
 * Main JavaScript file for the application
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('GEN-Z LIBRARY initialized');
    
    // Initialize mobile menu toggle
    initializeMobileMenu();
    
    // Initialize flash message auto-hide
    initializeFlashMessages();
    
    // Handle tab functionality (if present)
    initializeTabs();
    
    // Initialize book card hover effects
    initializeBookCards();
    
    // Load dark mode (this will be further managed by darkmode.js)
    initializeDarkMode();
    
    // Check if user is logged in and update UI accordingly
    updateUIForLoggedInUser();
});

/**
 * Mobile Menu Functionality
 */
function initializeMobileMenu() {
    const mobileMenuButton = document.querySelector('.md\\:hidden');
    if (!mobileMenuButton) return;
    
    const mobileMenu = document.querySelector('.md\\:hidden.hidden');
    
    mobileMenuButton.addEventListener('click', function() {
        if (mobileMenu.classList.contains('hidden')) {
            mobileMenu.classList.remove('hidden');
        } else {
            mobileMenu.classList.add('hidden');
        }
    });
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', function(event) {
        if (!mobileMenuButton.contains(event.target) && !mobileMenu.contains(event.target)) {
            mobileMenu.classList.add('hidden');
        }
    });
}

/**
 * Flash Message Auto-hide
 */
function initializeFlashMessages() {
    const flashMessages = document.querySelectorAll('.flash-message');
    
    if (flashMessages.length > 0) {
        setTimeout(() => {
            flashMessages.forEach(msg => {
                msg.classList.add('opacity-0');
                setTimeout(() => {
                    msg.remove();
                }, 300);
            });
        }, 5000);
    }
    
    // Add click handler to close flash messages manually
    flashMessages.forEach(msg => {
        const closeButton = msg.querySelector('button');
        if (closeButton) {
            closeButton.addEventListener('click', () => {
                msg.classList.add('opacity-0');
                setTimeout(() => {
                    msg.remove();
                }, 300);
            });
        }
    });
}

/**
 * Tab Functionality
 */
function initializeTabs() {
    const tabs = document.querySelectorAll('[role="tab"]');
    if (tabs.length === 0) return;
    
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            
            // Update tab states
            tabs.forEach(t => {
                t.classList.remove('border-indigo-600');
                t.classList.add('border-transparent');
                t.setAttribute('aria-selected', 'false');
            });
            
            this.classList.remove('border-transparent');
            this.classList.add('border-indigo-600');
            this.setAttribute('aria-selected', 'true');
            
            // Update content states
            tabContents.forEach(content => {
                content.classList.add('hidden');
            });
            
            document.getElementById(tabId).classList.remove('hidden');
        });
    });
}

/**
 * Book Card Hover Effects
 */
function initializeBookCards() {
    const bookCards = document.querySelectorAll('.card');
    
    bookCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.classList.add('shadow-lg');
        });
        
        card.addEventListener('mouseleave', function() {
            this.classList.remove('shadow-lg');
        });
    });
}

/**
 * Dark Mode Initialization (basic version)
 * Full functionality is in darkmode.js
 */
function initializeDarkMode() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.documentElement.className = savedTheme;
    }
}

/**
 * UI Updates based on login status
 */
function updateUIForLoggedInUser() {
    // This function can be expanded as needed
    const isLoggedIn = document.querySelector('[data-user-logged-in]');
    
    if (isLoggedIn) {
        // Add any UI changes for logged in users
        console.log('User is logged in');
    }
}

/**
 * Copy text to clipboard helper
 * @param {string} text - The text to copy
 * @returns {boolean} - Success status
 */
function copyToClipboard(text) {
    const tempInput = document.createElement('input');
    tempInput.value = text;
    document.body.appendChild(tempInput);
    tempInput.select();
    
    let success = false;
    try {
        success = document.execCommand('copy');
    } catch (err) {
        console.error('Failed to copy text: ', err);
    }
    
    document.body.removeChild(tempInput);
    return success;
}

/**
 * Format file size in human-readable format
 * @param {number} bytes - Size in bytes
 * @returns {string} - Formatted size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    
    return parseFloat((bytes / Math.pow(1024, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Share functionality
 * @param {string} title - The title to share
 * @param {string} url - The URL to share
 */
function sharePage(title, url) {
    if (navigator.share) {
        navigator.share({
            title: title,
            url: url
        }).then(() => {
            console.log('Thanks for sharing!');
        }).catch(console.error);
    } else {
        // Fallback for browsers that don't support the Web Share API
        copyToClipboard(url);
        alert('Link copied to clipboard!');
    }
}
