/**
 * GEN-Z LIBRARY
 * Dark Mode Toggle and Theme Management
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get theme toggle button
    const themeToggle = document.getElementById('themeToggle');
    if (!themeToggle) return;
    
    // Initialize theme based on local storage or system preference
    initializeTheme();
    
    // Add click event to theme toggle button
    themeToggle.addEventListener('click', toggleTheme);
    
    // Listen for system theme changes
    watchSystemThemeChanges();
});

/**
 * Initialize theme based on local storage or system preference
 */
function initializeTheme() {
    // Check if theme is stored in local storage
    const storedTheme = localStorage.getItem('theme');
    
    if (storedTheme) {
        // Apply stored theme
        applyTheme(storedTheme);
    } else {
        // Check system preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            applyTheme('dark');
        } else {
            applyTheme('light');
        }
    }
}

/**
 * Toggle between light and dark themes
 */
function toggleTheme() {
    // Get current theme
    const currentTheme = document.documentElement.classList.contains('dark') ? 'dark' : 'light';
    // Toggle to opposite theme
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    // Send theme change to server
    fetch('/toggle-theme', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        // Apply the new theme
        applyTheme(data.theme);
        // Store the theme preference
        localStorage.setItem('theme', data.theme);
    })
    .catch(error => {
        console.error('Error toggling theme:', error);
        // Apply theme anyway in case of error
        applyTheme(newTheme);
        localStorage.setItem('theme', newTheme);
    });
}

/**
 * Apply theme to document and update UI
 * @param {string} theme - 'light' or 'dark'
 */
function applyTheme(theme) {
    // Apply theme class to html element
    if (theme === 'dark') {
        document.documentElement.classList.add('dark');
        document.documentElement.classList.remove('light');
    } else {
        document.documentElement.classList.add('light');
        document.documentElement.classList.remove('dark');
    }
    
    // Update theme toggle button appearance
    updateThemeToggleButton(theme);
    
    // Dispatch theme change event
    document.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme } }));
}

/**
 * Update the theme toggle button appearance
 * @param {string} theme - 'light' or 'dark'
 */
function updateThemeToggleButton(theme) {
    const themeToggle = document.getElementById('themeToggle');
    if (!themeToggle) return;
    
    const sunIcon = themeToggle.querySelector('.fa-sun');
    const moonIcon = themeToggle.querySelector('.fa-moon');
    
    if (theme === 'dark') {
        if (sunIcon) sunIcon.classList.add('hidden');
        if (moonIcon) moonIcon.classList.remove('hidden');
    } else {
        if (sunIcon) sunIcon.classList.remove('hidden');
        if (moonIcon) moonIcon.classList.add('hidden');
    }
}

/**
 * Listen for system theme changes
 */
function watchSystemThemeChanges() {
    if (window.matchMedia) {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        
        // Add change listener
        try {
            // Chrome & Firefox
            mediaQuery.addEventListener('change', (e) => {
                // Only change if user hasn't set a preference
                if (!localStorage.getItem('theme')) {
                    const newTheme = e.matches ? 'dark' : 'light';
                    applyTheme(newTheme);
                }
            });
        } catch (e1) {
            try {
                // Safari
                mediaQuery.addListener((e) => {
                    // Only change if user hasn't set a preference
                    if (!localStorage.getItem('theme')) {
                        const newTheme = e.matches ? 'dark' : 'light';
                        applyTheme(newTheme);
                    }
                });
            } catch (e2) {
                console.error('Error setting up theme change listener:', e2);
            }
        }
    }
}

/**
 * Get current theme
 * @returns {string} - 'light' or 'dark'
 */
function getCurrentTheme() {
    return document.documentElement.classList.contains('dark') ? 'dark' : 'light';
}

/**
 * Expose theme functions globally
 */
window.themeUtils = {
    toggle: toggleTheme,
    apply: applyTheme,
    getCurrent: getCurrentTheme
};
