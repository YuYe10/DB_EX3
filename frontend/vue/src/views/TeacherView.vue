<template>
  <div class="teacher-page">
    <!-- Hero -->
    <div class="teacher-hero animate-fade-in">
      <p class="hero-eyebrow">教师界面</p>
      <h1 class="hero-title">欢迎，{{ user?.name || user?.username }}</h1>
      <div class="hero-meta">
        <span class="hero-badge">{{ user?.teacher_no || user?.username }}</span>
      </div>
    </div>

    <!-- Course Tabs -->
    <div class="teacher-tabs" v-if="courses.length">
      <button v-for="c in courses" :key="c.id" class="tab-btn" :class="{ active: activeCourseId === c.id }"
        @click="selectCourse(c)">
        <span class="tab-name">{{ c.name }}</span>
        <span class="tab-count">{{ c.enrolled_count }}人</span>
      </button>
    </div>

    <div v-if="activeCourseId" class="teacher-content stagger">
      <!-- Actions Bar -->
      <div class="action-bar card--glass">
        <button class="action-btn" @click="exportGrades">📥 导出成绩</button>
        <label class="action-btn action-btn--upload">
          📤 导入花名册
          <input type="file" accept=".xlsx,.xls" hidden @change="handleImport" />
        </label>
        <button class="action-btn" @click="downloadSample">📋 下载模板</button>
      </div>

      <!-- Stats Row -->
      <div class="stats-row" v-if="activeStats">
        <StatCard label="选课人数" :value="activeStats.enrolled_count" icon="👥" variant="accent" />
        <StatCard label="平均成绩" :value="activeStats.avg_grade" icon="📊" format="decimal" variant="default" />
        <StatCard label="及格率" :value="activeStats.pass_rate" icon="✅" format="percent" variant="success" />
        <StatCard label="优秀率" :value="activeStats.excellent_rate" icon="🌟" format="percent" variant="warning" />
      </div>

      <!-- Weight Editor -->
      <WeightEditor v-if="activeCourse" :ordinary-weight="activeCourse.ordinary_weight"
        :final-weight="activeCourse.final_weight" @save="saveWeights" />

      <!-- Students Table -->
      <section class="card--glass">
        <div class="card__header">
          <h2 class="card__title">学生名单</h2>
          <span class="card__count">{{ activeStudents.length }} 人</span>
        </div>
        <div class="card__body">
          <LoadingSpinner v-if="loadingStudents" text="加载学生..." />
          <div v-else-if="activeStudents.length">
            <div v-for="stu in activeStudents" :key="stu.id" class="student-row">
              <div class="student-row__info">
                <div class="student-row__no">{{ stu.student_no }}</div>
                <div class="student-row__name">{{ stu.student_name }}</div>
                <div class="student-row__major">{{ stu.major || '-' }}</div>
              </div>
              <div class="student-row__grade">
                <span class="grade-chip" :class="gradeChipClass(stu.final_grade)">
                  {{ stu.final_grade != null ? stu.final_grade + '分' : '未评分' }}
                </span>
              </div>
              <button class="edit-toggle" @click="toggleEditor(stu.id)">
                {{ editingId === stu.id ? '收起' : '编辑成绩' }}
              </button>
            </div>

            <!-- Inline Grade Editor -->
            <Transition name="collapse">
              <div v-if="editingId" class="editor-panel">
                <GradeEditor :ordinary-score="editingStudent?.ordinary_score"
                  :final-score="editingStudent?.final_score"
                  :ordinary-weight="activeCourse?.ordinary_weight || 0.5"
                  :final-weight="activeCourse?.final_weight || 0.5"
                  @save="saveGrade" @cancel="editingId = null" />
              </div>
            </Transition>
          </div>
          <EmptyState v-else icon="👨‍🎓" title="暂无学生" description="导入花名册或等待学生选课" />
        </div>
      </section>
    </div>

    <!-- Empty state: no courses -->
    <EmptyState v-if="!loadingCourses && courses.length === 0" icon="📚" title="暂无课程"
      description="联系管理员为您分配课程，或通过花名册导入创建课程" />

    <!-- Import Summary -->
    <Teleport to="body">
      <Transition name="overlay">
        <div v-if="importSummary" class="modal-overlay" @click.self="importSummary = null">
          <Transition name="modal">
            <div v-if="importSummary" class="modal-card modal-content">
              <h3>📤 导入完成</h3>
              <div class="import-stats">
                <div v-for="(v, k) in importSummary" :key="k" class="import-stat" v-show="typeof v === 'number'">
                  <span class="import-stat__label">{{ importLabels[k] || k }}</span>
                  <span class="import-stat__val">{{ v }}</span>
                </div>
              </div>
              <button class="btn-save" @click="importSummary = null">确定</button>
            </div>
          </Transition>
        </div>
      </Transition>
    </Teleport>

    <!-- Password Modal -->
    <Teleport to="body">
      <Transition name="overlay">
        <div v-if="showPwModal" class="modal-overlay" @click.self="showPwModal = false">
          <Transition name="modal">
            <div v-if="showPwModal" class="modal-card modal-content">
              <h3>修改密码</h3>
              <form @submit.prevent="changePassword">
                <label class="modal-field"><span>旧密码</span><input v-model="pwForm.old_password" type="password" required /></label>
                <label class="modal-field"><span>新密码</span><input v-model="pwForm.new_password" type="password" required /></label>
                <p v-if="pwError" class="form-error">{{ pwError }}</p>
                <div class="modal-actions">
                  <button type="button" class="btn-cancel" @click="showPwModal = false">取消</button>
                  <button type="submit" class="btn-save">保存</button>
                </div>
              </form>
            </div>
          </Transition>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import StatCard from '../components/shared/StatCard.vue'
