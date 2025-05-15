<template>
  <div class="project-card">
    <div class="card-header">
      <h3 class="project-title">{{ project.title || 'Untitled Project' }}</h3>
      <span :class="['status-badge', statusClass]">{{ project.status || 'Unknown' }}</span>
    </div>

    <div class="card-body">
      <p class="project-country">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
        {{ project.country ? project.country.name : 'N/A' }}
      </p>
      <p class="project-description">{{ truncatedDescription }}</p>
    </div>

    <div class="card-footer">
      <span class="project-id">ID: {{ project.id }}</span>
      <div class="action-buttons"> <router-link :to="{ name: 'ProjectDetails', params: { id: project.id } }" class="details-button">View Details</router-link>
        <button @click="emit('delete', project.id)" class="delete-button">Delete</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
// Import defineEmits to declare custom events
import { defineProps, defineEmits } from 'vue'; // <-- Import defineEmits
import { useRouter } from 'vue-router'; // Import useRouter for View/Edit links

// Define the props that this component accepts (remains the same)
const props = defineProps({
  project: {
    type: Object,
    required: true,
  },
});

// Define the custom events that this component can emit
const emit = defineEmits(['delete']); // <-- Declare the 'delete' event

// Get the router instance for navigation links
const router = useRouter();


// Computed property for status badge class (remains the same)
const statusClass = computed(() => {
  if (!props.project.status) return 'status-unknown';
  const status = props.project.status.toLowerCase().replace(/\s+/g, '-');
  return `status-${status}`;
});

// Computed property to truncate the project description (remains the same)
const truncatedDescription = computed(() => {
  const desc = props.project.description || "No description available.";
  const maxLength = 100;
  if (desc.length > maxLength) {
    return desc.substring(0, maxLength) + '...';
  }
  return desc;
});

// The variables and functions declared in <script setup> are automatically
// available to the <template>.
</script>

<style scoped>
/* Scoped styles specific to ProjectCard.vue */

.project-card {
  /* Use CSS variables for background, border, and shadows defined in global.css */
  background-color: var(--color-background-content);
  border-radius: var(--border-radius-lg); /* Large rounded corners */
  box-shadow: var(--shadow-md); /* Medium shadow */
  padding: 20px;
  display: flex;
  flex-direction: column; /* Stack content vertically */
  justify-content: space-between; /* Space out header, body, and footer */
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out; /* Smooth hover effects */
  cursor: pointer; /* Indicate that the card is clickable */
  border: 1px solid var(--color-border); /* Add a subtle border */
  height: 100%; /* Ensure cards in a grid have equal height */
}

.project-card:hover {
  transform: translateY(-5px); /* Lift the card slightly on hover */
  box-shadow: var(--shadow-lg); /* Increase shadow on hover */
}

.card-header {
  display: flex; /* Use flexbox to align title and status badge */
  justify-content: space-between; /* Space out title and badge */
  align-items: flex-start; /* Align items to the top */
  margin-bottom: 15px; /* Space below the header */
}

.project-title {
  font-size: 1.3em;
  font-weight: 600;
  color: var(--color-text-heading); /* Use heading text color */
  margin: 0;
  line-height: 1.3;
  flex-grow: 1; /* Allow title to take available space */
  margin-right: 10px; /* Space between title and badge */
}

.status-badge {
  padding: 5px 10px;
  border-radius: var(--border-radius-sm); /* Small rounded corners */
  font-size: 0.8em;
  font-weight: 500;
  text-transform: uppercase;
  white-space: nowrap; /* Prevent the badge text from wrapping */
  flex-shrink: 0; /* Prevent the badge from shrinking */
}

/* Status-specific background and text colors using CSS variables */
.status-completed { background-color: var(--color-status-completed-bg); color: var(--color-status-completed-text); }
.status-in-progress { background-color: var(--color-status-inprogress-bg); color: var(--color-status-inprogress-text); }
.status-pending, .status-pending-approval { background-color: var(--color-status-pending-bg); color: var(--color-status-pending-text); }
.status-cancelled { background-color: var(--color-status-cancelled-bg); color: var(--color-status-cancelled-text); }
.status-on-hold { background-color: var(--color-status-onhold-bg); color: var(--color-status-onhold-text); }
.status-unknown { background-color: var(--color-background-mute); color: var(--color-text-secondary); }


.card-body {
  margin-bottom: 15px; /* Space below the body */
  flex-grow: 1; /* Allows the body to expand and push the footer down */
}

.project-country {
  font-size: 0.95em;
  color: var(--color-text-secondary); /* Use secondary text color */
  margin-bottom: 10px;
  display: flex; /* Use flexbox to align icon and text */
  align-items: center; /* Vertically align icon and text */
}
.project-country svg {
  margin-right: 6px; /* Space between icon and text */
  color: var(--color-primary); /* Use primary color for the icon */
  flex-shrink: 0; /* Prevent icon from shrinking */
}

.project-description {
  font-size: 0.9em;
  color: var(--color-text-primary); /* Use primary text color */
  line-height: 1.5; /* Improve readability with line height */
  /* Optional: CSS for text clamping if you want to limit the number of lines */
  /*
  display: -webkit-box;
  -webkit-line-clamp: 3; // Limit to 3 lines
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  */
}

.card-footer {
  display: flex; /* Use flexbox for layout */
  justify-content: space-between; /* Space out project ID and button */
  align-items: center; /* Vertically align items */
  font-size: 0.85em;
  color: var(--color-text-secondary); /* Use secondary text color */
  padding-top: 10px;
  border-top: 1px solid var(--color-border-light); /* Add a light border at the top of the footer */
}

.project-id {
  font-style: italic;
}

.details-button {
  background-color: var(--color-primary-light); /* Light primary background */
  color: var(--color-primary); /* Primary text color */
  border: 1px solid var(--color-primary-light); /* Border matching background */
  padding: 6px 12px;
  border-radius: var(--border-radius-md); /* Medium rounded corners */
  font-weight: 500;
  cursor: pointer; /* Indicate clickable */
  transition: background-color 0.2s, color 0.2s, border-color 0.2s; /* Smooth transitions */
}

.details-button:hover {
  background-color: var(--color-primary); /* Primary background on hover */
  color: var(--color-text-light); /* Light text on hover */
  border-color: var(--color-primary); /* Primary border on hover */
}
</style>
