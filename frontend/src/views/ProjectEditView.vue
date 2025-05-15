<template>
  <div class="project-edit-view">
    <header class="view-header">
      <h1>Edit Project</h1>
      <p>Modify the details below to update the project.</p>
    </header>

    <div v-if="loadingInitialData" class="loading-indicator">
      <div class="spinner"></div>
      <p>Loading project data...</p>
    </div>

    <div v-if="initialDataError" class="error-message">
      <p><strong>Oops! Could not load project data for editing.</strong></p>
      <p>{{ initialDataError }}</p>
       <button @click="fetchProjectData" class="retry-button">Try Again</button>
    </div>

    <div v-if="!loadingInitialData && !initialDataError && formData" class="edit-form-container">
      <form @submit.prevent="handleSubmit">

        <div class="form-group">
          <label for="title">Project Title:</label>
          <input type="text" id="title" v-model="formData.title" required>
        </div>

        <div class="form-group">
          <label for="project_id_excel">Project ID (Excel):</label>
          <input type="text" id="project_id_excel" v-model="formData.project_id_excel">
        </div>

        <div class="form-group">
          <label for="paas_code">PAAS Code:</label>
          <input type="text" id="paas_code" v-model="formData.paas_code">
        </div>

        <div class="form-group">
          <label for="status">Status:</label>
          <select id="status" v-model="formData.status" required>
            <option value="" disabled>Select Status</option>
            <option v-for="statusChoice in statusChoices" :value="statusChoice.key" :key="statusChoice.key">
              {{ statusChoice.label }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label for="fund">Fund:</label>
          <input type="text" id="fund" v-model="formData.fund">
        </div>

        <div class="form-group">
           <label for="country">Country:</label>
           <select id="country" v-model="formData.country">
              <option :value="null">Select Country</option>
              <option v-for="country in countryOptions" :value="country.id" :key="country.id"> {{ country.name }}
              </option>
           </select>
        </div>

         <div class="form-group">
           <label for="lead_org_unit">Lead Org Unit:</label>
           <input type="text" id="lead_org_unit" v-model="formData.lead_org_unit">
        </div>

        <div class="form-group">
           <label for="themes">Themes (comma-separated):</label>
           <input type="text" id="themes" v-model="formData.themes">
        </div>

         <div class="form-group">
           <label for="donors">Donors (comma-separated):</label>
           <input type="text" id="donors" v-model="formData.donors">
        </div>

        <div class="form-group">
           <label for="approval_date">Approval Date:</label>
           <input type="date" id="approval_date" v-model="formData.approval_date">
        </div>

        <div class="form-group">
           <label for="start_date">Start Date:</label>
           <input type="date" id="start_date" v-model="formData.start_date">
        </div>

        <div class="form-group">
           <label for="end_date">End Date:</label>
           <input type="date" id="end_date" v-model="formData.end_date">
        </div>

        <div class="form-group">
           <label for="budget_amount">Budget Amount:</label>
           <input type="number" id="budget_amount" v-model="formData.budget_amount" step="0.01">
        </div>
         <div class="form-group">
           <label for="pag_value">PAG Value:</label>
           <input type="number" id="pag_value" v-model="formData.pag_value" step="0.01">
        </div>
         <div class="form-group">
           <label for="total_expenditure">Total Expenditure:</label>
           <input type="number" id="total_expenditure" v-model="formData.total_expenditure" step="0.01">
        </div>
         <div class="form-group">
           <label for="total_contribution">Total Contribution:</label>
           <input type="number" id="total_contribution" v-model="formData.total_contribution" step="0.01">
        </div>
         <div class="form-group">
           <label for="total_contribution_expenditure_diff">Total Contribution - Total Expenditure:</label>
           <input type="number" id="total_contribution_expenditure_diff" v-model="formData.total_contribution_expenditure_diff" step="0.01">
        </div>
         <div class="form-group">
           <label for="total_psc">Total PSC:</label>
           <input type="number" id="total_psc" v-model="formData.total_psc" step="0.01">
        </div>

        <div class="form-actions">
          <button type="submit" :disabled="isSubmitting">
            {{ isSubmitting ? 'Updating...' : 'Update Project' }}
          </button>
          <button type="button" @click="handleCancel">Cancel</button>
        </div>

        <div v-if="submissionError" class="error-message">
          <p><strong>Error submitting form:</strong></p>
          <p>{{ submissionError }}</p>
           </div>
      </form>
    </div>

    <div v-if="!loadingInitialData && !initialDataError && !formData" class="no-project-found">
      <p>Project not found.</p>
       <button @click="handleCancel" class="back-button">Back to Projects List</button>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'; // Import onMounted and watch
import { useRoute, useRouter } from 'vue-router'; // Import useRoute and useRouter
// Import service functions for fetching project data and updating
import { getProjectById, updateProject } from '../services/projectService';
// TODO: Import service function to fetch Countries for dropdown
// import { getCountries } from '../services/yourOtherServiceFile'; // Example

const route = useRoute();
const router = useRouter();

// Get the project ID from the route parameters
const projectId = route.params.id;

// Reactive variable to hold form data (initially null or empty)
const formData = ref(null); // Initialize as null, will be populated after fetching

// States for fetching initial data
const loadingInitialData = ref(true);
const initialDataError = ref(null);

// States for form submission
const isSubmitting = ref(false);
const submissionError = ref(null);

// Reactive variable to hold options for Country dropdown
const countryOptions = ref([]);

// Hardcoded status choices based on your Django model
const statusChoices = ref([
  { key: 'Pending Approval', label: 'Pending Approval' },
  { key: 'Approved', label: 'Approved' },
  // Add other choices from your Django model if they exist
  // { key: 'Completed', label: 'Completed' },
  // { key: 'Cancelled', label: 'Cancelled' },
]);


// Function to fetch the existing project data
async function fetchProjectData() {
  loadingInitialData.value = true;
  initialDataError.value = null;
  formData.value = null; // Clear previous data

   // Ensure projectId is available before fetching
  if (!projectId) {
     initialDataError.value = "Project ID is missing from the URL.";
     loadingInitialData.value = false;
     return; // Stop execution if ID is missing
  }

  try {
    const response = await getProjectById(projectId);
    // Populate formData with fetched data
    // Need to map backend data format to form data structure
    formData.value = {
        ...response.data, // Spread most fields directly
        // For ForeignKey fields, the backend sends the nested object or null.
        // We need to bind the select to the ID for submission, but the initial value
        // might need to be the object or just the ID depending on how you bind.
        // Let's bind the select to the ID for simplicity in edit.
        country: response.data.country ? response.data.country.id : null, // Bind to country ID

        // For ManyToMany fields (Themes, Donors), backend sends array of objects.
        // We need to convert this back to a comma-separated string for text input.
        themes: response.data.themes ? response.data.themes.map(theme => theme.name).join(', ') : '',
        donors: response.data.donors ? response.data.donors.map(donor => donor.name).join(', ') : '',

        // Date fields might need formatting if backend sends different format
        // v-model="input type='date'" usually handles YYYY-MM-DD
        approval_date: response.data.approval_date || '',
        start_date: response.data.start_date || '',
        end_date: response.data.end_date || '',

        // Monetary fields might be strings from backend, ensure they work with number input
        // v-model="input type='number'" usually handles this, but confirm if issues arise
        budget_amount: response.data.budget_amount || null,
        pag_value: response.data.pag_value || null,
        total_expenditure: response.data.total_expenditure || null,
        total_contribution: response.data.total_contribution || null,
        total_contribution_expenditure_diff: response.data.total_contribution_expenditure_diff || null,
        total_psc: response.data.total_psc || null,

        // Ensure other fields like project_id_excel, paas_code, fund, title, status are mapped
        project_id_excel: response.data.project_id_excel || '',
        paas_code: response.data.paas_code || '',
        status: response.data.status || '', // Should match a key in statusChoices
        fund: response.data.fund || '',
        title: response.data.title || '',
        // description is already spread
    };


    console.log('Project data fetched for editing:', formData.value);

  } catch (err) {
    console.error(`Error fetching project with ID ${projectId} for editing:`, err);
     if (err.response) {
        if (err.response.status === 404) {
           initialDataError.value = `Project with ID ${projectId} not found.`;
        } else {
           initialDataError.value = `Error ${err.response.status}: ${err.response.data.detail || err.message || 'Failed to load project data.'}`;
        }
      } else if (err.request) {
        initialDataError.value = 'Failed to load project data. No response from server.';
      } else {
        initialDataError.value = `Failed to load project data: ${err.message}`;
      }
  } finally {
    loadingInitialData.value = false;
  }
}


// TODO: Function to fetch options for Country dropdown from the backend
async function fetchDropdownOptions() {
  try {
    // Example: Fetch countries
    // const countriesResponse = await getCountries();
    // countryOptions.value = countriesResponse.data;
    console.log("TODO: Fetch Country dropdown options for edit form");

    // Simulate fetching data for now
    countryOptions.value = [{id: 1, name: 'Kenya'}, {id: 2, name: 'Uganda'}, {id: 3, name: 'Ethiopia'}]; // Simulated data


  } catch (err) {
    console.error('Error fetching dropdown options:', err);
    // You might want to set an error state or show a message
  }
}


// Fetch initial project data and dropdown options when the component is mounted
onMounted(() => {
  fetchProjectData();
  fetchDropdownOptions();
});


// Function to handle form submission (Update)
async function handleSubmit() {
  isSubmitting.value = true;
  submissionError.value = null;

  // Ensure formData is loaded before submitting
  if (!formData.value) {
      submissionError.value = "Form data not loaded.";
      isSubmitting.value = false;
      return;
  }

  try {
    // Prepare data for submission - ensure correct format for backend API
    // For ForeignKey fields, send the ID (number) or null
    // For ManyToMany fields, send an array of IDs (numbers)
    // For text inputs (Lead Org Unit, Themes, Donors), send the string value.
    // NOTE: Your backend DRF serializer for Project will need to be updated
    // to handle receiving strings for lead_org_unit, themes, and donors,
    // and either find/create the related objects based on the string name(s),
    // or you'll need to add frontend logic to convert names to IDs before submitting.
    // Sending raw strings for ManyToMany fields like 'themes' and 'donors'
    // will likely cause validation errors on the backend unless the serializer is customized.

    const dataToSubmit = {
       ...formData.value, // Spread existing form data
       // For ForeignKey 'country', send the selected country ID or null
       country: formData.value.country, // formData.value.country is already the ID or null

       // For text inputs, send the string value directly
       lead_org_unit: formData.value.lead_org_unit || null, // Send null if empty string
       themes: formData.value.themes || null, // Send null if empty string
       donors: formData.value.donors || null, // Send null if empty string

       // Ensure date fields are in the correct format (YYYY-MM-DD)
       approval_date: formData.value.approval_date || null,
       start_date: formData.value.start_date || null,
       end_date: formData.value.end_date || null,

       // Ensure monetary fields are numbers or null
       budget_amount: formData.value.budget_amount || null,
       pag_value: formData.value.pag_value || null,
       total_expenditure: formData.value.total_expenditure || null,
       total_contribution: formData.value.total_contribution || null,
       total_contribution_expenditure_diff: formData.value.total_contribution_expenditure_diff || null,
       total_psc: formData.value.total_psc || null,

       // project_id_excel, paas_code, fund, title, status are already strings/numbers
       // Do NOT send auto-generated fields like id, created_at, updated_at in the update data
       id: undefined, // Explicitly exclude ID from the data payload
       created_at: undefined,
       updated_at: undefined,
    };

    console.log("Submitting updated data:", dataToSubmit); // Log data before submitting

    // Call the updateProject service function, passing the project ID and the data
    const response = await updateProject(projectId, dataToSubmit);

    console.log('Project updated successfully:', response.data);

    // Redirect to the updated project's detail page
    router.push({ name: 'ProjectDetails', params: { id: response.data.id } });

  } catch (err) {
    console.error(`Error updating project with ID ${projectId}:`, err);
    // Handle and display errors from the backend (e.g., validation errors)
     if (err.response && err.response.data) {
        // DRF often returns validation errors in err.response.data
        submissionError.value = 'Failed to update project. Please check the form data.';
        // You could parse err.response.data to show specific field errors
        console.error("Backend validation errors:", err.response.data);
     } else {
        submissionError.value = `Failed to update project: ${err.message || 'An unknown error occurred.'}`;
     }
  } finally {
    isSubmitting.value = false; // Re-enable the submit button
  }
}

// Function to handle cancel button click
function handleCancel() {
  // Navigate back to the previous page (likely the detail view or list)
  router.back(); // Go back in history
  // Or navigate explicitly: router.push({ name: 'ProjectDetails', params: { id: projectId } });
  // Or back to list: router.push({ name: 'Projects' });
}

// Variables and functions declared in <script setup> are automatically exposed to the template.
</script>

<style scoped>
/* Scoped styles specific to ProjectEditView.vue */
/* Reuse many styles from ProjectCreateView.vue for consistency */

.project-edit-view {
  padding: 20px;
  max-width: 800px; /* Limit form width for better usability */
  margin: 0 auto;
  color: var(--color-text-primary);
}

.view-header {
  text-align: center;
  margin-bottom: 40px;
  color: var(--color-text-primary);
}

.view-header h1 {
  font-size: 2.4em;
  font-weight: 600;
  color: var(--color-primary);
  margin-bottom: 10px;
}

.view-header p {
  font-size: 1.1em;
  color: var(--color-text-secondary);
}

.edit-form-container { /* Using a different class name but similar styles to create form */
  background-color: var(--color-background-content);
  padding: 30px;
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--color-border);
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: var(--color-text-heading);
  font-size: 0.95em;
}

