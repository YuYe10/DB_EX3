<template>
  <div class="page">
    <header class="hero">
      <div class="hero-content">
        <p class="eyebrow">✨ 管理员界面</p>
        <h1 class="hero-title">学生选课与成绩管理系统</h1>
        <p class="subtitle">欢迎，<strong>管理员</strong> · 完整权限</p>
        <div class="status" :class="health.db ? 'ok' : 'bad'">
          <span class="status-dot" :class="health.db ? 'online' : 'offline'"></span>
          {{ health.db ? '✓ 后端连接正常' : '✗ 等待后端连接' }}
        </div>
      </div>
      <div class="stat-panel" v-if="stats.counts">
        <div class="stat-card">
          <div class="stat-value">{{ stats.counts.students }}</div>
          <div class="stat-label">学生</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.counts.teachers }}</div>
          <div class="stat-label">教师</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.counts.courses }}</div>
          <div class="stat-label">课程</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.counts.enrollments }}</div>
          <div class="stat-label">选课</div>
        </div>
        <button @click="handleLogout" class="btn-logout-hero">退出登录</button>
      </div>
    </header>

    <section class="grid">
      <article class="card" style="--accent: #3b82f6;">
        <header class="card-header">
          <h2>👥 新增学生</h2>
          <p class="card-desc">创建学生账户，输入学号和姓名</p>
        </header>
        <form @submit.prevent="createStudent" class="form-grid">
          <label class="form-group">
            <span class="label-text">学号</span>
            <input v-model="studentForm.student_no" required placeholder="例: S001" />
          </label>
          <label class="form-group">
            <span class="label-text">姓名</span>
            <input v-model="studentForm.name" required placeholder="例: 张三" />
          </label>
          <label class="form-group">
            <span class="label-text">专业</span>
            <input v-model="studentForm.major" placeholder="例: 计算机科学" />
          </label>
          <button type="submit" class="btn-primary">+ 添加学生</button>
        </form>
        <div class="list" v-if="students.length">
          <h3 class="list-title">📋 学生列表</h3>
          <div class="item-card" v-for="s in students" :key="s.id">
            <div class="item-content">
              <div class="item-badge">{{ s.student_no }}</div>
              <div class="item-details">
                <div class="item-name">{{ s.name }}</div>
                <div class="item-meta">{{ s.major || '未填专业' }}</div>
              </div>
            </div>
            <button class="btn-danger-sm" @click="deleteStudent(s.id)">删除</button>
          </div>
        </div>
        <div class="empty-state" v-else>
          <p>暂无学生记录</p>
        </div>
      </article>

      <article class="card" style="--accent: #8b5cf6;">
        <header class="card-header">
          <h2>🎓 新增教师</h2>
          <p class="card-desc">创建教师账户，输入工号和姓名</p>
        </header>
        <form @submit.prevent="createTeacher" class="form-grid">
          <label class="form-group">
            <span class="label-text">工号</span>
            <input v-model="teacherForm.teacher_no" required placeholder="例: T001" />
          </label>
          <label class="form-group">
            <span class="label-text">姓名</span>
            <input v-model="teacherForm.name" required placeholder="例: 王老师" />
          </label>
          <label class="form-group">
            <span class="label-text">院系</span>
            <input v-model="teacherForm.department" placeholder="例: 计算机学院" />
          </label>
          <button type="submit" class="btn-primary">+ 添加教师</button>
        </form>
        <div class="list" v-if="teachers.length">
          <h3 class="list-title">📋 教师列表</h3>
          <div class="item-card" v-for="t in teachers" :key="t.id">
            <div class="item-content">
              <div class="item-badge" style="background: #f3e8ff; color: #6d28d9;">{{ t.teacher_no }}</div>
              <div class="item-details">
                <div class="item-name">{{ t.name }}</div>
                <div class="item-meta">{{ t.department || '未填院系' }}</div>
              </div>
            </div>
            <button class="btn-danger-sm" @click="deleteTeacher(t.id)">删除</button>
          </div>
        </div>
        <div class="empty-state" v-else>
          <p>暂无教师记录</p>
        </div>
      </article>

      <article class="card" style="--accent: #ec4899;">
        <header class="card-header">
          <h2>📚 新增课程</h2>
          <p class="card-desc">创建课程，可关联授课教师</p>
        </header>
        <form @submit.prevent="createCourse" class="form-grid">
          <label class="form-group">
            <span class="label-text">课程号</span>
            <input v-model="courseForm.course_code" required placeholder="例: C001" />
          </label>
          <label class="form-group">
            <span class="label-text">课程名</span>
            <input v-model="courseForm.name" required placeholder="例: 数据库原理" />
          </label>
          <label class="form-group">
            <span class="label-text">学分</span>
            <input type="number" step="0.5" v-model.number="courseForm.credit" placeholder="例: 3" />
          </label>
          <label class="form-group">
            <span class="label-text">容量</span>
            <input type="number" v-model.number="courseForm.capacity" placeholder="例: 50" />
          </label>
          <label class="form-group">
            <span class="label-text">授课教师</span>
            <select v-model.number="courseForm.teacher_id">
              <option :value="null">── 未指定教师</option>
              <option v-for="t in teachers" :value="t.id" :key="t.id">{{ t.name }}</option>
            </select>
          </label>
          <button type="submit" class="btn-primary">+ 添加课程</button>
        </form>
        <div class="list" v-if="courses.length">
          <h3 class="list-title">📋 课程列表</h3>
          <div class="item-card" v-for="c in courses" :key="c.id">
            <div class="item-content">
              <div class="item-badge" style="background: #fce7f3; color: #be185d;">{{ c.course_code }}</div>
              <div class="item-details">
                <div class="item-name">{{ c.name }}</div>
                <div class="item-meta">{{ c.teacher_name || '暂无教师' }} · {{ c.credit }}学分</div>
              </div>
            </div>
            <button class="btn-danger-sm" @click="deleteCourse(c.id)">删除</button>
          </div>
        </div>
        <div class="empty-state" v-else>
          <p>暂无课程记录</p>
        </div>
      </article>

      <article class="card" style="--accent: #14b8a6;">
        <header class="card-header">
          <h2>⭐ 选课/退课与成绩</h2>
          <p class="card-desc">管理选课关系和成绩信息</p>
        </header>
        <form class="enroll-form" @submit.prevent="enroll">
          <div class="form-row">
            <label class="form-group">
              <span class="label-text">学生</span>
              <select v-model.number="enrollForm.student_id" required>
                <option disabled value="">请选择学生</option>
                <option v-for="s in students" :value="s.id" :key="s.id">{{ s.name }}</option>
              </select>
            </label>
            <label class="form-group">
              <span class="label-text">课程</span>
              <select v-model.number="enrollForm.course_id" required>
                <option disabled value="">请选择课程</option>
                <option v-for="c in courses" :value="c.id" :key="c.id">{{ c.name }}</option>
              </select>
            </label>
          </div>
          <button type="submit" class="btn-primary">✓ 选课</button>
        </form>

        <div class="list" v-if="enrollments.length">
          <h3 class="list-title">📋 选课记录</h3>
          <div class="enrollment-item" v-for="e in enrollments" :key="e.id">
            <div class="enrollment-info">
              <div class="enrollment-header">
                <strong>{{ e.student_name }}</strong>
                <span class="divider">→</span>
                <strong>{{ e.course_name }}</strong>
              </div>
              <div class="enrollment-meta">
                <span>教师: {{ e.teacher_name || '未分配' }}</span>
                <span class="grade-tag" v-if="e.grade !== null">成绩: <strong>{{ e.grade }}</strong></span>
              </div>
            </div>
            <div class="enrollment-actions">
              <div class="grade-input-group">
                <input type="number" step="0.5" placeholder="输入成绩" v-model.number="gradeInput[e.id]" />
                <button class="btn-success-sm" @click="setGrade(e.id)" type="button">更新</button>
              </div>
              <button class="btn-danger-sm" @click="dropCourse(e.id)">退课</button>
            </div>
          </div>
        </div>
        <div class="empty-state" v-else>
          <p>暂无选课记录</p>
        </div>
      </article>

      <article class="card" style="--accent: #f59e0b;">
        <header class="card-header">
          <h2>📥 Excel导入/导出</h2>
          <p class="card-desc">批量导入课程与学生名单，导出课程成绩</p>
        </header>

        <div class="import-box">
          <label class="upload-btn">
            <input type="file" accept=".xlsx,.xls" @change="importExcel" />
            <span>{{ importLoading ? '正在导入...' : '上传Excel导入' }}</span>
          </label>
          <p class="help-text">工作表要求：courses(必填)，可选 students、enrollments</p>
          <p class="error-text" v-if="importError">{{ importError }}</p>
          <div class="summary" v-if="importSummary">
            <div>课程新增 {{ importSummary.courses_created }}，跳过 {{ importSummary.courses_skipped }}</div>
            <div>学生新增 {{ importSummary.students_created }}，跳过 {{ importSummary.students_skipped }}</div>
            <div>教师新增 {{ importSummary.teachers_created }}</div>
            <div>选课新增 {{ importSummary.enrollments_created }}，跳过 {{ importSummary.enrollments_skipped }}</div>
            <div v-if="importSummary.errors?.length" class="error-list">
              <strong>提醒:</strong>
              <ul>
                <li v-for="(e, idx) in importSummary.errors" :key="idx">{{ e }}</li>
              </ul>
            </div>
          </div>
        </div>

        <div class="export-box">
          <div class="form-row">
            <label class="form-group">
              <span class="label-text">选择课程</span>
              <select v-model.number="exportCourseId">
                <option :value="''">请选择课程</option>
                <option v-for="c in courses" :value="c.id" :key="c.id">{{ c.name }}</option>
              </select>
            </label>
          </div>
          <button class="btn-primary" @click="exportGrades" :disabled="!exportCourseId || exportLoading">
            {{ exportLoading ? '生成中...' : '导出成绩Excel' }}
          </button>
          <p class="error-text" v-if="exportError">{{ exportError }}</p>
        </div>
      </article>
    </section>

    <section class="card stats-card" v-if="stats.course_avg?.length">
      <header class="card-header">
        <h2>📊 课程平均成绩统计</h2>
        <p class="card-desc">实时显示各课程的平均成绩</p>
      </header>
      <div class="stats-grid">
        <div class="stat-item" v-for="c in stats.course_avg" :key="c.id">
          <div class="stat-item-header">
            <span class="stat-code">{{ c.course_code }}</span>
            <span class="stat-name">{{ c.name }}</span>
          </div>
          <div class="stat-value-large">{{ c.avg_grade ?? '无' }}</div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted, computed } from 'vue'

