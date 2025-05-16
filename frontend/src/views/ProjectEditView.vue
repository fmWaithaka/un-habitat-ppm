<template>
  <div class="edit-project-page">
    <div class="page-header">
      <h1 class="page-title">{{ isNewProject ? 'Create New Project' : `Edit Project: ${formData.title || 'Loading...'}` }}</h1>
      <router-link to="/" class="btn btn-secondary">Cancel</router-link>
    </div>

    <div v-if="loadingInitialData" class="loading-state">Loading project data...</div>
    <div v-if="initialDataError" class="error-state">
      <p>Error loading project data: {{ initialDataError.message || 'Unknown error' }}</p>
      <button @click="fetchProjectData" class="btn">Try Again</button>
    </div>

    <form @submit.prevent="handleSubmit" v-if="!loadingInitialData && !initialDataError">
      <div class="form-section">
        <h3>Basic Information</h3>
        <div class="form-group">
          <label for="title">Project Title <span class="required">*</span></label>
          <input type="text" id="title" v-model="formData.title" required />
          <span v-if="formErrors.title" class="error-message">{{ formErrors.title && formErrors.title[0] }}</span>
        </div>

        <div class="form-group">
          <label for="project_id_excel">Project ID</label>
          <input type="text" id="project_id_excel" v-model="formData.project_id_excel" />
           <span v-if="formErrors.project_id_excel" class="error-message">{{ formErrors.project_id_excel && formErrors.project_id_excel[0] }}</span>
        </div>

        <div class="form-group">
          <label for="paas_code">PAAS Code</label>
          <input type="text" id="paas_code" v-model="formData.paas_code" />
           <span v-if="formErrors.paas_code" class="error-message">{{ formErrors.paas_code && formErrors.paas_code[0] }}</span>
        </div>

        <div class="form-group">
          <label for="status">Status <span class="required">*</span></label>
          <select id="status" v-model="formData.status" required>
            <option value="" disabled selected>Select Status</option>
            <option value="Pending Approval">Pending Approval</option>
            <option value="Approved">Approved</option>
            <option value="Completed">Completed</option>
            <option value="Cancelled">Cancelled</option>
          </select>
           <span v-if="formErrors.status" class="error-message">{{ formErrors.status && formErrors.status[0] }}</span>
        </div>

         <div class="form-group">
          <label for="fund">Fund</label>
          <input type="text" id="fund" v-model="formData.fund" />
           <span v-if="formErrors.fund" class="error-message">{{ formErrors.fund && formErrors.fund[0] }}</span>
        </div>

         <div class="form-group">
          <label for="country_name_input">Country <span class="required">*</span></label>
          <select id="country_name_input" v-model="formData.country_name_input" required>
            <option value="" disabled selected>Select Country</option>
            <option v-for="country in countries" :key="country.id" :value="country.name">{{ country.name }}</option>
          </select>
           <span v-if="formErrors.country_name_input" class="error-message">{{ formErrors.country_name_input && formErrors.country_name_input[0] }}</span>
        </div>

         <div class="form-group">
          <label for="lead_org_unit_name_input">Lead Organization Unit</label>
          <input type="text" id="lead_org_unit_name_input" v-model="formData.lead_org_unit_name_input" placeholder="Enter Lead Org Unit name"/>
           <span v-if="formErrors.lead_org_unit_name_input" class="error-message">{{ formErrors.lead_org_unit_name_input && formErrors.lead_org_unit_name_input[0] }}</span>
        </div>
      </div>

      <div class="form-section">
        <h3>Financial Details</h3>
         <div class="form-group">
          <label for="budget_amount">Budget Amount</label>
          <input type="number" id="budget_amount" v-model.number="formData.budget_amount" step="0.01" />
           <span v-if="formErrors.budget_amount" class="error-message">{{ formErrors.budget_amount && formErrors.budget_amount[0] }}</span>
        </div>
         <div class="form-group">
          <label for="pag_value">PAG Value</label>
          <input type="number" id="pag_value" v-model.number="formData.pag_value" step="0.01" />
           <span v-if="formErrors.pag_value" class="error-message">{{ formErrors.pag_value && formErrors.pag_value[0] }}</span>
        </div>
         <div class="form-group">
          <label for="total_expenditure">Total Expenditure</label>
          <input type="number" id="total_expenditure" v-model.number="formData.total_expenditure" step="0.01" />
           <span v-if="formErrors.total_expenditure" class="error-message">{{ formErrors.total_expenditure && formErrors.total_expenditure[0] }}</span>
        </div>
         <div class="form-group">
          <label for="total_contribution">Total Contribution</label>
          <input type="number" id="total_contribution" v-model.number="formData.total_contribution" step="0.01" />
           <span v-if="formErrors.total_contribution" class="error-message">{{ formErrors.total_contribution && formErrors.total_contribution[0] }}</span>
        </div>
         <div class="form-group">
          <label for="total_psc">Total PSC</label>
          <input type="number" id="total_psc" v-model.number="formData.total_psc" step="0.01" />
           <span v-if="formErrors.total_psc" class="error-message">{{ formErrors.total_psc && formErrors.total_psc[0] }}</span>
        </div>
      </div>

       <div class="form-section">
        <h3>Dates</h3>
         <div class="form-group">
          <label for="start_date">Start Date</label>
          <input type="date" id="start_date" v-model="formData.start_date" />
           <span v-if="formErrors.start_date" class="error-message">{{ formErrors.start_date && formErrors.start_date[0] }}</span>
        </div>
         <div class="form-group">
          <label for="end_date">End Date</label>
          <input type="date" id="end_date" v-model="formData.end_date" />
           <span v-if="formErrors.end_date" class="error-message">{{ formErrors.end_date && formErrors.end_date[0] }}</span>
        </div>
         <div class="form-group">
          <label for="approval_date">Approval Date</label>
          <input type="date" id="approval_date" v-model="formData.approval_date" />
           <span v-if="formErrors.approval_date" class="error-message">{{ formErrors.approval_date && formErrors.approval_date[0] }}</span>
        </div>
      </div>

       <div class="form-section">
        <h3>Relationships (Select or Enter Names)</h3>
         <div class="form-group">
          <label for="donors_select">Donors (select one or more)</label>
          <select id="donors_select" v-model="selectedDonors" multiple>
            <option v-for="donor in availableDonors" :key="donor.id" :value="donor.name">{{ donor.name }}</option>
          </select>
          <small>Hold Ctrl/Cmd to select multiple.</small>
          <span v-if="formErrors.donors_input" class="error-message">{{ formErrors.donors_input && formErrors.donors_input[0] }}</span>
        </div>
         <div class="form-group">
          <label for="themes_select">Themes (select one or more)</label>
          <select id="themes_select" v-model="selectedThemes" multiple>
            <option v-for="theme in availableThemes" :key="theme.id" :value="theme.name">{{ theme.name }}</option>
          </select>
          <small>Hold Ctrl/Cmd to select multiple.</small>
           <span v-if="formErrors.themes_input" class="error-message">{{ formErrors.themes_input && formErrors.themes_input[0] }}</span>
        </div>
      </div>

      <div class="form-actions">
        <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
          <span v-if="isSubmitting" class="spinner"></span>
          {{ isSubmitting ? 'Saving...' : 'Save Changes' }}
        </button>
        <router-link to="/" class="btn btn-secondary" :disabled="isSubmitting">Cancel</router-link>
      </div>

      <div v-if="submitError" class="error-state submit-error">
        <p>Error saving project: {{ submitError.message || 'Unknown error' }}</p>
        <p v-if="submitError.response && submitError.response.data">
          Server says: {{ formatBackendErrors(submitError.response.data) }}
        </p>
      </div>
      <div v-if="submitSuccess" class="success-state">
        <p>Project saved successfully!</p>
        <router-link :to="{ name: 'ProjectList' }" class="btn btn-secondary">View All Projects</router-link>
        </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'; // Import computed
