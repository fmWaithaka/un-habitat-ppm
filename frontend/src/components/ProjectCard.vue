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
      <p class="project-excel-id">ID: {{ project.project_id_excel || 'N/A' }}</p>
      </div>

    <div class="card-footer">
      <router-link :to="{ name: 'ProjectEdit', params: { id: project.id } }" class="edit-button">Edit</router-link>

      <div class="action-buttons"> <router-link :to="{ name: 'ProjectDetails', params: { id: project.id } }" class="details-button">View Details</router-link>
        <button @click="emit('delete', project.id)" class="delete-button">Delete</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
// Import defineEmits to declare custom events
import { defineProps, defineEmits } from 'vue';
import { useRouter } from 'vue-router'; // Import useRouter for View/Edit links

// Define the props that this component accepts (remains the same)
const props = defineProps({
  project: {
    type: Object, // Expecting a project object from the parent component
    required: true, // The project prop is mandatory
  },
});

// Define the custom events that this component can emit
const emit = defineEmits(['delete']); // Declare the 'delete' event

// Get the router instance for navigation links
const router = useRouter();


// Computed property for status badge class (remains the same)
const statusClass = computed(() => {
  if (!props.project.status) return 'status-unknown';
  const status = props.project.status.toLowerCase().replace(/\s+/g, '-');
  return `status-${status}`;
});

// Removed the truncatedDescription computed property as description is removed
// const truncatedDescription = computed(() => { ... });


// The variables and functions declared in <script setup> are automatically exposed to the template.
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
  /* Removed cursor: pointer; from the card itself */
  border: 1px solid var(--color-border); /* Add a subtle border */
  height: 100%; /* Ensure cards in a grid have equal height */
}

.project-card:hover {
  transform: translateY(-5px); /* Lift the card slightly on hover */
  box-shadow: var(--shadow-lg); /* Increase shadow on hover */
}

.card-header {
  display: flex; /* Use flexbox */
  justify-content: space-between; /* Space out title and the status badge */
  align-items: flex-start; /* Align items to the top */
  margin-bottom: 15px; /* Space below the header */
  flex-wrap: wrap; /* Allow items to wrap on smaller screens */
}

/* Removed .header-meta style */

.project-title {
  font-size: 1.3em;
  font-weight: 600;
  color: var(--color-text-heading); /* Use heading text color */
  margin: 0;
  line-height: 1.3;
  flex-grow: 1; /* Allow title to take available space */
  margin-right: 10px; /* Space between title and status badge */
  /* Ensure title doesn't take up all space if status is long */
  min-width: 0; /* Allow flex item to shrink below content size */
}

.status-badge {
  padding: 5px 10px;
  border-radius: var(--border-radius-sm); /* Small rounded corners */
  font-size: 0.8em;
  font-weight: 500;
  text-transform: uppercase;
  white-space: nowrap; /* Prevent the badge text from wrapping */
  flex-shrink: 0; /* Prevent the badge from shrinking */
  /* Removed margin-bottom as it's not stacked vertically in header anymore */
}

/* Removed .project-id-header style */


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
  /* Added flex properties to stack country and excel ID */
  display: flex;
  flex-direction: column;
  gap: 8px; /* Space between country and excel ID */
}

.project-country {
  font-size: 0.95em;
  color: var(--color-text-secondary); /* Use secondary text color */
  /* Removed margin-bottom: 10px; as gap handles spacing */
  display: flex; /* Use flexbox to align icon and text */
  align-items: center; /* Vertically align icon and text */
}
.project-country svg {
  margin-right: 6px; /* Space between icon and text */
  color: var(--color-primary); /* Use primary color for the icon */
  flex-shrink: 0; /* Prevent icon from shrinking */
}

/* Style for the Project ID displayed in the body */
.project-excel-id {
  font-size: 0.9em; /* Match description font size */
  color: var(--color-text-primary); /* Use primary text color */
  font-style: italic;
  margin: 0; /* Remove default paragraph margin */
}


/* Removed .project-description style */


.card-footer {
  display: flex; /* Use flexbox for layout */
  justify-content: space-between; /* Space out Edit button and action-buttons container */
  align-items: center; /* Vertically align items */
  font-size: 0.85em;
  color: var(--color-text-secondary); /* Use secondary text color */
  padding-top: 10px;
  border-top: 1px solid var(--color-border-light); /* Add a light border at the top of the footer */
}

/* Container for View Details and Delete buttons */
.action-buttons {
    display: flex;
    align-items: center;
    gap: 10px; /* Space between buttons */
}


/* Style for the View Details button (now a router-link styled as a button) */
.details-button {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
  border: 1px solid var(--color-primary-light);
  padding: 6px 12px;
  border-radius: var(--border-radius-md);
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s, color 0.2s, border-color 0.2s;
  text-decoration: none; /* Remove underline from router-link */
  display: inline-block; /* Ensure padding/border apply correctly */
}

.details-button:hover {
  background-color: var(--color-primary);
  color: var(--color-text-light);
  border-color: var(--color-primary);
}

/* Style for the Delete button */
.delete-button {
  background-color: var(--color-background-error); /* Error color background */
  color: var(--color-text-error); /* Error text color */
  border: 1px solid var(--color-border-error); /* Error border color */
  padding: 6px 12px;
  border-radius: var(--border-radius-md);
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s, color 0.2s, border-color 0.2s;
}

.delete-button:hover {
  background-color: var(--color-text-error); /* Use text color for hover background */
  color: var(--color-background-error); /* Use background color for hover text */
  border-color: var(--color-text-error);
}

/* Style for the Edit button */
.edit-button {
    background-color: var(--color-background-mute);
    color: var(--color-text-primary);
    border: 1px solid var(--color-border);
    padding: 6px 12px;
    border-radius: var(--border-radius-md);
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s ease, border-color 0.2s ease;
    text-decoration: none; /* Remove underline from router-link */
    display: inline-block; /* Ensure padding/border apply correctly */
}

.edit-button:hover {
    background-color: var(--color-border);
    border-color: var(--color-text-secondary);
}
</style>
