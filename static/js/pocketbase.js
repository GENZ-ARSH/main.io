/**
 * GEN-Z LIBRARY
 * PocketBase Integration Client-Side
 */

/**
 * PocketBase API wrapper
 */
class PocketBaseAPI {
    constructor(baseUrl) {
        this.baseUrl = baseUrl || 'http://127.0.0.1:8090';
        this.token = localStorage.getItem('pb_auth') || null;
    }
    
    /**
     * Set authentication token
     * @param {string} token - The auth token
     */
    setToken(token) {
        this.token = token;
        if (token) {
            localStorage.setItem('pb_auth', token);
        } else {
            localStorage.removeItem('pb_auth');
        }
    }
    
    /**
     * Get authentication token
     * @returns {string|null} - The auth token
     */
    getToken() {
        return this.token;
    }
    
    /**
     * Make API request to PocketBase
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Request options
     * @returns {Promise<Object>} - Response data
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}/api/${endpoint}`;
        
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        try {
            const response = await fetch(url, {
                ...options,
                headers
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Error making request to PocketBase');
            }
            
            return await response.json();
        } catch (error) {
            console.error('PocketBase API error:', error);
            throw error;
        }
    }
    
    /**
     * Login user
     * @param {string} email - User email
     * @param {string} password - User password
     * @returns {Promise<Object>} - Auth data
     */
    async login(email, password) {
        try {
            const data = await this.request('collections/users/auth-with-password', {
                method: 'POST',
                body: JSON.stringify({ email, password })
            });
            
            this.setToken(data.token);
            return data;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    }
    
    /**
     * Register user
     * @param {Object} userData - User data
     * @returns {Promise<Object>} - User data
     */
    async register(userData) {
        try {
            return await this.request('collections/users/records', {
                method: 'POST',
                body: JSON.stringify(userData)
            });
        } catch (error) {
            console.error('Registration error:', error);
            throw error;
        }
    }
    
    /**
     * Logout user
     */
    logout() {
        this.setToken(null);
    }
    
    /**
     * Get books with optional filters
     * @param {Object} filters - Filter parameters
     * @returns {Promise<Array>} - Books data
     */
    async getBooks(filters = {}) {
        let queryParams = '';
        
        if (Object.keys(filters).length > 0) {
            const params = new URLSearchParams();
            
            if (filters.category) {
                params.append('filter', `category='${filters.category}'`);
            }
            
            if (filters.search) {
                const searchFilter = `title~'${filters.search}' || author~'${filters.search}'`;
                if (params.has('filter')) {
                    params.set('filter', `${params.get('filter')} && (${searchFilter})`);
                } else {
                    params.append('filter', searchFilter);
                }
            }
            
            if (filters.tag) {
                const tagFilter = `tags~'${filters.tag}'`;
                if (params.has('filter')) {
                    params.set('filter', `${params.get('filter')} && (${tagFilter})`);
                } else {
                    params.append('filter', tagFilter);
                }
            }
            
            queryParams = `?${params.toString()}`;
        }
        
        try {
            const data = await this.request(`collections/books/records${queryParams}`);
            return data.items;
        } catch (error) {
            console.error('Error fetching books:', error);
            throw error;
        }
    }
    
    /**
     * Get single book by ID
     * @param {string} id - Book ID
     * @returns {Promise<Object>} - Book data
     */
    async getBook(id) {
        try {
            return await this.request(`collections/books/records/${id}`);
        } catch (error) {
            console.error(`Error fetching book ${id}:`, error);
            throw error;
        }
    }
    
    /**
     * Create a book request
     * @param {Object} requestData - Request data
     * @returns {Promise<Object>} - Request data
     */
    async createBookRequest(requestData) {
        try {
            return await this.request('collections/bookRequests/records', {
                method: 'POST',
                body: JSON.stringify(requestData)
            });
        } catch (error) {
            console.error('Error creating book request:', error);
            throw error;
        }
    }
    
    /**
     * Create an admin request
     * @param {Object} requestData - Request data
     * @returns {Promise<Object>} - Request data
     */
    async createAdminRequest(requestData) {
        try {
            return await this.request('collections/adminRequests/records', {
                method: 'POST',
                body: JSON.stringify(requestData)
            });
        } catch (error) {
            console.error('Error creating admin request:', error);
            throw error;
        }
    }
    
    /**
     * Upload a book (admin only)
     * @param {Object} bookData - Book data
     * @returns {Promise<Object>} - Book data
     */
    async uploadBook(bookData) {
        try {
            return await this.request('collections/books/records', {
                method: 'POST',
                body: JSON.stringify(bookData)
            });
        } catch (error) {
            console.error('Error uploading book:', error);
            throw error;
        }
    }
}

// Initialize PocketBase API
const pocketBase = new PocketBaseAPI(window.pbBaseUrl || 'http://127.0.0.1:8090');

// Export for global access
window.pocketBase = pocketBase;
