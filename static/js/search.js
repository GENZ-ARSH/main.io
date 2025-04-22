/**
 * GEN-Z LIBRARY
 * Search and Filtering Functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize search functionality
    initializeSearch();
    
    // Initialize filter functionality
    initializeFilters();
    
    // Initialize tag cloud functionality
    initializeTagCloud();
});

/**
 * Initialize search functionality
 */
function initializeSearch() {
    const searchForm = document.getElementById('searchForm');
    if (!searchForm) return;
    
    const searchInput = document.getElementById('search');
    if (!searchInput) return;
    
    // Add input event to enable live search
    searchInput.addEventListener('input', debounce(function() {
        const searchTerm = this.value.trim();
        
        // Only search if term is at least 2 characters or empty
        if (searchTerm.length >= 2 || searchTerm.length === 0) {
            // If we want real-time search, we can implement it here
            // For now, we'll just submit the form on Enter key
        }
    }, 500));
    
    // Submit form on Enter key
    searchInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            searchForm.submit();
        }
    });
    
    // Clear search button
    const clearSearchButton = document.getElementById('clearSearch');
    if (clearSearchButton) {
        clearSearchButton.addEventListener('click', function() {
            searchInput.value = '';
            searchForm.submit();
        });
    }
}

/**
 * Initialize filter functionality
 */
function initializeFilters() {
    const resetFiltersButton = document.getElementById('resetFilters');
    if (!resetFiltersButton) return;
    
    resetFiltersButton.addEventListener('click', function() {
        // Reset all checkboxes
        document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
            checkbox.checked = false;
        });
        
        // Get the base URL without query parameters
        const url = window.location.href.split('?')[0];
        
        // Redirect to base URL
        window.location.href = url;
    });
    
    // Apply filters when checkboxes change
    const filterCheckboxes = document.querySelectorAll('input[type="checkbox"][name]');
    filterCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', applyFilters);
    });
}

/**
 * Apply filters and update URL
 */
function applyFilters() {
    // Get current URL and create URL object
    let url = new URL(window.location.href);
    let searchParams = new URLSearchParams(url.search);
    
    // Get all filter groups
    const filterGroups = {};
    
    // Process each checkbox
    document.querySelectorAll('input[type="checkbox"]:checked').forEach(checkbox => {
        const name = checkbox.getAttribute('name');
        const value = checkbox.value;
        
        if (!filterGroups[name]) {
            filterGroups[name] = [];
        }
        
        filterGroups[name].push(value);
    });
    
    // Update search params with filter groups
    for (const [name, values] of Object.entries(filterGroups)) {
        if (values.length > 0) {
            searchParams.set(name, values.join(','));
        } else {
            searchParams.delete(name);
        }
    }
    
    // Keep search term if it exists
    const searchInput = document.getElementById('search');
    if (searchInput && searchInput.value) {
        searchParams.set('search', searchInput.value);
    }
    
    // Keep tag if it exists
    if (url.searchParams.has('tag')) {
        searchParams.set('tag', url.searchParams.get('tag'));
    }
    
    // Create the new URL
    const newUrl = `${url.pathname}?${searchParams.toString()}`;
    
    // Update browser URL without reloading the page
    window.history.pushState({}, '', newUrl);
    
    // Here we could implement AJAX-based filtering to avoid page reload
    // For now, we'll just reload the page with the new URL
    window.location.href = newUrl;
}

/**
 * Initialize tag cloud functionality
 */
function initializeTagCloud() {
    const tagCloud = document.querySelector('.flex.flex-wrap.gap-2');
    if (!tagCloud) return;
    
    // Add click handler for tag links
    const tagLinks = tagCloud.querySelectorAll('a');
    tagLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            
            // Get the tag from the link
            const tag = this.textContent.trim();
            
            // Get current URL and create URL object
            let url = new URL(window.location.href);
            let searchParams = new URLSearchParams(url.search);
            
            // Update search params with the tag
            searchParams.set('tag', tag);
            
            // Create the new URL
            const newUrl = `${url.pathname}?${searchParams.toString()}`;
            
            // Navigate to the new URL
            window.location.href = newUrl;
        });
    });
}

/**
 * Debounce function to limit how often a function can be called
 * @param {Function} func - The function to debounce
 * @param {number} wait - The debounce wait time in milliseconds
 * @returns {Function} - The debounced function
 */
function debounce(func, wait) {
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
 * Highlight search terms in text
 * @param {string} text - The text to highlight in
 * @param {string} term - The term to highlight
 * @returns {string} - Text with highlighted terms
 */
function highlightSearchTerm(text, term) {
    if (!term || !text) return text;
    
    const regex = new RegExp(`(${term})`, 'gi');
    return text.replace(regex, '<mark class="bg-yellow-200 dark:bg-yellow-800">$1</mark>');
}

/**
 * Update book display based on filters
 * This would be used for client-side filtering if implemented
 * @param {Object} filters - The active filters
 */
function updateBookDisplay(filters) {
    const bookCards = document.querySelectorAll('.book-card');
    
    bookCards.forEach(card => {
        let shouldShow = true;
        
        // Check each filter type
        if (filters.subject && filters.subject.length > 0) {
            const cardSubject = card.getAttribute('data-subject').toLowerCase();
            shouldShow = shouldShow && filters.subject.some(subject => 
                cardSubject === subject.toLowerCase()
            );
        }
        
        if (filters.format && filters.format.length > 0) {
            const cardFormat = card.getAttribute('data-format').toLowerCase();
            shouldShow = shouldShow && filters.format.some(format => 
                cardFormat === format.toLowerCase()
            );
        }
        
        // More filter types can be added here
        
        // Show or hide the card
        if (shouldShow) {
            card.classList.remove('hidden');
        } else {
            card.classList.add('hidden');
        }
    });
}
