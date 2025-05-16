<template>
  <div class="project-list-page-content">
    <div class="page-header sticky-header">
      <h1 class="page-title">Projects</h1>
      <div class="actions-bar">
        <div class="search-filter">
          <input type="text" placeholder="Filter by project, country..." v-model="searchQuery" @input="debouncedApplyFilter" />
        </div>
        <button class="btn btn-primary new-project-btn" @click="router.push({ name: 'CreateProject' })">
          <span class="plus-icon">+</span> New Project
        </button>
      </div>
    </div>

    <div class="scrollable-content">
      <div v-if="loading" class="loading-state">Loading projects...</div>
      <div v-if="error" class="error-state">
        <p>Error loading projects: {{ error.message || 'Unknown error' }}</p>
        <p v-if="error.response && error.response.data">
          Server says: {{ JSON.stringify(error.response.data) }}
        </p>
        <button @click="() => fetchProjects(currentPage)" class="btn">Try Again</button>
      </div>

      <div v-if="!loading && !error && projects.length > 0" class="table-container">
        <table>
          <thead>
            <tr class="sticky-table-header">
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
            <tr v-for="project in projects" :key="project.id" @click="viewProjectDetails(project)" class="project-row">
              <td class="checkbox-col"><input type="checkbox" v-model="selectedProjects" :value="project.id" @click.stop /></td>
              <td class="id-col">{{ project.id }}</td>
              <td class="title-col">
                <div class="project-title-main">{{ project.title }}</div>
                <div class="project-title-sub">{{ project.project_id_excel || 'N/A' }}</div>
              </td>
              <td class="donors-col">
                <span v-if="project.donors_detail && project.donors_detail.length > 0">
                  {{ project.donors_detail.map(donor => donor.name).join(', ') }}
                </span>
                <span v-else>N/A</span>
              </td>
              <td class="country-col">{{ project.country_detail ? project.country_detail.name : 'N/A' }}</td>
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

      <div v-if="!loading && !error && projects.length === 0 && totalItems === 0" class="no-projects-found">
        <p>No projects have been created yet.</p>
      </div>
      <div v-if="!loading && !error && projects.length === 0 && totalItems > 0 && searchQuery" class="no-projects-found">
        <p>No projects match your current filter: "{{ searchQuery }}"</p>
      </div>
    </div>

    <div v-if="selectedProjects.length > 0 && !loading && !error" class="bulk-actions-footer">
      <button @click="deleteSelectedProjects" class="btn btn-danger">
        Delete Selected ({{ selectedProjects.length }})
      </button>
    </div>

    <div v-if="!loading && !error && totalItems > 0 && totalPages > 1" class="pagination-controls">
      <span class="pagination-info">
        {{ (currentPage - 1) * itemsPerPage + 1 }} - {{ Math.min(currentPage * itemsPerPage, totalItems) }} of {{ totalItems }}
      </span>
      <div class="pagination-buttons">
        <button @click="prevPage" :disabled="currentPage === 1 || loading" class="btn pagination-btn">
          &lt; Previous
        </button>
        <span class="page-indicator">Page {{ currentPage }} of {{ totalPages }}</span>
        <button @click="nextPage" :disabled="currentPage === totalPages || loading" class="btn pagination-btn">
          Next &gt;
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import apiService from '@/services/api';
import { useRouter } from 'vue-router';
// import { debounce } from 'lodash-es'; // Optional: for debouncing search input

const router = useRouter();

const projects = ref([]);
const loading = ref(true);
const error = ref(null);
const searchQuery = ref('');
const selectedProjects = ref([]);
const showActionsFor = ref(null);

// Pagination state
const currentPage = ref(1);
const itemsPerPage = ref(10); // As requested
const totalItems = ref(0);

const totalPages = computed(() => {
  if (totalItems.value === 0) return 1; // Avoid division by zero, ensure at least 1 page
  return Math.ceil(totalItems.value / itemsPerPage.value);
});

// Debounce function (simple implementation if not using lodash)
const debounce = (func, delay) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => {
      func.apply(null, args);
    }, delay);
  };
};

const fetchProjectsAPI = async (pageToFetch) => {
  loading.value = true;
  error.value = null;
  selectedProjects.value = []; // Clear selection on data change

  const params = {
    page: pageToFetch,
    page_size: itemsPerPage.value,
  };
  if (searchQuery.value) {
    params.search = searchQuery.value.trim(); // Assuming your backend uses 'search' for filtering
  }

  try {
    const response = await apiService.getProjects(params);
    projects.value = response.data.results || [];
    totalItems.value = response.data.count || 0;
    currentPage.value = pageToFetch; // Update current page after successful fetch

    console.log("Fetched projects data:", projects.value); // Log fetched data for inspection

      if (pageToFetch > totalPages.value && totalPages.value > 0) {
        // If current page is out of bounds after a search/delete, go to last valid page
        await fetchProjectsAPI(totalPages.value);
    }

  } catch (err) {
    console.error('Failed to fetch projects:', err);
    error.value = err;
    projects.value = []; // Clear projects on error
    totalItems.value = 0; // Reset total items on error
  } finally {
    loading.value = false;
  }
};

