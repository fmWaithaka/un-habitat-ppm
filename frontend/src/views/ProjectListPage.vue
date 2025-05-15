<template>
  <div class="project-list-page">
    <div class="page-header">
      <h1 class="page-title">Projects</h1>
      <div class="actions-bar">
        <div class="search-filter">
          <input type="text" placeholder="Filter by country..." v-model="searchQuery" @input="applyFilter" />
          </div>
        <button class="btn btn-primary new-project-btn">
          <span class="plus-icon">+</span> New Project
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">Loading projects...</div>
    <div v-if="error" class="error-state">
      <p>Error loading projects: {{ error.message || 'Unknown error' }}</p>
      <p v-if="error.response && error.response.data">
        Server says: {{ JSON.stringify(error.response.data) }}
      </p>
      <button @click="fetchProjects" class="btn">Try Again</button>
    </div>

    <div v-if="!loading && !error && filteredProjects.length > 0" class="table-container">
      <table>
        <thead>
          <tr>
            <th class="checkbox-col"><input type="checkbox" @change="toggleSelectAll" :checked="allSelected" /></th>
            <th class="id-col">ID</th>
            <th class="title-col">Project Title</th>
            <th class="donors-col">Donor(s)</th>
            <th class="country-col">Country(ies)</th>
            <th class="status-col">Status</th>
            <th class="actions-col"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="project in filteredProjects" :key="project.id" @click="viewProjectDetails(project)" class="project-row">
            <td class="checkbox-col"><input type="checkbox" v-model="selectedProjects" :value="project.id" @click.stop /></td>
            <td class="id-col">{{ project.id }}</td>
            <td class="title-col">
              <div class="project-title-main">{{ project.title }}</div>
              <div class="project-title-sub">{{ project.project_id_excel || 'N/A' }}</div>
            </td>
            <td class="donors-col">
              <span v-if="project.donors && project.donors.length">
                {{ project.donors.map(donor => donor.name).join(', ') }}
              </span>
              <span v-else>N/A</span>
            </td>
            <td class="country-col">{{ project.country ? project.country.name : 'N/A' }}</td>
            <td class="status-col">
              <span :class="getStatusClass(project.status)" class="status-badge">
                {{ project.status }}
              </span>
            </td>
            <td class="actions-col">
              <button class="action-btn three-dots-btn" @click.stop="toggleProjectActions(project.id)">
                &#x22EE; </button>
              <div v-if="showActionsFor === project.id" class="actions-dropdown">
                <button @click.stop="editProject(project.id)">Edit</button>
                <button @click.stop="deleteSingleProject(project.id)" class="delete-action">Delete</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="!loading && !error && filteredProjects.length === 0" class="no-projects-found">
      <p v-if="projects.length === 0">No projects have been created yet.</p>
      <p v-else>No projects match your current filter.</p>
    </div>

     <div v-if="selectedProjects.length > 0 && !loading && !error" class="bulk-actions-footer">
        <button @click="deleteSelectedProjects" class="btn btn-danger">
            Delete Selected ({{ selectedProjects.length }})
        </button>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import apiService from '@/services/api'; // Corrected path based on your info
// import { useRouter } from 'vue-router'; // Uncomment if you use router.push for navigation

// const router = useRouter(); // Uncomment for navigation

const projects = ref([]);
const loading = ref(true);
const error = ref(null);
const searchQuery = ref('');
const selectedProjects = ref([]); // For checkboxes
const showActionsFor = ref(null); // To toggle individual project action dropdowns

const fetchProjects = async () => {
  loading.value = true;
  error.value = null;
  try {
    const response = await apiService.getProjects();
    // Assuming DRF pagination, actual data is in response.data.results
    // If not paginated, it might just be response.data
    projects.value = response.data.results || response.data || [];
    console.log('Fetched projects:', projects.value);
  } catch (err) {
    console.error('Failed to fetch projects:', err);
    error.value = err;
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchProjects();
});

const filteredProjects = computed(() => {
  if (!searchQuery.value) {
    return projects.value;
  }
  const lowerSearchQuery = searchQuery.value.toLowerCase();
  return projects.value.filter(project =>
    (project.country && project.country.name.toLowerCase().includes(lowerSearchQuery)) ||
    (project.title && project.title.toLowerCase().includes(lowerSearchQuery)) // Also filter by title for broader search
  );
});

