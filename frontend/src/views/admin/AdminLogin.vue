<template>
  <div class="admin-login-page">
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="bg-gradient"></div>
      <div class="bg-grid"></div>
      <div class="bg-glow glow-1"></div>
      <div class="bg-glow glow-2"></div>
    </div>

    <!-- 返回按钮 -->
    <button class="back-button" @click="goBack">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="19" y1="12" x2="5" y2="12"/>
        <polyline points="12 19 5 12 12 5"/>
      </svg>
      <span>返回</span>
    </button>

    <!-- 登录卡片 -->
    <div class="login-card" :class="{ 'shake': shake }">
      <!-- Logo区域 -->
      <div class="card-header">
        <div class="logo-container">
          <div class="logo-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z"/>
              <path d="M2 17l10 5 10-5"/>
              <path d="M2 12l10 5 10-5"/>
            </svg>
          </div>
          <div class="logo-text">
            <span class="logo-title">AI小商</span>
            <span class="logo-subtitle">智能运营平台</span>
          </div>
        </div>
        <p class="welcome-text">欢迎回来，请登录您的管理员账号</p>
      </div>

      <!-- 登录表单 -->
      <form class="login-form" @submit.prevent="handleLogin">
        <div class="form-group">
          <label class="form-label">
            <svg class="label-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
            管理员账号
          </label>
          <div class="input-wrapper" :class="{ 'focused': focusedField === 'username', 'error': errors.username }">
            <input
              type="text"
              v-model="form.username"
              placeholder="请输入管理员账号"
              class="form-input"
              @focus="focusedField = 'username'"
              @blur="focusedField = ''"
              autocomplete="username"
            />
            <div class="input-line"></div>
          </div>
          <span class="error-message" v-if="errors.username">{{ errors.username }}</span>
        </div>

        <div class="form-group">
          <label class="form-label">
            <svg class="label-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
            </svg>
            密码
          </label>
          <div class="input-wrapper password-wrapper" :class="{ 'focused': focusedField === 'password', 'error': errors.password }">
            <input
              :type="showPassword ? 'text' : 'password'"
              v-model="form.password"
              placeholder="请输入密码"
              class="form-input"
              @focus="focusedField = 'password'"
              @blur="focusedField = ''"
              autocomplete="current-password"
            />
            <button type="button" class="password-toggle" @click="showPassword = !showPassword">
              <svg v-if="!showPassword" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                <line x1="1" y1="1" x2="23" y2="23"/>
              </svg>
            </button>
            <div class="input-line"></div>
          </div>
          <span class="error-message" v-if="errors.password">{{ errors.password }}</span>
        </div>

        <div class="form-actions">
          <label class="remember-me">
            <input type="checkbox" v-model="rememberMe" />
            <span class="checkmark"></span>
            <span>记住账号</span>
          </label>
        </div>

        <button type="submit" class="login-button" :disabled="loading">
          <span v-if="!loading">登 录</span>
          <span v-else class="loading-spinner"></span>
        </button>
      </form>

      <!-- 提示信息 -->
      <div class="login-hint">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="16" x2="12" y2="12"/>
          <line x1="12" y1="8" x2="12.01" y2="8"/>
        </svg>
        <span>默认账号：admin / 123456</span>
      </div>
    </div>

    <!-- 版本信息 -->
    <div class="version-info">
      <span>v1.0.0</span>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAdminStore } from '@/stores/admin'
import logger from '@/utils/logger'

const router = useRouter()
const adminStore = useAdminStore()

// 表单数据
const form = reactive({
  username: '',
  password: ''
})

// 状态
const loading = ref(false)
const shake = ref(false)
const showPassword = ref(false)
const rememberMe = ref(false)
const focusedField = ref('')

// 错误信息
const errors = reactive({
  username: '',
  password: ''
})

// 验证表单
function validateForm() {
  let isValid = true
  errors.username = ''
  errors.password = ''

  if (!form.username.trim()) {
    errors.username = '请输入管理员账号'
    isValid = false
  }

  if (!form.password) {
    errors.password = '请输入密码'
    isValid = false
  } else if (form.password.length < 6) {
    errors.password = '密码长度至少6位'
    isValid = false
  }

  return isValid
}

// 处理登录
async function handleLogin() {
  if (!validateForm()) {
    triggerShake()
    return
  }

  loading.value = true
  logger.info('[AdminLogin] Starting login process...')

  try {
    await adminStore.login(form.username, form.password)
    logger.info('[AdminLogin] Login successful, redirecting to dashboard...')
    router.push('/admin/dashboard')
  } catch (error) {
    logger.error('[AdminLogin] Login failed:', error?.response?.data?.error?.message || error.message)
    const errorMsg = error?.response?.data?.error?.message || '登录失败，请检查账号密码'
    errors.password = errorMsg
    triggerShake()
  } finally {
    loading.value = false
  }
}

// 触发抖动效果
function triggerShake() {
  shake.value = true
  setTimeout(() => {
    shake.value = false
  }, 500)
}

// 记住账号
onMounted(() => {
  const savedUsername = localStorage.getItem('admin_username')
  if (savedUsername) {
    form.username = savedUsername
    rememberMe.value = true
  }
})

// 返回上一页
function goBack() {
  router.push('/login')
}
</script>

<style scoped>
/* ============================================
   AI小商 管理端登录页
   设计风格：深色科技风 + 渐变光效
   ============================================ */

