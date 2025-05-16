// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import ProjectListPage from '../views/ProjectListPage.vue';
import ProjectDetailPage from '../views/ProjectDetailPage.vue';
import ProjectCreateView from '../views/ProjectCreateView.vue';
import ProjectEditView from '../views/ProjectEditView.vue'; 

const routes = [
  {
    path: '/',
    name: 'ProjectList',
    component: ProjectListPage
  },
  {
    // Route for viewing a single project's details
    // :id is a dynamic route parameter that will hold the project's ID
    path: '/project/:id', 
    name: 'ProjectDetail',
    component: ProjectDetailPage,
    props: true // This allows the route param 'id' to be passed as a prop to ProjectDetailPage
  },
  {
    path: '/projects/:id/edit', // Route for editing a project
    name: 'EditProject',
    component: ProjectEditView,
    props: true // Pass route params as props to the component
  },
  {
    path: '/projects/create', // Route for creating a new project
    name: 'CreateProject',
    component: ProjectCreateView // Reuse ProjectEditView for creation
  },
  {
    path: '/dashboard', 
    name: 'Dashboard',
    // component: () => import('../views/DashboardPage.vue') // Lazy load example
    component: { template: '<div>Dashboard Page - Coming Soon!</div>' } // Placeholder
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
});

export default router;