const props = defineProps({
  user: { type: Object, required: true }
})

const emit = defineEmits(['logout'])

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api'

const health = reactive({ db: false })
const students = ref([])
const teachers = ref([])
const courses = ref([])
const enrollments = ref([])
const stats = reactive({ counts: null, course_avg: [] })
const importSummary = ref(null)
const importError = ref('')
const importLoading = ref(false)
const exportCourseId = ref('')
const exportLoading = ref(false)
const exportError = ref('')

const studentForm = reactive({ student_no: '', name: '', major: '' })
const teacherForm = reactive({ teacher_no: '', name: '', department: '' })
const courseForm = reactive({ course_code: '', name: '', credit: 0, capacity: 50, teacher_id: null })
const enrollForm = reactive({ student_id: '', course_id: '' })
const gradeInput = reactive({})

const healthText = computed(() => (health.db ? '连接正常' : '等待连接'))

function handleLogout() {
  emit('logout')
}

async function api(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    ...options,
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

async function loadHealth() {
  try {
    const data = await api('/health')
    health.db = data.db
  } catch (err) {
    health.db = false
    console.error(err)
  }
}

async function loadAll() {
  const [s, t, c, e, st] = await Promise.all([
    api('/students'),
    api('/teachers'),
    api('/courses'),
    api('/enrollments'),
    api('/statistics/overview'),
  ])
  students.value = s
  teachers.value = t
  courses.value = c
  enrollments.value = e
  stats.counts = st.counts
  stats.course_avg = st.course_avg
}

async function createStudent() {
  await api('/students', { method: 'POST', body: JSON.stringify(studentForm) })
  Object.assign(studentForm, { student_no: '', name: '', major: '' })
  await loadAll()
}

async function deleteStudent(id) {
  await api(`/students/${id}`, { method: 'DELETE' })
  await loadAll()
}

async function createTeacher() {
  await api('/teachers', { method: 'POST', body: JSON.stringify(teacherForm) })
  Object.assign(teacherForm, { teacher_no: '', name: '', department: '' })
  await loadAll()
}

async function deleteTeacher(id) {
  await api(`/teachers/${id}`, { method: 'DELETE' })
  await loadAll()
}

async function createCourse() {
  await api('/courses', { method: 'POST', body: JSON.stringify(courseForm) })
  Object.assign(courseForm, { course_code: '', name: '', credit: 0, capacity: 50, teacher_id: null })
  await loadAll()
}

async function deleteCourse(id) {
  await api(`/courses/${id}`, { method: 'DELETE' })
  await loadAll()
}

async function enroll() {
  await api('/enrollments', { method: 'POST', body: JSON.stringify(enrollForm) })
  enrollForm.student_id = ''
  enrollForm.course_id = ''
  await loadAll()
}

async function setGrade(id) {
  const grade = gradeInput[id]
  if (grade === undefined || grade === '') return
  await api(`/enrollments/${id}/grade`, { method: 'PUT', body: JSON.stringify({ grade }) })
  await loadAll()
}

async function dropCourse(id) {
  await api(`/enrollments/${id}`, { method: 'DELETE' })
  await loadAll()
}

async function importExcel(event) {
  const file = event.target.files?.[0]
  if (!file) return
  importError.value = ''
  importSummary.value = null
  importLoading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    const res = await fetch(`${API_BASE}/import/courses`, {
      method: 'POST',
      body: formData,
      credentials: 'include',
    })
    const data = await res.json()
    if (!res.ok || data.success === false) throw new Error(data.message || '导入失败')
    importSummary.value = data.summary || null
    await loadAll()
  } catch (err) {
    importError.value = err.message
  } finally {
    importLoading.value = false
    event.target.value = ''
  }
}

