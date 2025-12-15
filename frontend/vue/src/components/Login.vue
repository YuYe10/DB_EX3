<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <h1>🎓 教务管理系统</h1>
        <p>欢迎登录</p>
      </div>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label>账号</label>
          <input 
            v-model="form.username" 
            required 
            placeholder="学号/工号/admin"
            autocomplete="username"
            @keydown="handleKeydown"
            autofocus
          />
        </div>
        
        <div class="form-group">
          <label>密码</label>
          <input 
            v-model="form.password" 
            type="password"
            required 
            placeholder="请输入密码"
            autocomplete="current-password"
            @keydown="handleKeydown"
          />
        </div>
        
        <div class="error-message" v-if="errorMsg">{{ errorMsg }}</div>
        
        <button type="submit" class="btn-login" :disabled="loading">
          {{ loading ? '登录中...' : '登 录' }}
        </button>
      </form>
      
      <div class="login-hints">
        <div class="hint-item">
          <strong>学生:</strong> 账号=学号, 密码=s+学号
        </div>
        <div class="hint-item">
          <strong>教师:</strong> 账号=工号, 密码=t+工号
        </div>
        <div class="hint-item">
          <strong>管理员:</strong> 账号=admin, 密码=admin@123
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'

const emit = defineEmits(['login-success'])

const form = reactive({
  username: '',
  password: ''
})

const loading = ref(false)
const errorMsg = ref('')

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api'

// 从localStorage读取记忆的账号
onMounted(() => {
  const savedUsername = localStorage.getItem('login_username')
  if (savedUsername) {
    form.username = savedUsername
  }
})

async function handleLogin() {
  // 前端验证
  if (!form.username.trim()) {
    errorMsg.value = '请输入账号'
    return
  }
  if (!form.password) {
    errorMsg.value = '请输入密码'
    return
  }
  
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
    
    if (!res.ok) {
      errorMsg.value = data.message || '登录失败，请检查账号和密码'
      return
    }
    
    // 登录成功，记忆账号
    localStorage.setItem('login_username', form.username)
    emit('login-success', data.user)
  } catch (error) {
    errorMsg.value = '网络错误，请检查后端服务或网络连接'
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 支持Enter键快速登录
function handleKeydown(e) {
  if (e.key === 'Enter') {
    handleLogin()
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%);
  background-size: 400% 400%;
  animation: gradient-shift 15s ease infinite;
  padding: 20px;
}

@keyframes gradient-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.login-card {
  background: white;
  border-radius: 20px;
  padding: 40px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
  animation: fade-in 0.6s ease-out;
}

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-header h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.login-header p {
  margin: 0;
  color: #64748b;
  font-size: 14px;
}

.login-form {
  margin-bottom: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 700;
  color: #0f172a;
  font-size: 14px;
}

.form-group input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 14px;
  font-family: inherit;
  outline: none;
  transition: all 0.3s ease;
  background: #f8fafc;
  box-sizing: border-box;
}

.form-group input::placeholder {
  color: #cbd5e1;
}

.form-group input:focus {
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  transform: translateY(-1px);
}

.error-message {
  padding: 12px 16px;
  background: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 10px;
  color: #b91c1c;
  font-size: 13px;
  margin-bottom: 16px;
  text-align: center;
  animation: shake 0.3s;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

.btn-login {
  width: 100%;
  padding: 14px;
  border: none;
  border-radius: 12px;
  font-weight: 700;
  font-size: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
}

.btn-login:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 28px rgba(102, 126, 234, 0.4);
}

.btn-login:active:not(:disabled) {
  transform: translateY(0);
}

.btn-login:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-hints {
  background: #f8fafc;
  border-radius: 12px;
  padding: 16px;
  border: 1px solid #e2e8f0;
}

.hint-item {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 8px;
  line-height: 1.6;
}

.hint-item:last-child {
  margin-bottom: 0;
}

.hint-item strong {
  color: #0f172a;
  font-weight: 700;
}

@media (max-width: 480px) {
  .login-card {
    padding: 28px 24px;
  }
  
  .login-header h1 {
    font-size: 24px;
  }
}
</style>