.form-group input[type="text"],
.form-group input[type="date"],
.form-group input[type="number"],
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  font-size: 1em;
  color: var(--color-text-primary);
  background-color: var(--color-background-body);
  box-sizing: border-box;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.form-group select option {
    color: var(--color-text-primary);
    background-color: var(--color-background-content);
}


.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.form-group textarea {
  min-height: 120px;
  resize: vertical;
}

.form-actions {
  margin-top: 30px;
  text-align: right;
}

.form-actions button {
  padding: 10px 20px;
  border-radius: var(--border-radius-md);
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease, opacity 0.2s ease;
  margin-left: 15px;
}

.form-actions button[type="submit"] {
  background-color: var(--color-primary);
  color: var(--color-text-light);
  border: 1px solid var(--color-primary);
}

.form-actions button[type="submit"]:hover:not(:disabled) {
  background-color: var(--color-primary-dark);
  border-color: var(--color-primary-dark);
}

.form-actions button[type="submit"]:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-actions button[type="button"] {
  background-color: var(--color-background-mute);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

.form-actions button[type="button"]:hover:not(:disabled) {
  background-color: var(--color-border);
  border-color: var(--color-text-secondary);
}

.error-message {
  background-color: var(--color-background-error);
  color: var(--color-text-error);
  border: 1px solid var(--color-border-error);
  padding: 15px;
  border-radius: var(--border-radius-md);
  margin-top: 20px;
}

/* Styles for the "Project not found" message */
.no-project-found {
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

.no-project-found p {
    margin-bottom: 20px;
}

.back-button { /* Style for the back button in error/not found states */
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
