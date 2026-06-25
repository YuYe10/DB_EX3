<template>
  <section class="card--glass animate-slide-up">
    <div class="card__header">
      <h2 class="card__title">专业培养计划</h2>
      <span class="card__count" v-if="plans.length">{{ plans.length }} 个计划</span>
    </div>
    <div class="card__body">
      <!-- Create Plan -->
      <form @submit.prevent="createPlan" class="inline-form">
        <input v-model="planForm.major_name" placeholder="专业名称" required class="form-input" />
        <input v-model="planForm.description" placeholder="计划描述（可选）" class="form-input" />
        <button type="submit" class="btn-add">+ 创建计划</button>
      </form>

      <!-- Plan List -->
      <div v-if="plans.length">
        <div v-for="plan in plans" :key="plan.id" class="plan-card">
          <div class="plan-card__header" @click="togglePlan(plan.id)">
            <div>
              <span class="plan-name">{{ plan.major_name }}</span>
              <span class="plan-desc">{{ plan.description || '暂无描述' }}</span>
            </div>
            <div class="plan-actions">
              <span class="plan-count">{{ plan._courseCount || 0 }} 门课程</span>
              <button class="btn-sm btn-sm--danger" @click.stop="confirmDeletePlan(plan)">删除</button>
            </div>
          </div>
          <Transition name="collapse">
            <div v-if="expandedPlanId === plan.id" class="plan-detail">
              <!-- Add Course -->
              <div class="plan-add-course">
                <select v-model="addCourseForm.course_id" class="form-input">
                  <option value="">选择课程</option>
                  <option v-for="c in allCourses" :key="c.id" :value="c.id">{{ c.course_code }} {{ c.name }}</option>
                </select>
                <select v-model.number="addCourseForm.semester" class="form-input form-input--sm">
                  <option :value="null">学期</option>
                  <option v-for="n in 12" :key="n" :value="n">第{{ n }}学期</option>
                </select>
                <label class="checkbox-label"><input type="checkbox" v-model="addCourseForm.is_required" /> 必修</label>
                <button class="btn-add" @click="addCourse(plan.id)" :disabled="!addCourseForm.course_id || !addCourseForm.semester">添加</button>
              </div>
              <!-- Courses by Semester -->
              <div v-if="plan._courses?.length">
                <div v-for="sem in uniqueSemesters(plan._courses)" :key="sem" class="sem-group">
                  <h4 class="sem-title">第 {{ sem }} 学期</h4>
                  <div v-for="mpc in plan._courses.filter(c => c.semester === sem)" :key="mpc.id" class="sem-course">
                    <span class="item-badge">{{ mpc.course_code }}</span>
                    <span>{{ mpc.course_name }}</span>
                    <span class="item-meta">{{ mpc.credit }}学分 · {{ mpc.teacher_name || '未分配' }}</span>
                    <span class="sem-tag" :class="mpc.is_required ? 'is-required' : 'is-elective'">
                      {{ mpc.is_required ? '必修' : '选修' }}
                    </span>
                    <button class="btn-sm btn-sm--danger" @click="removeCourse(mpc.id)">移除</button>
                  </div>
                </div>
              </div>
              <EmptyState v-else icon="📋" title="暂无课程" description="使用上方表单添加课程到此计划" />
            </div>
          </Transition>
        </div>
      </div>
      <EmptyState v-else icon="🎓" title="暂无培养计划" description="创建专业培养计划以组织课程体系" />
    </div>
    <ConfirmDialog :visible="deleteTarget != null" title="删除培养计划"
      :message="`确定要删除「${deleteTarget?.major_name}」培养计划吗？`"
      icon="⚠️" confirm-text="删除" variant="danger"
      @confirm="doDeletePlan" @cancel="deleteTarget = null" />
  </section>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import EmptyState from '../../components/shared/EmptyState.vue'
import ConfirmDialog from '../../components/shared/ConfirmDialog.vue'

const props = defineProps({ allCourses: { type: Array, default: () => [] } })
const emit = defineEmits(['changed'])
const API = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api'
const plans = ref([]); const expandedPlanId = ref(null)
const deleteTarget = ref(null)
const planForm = reactive({ major_name: '', description: '' })
const addCourseForm = reactive({ course_id: '', semester: null, is_required: true })

function uniqueSemesters(courses) { return [...new Set(courses.map(c => c.semester))].sort((a, b) => a - b) }

