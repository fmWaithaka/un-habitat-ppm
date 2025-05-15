<template>
  <div class="dashboard-view">
    <header class="view-header">
      <h1>Project Dashboard</h1>
      <p>Visualizations of project data by key categories.</p>
    </header>

    <div v-if="loading" class="loading-indicator">
      <div class="spinner"></div>
      <p>Loading dashboard data...</p>
    </div>

    <div v-if="error" class="error-message">
      <p><strong>Oops! Could not load dashboard data.</strong></p>
      <p>{{ error }}</p>
      <button @click="fetchDashboardData" class="retry-button">Try Again</button>
    </div>

    <div v-if="!loading && !error" class="dashboard-content">

      <div class="dashboard-card">
        <h2>Projects by Country</h2>
        <div class="chart-container">
          <canvas ref="countryChartCanvas"></canvas>
          <div v-if="!countryChartData || countryChartData.length === 0" class="no-data-overlay">
            <p>No country data available to display chart.</p>
          </div>
        </div>
        <p v-if="countryChartData && countryChartData.length > 0" class="visualization-note">
            Showing projects by country, sorted by project count.
        </p>
      </div>

      <div class="dashboard-card">
        <h2>Projects by Lead Organization Unit</h2>
          <div class="chart-container">
            <canvas ref="orgUnitChartCanvas"></canvas>
            <div v-if="!orgUnitChartData || orgUnitChartData.length === 0" class="no-data-overlay">
              <p>No organization unit data available to display chart.</p>
            </div>
          </div>
      </div>

      <div class="dashboard-card">
        <h2>Projects by Themes</h2>
        <div v-if="themeChartData && themeChartData.length > 0">
            <ul>
                <li v-for="item in themeChartData" :key="item.name"> {{ item.name }}: {{ item.project_count }}
                </li>
            </ul>
        </div>
          <div v-else class="no-data-message">
            <p>No theme data available.</p>
          </div>
          <p class="visualization-note">Note: A Treemap or Sunburst chart could provide a more creative visualization for themes.</p>
      </div>

        <div class="dashboard-card">
        <h2>Projects on World Map</h2>
          <div v-if="worldMapData && worldMapData.length > 0">
            <ul>
                <li v-for="item in worldMapData" :key="item.country_name">
                    {{ item.country_name }}: {{ item.project_count }} projects
                </li>
            </ul>
        </div>
          <div v-else class="no-data-message">
            <p>No world map data available.</p>
        </div>
          <p class="visualization-note">Note: An interactive world map visualization could highlight countries with projects.</p>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';
// Import the service functions to fetch aggregated dashboard data
import {
    getProjectCountByCountry,
    getProjectCountByOrgUnit,
    getProjectCountByTheme,
    getWorldMapProjectData
} from '../services/projectService'; // Adjust path as needed

// Import Chart.js and necessary components for bar charts
import Chart from 'chart.js/auto';
import { BarController, CategoryScale, LinearScale, Title, Tooltip, Legend } from 'chart.js';

// Register the necessary Chart.js components for the chart types you are using
// 'auto' import usually handles common ones, but explicit registration is safer
Chart.register(BarController, CategoryScale, LinearScale, Title, Tooltip, Legend);


// Reactive variables to store fetched data and component states
const countryChartData = ref(null); // Data for country chart
const orgUnitChartData = ref(null); // Data for organization unit chart
const themeChartData = ref(null); // Data for themes (initially list)
const worldMapData = ref(null); // Data for world map (initially list)

const loading = ref(true); // Loading state
const error = ref(null); // Error state

// Refs to access the canvas elements in the template
const countryChartCanvas = ref(null);
const orgUnitChartCanvas = ref(null);

// Variables to hold the Chart.js chart instances
let countryChartInstance = null;
let orgUnitChartInstance = null;

// Define a color palette for the bars
const barColors = [
  'rgba(75, 192, 192, 0.8)', // Teal
  'rgba(153, 102, 255, 0.8)', // Purple
  'rgba(255, 159, 64, 0.8)', // Orange
  'rgba(255, 99, 132, 0.8)', // Red
  'rgba(54, 162, 235, 0.8)', // Blue
  'rgba(201, 203, 207, 0.8)', // Grey
  'rgba(255, 205, 86, 0.8)', // Yellow
  // Add more colors if you have more categories
];

