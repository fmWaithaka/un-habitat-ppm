// src/services/projectService.js
// Purpose: Provides specific functions for interacting with the project-related API endpoints
// using the configured API client. This abstracts the API calls away from the components.

// Import the configured Axios API client
import apiClient from './api';

// Function to fetch all projects
export const getProjects = () => {
  // Makes a GET request to the 'projects/' endpoint relative to the apiClient's baseURL
  // e.g., http://127.0.0.1:8000/api/projects/
  return apiClient.get('projects/');
};

// Function to fetch a single project by its ID
export const getProjectById = (id) => {
  // Makes a GET request to the 'projects/{id}/' endpoint
  // e.g., http://127.0.0.1:8000/api/projects/123/
  return apiClient.get(`projects/${id}/`);
};

// TODO: Add other project-related API functions as needed based on your backend API
// These functions will use apiClient and the appropriate HTTP method (POST, PUT, DELETE)

// Function to create a new project
export const createProject = (data) => {
  // Makes a POST request to the 'projects/' endpoint with the project data
  return apiClient.post('projects/', data);
};

// Example: Function to update an existing project
export const updateProject = (id, data) => {
  // Makes a PUT or PATCH request to the 'projects/{id}/' endpoint with updated data
  return apiClient.put(`projects/${id}/`, data); // Use put for full update, patch for partial
};

// Function to delete a project by its ID
export const deleteProject = (id) => {
  // Makes a DELETE request to the 'projects/{id}/' endpoint
  // e.g., http://127.0.0.1:8000/api/projects/123/
  return apiClient.delete(`projects/${id}/`);
};


// TODO: Add functions for filtering projects by country or status as per your API
// Example: Function to get projects by country name
// export const getProjectsByCountry = (countryName) => {
//   return apiClient.get(`projects/country/${countryName}/`);
// };

// Example: Function to get projects by status key
// export const getProjectsByStatus = (statusKey) => {
//   return apiClient.get(`projects/status/${statusKey}/`);
// };
