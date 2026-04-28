/**
 * CrisisSignal AI — API Wrapper (api.js)
 * Single source of truth for all API calls.
 */

const API = {
    /**
     * Make a fetch request with JSON handling
     */
    async request(url, options = {}) {
        const defaults = {
            headers: { 'Content-Type': 'application/json' },
        };
        const config = { ...defaults, ...options };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP ${response.status}`);
            }
            return data;
        } catch (error) {
            console.error(`API Error [${url}]:`, error);
            throw error;
        }
    },

    // ── Alerts ────────────────────────────────────────────
    async getAlerts(filters = {}) {
        const params = new URLSearchParams(filters).toString();
        return this.request(`/api/alerts${params ? '?' + params : ''}`);
    },

    async getAlert(alertId) {
        return this.request(`/api/alerts/${alertId}`);
    },

    async createAlert(message, location) {
        return this.request('/api/alerts', {
            method: 'POST',
            body: JSON.stringify({ message, location }),
        });
    },

    async previewAlert(message) {
        return this.request('/api/alerts/preview', {
            method: 'POST',
            body: JSON.stringify({ message }),
        });
    },

    // ── Votes ─────────────────────────────────────────────
    async castVote(alertId, voteType) {
        return this.request(`/api/alerts/${alertId}/vote`, {
            method: 'POST',
            body: JSON.stringify({ vote: voteType }),
        });
    },

    // ── Dashboard ─────────────────────────────────────────
    async getDashboardStats() {
        return this.request('/api/dashboard/stats');
    },

    // ── User ──────────────────────────────────────────────
    async getCurrentUser() {
        return this.request('/api/users/me');
    },

    // ── Demo ──────────────────────────────────────────────
    async getDemoScenarios() {
        return this.request('/demo/scenarios');
    },

    async resetSystem() {
        return this.request('/api/reset', { method: 'POST' });
    },
};
