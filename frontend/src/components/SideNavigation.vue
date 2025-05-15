<template>
  <nav class="side-navigation">
    <div class="logo-area">
      <img v-if="logoUrl" :src="logoUrl" alt="App Logo" class="app-logo" />
      <span v-else class="app-logo-placeholder">LOGO</span>
      <span class="app-name">UN-Habitat</span>
    </div>
    <ul>
      <li class="nav-item" :class="{ active: isActive('/') }"> 
        <router-link to="/">
          <span class="nav-icon">🗂️</span> Projects
        </router-link>
      </li>
      <li class="nav-item" :class="{ active: isActive('/dashboard') }">
        <router-link to="/dashboard">
          <span class="nav-icon">📊</span> Dashboard
        </router-link>
      </li>
      </ul>
    <div class="nav-footer">
        <div class="user-profile">
            <div class="user-avatar-placeholder">FW</div>
            <span class="user-name">Francis Waithaka</span>
        </div>
        <a href="#" @click.prevent="logout" class="nav-item-footer">
            <span class="nav-icon">↩️</span>
            Logout
        </a>
    </div>
  </nav>
</template>

<script setup>
import { useRoute } from 'vue-router';
import logoUrl from '@/assets/un-logo-white.png';

const route = useRoute();

const isActive = (path) => {
  return route.path === path;
};

const logout = () => {
    alert("Logout action placeholder");
    // router.push('/login'); // Example redirect
}
</script>

<style scoped>
.side-navigation {
  width: 260px; /* Width of the sidebar */
  height: 100vh; /* Full viewport height */
  background-color: #1a202c; /* Dark background like image */
  color: #a0aec0; /* Light grey text for less important items */
  display: flex;
  flex-direction: column;
  position: fixed; /* Fixed position */
  left: 0;
  top: 0;
  z-index: 1000; /* High z-index to stay on top */
  box-shadow: 2px 0 8px rgba(0,0,0,0.15); /* Subtle shadow */
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.logo-area {
  display: flex;
  align-items: center;
  padding: 20px 20px 20px 25px; /* More padding on left */
  border-bottom: 1px solid #2d3748; /* Separator line */
  margin-bottom: 15px; /* Space before nav items */
}

.app-logo {
  height: 32px;
  margin-right: 12px;
}
.app-logo-placeholder {
  display: inline-block;
  width: 32px;
  height: 32px;
  line-height: 32px;
  text-align: center;
  background-color: #4a5568;
  color: #e2e8f0;
  font-weight: bold;
  border-radius: 4px;
  margin-right: 12px;
}

.app-name {
  font-size: 1.15em;
  font-weight: 600;
  color: #e2e8f0; /* Lighter color for app name */
}

.side-navigation ul {
  list-style: none;
  padding: 0;
  margin: 0;
  flex-grow: 1; /* Allows footer to be pushed down */
}

.nav-item a, .nav-item-footer {
  display: flex;
  align-items: center;
  padding: 13px 25px; /* Padding for nav items */
  text-decoration: none;
  color: #cbd5e0; /* Brighter default text color */
  font-size: 0.92em; /* Slightly smaller font */
  font-weight: 500;
  transition: background-color 0.2s ease, color 0.2s ease, border-left-color 0.2s ease;
  border-left: 4px solid transparent; /* For active indicator */
  margin: 2px 0; /* Small vertical margin between items */
}

.nav-item a:hover {
  background-color: #2d3748; /* Slightly lighter dark on hover */
  color: #ffffff; /* White text on hover */
  border-left-color: #4a5568; /* Subtle indicator on hover */
}

.nav-item.active a {
  background-color: #2c5282; /* Active background (blueish) */
  color: #ffffff; /* White text for active */
  font-weight: 600;
  border-left-color: #63b3ed; /* Active indicator color (brighter blue) */
}
.nav-item.active .nav-icon {
  opacity: 1;
}

.nav-icon {
  margin-right: 15px;
  width: 20px;
  text-align: center;
  font-size: 1.1em; /* Slightly larger icons */
  opacity: 0.8; /* Slightly faded icons for non-active items */
}

.nav-footer {
  padding: 15px 0px; /* Reduced top/bottom padding */
  border-top: 1px solid #2d3748;
}

.user-profile {
  display: flex;
  align-items: center;
  padding: 10px 25px;
  margin-bottom: 10px;
  color: #e2e8f0;
}

.user-avatar-placeholder {
  width: 36px;
  height: 36px;
  line-height: 36px;
  text-align: center;
  background-color: #4a5568;
  color: #e2e8f0;
  font-weight: bold;
  border-radius: 50%;
  margin-right: 12px;
  font-size: 1em;
}
.user-name {
    font-size: 0.9em;
    font-weight: 500;
}

.nav-item-footer {
    margin-top: 5px; /* Space above logout or other footer items */
}
.nav-item-footer:hover {
  background-color: #2d3748;
  color: #ffffff;
  border-left-color: #4a5568;
}

</style>