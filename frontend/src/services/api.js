// frontend/src/services/api.js
import axios from 'axios';

const apiClient = axios.create({
    baseURL: 'http://127.0.0.1:8000/api', //Django API base URL
    headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
});

// Interceptor for handling API errors (optional but good practice)
apiClient.interceptors.response.use(
    response => response,
    error => {
        // Handle errors globally here if needed
        // e.g., redirect to login on 401, show a toast notification, etc.
        console.error('API Error:', error.response || error.message);
        return Promise.reject(error);
    }
);

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

    // Custom API endpoints from Django (if you created them)
    getProjectsByCountry(countryName, params = {}) {
        return apiClient.get(`/projects/country/${encodeURIComponent(countryName)}/`, { params });
    },
    getProjectsByStatus(status, params = {}) {
        return apiClient.get(`/projects/status/${encodeURIComponent(status)}/`, { params });
    }
    // Add other specific API calls as needed
};