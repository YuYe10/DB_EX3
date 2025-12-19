<template>
  <div class="teacher-page">
    <header class="hero">
      <div class="user-info">
        <h1>👨‍🏫 教师界面</h1>
        <p>欢迎，<strong>{{ user.name }}</strong> ({{ user.teacher_no }})</p>
      </div>
      <div class="actions">
        <button @click="showChangePassword = true" class="btn-secondary">修改密码</button>
        <button @click="handleLogout" class="btn-logout">退出登录</button>
      </div>
    </header>

    <section class="card">
      <h2>📖 我的授课</h2>
      <div v-if="myCourses.length === 0" class="empty">暂无授课课程</div>
      <div v-else class="course-tabs">
        <div class="tab-buttons">
          <button 
            v-for="c in myCourses" 
            :key="c.id"
            @click="selectCourse(c.id)"
            :class="{ active: selectedCourseId === c.id }"
            class="tab-btn"
          >
            {{ c.name }} ({{ c.enrolled_count }}人)
          </button>
        </div>
        
        <div v-if="selectedCourse" class="tab-content">
          <div class="course-header">
            <h3>{{ selectedCourse.name }}</h3>
            <p class="course-detail">
              {{ selectedCourse.course_code }} · {{ selectedCourse.credit }}学分 · 
              容量{{ selectedCourse.capacity }}
            </p>
          </div>

          <div class="course-actions">
            <button class="btn-primary" @click="exportGrades" :disabled="!selectedCourseId || exportLoading">
              {{ exportLoading ? '导出中...' : '导出成绩Excel' }}
            </button>
            <label class="upload-btn">
              <input type="file" accept=".xlsx,.xls" @change="importRoster" :disabled="importLoading">
              <span>{{ importLoading ? '正在导入...' : '导入课程名单' }}</span>
            </label>
            <button class="btn-secondary" @click="downloadSample" :disabled="importLoading || exportLoading">
              下载示例名单
            </button>
          </div>
          <p class="error" v-if="exportError">{{ exportError }}</p>
          <p class="error" v-if="importError">{{ importError }}</p>
          <div class="import-summary" v-if="importSummary">
            <p>课程：{{ importSummary.course_name }} ({{ importSummary.course_code }})</p>
            <p>
              学生新增 {{ importSummary.students_created }}，跳过 {{ importSummary.students_skipped }}；
              选课新增 {{ importSummary.enrollments_created }}，跳过 {{ importSummary.enrollments_skipped }}
            </p>
            <p>课程创建 {{ importSummary.course_created }}，更新 {{ importSummary.course_updated }}</p>
          </div>

          <section class="card stats-card" v-if="courseStats.length">
            <header class="card-header">
              <h3>📊 我的课程成绩概览</h3>
              <p class="card-desc">展示授课课程的平均分、及格率、优秀率</p>
            </header>
            <div class="stats-grid">
              <div class="stat-item" v-for="c in courseStats" :key="c.id">
                <div class="stat-item-header">
                  <span class="stat-code">{{ c.course_code }}</span>
                  <span class="stat-name">{{ c.name }}</span>
                </div>
                <div class="stat-value-large">{{ c.avg_grade ?? '无' }}</div>
                <div class="stat-meta">
                  <span class="stat-chip">📈 及格率 {{ formatRate(c.pass_rate) }}</span>
                  <span class="stat-chip">🌟 优秀率 {{ formatRate(c.excellent_rate) }}</span>
                  <span class="stat-chip">👥 选课人数 {{ c.enrolled_count ?? 0 }}</span>
                </div>
              </div>
            </div>
          </section>
          
          <div class="student-list">
            <div v-if="students.length === 0" class="empty-small">暂无学生选课</div>
            <div v-else class="student-table">
              <table>
                <thead>
                  <tr>
                    <th>学号</th>
                    <th>姓名</th>
                    <th>专业</th>
                    <th>最终成绩</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  <template v-for="s in students" :key="s.id">
                    <tr>
                      <td>{{ s.student_no }}</td>
                      <td><strong>{{ s.student_name }}</strong></td>
                      <td>{{ s.major || '-' }}</td>
                      <td>
                        <span v-if="s.final_grade !== null" class="grade-display">{{ s.final_grade }}</span>
                        <span v-else-if="s.grade !== null" class="grade-display">{{ s.grade }}</span>
                        <span v-else class="grade-display empty">未评分</span>
                      </td>
                      <td>
                        <button @click="toggleGradeEditor(s.id)" class="btn-grade">{{ expandedGradeEditors[s.id] ? '收起' : '编辑成绩' }}</button>
                      </td>
                    </tr>
                    <tr v-if="expandedGradeEditors[s.id]" class="grade-editor-row">
                      <td colspan="5">
                        <div class="grade-editor-inline">
                          <div class="editor-group">
                            <label>平时成绩 (0-100)</label>
                            <input 
                              type="number" 
                              min="0" 
                              max="100" 
                              step="0.5"
                              :value="gradeEditForm[s.id]?.ordinary_score ?? ''"
                              @input="(e) => { if (!gradeEditForm[s.id]) gradeEditForm[s.id] = {}; gradeEditForm[s.id].ordinary_score = e.target.value ? parseFloat(e.target.value) : null; }"
                              placeholder="输入平时成绩"
                            />
                          </div>
                          <div class="editor-group">
                            <label>期末成绩 (0-100)</label>
                            <input 
                              type="number" 
                              min="0" 
                              max="100" 
                              step="0.5"
                              :value="gradeEditForm[s.id]?.final_score ?? ''"
                              @input="(e) => { if (!gradeEditForm[s.id]) gradeEditForm[s.id] = {}; gradeEditForm[s.id].final_score = e.target.value ? parseFloat(e.target.value) : null; }"
                              placeholder="输入期末成绩"
                            />
                          </div>
                          <div class="editor-group">
                            <label>平时占比</label>
                            <input 
                              type="number" 
                              min="0" 
                              max="1" 
                              step="0.01"
                              :value="gradeEditForm[s.id]?.ordinary_weight ?? 0.5"
                              @input="(e) => { if (!gradeEditForm[s.id]) gradeEditForm[s.id] = {}; gradeEditForm[s.id].ordinary_weight = e.target.value ? parseFloat(e.target.value) : 0.5; }"
                              @change="() => autoCalcWeight(s.id, 'ordinary')"
                              placeholder="0.5"
                            />
                            <span class="weight-percent">{{ (Number(gradeEditForm[s.id]?.ordinary_weight ?? 0.5) * 100).toFixed(0) }}%</span>
                          </div>
                          <div class="editor-group">
                            <label>期末占比</label>
                            <input 
                              type="number" 
                              min="0" 
                              max="1" 
                              step="0.01"
                              :value="gradeEditForm[s.id]?.final_weight ?? 0.5"
                              @input="(e) => { if (!gradeEditForm[s.id]) gradeEditForm[s.id] = {}; gradeEditForm[s.id].final_weight = e.target.value ? parseFloat(e.target.value) : 0.5; }"
                              @change="() => autoCalcWeight(s.id, 'final')"
                              placeholder="0.5"
                            />
                            <span class="weight-percent">{{ (Number(gradeEditForm[s.id]?.final_weight ?? 0.5) * 100).toFixed(0) }}%</span>
                          </div>
                          <div class="weight-sum">占比和: {{ (Number(gradeEditForm[s.id]?.ordinary_weight ?? 0.5) + Number(gradeEditForm[s.id]?.final_weight ?? 0.5)).toFixed(2) }}</div>
                          <div class="preview-grade">预计最终成绩: {{ calcPreviewGrade(s.id) }}</div>
                          <div class="editor-actions">
                            <button type="button" @click="updateGrades(s.id)" class="btn-primary-sm">✓ 保存</button>
                            <button type="button" @click="toggleGradeEditor(s.id)" class="btn-cancel-sm">取消</button>
                          </div>
                        </div>
                      </td>
                    </tr>
                  </template>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </section>

    <div v-if="showGradeModal" class="modal" @click.self="showGradeModal = false">
      <div class="modal-content">
        <h3>录入成绩</h3>
        <div class="student-info-box">
          <p><strong>学生:</strong> {{ currentStudent?.student_name }} ({{ currentStudent?.student_no }})</p>
          <p><strong>课程:</strong> {{ selectedCourse?.name }}</p>
        </div>
        <form @submit.prevent="submitGrade">
          <div class="form-group">
            <label>成绩 (0-100)</label>
            <input 
              v-model.number="gradeForm.grade" 
              type="number" 
              min="0" 
              max="100" 
              step="0.5"
              required 
              placeholder="请输入成绩"
            />
          </div>
          <div class="error-message" v-if="errorMsg">{{ errorMsg }}</div>
          <div class="modal-actions">
            <button type="button" @click="showGradeModal = false" class="btn-cancel">取消</button>
            <button type="submit" class="btn-primary">提交</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showChangePassword" class="modal" @click.self="showChangePassword = false">
      <div class="modal-content">
        <h3>修改密码</h3>
        <form @submit.prevent="changePassword">
          <div class="form-group">
            <label>旧密码</label>
            <input v-model="passwordForm.old_password" type="password" required />
          </div>
          <div class="form-group">
            <label>新密码</label>
            <input v-model="passwordForm.new_password" type="password" required />
          </div>
          <div class="error-message" v-if="pwdErrorMsg">{{ pwdErrorMsg }}</div>
          <div class="modal-actions">
            <button type="button" @click="showChangePassword = false" class="btn-cancel">取消</button>
            <button type="submit" class="btn-primary">确认修改</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'