import WeightEditor from '../components/shared/WeightEditor.vue'
import GradeEditor from '../components/shared/GradeEditor.vue'
import EmptyState from '../components/shared/EmptyState.vue'
import LoadingSpinner from '../components/shared/LoadingSpinner.vue'

const props = defineProps({ user: { type: Object, required: true } })
const emit = defineEmits(['logout'])
const API = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api'

const courses = ref([])
const activeCourseId = ref(null)
const activeStudents = ref([])
const activeStats = ref(null)
const allStats = ref([])
const loadingCourses = ref(false)
const loadingStudents = ref(false)
const editingId = ref(null)
const importSummary = ref(null)
const showPwModal = ref(false)
const pwError = ref('')
const pwForm = reactive({ old_password: '', new_password: '' })

const importLabels = {
  course_created: '课程创建', course_updated: '课程更新',
  students_created: '学生创建', students_skipped: '学生跳过',
  enrollments_created: '选课创建', enrollments_skipped: '选课跳过',
  errors: '错误'
}

const activeCourse = computed(() => courses.value.find(c => c.id === activeCourseId.value))
const editingStudent = computed(() => activeStudents.value.find(s => s.id === editingId.value))

async function api(path, opts = {}) {
  const res = await fetch(`${API}${path}`, {
    credentials: 'include',
    headers: opts.headers || { 'Content-Type': 'application/json' },
    ...opts
  })
  if (!res.ok) { const d = await res.json().catch(() => ({})); throw new Error(d.message || '操作失败') }
  const ct = res.headers.get('content-type') || ''
  return ct.includes('application/json') ? res.json() : res.blob()
}

async function loadCourses() {
  loadingCourses.value = true
  try {
    courses.value = await api('/teacher/courses')
    allStats.value = await api('/teacher/courses/stats').catch(() => [])
    if (courses.value.length && !activeCourseId.value) selectCourse(courses.value[0])
  } catch (e) { console.error(e) } finally { loadingCourses.value = false }
}

function selectCourse(course) {
  activeCourseId.value = course.id
  editingId.value = null
  loadStudents()
  const s = allStats.value.find(s => s.id === course.id)
  activeStats.value = s || null
}

async function loadStudents() {
  loadingStudents.value = true
  try {
    activeStudents.value = await api(`/teacher/courses/${activeCourseId.value}/students`).catch(() => [])
  } finally { loadingStudents.value = false }
}

function toggleEditor(id) { editingId.value = editingId.value === id ? null : id }

