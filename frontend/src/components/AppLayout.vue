<template>
  <div class="app-shell">
    <aside class="app-sidebar" aria-label="系统主导航">
      <div class="sidebar-brand">
        <div class="brand-mark"><svg viewBox="0 0 24 24" class="brand-shield" fill="none" aria-hidden="true"><path d="M12 2.5 20 6.2v5.7c0 5.3-3.3 9-8 10.6-4.7-1.6-8-5.3-8-10.6V6.2L12 2.5Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="m8.5 12 2.2 2.2 4.8-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
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
          <div class="system-title-group">
            <h1 class="brand-title">金融影像智能相似度检测系统</h1>
            <p class="system-subtitle">AI驱动的金融业务影像智能分析与风险识别</p>
          </div>
        </div>
        <div class="top-bar-right">
          <el-button class="theme-toggle" circle :icon="isDark ? Sunny : Moon" size="default" @click="toggleTheme"/>
          <el-button class="header-action username-action" type="info" plain size="small"><el-icon><User /></el-icon><span>{{ username }}</span></el-button>
          <el-button class="header-action" type="danger" plain size="small" @click="handleLogout"><el-icon><SwitchButton /></el-icon><span>退出登录</span></el-button>
        </div>
      </header>
      <main class="app-main"><RouterView /></main>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { House, Search, Setting, User, SwitchButton, Sunny, Moon } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const isDark = ref(false)
const menuItems = [
  { path: '/dashboard', label: '案件分析', icon: House }, { path: '/detection', label: '智能影像检测', icon: Search },
  { path: '/settings', label: '系统管理', icon: Setting },
]
const username = computed(() => JSON.parse(localStorage.getItem('user') || '{}').username || 'anonymous')
const toggleTheme = () => { isDark.value = !isDark.value; const theme = isDark.value ? 'dark' : 'light'; document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : ''); document.querySelector('meta[name="theme-color"]')?.setAttribute('content', isDark.value ? '#1e293b' : '#3b82f6'); localStorage.setItem('theme', theme) }
const handleLogout = () => { localStorage.removeItem('user'); localStorage.removeItem('session_id'); router.push('/') }
onMounted(() => { isDark.value = document.documentElement.getAttribute('data-theme') === 'dark' })
</script>

<style scoped>
.app-shell { min-height:100vh; background:var(--bg-primary); }.app-sidebar { position:fixed; inset:0 auto 0 0; z-index:200; width:240px; display:flex; flex-direction:column; padding:22px 14px 16px; background:var(--bg-card); border-right:1px solid var(--border-color); box-shadow:var(--shadow-sm); }.sidebar-brand { display:flex; align-items:center; gap:11px; padding:0 10px 24px; border-bottom:1px solid var(--border-light); }.brand-mark { display:grid; place-items:center; width:38px; height:38px; color:#fff; border-radius:11px; background:linear-gradient(135deg,#6366f1,#2563eb); box-shadow:0 6px 16px rgba(79,70,229,.25); }.brand-shield { width:24px; height:24px; }.brand-name { color:var(--text-primary); font-size:14px; font-weight:700; white-space:nowrap; }.brand-subtitle { margin-top:3px; color:var(--text-muted); font-size:11px; }.sidebar-nav { display:flex; flex-direction:column; gap:5px; padding-top:20px; }.nav-item { display:flex; align-items:center; gap:12px; min-height:44px; padding:0 13px; color:var(--text-secondary); text-decoration:none; border-radius:var(--radius-sm); font-size:14px; font-weight:500; transition:color .2s,background-color .2s,transform .2s; }.nav-item:hover { color:var(--accent); background:var(--accent-light); transform:translateX(2px); }.nav-item.active { color:#fff; background:linear-gradient(135deg,#6366f1,#4f46e5); box-shadow:0 5px 14px rgba(79,70,229,.22); }.sidebar-footer { margin-top:auto; padding:14px 10px 0; color:var(--text-muted); font-size:11px; border-top:1px solid var(--border-light); white-space:nowrap; }.app-stage { min-width:0; min-height:100vh; margin-left:240px; display:flex; flex-direction:column; }.top-bar { position:sticky; top:0; z-index:100; height:60px; display:flex; align-items:center; justify-content:space-between; gap:20px; padding:0 28px; background:var(--bg-card); border-bottom:1px solid var(--border-color); box-shadow:var(--shadow-sm); }.top-bar-left,.top-bar-right { display:flex; align-items:center; gap:12px; min-width:0; }.top-bar-right { flex:0 0 auto; }.header-action { height:32px; padding:0 12px; border-radius:8px; font-size:13px; font-weight:500; gap:6px; }.header-action .el-icon { margin-right:0; }.username-action { max-width:220px; overflow:hidden; }.username-action span { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }.task-status{max-width:290px;overflow:hidden;text-overflow:ellipsis}.nav-logo { flex:0 0 auto; color:#3b82f6; }.theme-toggle { transition:transform .3s; }.theme-toggle:hover { transform:rotate(30deg); }.app-main { flex:1; min-width:0; padding:20px 28px 28px; overflow-x:hidden; }@media(max-width:1280px){.app-main{padding:16px 20px 24px}.top-bar{padding:0 20px}}
.top-bar{height:72px}.system-title-group{min-width:0}.system-title-group .brand-title{margin:0;font-size:18px!important;line-height:1.2}.system-subtitle{overflow:hidden;margin:4px 0 0;color:var(--text-muted);font-size:12px;line-height:1.2;text-overflow:ellipsis;white-space:nowrap}@media(max-width:700px){.top-bar{height:auto;min-height:96px;flex-wrap:wrap;padding-top:9px;padding-bottom:9px}.top-bar-left{flex:1 1 100%}.top-bar-right{margin-left:auto}.system-title-group .brand-title{font-size:16px!important}.system-subtitle{max-width:100%}}
</style>
