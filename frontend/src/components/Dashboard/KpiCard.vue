<template>
  <div class="kpi-card">
    <div v-if="indicatorColor" class="kpi-indicator" :style="{ backgroundColor: indicatorColor }"></div>

    <div class="kpi-content">
      <div class="kpi-title">{{ title }}</div>
      <div class="kpi-value">
        <span v-if="format === 'currency'" class="currency-symbol">{{ currency }}</span>
        <span>{{ formattedValuePart }}</span> </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [Number, String, null], // Allow number, string, or null
    default: null
  },
  indicatorColor: { // New prop for a subtle color indicator
    type: String,
    default: '#007bff' // Default indicator color (primary app color)
  },
  format: { // Optional prop for value formatting ('number', 'currency', etc.)
    type: String,
    default: 'number' // Default format
  },
  currency: { // Optional prop for currency symbol if format is 'currency'
    type: String,
    default: 'USD' // Default currency code for Intl.NumberFormat
  }
});

// Computed property to format just the numeric part of the value
const formattedValuePart = computed(() => {
  if (props.value === null || props.value === undefined) {
    return 'N/A';
  }

  const numericValue = typeof props.value === 'string' ? parseFloat(props.value) : props.value;

  if (isNaN(numericValue)) {
      return 'Invalid Value';
  }

  // Use Intl.NumberFormat for robust formatting, without the currency symbol
  try {
    switch (props.format) {
      case 'currency':
        // Format as a number, then prepend currency symbol in the template
        // Use 'en-KE' locale for Kenyan Shilling formatting style
        return new Intl.NumberFormat('en-KE', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(numericValue);
      case 'number':
        return new Intl.NumberFormat('en-US').format(numericValue);
      case 'percentage':
          return `${new Intl.NumberFormat('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 2 }).format(numericValue)}`;
      default:
        return String(numericValue); // Return raw numeric value as string if format is unknown
    }
  } catch (e) {
      console.error("Formatting error:", e);
      return String(numericValue); // Fallback to raw numeric value
  }
});

</script>

<style scoped>
.kpi-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 15px 20px; /* Adjusted vertical padding slightly */
  display: flex;
  align-items: center;
  gap: 15px;
  min-width: 200px; /* Ensure a minimum width */
  flex-grow: 1; /* Allow cards to grow */
  flex-basis: 0; /* Allow flex items to shrink below content size */
  transition: transform 0.2s ease-in-out; /* Subtle hover effect */
   position: relative; /* Needed for absolute positioning of indicator */
   overflow: hidden; /* Hide indicator overflow */
}

.kpi-card:hover {
    transform: translateY(-3px);
}

.kpi-indicator {
    width: 6px; /* Slightly reduced indicator width */
    height: 100%; /* Full height of the card */
    position: absolute;
    top: 0;
    left: 0;
    border-top-left-radius: 8px; /* Match card border radius */
    border-bottom-left-radius: 8px; /* Match card border radius */
}


.kpi-content {
  display: flex;
  flex-direction: column;
  /* Adjust padding-left based on new indicator width */
   padding-left: 10px; /* Adjusted padding left */
   flex-grow: 1; /* Allow content to take available space */
   min-width: 0; /* Allow content to shrink */
   padding-right: 5px; /* Add a little padding on the right */
}

.kpi-title {
  font-size: 0.85rem; /* Slightly decreased title font size */
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
   margin-bottom: 3px; /* Reduced space between title and value */
}

.kpi-value {
  font-size: 1.3rem; /* Main font size for the number */
  font-weight: 700;
  color: #333;
  word-break: break-word; /* Allow long words/numbers to break */
  overflow-wrap: break-word; /* Another property for breaking words */
  line-height: 1.2; /* Adjust line height if needed for wrapping */
  /* margin-bottom: 5px; Removed as margin is on title */

  /* Ensure the value part is displayed inline or inline-block */
  display: inline-block;
  vertical-align: bottom; /* Align with currency symbol */
}

.kpi-value .currency-symbol {
    font-size: 0.8em; /* Make the currency symbol smaller relative to the value */
    font-weight: 500; /* Slightly less bold */
    margin-right: 2px; /* Small space between symbol and number */
    vertical-align: bottom; /* Align with the number */
    display: inline-block; /* Ensure it behaves correctly with margin/padding */
}
</style>
