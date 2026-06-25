<template>
  <section class="card--glass animate-slide-up">
    <div class="card__header">
      <h2 class="card__title">课程成绩统计</h2>
      <div class="stats-filters">
        <input v-model="filterCode" placeholder="课程编号" class="filter-input" />
        <input v-model="filterName" placeholder="课程名称" class="filter-input" />
        <button class="btn-filter" @click="loadStats">筛选</button>
      </div>
    </div>
    <div class="card__body">
      <LoadingSpinner v-if="loading" text="加载统计数据..." />
      <template v-else-if="courseStats.length">
        <!-- Charts Row -->
        <div class="charts-grid">
          <div class="chart-card">
            <h4 class="chart-title">成绩分布</h4>
            <BarChart :labels="chartLabels" :datasets="[chartDataset]" :height="240" />
          </div>
          <div class="chart-card">
            <h4 class="chart-title">及格率概览</h4>
            <DoughnutChart :labels="['及格 (≥60)', '不及格 (<60)']"
              :datasets="[passRateDataset]" :height="240" />
          </div>
        </div>
        <!-- Stats Grid -->
        <div class="stats-grid">
          <div v-for="s in courseStats" :key="s.id" class="stat-item">
            <div class="stat-item__name">{{ s.name }}</div>
            <div class="stat-item__code">{{ s.course_code }}</div>
            <div class="stat-item__values">
              <div class="stat-val"><span class="stat-val__label">平均分</span><strong>{{ s.avg_grade || '-' }}</strong></div>
              <div class="stat-val"><span class="stat-val__label">及格率</span><strong :class="s.pass_rate >= 80 ? 'is-good' : ''">{{ s.pass_rate }}%</strong></div>
              <div class="stat-val"><span class="stat-val__label">优秀率</span><strong>{{ s.excellent_rate }}%</strong></div>
              <div class="stat-val"><span class="stat-val__label">人数</span><strong>{{ s.enrolled_count }}</strong></div>
            </div>
          </div>
        </div>
      </template>
      <EmptyState v-else icon="📊" title="暂无数据" description="尚未有成绩数据或课程为空" />
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import BarChart from '../../components/charts/BarChart.vue'
import DoughnutChart from '../../components/charts/DoughnutChart.vue'
import EmptyState from '../../components/shared/EmptyState.vue'
import LoadingSpinner from '../../components/shared/LoadingSpinner.vue'

const API = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api'
const courseStats = ref([]); const loading = ref(false)
const filterCode = ref(''); const filterName = ref('')

const chartLabels = computed(() => courseStats.value.map(s => s.course_code || s.name?.slice(0, 8)))
const chartDataset = computed(() => ({
  label: '平均成绩', data: courseStats.value.map(s => parseFloat(s.avg_grade) || 0),
  backgroundColor: courseStats.value.map((_, i) =>
    ['rgba(0,113,227,0.7)', 'rgba(52,199,89,0.7)', 'rgba(255,159,10,0.7)', 'rgba(255,59,48,0.7)', 'rgba(90,200,250,0.7)'][i % 5])
}))

const passRateDataset = computed(() => {
  const pass = courseStats.value.reduce((sum, s) => sum + parseFloat(s.pass_rate || 0), 0) / Math.max(courseStats.value.length, 1)
  return { data: [pass, 100 - pass], backgroundColor: ['rgba(52,199,89,0.7)', 'rgba(255,59,48,0.3)'] }
})

async function loadStats() {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (filterCode.value) params.set('course_code', filterCode.value)
    if (filterName.value) params.set('course_name', filterName.value)
    const qs = params.toString()
    const r = await fetch(`${API}/statistics/overview${qs ? '?' + qs : ''}`, { credentials: 'include' })
    const data = await r.json()
    courseStats.value = data.course_avg || []
  } catch (e) { console.error(e) } finally { loading.value = false }
}

onMounted(loadStats)
defineExpose({ load: loadStats })
</script>

<style scoped>
.card--glass { background: var(--color-bg-glass); backdrop-filter: var(--blur-glass); -webkit-backdrop-filter: var(--blur-glass); border: 1px solid var(--color-border); border-radius: var(--radius-xl); overflow: hidden; box-shadow: var(--shadow-sm); }
.card__header { display: flex; align-items: center; justify-content: space-between; padding: var(--space-5) var(--space-6) var(--space-3); flex-wrap: wrap; gap: var(--space-3); }
.card__title { font-size: var(--text-lg); font-weight: var(--weight-bold); }
.card__body { padding: var(--space-6); }
.stats-filters { display: flex; gap: var(--space-2); }
.filter-input { padding: var(--space-1) var(--space-3); border: 1px solid var(--color-border); border-radius: var(--radius-md); font-size: var(--text-xs); width: 120px; outline: none; }
.filter-input:focus { border-color: var(--color-accent); }
.btn-filter { padding: var(--space-1) var(--space-3); background: var(--color-accent); color: white; border-radius: var(--radius-md); font-size: var(--text-xs); font-weight: var(--weight-medium); }
.charts-grid { display: grid; grid-template-columns: 2fr 1fr; gap: var(--space-6); margin-bottom: var(--space-6); }
@media (max-width: 768px) { .charts-grid { grid-template-columns: 1fr; } }
.chart-card { background: var(--color-bg-secondary); border-radius: var(--radius-lg); border: 1px solid var(--color-border); padding: var(--space-4); }
.chart-title { font-size: var(--text-sm); font-weight: var(--weight-semibold); color: var(--color-text-secondary); margin-bottom: var(--space-2); }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: var(--space-3); }
.stat-item { background: var(--color-bg-secondary); border: 1px solid var(--color-border); border-radius: var(--radius-lg); padding: var(--space-4); }
.stat-item__name { font-size: var(--text-md); font-weight: var(--weight-semibold); margin-bottom: 2px; }
.stat-item__code { font-size: var(--text-xs); color: var(--color-accent); font-weight: var(--weight-bold); margin-bottom: var(--space-3); }
.stat-item__values { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-2); }
.stat-val { display: flex; flex-direction: column; }
.stat-val__label { font-size: 10px; color: var(--color-text-tertiary); text-transform: uppercase; letter-spacing: 0.04em; }
.stat-val strong { font-size: var(--text-lg); font-weight: var(--weight-bold); color: var(--color-text-primary); }
.stat-val strong.is-good { color: var(--color-success); }
</style>
