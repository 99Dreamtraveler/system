<template>
  <router-view />
</template>

<script setup>
</script>

<style>
/* ============================================
   全局重置
   ============================================ */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  transition: background-color 0.3s ease, color 0.3s ease;
}

/* ============================================
   浅色主题 (默认)
   ============================================ */
:root {
  --bg-primary: #f0f2f5;
  --bg-card: #ffffff;
  --bg-card-hover: #f9fafb;
  --bg-input: #ffffff;
  --bg-overlay: rgba(0, 0, 0, 0.04);
  --text-primary: #1f2937;
  --text-secondary: #4b5563;
  --text-muted: #9ca3af;
  --text-inverse: #ffffff;
  --border-color: #e5e7eb;
  --border-light: #f3f4f6;
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.06);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.08);
  --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.12);
  --brand-start: #1a365d;
  --brand-mid: #2563eb;
  --brand-end: #3b82f6;
  --brand-light: #60a5fa;
  --accent: #3b82f6;
  --accent-light: #eff6ff;
  --accent-glow: rgba(59, 130, 246, 0.4);
  --warning: #f59e0b;
  --warning-light: #fffbeb;
  --success: #10b981;
  --success-light: #ecfdf5;
  --danger: #ef4444;
  --danger-light: #fef2f2;
  --stat-gradient-1: linear-gradient(135deg, #eff6ff, #f0fdf4);
  --stat-gradient-2: linear-gradient(135deg, #fffbeb, #fef3c7);
  --step-bg: #ffffff;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
}

/* ============================================
   深色主题
   ============================================ */
[data-theme="dark"] {
  --bg-primary: #0f172a;
  --bg-card: #1e293b;
  --bg-card-hover: #253449;
  --bg-input: #1e293b;
  --bg-overlay: rgba(255, 255, 255, 0.03);
  --text-primary: #f1f5f9;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
  --text-inverse: #ffffff;
  --border-color: #334155;
  --border-light: #263348;
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.5);
  --brand-start: #1e3a5f;
  --brand-mid: #3b82f6;
  --brand-end: #60a5fa;
  --brand-light: #93c5fd;
  --accent: #60a5fa;
  --accent-light: #1e3a5f;
  --accent-glow: rgba(96, 165, 250, 0.4);
  --warning: #fbbf24;
  --warning-light: #3d2e0a;
  --stat-gradient-1: linear-gradient(135deg, #1e293b, #1a2e1a);
  --stat-gradient-2: linear-gradient(135deg, #2d2416, #1e293b);
  --step-bg: #1e293b;
  --el-color-primary: #60a5fa;
  --el-color-primary-light-3: #3b82f6;
  --el-color-primary-light-5: #2563eb;
  --el-color-primary-light-7: #1d4ed8;
  --el-color-primary-light-8: #1e40af;
  --el-color-primary-light-9: #1e3a5f;
  --el-color-primary-dark-2: #93c5fd;
  --el-fill-color-blank: #1e293b;
  --el-bg-color: #0f172a;
  --el-bg-color-overlay: #1e293b;
  --el-text-color-primary: #f1f5f9;
  --el-text-color-regular: #94a3b8;
  --el-text-color-secondary: #64748b;
  --el-text-color-placeholder: #475569;
  --el-border-color: #334155;
  --el-border-color-light: #263348;
  --el-border-color-lighter: #1e293b;
  --el-fill-color-light: #263348;
  --el-fill-color: #1e293b;
  color-scheme: dark;
}

/* ============================================
   全局 body 背景
   ============================================ */
body {
  background-color: var(--bg-primary);
  color: var(--text-primary);
}

/* ============================================
   按钮呼吸渐变 — 统一靛蓝紫协调色系
   ============================================ */
/*
   色系协调原则：所有按钮在同一靛蓝紫→青→玫红光谱上
   Primary  : 靛紫 #6366f1 → #4f46e5  (主操作)
   Warning  : 青蓝 #3b82f6 → #2563eb  (检索/辅助操作)
   Danger   : 玫红 #f43f5e → #e11d48  (退出/危险操作)
   Success  : 青绿 #10b981 → #059669  (成功/确认)
*/

/* ---- 共享呼吸动画 ---- */
@keyframes breathe-primary {
  0%, 100% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.45), 0 2px 8px rgba(0,0,0,0.06); }
  50%      { box-shadow: 0 0 0 12px rgba(99, 102, 241, 0), 0 6px 20px rgba(99, 102, 241, 0.25); }
}
@keyframes breathe-warning {
  0%, 100% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.45), 0 2px 8px rgba(0,0,0,0.06); }
  50%      { box-shadow: 0 0 0 12px rgba(59, 130, 246, 0), 0 6px 20px rgba(59, 130, 246, 0.25); }
}
@keyframes breathe-danger {
  0%, 100% { box-shadow: 0 0 0 0 rgba(244, 63, 94, 0.45), 0 2px 8px rgba(0,0,0,0.06); }
  50%      { box-shadow: 0 0 0 12px rgba(244, 63, 94, 0), 0 6px 20px rgba(244, 63, 94, 0.25); }
}
@keyframes breathe-success {
  0%, 100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.45), 0 2px 8px rgba(0,0,0,0.06); }
  50%      { box-shadow: 0 0 0 12px rgba(16, 185, 129, 0), 0 6px 20px rgba(16, 185, 129, 0.25); }
}