// Function to fetch all dashboard data from backend endpoints
async function fetchDashboardData() {
  loading.value = true; // Set loading state to true
  error.value = null; // Clear any previous errors

  // Clear previous data
  countryChartData.value = null;
  orgUnitChartData.value = null;
  themeChartData.value = null;
  worldMapData.value = null;

  // Destroy existing charts before fetching new data
  destroyCharts();


  try {
    // Fetch data from the backend summary endpoints concurrently using Promise.all
    const [
        countryResponse,
        orgUnitResponse,
        themeResponse,
        worldMapResponse
    ] = await Promise.all([
        getProjectCountByCountry(),
        getProjectCountByOrgUnit(),
        getProjectCountByTheme(),
        getWorldMapProjectData() // Reusing country count endpoint for map data initially
    ]);

    // Assign fetched data to reactive variables
    countryChartData.value = countryResponse.data;
    orgUnitChartData.value = orgUnitResponse.data;
    themeChartData.value = themeResponse.data;
    worldMapData.value = worldMapResponse.data; // Data for the world map visualization

    console.log('Dashboard data fetched:', {
        country: countryChartData.value,
        orgUnit: orgUnitChartData.value,
        theme: themeChartData.value,
        worldMap: worldMapData.value,
    });

    // Data is fetched, the watch effects will now react when canvas refs become available
    // No need for nextTick() or immediate renderCharts() call here anymore

  } catch (err) {
    console.error('Error fetching dashboard data:', err);
      // Set error message based on the type of error
      if (err.response) {
      // Backend returned a response (e.g., 404, 500)
      error.value = `Error ${err.response.status}: ${err.response.data.detail || err.message || 'Failed to load dashboard data.'}`;
    } else if (err.request) {
      // Request was made but no response was received (e.g., network error)
      error.value = 'Failed to load dashboard data. No response from server.';
    } else {
      // Something else happened in setting up the request
      error.value = `Failed to load dashboard data: ${err.message}`;
    }
  } finally {
    loading.value = false; // Set loading state to false regardless of success or failure
  }
}

// Function to destroy existing Chart.js instances
function destroyCharts() {
    if (countryChartInstance) {
        countryChartInstance.destroy();
        countryChartInstance = null; // Set to null after destroying
    }
    if (orgUnitChartInstance) {
        orgUnitChartInstance.destroy();
        orgUnitChartInstance = null; // Set to null after destroying
    }
}