// Renamed original fetchProjects to fetchProjectsAPI to avoid confusion
const fetchProjects = (page = 1) => {
    fetchProjectsAPI(page);
};


// Watch for searchQuery changes to trigger a new fetch (debounced)
const debouncedApplyFilter = debounce(() => {
  fetchProjects(1); // Go to page 1 for new search
}, 500); // 500ms debounce delay

onMounted(() => {
  fetchProjects(currentPage.value); // Fetch initial page
});

const allSelected = computed({
  get: () => {
    // Selects all items on the current page
    return projects.value.length > 0 && selectedProjects.value.length === projects.value.length;
  },
  set: (value) => {
    if (value) {
      selectedProjects.value = projects.value.map(p => p.id);
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
  if (lowerStatus === 'approved') return 'status-approved';
  if (lowerStatus === 'completed') return 'status-approved'; // Assuming 'Completed' is also a 'good' status
  if (lowerStatus === 'cancelled') return 'status-cancelled';
  return 'status-default';
};

const viewProjectDetails = (project) => {
  console.log('View details for project:', project.id);
  // Navigate to the project detail page
  router.push({ name: 'ProjectDetail', params: { id: project.id } });
};


const toggleProjectActions = (projectId) => {
  showActionsFor.value = showActionsFor.value === projectId ? null : projectId;
};

const editProject = (projectId) => {
  console.log('Editing project:', projectId);
  showActionsFor.value = null; // Close dropdown
  // Navigate to the edit project page, passing the project ID as a route parameter
  router.push({ name: 'EditProject', params: { id: projectId } });
};

const deleteSingleProject = async (projectId) => {
  if (!confirm(`Are you sure you want to delete project ID ${projectId}?`)) return;
  showActionsFor.value = null; // Close dropdown
  loading.value = true; // Optional: show loading state during delete
  try {
    await apiService.deleteProject(projectId);
    alert(`Project ID ${projectId} deleted successfully.`);
    // Refresh the current page's data
    // Check if it was the last item on the page and if it's not the first page
    if (projects.value.length === 1 && currentPage.value > 1) {
        fetchProjects(currentPage.value - 1); // Go to previous page
    } else {
        fetchProjects(currentPage.value); // Refresh current page
    }
  } catch (err) {
    console.error(`Failed to delete project ${projectId}:`, err);
    alert(`Error deleting project: ${err.message}`);
  } finally {
    loading.value = false;
  }
};

const deleteSelectedProjects = async () => {
  if (!selectedProjects.value.length) return;
  if (!confirm(`Are you sure you want to delete ${selectedProjects.value.length} selected project(s)?`)) return;

  loading.value = true;
  let failedDeletes = 0;
  try {
    for (const projectId of selectedProjects.value) {
      try {
        await apiService.deleteProject(projectId);
      } catch (singleDeleteError) {
        console.error(`Failed to delete project ${projectId}:`, singleDeleteError);
        failedDeletes++;
      }
    }
    const successfulDeletes = selectedProjects.value.length - failedDeletes;
    if (successfulDeletes > 0) {
        alert(`${successfulDeletes} project(s) deleted successfully.`);
    }
    if (failedDeletes > 0) {
      // You might want to display which projects failed to delete
        alert(`${failedDeletes} project(s) could not be deleted. Check console for errors.`);
    }

    selectedProjects.value = []; // Clear selection
    // Refresh logic: determine the page to go to after deletion
    // If current page would be empty and it's not the first page, try to go to previous.
    // This is a simplified refresh; more complex logic might be needed for exact page after bulk delete.
    const newTotalItems = totalItems.value - successfulDeletes;
    const newTotalPages = Math.ceil(newTotalItems / itemsPerPage.value) || 1;
    fetchProjects(Math.min(currentPage.value, newTotalPages));

  } catch (err) { // This catch might be redundant if individual errors are caught
    console.error('Failed to delete selected projects:', err);
    alert(`Error during bulk delete operation: ${err.message}`);
  } finally {
    loading.value = false;
  }
};

// Pagination navigation methods
const goToPage = (pageNumber) => {
  if (pageNumber >= 1 && pageNumber <= totalPages.value && pageNumber !== currentPage.value) {
    fetchProjects(pageNumber);
  }
};

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    fetchProjects(currentPage.value + 1);
  }
};

const prevPage = () => {
  if (currentPage.value > 1) {
    fetchProjects(currentPage.value - 1);
  }
};

// Watch for external changes that might affect total pages (e.g. if totalItems could change by other means)
// This is more advanced and often not needed if all data changes trigger fetchProjects.
// watch(totalItems, () => {
//    if (currentPage.value > totalPages.value && totalPages.value > 0) {
//      fetchProjects(totalPages.value);
//    }
// });

</script>

<style scoped>
/* ... (previous styles remain the same) ... */
.project-list-page-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 20px 25px;
  background-color: #f9fbfd;
  box-sizing: border-box;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px; /* Space before content/table */
  background-color: #f9fbfd; /* Match page background */
  z-index: 100; /* Keep above scrollable content */
}

