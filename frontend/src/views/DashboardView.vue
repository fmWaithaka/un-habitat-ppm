<template>
  <div class="dashboard-view">
    <header class="view-header">
      <h1>Dashboard</h1>
      <p>Key project insights and visualizations.</p>
    </header>

    <div class="dashboard-content">
      <p>Dashboard content will be implemented here in a future phase.</p>
      <p>This will include various charts and metrics for project analysis.</p>
      </div>
  </div>
</template>

<script setup>
// No specific script logic is needed for this placeholder dashboard view yet.
// Data fetching and visualization logic will be added in a future phase.
</script>

<style scoped>
/* Scoped styles specific to DashboardView.vue */

.dashboard-view {
  padding: 20px;
  width: 100%; /* Explicitly set width to 100% of its parent (.main-content) */
  margin: 0; /* Explicitly remove any margin */
  color: var(--color-text-primary); /* Ensure text color is set */
  box-sizing: border-box; /* Include padding in the element's total width */
  /* Optional: Add a temporary border to visualize this element's boundaries */
  /* border: 2px dashed blue; */
}

.view-header {
  text-align: center; /* Center the header text */
  margin-bottom: 40px; /* Space below the header */
  color: var(--color-text-primary); /* Use primary text color from global variables */
}

.view-header h1 {
  font-size: 2.8em;
  font-weight: 300; /* Lighter weight for a modern heading */
  color: var(--color-primary); /* Use the primary color for the main heading */
  margin-bottom: 10px;
}

.view-header p {
  font-size: 1.2em;
  color: var(--color-text-secondary); /* Use secondary text color */
  max-width: 1200px; /* Limit paragraph width for readability */
  margin: 0 auto; /* Center the paragraph */
}

/* Ensure the content container inside the dashboard doesn't have constraints */
.dashboard-content {
  background-color: var(--color-background-content);
  padding: 30px;
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-sm);
  text-align: center;
  color: var(--color-text-secondary);
  font-size: 1.1em;
  width: 100%; /* Explicitly set content width to 100% of its parent (.dashboard-view) */
  box-sizing: border-box; /* Include padding/border in width */
  /* Ensure it doesn't have its own max-width or fixed width */
}


.dashboard-content p {
    margin-bottom: 15px;
}

/* Placeholder for chart grid styling if you add charts later */
/*
.chart-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 30px;
}

.chart-container {
  background-color: var(--color-background-mute);
  padding: 20px;
  border-radius: var(--border-radius-md);
  border: 1px solid var(--color-border);
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-primary);
}
*/
</style>