import apiService from '@/services/api'; // Ensure this path is correct
import { useRouter, useRoute } from 'vue-router'; // Import useRoute

const router = useRouter();
const route = useRoute(); // Use useRoute to access route params

// Determine if we are creating or editing based on the route param
const isNewProject = computed(() => !route.params.id); // Check if id param exists

const initialFormData = {
  title: '',
  project_id_excel: '',
  paas_code: '',
  status: '',
  fund: '',
  pag_value: null,
  start_date: null,
  end_date: null,
  approval_date: null,
  budget_amount: null,
  total_expenditure: null,
  total_contribution: null,
  total_psc: null,
  // These will hold the string names for the backend
  country_name_input: '',
  lead_org_unit_name_input: '',
  // The actual `donors_input` and `themes_input` will be generated in handleSubmit
};
// Use a function to create a fresh copy of initialFormData
const getInitialFormData = () => ({ ...initialFormData });

const formData = ref(getInitialFormData());

// For multi-selects - these will hold arrays of selected *names*
const selectedDonors = ref([]);
const selectedThemes = ref([]);

// Data for dropdowns (only countries, themes, donors needed for selection by name)
const countries = ref([]);
const availableThemes = ref([]);
const availableDonors = ref([]);

const loadingInitialData = ref(true);
const initialDataError = ref(null);
const isSubmitting = ref(false);
const submitError = ref(null);
const submitSuccess = ref(false);
const formErrors = ref({});

