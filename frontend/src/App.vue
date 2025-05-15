<template>
  <div id="app-layout"> <SideNavigation v-if="showSidebar" /> <main class="main-content-area" :class="{ 'with-sidebar': showSidebar }">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import SideNavigation from '@/components/SideNavigation.vue'; // Adjust path if needed
import { computed } from 'vue';
// import { useRoute } from 'vue-router'; // Uncomment if you need route-based logic for sidebar

// const route = useRoute(); // Uncomment for route-based logic

// Determine if the sidebar should be shown.
// For now, it's always shown. You might want to hide it on login pages, etc.
const showSidebar = computed(() => {
  // Example: return route.meta.requiresAuth; // if you have route meta fields
  return true; // Always show for this example
});

</script>

<style>
/* Global styles for html, body to ensure proper layout */
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; /* Consistent font */
  background-color: #f9fbfd; /* Background for the area outside content if any */
  overflow-x: hidden; /* Prevent horizontal scroll on body */
}

#app-layout {
  display: flex; /* Enables flexbox layout */
  height: 100vh; /* Full viewport height for the layout container */
}

.main-content-area {
  flex-grow: 1; /* Takes up remaining space */
  height: 100vh; /* Full height for the content area */
  overflow-y: auto; /* Allows main content to scroll independently */
  /*
    Padding within the main content area where ProjectListPage and others will render.
    This gives some breathing room around your page content.
    The ProjectListPage.vue itself then also has internal padding.
  */
  /* padding: 20px 25px; -- REMOVED: Let ProjectListPage handle its own top/side padding. */
  position: relative; /* For potential absolute positioned elements within */
  background-color: #f9fbfd; /* Matches ProjectListPage background */
}

.main-content-area.with-sidebar {
  margin-left: 260px; /* Same as sidebar width - this pushes the content to the right */
  /* Alternatively, use padding-left if you prefer content to flow under fixed sidebar
     but margin-left is often simpler for distinct scrolling areas.
  */
}

/*
  Your ProjectListPage.vue styles will now apply *within* this .main-content-area.
  The .project-list-page-content in ProjectListPage.vue should be fine as is,
  but ensure its width is 100% of its parent (.main-content-area) and it handles its own internal padding.
*/
</style>