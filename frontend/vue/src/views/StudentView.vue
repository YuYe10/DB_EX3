<template>
  <div class="student-page">
    <div class="student-hero animate-fade-in">
      <div class="hero-content">
        <p class="hero-eyebrow">学生界面</p>
        <h1 class="hero-title">欢迎，{{ studentInfo?.name || user?.username }}</h1>
        <div class="hero-meta">
          <span class="hero-badge">{{ user?.student_no || user?.username }}</span>
          <span class="hero-badge hero-badge--semester">
            第 {{ studentInfo?.current_semester || 1 }} 学期
          </span>
          <span class="hero-badge hero-badge--major" v-if="studentInfo?.major">
            {{ studentInfo.major }}
          </span>
        </div>
      </div>
    </div>

    <div class="student-grid stagger">
      <!-- Available Courses -->
      <section class="card card--glass">
        <div class="card__header">
          <h2 class="card__title">可选课程</h2>
          <span class="card__count" v-if="filteredCourses.length">{{ filteredCourses.length }} 门</span>
        </div>
        <SearchFilter v-model="searchKeyword" placeholder="搜索课程名称或编号..." class="card__search">
          <template #filters>
            <select v-model="selectedSemester" class="filter-select">
              <option :value="null">全部学期</option>
              <option v-for="sem in availableSemesters" :key="sem" :value="sem">第 {{ sem }} 学期</option>
            </select>
            <select v-model="filterCredit" class="filter-select">
              <option :value="null">全部学分</option>
              <option v-for="c in [1,2,3,4,5,6]" :key="c" :value="c">{{ c }} 学分</option>
            </select>
          </template>
        </SearchFilter>

        <div class="card__body">
          <LoadingSpinner v-if="loadingCourses" text="加载课程..." />
          <div v-else-if="filteredCourses.length" class="course-list">
            <TransitionGroup name="list-stagger">
              <div v-for="course in filteredCourses" :key="course.course_id" class="course-item"
                :class="{ 'course-item--disabled': !canEnroll(course) }">
                <div class="course-item__main">
                  <div class="course-item__code">{{ course.course_code }}</div>
                  <div class="course-item__name">{{ course.course_name }}</div>
                  <div class="course-item__meta">
                    <span class="meta-tag">{{ course.teacher_name || '未分配教师' }}</span>
                    <span class="meta-tag">{{ course.credit }} 学分</span>
                    <span class="meta-tag" v-if="course.semester">第{{ course.semester }}学期</span>
                  </div>
                </div>
                <div class="course-item__right">
                  <div class="course-capacity" :class="{ 'is-full': course.enrolled_count >= course.capacity }">
                    {{ course.enrolled_count }} / {{ course.capacity }}
                  </div>
                  <button class="enroll-btn" @click="enrollCourse(course.course_id)"
                    :disabled="!canEnroll(course) || enrollingId === course.course_id">
                    <LoadingSpinner v-if="enrollingId === course.course_id" size="sm" />
                    <span v-else-if="course.already_enrolled">已选</span>
                    <span v-else-if="course.enrolled_count >= course.capacity">已满</span>
                    <span v-else>选课</span>
                  </button>
                </div>
              </div>
            </TransitionGroup>
          </div>
          <EmptyState v-else icon="📚" title="暂无可选课程"
            description="当前学期没有匹配的课程，或专业培养计划尚未配置" />
        </div>
      </section>

      <!-- My Enrollments -->
      <section class="card card--glass">
        <div class="card__header">
          <h2 class="card__title">我的选课</h2>
          <span class="card__count" v-if="myEnrollments.length">{{ myEnrollments.length }} 门</span>
        </div>
        <div class="card__body">
          <LoadingSpinner v-if="loadingEnrollments" text="加载选课..." />
          <div v-else-if="myEnrollments.length" class="enroll-list">
            <TransitionGroup name="list-stagger">
              <div v-for="enr in myEnrollments" :key="enr.id" class="enroll-item">
                <div class="enroll-item__main">
                  <div class="enroll-item__code">{{ enr.course_code }}</div>
                  <div class="enroll-item__name">{{ enr.course_name }}</div>
                  <div class="enroll-item__meta">
                    <span class="meta-tag">{{ enr.teacher_name || '未分配教师' }}</span>
                    <span class="meta-tag">{{ enr.credit }} 学分</span>
                  </div>
                </div>
                <div class="enroll-item__right">
                  <div class="grade-badge" :class="gradeClass(enr.final_grade)">
                    {{ enr.final_grade != null ? enr.final_grade + '分' : '未评分' }}
                  </div>
                  <button class="drop-btn" @click="confirmDrop(enr)" :disabled="droppingId === enr.id">
                    {{ droppingId === enr.id ? '...' : '退课' }}
                  </button>
                </div>
              </div>
            </TransitionGroup>
          </div>
          <EmptyState v-else icon="📝" title="暂无选课记录" description="在左侧可选课程中选择课程加入学习" />
        </div>
      </section>
    </div>

    <!-- Change Password Modal -->
    <Teleport to="body">
      <Transition name="overlay">
        <div v-if="showChangePassword" class="modal-overlay" @click.self="showChangePassword = false">
          <Transition name="modal">
            <div v-if="showChangePassword" class="modal-card modal-content">
              <h3>修改密码</h3>
              <form @submit.prevent="changePassword" class="modal-form">
                <label class="login-field">
                  <span class="login-field__label">旧密码</span>
                  <input v-model="pwForm.old_password" type="password" required class="login-field__input" />
                </label>
                <label class="login-field">
                  <span class="login-field__label">新密码</span>
                  <input v-model="pwForm.new_password" type="password" required class="login-field__input" />
                </label>
                <p v-if="pwError" class="login-error">{{ pwError }}</p>
                <div class="modal-actions">
                  <button type="button" class="btn-cancel" @click="showChangePassword = false">取消</button>
                  <button type="submit" class="btn-save">保存</button>
                </div>
              </form>
            </div>
          </Transition>
        </div>
      </Transition>
    </Teleport>

    <!-- Drop Confirm -->
    <ConfirmDialog :visible="dropTarget != null" title="确认退课" :message="dropTarget ? `确定要退选「${dropTarget.course_name}」吗？` : ''"
      icon="📋" confirm-text="确认退课" variant="danger" @confirm="doDrop" @cancel="dropTarget = null" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import SearchFilter from '../components/shared/SearchFilter.vue'