const props = defineProps({
  user: { type: Object, required: true }
})

const emit = defineEmits(['logout'])
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api'

const myCourses = ref([])
const selectedCourseId = ref(null)
const students = ref([])
const showGradeModal = ref(false)
const showChangePassword = ref(false)
const currentStudent = ref(null)
const errorMsg = ref('')
const pwdErrorMsg = ref('')
const gradeForm = reactive({ grade: null })
const passwordForm = reactive({ old_password: '', new_password: '' })
const exportLoading = ref(false)
const exportError = ref('')
const importLoading = ref(false)
const importError = ref('')
const importSummary = ref(null)
const courseStats = ref([])
const expandedGradeEditors = ref({})
const gradeEditForm = ref({})

const selectedCourse = computed(() => myCourses.value.find(c => c.id === selectedCourseId.value))

async function api(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    ...options
  })
  if (!res.ok) {
    const data = await res.json()
    throw new Error(data.message || '操作失败')
  }
  return res.json()
}

const timestamp = () => {
  const d = new Date()
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}-${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}`
}

async function loadCourses() {
  try {
    myCourses.value = await api('/teacher/courses')
    if (myCourses.value.length > 0 && !selectedCourseId.value) {
      selectCourse(myCourses.value[0].id)
    }
    await loadCourseStats()
  } catch (error) {
    console.error('加载课程失败:', error)
  }
}

async function loadCourseStats() {
  try {
    courseStats.value = await api('/teacher/courses/stats')
  } catch (error) {
    console.error('加载课程统计失败:', error)
  }
}

async function selectCourse(courseId) {
  selectedCourseId.value = courseId
  try {
    students.value = await api(`/teacher/courses/${courseId}/students`)
  } catch (error) {
    console.error('加载学生列表失败:', error)
  }
}

function toggleGradeEditor(enrollmentId) {
  const current = expandedGradeEditors.value[enrollmentId] || false
  expandedGradeEditors.value = { ...expandedGradeEditors.value, [enrollmentId]: !current }
  
  if (!current) {
    const enrollment = students.value.find(s => s.id === enrollmentId)
    if (enrollment) {
      gradeEditForm.value = {
        ...gradeEditForm.value,
        [enrollmentId]: {
          ordinary_score: enrollment.ordinary_score ?? null,
          final_score: enrollment.final_score ?? null,
          ordinary_weight: enrollment.ordinary_weight ?? 0.5,
          final_weight: enrollment.final_weight ?? 0.5,
        }
      }
    }
  }
}

function autoCalcWeight(enrollmentId, changedField) {
  const form = gradeEditForm.value[enrollmentId]
  if (!form) return
  
  if (changedField === 'ordinary') {
    const ow = form.ordinary_weight
    if (ow !== undefined && ow !== null) {
      form.final_weight = Math.round((1 - ow) * 100) / 100
    }
  } else if (changedField === 'final') {
    const fw = form.final_weight
    if (fw !== undefined && fw !== null) {
      form.ordinary_weight = Math.round((1 - fw) * 100) / 100
    }
  }
}

function calcPreviewGrade(enrollmentId) {
  const form = gradeEditForm.value[enrollmentId]
  if (!form) return '—'
  
  const os = form.ordinary_score
  const fs = form.final_score
  const ow = form.ordinary_weight || 0.5
  const fw = form.final_weight || 0.5
  
  if (os === null || os === undefined || fs === null || fs === undefined) {
    return '—'
  }
  
  const final = Number(os) * Number(ow) + Number(fs) * Number(fw)
  return final.toFixed(1)
}

function formatRate(val) {
  if (val === null || val === undefined) return '—'
  const num = Number(val)
  if (Number.isNaN(num)) return '—'
  return `${num.toFixed(2)}%`
}

async function updateGrades(enrollmentId) {
  const form = gradeEditForm.value[enrollmentId]
  if (!form) return
  
  const totalWeight = (form.ordinary_weight || 0.5) + (form.final_weight || 0.5)
  if (Math.abs(totalWeight - 1) > 0.01) {
    alert('占比和必须等于 1，当前为: ' + totalWeight.toFixed(2))
    return
  }
  
  try {
    const payload = {
      ordinary_score: form.ordinary_score,
      final_score: form.final_score,
      ordinary_weight: form.ordinary_weight,
      final_weight: form.final_weight,
    }
    
    await api(`/teacher/enrollments/${enrollmentId}/grades`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    })
    
    alert('成绩更新成功')
    toggleGradeEditor(enrollmentId)
    await selectCourse(selectedCourseId.value)
  } catch (error) {
    alert(`成绩更新失败: ${error.message}`)
  }
}

function openGradeModal(student) {
  currentStudent.value = student
  gradeForm.grade = student.grade
  showGradeModal.value = true
  errorMsg.value = ''
}

async function submitGrade() {
  errorMsg.value = ''
  try {
    await api(`/teacher/enrollments/${currentStudent.value.id}/grade`, {
      method: 'PUT',
      body: JSON.stringify({ grade: gradeForm.grade })
    })
    showGradeModal.value = false
    await selectCourse(selectedCourseId.value)
  } catch (error) {
    errorMsg.value = error.message
  }
}

async function changePassword() {
  pwdErrorMsg.value = ''
  try {
    await api('/auth/change-password', {
      method: 'POST',
      body: JSON.stringify(passwordForm)
    })
    alert('密码修改成功')
    showChangePassword.value = false
    passwordForm.old_password = ''
    passwordForm.new_password = ''
  } catch (error) {
    pwdErrorMsg.value = error.message
  }
}

function handleLogout() {
  emit('logout')
}

async function exportGrades() {
  if (!selectedCourseId.value) return
  exportError.value = ''
  exportLoading.value = true
  try {
    const res = await fetch(`${API_BASE}/teacher/courses/${selectedCourseId.value}/grades/export`, {
      credentials: 'include'
    })
    if (!res.ok) throw new Error(await res.text())
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const cd = res.headers.get('Content-Disposition') || ''
    let filename = ''
    const match = cd.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
    if (match && match[1]) {
      filename = match[1].replace(/['"]/g, '')
    }
    if (!filename) {
      const course = selectedCourse.value
      const courseName = (course?.name || '课程').replace(/\//g, '-')
      const teacherName = (props.user?.name || '教师').replace(/\//g, '-')
      filename = `${courseName}-${teacherName}-${timestamp()}.xlsx`
    }
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  } catch (error) {
    exportError.value = error.message
  } finally {
    exportLoading.value = false
  }
}

async function importRoster(event) {
  const file = event.target.files?.[0]
  if (!file) return
  importError.value = ''
  importSummary.value = null
  importLoading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    const res = await fetch(`${API_BASE}/teacher/courses/import`, {
      method: 'POST',
      credentials: 'include',
      body: formData
    })
    const data = await res.json()
    if (!res.ok || data.success === false) throw new Error(data.message || '导入失败')
    importSummary.value = data.summary
    await loadCourses()
    if (data.summary?.course_id) {
      await selectCourse(data.summary.course_id)
    }
  } catch (error) {
    importError.value = error.message
  } finally {
    importLoading.value = false
    event.target.value = ''
  }
}

async function downloadSample() {
  importError.value = ''
  exportError.value = ''
  try {
    const res = await fetch(`${API_BASE}/teacher/courses/import/sample`, {
      credentials: 'include'
    })
    if (!res.ok) throw new Error(await res.text())
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const cd = res.headers.get('Content-Disposition') || ''
    let filename = '课程名单示例.xlsx'
    const match = cd.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
    if (match && match[1]) filename = match[1].replace(/['"]/g, '')
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  } catch (error) {
    importError.value = error.message
  }
}

onMounted(() => loadCourses())
</script>

<style scoped>
.teacher-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Inter', system-ui, sans-serif;
}

.hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 20px 28px;
  background: white;
  border-radius: 14px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.06);
  margin-bottom: 20px;
}

.user-info h1 {
  margin: 0 0 4px 0;
  font-size: 22px;
  font-weight: 700;
}

.user-info p {
  margin: 0;
  color: #64748b;
  font-size: 13px;
}

.actions {
  display: flex;
  gap: 10px;
}

.btn-secondary, .btn-logout {
  padding: 7px 14px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary {
  border: 1px solid #e2e8f0;
  background: white;
  color: #0f172a;
}

.btn-secondary:hover {
  background: #f8fafc;
}

.btn-logout {
  border: none;
  background: #ef4444;
  color: white;
}

.btn-logout:hover {
  background: #dc2626;
}

.card {
  background: white;
  border-radius: 14px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.06);
}

.card h2 {
  margin: 0 0 16px 0;
  font-size: 17px;
  font-weight: 700;
}

.empty, .empty-small {
  text-align: center;
  padding: 28px;
  color: #94a3b8;
  font-size: 13px;
}

.empty-small {
  padding: 16px;
}

.tab-buttons {
  display: flex;
  gap: 6px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.tab-btn {
  padding: 8px 14px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  color: #64748b;
  font-weight: 600;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover {
  border-color: #cbd5e1;
  background: #f8fafc;
}

.tab-btn.active {
  border-color: #8b5cf6;
  background: #8b5cf6;
  color: white;
}

.course-header {
  padding: 14px;
  background: #f8fafc;
  border-radius: 8px;
  margin-bottom: 16px;
}

.course-header h3 {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 700;
}

.course-detail {
  margin: 0;
  color: #64748b;
  font-size: 12px;
}

.student-table {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

thead {
  background: #f8fafc;
}

th {
  padding: 10px;
  text-align: left;
  font-weight: 700;
  font-size: 11px;
  color: #64748b;
  text-transform: uppercase;
}

td {
  padding: 10px;
  border-bottom: 1px solid #e2e8f0;
}

tbody tr:hover {
  background: #f8fafc;
}

.grade-display {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 6px;
  background: #dcfce7;
  color: #166534;
  font-weight: 700;
  font-size: 12px;
}

.grade-display.empty {
  background: #fef3c7;
  color: #92400e;
}

.course-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin: 12px 0;
}

.upload-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 10px;
  background: #6366f1;
  color: #fff;
  cursor: pointer;
  font-weight: 700;
  border: none;
  box-shadow: 0 8px 18px rgba(99, 102, 241, 0.25);
  position: relative;
  overflow: hidden;
}

.upload-btn input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.error {
  color: #b91c1c;
  font-size: 13px;
  margin: 4px 0;
}

.import-summary {
  background: #ecfdf3;
  border: 1px solid #bbf7d0;
  color: #166534;
  padding: 10px 12px;
  border-radius: 10px;
  font-size: 13px;
  margin-bottom: 10px;
}

.btn-grade {
  padding: 5px 10px;
  border: none;
  border-radius: 6px;
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  color: white;
  font-weight: 600;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-grade:hover {
  transform: translateY(-1px);
  box-shadow: 0 3px 10px rgba(139,92,246,0.3);
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 14px;
  padding: 28px;
  width: 100%;
  max-width: 380px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.3);
}

.modal-content h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 700;
}

.student-info-box {
  padding: 10px 14px;
  background: #f8fafc;
  border-radius: 8px;
  margin-bottom: 14px;
}

.student-info-box p {
  margin: 3px 0;
  font-size: 12px;
  color: #64748b;
}

.form-group {
  margin-bottom: 14px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
  font-size: 12px;
  color: #0f172a;
}

.form-group input {
  width: 100%;
  padding: 9px 11px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 13px;
  outline: none;
  transition: all 0.2s;
  box-sizing: border-box;
}

.form-group input:focus {
  border-color: #8b5cf6;
  box-shadow: 0 0 0 3px rgba(139,92,246,0.1);
}

.error-message {
  padding: 8px;
  background: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  color: #b91c1c;
  font-size: 11px;
  margin-bottom: 12px;
}

.modal-actions {
  display: flex;
  gap: 10px;
}

.btn-cancel, .btn-primary {
  flex: 1;
  padding: 9px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
}

.btn-cancel {
  border: 1px solid #e2e8f0;
  background: white;
  color: #0f172a;
}

.btn-primary {
  border: none;
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  color: white;
}

/* 课程统计样式 */
.stats-card {
  margin-top: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-top: 14px;
}

.stat-item {
  padding: 18px;
  border-radius: 14px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 2px solid #7dd3fc;
  transition: all 0.3s ease;
}

.stat-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
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
  font-size: 32px;
  font-weight: 800;
  background: linear-gradient(135deg, #0284c7 0%, #06b6d4 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 6px;
  margin-top: 10px;
}

.stat-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 10px;
  border-radius: 10px;
  background: #e0f2fe;
  color: #0c4a6e;
  font-weight: 600;
  font-size: 12px;
  border: 1px solid #bae6fd;
}

/* 成绩编辑器样式 */
.grade-editor-row {
  background: #f0f9ff;
}

.grade-editor-row td {
  padding: 0;
}

.grade-editor-inline {
  padding: 16px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
  align-items: flex-end;
}

.editor-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.editor-group label {
  font-size: 11px;
  font-weight: 600;
  color: #0c4a6e;
}

.editor-group input {
  padding: 8px 10px;
  border: 1px solid #bfdbfe;
  border-radius: 6px;
  font-size: 12px;
  background: white;
}

.editor-group input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.weight-percent {
  display: inline-block;
  min-width: 40px;
  text-align: right;
  font-weight: 600;
  color: #1e40af;
  font-size: 11px;
  margin-left: 4px;
}

.weight-sum {
  grid-column: 1 / -1;
  padding: 8px;
  background: white;
  border: 1px solid #bfdbfe;
  border-radius: 6px;
  font-size: 12px;
  color: #0c4a6e;
  font-weight: 600;
}

.preview-grade {
  grid-column: 1 / -1;
  padding: 8px;
  background: #dcfce7;
  border: 1px solid #86efac;
  border-radius: 6px;
  font-size: 12px;
  color: #166534;
  font-weight: 600;
}

.editor-actions {
  grid-column: 1 / -1;
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  margin-top: 4px;
}

.btn-primary-sm, .btn-cancel-sm {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn-primary-sm {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  color: white;
}

.btn-primary-sm:hover {
  transform: translateY(-1px);
  box-shadow: 0 3px 10px rgba(139,92,246,0.3);
}

.btn-cancel-sm {
  background: #f3f4f6;
  color: #374151;
}

.btn-cancel-sm:hover {
  background: #e5e7eb;
}

@media (max-width: 768px) {
  .hero {
    flex-direction: column;
    align-items: flex-start;
  }
  .actions {
    width: 100%;
  }
  .actions button {
    flex: 1;
  }
  table {
    font-size: 11px;
  }
  th, td {
    padding: 7px;
  }
}
</style>
