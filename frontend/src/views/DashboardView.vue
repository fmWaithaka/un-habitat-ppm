<template>
  <div class="dashboard-view-container">
    <div class="page-header">
      <h1 class="page-title">Project Dashboard</h1>
    </div>

    <div v-if="loading" class="loading-state">
      <LoadingSpinner text="Loading dashboard data..." />
    </div>

    <div v-if="error" class="error-state">
      <p>Error loading dashboard data: {{ error.message || 'Unknown error' }}</p>
      <button @click="fetchDashboardData" class="btn">Try Again</button>
    </div>

    <div v-if="!loading && !error" class="dashboard-content">
      <section class="kpi-section">
        <SectionTitle>Overall Summary</SectionTitle>
        <KpiCardRow :kpis="kpiData" />
      </section>

      <div class="main-charts-grid">

          <div class="chart-grid-item country-bar-chart-item">
                <h4 class="chart-title-h4">Top Single Countries by PAG Value</h4>
                <BarChart
                  :chartData="singleCountryDataForBarChart"
                  dataKey="name"
                  valueKey="value"
                  title="" orientation="horizontal"
                  :topN="15"
                />
           </div>

          <div class="chart-grid-item pie-chart-item">
               <h4 class="chart-title-h4">Combined/Regional/Global PAG Value Distribution</h4>
               <PieChart
                 :chartData="topNCombinedCountryData"
                 title="" legendPosition="right"
                 :showLegend="false"
               />
          </div>

          <div class="chart-grid-item organizational-chart-item">
               <h4 class="chart-title-h4">Organizational Distribution (Total PAG Value)</h4>
               <BarChart
                 :chartData="valueByLeadOrgData"
                 dataKey="name"
                 valueKey="value"
                 title="" orientation="vertical"
               />
          </div>

          <div class="chart-grid-item thematic-chart-item">
               <h4 class="chart-title-h4">Thematic Distribution (Total PAG Value)</h4>
               <BarChart
                 :chartData="valueByThemeData"
                 dataKey="name"
                 valueKey="value"
                 title="" orientation="vertical"
               />
          </div>

           </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
// Import the object containing all API call functions from api.js
import apiService from '@/services/api'; // Ensure this path is correct

import LoadingSpinner from '@/components/common/LoadingSpinner.vue';
import SectionTitle from '@/components/dashboard/SectionTitle.vue'; // Keep SectionTitle for the main section
import KpiCardRow from '@/components/dashboard/KpiCardRow.vue';
// import WorldMap from '@/components/dashboard/WorldMap.vue'; // Removed WorldMap import
import BarChart from '@/components/common/BarChart.vue';
import PieChart from '@/components/common/PieChart.vue';


// Data refs for fetched data
const kpiData = ref(null);
// valueByCountryData will now hold the object { single_countries_data: [], combined_data: [] }
const valueByCountryData = ref(null); // Initialize as null to check if data has been fetched
const valueByLeadOrgData = ref([]);
const valueByThemeData = ref([]);
// const aiInsight = ref(''); // Ref for AI insights


// Loading and error states
const loading = ref(true);
const error = ref(null);

// Define how many top items to show in the combined data pie chart
const TOP_N_COMBINED = 7; // Show top 7 combined/regional/global categories

// Computed properties to extract and process data for different charts
const singleCountryDataForMap = computed(() => {
    // WorldMap expects an array of { name, value } for single countries
    // Return empty array if valueByCountryData is null or single_countries_data is missing/empty
    // This computed property is still needed even if the map is removed,
    // as the BarChart for single countries uses this data.
    return valueByCountryData.value && valueByCountryData.value.single_countries_data
           ? valueByCountryData.value.single_countries_data
           : [];
});

const singleCountryDataForBarChart = computed(() => {
    // BarChart for single countries expects an array of { name, value }
    // Return empty array if valueByCountryData is null or single_countries_data is missing/empty
     return valueByCountryData.value && valueByCountryData.value.single_countries_data
           ? valueByCountryData.value.single_countries_data
           : [];
});

const combinedCountryData = computed(() => {
    // This computed property holds the raw combined/regional/global data
    return valueByCountryData.value && valueByCountryData.value.combined_data
           ? valueByCountryData.value.combined_data
           : [];
});

