<template>
  <section class="card--glass animate-slide-up">
    <div class="card__header">
      <h2 class="card__title">课程管理</h2>
      <span class="card__count" v-if="courses.length">{{ filteredCourses.length }}/{{ courses.length }}</span>
    </div>
    <form @submit.prevent="create" class="inline-form">
      <input v-model="form.course_code" placeholder="课程编号" required class="form-input" />
      <input v-model="form.name" placeholder="课程名称" required class="form-input" />
      <input v-model.number="form.credit" type="number" placeholder="学分" class="form-input form-input--sm" />
      <input v-model.number="form.capacity" type="number" placeholder="容量" class="form-input form-input--sm" />
      <select v-model="form.teacher_id" class="form-input">
        <option :value="null">选择教师</option>
        <option v-for="t in teachers" :key="t.id" :value="t.id">{{ t.name }} ({{ t.teacher_no }})</option>
      </select>
      <button type="submit" class="btn-add" :disabled="creating">+ 添加</button>
    </form>
    <SearchFilter v-model="search" placeholder="搜索课程编号或名称..." class="card__search" />
    <div class="card__body" v-if="filteredCourses.length">
      <TransitionGroup name="list-stagger">
        <div v-for="c in filteredCourses" :key="c.id" class="item-row">
          <div class="item-row__main">
            <span class="item-badge">{{ c.course_code }}</span>
            <span class="item-name">{{ c.name }}</span>
            <span class="item-meta">{{ c.credit }}学分 · 容量{{ c.capacity }} · {{ c.teacher_name || '未分配教师' }}</span>
          </div>
          <div class="item-row__actions">
            <button class="btn-sm" @click="toggleWeights(c)">权重</button>
            <button class="btn-sm btn-sm--danger" @click="confirmDelete(c)">删除</button>
          </div>
        </div>
      </TransitionGroup>
    </div>
    <EmptyState v-else icon="📚" title="暂无课程" />

    <!-- Weight Editor Modal -->
    <Teleport to="body">
      <Transition name="overlay">
        <div v-if="weightTarget" class="modal-overlay" @click.self="weightTarget = null">
          <Transition name="modal">
            <div v-if="weightTarget" class="modal-card modal-content">
              <h3>成绩权重 — {{ weightTarget.name }}</h3>
              <WeightEditor :ordinary-weight="weightTarget.ordinary_weight || 0.5"
                :final-weight="weightTarget.final_weight || 0.5" @save="saveWeights" />
            </div>
          </Transition>
        </div>
      </Transition>
    </Teleport>

    <ConfirmDialog :visible="deleteTarget != null" title="删除课程"
      :message="`确定要删除课程「${deleteTarget?.name}」吗？`"
      icon="⚠️" confirm-text="删除" variant="danger"
      @confirm="doDelete" @cancel="deleteTarget = null" />
  </section>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import SearchFilter from '../../components/shared/SearchFilter.vue'
import EmptyState from '../../components/shared/EmptyState.vue'
import ConfirmDialog from '../../components/shared/ConfirmDialog.vue'
import WeightEditor from '../../components/shared/WeightEditor.vue'

const props = defineProps({ teachers: { type: Array, default: () => [] } })
const emit = defineEmits(['changed'])
const API = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api'
const courses = ref([]); const search = ref(''); const creating = ref(false)
const deleteTarget = ref(null); const weightTarget = ref(null)
const form = reactive({ course_code: '', name: '', credit: 0, capacity: 50, teacher_id: null })

const filteredCourses = computed(() => {
  if (!search.value) return courses.value
  const kw = search.value.toLowerCase()
  return courses.value.filter(c => c.course_code?.toLowerCase().includes(kw) || c.name?.toLowerCase().includes(kw))
})

async function api(p, o = {}) {
  const r = await fetch(`${API}${p}`, { credentials: 'include', headers: o.headers || { 'Content-Type': 'application/json' }, ...o })
  if (!r.ok) { const d = await r.json().catch(() => ({})); throw new Error(d.message || '操作失败') }
  return r.json()
}
async function load() { try { courses.value = await api('/courses') } catch (e) { console.error(e) } }
async function create() {
  creating.value = true
  try { await api('/courses', { method: 'POST', body: JSON.stringify({ ...form }) }); form.course_code = ''; form.name = ''; await load(); emit('changed') }
  catch (e) { alert(e.message) } finally { creating.value = false }
}
function toggleWeights(c) { weightTarget.value = c }
async function saveWeights(payload) {
  try { await api(`/courses/${weightTarget.value.id}/weights`, { method: 'PUT', body: JSON.stringify(payload) }); weightTarget.value = null; await load() }
  catch (e) { alert(e.message) }
}
function confirmDelete(c) { deleteTarget.value = c }
async function doDelete() {
  if (!deleteTarget.value) return
  try { await api(`/courses/${deleteTarget.value.id}`, { method: 'DELETE' }); deleteTarget.value = null; await load(); emit('changed') }
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
.card__body { padding: 0 var(--space-6) var(--space-6); max-height: 400px; overflow-y: auto; }
.inline-form { display: flex; gap: var(--space-2); padding: 0 var(--space-6) var(--space-4); flex-wrap: wrap; align-items: center; }
.form-input { padding: var(--space-2) var(--space-3); border: 1px solid var(--color-border); border-radius: var(--radius-md); font-size: var(--text-sm); flex: 1; min-width: 100px; outline: none; transition: border-color var(--duration-fast); }
.form-input--sm { flex: 0 0 70px; min-width: 60px; }
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
.btn-sm { padding: var(--space-1) var(--space-3); border-radius: var(--radius-md); font-size: var(--text-xs); font-weight: var(--weight-medium); color: var(--color-accent); border: 1px solid rgba(0,113,227,0.2); transition: all var(--duration-fast); }
.btn-sm:hover { background: var(--color-accent-light); }
.btn-sm--danger { color: var(--color-danger); border-color: rgba(255,59,48,0.2); }
.btn-sm--danger:hover { background: var(--color-danger-light); }
.modal-overlay { position: fixed; inset: 0; z-index: 1000; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.3); backdrop-filter: var(--blur-subtle); padding: var(--space-6); }
.modal-card { background: var(--color-bg-elevated); border-radius: var(--radius-xl); padding: var(--space-8); max-width: 500px; width: 100%; box-shadow: var(--shadow-2xl); border: 1px solid var(--color-border); }
.modal-card h3 { font-size: var(--text-lg); font-weight: var(--weight-bold); margin-bottom: var(--space-6); }
select.form-input { cursor: pointer; }
</style>
