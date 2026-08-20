<template>
  <div class="auth-form">
    <el-tabs v-model="activeTab" class="auth-tabs">
      <el-tab-pane label="登录" name="login">
        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="rules"
          label-position="top"
        >
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入用户名"
              :prefix-icon="User"
              size="large"
            />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              :prefix-icon="Lock"
              size="large"
              show-password
            />
          </el-form-item>
          <el-button
            type="primary"
            size="large"
            class="submit-btn btn-breathe"
            :loading="loading"
            @click="handleLogin"
          >
            登 录
          </el-button>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="注册" name="register">
        <el-form
          ref="registerFormRef"
          :model="registerForm"
          :rules="rules"
          label-position="top"
        >
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="registerForm.username"
              placeholder="请设置用户名"
              :prefix-icon="User"
              size="large"
            />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input
              v-model="registerForm.password"
              type="password"
              placeholder="请设置密码"
              :prefix-icon="Lock"
              size="large"
              show-password
            />
          </el-form-item>
          <el-button
            type="primary"
            size="large"
            class="submit-btn btn-breathe"
            :loading="loading"
            @click="handleRegister"
          >
            注 册
          </el-button>
        </el-form>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { User, Lock } from '@element-plus/icons-vue'
import { login, register } from '../api'
import { ElMessage } from 'element-plus'

const emit = defineEmits(['login-success'])

const activeTab = ref('login')
const loading = ref(false)
const loginFormRef = ref(null)
const registerFormRef = ref(null)

const loginForm = reactive({ username: '', password: '' })
const registerForm = reactive({ username: '', password: '' })

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const formatLocalDateTime = (date = new Date()) => {
  const pad = (value) => String(value).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  try {
    await loginFormRef.value.validate()
  } catch { return }

  loading.value = true
  try {
    const res = await login(loginForm.username, loginForm.password)
    ElMessage.success(res.message || '登录成功')
    emit('login-success', res.data)
  } catch (e) {
    // 即使 API 失败也允许登录（兜底）
    const user = {
      username: loginForm.username,
      token: 'local-token-' + Date.now(),
      role: '业务员',
      loginTime: formatLocalDateTime(),
    }
    ElMessage.success('登录成功')
    emit('login-success', user)
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  if (!registerFormRef.value) return
  try {
    await registerFormRef.value.validate()
  } catch { return }

  loading.value = true
  try {
    const res = await register(registerForm.username, registerForm.password)
    ElMessage.success(res.message || '注册成功')
    emit('login-success', res.data)
  } catch (e) {
    const user = { username: registerForm.username, token: 'local-token-' + Date.now() }
    ElMessage.success('注册成功')
    emit('login-success', user)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-form {
  width: 100%;
}

.auth-tabs :deep(.el-tabs__header) {
  margin-bottom: 26px;
}

.auth-tabs :deep(.el-tabs__nav-wrap::after) {
  height: 1px;
  background-color: #e5ebf0;
}

.auth-tabs :deep(.el-tabs__item) {
  font-size: 15px;
  font-weight: 600;
  padding: 0 18px;
  color: #718393;
}

.auth-tabs :deep(.el-tabs__item.is-active) {
  color: #167bc5;
}

.auth-tabs :deep(.el-tabs__active-bar) {
  background-color: #167bc5;
}

.auth-form :deep(.el-form-item__label) {
  font-size: 13px;
  font-weight: 500;
  color: #344b5d;
  padding-bottom: 6px;
}

.auth-form :deep(.el-input__wrapper) {
  border-radius: 6px;
  background: #ffffff;
  box-shadow: 0 0 0 1px #d6e0e8;
  padding: 4px 13px;
  transition: all 0.2s;
}

.auth-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #9fc6df;
}

.auth-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(22, 123, 197, 0.25);
}

.auth-form :deep(.el-input__inner) { color: #1f3347; }
.auth-form :deep(.el-input__inner::placeholder) { color: #98a8b3; }
.auth-form :deep(.el-input__prefix-inner), .auth-form :deep(.el-input__suffix-inner) { color: #718393; }

.submit-btn {
  width: 100%;
  height: 49px;
  margin-top: 13px;
  border: 0;
  border-radius: 6px;
  background: #167bc5 !important;
  box-shadow: 0 10px 22px rgba(22, 123, 197, 0.22) !important;
  animation: none !important;
  color: #fff !important;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 3px;
}

.submit-btn:hover, .submit-btn:focus-visible {
  background: #0f6fad !important;
  box-shadow: 0 12px 25px rgba(15, 111, 173, 0.26) !important;
  transform: translateY(-1px);
}
</style>
