<template>
  <div class="welcome-container">
    <!-- 顶部导航栏 -->
    <header class="top-nav">
      <div class="nav-brand">
        <svg viewBox="0 0 32 32" fill="none" class="nav-logo-sm" width="28" height="28">
          <defs>
            <linearGradient id="navShieldSm" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#6366f1"/>
              <stop offset="100%" stop-color="#4f46e5"/>
            </linearGradient>
          </defs>
          <path d="M16 3 L26 8 L26 18 C26 27 20 31 16 33 C12 31 6 27 6 18 L6 8 Z"
                fill="url(#navShieldSm)" stroke="none"/>
        </svg>
        <span>金融影像智能检测平台</span>
      </div>
    </header>

    <!-- 主体 -->
    <div class="main-body">
      <!-- 左侧品牌区 -->
      <div class="hero-section">
        <div class="hero-inner">
          <!-- 装饰性渐变环 -->
          <div class="decor-ring ring-1"></div>
          <div class="decor-ring ring-2"></div>
          <div class="decor-ring ring-3"></div>

          <div class="hero-content">

            <p class="hero-desc">基于多模态大模型的金融影像智能分析平台，提供面签照筛选、相似度检测、可疑交易预警等核心能力</p>

            <!-- 特性卡片 -->
            <div class="feature-cards">
              <div class="feat-card theme-indigo">
                <div class="feat-title">
                  <span class="feat-title-main">AI 面签照</span>
                  <span class="feat-title-sub">智能筛选</span>
                </div>
                <div class="feat-content">
                  <div class="feat-icon f1">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>
                  </div>
                  <div class="mock-list">
                    <div class="mock-row"><span class="dot"></span><span>人脸检测</span><span class="tag">通过</span></div>
                    <div class="mock-row"><span class="dot"></span><span>清晰度检测</span><span class="tag">通过</span></div>
                    <div class="mock-row"><span class="dot"></span><span>遮挡判断</span><span class="tag warn">待复核</span></div>
                  </div>
                </div>
              </div>
              <div class="feat-card theme-green">
                <div class="feat-title">
                  <span class="feat-title-main">多模态</span>
                  <span class="feat-title-sub">相似度检测</span>
                </div>
                <div class="feat-content">
                  <div class="feat-icon f2">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                  </div>
                  <div class="mock-chart">
                    <div class="bar" style="height: 40%"></div>
                    <div class="bar" style="height: 70%"></div>
                    <div class="bar active" style="height: 92%"></div>
                    <div class="bar" style="height: 55%"></div>
                    <div class="bar" style="height: 30%"></div>
                  </div>
                  <div class="mock-score">相似度 92.4%</div>
                </div>
              </div>
              <div class="feat-card theme-amber">
                <div class="feat-title">
                  <span class="feat-title-main">可疑交易</span>
                  <span class="feat-title-sub">风险预警</span>
                </div>
                <div class="feat-content">
                  <div class="feat-icon f3">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
                  </div>
                  <div class="mock-radar">
                    <div class="radar-ring"></div>
                    <div class="radar-ring"></div>
                    <div class="radar-ring"></div>
                    <div class="radar-sweep"></div>
                  </div>
                  <div class="mock-alert">发现 3 组相似交易</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧登录卡片 -->
      <div class="auth-section">
        <div class="auth-card">
          <div class="auth-tab-row">
            <h2>欢迎登录</h2>
            <p>登录或创建账户以使用系统</p>
          </div>
          <LoginRegister @login-success="onLoginSuccess" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import LoginRegister from '../components/LoginRegister.vue'

const router = useRouter()

const onLoginSuccess = (user) => {
  localStorage.setItem('user', JSON.stringify(user))
  router.push('/dashboard')
}
</script>

<style scoped>
/* ============================================
   整体容器
   ============================================ */
.welcome-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f6fa;
}

/* ============================================
   顶部导航
   ============================================ */
.top-nav {
  height: 56px;
  display: flex;
  align-items: center;
  padding: 0 40px;
  background: transparent;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: 10;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
}

.nav-logo-sm {
  flex-shrink: 0;
}

/* ============================================
   主体区
   ============================================ */
.main-body {
  flex: 1;
  display: flex;
  min-height: 100vh;
}

/* ============================================
   左侧品牌区
   ============================================ */
.hero-section {
  flex: 1;
  background: #f3f7fb;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.hero-inner {
  position: relative;
  width: 100%;
  max-width: 600px;
  padding: 80px 60px 60px;
}

/* 装饰渐变圆环 */
.decor-ring {
  position: absolute;
  border-radius: 50%;
  border: 1px solid rgba(129, 140, 248, 0.15);
  pointer-events: none;
}

.ring-1 {
  width: 500px;
  height: 500px;
  top: -180px;
  right: -120px;
  animation: float-ring 8s ease-in-out infinite;
}

.ring-2 {
  width: 350px;
  height: 350px;
  bottom: -100px;
  left: -80px;
  border-color: rgba(99, 102, 241, 0.1);
  animation: float-ring 10s ease-in-out infinite reverse;
}

.ring-3 {
  width: 200px;
  height: 200px;
  top: 40%;
  right: 20px;
  border-color: rgba(167, 139, 250, 0.12);
  animation: float-ring 7s ease-in-out infinite 2s;
}

@keyframes float-ring {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  33% { transform: translateY(-12px) rotate(120deg); }
  66% { transform: translateY(8px) rotate(240deg); }
}

.hero-content {
  position: relative;
  z-index: 1;
}

