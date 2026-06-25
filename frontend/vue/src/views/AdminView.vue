<template>
  <div class="admin-page">
    <AdminDashboard :stats="stats" :health="health" />

    <!-- macOS-Style Tab Bar -->
    <nav class="admin-tabs">
      <button v-for="tab in tabs" :key="tab.id" class="admin-tab" :class="{ active: activeTab === tab.id }"
        @click="activeTab = tab.id">
        <span class="admin-tab__icon">{{ tab.icon }}</span>
        <span class="admin-tab__label">{{ tab.label }}</span>
      </button>
    </nav>

    <!-- Tab Content with Transitions -->
    <Transition name="tab-fade" mode="out-in">
      <AdminStudents v-if="activeTab === 'students'" :key="'students'" @changed="refreshAll" ref="studentsRef" />
      <AdminTeachers v-else-if="activeTab === 'teachers'" :key="'teachers'" @changed="refreshAll" ref="teachersRef" />
      <AdminCourses v-else-if="activeTab === 'courses'" :key="'courses'" :teachers="teachers" @changed="refreshAll" ref="coursesRef" />
      <AdminEnrollments v-else-if="activeTab === 'enrollments'" :key="'enrollments'" :students="students" :courses="courses" @changed="refreshAll" ref="enrollmentsRef" />
      <AdminImportExport v-else-if="activeTab === 'import'" :key="'import'" :courses="courses" @changed="refreshAll" />
      <AdminStatistics v-else-if="activeTab === 'stats'" :key="'stats'" ref="statsRef" />
      <AdminMajorPlans v-else-if="activeTab === 'plans'" :key="'plans'" :all-courses="courses" @changed="refreshAll" ref="plansRef" />
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AdminDashboard from './admin/AdminDashboard.vue'
import AdminStudents from './admin/AdminStudents.vue'
import AdminTeachers from './admin/AdminTeachers.vue'
import AdminCourses from './admin/AdminCourses.vue'
import AdminEnrollments from './admin/AdminEnrollments.vue'
import AdminImportExport from './admin/AdminImportExport.vue'
import AdminStatistics from './admin/AdminStatistics.vue'
import AdminMajorPlans from './admin/AdminMajorPlans.vue'

const API = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api'

const activeTab = ref('students')
const health = ref({ db: false })
const stats = ref(null)
const students = ref([])
const teachers = ref([])
const courses = ref([])

const tabs = [
  { id: 'students', label: '学生', icon: '👥' },
  { id: 'teachers', label: '教师', icon: '👨‍🏫' },
  { id: 'courses', label: '课程', icon: '📚' },
  { id: 'enrollments', label: '选课', icon: '📝' },
  { id: 'import', label: '导入导出', icon: '📦' },
  { id: 'stats', label: '统计', icon: '📊' },
  { id: 'plans', label: '培养计划', icon: '🎓' },
]

async function fetchJSON(path) {
  const r = await fetch(`${API}${path}`, { credentials: 'include' })
  return r.json()
}

async function refreshAll() {
  try {
    const [s, statData] = await Promise.all([
      Promise.all([
        fetchJSON('/students').catch(() => []),
        fetchJSON('/teachers').catch(() => []),
        fetchJSON('/courses').catch(() => []),
      ]),
      fetchJSON('/statistics/overview').catch(() => null)
    ])
    students.value = s[0]; teachers.value = s[1]; courses.value = s[2]
    stats.value = statData
    health.value = { db: true }
  } catch { health.value = { db: false } }
}

onMounted(async () => {
  try { health.value = await fetchJSON('/health') } catch { health.value = { db: false } }
  await refreshAll()
})
</script>

<style scoped>
.admin-page {
  max-width: var(--content-max-width);
  margin: 0 auto;
  padding: var(--space-6);
}

/* Tabs — macOS pill style */
.admin-tabs {
  display: flex;
  gap: var(--space-1);
  margin-bottom: var(--space-6);
  padding: var(--space-1);
  background: var(--color-bg-glass);
  backdrop-filter: var(--blur-glass);
  -webkit-backdrop-filter: var(--blur-glass);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  position: sticky;
  top: calc(var(--header-height) + var(--space-6));
  z-index: 50;
}
.admin-tab {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  color: var(--color-text-secondary);
  transition: all var(--duration-fast) var(--ease-default);
  white-space: nowrap;
  flex-shrink: 0;
}
.admin-tab.active {
  background: var(--color-bg-elevated);
  color: var(--color-text-primary);
  font-weight: var(--weight-semibold);
  box-shadow: var(--shadow-sm);
}
.admin-tab:hover:not(.active) {
  color: var(--color-text-primary);
  background: rgba(0, 0, 0, 0.03);
}
.admin-tab__icon { font-size: var(--text-lg); }
.admin-tab__label { font-size: var(--text-sm); }

@media (max-width: 640px) {
  .admin-tab__label { display: none; }
  .admin-tab { padding: var(--space-2) var(--space-3); }
}
</style>
