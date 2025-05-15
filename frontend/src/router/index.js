// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import ProjectListPage from '../views/ProjectListPage.vue';

const routes = [
  {
    path: '/',
    name: 'ProjectList',
    component: ProjectListPage
  },
  // You can add more routes here later
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
});

export default router;