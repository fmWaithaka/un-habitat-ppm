// src/services/projectService.js
// Purpose: Provides specific functions for interacting with the project-related API endpoints.

import apiClient from './api';

// Function to fetch all projects
export const getProjects = () => {
  return apiClient.get('projects/');
};

// Function to fetch a single project by its ID
export const getProjectById = (id) => {
  return apiClient.get(`projects/${id}/`);
};

// Function to delete a project by its ID
export const deleteProject = (id) => {
  return apiClient.delete(`projects/${id}/`);
};

// Function to create a new project
export const createProject = (data) => {
  return apiClient.post('projects/', data);
};

// Function to update an existing project by its ID
export const updateProject = (id, data) => {
  // Makes a PUT request to the 'projects/{id}/' endpoint with the updated data
  // Use apiClient.patch(`projects/${id}/`, data) for partial updates if preferred
  return apiClient.put(`projects/${id}/`, data);
};


// --- New Functions for Dashboard Aggregated Data ---

// Function to get project count aggregated by country
export const getProjectCountByCountry = () => {
  return apiClient.get('projects/summary/by_country/');
};

// Function to get project count aggregated by lead organization unit
export const getProjectCountByOrgUnit = () => {
  return apiClient.get('projects/summary/by_org_unit/');
};

// Function to get project count aggregated by theme
export const getProjectCountByTheme = () => {
  return apiClient.get('projects/summary/by_theme/');
};

// Function to get data for world map visualization (project count by country)
export const getWorldMapProjectData = () => {
   // Reusing the country count endpoint for map data as planned
   return apiClient.get('projects/summary/world_map_data/');
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

// TODO: Add service functions to fetch lists for dropdowns (Countries, etc.)
// Example: Function to get all countries
// export const getCountries = () => {
//   return apiClient.get('countries/'); // Assuming you have a /api/countries/ endpoint
// };