import LoadingSpinner from '../components/shared/LoadingSpinner.vue'
import EmptyState from '../components/shared/EmptyState.vue'
import ConfirmDialog from '../components/shared/ConfirmDialog.vue'

const props = defineProps({ user: { type: Object, required: true } })
const emit = defineEmits(['logout'])

const API = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api'

// --- State ---
const availableCourses = ref([])
const myEnrollments = ref([])
const studentInfo = ref(null)
const availableSemesters = ref([])
const loadingCourses = ref(false)
const loadingEnrollments = ref(false)
const enrollingId = ref(null)
const droppingId = ref(null)
const searchKeyword = ref('')
const filterCredit = ref(null)
const selectedSemester = ref(null)
const showChangePassword = ref(false)
const pwError = ref('')
const dropTarget = ref(null)
const pwForm = reactive({ old_password: '', new_password: '' })

// --- Computed ---
const filteredCourses = computed(() => {
  let list = availableCourses.value
  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase()
    list = list.filter(c => c.course_code?.toLowerCase().includes(kw) || c.course_name?.toLowerCase().includes(kw))
  }
  if (selectedSemester.value) list = list.filter(c => c.semester === selectedSemester.value)
  if (filterCredit.value) list = list.filter(c => c.credit === filterCredit.value)
  return list
})

function canEnroll(course) {
  return !course.already_enrolled && course.enrolled_count < course.capacity &&
    course.semester === studentInfo.value?.current_semester
}

function gradeClass(grade) {
  if (grade == null) return ''
  if (grade >= 90) return 'is-excellent'
  if (grade >= 60) return 'is-pass'
  return 'is-fail'
}

// --- API ---
async function api(path, opts = {}) {
  const res = await fetch(`${API}${path}`, {
    credentials: 'include',
    headers: opts.headers || { 'Content-Type': 'application/json' },
    ...opts
  })
  if (!res.ok) { const d = await res.json().catch(() => ({})); throw new Error(d.message || '操作失败') }
  return res.json()
}

async function loadData() {
  loadingCourses.value = true; loadingEnrollments.value = true
  try {
    const [courses, enrollments, sems, info] = await Promise.all([
      api('/student/courses/available').catch(() => []),
      api('/student/enrollments').catch(() => []),
      api('/student/semesters').catch(() => []),
      api('/student/info').catch(() => null)
    ])
    availableCourses.value = Array.isArray(courses) ? courses : []
    myEnrollments.value = Array.isArray(enrollments) ? enrollments : []
    availableSemesters.value = Array.isArray(sems) ? sems : []
    studentInfo.value = info
  } catch (e) { console.error(e) }
  finally { loadingCourses.value = false; loadingEnrollments.value = false }
}

async function enrollCourse(courseId) {
  enrollingId.value = courseId
  try {
    await api('/student/enrollments', {
      method: 'POST', body: JSON.stringify({ course_id: courseId })
    })
    await loadData()
  } catch (e) { alert(e.message) }
  finally { enrollingId.value = null }
}

function confirmDrop(enr) { dropTarget.value = enr }

async function doDrop() {
  if (!dropTarget.value) return
  droppingId.value = dropTarget.value.id
  try {
    await api(`/student/enrollments/${dropTarget.value.id}`, { method: 'DELETE' })
    dropTarget.value = null
    await loadData()
  } catch (e) { alert(e.message) }
  finally { droppingId.value = null }
}

async function changePassword() {
  pwError.value = ''
  try {
    await api('/auth/change-password', {
      method: 'POST', body: JSON.stringify(pwForm)
    })
    showChangePassword.value = false
    alert('密码修改成功')
  } catch (e) { pwError.value = e.message }
}

onMounted(loadData)
</script>

<style scoped>
.student-page {
  max-width: var(--content-max-width);
  margin: 0 auto;
  padding: var(--space-6);
}