// For the master checkbox in the header
const allSelected = computed({
  get: () => {
    return filteredProjects.value.length > 0 && selectedProjects.value.length === filteredProjects.value.length;
  },
  set: (value) => {
    if (value) {
      selectedProjects.value = filteredProjects.value.map(p => p.id);
    } else {
      selectedProjects.value = [];
    }
  }
});

const toggleSelectAll = (event) => {
  allSelected.value = event.target.checked;
};


const getStatusClass = (status) => {
  if (!status) return 'status-default';
  const lowerStatus = status.toLowerCase();
  if (lowerStatus === 'pending approval') return 'status-pending';
  if (lowerStatus === 'active' || lowerStatus === 'completed') return 'status-approved';
  if (lowerStatus === 'cancelled') return 'status-cancelled';
  return 'status-default'; // Fallback for any other statuses
};

const viewProjectDetails = (project) => {
  console.log('View details for project:', project.id);
  // router.push({ name: 'ProjectDetail', params: { id: project.id } }); // Example navigation
  alert(`Maps to details for project: ${project.title}`);
};

const toggleProjectActions = (projectId) => {
  if (showActionsFor.value === projectId) {
    showActionsFor.value = null; // Close if already open
  } else {
    showActionsFor.value = projectId; // Open for this project
  }
};

const editProject = (projectId) => {
  console.log('Edit project:', projectId);
  showActionsFor.value = null; // Close dropdown
  alert(`Edit project ID: ${projectId}`);
  // router.push({ name: 'EditProject', params: { id: projectId } });
};

const deleteSingleProject = async (projectId) => {
    if (!confirm(`Are you sure you want to delete project ID ${projectId}?`)) return;
    showActionsFor.value = null; // Close dropdown
    try {
        await apiService.deleteProject(projectId);
        projects.value = projects.value.filter(p => p.id !== projectId);
        selectedProjects.value = selectedProjects.value.filter(id => id !== projectId);
        alert(`Project ID ${projectId} deleted.`);
    } catch (err) {
        console.error(`Failed to delete project ${projectId}:`, err);
        alert(`Error deleting project: ${err.message}`);
    }
};

const deleteSelectedProjects = async () => {
    if (!selectedProjects.value.length) return;
    if (!confirm(`Are you sure you want to delete ${selectedProjects.value.length} selected project(s)?`)) return;

    // Show loading state for bulk delete, TBD
    try {
        // This should ideally be a single API call if your backend supports bulk delete
        // For now, deleting one by one:
        for (const projectId of selectedProjects.value) {
            await apiService.deleteProject(projectId);
        }
        alert(`${selectedProjects.value.length} project(s) deleted successfully.`);
        fetchProjects(); // Refresh the list
        selectedProjects.value = []; // Clear selection
    } catch (err) {
        console.error('Failed to delete selected projects:', err);
        alert(`Error deleting projects: ${err.message}`);
    }
};

// Watch for clicks outside the actions dropdown to close it
// This requires a bit more setup, typically by adding a global event listener.
// For simplicity, clicking another project's actions or the same button again closes it.

const applyFilter = () => {
  // The computed property `filteredProjects` handles the filtering automatically
  // This function is here if you wanted to add debouncing or other logic on input
  console.log("Filtering with query:", searchQuery.value)
};

</script>

<style scoped>
.project-list-page {
  padding: 20px 25px; /* Slightly more padding */
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; /* Modern font stack */
  background-color: #f9fbfd; /* Very light background for the page */
  min-height: calc(100vh - 40px); /* Full height minus padding */
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

.page-title {
  font-size: 28px; /* Larger title like in image */
  font-weight: 600;
  color: #333;
}

.actions-bar {
  display: flex;
  align-items: center;
  gap: 15px; /* Space between search and button */
}

.search-filter input {
  padding: 10px 15px;
  border: 1px solid #dde2e7;
  border-radius: 6px;
  min-width: 250px; /* Good width for search */
  font-size: 14px;
}
.search-filter input:focus {
  outline: none;
  border-color: #007bff; /* Highlight on focus */
  box-shadow: 0 0 0 2px rgba(0,123,255,.25);
}

.btn {
  padding: 10px 18px;
  font-size: 14px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s ease, box-shadow 0.2s ease;
  font-weight: 500;
}

.btn-primary {
  background-color: #007bff; /* Blue like in image */
  color: white;
  display: flex;
  align-items: center;
  gap: 8px; /* Space between icon and text */
}
.btn-primary:hover {
  background-color: #0056b3;
}
.btn-primary .plus-icon {
  font-size: 18px;
  font-weight: bold;
}
.btn-danger {
    background-color: #dc3545;
    color: white;
}
.btn-danger:hover {
    background-color: #c82333;
}


.loading-state, .error-state, .no-projects-found {
  text-align: center;
  padding: 40px 20px;
  margin-top: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  color: #555;
}
.error-state {
  border-left: 4px solid #dc3545; /* Red accent for error */
  color: #721c24;
  background-color: #f8d7da;
}
.error-state .btn {
    margin-top: 15px;
    background-color: #007bff;
    color: white;
}

.table-container {
  background-color: #ffffff;
  border-radius: 8px; /* Rounded corners for the table container */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08); /* Softer shadow */
  overflow-x: auto; /* Allow horizontal scrolling on small screens */
}

