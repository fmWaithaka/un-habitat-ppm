<template>
  <div class="project-create-view">
    <header class="view-header">
      <h1>Create New Project</h1>
      <p>Fill in the details below to add a new project to the portfolio.</p>
    </header>

    <div class="create-form-container">
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
            <option value="" disabled>Select Status</option> <option v-for="statusChoice in statusChoices" :value="statusChoice.key" :key="statusChoice.key">
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
              <option :value="null">Select Country</option> <option v-for="country in countryOptions" :value="country" :key="country.id">
                 {{ country.name }}
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
            {{ isSubmitting ? 'Creating...' : 'Create Project' }}
          </button>
          <button type="button" @click="handleCancel">Cancel</button>
        </div>

        <div v-if="submissionError" class="error-message">
          <p><strong>Error submitting form:</strong></p>
          <p>{{ submissionError }}</p>
           </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'; // Import onMounted
import { useRouter } from 'vue-router';
import { createProject } from '../services/projectService'; // Import createProject function
// TODO: Import service function to fetch Countries
// import { getCountries } from '../services/yourOtherServiceFile'; // Example

const router = useRouter();

// Reactive variable to hold form data
const formData = ref({
  title: '',
  project_id_excel: '',
  paas_code: '',
  status: '', // Initialize status as empty string to match default option value
  fund: '',
  country: null, // Initialize ForeignKey field as null (will hold Country object)
  lead_org_unit: '', // Changed to empty string for text input
  themes: '', // Changed to empty string for text input (assuming comma-separated names)
  donors: '', // Changed to empty string for text input (assuming comma-separated names)
  approval_date: '', // Date inputs work best with empty string or null
  start_date: '',
  end_date: '',
  budget_amount: null, // Initialize monetary fields as null or 0
  pag_value: null,
  total_expenditure: null,
  total_contribution: null,
  total_contribution_expenditure_diff: null,
  total_psc: null,
});

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


// TODO: Function to fetch options for Country dropdown from the backend
async function fetchDropdownOptions() {
  try {
    // Example: Fetch countries
    // const countriesResponse = await getCountries();
    // countryOptions.value = countriesResponse.data;
    console.log("TODO: Fetch Country dropdown options");

    // Simulate fetching data for now
    countryOptions.value = [{id: 1, name: 'Kenya'}, {id: 2, name: 'Uganda'}, {id: 3, name: 'Ethiopia'}]; // Simulated data


  } catch (err) {
    console.error('Error fetching dropdown options:', err);
    // You might want to set an error state or show a message
  }
}

// Fetch dropdown options when the component is mounted
onMounted(() => {
  fetchDropdownOptions();
});


// Function to handle form submission
async function handleSubmit() {
  isSubmitting.value = true;
  submissionError.value = null;

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
       // For ForeignKey 'country', if an object is selected, send its ID. If null, send null.
       country: formData.value.country ? formData.value.country.id : null,
       // For text inputs, send the string value directly
       lead_org_unit: formData.value.lead_org_unit || null, // Send null if empty string
       themes: formData.value.themes || null, // Send null if empty string
       donors: formData.value.donors || null, // Send null if empty string
       // Ensure date fields are in the correct format (YYYY-MM-DD) if not already
       // Date inputs with v-model usually handle this, but confirm format if needed
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
    };

    console.log("Submitting data:", dataToSubmit); // Log data before submitting

    // Call the createProject service function
    const response = await createProject(dataToSubmit);

    console.log('Project created successfully:', response.data);

    // Redirect to the new project's detail page or the project list
    router.push({ name: 'ProjectDetails', params: { id: response.data.id } });
    // Or redirect to the list: router.push({ name: 'Projects' });

  } catch (err) {
    console.error('Error creating project:', err);
    // Handle and display errors from the backend (e.g., validation errors)
     if (err.response && err.response.data) {
        // DRF often returns validation errors in err.response.data
        submissionError.value = 'Failed to create project. Please check the form data.';
        // You could parse err.response.data to show specific field errors
        console.error("Backend validation errors:", err.response.data);
     } else {
        submissionError.value = `Failed to create project: ${err.message || 'An unknown error occurred.'}`;
     }
  } finally {
    isSubmitting.value = false; // Re-enable the submit button
  }
}

// Function to handle cancel button click
function handleCancel() {
  // Navigate back to the previous page or the project list
  router.back(); // Go back in history
  // Or navigate to the list: router.push({ name: 'Projects' });
}

// Variables and functions declared in <script setup> are automatically exposed to the template.
</script>

<style scoped>
/* Scoped styles specific to ProjectCreateView.vue */
.project-create-view {
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

.create-form-container {
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
  /* Ensure text is visible in dark mode */
  color: var(--color-text-primary); /* Use primary text color */
  background-color: var(--color-background-body); /* Use body background for input fill */
  box-sizing: border-box;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

/* Style for select options to ensure visibility in dark mode */
/* This rule uses global CSS variables which should adapt based on theme */
.form-group select option {
    color: var(--color-text-primary); /* Use primary text color for options */
    background-color: var(--color-background-content); /* Use content background for option background */
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
</style>
