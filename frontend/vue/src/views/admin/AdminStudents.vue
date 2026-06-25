<template>
  <section class="card--glass animate-slide-up">
    <div class="card__header">
      <h2 class="card__title">学生管理</h2>
      <span class="card__count" v-if="students.length">{{ filteredStudents.length }}/{{ students.length }}</span>
    </div>
    <!-- Create Form -->
    <form @submit.prevent="create" class="inline-form">
      <input v-model="form.student_no" placeholder="学号" required class="form-input" />
      <input v-model="form.name" placeholder="姓名" required class="form-input" />
      <input v-model="form.major" placeholder="专业" class="form-input" />
      <button type="submit" class="btn-add" :disabled="creating">+ 添加</button>
    </form>
    <!-- Search -->
    <SearchFilter v-model="search" placeholder="搜索学号、姓名或专业..." class="card__search" />
    <!-- List -->
    <div class="card__body" v-if="filteredStudents.length">
      <TransitionGroup name="list-stagger">
        <div v-for="s in filteredStudents" :key="s.id" class="item-row">
          <div class="item-row__main">
            <span class="item-badge">{{ s.student_no }}</span>
            <span class="item-name">{{ s.name }}</span>
            <span class="item-meta">{{ s.major || '未填专业' }} · 第{{ s.current_semester || 1 }}学期</span>
          </div>
          <div class="item-row__actions">
            <select v-model.number="semesterEdit[s.id]" class="semester-select">
              <option v-for="n in 8" :key="n" :value="n">第{{ n }}学期</option>
            </select>
            <button class="btn-sm" @click="updateSemester(s.id)" :disabled="semesterEdit[s.id] === s.current_semester">保存</button>
            <button class="btn-sm btn-sm--danger" @click="confirmDelete(s)">删除</button>
          </div>
        </div>
      </TransitionGroup>
    </div>
    <EmptyState v-else icon="👥" title="暂无学生" description="使用上方表单添加第一个学生" />

    <ConfirmDialog :visible="deleteTarget != null" title="删除学生"
      :message="`确定要删除学生「${deleteTarget?.name}」吗？此操作不可撤销。`"
      icon="⚠️" confirm-text="删除" variant="danger"
      @confirm="doDelete" @cancel="deleteTarget = null" />
  </section>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import SearchFilter from '../../components/shared/SearchFilter.vue'
import EmptyState from '../../components/shared/EmptyState.vue'
import ConfirmDialog from '../../components/shared/ConfirmDialog.vue'

const emit = defineEmits(['changed'])
const API = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api'

const students = ref([])
const search = ref('')
const creating = ref(false)
const deleteTarget = ref(null)
const semesterEdit = reactive({})
const form = reactive({ student_no: '', name: '', major: '' })

const filteredStudents = computed(() => {
  if (!search.value) return students.value
  const kw = search.value.toLowerCase()
  return students.value.filter(s =>
    s.student_no?.toLowerCase().includes(kw) ||
    s.name?.toLowerCase().includes(kw) ||
    s.major?.toLowerCase().includes(kw))
})

watch(students, list => {
  list.forEach(s => { if (!(s.id in semesterEdit)) semesterEdit[s.id] = s.current_semester || 1 })
}, { immediate: true })

async function api(path, opts = {}) {
  const res = await fetch(`${API}${path}`, {
    credentials: 'include',
    headers: opts.headers || { 'Content-Type': 'application/json' },
    ...opts
  })
  if (!res.ok) { const d = await res.json().catch(() => ({})); throw new Error(d.message || '操作失败') }
  return res.json()
}

async function load() {
  try { students.value = await api('/students') } catch (e) { console.error(e) }
}

async function create() {
  creating.value = true
  try {
    await api('/students', { method: 'POST', body: JSON.stringify({ ...form }) })
    form.student_no = ''; form.name = ''; form.major = ''
    await load(); emit('changed')
  } catch (e) { alert(e.message) } finally { creating.value = false }
}

async function updateSemester(id) {
  try {
    await api(`/students/${id}`, { method: 'PUT', body: JSON.stringify({ current_semester: semesterEdit[id] }) })
    await load(); emit('changed')
  } catch (e) { alert(e.message) }
}

function confirmDelete(s) { deleteTarget.value = s }
async function doDelete() {
  if (!deleteTarget.value) return
  try {
    await api(`/students/${deleteTarget.value.id}`, { method: 'DELETE' })
    deleteTarget.value = null
    await load(); emit('changed')
  } catch (e) { alert(e.message) }
}

onMounted(load)
defineExpose({ load })
</script>

<style scoped>
.card--glass {
  background: var(--color-bg-glass);
  backdrop-filter: var(--blur-glass);
  -webkit-backdrop-filter: var(--blur-glass);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}
.card__header {
  display: flex; align-items: center; justify-content: space-between;
  padding: var(--space-5) var(--space-6) var(--space-3);
}
.card__title { font-size: var(--text-lg); font-weight: var(--weight-bold); }
.card__count {
  font-size: var(--text-xs); color: var(--color-text-tertiary);
  background: var(--color-bg-secondary); padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-full);
}
.card__search { padding: 0 var(--space-6) var(--space-3); }
.card__body { padding: 0 var(--space-6) var(--space-6); max-height: 400px; overflow-y: auto; }

.inline-form {
  display: flex; gap: var(--space-2); padding: 0 var(--space-6) var(--space-4);
  flex-wrap: wrap;
}
.form-input {
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  flex: 1; min-width: 100px;
  outline: none;
  transition: border-color var(--duration-fast);
}
.form-input:focus { border-color: var(--color-accent); box-shadow: 0 0 0 3px var(--color-accent-light); }
.btn-add {
  padding: var(--space-2) var(--space-4);
  background: var(--color-accent); color: white;
  border-radius: var(--radius-md);
  font-size: var(--text-sm); font-weight: var(--weight-semibold);
  transition: all var(--duration-fast);
}
.btn-add:hover:not(:disabled) { background: var(--color-accent-hover); }
.btn-add:disabled { opacity: 0.5; }

.item-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  margin-bottom: var(--space-2);
  transition: all var(--duration-fast);
}
.item-row:hover { border-color: var(--color-border-strong); background: var(--color-bg-elevated); }
.item-row__main { display: flex; align-items: center; gap: var(--space-3); flex-wrap: wrap; flex: 1; min-width: 0; }
.item-badge {
  font-size: var(--text-xs); font-weight: var(--weight-bold); color: var(--color-accent);
  background: var(--color-accent-light); padding: 2px 8px; border-radius: var(--radius-sm);
}
.item-name { font-size: var(--text-md); font-weight: var(--weight-semibold); }
.item-meta { font-size: var(--text-xs); color: var(--color-text-tertiary); }
.item-row__actions { display: flex; gap: var(--space-2); align-items: center; flex-shrink: 0; }
.semester-select {
  padding: var(--space-1) var(--space-2);
  border: 1px solid var(--color-border); border-radius: var(--radius-sm);
  font-size: var(--text-xs);
}
.btn-sm {
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-md);
  font-size: var(--text-xs); font-weight: var(--weight-medium);
  color: var(--color-accent); border: 1px solid rgba(0,113,227,0.2);
  transition: all var(--duration-fast);
}
.btn-sm:hover { background: var(--color-accent-light); }
.btn-sm--danger { color: var(--color-danger); border-color: rgba(255,59,48,0.2); }
.btn-sm--danger:hover { background: var(--color-danger-light); }
</style>
