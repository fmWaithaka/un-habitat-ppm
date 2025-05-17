<template>
  <div class="kpi-card-row">
    <KpiCard
      v-for="(kpi, key) in kpis"
      :key="key"
      :title="kpi.title"
      :value="kpi.value"
      :iconText="kpi.iconText"
      :iconClass="kpi.iconClass"
      :format="kpi.format"
      :currency="kpi.currency"
    />
  </div>
</template>

<script setup>
import KpiCard from './KpiCard.vue'; // Import the KpiCard component

const props = defineProps({
  kpis: {
    type: [Object, null], // Expect an object where keys are KPI identifiers and values are KPI data
    default: () => ({}) // Default to an empty object
  }
});

</script>

<style scoped>
.kpi-card-row {
  display: flex;
  flex-wrap: wrap; /* Allow cards to wrap to the next line */
  gap: 20px; /* Space between KPI cards */
  justify-content: center; /* Center cards horizontally */
}

/* Adjust layout for smaller screens if needed */
@media (max-width: 767px) {
  .kpi-card-row {
    flex-direction: column; /* Stack cards vertically on small screens */
    align-items: stretch; /* Stretch cards to fill width */
  }
}
</style>