/* Hero */
.student-hero {
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
.hero-meta {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}
.hero-badge {
  display: inline-flex;
  align-items: center;
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  background: var(--color-bg-secondary);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}
.hero-badge--semester { color: var(--color-accent); border-color: rgba(0,113,227,0.2); }
.hero-badge--major { color: var(--color-success); border-color: rgba(52,199,89,0.2); }

/* Grid */
.student-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-6);
  align-items: start;
}
@media (max-width: 768px) {
  .student-grid { grid-template-columns: 1fr; }
}

/* Cards */
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
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-5) var(--space-6) var(--space-3);
}
.card__title {
  font-size: var(--text-lg);
  font-weight: var(--weight-bold);
}
.card__count {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  background: var(--color-bg-secondary);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-full);
}
.card__search { padding: 0 var(--space-6) var(--space-3); }
.card__body {
  max-height: 520px;
  overflow-y: auto;
  padding: 0 var(--space-6) var(--space-6);
}

/* Course Items */
.course-item, .enroll-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  margin-bottom: var(--space-2);
  transition: all var(--duration-fast) var(--ease-default);
}
.course-item:hover, .enroll-item:hover {
  border-color: var(--color-border-strong);
  background: var(--color-bg-elevated);
  box-shadow: var(--shadow-xs);
}
.course-item--disabled { opacity: 0.55; pointer-events: none; }

.course-item__code, .enroll-item__code {
  font-size: var(--text-xs);
  font-weight: var(--weight-bold);
  color: var(--color-accent);
  text-transform: uppercase;
  margin-bottom: var(--space-1);
}
.course-item__name, .enroll-item__name {
  font-size: var(--text-md);
  font-weight: var(--weight-semibold);
  margin-bottom: var(--space-1);
}
.course-item__meta, .enroll-item__meta {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}
.meta-tag {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
}

/* Buttons & badges */
.enroll-btn {
  padding: var(--space-1) var(--space-4);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  background: var(--color-accent);
  color: white;
  transition: all var(--duration-fast) var(--ease-default);
  min-width: 56px;
}
.enroll-btn:hover:not(:disabled) { background: var(--color-accent-hover); }
.enroll-btn:disabled { background: var(--color-border); color: var(--color-text-tertiary); cursor: not-allowed; }
.drop-btn {
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-md);
  font-size: var(--text-xs);
  font-weight: var(--weight-medium);
  color: var(--color-danger);
  border: 1px solid rgba(255,59,48,0.2);
  transition: all var(--duration-fast) var(--ease-default);
}
.drop-btn:hover:not(:disabled) { background: var(--color-danger-light); }
.course-capacity { font-size: var(--text-xs); color: var(--color-text-tertiary); margin-bottom: var(--space-2); text-align: center; }
.course-capacity.is-full { color: var(--color-danger); font-weight: var(--weight-semibold); }

.grade-badge {
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: var(--text-sm);
  font-weight: var(--weight-bold);
  text-align: center;
  min-width: 64px;
  margin-bottom: var(--space-2);
}
.grade-badge.is-excellent { color: var(--color-success); background: var(--color-success-light); }
.grade-badge.is-pass { color: var(--color-accent); background: var(--color-accent-light); }
.grade-badge.is-fail { color: var(--color-danger); background: var(--color-danger-light); }

/* Filter select */
.filter-select {
  padding: var(--space-1) var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--text-xs);
  background: var(--color-bg-elevated);
  color: var(--color-text-primary);
  outline: none;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0,0,0,0.3);
  backdrop-filter: var(--blur-subtle);
  padding: var(--space-6);
}
.modal-card {
  background: var(--color-bg-elevated);
  border-radius: var(--radius-xl);
  padding: var(--space-8);
  max-width: 400px;
  width: 100%;
  box-shadow: var(--shadow-2xl);
  border: 1px solid var(--color-border);
}
.modal-card h3 { font-size: var(--text-lg); font-weight: var(--weight-bold); margin-bottom: var(--space-6); }
.modal-form { display: flex; flex-direction: column; gap: var(--space-4); }
.modal-actions { display: flex; gap: var(--space-3); justify-content: flex-end; margin-top: var(--space-4); }
.btn-save {
  padding: var(--space-2) var(--space-5);
  background: var(--color-accent);
  color: white;
  border-radius: var(--radius-md);
  font-weight: var(--weight-semibold);
  font-size: var(--text-sm);
}
.btn-cancel {
  padding: var(--space-2) var(--space-5);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-weight: var(--weight-medium);
  font-size: var(--text-sm);
}

/* Reuse field styles from login */
.login-field__label {
  display: block;
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-2);
}
.login-field__input {
  width: 100%;
  padding: var(--space-3) var(--space-4);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--text-md);
  background: var(--color-bg-elevated);
  outline: none;
  transition: border-color var(--duration-fast);
}
.login-field__input:focus {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px var(--color-accent-light);
}
.login-error {
  padding: var(--space-2) var(--space-3);
  background: var(--color-danger-light);
  border-radius: var(--radius-md);
  color: var(--color-danger);
  font-size: var(--text-sm);
}
</style>
