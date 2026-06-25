<template>
  <div class="login-page">
    <div class="login-bg">
      <div class="login-bg__orb login-bg__orb--1" />
      <div class="login-bg__orb login-bg__orb--2" />
      <div class="login-bg__orb login-bg__orb--3" />
    </div>
    <div class="login-card animate-fade-in-scale">
      <div class="login-card__header">
        <div class="login-logo">
          <svg viewBox="0 0 24 24" width="36" height="36" fill="none">
            <rect x="2" y="3" width="20" height="18" rx="4" stroke="currentColor" stroke-width="1.2"/>
            <path d="M7 8h10M7 12h10M7 16h7" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
          </svg>
        </div>
        <h1 class="login-card__title">教务管理系统</h1>
        <p class="login-card__subtitle">登录您的账户以继续</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="login-field">
          <label class="login-field__label">账号</label>
          <input v-model="form.username" required
            placeholder="学号 / 工号 / admin"
            autocomplete="username" autofocus
            class="login-field__input" />
        </div>
        <div class="login-field">
          <label class="login-field__label">密码</label>
          <input v-model="form.password" type="password" required
            placeholder="输入密码"
            autocomplete="current-password"
            class="login-field__input" />
        </div>

        <Transition name="tab-fade">
          <div v-if="errorMsg" class="login-error">{{ errorMsg }}</div>
        </Transition>

        <button type="submit" class="login-btn" :disabled="loading">
          <LoadingSpinner v-if="loading" size="sm" />
          <span v-else>登 录</span>
        </button>
      </form>

      <div class="login-hints">
        <div class="hint-row"><strong>学生</strong> 账号=学号 密码=s+学号</div>
        <div class="hint-row"><strong>教师</strong> 账号=工号 密码=t+工号</div>
        <div class="hint-row"><strong>管理员</strong> 账号=admin 密码=admin@123</div>
      </div>
    </div>
    <p class="login-footer">Student Course Management System</p>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import LoadingSpinner from '../components/shared/LoadingSpinner.vue'

const emit = defineEmits(['login-success'])
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api'

const form = reactive({ username: '', password: '' })
const loading = ref(false)
const errorMsg = ref('')

onMounted(() => {
  const saved = localStorage.getItem('login_username')
  if (saved) form.username = saved
})

async function handleLogin() {
  if (!form.username.trim()) { errorMsg.value = '请输入账号'; return }
  if (!form.password) { errorMsg.value = '请输入密码'; return }

  loading.value = true
  errorMsg.value = ''

  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(form)
    })
    const data = await res.json()
    if (!res.ok) { errorMsg.value = data.message || '登录失败'; return }
    localStorage.setItem('login_username', form.username)
    emit('login-success', data.user)
  } catch {
    errorMsg.value = '网络错误，请检查后端服务'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  padding: var(--space-6);
}

/* Soft orbs background */
.login-bg {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}
.login-bg__orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.3;
  animation: float 8s ease-in-out infinite;
}
.login-bg__orb--1 {
  width: 500px; height: 500px;
  background: radial-gradient(circle, rgba(0,113,227,0.3), transparent);
  top: -15%; left: -10%;
  animation-delay: 0s;
}
.login-bg__orb--2 {
  width: 400px; height: 400px;
  background: radial-gradient(circle, rgba(52,199,89,0.2), transparent);
  bottom: -10%; right: -5%;
  animation-delay: -3s;
}
.login-bg__orb--3 {
  width: 350px; height: 350px;
  background: radial-gradient(circle, rgba(90,200,250,0.25), transparent);
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  animation-delay: -6s;
}

/* Card */
.login-card {
  position: relative;
  z-index: 1;
  background: var(--color-bg-glass);
  backdrop-filter: var(--blur-glass);
  -webkit-backdrop-filter: var(--blur-glass);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-2xl);
  padding: var(--space-12) var(--space-10);
  width: 100%;
  max-width: 400px;
  box-shadow: var(--shadow-glass);
}
@supports not (backdrop-filter: blur(1px)) {
  .login-card { background: rgba(255,255,255,0.92); }
}

.login-card__header {
  text-align: center;
  margin-bottom: var(--space-8);
}
.login-logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: var(--radius-lg);
  background: var(--color-accent);
  color: white;
  margin-bottom: var(--space-4);
}
.login-card__title {
  font-size: var(--text-2xl);
  font-weight: var(--weight-extrabold);
  letter-spacing: var(--tracking-tight);
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}
.login-card__subtitle {
  font-size: var(--text-md);
  color: var(--color-text-secondary);
}

/* Form */
.login-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}
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
  color: var(--color-text-primary);
  transition: all var(--duration-fast) var(--ease-default);
  outline: none;
}
.login-field__input::placeholder { color: var(--color-text-tertiary); }
.login-field__input:focus {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px var(--color-accent-light);
}

.login-error {
  padding: var(--space-3) var(--space-4);
  background: var(--color-danger-light);
  border: 1px solid rgba(255,59,48,0.2);
  border-radius: var(--radius-md);
  color: var(--color-danger);
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  text-align: center;
}

.login-btn {
  width: 100%;
  padding: var(--space-3) var(--space-4);
  background: var(--color-accent);
  color: var(--color-text-inverse);
  border-radius: var(--radius-md);
  font-size: var(--text-md);
  font-weight: var(--weight-semibold);
  letter-spacing: 0.02em;
  transition: all var(--duration-fast) var(--ease-default);
  box-shadow: var(--shadow-button);
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  margin-top: var(--space-2);
}
.login-btn:hover:not(:disabled) {
  background: var(--color-accent-hover);
  box-shadow: var(--shadow-button-hover);
  transform: translateY(-1px);
}
.login-btn:active:not(:disabled) { transform: scale(0.98); }
.login-btn:disabled { opacity: 0.5; cursor: not-allowed; }

/* Hints */
.login-hints {
  margin-top: var(--space-6);
  padding: var(--space-4);
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}
.hint-row {
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-2);
  line-height: 1.6;
}
.hint-row:last-child { margin-bottom: 0; }
.hint-row strong { color: var(--color-text-primary); font-weight: var(--weight-semibold); }

.login-footer {
  position: relative;
  z-index: 1;
  margin-top: var(--space-8);
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
}

@media (max-width: 480px) {
  .login-card { padding: var(--space-8) var(--space-6); }
  .login-card__title { font-size: var(--text-xl); }
}
</style>
