<template>
  <section class="card--glass animate-slide-up">
    <div class="card__header">
      <h2 class="card__title">选课与成绩管理</h2>
      <span class="card__count" v-if="enrollments.length">{{ filteredEnrollments.length }}/{{ enrollments.length }}</span>
    </div>
    <!-- Create enrollment -->
    <form @submit.prevent="createEnrollment" class="inline-form">
      <select v-model="enrollForm.student_id" required class="form-input">
        <option value="">选择学生</option>
        <option v-for="s in students" :key="s.id" :value="s.id">{{ s.student_no }} {{ s.name }}</option>
      </select>
      <select v-model="enrollForm.course_id" required class="form-input">
        <option value="">选择课程</option>
        <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.course_code }} {{ c.name }}</option>
      </select>
      <button type="submit" class="btn-add" :disabled="creatingEnr">+ 添加选课</button>
    </form>
    <SearchFilter v-model="search" placeholder="搜索学生或课程..." class="card__search" />
    <div class="card__body" v-if="filteredEnrollments.length">
      <div v-for="e in filteredEnrollments" :key="e.id" class="item-row">
        <div class="item-row__main">
          <span class="item-badge">{{ e.student_no }}</span>
          <span class="item-name">{{ e.student_name }}</span>
          <span class="item-meta">→ {{ e.course_name }}</span>
          <span class="grade-chip" :class="gradeClass(e.final_grade)">
            {{ e.final_grade != null ? e.final_grade + '分' : '未评分' }}
          </span>
        </div>
        <div class="item-row__actions">
          <button class="btn-sm" @click="toggleGrade(e)">成绩</button>
          <button class="btn-sm btn-sm--danger" @click="confirmDelete(e)">退课</button>
        </div>
      </div>
      <!-- Inline Grade Editor -->
      <Transition name="collapse">
        <div v-if="gradingTarget" class="editor-panel">
          <GradeEditor :ordinary-score="gradingTarget.ordinary_score" :final-score="gradingTarget.final_score"
            :ordinary-weight="gradingTarget.course_ordinary_weight ?? 0.5"
            :final-weight="gradingTarget.course_final_weight ?? 0.5"
            @save="saveGrade" @cancel="gradingTarget = null" />
        </div>
      </Transition>
    </div>
    <EmptyState v-else icon="📝" title="暂无选课记录" />
    <ConfirmDialog :visible="deleteTarget != null" title="退课"
      :message="`确定要移除「${deleteTarget?.student_name}」的选课记录吗？`"
      icon="⚠️" confirm-text="确认退课" variant="danger"
      @confirm="doDelete" @cancel="deleteTarget = null" />
  </section>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import SearchFilter from '../../components/shared/SearchFilter.vue'
import EmptyState from '../../components/shared/EmptyState.vue'
import ConfirmDialog from '../../components/shared/ConfirmDialog.vue'
import GradeEditor from '../../components/shared/GradeEditor.vue'

const props = defineProps({
  students: { type: Array, default: () => [] },
  courses: { type: Array, default: () => [] }
})
const emit = defineEmits(['changed'])
const API = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api'
const enrollments = ref([]); const search = ref(''); const creatingEnr = ref(false)
const deleteTarget = ref(null); const gradingTarget = ref(null)
const enrollForm = reactive({ student_id: '', course_id: '' })

const filteredEnrollments = computed(() => {
  if (!search.value) return enrollments.value
  const kw = search.value.toLowerCase()
  return enrollments.value.filter(e => e.student_name?.toLowerCase().includes(kw) || e.course_name?.toLowerCase().includes(kw) || e.student_no?.toLowerCase().includes(kw))
})

function gradeClass(g) { if (g == null) return ''; if (g >= 90) return 'is-excellent'; if (g >= 60) return 'is-pass'; return 'is-fail' }