/* 标题 */
.hero-desc {
  font-size: 15px;
  color: #111827;
  line-height: 1.8;
  margin-bottom: 36px;
  font-weight: 500;
}

/* 特性卡片 */
.feature-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.feat-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.feat-title {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  text-align: center;
}

.feat-title-main {
  font-size: 15px;
  font-weight: 600;
}

.feat-title-sub {
  font-size: 17px;
  font-weight: 700;
  color: #1e293b;
}

.feat-content {
  flex: 1;
  min-height: 170px;
  background: #ffffff;
  border-radius: 16px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 12px;
  border: 1px solid;
  transition: all 0.25s ease;
}

.feat-content:hover {
  transform: translateY(-3px);
}

.feat-icon {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.feat-icon svg {
  width: 22px;
  height: 22px;
}

/* Indigo 主题 */
.theme-indigo .feat-title-main { color: #6366f1; }
.theme-indigo .feat-content {
  border-color: #e0e7ff;
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.10);
}
.theme-indigo .feat-content:hover {
  box-shadow: 0 10px 28px rgba(99, 102, 241, 0.18);
}
.theme-indigo .feat-icon.f1 { background: #eef2ff; color: #6366f1; }
.theme-indigo .mock-row .dot { background: #6366f1; }
.theme-indigo .mock-row .tag { background: #e0e7ff; color: #4338ca; }
.theme-indigo .mock-row .tag.warn { background: #fee2e2; color: #b91c1c; }

/* Green 主题 */
.theme-green .feat-title-main { color: #10b981; }
.theme-green .feat-content {
  border-color: #d1fae5;
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.10);
}
.theme-green .feat-content:hover {
  box-shadow: 0 10px 28px rgba(16, 185, 129, 0.18);
}
.theme-green .feat-icon.f2 { background: #f0fdf4; color: #10b981; }
.theme-green .mock-chart .bar { background: #d1fae5; }
.theme-green .mock-chart .bar.active { background: linear-gradient(180deg, #10b981, #34d399); }
.theme-green .mock-score { color: #059669; }

/* Amber 主题 */
.theme-amber .feat-title-main { color: #f59e0b; }
.theme-amber .feat-content {
  border-color: #fef3c7;
  box-shadow: 0 6px 20px rgba(245, 158, 11, 0.10);
}
.theme-amber .feat-content:hover {
  box-shadow: 0 10px 28px rgba(245, 158, 11, 0.18);
}
.theme-amber .feat-icon.f3 { background: #fffbeb; color: #f59e0b; }
.theme-amber .mock-radar .radar-ring { border-color: #fde68a; }
.theme-amber .mock-radar .radar-sweep { border-color: #f59e0b; }
.theme-amber .mock-alert { background: #fffbeb; color: #b45309; }

/* 卡片内演示内容 */
.mock-list {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 9px;
}

.mock-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #475569;
}

.mock-row .dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
}

.mock-row span:nth-child(2) {
  flex: 1;
}

.mock-row .tag {
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
}

.mock-chart {
  width: 100%;
  height: 64px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 8px;
}

.mock-chart .bar {
  width: 14px;
  border-radius: 3px 3px 0 0;
  transition: all 0.3s ease;
}

.mock-score {
  font-size: 12px;
  font-weight: 700;
}

.mock-radar {
  width: 64px;
  height: 64px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mock-radar .radar-ring {
  position: absolute;
  border-radius: 50%;
  border: 1px solid;
}

.mock-radar .radar-ring:nth-child(1) {
  width: 22px;
  height: 22px;
}

.mock-radar .radar-ring:nth-child(2) {
  width: 44px;
  height: 44px;
}

.mock-radar .radar-ring:nth-child(3) {
  width: 64px;
  height: 64px;
}

.mock-radar .radar-sweep {
  position: absolute;
  width: 32px;
  height: 32px;
  border-radius: 0 80px 0 0;
  border-top: 2px solid;
  border-right: 2px solid transparent;
  animation: radar-spin 1.5s linear infinite;
  transform-origin: bottom left;
}

@keyframes radar-spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.mock-alert {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 999px;
}

/* ============================================
   右侧登录区
   ============================================ */
.auth-section {
  width: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ffffff;
  padding: 60px 52px;
}

.auth-card {
  width: 100%;
  max-width: 380px;
}

.auth-tab-row {
  text-align: center;
  margin-bottom: 32px;
}

.auth-tab-row h2 {
  font-size: 24px;
  font-weight: 700;
  color: #182536;
  margin-bottom: 6px;
}

.auth-tab-row p {
  font-size: 14px;
  color: #94a3b8;
}

/* ============================================
   响应式
   ============================================ */
@media (max-width: 1024px) {
  .hero-inner {
    padding: 60px 40px 40px;
  }
  .feature-cards {
    grid-template-columns: 1fr;
  }
  .feat-content {
    min-height: 140px;
  }
  .auth-section {
    width: 440px;
    padding: 40px 36px;
  }
}

@media (max-width: 768px) {
  .main-body {
    flex-direction: column;
  }
  .hero-section {
    flex: none;
    padding: 60px 20px 40px;
  }
  .hero-inner {
    padding: 20px;
  }
  .hero-desc {
    font-size: 14px;
    margin-bottom: 24px;
  }
  .auth-section {
    width: 100%;
    padding: 32px 24px;
  }
  .decor-ring {
    display: none;
  }
  .feature-cards {
    grid-template-columns: 1fr;
    gap: 14px;
  }
  .feat-content {
    min-height: 140px;
  }
}
</style>