.sticky-header {
  position: sticky;
  top: 0; /* Adjust if you have a global navbar above this component */
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.actions-bar {
  display: flex;
  align-items: center;
  gap: 15px;
}

.search-filter input {
  padding: 10px 15px;
  border: 1px solid #dde2e7;
  border-radius: 6px;
  min-width: 250px;
  font-size: 14px;
}
.search-filter input:focus {
  outline: none;
  border-color: #007bff;
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
  white-space: nowrap; /* Prevent text wrapping on buttons */
}

.btn-primary {
  background-color: #007bff;
  color: white;
  display: flex;
  align-items: center;
  gap: 8px;
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

.scrollable-content {
  flex-grow: 1;
  overflow-y: auto;
  /* Consider removing explicit margin/padding here if table-container handles it */
}

.loading-state, .error-state, .no-projects-found {
  text-align: center;
  padding: 40px 20px;
  margin: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  color: #555;
}
.error-state {
  border-left: 4px solid #dc3545;
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
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  overflow-x: auto;
  margin-bottom: 20px; /* Space before pagination or bulk actions */
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

th, td {
  padding: 14px 18px;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
  vertical-align: middle;
}

thead th {
  background-color: #f8f9fa;
  color: #495057;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 12px;
  letter-spacing: 0.5px;
}

.sticky-table-header th {
  position: sticky;
  top: 0; /* Will stick to top of .scrollable-content or .table-container if it's the one scrolling */
  background-color: #f8f9fa; /* Ensure background is opaque */
  z-index: 10; /* Above table content */
}
/* Apply border radius to the actual first/last th cells in the sticky header */
.sticky-table-header th:first-child {
  border-top-left-radius: 8px;
}
.sticky-table-header th:last-child {
  border-top-right-radius: 8px;
}


.project-row {
  cursor: pointer;
  transition: background-color 0.15s ease-in-out;
}
.project-row:hover {
  background-color: #f1f5f9;
}
.project-row:last-child td {
  border-bottom: none;
}

.checkbox-col { width: 40px; text-align: center; }
.id-col { width: 70px; color: #6c757d; }
.title-col { min-width: 200px; }
.project-title-main {
  font-weight: 500;
  color: #212529;
  margin-bottom: 3px;
}
.project-title-sub {
  font-size: 0.85em;
  color: #6c757d;
}
.donors-col, .country-col { width: 15%; color: #495057; }
.status-col { width: 130px; }
.actions-col { width: 50px; text-align: center; position: relative; }

.status-badge {
  padding: 5px 10px;
  border-radius: 15px;
  font-size: 0.8em;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: inline-block;
  min-width: 100px;
  text-align: center;
}
.status-approved { background-color: rgba(40, 167, 69, 0.1); color: #1e7200; }
.status-pending { background-color: rgba(253, 126, 20, 0.1); color: #c85a00; }
.status-cancelled { background-color: rgba(108, 117, 125, 0.1); color: #495057; }
.status-default { background-color: #e9ecef; color: #495057; }

.action-btn { background: none; border: none; cursor: pointer; padding: 5px; border-radius: 4px; }
.action-btn:hover { background-color: #e9ecef; }
.three-dots-btn { font-size: 20px; color: #6c757d; }

.actions-dropdown {
  position: absolute;
  right: 100%;
  top: 0;
  margin-right: 5px;
  background-color: white;
  border: 1px solid #dde2e7;
  border-radius: 6px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
  z-index: 20;
  width: 100px;
}
.actions-dropdown button { display: block; width: 100%; padding: 8px 12px; text-align: left; background: none; border: none; cursor: pointer; font-size: 14px; }
.actions-dropdown button:hover { background-color: #f1f5f9; }
.actions-dropdown button.delete-action { color: #dc3545; }

.bulk-actions-footer {
  position: sticky;
  bottom: 0;
  padding: 15px 25px; /* Matches page padding */
  background-color: #ffffff;
  box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
  display: flex;
  justify-content: flex-start;
  z-index: 50;
  /* width is 100% of .project-list-page-content by default, adjusted for padding */
  margin: 0 -25px; /* Counteract parent padding to span full width */
  padding-left: 25px; /* Restore padding */
  padding-right: 25px; /* Restore padding */
}


.pagination-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0; /* Padding above and below controls */
  margin-top: 10px; /* Space above pagination if bulk actions footer is not visible */
  border-top: 1px solid #e9ecef; /* Separator line */
}
.pagination-info {
  font-size: 0.9em;
  color: #6c757d;
}
.pagination-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
}
.pagination-btn {
  background-color: #fff;
  border: 1px solid #dde2e7;
  color: #007bff;
}
.pagination-btn:disabled {
  color: #6c757d;
  border-color: #e9ecef;
  cursor: not-allowed;
  background-color: #f8f9fa;
}
.pagination-btn:hover:not(:disabled) {
  background-color: #e9ecef;
}
.page-indicator {
    font-size: 0.9em;
    color: #333;
    padding: 0 10px;
}
</style>