// Function to render Chart.js visualizations
function renderCharts() {
    console.log("Attempting to render charts...");
    console.log("Country canvas ref:", countryChartCanvas.value);
    console.log("Org Unit canvas ref:", orgUnitChartCanvas.value);
    console.log("Country data:", countryChartData.value);
    console.log("Org Unit data:", orgUnitChartData.value);

    // --- Render Projects by Country Horizontal Bar Chart ---
    // Check if canvas element exists AND data is available and not empty
    if (countryChartCanvas.value && countryChartData.value && countryChartData.value.length > 0) {
        console.log("Rendering Country Chart (Horizontal Bar)...");
        const ctx = countryChartCanvas.value.getContext('2d'); // Get the canvas rendering context
        if (ctx) { // Ensure context is successfully obtained

            // --- Data Preparation for Country Chart ---
            // Sort data by project_count descending for better readability
            // Use slice() to create a shallow copy before sorting to avoid mutating the original ref's value directly,
            // although for simple arrays used immediately, direct mutation might be acceptable depending on state management needs.
            const sortedCountryData = countryChartData.value.slice().sort((a, b) => b.project_count - a.project_count);

            // Optional: Limit the number of countries shown if the list is very long
            // const topN = 20; // Example: show only top 20
            // const limitedCountryData = sortedCountryData.slice(0, topN);

            const labels = sortedCountryData.map(item => item.country_name);
            const dataValues = sortedCountryData.map(item => item.project_count);

            // Generate background colors using the palette, cycling through colors
            const backgroundColors = labels.map((_, index) => barColors[index % barColors.length]);


            // Destroy existing instance before creating a new one
            if (countryChartInstance) {
              countryChartInstance.destroy();
            }

             countryChartInstance = new Chart(ctx, {
                type: 'bar', // Specify the chart type as 'bar'
                 options: { // Options for the chart
                   indexAxis: 'y', // <-- Set indexAxis to 'y' for horizontal bars
                   responsive: true, // Make the chart responsive to container size
                   maintainAspectRatio: false, // Allow the chart's aspect ratio to be controlled by its container's dimensions
                   scales: {
                       x: { // X-axis is now the value axis
                           beginAtZero: true, // Ensure the x-axis starts at zero
                           title: {
                               display: true,
                               text: 'Number of Projects', // Title for the x-axis
                                color: 'var(--color-text-primary)' // Use CSS variable for text color
                           },
                           ticks: {
                                color: 'var(--color-text-secondary)' // Use CSS variable for tick label color
                             },
                            grid: {
                                color: 'var(--color-border-light)' // Use CSS variable for grid line color
                            }
                       },
                        y: { // Y-axis is now the category axis (for country names)
                           ticks: {
                                color: 'var(--color-text-secondary)' // Use CSS variable for tick label color
                             },
                            grid: {
                                color: 'var(--color-border-light)' // Use CSS variable for grid line color
                            }
                        }
                   },
                    plugins: {
                        title: {
                            display: false, // Hide the Chart.js built-in title as we have a card header title
                        },
                        tooltip: {
                            enabled: true, // Enable tooltips on hover
                            backgroundColor: 'rgba(0, 0, 0, 0.8)', // Tooltip background color
                            titleColor: '#fff', // Tooltip title text color
                            bodyColor: '#fff', // Tooltip body text color
                            borderColor: 'rgba(255, 255, 255, 0.5)', // Tooltip border color
                            borderWidth: 1,
                            cornerRadius: 4, // Rounded corners for tooltip
                        },
                         legend: {
                             display: false, // Hide the legend if there's only one dataset
                         }
                    }
                },
                data: { // Data for the chart
                    labels: labels, // Use sorted country names
                    datasets: [{
                        label: 'Number of Projects', // Label for the dataset
                        data: dataValues, // Use sorted project counts
                         backgroundColor: backgroundColors, // Use the generated colors
                         borderColor: backgroundColors.map(color => color.replace('0.8', '1')), // Use a slightly less transparent border
                         borderWidth: 1
                    }]
                }
            });
        } else {
             console.error("Could not get 2D rendering context for Country Chart.");
        }
    } else {
        console.log("Skipping Country Chart rendering: Canvas or data not available or empty.");
    }


    // --- Render Projects by Lead Organization Unit Bar Chart (Vertical) ---
    // Similar logic to the Country chart, but keep vertical and simple colors
     if (orgUnitChartCanvas.value && orgUnitChartData.value && orgUnitChartData.value.length > 0) {
        console.log("Rendering Org Unit Chart (Vertical Bar)...");
        const ctx = orgUnitChartCanvas.value.getContext('2d');
         if (ctx) { // Ensure context is successfully obtained

            // Destroy existing instance before creating a new one
            if (orgUnitChartInstance) {
              orgUnitChartInstance.destroy();
            }

             orgUnitChartInstance = new Chart(ctx, {
                type: 'bar', // Specify the chart type as 'bar'
                data: {
                    // Use organization unit names from fetched data as labels on the x-axis
                    labels: orgUnitChartData.value.map(item => item.org_unit_name),
                    datasets: [{
                        label: 'Number of Projects', // Label for the dataset
                        // Use project counts from fetched data as the bar values
                        data: orgUnitChartData.value.map(item => item.project_count),
                         backgroundColor: 'rgba(153, 102, 255, 0.8)', // Example color
                         borderColor: 'rgba(153, 102, 255, 1)', // Example border color
                         borderWidth: 1 // Bar border width
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                     scales: {
                         y: {
                             beginAtZero: true,
                             title: {
                                 display: true,
                                 text: 'Number of Projects',
                                  color: 'var(--color-text-primary)'
                             },
                             ticks: {
                                 color: 'var(--color-text-secondary)'
                              },
                             grid: {
                                 color: 'var(--color-border-light)'
                             }
                         }
                         ,
                         x: {
                             ticks: {
                                 color: 'var(--color-text-secondary)'
                              },
                              grid: {
                                 color: 'var(--color-border-light)'
                              }
                         }
                    },
                     plugins: {
                         title: {
                             display: false, // Hide the Chart.js built-in title
                         },
                         tooltip: {
                             enabled: true, // Enable tooltips
                             backgroundColor: 'rgba(0, 0, 0, 0.8)', // Tooltip background color
                             titleColor: '#fff', // Tooltip title text color
                             bodyColor: '#fff', // Tooltip body text color
                             borderColor: 'rgba(255, 255, 255, 0.5)', // Tooltip border color
                             borderWidth: 1,
                             cornerRadius: 4, // Rounded corners for tooltip
                         },
                         legend: {
                             display: false, // Hide legend
                         }
                     }
                }
            });
        } else {
            console.error("Could not get 2D rendering context for Org Unit Chart.");
        }
    } else {
         console.log("Skipping Org Unit Chart rendering: Canvas or data not available or empty.");
    }


    // Note: Themes and World Map are rendered as lists in the template for now.
    // More creative visualizations (Treemap, Sunburst, World Map) would require
    // integrating different libraries or more complex Chart.js configurations.
}


// Lifecycle hook: Called after the component is mounted to the DOM
onMounted(() => {
  console.log("DashboardView mounted. Fetching data...");
  fetchDashboardData(); // Fetch data when the component is ready
});

// Watch for the countryChartCanvas ref to be assigned a DOM element
// and countryChartData to be loaded.
watch([countryChartCanvas, countryChartData], ([newCanvas, newData]) => {
    console.log("Country watch triggered. Canvas:", newCanvas, "Data loaded:", !!newData);
    if (newCanvas && newData && newData.length > 0) {
        console.log("Conditions met for Country Chart rendering via watch.");
        renderCharts(); // Call renderCharts when both are ready
    }
});

// Watch for the orgUnitChartCanvas ref to be assigned a DOM element
// and orgUnitChartData to be loaded.
watch([orgUnitChartCanvas, orgUnitChartData], ([newCanvas, newData]) => {
    console.log("Org Unit watch triggered. Canvas:", newCanvas, "Data loaded:", !!newData);
    if (newCanvas && newData && newData.length > 0) {
        console.log("Conditions met for Org Unit Chart rendering via watch.");
         renderCharts(); // Call renderCharts when both are ready
    }
});


// Lifecycle hook: Called before the component is unmounted from the DOM
// Destroy chart instances to prevent memory leaks
onBeforeUnmount(() => {
    console.log("DashboardView unmounting. Destroying charts...");
    destroyCharts();
});


// Variables and functions declared in <script setup> are automatically exposed to the template.
</script>

<style scoped>
/* Scoped styles specific to DashboardView.vue */
/*
  Ensure these CSS variables are defined somewhere globally in your project,
  e.g., in a CSS framework or a dedicated variables file:
  --color-text-primary, --color-text-secondary, --color-primary, --color-primary-dark,
  --color-background-content, --border-radius-lg, --shadow-md, --color-border,
  --color-text-heading, --color-border-light, --border-radius-md, --color-background-body,
  --color-background-error, --color-text-error, --color-border-error,
  --color-text-light, --border-radius-sm, --color-background-mute, --color-background-body-rgb
*/
.dashboard-view {
  padding: 20px;
  max-width: 1200px; /* Allow wider layout for dashboard */
  margin: 0 auto;
  color: var(--color-text-primary); /* Use primary text color */
}

.view-header {
  text-align: center;
  margin-bottom: 40px;
  color: var(--color-text-primary); /* Use primary text color */
}

.view-header h1 {
  font-size: 2.8em; /* Larger heading for dashboard */
  font-weight: 700;
  color: var(--color-primary); /* Use primary color for main heading */
  margin-bottom: 10px;
}

.view-header p {
  font-size: 1.2em;
  color: var(--color-text-secondary); /* Use secondary text color */
}

.dashboard-content {
    display: grid;
    /* Create a responsive grid: min column width 300px, max 1fr (fraction of available space) */
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px; /* Space between grid items (dashboard cards) */
}

.dashboard-card {
  background-color: var(--color-background-content); /* Use content background color */
  border-radius: var(--border-radius-lg); /* Large rounded corners */
  box-shadow: var(--shadow-md); /* Medium shadow */
  padding: 20px;
  display: flex;
  flex-direction: column; /* Stack content vertically within the card */
  border: 1px solid var(--color-border); /* Add a subtle border */
}

.dashboard-card h2 {
  font-size: 1.6em;
  font-weight: 600;
  color: var(--color-text-heading); /* Use heading text color */
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--color-border-light); /* Separator below title */
}

.chart-container {
    position: relative; /* Needed for Chart.js responsiveness and overlay positioning */
    height: 300px; /* Set a fixed height for the chart container */
    width: 100%; /* Take full width of the parent card */
    margin-bottom: 15px;
    /* Added display flex to help canvas take up space */
    display: flex;
    justify-content: center; /* Center the canvas if it doesn't fill */
    align-items: center; /* Center the canvas vertically */
}

/* Ensure canvas takes up space within its container */
.chart-container canvas {
    display: block; /* Make canvas a block element */
    max-width: 100%; /* Ensure it doesn't overflow */
    max-height: 100%; /* Ensure it doesn't overflow */
    /* Optional: Set explicit initial dimensions if needed, but responsive should handle */
    /* width: 100%; */
    /* height: 100%; */
}

/* Style for the no-data-overlay */
.no-data-overlay {
    position: absolute; /* Position over the canvas */
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    /* Using rgba with var is tricky, consider defining background-color directly */
    /* Example assuming --color-background-body-rgb exists and is comma-separated RGB values */
    /* background-color: rgba(var(--color-background-body-rgb, 255, 255, 255), 0.8); */
    /* A safer approach is a fixed or calculated color */
     background-color: rgba(255, 255, 255, 0.8); /* Example white with transparency */
     /* Or use your theme colors if possible */
     /* background-color: hsla(var(--color-background-body-hsl), 0.8); */

    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    color: var(--color-text-secondary);
    font-size: 1.1em;
    z-index: 1; /* Ensure it's above the canvas */
    border-radius: var(--border-radius-md); /* Match card border radius */
}


/* Styles for loading, error, and no data messages */
.loading-indicator,
.error-message,
.no-data-message { /* Keep no-data-message for the list sections */
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px 20px;
  text-align: center;
  min-height: 150px;
  border-radius: var(--border-radius-md);
  background-color: var(--color-background-body); /* Use body background for contrast */
  color: var(--color-text-primary);
  margin-top: 10px;
}

.error-message {
  background-color: var(--color-background-error); /* Error background color */
  color: var(--color-text-error); /* Error text color */
  border: 1px solid var(--color-border-error); /* Error border color */
}

.error-message p,
.no-data-message p {
    margin-bottom: 10px;
}

.retry-button {
  background-color: var(--color-primary); /* Primary color background */
  color: var(--color-text-light); /* Light text color */
  border: none;
  padding: 8px 16px;
  border-radius: var(--border-radius-md);
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s ease;
  margin-top: 10px;
}

.retry-button:hover {
  background-color: var(--color-primary-dark); /* Darker primary on hover */
}

/* Styles for the data lists (for Themes and World Map initially) */
.dashboard-card ul {
    list-style: none; /* Remove default list bullets */
    padding: 0;
    margin-top: 10px;
}

.dashboard-card li {
    background-color: var(--color-background-mute); /* Muted background for list items */
    padding: 8px 12px;
    margin-bottom: 5px;
    border-radius: var(--border-radius-sm);
    font-size: 0.9em;
    color: var(--color-text-secondary); /* Secondary text color */
    border: 1px solid var(--color-border-light); /* Light border */
}

.visualization-note {
    font-size: 0.9em;
    color: var(--color-text-secondary);
    margin-top: 15px;
    font-style: italic;
    text-align: center;
}

/* Spinner styles (Ensure these are defined, either globally or copied here) */
/* Example basic spinner styles:
.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-left-color: var(--color-primary);
  border-radius: 50%;
  width: 30px;
  height: 30px;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
*/

</style>