async function exportGrades() {
  if (!exportCourseId.value) return
  exportError.value = ''
  exportLoading.value = true
  try {
    const res = await fetch(`${API_BASE}/courses/${exportCourseId.value}/grades/export`, {
      credentials: 'include',
    })
    if (!res.ok) throw new Error(await res.text())
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const course = courses.value.find(c => c.id === exportCourseId.value) || {}
    const filename = `成绩单_${course.course_code || course.name || 'course'}.xlsx`
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  } catch (err) {
    exportError.value = err.message
  } finally {
    exportLoading.value = false
  }
}

onMounted(async () => {
  await loadHealth()
  await loadAll()
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+SC:wght@400;500;600;700&display=swap');

:global(body) {
  margin: 0;
  font-family: 'Inter', 'Noto Sans SC', system-ui, -apple-system, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%);
  background-size: 400% 400%;
  animation: gradient-shift 15s ease infinite;
  color: #0f172a;
  min-height: 100vh;
}

@keyframes gradient-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.page {
  max-width: 1280px;
  margin: 0 auto;
  padding: 40px 24px 60px;
}

/* ===== HERO SECTION ===== */
.hero {
  display: flex;
  justify-content: space-between;
  gap: 40px;
  align-items: flex-start;
  padding: 48px 48px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 24px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15), 0 0 1px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.5);
  animation: fade-in 0.6s ease-out;
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.hero-content {
  flex: 1;
}

