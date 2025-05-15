<template>
  <div id="app-container">
    <Navbar />

    <main class="main-content">
      <router-view v-slot="{ Component, route }">
        <transition :name="route.meta.transition || 'fade'" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <footer class="app-footer">
      <p>&copy; {{ new Date().getFullYear() }} UN Habitat Project Portfolio Management</p>
    </footer>
  </div>
</template>

<script setup>
// Import the Navbar component
import Navbar from './components/Navbar.vue';

// No specific script logic needed for App.vue in this phase.
// The <script setup> syntax automatically exposes variables and functions
// declared at the top level to the template.
</script>

<style scoped>
/* Scoped styles specific to App.vue */

/* Main container for the entire application layout */
.app-container {
  display: flex;
  flex-direction: column; /* Stack children vertically */
  min-height: 100vh; /* Ensure the container takes at least the full viewport height */
  /* ... other styles */
}

.main-content {
  flex-grow: 1; /* Allow the main content area to take up all available space */
  padding: 20px; /* Add padding around the content area */
  /* ... other styles */
}
/* Styles for the application footer */
.app-footer {
  /* Use CSS variables for background and text colors defined in global.css */
  background-color: var(--color-background-nav); /* Often same as navbar background */
  color: var(--color-text-nav); /* Often same as navbar text color */
  text-align: center; /* Center the footer text */
  padding: 15px 20px; /* Padding inside the footer */
  font-size: 0.9em; /* Slightly smaller font size for the footer */
  border-top: 1px solid var(--color-border); /* Add a border at the top of the footer */
  flex-shrink: 0; /* Prevent the footer from shrinking */
}

/* Basic fade transition for route changes */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease; /* Apply a smooth transition to opacity over 0.3 seconds */
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0; /* Start/end with zero opacity (fully transparent) */
}
</style>
