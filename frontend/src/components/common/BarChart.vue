<template>
  <div class="bar-chart-container">
    <div ref="chartRef" class="bar-chart"></div>
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
    default: () => [] // Default to an empty array
  },
  dataKey: { // Key for the data labels (e.g., 'country_name', 'org_unit_name')
    type: String,
    required: true
  },
  valueKey: { // Key for the data values (e.g., 'total_pag_value', 'project_count')
    type: String,
    required: true
  },
  title: { // Optional chart title
    type: String,
    default: ''
  },
  orientation: { // New prop to specify chart orientation ('vertical' or 'horizontal')
      type: String,
      default: 'vertical', // Default to vertical
      validator: (value) => ['vertical', 'horizontal'].includes(value) // Validate prop value
  },
  topN: { // Optional prop to limit to Top N items
      type: Number,
      default: null // Default to showing all data
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
      // Use 'light' theme if available in ECharts, or remove theme option
      myChart = echarts.init(chartRef.value, 'light'); // Assuming a 'light' theme is available or registered
      console.log("BarChart: ECharts instance initialized.");
      // Add resize listener only after successful initialization
      window.addEventListener('resize', resizeChart);
    } catch (e) {
      console.error("BarChart: Failed to initialize ECharts:", e);
      myChart = null; // Ensure myChart is null if initialization fails
    }
  } else if (!chartRef.value) {
     console.warn("BarChart: Cannot initialize ECharts, chartRef.value is null.");
  }
};

// Function to dispose the ECharts instance
const disposeChart = () => {
  if (myChart) {
    try {
      myChart.dispose();
      console.log("BarChart: ECharts instance disposed.");
    } catch (e) {
       console.error("BarChart: Failed to dispose ECharts:", e);
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
       console.warn("BarChart: myChart instance is null. Cannot update chart.");
       return;
   }

  // Ensure chartData is an array and has data
  if (!props.chartData || props.chartData.length === 0) {
    // Clear chart if no data
    myChart.clear();
    console.warn("BarChart: No data provided to render.");
    return;
  }

  // Sort data descending by value
  const sortedData = [...props.chartData].sort((a, b) => b[props.valueKey] - a[props.valueKey]);

  // Apply Top N limit if specified
  const displayData = props.topN !== null ? sortedData.slice(0, props.topN) : sortedData;

  // Reverse data for horizontal bar chart to have highest value at the top
  if (props.orientation === 'horizontal') {
      displayData.reverse();
  }


  const labels = displayData.map(item => item[props.dataKey]);
  const values = displayData.map(item => item[props.valueKey]);

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
      trigger: 'axis',
      axisPointer: {
        type: 'shadow' // Show shadow for axis pointer
      },
       formatter: (params) => {
           // Custom tooltip formatter for better readability
           const param = params[0];
           const value = param.value;
           // Find the original data item in the potentially filtered/sorted array
           const dataItem = displayData.find(item => item[props.dataKey] === param.name);


           let formattedValue = value;
           // Attempt to format currency if valueKey suggests it (basic heuristic)
           if (props.valueKey.toLowerCase().includes('value') || props.valueKey.toLowerCase().includes('amount')) {
               try {
                    // Use Intl.NumberFormat for currency formatting (adjust locale/currency as needed)
                   formattedValue = new Intl.NumberFormat('en-KE', { style: 'currency', currency: 'KSh', minimumFractionDigits: 0, maximumFractionDigits: 2 }).format(value);
               } catch (e) {
                   console.error("Tooltip currency formatting error:", e);
                   // Fallback to number formatting if currency formatting fails
                   formattedValue = new Intl.NumberFormat('en-US').format(value);
               }
           } else {
               // Default to number formatting
               formattedValue = new Intl.NumberFormat('en-US').format(value);
           }


           return `${param.name}<br/>${param.marker}${param.seriesName}: <strong>${formattedValue}</strong>`;
       }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: props.orientation === 'vertical' ? '15%' : '3%', // More space at bottom for vertical labels
      top: props.orientation === 'horizontal' ? '10%' : '15%', // More space at top for horizontal title
      containLabel: true // Ensure labels are fully displayed
    },
    xAxis: {
      type: props.orientation === 'vertical' ? 'category' : 'value', // Category for vertical, value for horizontal
      data: props.orientation === 'vertical' ? labels : null, // Labels on x for vertical
       axisLabel: {
        interval: 0, // Show all labels
        rotate: props.orientation === 'vertical' ? 60 : 0, // Rotate labels for vertical
        fontSize: 10, // Smaller font size for labels
        align: props.orientation === 'vertical' ? 'right' : 'center' // Align labels
      },
       axisTick: {
           alignWithLabel: true
       }
    },
    yAxis: {
      type: props.orientation === 'vertical' ? 'value' : 'category', // Value for vertical, category for horizontal
      data: props.orientation === 'horizontal' ? labels : null, // Labels on y for horizontal
      axisLabel: {
          // Optional: format y-axis labels for large numbers (applies to vertical)
           formatter: (value) => {
               if (props.orientation === 'vertical') { // Only format value axis
                   if (value >= 1000000000) { // Billions
                        return (value / 1000000000).toFixed(1) + 'B';
                   } else if (value >= 1000000) { // Millions
                       return (value / 1000000).toFixed(1) + 'M';
                   } else if (value >= 1000) { // Thousands
                       return (value / 1000).toFixed(1) + 'k';
                   }
                   return value;
               } else { // For horizontal, this is the category axis
                   return value; // No formatting needed for category labels
               }
           },
            fontSize: 10 // Smaller font size for labels
      }
    },
    series: [
      {
        name: props.title || 'Value', // Series name for tooltip
        type: 'bar',
        data: values,
        itemStyle: {
            color: '#007bff' // Bar color (primary app color)
        },
         // Optional: Add value labels on top of bars
         label: {
             show: false, // Set to true to show labels if space allows
             position: props.orientation === 'vertical' ? 'top' : 'right', // Position labels based on orientation
             formatter: (params) => {
                 // Format label value similarly to tooltip
                 const value = params.value;
                 let formattedValue = value;
                  if (props.valueKey.toLowerCase().includes('value') || props.valueKey.toLowerCase().includes('amount')) {
                      try {
                           formattedValue = new Intl.NumberFormat('en-KE', { style: 'currency', currency: 'KSh', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(value); // No decimals for label
                      } catch (e) {
                          formattedValue = new Intl.NumberFormat('en-US').format(value);
                      }
                  } else {
                      formattedValue = new Intl.NumberFormat('en-US').format(value);
                  }
                  return formattedValue;
             },
             fontSize: 8 // Even smaller font size for labels to fit
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

// Watch for changes in chartData, dataKey, valueKey, orientation, or topN props and re-render the chart
watch(() => [props.chartData, props.dataKey, props.valueKey, props.orientation, props.topN], ([newData, newDataKey, newValueKey, newOrientation, newTopN], [oldData, oldDataKey, oldValueKey, oldOrientation, oldTopN]) => {
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
.bar-chart-container {
  width: 100%;
  height: 400px; /* Set a default height for the chart container */
  /* You might adjust this height or make it responsive */
}

.bar-chart {
  width: 100%;
  height: 100%;
}
</style>
