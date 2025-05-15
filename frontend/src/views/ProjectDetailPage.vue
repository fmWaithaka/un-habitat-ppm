<template>
  <div class="project-detail-page">
    <div class="page-header">
      <h1 class="page-title">Project Details</h1>
      <router-link to="/" class="btn btn-secondary">Back to Projects</router-link>
    </div>

    <div v-if="loading" class="loading-state">Loading project details...</div>
    <div v-if="error" class="error-state">
      <p>Error loading project: {{ error.message || 'Unknown error' }}</p>
      <button @click="fetchProjectDetails" class="btn">Try Again</button>
    </div>

    <div v-if="project && !loading && !error" class="project-details-content">
      <h2>{{ project.title }}</h2>
      <p><strong>ID:</strong> {{ project.id }}</p>
      <p><strong>Excel ID:</strong> {{ project.project_id_excel || 'N/A' }}</p>
      <p><strong>Status:</strong> <span :class="getStatusClass(project.status)" class="status-badge">{{ project.status || 'N/A' }}</span></p>
      <p><strong>Country:</strong> {{ project.country ? project.country.name : 'N/A' }}</p>
      <p>
        <strong>Donor(s):</strong>
        <span v-if="project.donors && project.donors.length">
          {{ project.donors.map(donor => donor.name).join(', ') }}
        </span>
        <span v-else>N/A</span>
      </p>
      <section class="details-section">
        <h3>Timelines</h3>
        <p><strong>Start Date:</strong> {{ project.start_date || 'N/A' }}</p>
        <p><strong>End Date:</strong> {{ project.end_date || 'N/A' }}</p>
      </section>

      </div>
     <div v-if="!project && !loading && !error" class="no-project-found">
      <p>Project not found.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch} from 'vue';
import apiService from '@/services/api';
import { useRouter } from 'vue-router'; 

const router = useRouter(); 

const props = defineProps({
  id: { // This prop is automatically passed due to `props: true` in router config
    type: [String, Number],
    required: true
  }
});

const project = ref(null);
const loading = ref(true);
const error = ref(null);

const fetchProjectDetails = async () => {
  loading.value = true;
  error.value = null;
  try {
    // Use the id from props (passed by the router)
    const response = await apiService.getProjectById(props.id); // You'll need to implement getProjectById in apiService
    project.value = response.data;
  } catch (err) {
    console.error(`Failed to fetch project ${props.id}:`, err);
    error.value = err;
    project.value = null; // Ensure project is null on error
  } finally {
    loading.value = false;
  }
};

// Fetch details when component is mounted
onMounted(() => {
  fetchProjectDetails();
});

// Optional: If the route ID could change while the component is already mounted
// (e.g., navigating from /project/1 to /project/2 directly)
watch(() => props.id, (newId) => {
  if (newId) {
    fetchProjectDetails();
  }
});

// Re-use status class logic if needed, or import from a utility
const getStatusClass = (status) => {
  if (!status) return 'status-default';
  const lowerStatus = status.toLowerCase();
  if (lowerStatus === 'pending approval') return 'status-pending';
  if (lowerStatus === 'active' || lowerStatus === 'completed') return 'status-approved';
  if (lowerStatus === 'cancelled') return 'status-cancelled';
  return 'status-default';
};
</script>

<style scoped>
.project-detail-page {
  padding: 20px 25px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f9fbfd;
  height: 100%;
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
  text-decoration: none; /* For router-link styled as button */
  display: inline-block; /* For router-link styled as button */
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}
.btn-secondary:hover {
  background-color: #5a6268;
}

.loading-state, .error-state, .no-project-found {
  text-align: center;
  padding: 40px 20px;
  margin-top: 20px;
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

.project-details-content {
  background-color: #ffffff;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.project-details-content h2 {
  margin-top: 0;
  font-size: 24px;
  color: #333;
  margin-bottom: 20px;
}

.project-details-content p {
  margin-bottom: 12px;
  line-height: 1.6;
  color: #495057;
}

.project-details-content p strong {
  color: #343a40;
  margin-right: 8px;
}

.details-section {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px dashed #e0e0e0;
}
.details-section h3 {
  font-size: 18px;
  color: #333;
  margin-bottom: 15px;
}

/* Copied status badge styles for consistency - consider moving to a global CSS or a utility */
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
</style>