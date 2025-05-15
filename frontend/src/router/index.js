// src/router/index.js

import { createRouter, createWebHistory } from 'vue-router';

// Import the view components for the routes
import ProjectListView from '../views/ProjectListView.vue';
import DashboardView from '../views/DashboardView.vue'; // <-- Ensure this is imported
import ProjectDetailView from '../views/ProjectDetailView.vue';
import ProjectCreateView from '../views/ProjectCreateView.vue';
import ProjectEditView from '../views/ProjectEditView.vue';

// Define the route configurations
const routes = [
  {
    path: '/',
    name: 'Projects', // Name for the Projects List route
    component: ProjectListView,
  },
  {
    path: '/dashboard',
    name: 'Dashboard', // Name for the Dashboard route
    component: DashboardView, // <-- Ensure this is mapped
  },
  {
    path: '/projects/:id',
    name: 'ProjectDetails', // Name for the Project Details route
    component: ProjectDetailView,
    props: true
  },
  {
    path: '/projects/create', // The URL path for creating a project
    name: 'ProjectCreate', // Unique name for the Create route
    component: ProjectCreateView,
  },
  {
    path: '/projects/:id/edit',
    name: 'ProjectEdit', // Unique name for the Edit route
    component: ProjectEditView,
    props: true
  },
];

// Create the router instance
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

export default router;