async function api(p, o = {}) {
  const r = await fetch(`${API}${p}`, { credentials: 'include', headers: o.headers || { 'Content-Type': 'application/json' }, ...o })
  if (!r.ok) { const d = await r.json().catch(() => ({})); throw new Error(d.message || '操作失败') }
  return r.json()
}
async function load() { try { enrollments.value = await api('/enrollments') } catch (e) { console.error(e) } }
async function createEnrollment() {
  creatingEnr.value = true
  try { await api('/enrollments', { method: 'POST', body: JSON.stringify(enrollForm) }); enrollForm.student_id = ''; enrollForm.course_id = ''; await load(); emit('changed') }
  catch (e) { alert(e.message) } finally { creatingEnr.value = false }
}
function toggleGrade(e) { gradingTarget.value = gradingTarget.value?.id === e.id ? null : e }
async function saveGrade(payload) {
  try { await api(`/enrollments/${gradingTarget.value.id}/grades`, { method: 'PUT', body: JSON.stringify(payload) }); gradingTarget.value = null; await load() }
  catch (e) { alert(e.message) }
}
function confirmDelete(e) { deleteTarget.value = e }
async function doDelete() {
  if (!deleteTarget.value) return
  try { await api(`/enrollments/${deleteTarget.value.id}`, { method: 'DELETE' }); deleteTarget.value = null; await load(); emit('changed') }
  catch (e) { alert(e.message) }
}
onMounted(load)
defineExpose({ load })
</script>

<style scoped>
.card--glass { background: var(--color-bg-glass); backdrop-filter: var(--blur-glass); -webkit-backdrop-filter: var(--blur-glass); border: 1px solid var(--color-border); border-radius: var(--radius-xl); overflow: hidden; box-shadow: var(--shadow-sm); }
.card__header { display: flex; align-items: center; justify-content: space-between; padding: var(--space-5) var(--space-6) var(--space-3); }
.card__title { font-size: var(--text-lg); font-weight: var(--weight-bold); }
.card__count { font-size: var(--text-xs); color: var(--color-text-tertiary); background: var(--color-bg-secondary); padding: var(--space-1) var(--space-2); border-radius: var(--radius-full); }
.card__search { padding: 0 var(--space-6) var(--space-3); }
.card__body { padding: 0 var(--space-6) var(--space-6); max-height: 500px; overflow-y: auto; }
.inline-form { display: flex; gap: var(--space-2); padding: 0 var(--space-6) var(--space-4); flex-wrap: wrap; align-items: center; }
.form-input { padding: var(--space-2) var(--space-3); border: 1px solid var(--color-border); border-radius: var(--radius-md); font-size: var(--text-sm); flex: 1; min-width: 120px; outline: none; transition: border-color var(--duration-fast); }
.form-input:focus { border-color: var(--color-accent); box-shadow: 0 0 0 3px var(--color-accent-light); }
.btn-add { padding: var(--space-2) var(--space-4); background: var(--color-accent); color: white; border-radius: var(--radius-md); font-size: var(--text-sm); font-weight: var(--weight-semibold); }
.btn-add:hover:not(:disabled) { background: var(--color-accent-hover); }
.item-row { display: flex; align-items: center; justify-content: space-between; padding: var(--space-3) var(--space-4); border-radius: var(--radius-md); border: 1px solid var(--color-border); margin-bottom: var(--space-2); transition: all var(--duration-fast); }
.item-row:hover { border-color: var(--color-border-strong); background: var(--color-bg-elevated); }
.item-row__main { display: flex; align-items: center; gap: var(--space-3); flex-wrap: wrap; flex: 1; }
.item-row__actions { display: flex; gap: var(--space-2); }
.item-badge { font-size: var(--text-xs); font-weight: var(--weight-bold); color: var(--color-accent); background: var(--color-accent-light); padding: 2px 8px; border-radius: var(--radius-sm); }
.item-name { font-size: var(--text-md); font-weight: var(--weight-semibold); }
.item-meta { font-size: var(--text-xs); color: var(--color-text-tertiary); }
.grade-chip { padding: var(--space-1) var(--space-2); border-radius: var(--radius-full); font-size: var(--text-xs); font-weight: var(--weight-bold); }
.grade-chip.is-excellent { color: var(--color-success); background: var(--color-success-light); }
.grade-chip.is-pass { color: var(--color-accent); background: var(--color-accent-light); }
.grade-chip.is-fail { color: var(--color-danger); background: var(--color-danger-light); }
.btn-sm { padding: var(--space-1) var(--space-3); border-radius: var(--radius-md); font-size: var(--text-xs); font-weight: var(--weight-medium); color: var(--color-accent); border: 1px solid rgba(0,113,227,0.2); transition: all var(--duration-fast); }
.btn-sm:hover { background: var(--color-accent-light); }
.btn-sm--danger { color: var(--color-danger); border-color: rgba(255,59,48,0.2); }
.btn-sm--danger:hover { background: var(--color-danger-light); }
.editor-panel { padding: var(--space-4); margin: var(--space-3) var(--space-4); }
select.form-input { cursor: pointer; }
</style>