table {
  width: 100%;
  border-collapse: collapse; /* Clean look */
  font-size: 14px;
}

th, td {
  padding: 14px 18px; /* More padding for cells */
  text-align: left;
  border-bottom: 1px solid #e9ecef; /* Lighter border for rows */
  vertical-align: middle; /* Align content vertically */
}

thead th {
  background-color: #f8f9fa; /* Very light grey for header */
  color: #495057; /* Darker grey for header text */
  font-weight: 600; /* Bolder header text */
  text-transform: uppercase; /* Uppercase header text like image */
  font-size: 12px; /* Smaller font for header */
  letter-spacing: 0.5px;
}
thead th:first-child {
  border-top-left-radius: 8px;
}
thead th:last-child {
  border-top-right-radius: 8px;
}


.project-row {
  cursor: pointer;
  transition: background-color 0.15s ease-in-out;
}
.project-row:hover {
  background-color: #f1f5f9; /* Slight hover effect for rows */
}
.project-row:last-child td {
  border-bottom: none; /* No border for the last row's cells */
}


.checkbox-col { width: 40px; text-align: center; }
.id-col { width: 70px; color: #6c757d; } /* Greyish for ID */
.title-col { min-width: 200px; }
.project-title-main {
  font-weight: 500;
  color: #212529; /* Darker for main title */
  margin-bottom: 3px;
}
.project-title-sub {
  font-size: 0.85em;
  color: #6c757d; /* Greyish for sub-id */
}
.donors-col, .country-col { width: 15%; color: #495057; }
.status-col { width: 130px; } /* Fixed width for status */
.actions-col { width: 50px; text-align: center; position: relative; }


.status-badge {
  padding: 5px 10px;
  border-radius: 15px; /* Pill shape */
  font-size: 0.8em;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: inline-block; /* So it takes padding correctly */
  min-width: 100px; /* Ensure badges have a decent width */
  text-align: center;
}

.status-approved { /* Green */
  background-color: rgba(40, 167, 69, 0.1); /* Lighter green background */
  color: #1e7200; /* Darker green text */
}
.status-pending { /* Orange */
  background-color: rgba(253, 126, 20, 0.1); /* Lighter orange background */
  color: #c85a00; /* Darker orange text */
}
.status-cancelled { /* Grey */
  background-color: rgba(108, 117, 125, 0.1); /* Lighter grey background */
  color: #495057; /* Darker grey text */
}
.status-default {
  background-color: #e9ecef;
  color: #495057;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 5px;
  border-radius: 4px;
}
.action-btn:hover {
  background-color: #e9ecef;
}
.three-dots-btn {
  font-size: 20px;
  color: #6c757d;
}

.actions-dropdown {
  position: absolute;
  right: 100%; /* Position to the left of the button */
  top: 0;
  margin-right: 5px; /* Small gap */
  background-color: white;
  border: 1px solid #dde2e7;
  border-radius: 6px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
  z-index: 10;
  width: 100px; /* Or min-content */
}
.actions-dropdown button {
  display: block;
  width: 100%;
  padding: 8px 12px;
  text-align: left;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
}
.actions-dropdown button:hover {
  background-color: #f1f5f9;
}
.actions-dropdown button.delete-action {
    color: #dc3545; /* Red for delete */
}

.bulk-actions-footer {
    position: sticky;
    bottom: 0;
    left: 0;
    width: 100%;
    padding: 15px 25px;
    background-color: #ffffff;
    box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
    display: flex;
    justify-content: flex-start; /* Or center, or flex-end */
    z-index: 20; /* Above table content */
    box-sizing: border-box;
}
</style>