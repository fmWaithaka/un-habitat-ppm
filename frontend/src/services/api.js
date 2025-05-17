// frontend/src/services/api.js
import axios from 'axios';

// Create the base Axios instance internally
const apiClient = axios.create({
    baseURL: 'http://127.0.0.1:8000/api', // Django API base URL
    headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
});

// Add interceptor to the internal Axios instance
apiClient.interceptors.response.use(
    response => response,
    error => {
        // Handle errors globally here if needed
        console.error('API Error:', error.response || error.message);
        return Promise.reject(error);
    }
);

// Export an OBJECT containing specific API call functions.
// These functions internally use the apiClient instance.
export default {
    // Project Endpoints
    getProjects(params = {}) { // params for pagination, filtering, search
        return apiClient.get('/projects/', { params });
    },
    getProjectById(id) {
        return apiClient.get(`/projects/${id}/`);
    },
    createProject(data) {
        return apiClient.post('/projects/', data);
    },
    updateProject(id, data) {
        return apiClient.put(`/projects/${id}/`, data);
    },
    deleteProject(id) {
        return apiClient.delete(`/projects/${id}/`);
    },

    // Endpoints for related data (for forms, filters, etc.)
    getCountries() {
        return apiClient.get('/countries/');
    },
    getLeadOrgUnits() {
        return apiClient.get('/lead-org-units/');
    },
    getThemes() {
        return apiClient.get('/themes/');
    },
    getDonors() {
        return apiClient.get('/donors/');
    },

    // Custom API endpoints from Django
    getProjectsByCountry(countryName, params = {}) {
        return apiClient.get(`/projects/country/${encodeURIComponent(countryName)}/`, { params });
    },
    getProjectsByStatus(status, params = {}) {
        return apiClient.get(`/projects/status/${encodeURIComponent(status)}/`, { params });
    },

    // --- Dashboard Specific Endpoints ---

    /**
     * Fetches Key Performance Indicators (KPIs) for the dashboard.
     * Corresponds to the /api/dashboard/kpis/ endpoint.
     */
    async getDashboardKPIs() {
      try {
        // Use the internal apiClient instance
        const response = await apiClient.get('/dashboard/kpis/');
        return response.data;
      } catch (error) {
        console.error('Error fetching dashboard KPIs:', error);
        throw error;
      }
    },

    /**
     * Fetches aggregated total PAG value by country, split into single and combined/regional.
     * Corresponds to the /api/dashboard/value-by-country/ endpoint.
     * Returns an object like { single_countries_data: [], combined_data: [] }
     */
    async getValueByCountry() {
      try {
        // Use the internal apiClient instance
        const response = await apiClient.get('/dashboard/value-by-country/');
        // Return the entire data object which contains both lists
        return response.data;
      } catch (error) {
        console.error('Error fetching value by country data:', error);
        throw error;
      }
    },

    /**
     * Fetches aggregated total PAG value by lead organization unit.
     * Corresponds to the /api/dashboard/value-by-lead-org/ endpoint.
     */
    async getValueByLeadOrg() {
      try {
        // Use the internal apiClient instance
        const response = await apiClient.get('/dashboard/value-by-lead-org/');
        return response.data;
      } catch (error) {
        console.error('Error fetching value by lead org unit data:', error);
        throw error;
      }
    },

    /**
     * Fetches aggregated total PAG value by theme.
     * Corresponds to the /api/dashboard/value-by-theme/ endpoint.
     */
    async getValueByTheme() {
      try {
        // Use the internal apiClient instance
        const response = await apiClient.get('/dashboard/value-by-theme/');
        return response.data;
      } catch (error) {
        console.error('Error fetching value by theme data:', error);
        throw error;
      }
    },

    /**
     * Fetches AI-generated insights.
     * Corresponds to the /api/projects/insights/ endpoint.
     */
    async getAIInsights() {
      try {
        // Use the internal apiClient instance
        const response = await apiClient.get('/projects/insights/');
        return response.data;
      } catch (error) {
        console.error('Error fetching AI insights:', error);
        throw error;
      }
    },

    // Add other specific API calls as needed
};
