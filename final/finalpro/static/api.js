// TweetBar API Client
class TweetAPI {
    constructor() {
        this.baseURL = '/api';
        this.token = localStorage.getItem('authToken');
    }

    // Get headers with authentication
    getHeaders(includeAuth = true) {
        const headers = {
            'Content-Type': 'application/json',
        };
        if (includeAuth && this.token) {
            headers['Authorization'] = `Token ${this.token}`;
        }
        return headers;
    }

    // Authentication methods
    async register(username, email, password, password2) {
        try {
            const response = await fetch(`${this.baseURL}/auth/register/`, {
                method: 'POST',
                headers: this.getHeaders(false),
                body: JSON.stringify({ username, email, password, password2 })
            });
            const data = await response.json();
            if (response.ok) {
                this.token = data.token;
                localStorage.setItem('authToken', data.token);
                localStorage.setItem('currentUser', JSON.stringify(data.user));
                return { success: true, data };
            }
            return { success: false, errors: data };
        } catch (error) {
            return { success: false, errors: { detail: 'Network error' } };
        }
    }

    async login(username, password) {
        try {
            const response = await fetch(`${this.baseURL}/auth/login/`, {
                method: 'POST',
                headers: this.getHeaders(false),
                body: JSON.stringify({ username, password })
            });
            const data = await response.json();
            if (response.ok) {
                this.token = data.token;
                localStorage.setItem('authToken', data.token);
                localStorage.setItem('currentUser', JSON.stringify(data.user));
                return { success: true, data };
            }
            return { success: false, errors: data };
        } catch (error) {
            return { success: false, errors: { detail: 'Network error' } };
        }
    }

    async logout() {
        try {
            await fetch(`${this.baseURL}/auth/logout/`, {
                method: 'POST',
                headers: this.getHeaders()
            });
        } catch (error) {
            console.error('Logout error:', error);
        }
        this.token = null;
        localStorage.removeItem('authToken');
        localStorage.removeItem('currentUser');
    }

    async getCurrentUser() {
        if (!this.token) return null;
        try {
            const response = await fetch(`${this.baseURL}/auth/me/`, {
                headers: this.getHeaders()
            });
            if (response.ok) {
                const user = await response.json();
                localStorage.setItem('currentUser', JSON.stringify(user));
                return user;
            }
        } catch (error) {
            console.error('Get current user error:', error);
        }
        return null;
    }

    isAuthenticated() {
        return !!this.token;
    }

    // Tweet methods
    async getTweets(page = 1, search = '', ordering = '') {
        try {
            let url = `${this.baseURL}/tweets/?page=${page}`;
            if (search) url += `&search=${encodeURIComponent(search)}`;
            if (ordering) url += `&ordering=${ordering}`;
            
            const response = await fetch(url, {
                headers: this.getHeaders(false)
            });
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Get tweets error:', error);
        }
        return null;
    }

    async getTweet(id) {
        try {
            const response = await fetch(`${this.baseURL}/tweets/${id}/`, {
                headers: this.getHeaders(false)
            });
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Get tweet error:', error);
        }
        return null;
    }

    async createTweet(text, imageFile = null) {
        try {
            const formData = new FormData();
            formData.append('text', text);
            if (imageFile) {
                formData.append('image', imageFile);
            }

            const response = await fetch(`${this.baseURL}/tweets/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Token ${this.token}`
                },
                body: formData
            });
            const data = await response.json();
            if (response.ok) {
                return { success: true, data };
            }
            return { success: false, errors: data };
        } catch (error) {
            return { success: false, errors: { detail: 'Network error' } };
        }
    }

    async updateTweet(id, text, imageFile = null) {
        try {
            const formData = new FormData();
            formData.append('text', text);
            if (imageFile) {
                formData.append('image', imageFile);
            }

            const response = await fetch(`${this.baseURL}/tweets/${id}/`, {
                method: 'PATCH',
                headers: {
                    'Authorization': `Token ${this.token}`
                },
                body: formData
            });
            const data = await response.json();
            if (response.ok) {
                return { success: true, data };
            }
            return { success: false, errors: data };
        } catch (error) {
            return { success: false, errors: { detail: 'Network error' } };
        }
    }

    async deleteTweet(id) {
        try {
            const response = await fetch(`${this.baseURL}/tweets/${id}/`, {
                method: 'DELETE',
                headers: this.getHeaders()
            });
            if (response.status === 204) {
                return { success: true };
            }
            return { success: false, errors: { detail: 'Failed to delete' } };
        } catch (error) {
            return { success: false, errors: { detail: 'Network error' } };
        }
    }
}

// Export global instance
window.tweetAPI = new TweetAPI();