// Fetch data needed for dropdowns AND existing project data if editing
const fetchProjectData = async () => {
  loadingInitialData.value = true;
  initialDataError.value = null;
  try {
    // Fetch necessary lookup data concurrently
    const [countriesResponse, themesResponse, donorsResponse] = await Promise.all([
      apiService.getCountries(),
      apiService.getThemes(),
      apiService.getDonors(),
    ]);
    countries.value = countriesResponse.data;
    availableThemes.value = themesResponse.data;
    availableDonors.value = donorsResponse.data;

    // If editing, fetch the existing project data
    if (!isNewProject.value) {
        const projectResponse = await apiService.getProjectById(route.params.id);
        const projectData = projectResponse.data;

        // Populate formData with existing project data
        // Map nested detail objects back to string inputs/selected arrays
        formData.value = {
            title: projectData.title || '',
            project_id_excel: projectData.project_id_excel || '',
            paas_code: projectData.paas_code || '',
            status: projectData.status || '',
            fund: projectData.fund || '',
            pag_value: projectData.pag_value, // Keep as number/null
            start_date: projectData.start_date, // Keep as date string/null
            end_date: projectData.end_date, // Keep as date string/null
            approval_date: projectData.approval_date, // Keep as date string/null
            budget_amount: projectData.budget_amount, // Keep as number/null
            total_expenditure: projectData.total_expenditure, // Keep as number/null
            total_contribution: projectData.total_contribution, // Keep as number/null
            total_psc: projectData.total_psc, // Keep as number/null
            // Map nested detail names back to string inputs
            country_name_input: projectData.country_detail ? projectData.country_detail.name : '',
            lead_org_unit_name_input: projectData.lead_org_unit_detail ? projectData.lead_org_unit_detail.name : '',
            // donors_input and themes_input are not directly populated, they are generated from selectedDonors/selectedThemes
        };

        // Populate selectedDonors and selectedThemes with names from fetched data
        selectedDonors.value = projectData.donors_detail ? projectData.donors_detail.map(d => d.name) : [];
        selectedThemes.value = projectData.themes_detail ? projectData.themes_detail.map(t => t.name) : [];

         console.log("Fetched project data for editing:", projectData);
         console.log("Populated formData:", formData.value);
         console.log("Populated selectedDonors:", selectedDonors.value);
         console.log("Populated selectedThemes:", selectedThemes.value);

    } else {
        // If creating a new project, initialize form with default values
        formData.value = getInitialFormData();
        selectedDonors.value = [];
        selectedThemes.value = [];
    }


  } catch (err) {
    console.error('Failed to fetch initial data or project data:', err);
    initialDataError.value = err;
  } finally {
    loadingInitialData.value = false;
  }
};

const formatBackendErrors = (errors) => {
  if (typeof errors === 'string') return errors;
  let errorMessages = [];
  for (const key in errors) {
    if (errors[key] && errors[key].length > 0) {
      // Capitalize the first letter of the field name for better readability
      const fieldName = key.charAt(0).toUpperCase() + key.slice(1).replace(/_input$/, '').replace(/_/g, ' ');
      errorMessages.push(`${fieldName}: ${errors[key].join(', ')}`);
    }
  }
  return errorMessages.join('; ');
};


const handleSubmit = async () => {
  isSubmitting.value = true;
  submitError.value = null;
  submitSuccess.value = false;
  formErrors.value = {};

  // Prepare data to send, ensuring numeric and date fields are null if empty
  // and M2M fields are comma-separated strings of names
  const dataToSend = {
    ...formData.value,
    // Ensure numeric fields are null if empty string or null
    pag_value: formData.value.pag_value === '' || formData.value.pag_value === null ? null : Number(formData.value.pag_value),
    budget_amount: formData.value.budget_amount === '' || formData.value.budget_amount === null ? null : Number(formData.value.budget_amount),
    total_contribution: formData.value.total_contribution === '' || formData.value.total_contribution === null ? null : Number(formData.value.total_contribution),
    total_expenditure: formData.value.total_expenditure === '' || formData.value.total_expenditure === null ? null : Number(formData.value.total_expenditure),
    total_psc: formData.value.total_psc === '' || formData.value.total_psc === null ? null : Number(formData.value.total_psc),

    // Ensure date fields are null if empty string
    start_date: formData.value.start_date === '' ? null : formData.value.start_date,
    end_date: formData.value.end_date === '' ? null : formData.value.end_date,
    approval_date: formData.value.approval_date === '' ? null : formData.value.approval_date,

    // String input fields are already in formData
    // country_name_input: formData.value.country_name_input, // Already in ...formData.value
    // lead_org_unit_name_input: formData.value.lead_org_unit_name_input, // Already in ...formData.value

    // Convert selected names arrays to comma-separated strings for backend input fields
    donors_input: selectedDonors.value.join(','),
    themes_input: selectedThemes.value.join(','),
  };

  // Optional: Log dataToSend to check its structure before sending
  console.log("Data to send:", dataToSend);


  try {
    let response;
    if (isNewProject.value) {
        // Create new project
        response = await apiService.createProject(dataToSend);
        console.log('Project created successfully:', response.data);
         // If creating, we might want to redirect to the edit page or list page
         // router.push({ name: 'ProjectList' }); // Example: Redirect to list after create
    } else {
        // Update existing project
        response = await apiService.updateProject(route.params.id, dataToSend);
        console.log('Project updated successfully:', response.data);
        // If updating, we might want to redirect to the detail page or list page
        // router.push({ name: 'ProjectDetail', params: { id: route.params.id } }); // Example: Redirect to detail after update
    }

    submitSuccess.value = true;


  } catch (err) {
    console.error(`Failed to ${isNewProject.value ? 'create' : 'save'} project:`, err);
    submitError.value = err;
    if (err.response && err.response.data) {
      formErrors.value = err.response.data;
    }
  } finally {
    isSubmitting.value = false;
  }
};

