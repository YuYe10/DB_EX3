<template>
  <div id="app">
    <Login v-if="!currentUser" @login-success="handleLoginSuccess" />
    <StudentView v-else-if="currentUser.role === 'student'" :user="currentUser" @logout="handleLogout" />
    <TeacherView v-else-if="currentUser.role === 'teacher'" :user="currentUser" @logout="handleLogout" />
    <AdminView v-else-if="currentUser.role === 'admin'" :user="currentUser" @logout="handleLogout" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Login from './components/Login.vue'
import StudentView from './components/StudentView.vue'
import TeacherView from './components/TeacherView.vue'
import AdminView from './components/AdminView.vue'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api'
const currentUser = ref(null)

async function checkAuth() {
  try {
    const res = await fetch(`${API_BASE}/auth/me`, {
      credentials: 'include'
    })
    if (res.ok) {
      const user = await res.json()
      currentUser.value = user
    }
  } catch (error) {
    console.log('未登录')
  }
}

function handleLoginSuccess(user) {
  currentUser.value = user
}

async function handleLogout() {
  try {
    await fetch(`${API_BASE}/auth/logout`, {
      method: 'POST',
      credentials: 'include'
    })
  } catch (error) {
    console.error('登出失败:', error)
  }
  currentUser.value = null
}

onMounted(() => {
  checkAuth()
})
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+SC:wght@400;500;600;700&display=swap');

* {
  box-sizing: border-box;
}

body {
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

#app {
  min-height: 100vh;
}
</style>
