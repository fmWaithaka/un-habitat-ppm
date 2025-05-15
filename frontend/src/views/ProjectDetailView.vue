<template>
  <div class="project-detail-view">
    <div v-if="loading" class="loading-indicator">
      <div class="spinner"></div>
      <p>Loading project details...</p>
    </div>

    <div v-if="error" class="error-message">
      <p><strong>Oops! Could not load project details.</strong></p>
      <p>{{ error }}</p>
      <button @click="fetchProjectDetails" class="retry-button">Try Again</button>
    </div>

    <div v-if="!loading && !error && project">
      <header class="detail-header">
        <h1>{{ project.title || 'Untitled Project' }}</h1>
        <span :class="['status-badge', statusClass]">{{ project.status || 'Unknown' }}</span>
      </header>

      <div class="detail-section">
        <h2>Basic Information</h2>
        <p><strong>Project ID (Excel):</strong> {{ project.project_id_excel || 'N/A' }}</p>
        <p><strong>PAAS Code:</strong> {{ project.paas_code || 'N/A' }}</p>
        <p><strong>Description:</strong> {{ project.description || 'No description available.' }}</p>
      </div>

      <div class="detail-section">
        <h2>Organization & Location</h2>
        <p><strong>Country:</strong> {{ project.country ? project.country.name : 'N/A' }}</p>
        <p><strong>Lead Org Unit:</strong> {{ project.lead_org_unit ? project.lead_org_unit.name : 'N/A' }}</p>
      </div>

      <div class="detail-section">
        <h2>Dates</h2>
        <p><strong>Start Date:</strong> {{ formatDate(project.start_date) }}</p>
        <p><strong>End Date:</strong> {{ formatDate(project.end_date) }}</p>
        <p><strong>Approval Date:</strong> {{ formatDate(project.approval_date) }}</p>
      </div>

      <div class="detail-section">
        <h2>Financials</h2>
        <p><strong>Fund:</strong> {{ project.fund || 'N/A' }}</p>
        <p><strong>Budget Amount:</strong> {{ formatCurrency(project.budget_amount) }}</p>
        <p><strong>PAG Value:</strong> {{ formatCurrency(project.pag_value) }}</p>
        <p><strong>Total Expenditure:</strong> {{ formatCurrency(project.total_expenditure) }}</p>
        <p><strong>Total Contribution:</strong> {{ formatCurrency(project.total_contribution) }}</p>
        <p><strong>Total Contribution - Total Expenditure:</strong> {{ formatCurrency(project.total_contribution_expenditure_diff) }}</p>
        <p><strong>Total PSC:</strong> {{ formatCurrency(project.total_psc) }}</p>
      </div>

      <div class="detail-section">
        <h2>Categorization</h2>
        <p><strong>Themes:</strong> {{ formatNames(project.themes) }}</p>
        <p><strong>Donors:</strong> {{ formatNames(project.donors) }}</p>
      </div>

      <div class="detail-section">
        <h2>Audit Information</h2>
        <p><strong>Created At:</strong> {{ formatDateTime(project.created_at) }}</p>
        <p><strong>Updated At:</strong> {{ formatDateTime(project.updated_at) }}</p>
      </div>

      <div class="back-button-container">
        <button @click="goBack" class="back-button">Back to Projects List</button>
      </div>
    </div>

    <div v-if="!loading && !error && !project" class="no-projects-message">
      <p>Project not found.</p>
       <button @click="goBack" class="back-button">Back to Projects List</button>
    </div>


  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router'; // Import useRoute and useRouter
import { getProjectById } from '../services/projectService'; // Import the specific service function

// Use the route object to access route parameters (like the project ID)
const route = useRoute();
// Use the router object for navigation (e.g., going back)
const router = useRouter();

// Reactive variables for state management
const project = ref(null); // Stores the fetched project object
const loading = ref(true); // Indicates loading state
const error = ref(null);   // Stores error message

// Get the project ID from the route parameters
const projectId = route.params.id;

// Asynchronous function to fetch project details from the API
async function fetchProjectDetails() {
  loading.value = true;
  error.value = null;
  project.value = null; // Clear previous project data

  // Ensure projectId is available before fetching
  if (!projectId) {
     error.value = "Project ID is missing from the URL.";
     loading.value = false;
     return; // Stop execution if ID is missing
  }

  try {
    // Call the service function to fetch the project by ID
    const response = await getProjectById(projectId);
    project.value = response.data; // Assign the fetched project data
    console.log('Project details fetched:', project.value); // Log success (optional)
  } catch (err) {
    console.error('Error fetching project details:', err);
     if (err.response) {
      // Handle specific HTTP errors, e.g., 404 Not Found
      if (err.response.status === 404) {
         error.value = `Project with ID ${projectId} not found.`;
      } else {
         error.value = `Error ${err.response.status}: ${err.response.data.detail || err.message || 'Failed to load project details.'}`;
      }
    } else if (err.request) {
      error.value = 'Failed to load project details. No response from server.';
    } else {
      error.value = `Failed to load project details: ${err.message}`;
    }
  } finally {
    loading.value = false; // Set loading to false after fetch attempt
  }
}

// Lifecycle hook: Fetch details when the component is mounted
onMounted(() => {
  fetchProjectDetails();
});

// Computed property for status badge class (reused from ProjectCard)
const statusClass = computed(() => {
  if (!project.value || !project.value.status) return 'status-unknown';
  const status = project.value.status.toLowerCase().replace(/\s+/g, '-');
  return `status-${status}`;
});

