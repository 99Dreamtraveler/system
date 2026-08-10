<template>
  <div class="app-shell">
    <aside class="app-sidebar" aria-label="系统主导航">
      <div class="sidebar-brand">
        <div class="brand-mark"><el-icon :size="22"><Lock /></el-icon></div>
        <div><p class="brand-name">金融影像智能检测</p><p class="brand-subtitle">风险识别平台</p></div>
      </div>
      <nav class="sidebar-nav">
        <RouterLink v-for="item in menuItems" :key="item.path" :to="item.path" class="nav-item" :class="{ active: route.path === item.path }">
          <el-icon :size="19"><component :is="item.icon" /></el-icon><span>{{ item.label }}</span>
        </RouterLink>
      </nav>
      <p class="sidebar-footer">金融影像风控系统 · v1.0</p>
    </aside>
    <section class="app-stage">
      <header class="top-bar">
        <div class="top-bar-left">
          <svg viewBox="0 0 40 40" fill="none" class="nav-logo" width="34" height="34" aria-hidden="true"><defs><linearGradient id="headerRingGrad" x1="4" y1="4" x2="36" y2="36" gradientUnits="userSpaceOnUse"><stop stop-color="#60a5fa"/><stop offset="1" stop-color="#2563eb"/></linearGradient><linearGradient id="headerShieldGrad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#e0f2fe"/><stop offset="100%" stop-color="#93c5fd"/></linearGradient></defs><circle cx="20" cy="20" r="18" stroke="url(#headerRingGrad)" stroke-width="1.5" fill="none" opacity="0.5"/><path d="M20 4 L32 10 L32 22 C32 32 25 38 20 40 C15 38 8 32 8 22 L8 10 Z" fill="url(#headerShieldGrad)" stroke="url(#headerRingGrad)" stroke-width="2.2"/></svg>
          <h1 class="brand-title">金融影像智能相似度检测系统</h1>
        </div>
        <div class="top-bar-right">
          <el-button class="theme-toggle" circle :icon="isDark ? Sunny : Moon" size="default" @click="toggleTheme"/>
          <el-tag type="info" effect="plain" size="large"><el-icon><User /></el-icon>{{ username }}</el-tag>
          <el-button type="danger" size="small" @click="handleLogout"><el-icon><SwitchButton /></el-icon>退出登录</el-button>
        </div>
      </header>
      <main class="app-main"><RouterView /></main>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Lock, House, Search, FolderOpened, WarningFilled, DataAnalysis, Collection, Document, Setting, User, SwitchButton, Sunny, Moon } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const isDark = ref(false)
const menuItems = [
  { path: '/dashboard', label: '首页驾驶舱', icon: House }, { path: '/detection', label: '智能影像检测', icon: Search },
  { path: '/tasks', label: '检测任务', icon: FolderOpened }, { path: '/cases', label: '风险案件', icon: WarningFilled },
  { path: '/analytics', label: '数据分析', icon: DataAnalysis }, { path: '/case-center', label: '案例中心', icon: Collection },
  { path: '/reports', label: '检测报告', icon: Document }, { path: '/settings', label: '系统管理', icon: Setting },
]
const username = computed(() => JSON.parse(localStorage.getItem('user') || '{}').username || 'anonymous')
const toggleTheme = () => { isDark.value = !isDark.value; const theme = isDark.value ? 'dark' : 'light'; document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : ''); document.querySelector('meta[name="theme-color"]')?.setAttribute('content', isDark.value ? '#1e293b' : '#3b82f6'); localStorage.setItem('theme', theme) }
const handleLogout = () => { localStorage.removeItem('user'); localStorage.removeItem('session_id'); router.push('/') }
onMounted(() => { isDark.value = document.documentElement.getAttribute('data-theme') === 'dark' })
</script>

<style scoped>
.app-shell { min-height:100vh; background:var(--bg-primary); }.app-sidebar { position:fixed; inset:0 auto 0 0; z-index:200; width:240px; display:flex; flex-direction:column; padding:22px 14px 16px; background:var(--bg-card); border-right:1px solid var(--border-color); box-shadow:var(--shadow-sm); }.sidebar-brand { display:flex; align-items:center; gap:11px; padding:0 10px 24px; border-bottom:1px solid var(--border-light); }.brand-mark { display:grid; place-items:center; width:38px; height:38px; color:#fff; border-radius:11px; background:linear-gradient(135deg,#6366f1,#2563eb); box-shadow:0 6px 16px rgba(79,70,229,.25); }.brand-name { color:var(--text-primary); font-size:14px; font-weight:700; white-space:nowrap; }.brand-subtitle { margin-top:3px; color:var(--text-muted); font-size:11px; }.sidebar-nav { display:flex; flex-direction:column; gap:5px; padding-top:20px; }.nav-item { display:flex; align-items:center; gap:12px; min-height:44px; padding:0 13px; color:var(--text-secondary); text-decoration:none; border-radius:var(--radius-sm); font-size:14px; font-weight:500; transition:color .2s,background-color .2s,transform .2s; }.nav-item:hover { color:var(--accent); background:var(--accent-light); transform:translateX(2px); }.nav-item.active { color:#fff; background:linear-gradient(135deg,#6366f1,#4f46e5); box-shadow:0 5px 14px rgba(79,70,229,.22); }.sidebar-footer { margin-top:auto; padding:14px 10px 0; color:var(--text-muted); font-size:11px; border-top:1px solid var(--border-light); white-space:nowrap; }.app-stage { min-width:0; min-height:100vh; margin-left:240px; display:flex; flex-direction:column; }.top-bar { position:sticky; top:0; z-index:100; height:60px; display:flex; align-items:center; justify-content:space-between; gap:20px; padding:0 28px; background:var(--bg-card); border-bottom:1px solid var(--border-color); box-shadow:var(--shadow-sm); }.top-bar-left,.top-bar-right { display:flex; align-items:center; gap:12px; min-width:0; }.top-bar-right { flex:0 0 auto; }.nav-logo { flex:0 0 auto; }.theme-toggle { transition:transform .3s; }.theme-toggle:hover { transform:rotate(30deg); }.app-main { flex:1; min-width:0; padding:20px 28px 28px; overflow-x:hidden; }@media(max-width:1280px){.app-main{padding:16px 20px 24px}.top-bar{padding:0 20px}}
</style>