async function api(p, o = {}) {
  const r = await fetch(`${API}${p}`, { credentials: 'include', headers: o.headers || { 'Content-Type': 'application/json' }, ...o })
  if (!r.ok) { const d = await r.json().catch(() => ({})); throw new Error(d.message || '操作失败') }
  return r.json()
}
async function load() {
  try {
    plans.value = await api('/major-plans')
    for (const plan of plans.value) {
      plan._courses = await api(`/major-plans/${plan.id}/courses`).catch(() => [])
      plan._courseCount = plan._courses.length
    }
  } catch (e) { console.error(e) }
}
async function createPlan() {
  try { await api('/major-plans', { method: 'POST', body: JSON.stringify(planForm) }); planForm.major_name = ''; planForm.description = ''; await load(); emit('changed') }
  catch (e) { alert(e.message) }
}
function togglePlan(id) { expandedPlanId.value = expandedPlanId.value === id ? null : id }
async function addCourse(planId) {
  try { await api(`/major-plans/${planId}/courses`, { method: 'POST', body: JSON.stringify({ course_id: addCourseForm.course_id, semester: addCourseForm.semester, is_required: addCourseForm.is_required }) }); addCourseForm.course_id = ''; addCourseForm.semester = null; await load() }
  catch (e) { alert(e.message) }
}
async function removeCourse(mpcId) {
  try { await api(`/major-plans/courses/${mpcId}`, { method: 'DELETE' }); await load() }
  catch (e) { alert(e.message) }
}
function confirmDeletePlan(p) { deleteTarget.value = p }
async function doDeletePlan() {
  if (!deleteTarget.value) return
  try { await api(`/major-plans/${deleteTarget.value.id}`, { method: 'DELETE' }); deleteTarget.value = null; await load(); emit('changed') }
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
.card__body { padding: var(--space-6); }
.inline-form { display: flex; gap: var(--space-2); margin-bottom: var(--space-4); flex-wrap: wrap; align-items: center; }
.form-input { padding: var(--space-2) var(--space-3); border: 1px solid var(--color-border); border-radius: var(--radius-md); font-size: var(--text-sm); flex: 1; min-width: 100px; outline: none; transition: border-color var(--duration-fast); }
.form-input:focus { border-color: var(--color-accent); box-shadow: 0 0 0 3px var(--color-accent-light); }
.form-input--sm { flex: 0 0 80px; }
.btn-add { padding: var(--space-2) var(--space-4); background: var(--color-accent); color: white; border-radius: var(--radius-md); font-size: var(--text-sm); font-weight: var(--weight-semibold); white-space: nowrap; }
.btn-add:hover:not(:disabled) { background: var(--color-accent-hover); }
.btn-add:disabled { opacity: 0.5; }

.plan-card { border: 1px solid var(--color-border); border-radius: var(--radius-lg); margin-bottom: var(--space-3); overflow: hidden; }
.plan-card__header { display: flex; align-items: center; justify-content: space-between; padding: var(--space-4); cursor: pointer; transition: background var(--duration-fast); }
.plan-card__header:hover { background: var(--color-bg-secondary); }
.plan-name { font-size: var(--text-md); font-weight: var(--weight-bold); display: block; }
.plan-desc { font-size: var(--text-xs); color: var(--color-text-tertiary); }
.plan-actions { display: flex; align-items: center; gap: var(--space-3); }
.plan-count { font-size: var(--text-xs); color: var(--color-text-secondary); }
.plan-detail { padding: var(--space-4); border-top: 1px solid var(--color-border); background: var(--color-bg-secondary); }
.plan-add-course { display: flex; gap: var(--space-2); margin-bottom: var(--space-4); align-items: center; flex-wrap: wrap; }
.checkbox-label { font-size: var(--text-sm); display: flex; align-items: center; gap: var(--space-1); white-space: nowrap; }
.sem-group { margin-bottom: var(--space-3); }
.sem-title { font-size: var(--text-sm); font-weight: var(--weight-bold); color: var(--color-accent); margin-bottom: var(--space-2); padding-bottom: var(--space-1); border-bottom: 1px solid var(--color-border); }
.sem-course { display: flex; align-items: center; gap: var(--space-3); padding: var(--space-2) var(--space-3); border-radius: var(--radius-md); margin-bottom: var(--space-1); font-size: var(--text-sm); }
.sem-course:hover { background: var(--color-bg-elevated); }
.item-badge { font-size: var(--text-xs); font-weight: var(--weight-bold); color: var(--color-accent); background: var(--color-accent-light); padding: 2px 8px; border-radius: var(--radius-sm); }
.item-meta { font-size: var(--text-xs); color: var(--color-text-tertiary); }
.sem-tag { font-size: 10px; font-weight: var(--weight-bold); padding: 2px 8px; border-radius: var(--radius-full); text-transform: uppercase; }
.sem-tag.is-required { color: var(--color-danger); background: var(--color-danger-light); }
.sem-tag.is-elective { color: var(--color-info); background: var(--color-info-light); }
.btn-sm { padding: var(--space-1) var(--space-3); border-radius: var(--radius-md); font-size: var(--text-xs); font-weight: var(--weight-medium); color: var(--color-accent); border: 1px solid rgba(0,113,227,0.2); transition: all var(--duration-fast); margin-left: auto; }
.btn-sm:hover { background: var(--color-accent-light); }
.btn-sm--danger { color: var(--color-danger); border-color: rgba(255,59,48,0.2); margin-left: var(--space-2); }
.btn-sm--danger:hover { background: var(--color-danger-light); }
select.form-input { cursor: pointer; }
</style>
