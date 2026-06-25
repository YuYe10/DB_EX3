<template>
  <section class="card--glass animate-slide-up">
    <div class="card__header">
      <h2 class="card__title">教师管理</h2>
      <span class="card__count" v-if="teachers.length">{{ filteredTeachers.length }}/{{ teachers.length }}</span>
    </div>
    <form @submit.prevent="create" class="inline-form">
      <input v-model="form.teacher_no" placeholder="工号" required class="form-input" />
      <input v-model="form.name" placeholder="姓名" required class="form-input" />
      <input v-model="form.department" placeholder="院系" class="form-input" />
      <button type="submit" class="btn-add" :disabled="creating">+ 添加</button>
    </form>
    <SearchFilter v-model="search" placeholder="搜索工号、姓名或院系..." class="card__search" />
    <div class="card__body" v-if="filteredTeachers.length">
      <TransitionGroup name="list-stagger">
        <div v-for="t in filteredTeachers" :key="t.id" class="item-row">
          <div class="item-row__main">
            <span class="item-badge">{{ t.teacher_no }}</span>
            <span class="item-name">{{ t.name }}</span>
            <span class="item-meta">{{ t.department || '未填院系' }}</span>
          </div>
          <button class="btn-sm btn-sm--danger" @click="confirmDelete(t)">删除</button>
        </div>
      </TransitionGroup>
    </div>
    <EmptyState v-else icon="👨‍🏫" title="暂无教师" />
    <ConfirmDialog :visible="deleteTarget != null" title="删除教师"
      :message="`确定要删除教师「${deleteTarget?.name}」吗？`"
      icon="⚠️" confirm-text="删除" variant="danger"
      @confirm="doDelete" @cancel="deleteTarget = null" />
  </section>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import SearchFilter from '../../components/shared/SearchFilter.vue'
import EmptyState from '../../components/shared/EmptyState.vue'
import ConfirmDialog from '../../components/shared/ConfirmDialog.vue'

const emit = defineEmits(['changed'])
const API = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api'
const teachers = ref([]); const search = ref(''); const creating = ref(false); const deleteTarget = ref(null)
const form = reactive({ teacher_no: '', name: '', department: '' })

const filteredTeachers = computed(() => {
  if (!search.value) return teachers.value
  const kw = search.value.toLowerCase()
  return teachers.value.filter(t => t.teacher_no?.toLowerCase().includes(kw) || t.name?.toLowerCase().includes(kw) || t.department?.toLowerCase().includes(kw))
})

async function api(p, o = {}) {
  const r = await fetch(`${API}${p}`, { credentials: 'include', headers: o.headers || { 'Content-Type': 'application/json' }, ...o })
  if (!r.ok) { const d = await r.json().catch(() => ({})); throw new Error(d.message || '操作失败') }
  return r.json()
}
async function load() { try { teachers.value = await api('/teachers') } catch (e) { console.error(e) } }
async function create() {
  creating.value = true
  try { await api('/teachers', { method: 'POST', body: JSON.stringify({ ...form }) }); form.teacher_no = ''; form.name = ''; form.department = ''; await load(); emit('changed') }
  catch (e) { alert(e.message) } finally { creating.value = false }
}
function confirmDelete(t) { deleteTarget.value = t }
async function doDelete() {
  if (!deleteTarget.value) return
  try { await api(`/teachers/${deleteTarget.value.id}`, { method: 'DELETE' }); deleteTarget.value = null; await load(); emit('changed') }
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
.inline-form { display: flex; gap: var(--space-2); padding: 0 var(--space-6) var(--space-4); flex-wrap: wrap; }
.form-input { padding: var(--space-2) var(--space-3); border: 1px solid var(--color-border); border-radius: var(--radius-md); font-size: var(--text-sm); flex: 1; min-width: 100px; outline: none; transition: border-color var(--duration-fast); }
.form-input:focus { border-color: var(--color-accent); box-shadow: 0 0 0 3px var(--color-accent-light); }
.btn-add { padding: var(--space-2) var(--space-4); background: var(--color-accent); color: white; border-radius: var(--radius-md); font-size: var(--text-sm); font-weight: var(--weight-semibold); transition: all var(--duration-fast); }
.btn-add:hover:not(:disabled) { background: var(--color-accent-hover); }
.item-row { display: flex; align-items: center; justify-content: space-between; padding: var(--space-3) var(--space-4); border-radius: var(--radius-md); border: 1px solid var(--color-border); margin-bottom: var(--space-2); transition: all var(--duration-fast); }
.item-row:hover { border-color: var(--color-border-strong); background: var(--color-bg-elevated); }
.item-row__main { display: flex; align-items: center; gap: var(--space-3); flex-wrap: wrap; flex: 1; }
.item-badge { font-size: var(--text-xs); font-weight: var(--weight-bold); color: var(--color-accent); background: var(--color-accent-light); padding: 2px 8px; border-radius: var(--radius-sm); }
.item-name { font-size: var(--text-md); font-weight: var(--weight-semibold); }
.item-meta { font-size: var(--text-xs); color: var(--color-text-tertiary); }
.btn-sm { padding: var(--space-1) var(--space-3); border-radius: var(--radius-md); font-size: var(--text-xs); font-weight: var(--weight-medium); transition: all var(--duration-fast); }
.btn-sm--danger { color: var(--color-danger); border: 1px solid rgba(255,59,48,0.2); }
.btn-sm--danger:hover { background: var(--color-danger-light); }
</style>