async function saveGrade(payload) {
  try {
    await api(`/teacher/enrollments/${editingId.value}/grades`, {
      method: 'PUT', body: JSON.stringify(payload)
    })
    editingId.value = null
    await loadStudents()
    await loadCourses()
  } catch (e) { alert(e.message) }
}

async function saveWeights(payload) {
  try {
    await api(`/teacher/courses/${activeCourseId.value}/weights`, {
      method: 'PUT', body: JSON.stringify(payload)
    })
    await loadCourses()
    if (activeCourse.value) {
      activeCourse.value.ordinary_weight = payload.ordinary_weight
      activeCourse.value.final_weight = payload.final_weight
    }
  } catch (e) { alert(e.message) }
}

async function exportGrades() {
  try {
    const blob = await api(`/teacher/courses/${activeCourseId.value}/grades/export`)
    downloadBlob(blob, `${activeCourse.value?.name || 'grades'}.xlsx`)
  } catch (e) { alert(e.message) }
}

async function handleImport(e) {
  const file = e.target.files[0]
  if (!file) return
  const fd = new FormData(); fd.append('file', file)
  try {
    const res = await fetch(`${API}/teacher/courses/import`, { method: 'POST', credentials: 'include', body: fd })
    importSummary.value = await res.json()
    await loadCourses()
    if (importSummary.value?.course_id) {
      activeCourseId.value = importSummary.value.course_id
      await loadStudents()
    }
  } catch (e) { alert(e.message) }
  e.target.value = ''
}

async function downloadSample() {
  try {
    const blob = await api('/teacher/courses/import/sample')
    downloadBlob(blob, '花名册示例.xlsx')
  } catch (e) { alert(e.message) }
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a'); a.href = url; a.download = filename
  a.click(); URL.revokeObjectURL(url)
}

async function changePassword() {
  pwError.value = ''
  try {
    await api('/auth/change-password', { method: 'POST', body: JSON.stringify(pwForm) })
    showPwModal.value = false
    alert('密码修改成功')
  } catch (e) { pwError.value = e.message }
}

function gradeChipClass(grade) {
  if (grade == null) return ''
  if (grade >= 90) return 'is-excellent'
  if (grade >= 60) return 'is-pass'
  return 'is-fail'
}

onMounted(loadCourses)
</script>

<style scoped>
.teacher-page {
  max-width: var(--content-max-width);
  margin: 0 auto;
  padding: var(--space-6);
}
.teacher-hero {
  background: var(--color-bg-glass);
  backdrop-filter: var(--blur-glass);
  -webkit-backdrop-filter: var(--blur-glass);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: var(--space-6) var(--space-8);
  margin-bottom: var(--space-6);
}
.hero-eyebrow {
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  color: var(--color-accent);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: var(--space-2);
}
.hero-title {
  font-size: var(--text-2xl);
  font-weight: var(--weight-extrabold);
  letter-spacing: var(--tracking-tight);
  margin-bottom: var(--space-3);
}
.hero-meta { display: flex; gap: var(--space-2); }
.hero-badge {
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  background: var(--color-bg-secondary);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}

/* Tabs */
.teacher-tabs {
  display: flex;
  gap: var(--space-1);
  margin-bottom: var(--space-6);
  padding: var(--space-1);
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}
.tab-btn {
  padding: var(--space-3) var(--space-5);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  color: var(--color-text-secondary);
  transition: all var(--duration-fast) var(--ease-default);
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: var(--space-2);
}
.tab-btn.active {
  background: var(--color-bg-elevated);
  color: var(--color-text-primary);
  font-weight: var(--weight-semibold);
  box-shadow: var(--shadow-sm);
}
.tab-btn:hover:not(.active) { color: var(--color-text-primary); }
.tab-count {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  background: var(--color-bg-secondary);
  padding: 2px 6px;
  border-radius: var(--radius-full);
}

/* Action Bar */
.action-bar {
  display: flex;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-5);
  margin-bottom: var(--space-6);
  border-radius: var(--radius-lg);
  flex-wrap: wrap;
  background: var(--color-bg-glass);
  border: 1px solid var(--color-border);
}
.action-btn {
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
  transition: all var(--duration-fast) var(--ease-default);
}
.action-btn:hover { background: var(--color-bg-elevated); border-color: var(--color-border-strong); }
.action-btn--upload { cursor: pointer; }