.eyebrow {
  letter-spacing: 0.15em;
  text-transform: uppercase;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 800;
  margin: 0 0 8px 0;
  font-size: 12px;
}

.hero-title {
  margin: 0 0 12px 0;
  font-size: 42px;
  font-weight: 800;
  background: linear-gradient(135deg, #0f172a 0%, #334155 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.02em;
}

.subtitle {
  color: #64748b;
  margin: 0 0 16px 0;
  font-size: 16px;
  line-height: 1.6;
  max-width: 500px;
}

.status {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding: 12px 16px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 14px;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.status.ok {
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
  color: #166534;
  border-color: #86efac;
}

.status.bad {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #991b1b;
  border-color: #fca5a5;
}

.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

.status-dot.online {
  background: #22c55e;
}

.status-dot.offline {
  background: #ef4444;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* ===== STAT PANEL ===== */
.stat-panel {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 16px;
  flex-wrap: wrap;
}

.stat-card {
  padding: 20px;
  border-radius: 16px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 2px solid #7dd3fc;
  text-align: center;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(56, 189, 248, 0.25);
}

.stat-value {
  font-size: 32px;
  font-weight: 800;
  background: linear-gradient(135deg, #0284c7 0%, #06b6d4 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  font-size: 12px;
  font-weight: 700;
  color: #0c4a6e;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-top: 4px;
}

/* ===== GRID LAYOUT ===== */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
  margin-top: 32px;
}

/* ===== CARD STYLES ===== */
.card {
  background: white;
  border-radius: 20px;
  padding: 28px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.08);
  border: 1px solid #f0f1f3;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  animation: slide-up 0.6s ease-out;
}

@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 48px rgba(0, 0, 0, 0.12);
  border-color: var(--accent, #3b82f6);
}

.card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--accent, #3b82f6), transparent);
  border-radius: 20px 20px 0 0;
}

.card-header {
  margin-bottom: 20px;
  border-bottom: 2px solid #f0f1f3;
  padding-bottom: 16px;
}

.card-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #0f172a;
}

