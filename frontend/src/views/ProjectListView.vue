<script setup>
import { ref, onMounted } from 'vue';
import ProjectCard from '../components/ProjectCard.vue';
// Import the deleteProject function along with getProjects
import { getProjects, deleteProject } from '../services/projectService'; // <-- Import deleteProject

const projects = ref([]);
const loading = ref(true);
const error = ref(null);

// Function to fetch projects from the API (already exists)
async function fetchProjectsData() {
  loading.value = true;
  error.value = null;
  try {
    const response = await getProjects();
    projects.value = response.data;
    console.log('Projects fetched successfully:', projects.value);
  } catch (err) {
    console.error('Error fetching projects:', err);
    if (err.response) {
      error.value = `Error ${err.response.status}: ${err.response.data.detail || err.message || 'Failed to load projects.'}`;
    } else if (err.request) {
      error.value = 'Failed to load projects. No response from server.';
    } else {
      error.value = `Failed to load projects: ${err.message}`;
    }
  } finally {
    loading.value = false;
  }
}

// --- Function to handle project deletion ---
async function handleDeleteProject(projectId) {
  // Optional: Add a confirmation dialog
  if (confirm('Are you sure you want to delete this project?')) {
    try {
      // Call the deleteProject service function
      await deleteProject(projectId);

      // If deletion is successful, update the projects list
      // Option 1: Re-fetch the entire list (simpler, but less efficient for large lists)
      // fetchProjectsData();

      // Option 2: Remove the deleted project from the local list (more efficient)
      projects.value = projects.value.filter(project => project.id !== projectId);
      console.log(`Project with ID ${projectId} deleted successfully.`);

    } catch (err) {
      console.error(`Error deleting project with ID ${projectId}:`, err);
      // Display an error message to the user (you might need a separate error notification system)
      alert(`Failed to delete project: ${err.message || 'An error occurred.'}`);
    }
  }
}

onMounted(fetchProjectsData);

// Expose the handleDeleteProject function to the template
// With <script setup>, top-level declarations are automatically exposed,
// but explicitly listing can be good for clarity or if not using <script setup>
// export { projects, loading, error, fetchProjectsData, handleDeleteProject }; // Not needed with setup

</script>

<template>
  <div class="project-list-view">
    <div v-if="!loading && !error && projects.length > 0" class="project-grid">
      <ProjectCard
        v-for="project in projects"
        :key="project.id"
        :project="project"
        @delete="handleDeleteProject" /> </div>
     </div>
</template>
<style scoped>
/* Scoped styles specific to ProjectListView.vue */

.project-list-view {
  padding: 20px;
  width: 100%; /* Explicitly set width to 100% of its parent (.main-content) */
  margin: 0; /* Explicitly remove any margin */
  color: var(--color-text-primary); /* Ensure text color is set */
  box-sizing: border-box; /* Include padding in the element's total width */
  /* Optional: Add a temporary border to visualize this element's boundaries */
  /* border: 2px dashed red; */
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
  max-width: 1900px; /* Limit paragraph width for readability */
  margin: 0 auto; /* Center the paragraph */
}

/* Styles for the project grid container */
.project-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 25px;
  /* Ensure it doesn't have its own max-width or fixed width */
  width: 100%; /* Explicitly set grid width to 100% of its parent (.project-list-view) */
  box-sizing: border-box; /* Include padding/border in width if added */
}

/* Styling for Loading, Error, and No Projects states */
.loading-indicator,
.error-message,
.no-projects-message {
  display: flex;
  flex-direction: column; /* Stack content vertically */
  align-items: center; /* Center content horizontally */
  justify-content: center; /* Center content vertically */
  padding: 50px 20px;
  text-align: center;
  min-height: 300px; /* Ensure these blocks take up a minimum height */
  border-radius: var(--border-radius-lg); /* Rounded corners */
  background-color: var(--color-background-content); /* Use content background color */
  box-shadow: var(--shadow-sm); /* Add a subtle shadow */
  color: var(--color-text-primary); /* Default text color */
}

.error-message {
  background-color: var(--color-background-error); /* Error specific background */
  color: var(--color-text-error); /* Error specific text color */
  border: 1px solid var(--color-border-error); /* Error specific border */
}

.error-message p {
  margin-bottom: 10px;
}

.retry-button {
  background-color: var(--color-primary); /* Primary color background */
  color: var(--color-text-light); /* Light text color */
  border: none;
  padding: 10px 20px;
  border-radius: var(--border-radius-md); /* Rounded corners */
  cursor: pointer; /* Indicate clickable */
  font-weight: 500;
  transition: background-color 0.2s ease; /* Smooth transition on hover */
  margin-top: 15px;
}

.retry-button:hover {
  background-color: var(--color-primary-dark); /* Darker primary on hover */
}

/* Simple Spinner Animation */
.spinner {
  border: 4px solid var(--color-background-mute); /* Light grey border */
  border-top: 4px solid var(--color-primary); /* Primary color for the spinning part */
  border-radius: 50%; /* Make it round */
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite; /* Apply the spin animation */
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); } /* Start rotation */
  100% { transform: rotate(360deg); } /* End rotation (one full turn) */
}
</style>
