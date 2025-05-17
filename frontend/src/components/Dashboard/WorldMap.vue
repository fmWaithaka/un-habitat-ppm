<template>
  <div class="world-map-container">
    <div ref="mapRef" class="world-map"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick, onUnmounted } from 'vue';
import * as echarts from 'echarts'; // Import ECharts library
// You might need to import the world map GeoJSON data.
// ECharts provides a world.js or world.json file.
// The exact import path depends on how ECharts is bundled/installed.
// Example (might vary based on your setup):
// import 'echarts/map/js/world.js';
// Or if using a build that includes maps:
// echarts.registerMap('world', require('echarts/map/json/world.json'));

// Define component props
const props = defineProps({
  mapData: {
    type: Array,
    required: true,
    default: () => [] // Default to an empty array
  },
  dataKey: { // Key for the country name (e.g., 'country_name')
    type: String,
    required: true
  },
  valueKey: { // Key for the data value (e.g., 'total_pag_value', 'project_count')
    type: String,
    required: true
  },
  title: { // Optional map title
    type: String,
    default: 'World Map'
  }
});

// Reactive reference to the map container div
const mapRef = ref(null);
// Reactive reference to the ECharts instance
let myMapChart = null;

// Helper function to filter data for mappable countries
const getMappableData = (data) => {
  // Define patterns to exclude (case-insensitive)
  const excludePatterns = [
    /GLOBAL/i,
    /Regional/i,
    /,/ // Exclude entries containing commas (assuming multi-country)
  ];

  return data.filter(item => {
    const countryName = item[props.dataKey];
    if (!countryName) return false; // Exclude items with no country name
    // Check if the country name matches any exclusion pattern
    return !excludePatterns.some(pattern => pattern.test(countryName));
  }).map(item => ({
      // Map to ECharts required format: { name: 'Country Name', value: numericValue }
      name: item[props.dataKey],
      value: item[props.valueKey]
  }));
};


// Function to initialize the ECharts map instance
const initMapChart = () => {
  // Only initialize if the DOM element exists and the map hasn't been initialized yet
  if (mapRef.value && !myMapChart) {
    try {
      // Initialize ECharts instance on the DOM element
      // Use 'light' theme if available, or remove theme option
      myMapChart = echarts.init(mapRef.value, 'light'); // Assuming a 'light' theme is available or registered
      console.log("WorldMap: ECharts instance initialized.");
      // Add resize listener only after successful initialization
      window.addEventListener('resize', resizeMapChart);
    } catch (e) {
      console.error("WorldMap: Failed to initialize ECharts:", e);
      myMapChart = null; // Ensure myMapChart is null if initialization fails
    }
  } else if (!mapRef.value) {
     console.warn("WorldMap: Cannot initialize ECharts, mapRef.value is null.");
  }
};

// Function to dispose the ECharts map instance
const disposeMapChart = () => {
  if (myMapChart) {
    try {
      myMapChart.dispose();
      console.log("WorldMap: ECharts instance disposed.");
    } catch (e) {
       console.error("WorldMap: Failed to dispose ECharts:", e);
    } finally {
       myMapChart = null; // Always set to null after attempting disposal
    }
  }
  // Remove resize listener when disposing
  window.removeEventListener('resize', resizeMapChart);
};


// Function to render or update the map options
const updateMapChart = () => {
   // Ensure map instance exists before setting options
   if (!myMapChart) {
       console.warn("WorldMap: myMapChart instance is null. Cannot update map.");
       return;
   }

  // Filter and format data for the map
  const mappableData = getMappableData(props.mapData);

  // Define ECharts map options
  const options = {
    title: {
      text: props.title,
      left: 'center',
      textStyle: {
          fontSize: 16,
          color: '#333'
      }
    },
    tooltip: {
      trigger: 'item', // Trigger on hovering over a map item
      formatter: (params) => {
          // Custom tooltip formatter
          if (params.value) {
              let formattedValue = params.value;
               // Attempt to format currency if valueKey suggests it
               if (props.valueKey.toLowerCase().includes('value') || props.valueKey.toLowerCase().includes('amount')) {
                   try {
                        formattedValue = new Intl.NumberFormat('en-KE', { style: 'currency', currency: 'KSh', minimumFractionDigits: 0, maximumFractionDigits: 2 }).format(params.value);
                   } catch (e) {
                       console.error("Tooltip currency formatting error:", e);
                       formattedValue = new Intl.NumberFormat('en-US').format(params.value);
                   }
               } else {
                   formattedValue = new Intl.NumberFormat('en-US').format(params.value);
               }
              return `${params.name}: <strong>${formattedValue}</strong>`;
          } else {
              return `${params.name}: No Data`;
          }
      }
    },
    visualMap: { // Configuration for coloring countries based on value
      min: 0, // Minimum value in the data
      max: Math.max(...mappableData.map(item => item.value || 0)), // Maximum value in the data
      left: 'left',
      top: 'bottom',
      text: ['High', 'Low'], // Text for the visual map
      calculable: true, // Allow dragging the visual map handle
      inRange: {
        color: ['#e0f3db', '#a8ddb5', '#7bccc4', '#4eb3d3', '#2b8cbe', '#08589e'] // Color range (adjust to your theme)
      }
    },
    series: [
      {
        name: props.title || 'Value', // Series name
        type: 'map',
        map: 'world', // Use the registered world map
        roam: true, // Allow zooming and panning
        emphasis: { // Styles when hovering over a country
          label: {
            show: true // Show country name on hover
          }
        },
        data: mappableData // The filtered and formatted data
      }
    ]
  };

  // Set the options to render the map
  myMapChart.setOption(options);
};

// Function to resize the map chart
const resizeMapChart = () => {
  if (myMapChart) {
    myMapChart.resize();
  }
};

// Initialize map chart on component mount
onMounted(() => {
  // Use nextTick to ensure the DOM element is available
  nextTick(() => {
    initMapChart(); // Initialize map chart after DOM is ready
    updateMapChart(); // Then update with data
  });
});

// Watch for changes in mapData prop and re-render the map chart
watch(() => props.mapData, (newData, oldData) => {
    // Dispose the old map chart instance before potentially creating a new one
    disposeMapChart();

    // Use nextTick to ensure DOM updates are complete before re-initializing/updating
    nextTick(() => {
      initMapChart(); // Re-initialize if disposed
      updateMapChart(); // Update map chart with new data
    });
}, { deep: true }); // Use deep: true to watch for changes within the array/objects

// Clean up resize listener and map chart instance on component unmount
onUnmounted(() => {
  disposeMapChart(); // Dispose map chart when component is unmounted
});

</script>

<style scoped>
.world-map-container {
  width: 100%;
  height: 500px; /* Set a default height for the map container */
  /* Adjust height as needed, potentially make it responsive */
}

.world-map {
  width: 100%;
  height: 100%;
}
</style>