const resetForm = () => {
  formData.value = getInitialFormData();
  selectedDonors.value = [];
  selectedThemes.value = [];
  formErrors.value = {};
  submitError.value = null;
  // submitSuccess will be handled by resetFormAndPrepareNew if user clicks "Create Another"
};

const resetFormAndPrepareNew = () => {
    resetForm();
    submitSuccess.value = false; // Explicitly reset success message for new form
}


// Fetch initial data and project data (if editing) when the component mounts or route ID changes
onMounted(() => {
  fetchProjectData();
});

watch(() => route.params.id, (newId) => {
    // Only refetch if the component is already mounted and the ID changes
    if (newId !== undefined) { // Check for undefined to distinguish from initial mount
        fetchProjectData();
    }
});

</script>

<style scoped>
/* Basic styling for the form - adapt to your existing styles */
.edit-project-page {
  padding: 20px 25px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f9fbfd;
  min-height: 100vh;
  box-sizing: border-box;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.btn {
  padding: 10px 18px;
  font-size: 14px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s ease, box-shadow 0.2s ease;
  font-weight: 500;
  text-decoration: none;
  display: inline-block;
  text-align: center;
  margin-left: 10px; /* Add some space between buttons */
}
.btn:first-child {
    margin-left: 0;
}


.btn-primary {
  background-color: #007bff;
  color: white;
}
.btn-primary:hover:not(:disabled) {
  background-color: #0056b3;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}
.btn-secondary:hover:not(:disabled) {
  background-color: #5a6268;
}

.btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.loading-state, .error-state, .success-state {
  text-align: center;
  padding: 20px;
  margin-top: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}
.loading-state { background-color: #e9ecef; color: #495057; }
.error-state {
  border-left: 4px solid #dc3545;
  color: #721c24;
  background-color: #f8d7da;
}
.success-state {
  border-left: 4px solid #28a745;
  color: #155724;
  background-color: #d4edda;
}
.error-state .btn, .success-state .btn { /* Apply to buttons within states */
    margin-top: 15px;
}
.submit-error {
    margin-top: 20px;
}


form {
  background-color: #ffffff;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  margin-top: 20px;
}

.form-section {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px dashed #e0e0e0;
}
.form-section:last-child {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
}

.form-section h3 {
  font-size: 18px;
  color: #333;
  margin-top: 0;
  margin-bottom: 20px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.form-group {
  margin-bottom: 18px;
}

.form-group label {
  display: block;
  font-weight: 500;
  margin-bottom: 8px;
  color: #495057;
  font-size: 14px;
}

.form-group input[type="text"],
.form-group input[type="number"],
.form-group input[type="date"],
.form-group select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
  background-color: #fff; /* Ensure select background is white */
}

.form-group input[type="text"]:focus,
.form-group input[type="number"]:focus,
.form-group input[type="date"]:focus,
.form-group select:focus {
  outline: none;
  border-color: #80bdff;
  box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
}

.form-group select[multiple] {
    height: auto; /* Adjust height for multiple select */
    min-height: 100px;
}
.form-group small {
    display: block;
    margin-top: 4px;
    font-size: 0.85em;
    color: #6c757d;
}

.required {
  color: #dc3545;
  margin-left: 4px;
}

.error-message {
    color: #dc3545;
    font-size: 0.875em; /* Slightly smaller */
    margin-top: 5px;
    display: block;
}

.form-actions {
  margin-top: 30px;
  display: flex;
  gap: 15px;
  justify-content: flex-end;
}

.spinner {
  display: inline-block;
  width: 1em;
  height: 1em;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 1s ease-in-out infinite;
  margin-right: 8px; /* Increased margin */
  vertical-align: -0.125em; /* Align better with text */
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
