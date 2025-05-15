// src/services/api.js
import axios from 'axios';

// Create a custom Axios instance
const apiClient = axios.create({
  // Set the base URL for all requests made with this instance.
  // It reads the VITE_API_BASE_URL environment variable defined in your .env file.
  // This makes your API URL configurable without changing code.
  // Provide a fallback URL in case the environment variable is not set.
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/',

  // Set default headers for requests
  headers: {
    'Content-Type': 'application/json', // Indicate that we are sending/expecting JSON
    // Add other headers here if needed (e.g., Accept, Authorization)
  }

  // You can add other Axios configurations here, like timeout
  // timeout: 5000, // Example: Request will time out after 5 seconds
});

// Optional: Add Axios interceptors for global handling of requests or responses.
// Interceptors can be used for tasks like:
// - Adding authentication tokens to request headers
// - Handling global errors (e.g., redirecting to login on 401 Unauthorized)
// - Logging requests/responses

// Example Request Interceptor: Add Authorization header
// apiClient.interceptors.request.use(config => {
//   const token = localStorage.getItem('authToken'); // Get token from local storage or state management
//   if (token) {
//     config.headers.Authorization = `Bearer ${token}`; // Add Bearer token
//   }
//   return config; // Return the updated config
// }, error => {
//   return Promise.reject(error); // Handle request error
// });

// Example Response Interceptor: Handle 401 Unauthorized errors
// apiClient.interceptors.response.use(response => response, error => {
//   if (error.response && error.response.status === 401) {
//     console.error("API request unauthorized. Redirecting to login...");
//     // TODO: Implement actual redirect logic here (e.g., using router.push)
//     // Make sure the router instance is accessible or handle this differently
//     // router.push('/login');
//   }
//   return Promise.reject(error); // Propagate the error
// });

// Export the configured Axios instance
export default apiClient;
