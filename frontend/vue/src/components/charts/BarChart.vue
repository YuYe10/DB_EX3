<template>
  <div class="chart-container" :style="{ height: height + 'px' }">
    <Bar v-if="ready" :data="chartData" :options="mergedOptions" />
    <LoadingSpinner v-else size="sm" />
  </div>
</template>

<script setup>
import { computed, ref, watch, onMounted } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS, BarElement, CategoryScale, LinearScale,
  Tooltip, Legend, Filler
} from 'chart.js'
import LoadingSpinner from '../shared/LoadingSpinner.vue'

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend, Filler)

const props = defineProps({
  labels: { type: Array, default: () => [] },
  datasets: { type: Array, default: () => [] },
  height: { type: Number, default: 300 },
  options: { type: Object, default: () => ({}) }
})

const ready = ref(false)
onMounted(() => { ready.value = true })

const defaultOptions = {
  responsive: true,
  maintainAspectRatio: false,
  animation: {
    duration: 800,
    easing: 'easeOutQuart'
  },
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      backgroundColor: 'rgba(255,255,255,0.95)',
      titleColor: '#1d1d1f',
      bodyColor: '#6e6e73',
      borderColor: 'rgba(0,0,0,0.06)',
      borderWidth: 1,
      cornerRadius: 10,
      padding: 12,
      boxPadding: 6,
      titleFont: { family: 'Inter', weight: '600', size: 13 },
      bodyFont: { family: 'Inter', size: 12 }
    }
  },
  scales: {
    x: {
      grid: { display: false },
      ticks: { font: { family: 'Inter', size: 11 }, color: '#aeaeb2' }
    },
    y: {
      grid: { color: 'rgba(0,0,0,0.04)' },
      ticks: { font: { family: 'Inter', size: 11 }, color: '#aeaeb2', padding: 8 },
      beginAtZero: true
    }
  }
}

const mergedOptions = computed(() => {
  return { ...defaultOptions, ...props.options,
    plugins: { ...defaultOptions.plugins, ...(props.options.plugins || {}) },
    scales: { ...defaultOptions.scales, ...(props.options.scales || {}) }
  }
})

const chartData = computed(() => ({
  labels: props.labels,
  datasets: props.datasets.map(ds => ({
    ...ds,
    borderRadius: 6,
    borderSkipped: false,
    backgroundColor: ds.backgroundColor || 'rgba(0,113,227,0.7)',
    borderColor: ds.borderColor || 'rgba(0,113,227,1)',
    borderWidth: 0,
    hoverBackgroundColor: ds.hoverBackgroundColor || 'rgba(0,113,227,0.9)'
  }))
}))
</script>

<style scoped>
.chart-container {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-4);
}
</style>