// New computed property to process combined data for the Pie Chart (Top N + Other)
const topNCombinedCountryData = computed(() => {
    const data = combinedCountryData.value; // Get the raw combined data

    if (!data || data.length === 0) {
        return []; // Return empty array if no data
    }

    // Sort data descending by value
    const sortedData = [...data].sort((a, b) => b.value - a.value);

    // Take the top N items
    const topNItems = sortedData.slice(0, TOP_N_COMBINED);

    // Calculate the sum of the remaining items
    const otherValue = sortedData.slice(TOP_N_COMBINED).reduce((sum, item) => sum + item.value, 0);

    // Create the final data array for the pie chart
    const pieChartData = [...topNItems];

    // Add the "Other" slice if there are remaining items
    if (otherValue > 0) {
        pieChartData.push({ name: 'Other', value: otherValue });
    }

    return pieChartData;
});


// Function to fetch all dashboard data
const fetchDashboardData = async () => {
  loading.value = true;
  error.value = null;
  // Reset country data to null before fetching
  valueByCountryData.value = null;


  try {
    // Fetch all data concurrently using Promise.all
    const [kpisResponse, countryValueResponse, leadOrgValueResponse, themeValueResponse /*, aiInsightResponse*/] = await Promise.all([
      apiService.getDashboardKPIs(),
      apiService.getValueByCountry(), // This now returns { single_countries_data, combined_data }
      apiService.getValueByLeadOrg(),
      apiService.getValueByTheme(),
      // apiService.getAIInsights(), // Uncomment if you want to fetch AI insights
    ]);

    // Map the fetched KPI data to the format expected by KpiCardRow/KpiCard
    kpiData.value = {
      totalProjects: { title: 'Total Projects', value: kpisResponse.total_projects_count, indicatorColor: '#007bff', format: 'number' }, // Primary color
      totalPagValue: { title: 'Total PAG Value', value: kpisResponse.total_pag_value, indicatorColor: '#28a745', format: 'currency', currency: 'KSh' }, // Success color, KSh
      totalContribution: { title: 'Total Contribution', value: kpisResponse.total_contribution, indicatorColor: '#17a2b8', format: 'currency', currency: 'KSh' }, // Info color, KSh
      totalExpenditure: { title: 'Total Expenditure', value: kpisResponse.total_expenditure, indicatorColor: '#dc3545', format: 'currency', currency: 'KSh' }, // Danger color, KSh
      overallFinancialHealth: { title: 'Financial Health', value: kpisResponse.overall_financial_health, indicatorColor: '#ffc107', format: 'currency', currency: 'KSh' }, // Warning color, KSh
      // Removed unique counts as per previous request
    };

    // Assign the full response object for country data
    valueByCountryData.value = countryValueResponse;
    // Assign data for other charts (assuming they return arrays of { name, value })
    valueByLeadOrgData.value = leadOrgValueResponse;
    valueByThemeData.value = themeValueResponse;
    // aiInsight.value = aiInsightResponse.insight; // Assign AI insight


    console.log("Fetched KPI Data:", kpiData.value);
    console.log("Fetched Value by Country Data:", valueByCountryData.value); // Log the structure
    console.log("Fetched Value by Lead Org Data:", valueByLeadOrgData.value);
    console.log("Fetched Value by Theme Data:", valueByThemeData.value);
    // console.log("Fetched AI Insight:", aiInsight.value);


  } catch (err) {
    console.error('Failed to fetch dashboard data:', err);
    error.value = err;
  } finally {
    loading.value = false;
  }
};


// Fetch data when the component is mounted
onMounted(() => {
  fetchDashboardData();
});

// Helper function for status class (can be moved to a utility if used elsewhere)
const getStatusClass = (status) => {
  if (!status) return 'status-default';
  const lowerStatus = status.toLowerCase();
  if (lowerStatus === 'pending approval') return 'status-pending';
  if (lowerStatus === 'approved' || lowerStatus === 'completed') return 'status-approved';
  if (lowerStatus === 'cancelled') return 'status-cancelled';
  return 'status-default';
};
</script>

<style scoped>
/* Base styling for the dashboard container */
.dashboard-view-container {
  padding: 20px 25px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f9fbfd;
  min-height: 100vh;
  box-sizing: border-box;
}

/* Styling for the page header */
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