.card-desc {
  margin: 8px 0 0 0;
  color: #64748b;
  font-size: 13px;
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: 32px 16px;
  color: #94a3b8;
  font-size: 14px;
}

/* ===== FORM STYLES ===== */
.form-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.label-text {
  font-weight: 700;
  color: #0f172a;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

input, select {
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  padding: 12px 14px;
  font-size: 14px;
  font-family: inherit;
  outline: none;
  transition: all 0.3s ease;
  background: #f8fafc;
}

input::placeholder, select::placeholder {
  color: #cbd5e1;
}

input:focus, select:focus {
  border-color: var(--accent, #3b82f6);
  background: white;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  transform: translateY(-1px);
}

/* ===== BUTTON STYLES ===== */
.btn-primary {
  border: none;
  border-radius: 12px;
  padding: 12px 24px;
  font-weight: 700;
  font-size: 14px;
  background: linear-gradient(135deg, var(--accent, #3b82f6) 0%, rgba(59, 130, 246, 0.8) 100%);
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 28px rgba(59, 130, 246, 0.4);
}

.btn-primary:active {
  transform: translateY(0);
}

.btn-danger-sm {
  border: 1px solid #fee2e2;
  border-radius: 8px;
  padding: 6px 12px;
  font-weight: 600;
  font-size: 12px;
  background: #fef2f2;
  color: #b91c1c;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-danger-sm:hover {
  background: #fee2e2;
  border-color: #fecaca;
}

.btn-success-sm {
  border: 1px solid #dcfce7;
  border-radius: 8px;
  padding: 6px 12px;
  font-weight: 600;
  font-size: 12px;
  background: #f0fdf4;
  color: #166534;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-success-sm:hover {
  background: #dcfce7;
  border-color: #86efac;
}

.btn-logout-hero {
  padding: 10px 16px;
  border: none;
  border-radius: 10px;
  background: #ef4444;
  color: white;
  font-weight: 700;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.btn-logout-hero:hover {
  background: #dc2626;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(239, 68, 68, 0.4);
}

/* ===== LIST STYLES ===== */
.list {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.list-title {
  margin: 0 0 16px 0;
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.item-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  transition: all 0.2s ease;
}

.item-card:hover {
  border-color: var(--accent, #3b82f6);
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.item-content {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.item-badge {
  padding: 6px 12px;
  border-radius: 8px;
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #1e40af;
  font-weight: 700;
  font-size: 12px;
  text-transform: uppercase;
  white-space: nowrap;
}

.item-details {
  flex: 1;
  min-width: 0;
}

.item-name {
  font-weight: 700;
  color: #0f172a;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-meta {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ===== ENROLLMENT STYLES ===== */
.enroll-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 12px;
}

.enrollment-item {
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  transition: all 0.2s ease;
}

.enrollment-item:hover {
  border-color: var(--accent, #14b8a6);
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.enrollment-header {
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 8px;
}

.divider {
  color: #cbd5e1;
  margin: 0 8px;
}

.enrollment-info {
  margin-bottom: 12px;
}

.enrollment-meta {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  font-size: 12px;
  color: #64748b;
}

.grade-tag {
  background: #fef3c7;
  color: #92400e;
  padding: 4px 8px;
  border-radius: 6px;
  font-weight: 600;
}

.enrollment-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.grade-input-group {
  display: flex;
  gap: 6px;
  flex: 1;
  min-width: 200px;
}

.grade-input-group input {
  flex: 1;
  padding: 8px 10px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 13px;
}

/* ===== IMPORT / EXPORT ===== */
.import-box, .export-box {
  margin-top: 12px;
  padding: 16px;
  border: 1px dashed #f59e0b;
  border-radius: 12px;
  background: #fff7ed;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.upload-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 10px;
  background: #f59e0b;
  color: #fff;
  cursor: pointer;
  font-weight: 700;
  border: none;
  box-shadow: 0 10px 25px rgba(245, 158, 11, 0.25);
  position: relative;
  overflow: hidden;
}

.upload-btn input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.help-text {
  margin: 0;
  color: #b45309;
  font-size: 13px;
}

.summary {
  font-size: 13px;
  color: #92400e;
  display: grid;
  gap: 4px;
}

.error-text {
  color: #b91c1c;
  font-size: 13px;
  margin: 0;
}

.error-list {
  margin-top: 6px;
  background: #fef2f2;
  border: 1px solid #fecdd3;
  border-radius: 8px;
  padding: 8px 10px;
  color: #991b1b;
}

.error-list ul {
  padding-left: 18px;
  margin: 6px 0 0 0;
}

/* ===== STATS SECTION ===== */
.stats-card {
  margin-top: 32px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-top: 20px;
}

.stat-item {
  padding: 20px;
  border-radius: 16px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 2px solid #7dd3fc;
  transition: all 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(56, 189, 248, 0.25);
}

.stat-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.stat-code {
  font-weight: 800;
  color: #0284c7;
  font-size: 13px;
  text-transform: uppercase;
  background: white;
  padding: 4px 8px;
  border-radius: 6px;
}

.stat-name {
  color: #0c4a6e;
  font-weight: 600;
  font-size: 12px;
}

.stat-value-large {
  font-size: 36px;
  font-weight: 800;
  background: linear-gradient(135deg, #0284c7 0%, #06b6d4 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* ===== RESPONSIVE DESIGN ===== */
@media (max-width: 768px) {
  .page {
    padding: 24px 16px 40px;
  }

  .hero {
    flex-direction: column;
    gap: 24px;
    padding: 32px 20px;
  }

  .hero-title {
    font-size: 28px;
  }

  .stat-panel {
    grid-template-columns: repeat(2, 1fr);
  }

  .card {
    padding: 20px;
  }

  .grid {
    grid-template-columns: 1fr;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .enrollment-actions {
    flex-direction: column;
  }

  .grade-input-group {
    min-width: auto;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .page {
    padding: 16px 12px 32px;
  }

  .hero {
    padding: 20px 16px;
  }

  .hero-title {
    font-size: 24px;
  }

  .stat-panel {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }

  .stat-card {
    padding: 12px;
  }

  .stat-value {
    font-size: 24px;
  }

  .card {
    padding: 16px;
  }

  .card-header {
    margin-bottom: 16px;
  }

  .card-header h2 {
    font-size: 16px;
  }

  .item-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .enrollment-item {
    padding: 12px;
  }
}
</style>
