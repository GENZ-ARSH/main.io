/**
 * GEN-Z LIBRARY
 * Admin Dashboard JavaScript Functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on admin page
    if (!document.getElementById('adminTabs')) return;
    
    // Initialize admin dashboard functionality
    initializeAdminDashboard();
    
    // Initialize book upload form functionality
    initializeBookUploadForm();
    
    // Initialize admin request handling
    initializeAdminRequests();
    
    // Initialize book request handling
    initializeBookRequests();
});

/**
 * Initialize Admin Dashboard functionality
 */
function initializeAdminDashboard() {
    const tabs = document.querySelectorAll('[role="tab"]');
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
            
            // Save active tab to session storage
            sessionStorage.setItem('activeAdminTab', tabId);
        });
    });
    
    // Restore active tab from session storage
    const activeTab = sessionStorage.getItem('activeAdminTab');
    if (activeTab) {
        const tabElement = document.querySelector(`[data-tab="${activeTab}"]`);
        if (tabElement) {
            tabElement.click();
        }
    }
    
    // Add confirmation for delete operations
    initializeDeleteConfirmations();
}

/**
 * Initialize delete confirmations
 */
function initializeDeleteConfirmations() {
    const deleteForms = document.querySelectorAll('form[onsubmit*="confirm"]');
    
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(event) {
            const confirmed = confirm('Are you sure you want to delete this item? This action cannot be undone.');
            if (!confirmed) {
                event.preventDefault();
            }
        });
    });
}

/**
 * Initialize Book Upload Form functionality
 */
function initializeBookUploadForm() {
    const uploadForm = document.querySelector('form[action*="upload-book"]');
    if (!uploadForm) return;
    
    // Form validation
    uploadForm.addEventListener('submit', function(event) {
        let isValid = true;
        const requiredFields = uploadForm.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                field.classList.add('border-red-500');
                
                // Add error message if not exists
                if (!field.nextElementSibling || !field.nextElementSibling.classList.contains('error-message')) {
                    const errorMessage = document.createElement('p');
                    errorMessage.classList.add('error-message', 'text-red-500', 'text-xs', 'mt-1');
                    errorMessage.textContent = 'This field is required';
                    field.parentNode.insertBefore(errorMessage, field.nextElementSibling);
                }
            } else {
                field.classList.remove('border-red-500');
                
                // Remove error message if exists
                if (field.nextElementSibling && field.nextElementSibling.classList.contains('error-message')) {
                    field.nextElementSibling.remove();
                }
            }
        });
        
        if (!isValid) {
            event.preventDefault();
            // Scroll to the first error
            const firstError = uploadForm.querySelector('.border-red-500');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                firstError.focus();
            }
        }
    });
    
    // Dynamic Tags Input
    const tagsInput = document.getElementById('tags');
    if (tagsInput) {
        tagsInput.addEventListener('keydown', function(event) {
            if (event.key === ',') {
                event.preventDefault();
                const value = this.value.trim();
                if (value) {
                    this.value = value + ', ';
                }
            }
        });
    }
}

/**
 * Initialize Admin Request handling
 */
function initializeAdminRequests() {
    const approveButtons = document.querySelectorAll('form[action*="approve-admin-request"]');
    const rejectButtons = document.querySelectorAll('form[action*="reject-admin-request"]');
    
    // Add confirmation for approve operations
    approveButtons.forEach(form => {
        form.addEventListener('submit', function(event) {
            const confirmed = confirm('Are you sure you want to approve this admin request? The user will gain admin privileges.');
            if (!confirmed) {
                event.preventDefault();
            }
        });
    });
    
    // Add confirmation for reject operations
    rejectButtons.forEach(form => {
        form.addEventListener('submit', function(event) {
            const confirmed = confirm('Are you sure you want to reject this admin request?');
            if (!confirmed) {
                event.preventDefault();
            }
        });
    });
}

/**
 * Initialize Book Request handling
 */
function initializeBookRequests() {
    // Add click handlers for approve/reject buttons
    const requestsTab = document.getElementById('requests');
    if (!requestsTab) return;
    
    // Get all approve buttons in the requests tab
    const approveButtons = requestsTab.querySelectorAll('.text-green-600');
    
    approveButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Get the request information
            const row = this.closest('tr');
            const bookName = row.querySelector('td:first-child').textContent;
            
            const confirmed = confirm(`Are you sure you want to approve the request for "${bookName}"?`);
            if (confirmed) {
                // Here we would submit a form or make an API call
                // For now, we'll just update the UI
                const statusCell = row.querySelector('td:nth-child(5) span');
                statusCell.textContent = 'approved';
                statusCell.classList.remove('bg-yellow-100', 'text-yellow-800', 'dark:bg-yellow-900', 'dark:text-yellow-200');
                statusCell.classList.add('bg-green-100', 'text-green-800', 'dark:bg-green-900', 'dark:text-green-200');
                
                // Disable buttons
                this.disabled = true;
                row.querySelector('.text-red-600').disabled = true;
            }
        });
    });
    
    // Get all reject buttons in the requests tab
    const rejectButtons = requestsTab.querySelectorAll('.text-red-600');
    
    rejectButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Get the request information
            const row = this.closest('tr');
            const bookName = row.querySelector('td:first-child').textContent;
            
            const confirmed = confirm(`Are you sure you want to reject the request for "${bookName}"?`);
            if (confirmed) {
                // Here we would submit a form or make an API call
                // For now, we'll just update the UI
                const statusCell = row.querySelector('td:nth-child(5) span');
                statusCell.textContent = 'rejected';
                statusCell.classList.remove('bg-yellow-100', 'text-yellow-800', 'dark:bg-yellow-900', 'dark:text-yellow-200');
                statusCell.classList.add('bg-red-100', 'text-red-800', 'dark:bg-red-900', 'dark:text-red-200');
                
                // Disable buttons
                this.disabled = true;
                row.querySelector('.text-green-600').disabled = true;
            }
        });
    });
}

/**
 * Get book statistics and update dashboard
 */
function updateBookStatistics() {
    fetch('/admin/stats')
        .then(response => response.json())
        .then(data => {
            // Update stats in UI
            document.getElementById('totalBooks').textContent = data.totalBooks;
            document.getElementById('totalDownloads').textContent = data.totalDownloads;
            
            // More stats could be added here
        })
        .catch(error => {
            console.error('Error fetching admin stats:', error);
        });
}

/**
 * Clear form fields
 * @param {HTMLFormElement} form - The form to clear
 */
function clearForm(form) {
    const inputs = form.querySelectorAll('input, textarea, select');
    
    inputs.forEach(input => {
        if (input.type === 'checkbox' || input.type === 'radio') {
            input.checked = false;
        } else {
            input.value = '';
        }
        
        // Remove validation styles
        input.classList.remove('border-red-500');
        
        // Remove error messages
        if (input.nextElementSibling && input.nextElementSibling.classList.contains('error-message')) {
            input.nextElementSibling.remove();
        }
    });
}
