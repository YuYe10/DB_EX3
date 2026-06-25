<template>
  <div id="app" class="app-shell">
    <!-- Not authenticated: show login -->
    <template v-if="!currentUser">
      <Login @login-success="handleLoginSuccess" />
    </template>

    <!-- Authenticated: show app with header -->
    <template v-else>
      <AppHeader :user="currentUser" @logout="handleLogout" />

      <main class="app-main">
        <Transition name="page-fade" mode="out-in">
          <StudentView v-if="currentUser.role === 'student'" :key="'student'" :user="currentUser" @logout="handleLogout" />
          <TeacherView v-else-if="currentUser.role === 'teacher'" :key="'teacher'" :user="currentUser" @logout="handleLogout" />
          <AdminView v-else-if="currentUser.role === 'admin'" :key="'admin'" :user="currentUser" @logout="handleLogout" />
        </Transition>
      </main>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Login from './views/Login.vue'
import StudentView from './views/StudentView.vue'
import TeacherView from './views/TeacherView.vue'
import AdminView from './views/AdminView.vue'
import AppHeader from './components/shared/AppHeader.vue'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api'

const currentUser = ref(null)

async function checkAuth() {
  try {
    const res = await fetch(`${API_BASE}/auth/me`, { credentials: 'include' })
    if (res.ok) {
      const data = await res.json()
      currentUser.value = data.user || data
    }
  } catch {
    // Backend not reachable — stay on login page
  }
}

function handleLoginSuccess(user) {
  currentUser.value = user
}

async function handleLogout() {
  try {
    await fetch(`${API_BASE}/auth/logout`, { method: 'POST', credentials: 'include' })
  } catch {
    // Proceed with client-side logout even if API fails
  }
  currentUser.value = null
}

onMounted(checkAuth)
</script>

<style>
/* ============================================================
 * Global App Styles — macOS-inspired design system
 * ============================================================ */

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+SC:wght@400;500;700&display=swap');

/* Reset */
*,
*::before,
*::after {
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
  font-family: 'Inter', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'SF Pro Display', system-ui, sans-serif;
  font-size: 0.875rem;
  line-height: 1.5;
  color: #1d1d1f;
  background: #f5f5f7;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  overflow-x: hidden;
}

/* App Shell */
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-main {
  flex: 1;
  padding-bottom: 64px;
}

/* Selection highlight */
::selection {
  background: rgba(0, 113, 227, 0.15);
  color: #1d1d1f;
}

/* Custom scrollbar — macOS style */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.12);
  border-radius: 9999px;
}
::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.22);
}

/* Focus ring for accessibility */
:focus-visible {
  outline: 2px solid #0071e3;
  outline-offset: 2px;
  border-radius: 6px;
}

/* Utility: visually hidden but screen-reader accessible */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
</style>
