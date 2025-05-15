import { createRouter, createWebHistory } from 'vue-router';

// Import the view components for the routes
import ProjectListView from '../views/ProjectListView.vue';
import DashboardView from '../views/DashboardView.vue'; // Placeholder view for now

import ProjectDetailView from '../views/ProjectDetailView.vue';

// Define the route configurations
const routes = [
  {
    path: '/', // The URL path for this route
    name: 'Projects', // A unique name for the route
    component: ProjectListView, // The component to render when this path is matched
    // Optional: Add meta fields for transitions, auth, etc.
    // meta: { transition: 'slide-right' }
  },
  {
    path: '/dashboard', // The URL path for the dashboard
    name: 'Dashboard', // A unique name for the dashboard route
    component: DashboardView, // The component to render for the dashboard
    // Example of lazy loading for better performance on initial load:
    // component: () => import('../views/DashboardView.vue')
  },
  {
    path: '/projects/:id',
    name: 'ProjectDetails', // Unique name for the Project Details route
    component: ProjectDetailView, // Component to render
    props: true // This tells Vue Router to pass the route parameters (like 'id') as props to the component
  },
  // TODO: Add routes for creating and editing projects later
  // {
  //   path: '/projects/create',
  //   name: 'ProjectCreate',
  //   component: () => import('../views/ProjectCreateView.vue'),
  // },
  // {
  //   path: '/projects/:id/edit',
  //   name: 'ProjectEdit',
  //   component: () => import('../views/ProjectEditView.vue'),
  //   props: true
  // },
];

// Create the router instance
const router = createRouter({
  // Use createWebHistory for cleaner URLs (e.g., /projects instead of /#/projects)
  history: createWebHistory(import.meta.env.BASE_URL),
  // Pass the defined routes array to the router
  routes,
});

// Export the router instance to be used in main.js
export default router;
