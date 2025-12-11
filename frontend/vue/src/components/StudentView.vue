<template>
  <div class="student-page">
    <header class="hero">
      <div class="user-info">
        <h1>👨‍🎓 学生界面</h1>
        <p>欢迎，<strong>{{ user.name }}</strong> ({{ user.student_no }})</p>
      </div>
      <div class="actions">
        <button @click="showChangePassword = true" class="btn-secondary">修改密码</button>
        <button @click="handleLogout" class="btn-logout">退出登录</button>
      </div>
    </header>

    <div class="content-grid">
      <!-- 可选课程 -->
      <section class="card">
        <h2>📚 可选课程</h2>
        <div class="course-list">
          <div v-if="availableCourses.length === 0" class="empty">暂无可选课程</div>
          <div v-for="c in availableCourses" :key="c.id" class="course-item">
            <div class="course-info">
              <div class="course-code">{{ c.course_code }}</div>
              <div class="course-details">
                <div class="course-name">{{ c.name }}</div>
                <div class="course-meta">
                  教师: {{ c.teacher_name || '待定' }} · {{ c.credit }}学分 · 
                  已选{{ c.enrolled_count }}/{{ c.capacity }}
                </div>
              </div>
            </div>
            <button @click="enrollCourse(c.id)" class="btn-enroll">选课</button>
          </div>
        </div>
      </section>

      <!-- 我的选课 -->
      <section class="card">
        <h2>✅ 我的选课</h2>
        <div class="enrollment-list">
          <div v-if="myEnrollments.length === 0" class="empty">暂无选课记录</div>
          <div v-for="e in myEnrollments" :key="e.id" class="enrollment-item">
            <div class="enrollment-info">
              <div class="course-badge">{{ e.course_code }}</div>
              <div class="enrollment-details">
                <div class="enrollment-name">{{ e.course_name }}</div>
                <div class="enrollment-meta">
                  {{ e.teacher_name || '暂无教师' }} · {{ e.credit }}学分
                  <span v-if="e.grade !== null" class="grade-badge">成绩: {{ e.grade }}</span>
                  <span v-else class="grade-badge pending">未评分</span>
                </div>
              </div>
            </div>
            <button @click="dropCourse(e.id)" class="btn-drop">退课</button>
          </div>
        </div>
      </section>
    </div>

    <!-- 修改密码弹窗 -->
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
          <div class="error-message" v-if="errorMsg">{{ errorMsg }}</div>
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
import { ref, reactive, onMounted } from 'vue'

const props = defineProps({
  user: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['logout'])

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api'

const availableCourses = ref([])
const myEnrollments = ref([])
const showChangePassword = ref(false)
const errorMsg = ref('')

const passwordForm = reactive({
  old_password: '',
  new_password: ''
})

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

async function loadData() {
  try {
    const [available, enrolled] = await Promise.all([
      api('/student/courses/available'),
      api('/student/enrollments')
    ])
    availableCourses.value = available
    myEnrollments.value = enrolled
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

async function enrollCourse(courseId) {
  try {
    await api('/student/enrollments', {
      method: 'POST',
      body: JSON.stringify({ course_id: courseId })
    })
    await loadData()
  } catch (error) {
    alert(error.message)
  }
}

async function dropCourse(enrollId) {
  if (!confirm('确定要退课吗？')) return
  
  try {
    await api(`/student/enrollments/${enrollId}`, { method: 'DELETE' })
    await loadData()
  } catch (error) {
    alert(error.message)
  }
}

async function changePassword() {
  errorMsg.value = ''
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
    errorMsg.value = error.message
  }
}

function handleLogout() {
  emit('logout')
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.student-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

.hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  padding: 24px 32px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 24px;
}

.user-info h1 {
  margin: 0 0 4px 0;
  font-size: 24px;
  font-weight: 700;
}

.user-info p {
  margin: 0;
  color: #64748b;
  font-size: 14px;
}

.actions {
  display: flex;
  gap: 12px;
}

.btn-secondary {
  padding: 8px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  color: #0f172a;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}

.btn-logout {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  background: #ef4444;
  color: white;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-logout:hover {
  background: #dc2626;
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 24px;
}

.card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.card h2 {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 700;
}

.course-list, .enrollment-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.empty {
  text-align: center;
  padding: 32px;
  color: #94a3b8;
  font-size: 14px;
}

.course-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  transition: all 0.2s;
}

.course-item:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
}

.course-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.course-code, .course-badge {
  padding: 6px 10px;
  border-radius: 8px;
  background: #dbeafe;
  color: #1e40af;
  font-weight: 700;
  font-size: 12px;
  white-space: nowrap;
}

.course-details, .enrollment-details {
  flex: 1;
  min-width: 0;
}

.course-name, .enrollment-name {
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.course-meta, .enrollment-meta {
  font-size: 12px;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.btn-enroll {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-enroll:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.enrollment-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  transition: all 0.2s;
}

.enrollment-item:hover {
  border-color: #10b981;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.1);
}

.enrollment-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.grade-badge {
  padding: 4px 8px;
  border-radius: 6px;
  background: #dcfce7;
  color: #166534;
  font-weight: 700;
  font-size: 11px;
  white-space: nowrap;
}

.grade-badge.pending {
  background: #fef3c7;
  color: #92400e;
}

.btn-drop {
  padding: 6px 12px;
  border: 1px solid #fee2e2;
  border-radius: 8px;
  background: #fef2f2;
  color: #b91c1c;
  font-weight: 600;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-drop:hover {
  background: #fee2e2;
}

/* Modal styles */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 16px;
  padding: 32px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
}

.modal-content h3 {
  margin: 0 0 20px 0;
  font-size: 20px;
  font-weight: 700;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 600;
  font-size: 13px;
  color: #0f172a;
}

.form-group input {
  width: 100%;
  padding: 10px 12px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: all 0.2s;
  box-sizing: border-box;
}

.form-group input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.error-message {
  padding: 10px;
  background: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #b91c1c;
  font-size: 12px;
  margin-bottom: 16px;
}

.modal-actions {
  display: flex;
  gap: 12px;
}

.btn-cancel {
  flex: 1;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  font-weight: 600;
  cursor: pointer;
}

.btn-primary {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  font-weight: 600;
  cursor: pointer;
}

@media (max-width: 768px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
  
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
}
</style>