// Helper function to format dates
function formatDate(dateString) {
  if (!dateString) return 'N/A';
  try {
    // Parse the date string (assuming YYYY-MM-DD from Django API)
    const date = new Date(dateString);
    // Format as needed, e.g., YYYY-MM-DD or more readable format
    // Using toLocaleDateString for user-friendly format
    return date.toLocaleDateString();
  } catch (e) {
    console.error('Error formatting date:', dateString, e);
    return dateString; // Return original string if formatting fails
  }
}

// Helper function to format datetime
function formatDateTime(dateTimeString) {
   if (!dateTimeString) return 'N/A';
   try {
      const date = new Date(dateTimeString);
      return date.toLocaleString(); // Format as local date and time
   } catch (e) {
      console.error('Error formatting datetime:', dateTimeString, e);
      return dateTimeString;
   }
}


// Helper function to format monetary values
function formatCurrency(amount) {
  if (amount === null || amount === undefined) return 'N/A';
  // Assuming USD for now, adjust currency and locale as needed
  try {
     // Convert string/number to number if necessary, then format
     const numberAmount = typeof amount === 'string' ? parseFloat(amount) : amount;
     if (isNaN(numberAmount)) return 'N/A';
     return numberAmount.toLocaleString('en-US', { style: 'currency', currency: 'USD' });
  } catch (e) {
     console.error('Error formatting currency:', amount, e);
     return amount; // Return original value if formatting fails
  }
}

// Helper function to format lists of names (Themes, Donors)
function formatNames(items) {
  if (!items || items.length === 0) return 'N/A';
  // Assuming items are objects with a 'name' property
  return items.map(item => item.name).join(', ');
}

// Function to navigate back to the projects list
function goBack() {
  router.push({ name: 'Projects' }); // Use the router to navigate back to the Projects route
}

// Variables and functions declared in <script setup> are automatically exposed to the template.
</script>

<style scoped>
/* Scoped styles specific to ProjectDetailView.vue */
.project-detail-view {
  padding: 20px;
  max-width: 900px; /* Slightly narrower max-width for readability of details */
  margin: 0 auto;
  color: var(--color-text-primary);
  background-color: var(--color-background-content); /* Use content background */
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-md);
}

.loading-indicator,
.error-message,
.no-projects-message {
  /* Inherit styles from ProjectListView for consistency */
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 50px 20px;
  text-align: center;
  min-height: 300px;
  border-radius: var(--border-radius-lg);
  background-color: var(--color-background-content);
  box-shadow: var(--shadow-sm);
  color: var(--color-text-primary);
}

.error-message {
  background-color: var(--color-background-error);
  color: var(--color-text-error);
  border: 1px solid var(--color-border-error);
}

.error-message p {
  margin-bottom: 10px;
}

.retry-button {
   /* Inherit styles from ProjectListView */
  background-color: var(--color-primary);
  color: var(--color-text-light);
  border: none;
  padding: 10px 20px;
  border-radius: var(--border-radius-md);
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s ease;
  margin-top: 15px;
}

.retry-button:hover {
  background-color: var(--color-primary-dark);
}

/* Spinner styles (copy from ProjectListView if not global) */
/* Assuming spinner styles are in global.css or copied here */


.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--color-border-light);
}

.detail-header h1 {
  font-size: 2em;
  font-weight: 600;
  color: var(--color-text-heading);
  margin: 0;
  line-height: 1.3;
  flex-grow: 1;
  margin-right: 20px;
}

/* Status badge styling (reused from ProjectCard) */
.status-badge {
  padding: 5px 10px;
  border-radius: var(--border-radius-sm);
  font-size: 0.9em; /* Slightly larger badge text than card */
  font-weight: 500;
  text-transform: uppercase;
  white-space: nowrap;
  flex-shrink: 0;
  align-self: center; /* Center vertically in header */
}

/* Status-specific colors (ensure these match global.css or ProjectCard.vue) */
.status-completed { background-color: var(--color-status-completed-bg); color: var(--color-status-completed-text); }
.status-in-progress { background-color: var(--color-status-inprogress-bg); color: var(--color-status-inprogress-text); }
.status-pending, .status-pending-approval { background-color: var(--color-status-pending-bg); color: var(--color-status-pending-text); }
.status-cancelled { background-color: var(--color-status-cancelled-bg); color: var(--color-status-cancelled-text); }
.status-on-hold { background-color: var(--color-status-onhold-bg); color: var(--color-status-onhold-text); }
.status-unknown { background-color: var(--color-background-mute); color: var(--color-text-secondary); }


.detail-section {
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 1px dashed var(--color-border-light); /* Dashed border for sections */
}

.detail-section:last-child {
    border-bottom: none; /* No border on the last section */
    margin-bottom: 0;
    padding-bottom: 0;
}

.detail-section h2 {
  font-size: 1.4em;
  font-weight: 600;
  color: var(--color-text-heading);
  margin-bottom: 15px;
}

.detail-section p {
  font-size: 1em;
  color: var(--color-text-primary);
  margin-bottom: 8px;
  line-height: 1.6;
}

.detail-section p strong {
    color: var(--color-text-secondary); /* Slightly different color for labels */
    font-weight: 600;
    margin-right: 5px;
}

.back-button-container {
    margin-top: 30px;
    text-align: center;
}

.back-button {
  background-color: var(--color-background-mute);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
  padding: 10px 20px;
  border-radius: var(--border-radius-md);
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s ease, border-color 0.2s ease;
}

.back-button:hover {
    background-color: var(--color-border);
    border-color: var(--color-text-secondary);
}

</style>
