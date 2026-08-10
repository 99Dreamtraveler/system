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
            <!-- Logo 盾牌 -->
            <div class="logo-wrap">
              <svg viewBox="0 0 80 80" fill="none" class="hero-shield">
                <defs>
                  <linearGradient id="heroShieldGrad" x1="20%" y1="0%" x2="80%" y2="100%">
                    <stop offset="0%" stop-color="#818cf8">
                      <animate attributeName="stop-color" values="#818cf8;#6366f1;#818cf8" dur="3s" repeatCount="indefinite"/>
                    </stop>
                    <stop offset="50%" stop-color="#6366f1">
                      <animate attributeName="stop-color" values="#6366f1;#4f46e5;#6366f1" dur="3s" repeatCount="indefinite"/>
                    </stop>
                    <stop offset="100%" stop-color="#4f46e5">
                      <animate attributeName="stop-color" values="#4f46e5;#4338ca;#4f46e5" dur="3s" repeatCount="indefinite"/>
                    </stop>
                  </linearGradient>
                  <filter id="heroGlow">
                    <feDropShadow dx="0" dy="0" stdDeviation="6" flood-color="#6366f1" flood-opacity="0.3"/>
                  </filter>
                </defs>
                <!-- 旋转光环 -->
                <circle cx="40" cy="40" r="36" stroke="#c7d2fe" stroke-width="1.5"
                        fill="none" stroke-dasharray="60 180" class="hero-ring"/>
                <!-- 盾牌 -->
                <path d="M40 12 L62 22 L62 42 C62 60 50 72 40 76 C30 72 18 60 18 42 L18 22 Z"
                      fill="url(#heroShieldGrad)" filter="url(#heroGlow)" class="hero-shield-path"/>
                <!-- 光扫描 -->
                <path d="M40 12 L62 22 L62 42 C62 60 50 72 40 76 C30 72 18 60 18 42 L18 22 Z"
                      fill="rgba(255,255,255,0.2)" class="shield-sweep-overlay"/>
              </svg>
            </div>

            <h1 class="hero-title">金融影像智能相似度检测系统</h1>
            <p class="hero-desc">基于多模态大模型的金融影像智能分析平台，提供面签照筛选、相似度检测、可疑交易预警等核心能力</p>

            <!-- 特性卡片 -->
            <div class="feature-cards">
              <div class="feat-card">
                <div class="feat-icon f1">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>
                </div>
                <div class="feat-text">
                  <strong>AI 面签照筛选</strong>
                  <span>YOLO 深度学习自动识别</span>
                </div>
              </div>
              <div class="feat-card">
                <div class="feat-icon f2">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                </div>
                <div class="feat-text">
                  <strong>多模态相似度检测</strong>
                  <span>CLIP + LoRA 特征比对</span>
                </div>
              </div>
              <div class="feat-card">
                <div class="feat-icon f3">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
                </div>
                <div class="feat-text">
                  <strong>可疑交易风险预警</strong>
                  <span>智能聚类相似交易组</span>
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
  font-size: 15px;
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

/* 盾牌 Logo */
.logo-wrap {
  margin-bottom: 32px;
}

.hero-shield {
  width: 80px;
  height: 80px;
  filter: drop-shadow(0 8px 24px rgba(99, 102, 241, 0.25));
}

.hero-ring {
  animation: spin 10s linear infinite;
  transform-origin: 40px 40px;
}

.hero-shield-path {
  transition: filter 0.3s;
}

.hero-shield:hover .hero-shield-path {
  filter: drop-shadow(0 0 14px rgba(99, 102, 241, 0.5)) !important;
}

.shield-sweep-overlay {
  animation: sweep-shield 3.5s ease-in-out infinite;
  clip-path: polygon(0 0, 100% 0, 100% 100%, 0 100%);
}

@keyframes sweep-shield {
  0%, 100% { opacity: 0; }
  20%, 50% { opacity: 0.25; }
  70% { opacity: 0; }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 标题 */
.hero-title {
  font-size: 28px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 14px;
  line-height: 1.4;
  letter-spacing: -0.3px;
}

.hero-desc {
  font-size: 15px;
  color: #111827;
  line-height: 1.8;
  margin-bottom: 36px;
  font-weight: 500;
}

/* 特性卡片 */
.feature-cards {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.feat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #eef1f6;
  transition: all 0.25s ease;
}

.feat-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  transform: translateY(-1px);
  border-color: #e0e4f0;
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

.feat-icon.f1 {
  background: #eef2ff;
  color: #6366f1;
}

.feat-icon.f2 {
  background: #f0fdf4;
  color: #10b981;
}

.feat-icon.f3 {
  background: #fffbeb;
  color: #f59e0b;
}

.feat-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.feat-text strong {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.feat-text span {
  font-size: 12px;
  color: #94a3b8;
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
  .hero-title {
    font-size: 24px;
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
  .hero-title {
    font-size: 22px;
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
  .logo-wrap {
    margin-bottom: 20px;
  }
  .hero-shield {
    width: 56px;
    height: 56px;
  }
  .feature-cards {
    display: none;
  }
}
</style>