/* CSS Variables */
:root {
  --primary: #0891B2;
  --primary-light: #22D3EE;
  --primary-dark: #0E7490;
  --success: #059669;
  --danger: #EF4444;
  --bg-dark: #0F172A;
  --bg-card: #1E293B;
  --bg-card-hover: #273549;
  --border-color: #334155;
  --text-primary: #F1F5F9;
  --text-secondary: #94A3B8;
  --text-muted: #64748B;
}

.admin-login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-dark);
  position: relative;
  overflow: hidden;
  font-family: 'Inter', 'Noto Sans SC', -apple-system, sans-serif;
}

/* 背景装饰 */
.bg-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

/* 返回按钮 */
.back-button {
  position: fixed;
  top: 24px;
  left: 24px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: rgba(30, 41, 59, 0.9);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s ease;
  z-index: 10;
}

.back-button:hover {
  background: rgba(30, 41, 59, 1);
  border-color: var(--primary);
  color: var(--text-primary);
}

.back-button svg {
  width: 18px;
  height: 18px;
}

.bg-gradient {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 80% 50% at 50% -20%, rgba(8, 145, 178, 0.15), transparent),
    radial-gradient(ellipse 60% 40% at 80% 60%, rgba(139, 92, 246, 0.08), transparent),
    radial-gradient(ellipse 50% 30% at 20% 80%, rgba(6, 182, 212, 0.08), transparent);
}

.bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(51, 65, 85, 0.3) 1px, transparent 1px),
    linear-gradient(90deg, rgba(51, 65, 85, 0.3) 1px, transparent 1px);
  background-size: 60px 60px;
  mask-image: radial-gradient(ellipse 80% 60% at 50% 50%, black 20%, transparent 70%);
}

.bg-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
}

.glow-1 {
  width: 400px;
  height: 400px;
  background: var(--primary);
  top: -200px;
  left: 50%;
  transform: translateX(-50%);
  opacity: 0.15;
}

.glow-2 {
  width: 300px;
  height: 300px;
  background: #8B5CF6;
  bottom: -150px;
  right: 10%;
  opacity: 0.1;
}

/* 登录卡片 */
.login-card {
  width: 420px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  padding: 48px 40px;
  position: relative;
  z-index: 1;
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.05),
    0 20px 50px -10px rgba(0, 0, 0, 0.5),
    0 0 100px -20px rgba(8, 145, 178, 0.2);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.login-card.shake {
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20%, 60% { transform: translateX(-10px); }
  40%, 80% { transform: translateX(10px); }
}

/* Logo区域 */
.card-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 20px;
}

.logo-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, var(--primary), var(--primary-light));
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(8, 145, 178, 0.3);
}

.logo-icon svg {
  width: 32px;
  height: 32px;
  color: white;
}

.logo-text {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.logo-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 2px;
}

.logo-subtitle {
  font-size: 13px;
  color: var(--text-muted);
  letter-spacing: 4px;
}

.welcome-text {
  font-size: 14px;
  color: var(--text-secondary);
}

/* 表单样式 */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}

.label-icon {
  width: 16px;
  height: 16px;
  opacity: 0.7;
}

.input-wrapper {
  position: relative;
}

.form-input {
  width: 100%;
  height: 52px;
  background: var(--bg-dark);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 0 16px;
  font-size: 15px;
  color: var(--text-primary);
  transition: all 0.2s ease;
}

.form-input::placeholder {
  color: var(--text-muted);
}

.form-input:focus {
  outline: none;
  border-color: var(--primary);
  background: rgba(8, 145, 178, 0.05);
}

.input-wrapper.error .form-input {
  border-color: var(--danger);
}

.input-line {
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--primary), var(--primary-light));
  border-radius: 1px;
  transition: all 0.3s ease;
  transform: translateX(-50%);
}

.input-wrapper.focused .input-line {
  width: 100%;
}

.password-wrapper {
  display: flex;
  align-items: center;
}

.password-wrapper .form-input {
  padding-right: 48px;
}

.password-toggle {
  position: absolute;
  right: 16px;
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
}

.password-toggle:hover {
  color: var(--text-secondary);
}

.password-toggle svg {
  width: 18px;
  height: 18px;
}

.error-message {
  font-size: 12px;
  color: var(--danger);
  margin-top: 4px;
}

/* 记住我 & 忘记密码 */
.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
}

.remember-me input {
  display: none;
}

.remember-me .checkmark {
  width: 16px;
  height: 16px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  position: relative;
  transition: all 0.2s;
}

.remember-me input:checked + .checkmark {
  background: var(--primary);
  border-color: var(--primary);
}

.remember-me input:checked + .checkmark::after {
  content: '';
  position: absolute;
  left: 5px;
  top: 2px;
  width: 4px;
  height: 8px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

/* 登录按钮 */
.login-button {
  height: 52px;
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  color: white;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(8, 145, 178, 0.3);
}

.login-button::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transform: translateX(-100%);
  transition: transform 0.5s;
}

.login-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 30px rgba(8, 145, 178, 0.4);
}

.login-button:hover::before {
  transform: translateX(100%);
}

.login-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 提示信息 */
.login-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
  font-size: 12px;
  color: var(--text-muted);
}

.login-hint svg {
  width: 14px;
  height: 14px;
}

/* 版本信息 */
.version-info {
  position: fixed;
  bottom: 20px;
  font-size: 12px;
  color: var(--text-muted);
  z-index: 1;
}

/* 响应式 */
@media (max-width: 480px) {
  .login-card {
    width: calc(100% - 32px);
    padding: 36px 24px;
  }
}
</style>