/* ---- 按钮流动渐变 keyframes ---- */
@keyframes btn-gradient-primary {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
@keyframes btn-gradient-warning {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
@keyframes btn-gradient-danger {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
@keyframes btn-gradient-success {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* ---- Primary : 靛紫流动渐变 ---- */
.el-button--primary {
  animation: breathe-primary 2.8s ease-in-out infinite !important;
  background: linear-gradient(270deg, #818cf8, #6366f1, #4f46e5, #6366f1, #818cf8) !important;
  background-size: 300% 100% !important;
  animation: breathe-primary 2.8s ease-in-out infinite, btn-gradient-primary 4s ease infinite !important;
  border: none !important;
  color: #fff !important;
  font-weight: 600 !important;
  transition: all 0.35s ease !important;
}
.el-button--primary:hover {
  animation: none !important;
  background: linear-gradient(270deg, #6366f1, #4f46e5, #4338ca, #4f46e5, #6366f1) !important;
  background-size: 300% 100% !important;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.45) !important;
}

/* ---- Warning : 青蓝流动渐变 ---- */
.el-button--warning {
  animation: breathe-warning 2.8s ease-in-out infinite, btn-gradient-warning 4s ease infinite !important;
  background: linear-gradient(270deg, #60a5fa, #3b82f6, #2563eb, #3b82f6, #60a5fa) !important;
  background-size: 300% 100% !important;
  border: none !important;
  color: #fff !important;
  font-weight: 600 !important;
  transition: all 0.35s ease !important;
}
.el-button--warning:hover {
  animation: none !important;
  background: linear-gradient(270deg, #3b82f6, #2563eb, #1d4ed8, #2563eb, #3b82f6) !important;
  background-size: 300% 100% !important;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(59, 130, 246, 0.45) !important;
}

/* ---- Danger : 玫红流动渐变 ---- */
.el-button--danger {
  animation: breathe-danger 2.8s ease-in-out infinite, btn-gradient-danger 4s ease infinite !important;
  background: linear-gradient(270deg, #fb7185, #f43f5e, #e11d48, #f43f5e, #fb7185) !important;
  background-size: 300% 100% !important;
  border: none !important;
  color: #fff !important;
  font-weight: 600 !important;
  transition: all 0.35s ease !important;
}
.el-button--danger:hover {
  animation: none !important;
  background: linear-gradient(270deg, #f43f5e, #e11d48, #be123c, #e11d48, #f43f5e) !important;
  background-size: 300% 100% !important;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(244, 63, 94, 0.45) !important;
}

/* ---- Success : 青绿流动渐变 ---- */
.el-button--success {
  animation: breathe-success 2.8s ease-in-out infinite, btn-gradient-success 4s ease infinite !important;
  background: linear-gradient(270deg, #34d399, #10b981, #059669, #10b981, #34d399) !important;
  background-size: 300% 100% !important;
  border: none !important;
  color: #fff !important;
  font-weight: 600 !important;
  transition: all 0.35s ease !important;
}
.el-button--success:hover {
  animation: none !important;
  background: linear-gradient(270deg, #10b981, #059669, #047857, #059669, #10b981) !important;
  background-size: 300% 100% !important;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(16, 185, 129, 0.45) !important;
}

/* ---- Default / plain — 不呼吸，简洁 hover ---- */
.el-button--default:hover,
.el-button.is-plain:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}
.el-button--text:hover {
  transform: translateY(-1px);
}

/* 旧类名兼容 */
.btn-breathe,
.btn-breathe-warning {
  animation: none;
}

/* ============================================
   炫彩文字系统
   ============================================ */
@keyframes rainbow-flow {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* ---- 标题类：静态多彩渐变（不流动） ---- */
h1, h2, h3,
.card-header span,
.el-step__title.is-process,
.el-step__title.is-finish,
.group-title strong,
.hero-title {
  background: linear-gradient(135deg,
    #6366f1 0%, #8b5cf6 25%, #3b82f6 50%, #06b6d4 75%, #6366f1 100%);
  background-size: 100% 100%;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* 暗色模式标题 */
[data-theme="dark"] h1,
[data-theme="dark"] h2,
[data-theme="dark"] h3,
[data-theme="dark"] .card-header span,
[data-theme="dark"] .el-step__title.is-process,
[data-theme="dark"] .el-step__title.is-finish {
  background: linear-gradient(135deg,
    #818cf8 0%, #a78bfa 25%, #60a5fa 50%, #22d3ee 75%, #818cf8 100%);
  background-size: 100% 100%;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* 深色背景上的白字标题恢复原色（已改为黑色）*/
.hero-title,
[data-theme] .hero-title {
  background: none !important;
  -webkit-background-clip: unset !important;
  background-clip: unset !important;
  -webkit-text-fill-color: unset !important;
  color: #111827 !important;
}

/* ---- 过程中文字：彩虹流动（仅阶段指示） ---- */
.loading-phase,
.upload-status-text,
p.loading-phase {
  background: linear-gradient(270deg,
    #6366f1, #8b5cf6, #3b82f6, #06b6d4, #10b981, #8b5cf6, #6366f1);
  background-size: 300% 100%;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: rainbow-flow 3s ease infinite;
}

[data-theme="dark"] .loading-phase,
[data-theme="dark"] .loading-content h3,
[data-theme="dark"] .loading-hint {
  background: linear-gradient(270deg,
    #818cf8, #a78bfa, #60a5fa, #22d3ee, #34d399, #a78bfa, #818cf8);
  background-size: 300% 100%;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* ---- 按钮文字：流光 ---- */
.el-button--primary,
.el-button--warning,
.el-button--danger,
.el-button--success {
  background-clip: padding-box !important;
}

.el-button--primary span,
.el-button--warning span,
.el-button--danger span,
.el-button--success span {
  position: relative;
  z-index: 1;
}

/* 褪去固定字色让渐变可见（按钮背景已是渐变） */
.el-button span {
  color: inherit;
}

/* ---- 品牌标题：醒目黑色 ---- */
.brand-title {
  font-size: 20px !important;
  font-weight: 800 !important;
  letter-spacing: 0.5px;
  background: none !important;
  -webkit-background-clip: unset !important;
  background-clip: unset !important;
  -webkit-text-fill-color: unset !important;
  color: #111827 !important;
  filter: none;
}

[data-theme="dark"] .brand-title {
  color: #f1f5f9 !important;
}

/* ---- 纯色回退 ---- */
@supports not (-webkit-background-clip: text) {
  h1, h2, h3, .card-header span {
    -webkit-text-fill-color: initial;
    color: #4f46e5;
  }
  .loading-phase, .loading-content h3, .loading-hint {
    -webkit-text-fill-color: initial;
    color: #3b82f6;
  }
}

/* ============================================
   Element Plus 全局深色覆盖
   ============================================ */
[data-theme="dark"] .el-card {
  background-color: var(--bg-card);
  border-color: var(--border-color);
}

[data-theme="dark"] .el-step__title {
  color: var(--text-secondary) !important;
}

[data-theme="dark"] .el-step__title.is-process {
  color: var(--accent) !important;
}

[data-theme="dark"] .el-step__title.is-finish {
  color: var(--text-muted) !important;
}

[data-theme="dark"] .el-step__description {
  color: var(--text-muted) !important;
}

/* 滚动条美化 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: var(--text-muted);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}
</style>
