<template>
  <div class="pie-chart-container">
    <div ref="chartRef" class="pie-chart"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick, onUnmounted } from 'vue';
import * as echarts from 'echarts'; // Import ECharts library

// Define component props
const props = defineProps({
  chartData: {
    type: Array,
    required: true,
    default: () => [] // Default to an empty array of { name, value } objects
  },
  title: { // Optional chart title
    type: String,
    default: ''
  },
  legendPosition: { // Position of the legend ('top', 'bottom', 'left', 'right')
      type: String,
      default: 'bottom',
      validator: (value) => ['top', 'bottom', 'left', 'right'].includes(value)
  },
  colorPalette: { // Optional custom color palette
      type: Array,
      default: () => [] // Default to empty array, ECharts will use its default palette
  },
  showLegend: { // New prop to control legend visibility
      type: Boolean,
      default: true // Default to showing the legend
  }
});

// Reactive reference to the chart container div
const chartRef = ref(null);
// Reactive reference to the ECharts instance
let myChart = null;

// Function to initialize the ECharts instance
const initChart = () => {
  // Only initialize if the DOM element exists and the chart hasn't been initialized yet
  if (chartRef.value && !myChart) {
    try {
      // Initialize ECharts instance on the DOM element
      // Use 'light' theme if available, or remove theme option
      myChart = echarts.init(chartRef.value, 'light'); // Assuming a 'light' theme is available or registered
      console.log("PieChart: ECharts instance initialized.");
      // Add resize listener only after successful initialization
      window.addEventListener('resize', resizeChart);
    } catch (e) {
      console.error("PieChart: Failed to initialize ECharts:", e);
      myChart = null; // Ensure myChart is null if initialization fails
    }
  } else if (!chartRef.value) {
     console.warn("PieChart: Cannot initialize ECharts, chartRef.value is null.");
  }
};

// Function to dispose the ECharts instance
const disposeChart = () => {
  if (myChart) {
    try {
      myChart.dispose();
      console.log("PieChart: ECharts instance disposed.");
    } catch (e) {
       console.error("PieChart: Failed to dispose ECharts:", e);
    } finally {
       myChart = null; // Always set to null after attempting disposal
    }
  }
  // Remove resize listener when disposing
  window.removeEventListener('resize', resizeChart);
};


// Function to render or update the chart options
const updateChart = () => {
   // Ensure chart instance exists before setting options
   if (!myChart) {
       console.warn("PieChart: myChart instance is null. Cannot update chart.");
       return;
   }

  // Ensure chartData is an array and has data
  if (!props.chartData || props.chartData.length === 0) {
    // Clear chart if no data
    myChart.clear();
    console.warn("PieChart: No data provided to render.");
    return;
  }

  // Define ECharts options
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
      trigger: 'item', // Trigger on hovering over a pie slice
       formatter: (params) => {
           // Custom tooltip formatter
           const value = params.value;
           let formattedValue = value;
           // Attempt to format currency (basic heuristic)
           if (params.seriesName && params.seriesName.toLowerCase().includes('value')) { // Check series name for 'Value'
                try {
                     formattedValue = new Intl.NumberFormat('en-KE', { style: 'currency', currency: 'KSh', minimumFractionDigits: 0, maximumFractionDigits: 2 }).format(value);
                } catch (e) {
                    formattedValue = new Intl.NumberFormat('en-US').format(value);
                }
           } else {
               formattedValue = new Intl.NumberFormat('en-US').format(value);
           }

          return `${params.name}: ${formattedValue} (${params.percent}%)`;
       }
    },
    // Conditionally include the legend configuration
    legend: props.showLegend ? {
      orient: props.legendPosition === 'left' || props.legendPosition === 'right' ? 'vertical' : 'horizontal',
      left: props.legendPosition === 'left' || props.legendPosition === 'right' ? props.legendPosition : 'center',
      top: props.legendPosition === 'top' || props.legendPosition === 'bottom' ? props.legendPosition : 'center',
      bottom: props.legendPosition === 'bottom' ? '0' : 'auto', // Adjust bottom position if legend is at the bottom
    } : null, // Set to null if legend should not be shown
    series: [
      {
        name: props.title || 'Value', // Series name for tooltip
        type: 'pie',
        radius: '50%', // Size of the pie chart
        center: ['50%', '50%'], // Center position of the pie chart
        data: props.chartData, // The data array { name, value }
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        // Use custom color palette if provided
        color: props.colorPalette.length > 0 ? props.colorPalette : undefined,
         label: {
             show: true, // Show labels
             formatter: '{b}: {d}%', // Format label to show name and percentage
             fontSize: 10
         },
         labelLine: {
             show: true // Show lines connecting labels to slices
         }
      }
    ]
  };

  // Set the options to render the chart
  myChart.setOption(options);
};

// Function to resize the chart
const resizeChart = () => {
  // Only resize if the chart instance exists and the container has dimensions
  if (myChart && chartRef.value && chartRef.value.offsetWidth > 0 && chartRef.value.offsetHeight > 0) {
    myChart.resize();
  }
};

// Initialize chart on component mount
onMounted(() => {
  // Use nextTick to ensure the DOM element is available
  nextTick(() => {
    initChart(); // Initialize chart after DOM is ready
    updateChart(); // Then update with data
    // Explicitly call resize after initial update within nextTick
    nextTick(() => {
        resizeChart();
    });
  });
});

// Watch for changes in chartData, title, legendPosition, colorPalette, or showLegend props and re-render the chart
watch(() => [props.chartData, props.title, props.legendPosition, props.colorPalette, props.showLegend], ([newData, newTitle, newLegendPosition, newColorPalette, newShowLegend], [oldData, oldTitle, oldLegendPosition, oldColorPalette, oldShowLegend]) => {
    // Dispose the old chart instance before potentially creating a new one
    disposeChart();

    // Use nextTick to ensure DOM updates are complete before re-initializing/updating
    nextTick(() => {
      initChart(); // Re-initialize if disposed
      updateChart(); // Update chart with new data
      // Explicitly call resize after update within nextTick
      nextTick(() => {
          resizeChart();
      });
    });
}, { deep: true }); // Use deep: true to watch for changes within the array/objects

// Clean up resize listener and chart instance on component unmount
onUnmounted(() => {
  disposeChart(); // Dispose chart when component is unmounted
});

</script>

<style scoped>
.pie-chart-container {
  width: 100%;
  height: 400px; /* Set a default height for the chart container */
  /* You might adjust this height or make it responsive */
}

.pie-chart {
  width: 100%;
  height: 100%;
}
</style>
