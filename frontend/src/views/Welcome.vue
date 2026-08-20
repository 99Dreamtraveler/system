<template>
  <div class="welcome-container">
    <div class="background-grid" aria-hidden="true"></div>
    <div class="verification-ring ring-large" aria-hidden="true"></div>
    <div class="verification-ring ring-small" aria-hidden="true"></div>

    <header class="top-nav">
      <div class="nav-brand">
        <span class="brand-mark" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none">
            <path d="M12 2.7 19 6v5.2c0 4.6-2.8 7.9-7 9.4-4.2-1.5-7-4.8-7-9.4V6l7-3.3Z" stroke="currentColor" stroke-width="1.9" stroke-linejoin="round"/>
            <path d="m8.6 11.6 2.2 2.2 4.7-4.8" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </span>
        <span>金融影像智能检测平台</span>
      </div>
      <div class="secure-status"><span></span>安全核验通道</div>
    </header>

    <main class="main-body">
      <section class="hero-section" aria-labelledby="welcome-title">
        <div class="hero-content">
          <p class="eyebrow">INTELLIGENT RISK VERIFICATION</p>
          <h1 id="welcome-title">让每一次金融影像<br>核验都更<span>可靠</span></h1>
          <p class="hero-desc">面向业务人员的智能相似度检测平台，快速识别异常影像与潜在风险交易，为业务决策提供可信依据。</p>
          <div class="capabilities">
            <div class="capability">
              <strong>图像识别</strong>
              <span>影像与交易信息联合核验</span>
            </div>
            <div class="capability">
              <strong>风险预警</strong>
              <span>聚焦可疑相似交易</span>
            </div>
          </div>
        </div>
      </section>

      <section class="auth-section" aria-label="账户登录">
        <div class="auth-card">
          <div class="auth-heading">
            <h2>欢迎登录</h2>
            <p>请输入您的账户信息以进入系统</p>
          </div>
          <LoginRegister @login-success="onLoginSuccess" />
          <p class="security-note">账户信息将通过加密通道传输</p>
        </div>
      </section>
    </main>

    <footer>FINANCIAL IMAGE INTELLIGENCE · 2026</footer>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import LoginRegister from '../components/LoginRegister.vue'

const router = useRouter()

const onLoginSuccess = (user) => {
  localStorage.setItem('user', JSON.stringify({
    ...user,
    role: '业务员',
  }))
  router.push('/dashboard')
}
</script>

<style scoped>
.welcome-container { position:relative; min-height:100vh; overflow:hidden; color:#1f2937; background:linear-gradient(135deg,#f5f7fa 0%,#f8fbfd 55%,#eef6fb 100%); }
.background-grid { position:absolute; inset:0 0 28%; opacity:.58; background-image:linear-gradient(rgba(85,150,191,.08) 1px,transparent 1px),linear-gradient(90deg,rgba(85,150,191,.08) 1px,transparent 1px); background-size:48px 48px; mask-image:linear-gradient(to bottom,#000,transparent); }
.verification-ring { position:absolute; border:1px solid rgba(75,145,190,.18); border-radius:50%; pointer-events:none; }
.ring-large { width:670px; height:670px; left:-255px; top:170px; }
.ring-small { width:485px; height:485px; left:-163px; top:263px; border-color:rgba(75,145,190,.12); }
.top-nav { position:relative; z-index:1; height:82px; display:flex; align-items:center; justify-content:space-between; padding:0 5.4%; border-bottom:1px solid rgba(29,61,88,.10); }
.nav-brand { display:flex; align-items:center; gap:14px; color:#1f3347; font-size:18px; font-weight:700; letter-spacing:.4px; white-space:nowrap; }
.brand-mark { width:38px; height:38px; display:grid; place-items:center; color:#fff; border:0; border-radius:10px; background:#167bc5; box-shadow:0 6px 16px rgba(22,123,197,.20); }
.brand-mark svg { width:23px; height:23px; }
.secure-status { display:flex; align-items:center; color:#6b7e8d; font-size:13px; letter-spacing:1px; white-space:nowrap; }
.secure-status span { width:7px; height:7px; margin-right:9px; border-radius:50%; background:#27a877; box-shadow:0 0 8px rgba(39,168,119,.32); }
.main-body { position:relative; z-index:1; min-height:calc(100vh - 82px); display:flex; align-items:center; justify-content:center; gap:clamp(80px,11vw,180px); padding:50px 7% 78px; }
.hero-section { width:min(520px,42vw); }
.eyebrow { margin:0 0 21px; color:#167bc5; font-size:13px; font-weight:600; letter-spacing:2.8px; }
.hero-content h1 { margin:0; color:#16324f; font-size:48px; font-weight:700; line-height:1.25; letter-spacing:0; background:none; -webkit-text-fill-color:currentColor; }
.hero-content h1 span { color:#167bc5; }
.hero-desc { max-width:460px; margin:24px 0 38px; color:#5e7180; font-size:16px; line-height:1.9; }
.capabilities { display:flex; gap:38px; }
.capability { min-width:170px; padding-left:14px; border-left:1px solid #9bcce8; }
.capability strong { display:block; color:#1f3347; font-size:19px; }
.capability span { display:block; margin-top:7px; color:#718393; font-size:12px; }
.auth-section { width:408px; flex:0 0 auto; }
.auth-card { padding:40px 36px 28px; border:1px solid #dce6ed; border-radius:8px; background:#fff; box-shadow:0 20px 48px rgba(28,64,92,.12); }
.auth-heading { margin-bottom:25px; }
.auth-heading h2 { margin:0 0 8px; color:#1f3347; font-size:25px; font-weight:700; letter-spacing:0; background:none; -webkit-text-fill-color:currentColor; }
.auth-heading p { margin:0; color:#718393; font-size:13px; }
.security-note { margin:18px 0 0; color:#8494a1; font-size:12px; text-align:center; }
footer { position:absolute; z-index:1; right:5.4%; bottom:28px; color:#8494a1; font-size:12px; letter-spacing:1px; }
@media (max-width:1024px) { .main-body { gap:56px; padding-left:6%; padding-right:6%; } .hero-section { width:min(430px,42vw); } .hero-content h1 { font-size:40px; } .capabilities { gap:18px; } }
@media (max-width:760px) { .welcome-container { min-height:100dvh; } .top-nav { height:64px; padding:0 20px; } .nav-brand { font-size:15px; } .brand-mark { width:33px; height:33px; border-radius:8px; } .secure-status { display:none; } .main-body { min-height:auto; flex-direction:column; align-items:stretch; gap:30px; padding:62px 24px 48px; } .hero-section { width:auto; } .hero-content h1 { font-size:34px; } .hero-desc { margin:17px 0 25px; font-size:14px; } .capabilities { gap:18px; } .capability { min-width:0; flex:1; } .capability strong { font-size:16px; } .capability span { line-height:1.5; } .auth-section { width:100%; max-width:408px; align-self:center; } .auth-card { padding:30px 24px 24px; } .ring-small { display:none; } footer { position:static; padding:0 24px 24px; font-size:10px; } }
</style>
