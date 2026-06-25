<template>
  <div class="chart-container" :style="{ height: height + 'px' }">
    <Doughnut v-if="ready" :data="chartData" :options="mergedOptions" />
    <LoadingSpinner v-else size="sm" />
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import LoadingSpinner from '../shared/LoadingSpinner.vue'

ChartJS.register(ArcElement, Tooltip, Legend)

const props = defineProps({
  labels: { type: Array, default: () => [] },
  datasets: { type: Array, default: () => [] },
  height: { type: Number, default: 260 },
  options: { type: Object, default: () => ({}) }
})

const ready = ref(false)
onMounted(() => { ready.value = true })

const defaultOptions = {
  responsive: true,
  maintainAspectRatio: false,
  animation: {
    animateScale: true,
    animateRotate: true,
    duration: 800,
    easing: 'easeOutQuart'
  },
  cutout: '60%',
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        padding: 16,
        usePointStyle: true,
        pointStyleWidth: 8,
        font: { family: 'Inter', size: 12 },
        color: '#6e6e73'
      }
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
  }
}

const mergedOptions = computed(() => ({
  ...defaultOptions,
  ...props.options,
  plugins: { ...defaultOptions.plugins, ...(props.options.plugins || {}) }
}))

const chartColors = [
  'rgba(0,113,227,0.8)',
  'rgba(52,199,89,0.8)',
  'rgba(255,159,10,0.8)',
  'rgba(255,59,48,0.8)',
  'rgba(90,200,250,0.8)',
  'rgba(175,82,222,0.8)',
  'rgba(255,55,95,0.8)',
  'rgba(100,210,190,0.8)'
]

const chartData = computed(() => ({
  labels: props.labels,
  datasets: props.datasets.map((ds, i) => ({
    ...ds,
    backgroundColor: ds.backgroundColor || chartColors,
    borderColor: '#ffffff',
    borderWidth: 2,
    hoverBorderWidth: 3
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