/* Styling for loading and error states */
.loading-state, .error-state {
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

/* --- Dashboard Content Grid Layout --- */
.dashboard-content {
    display: grid;
    grid-template-columns: 1fr; /* Default to single column on small screens */
    gap: 30px; /* Space between main sections */
    padding-top: 10px; /* Add some space above the first section */
}

/* Responsive adjustments for larger screens */
@media (min-width: 768px) {
    .dashboard-content {
        /* Use a 2-column layout for medium screens */
        grid-template-columns: repeat(2, 1fr);
        gap: 30px; /* Consistent gap */
    }

    .kpi-section {
        grid-column: 1 / -1; /* KPI row spans all columns */
        margin-bottom: 20px; /* Add space below KPI section */
    }

    /* Main charts grid container - Arranges charts in a 2x2 grid */
    .main-charts-grid {
        grid-column: 1 / -1; /* Spans both columns below the KPI section */
        display: grid;
        /* Define a 2x2 grid */
        grid-template-columns: repeat(2, 1fr);
        grid-template-rows: repeat(2, auto); /* Rows size based on content */
        gap: 30px; /* Space between charts */
    }

    /* Specific grid placement for charts within main-charts-grid */
     .chart-grid-item.country-bar-chart-item {
         grid-column: 1 / 2; /* Top Left */
         grid-row: 1 / 2;
     }

     .chart-grid-item.pie-chart-item {
         grid-column: 2 / 3; /* Top Right */
         grid-row: 1 / 2;
     }

     .chart-grid-item.organizational-chart-item {
         grid-column: 1 / 2; /* Bottom Left */
         grid-row: 2 / 3;
     }

     .chart-grid-item.thematic-chart-item {
         grid-column: 2 / 3; /* Bottom Right */
         grid-row: 2 / 3;
     }


     /* Optional: Adjust for very large screens */
     @media (min-width: 1200px) {
          .dashboard-content {
              grid-template-columns: repeat(3, 1fr); /* 3 columns for main layout */
          }

          .kpi-section {
              grid-column: 1 / -1; /* KPI row spans all columns */
          }

          .main-charts-grid {
               grid-template-columns: repeat(2, 1fr); /* Keep 2x2 for neatness */
               grid-template-rows: repeat(2, auto);
               gap: 30px; /* Consistent gap */
               grid-column: 1 / -1; /* Spans all 3 columns of the main grid */
          }

          /* Re-apply 2x2 grid placement for very large screens */
           .chart-grid-item.country-bar-chart-item {
               grid-column: 1 / 2; /* Top Left */
               grid-row: 1 / 2;
           }

           .chart-grid-item.pie-chart-item {
               grid-column: 2 / 3; /* Top Right */
               grid-row: 1 / 2;
           }

            .chart-grid-item.organizational-chart-item {
                grid-column: 1 / 2; /* Bottom Left */
                grid-row: 2 / 3;
            }

            .chart-grid-item.thematic-chart-item {
                grid-column: 2 / 3; /* Bottom Right */
                grid-row: 2 / 3;
            }
     }
}


/* --- Section Styling (for KPI section) --- */
.kpi-section {
    background-color: #ffffff;
    padding: 25px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    display: flex;
    flex-direction: column;
    gap: 20px;
}

/* --- Chart Grid Item Styling (Applies to all chart cards) --- */
.chart-grid-item {
    background-color: #ffffff; /* White background for chart items */
    padding: 0 25px 25px 25px; /* Adjusted padding: 0 top, 25px right/bottom/left */
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    display: flex;
    flex-direction: column;
    /* Adjusted gap to control space between title and chart */
    gap: 15px; /* Space between title and chart content */
    min-height: 350px; /* Ensure a minimum height for chart containers */
    width: 100%; /* Ensure items take full width of their grid cell */
    box-sizing: border-box; /* Include padding and border in width */
}

/* Style for the h3 chart titles */
.chart-grid-item .chart-title-h3 {
    font-size: 1.5rem; /* Increased font size */
    font-weight: 900; /* Extra extra bold */
    color: #000; /* Pure black color */
    margin: 0 -25px 0 -25px; /* Negative margins to span full card width */
    padding: 15px 25px; /* Padding within the title background area */
    border-bottom: 4px solid #ced4da; /* Thicker solid separator line */
    background-color: #f8f9fa; /* Added a light background color */
    text-align: center; /* Center align the text */
    text-transform: uppercase; /* Uppercase the text */
    letter-spacing: 1px; /* Increased letter spacing */
    border-top-left-radius: 8px; /* Match card border radius */
    border-top-right-radius: 8px;
    flex-shrink: 0; /* Prevent title from shrinking */
}


/* Basic styles for status badge (can be removed if using a global style) */
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