/* Stats Row */
.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

/* Card */
.card--glass {
  background: var(--color-bg-glass);
  backdrop-filter: var(--blur-glass);
  -webkit-backdrop-filter: var(--blur-glass);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  overflow: hidden;
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
.card__body { padding: 0 var(--space-6) var(--space-6); }

/* Student rows */
.student-row {
  display: flex; align-items: center; gap: var(--space-4);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  margin-bottom: var(--space-2);
  transition: all var(--duration-fast);
}
.student-row:hover { border-color: var(--color-border-strong); background: var(--color-bg-elevated); }
.student-row__info { flex: 1; min-width: 0; }
.student-row__no { font-size: var(--text-xs); font-weight: var(--weight-bold); color: var(--color-accent); }
.student-row__name { font-size: var(--text-md); font-weight: var(--weight-semibold); }
.student-row__major { font-size: var(--text-xs); color: var(--color-text-tertiary); }

.grade-chip {
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: var(--text-sm);
  font-weight: var(--weight-bold);
  white-space: nowrap;
}
.grade-chip.is-excellent { color: var(--color-success); background: var(--color-success-light); }
.grade-chip.is-pass { color: var(--color-accent); background: var(--color-accent-light); }
.grade-chip.is-fail { color: var(--color-danger); background: var(--color-danger-light); }

.edit-toggle {
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-md);
  font-size: var(--text-xs);
  font-weight: var(--weight-medium);
  color: var(--color-accent);
  border: 1px solid rgba(0,113,227,0.2);
  transition: all var(--duration-fast);
}
.edit-toggle:hover { background: var(--color-accent-light); }

.editor-panel { padding: var(--space-4); margin-top: var(--space-3); }

/* Modal */
.modal-overlay {
  position: fixed; inset: 0; z-index: 1000;
  display: flex; align-items: center; justify-content: center;
  background: rgba(0,0,0,0.3);
  backdrop-filter: var(--blur-subtle);
  padding: var(--space-6);
}
.modal-card {
  background: var(--color-bg-elevated);
  border-radius: var(--radius-xl);
  padding: var(--space-8);
  max-width: 480px; width: 100%;
  box-shadow: var(--shadow-2xl);
  border: 1px solid var(--color-border);
}
.modal-card h3 { font-size: var(--text-lg); font-weight: var(--weight-bold); margin-bottom: var(--space-6); }
.modal-field {
  display: flex; flex-direction: column; gap: var(--space-2); margin-bottom: var(--space-4);
  font-size: var(--text-xs); font-weight: var(--weight-semibold); color: var(--color-text-secondary);
  text-transform: uppercase; letter-spacing: 0.04em;
}
.modal-field input {
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--text-md);
  outline: none;
}
.modal-field input:focus { border-color: var(--color-accent); box-shadow: 0 0 0 3px var(--color-accent-light); }
.modal-actions { display: flex; gap: var(--space-3); justify-content: flex-end; margin-top: var(--space-4); }
.btn-save {
  padding: var(--space-2) var(--space-5);
  background: var(--color-accent); color: white;
  border-radius: var(--radius-md); font-weight: var(--weight-semibold); font-size: var(--text-sm);
}
.btn-cancel {
  padding: var(--space-2) var(--space-5);
  background: var(--color-bg-secondary); border: 1px solid var(--color-border);
  border-radius: var(--radius-md); font-weight: var(--weight-medium); font-size: var(--text-sm);
}
.form-error {
  padding: var(--space-2) var(--space-3);
  background: var(--color-danger-light); border-radius: var(--radius-md);
  color: var(--color-danger); font-size: var(--text-sm);
}
.import-stats {
  display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-3); margin-bottom: var(--space-6);
}
.import-stat__label { font-size: var(--text-xs); color: var(--color-text-secondary); }
.import-stat__val { font-size: var(--text-xl); font-weight: var(--weight-bold); }
</style>
