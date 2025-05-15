<template>
  <!-- Main app container -->
  <div id="app">
    <!-- Router view will render your ProjectListPage when at root path -->
    <router-view />
  </div>
</template>

<script setup>
// Basic App.vue typically doesn't need much logic
// Routing is handled through Vue Router configuration
</script>

<style>
/* Global styles (optional) */
#app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}
</style>