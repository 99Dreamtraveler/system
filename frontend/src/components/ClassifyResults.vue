<template>
  <div class="classify-section">
    <el-card class="classify-card" shadow="never">
      <template #header>
        <div class="card-header">
          <el-icon :size="22" color="var(--accent)"><Camera /></el-icon>
          <span>面签照智能筛选</span>
        </div>
      </template>

      <!-- 筛选按钮 -->
      <div class="action-area" v-if="!classified && !loading">
        <div class="action-hint">
          <el-icon :size="48" color="var(--warning)"><InfoFilled /></el-icon>
          <p>上传文件夹已完成，请点击下方按钮开始 AI 面签照智能筛选</p>
          <p class="sub-hint">系统将使用 YOLO 深度学习模型自动检测包含人物的面签合影照片</p>
        </div>
        <el-button
          type="primary"
          size="large"
          @click="runClassification"
          class="classify-btn btn-breathe"
        >
          <el-icon><MagicStick /></el-icon>
          筛选面签照
        </el-button>
      </div>

      <!-- 分类进行中 -->
      <div class="loading-area" v-if="loading">
        <!-- 浮动粒子 -->
        <div class="scan-particles">
          <span v-for="n in 12" :key="n" class="scan-dot" :style="{
            left: (10 + Math.sin(n * 1.8) * 40) + '%',
            top: (15 + Math.cos(n * 2.1) * 35) + '%',
            animationDelay: (n * 0.25) + 's',
            width: (4 + (n % 4) * 3) + 'px',
            height: (4 + (n % 4) * 3) + 'px',
          }"></span>
        </div>

        <div class="loading-content">
          <!-- 核心扫描动画 -->
          <div class="scanner">
            <!-- 外旋转光环 -->
            <svg viewBox="0 0 160 160" class="scanner-ring-outer">
              <circle cx="80" cy="80" r="72" fill="none" stroke="var(--accent)"
                      stroke-width="2" opacity="0.15"/>
              <circle cx="80" cy="80" r="72" fill="none" stroke="var(--accent)"
                      stroke-width="2.5" stroke-linecap="round"
                      stroke-dasharray="60 200" class="scanner-arc"/>
              <circle cx="80" cy="80" r="72" fill="none" stroke="var(--accent)"
                      stroke-width="2.5" stroke-linecap="round"
                      stroke-dasharray="40 220" class="scanner-arc-rev"/>
            </svg>
            <!-- 中圈 -->
            <svg viewBox="0 0 160 160" class="scanner-ring-mid">
              <circle cx="80" cy="80" r="54" fill="none" stroke="var(--accent)"
                      stroke-width="1.5" opacity="0.12"
                      stroke-dasharray="6 12" class="scanner-dots"/>
            </svg>
            <!-- 内图标 -->
            <div class="scanner-core">
              <div class="scanner-pulse"></div>
              <svg viewBox="0 0 48 48" fill="none" class="scanner-icon">
                <rect x="6" y="6" width="36" height="36" rx="4" stroke="var(--accent)" stroke-width="2" fill="none"/>
                <line x1="6" y1="30" x2="42" y2="30" stroke="var(--accent)" stroke-width="1.5" opacity="0.6"/>
                <line x1="6" y1="36" x2="42" y2="36" stroke="var(--accent)" stroke-width="1.5" opacity="0.6"/>
                <circle cx="24" cy="18" r="5" stroke="var(--accent)" stroke-width="2" fill="none" class="pulse-lens"/>
              </svg>
            </div>
          </div>

          <h3>AI 正在智能分析</h3>
          <p class="loading-hint">YOLO 深度学习模型逐张扫描影像，自动识别面签合影照片</p>

          <!-- 阶段指示器 -->
          <div class="phase-indicator">
            <div class="phase-dots">
              <span v-for="(_, i) in phaseTexts" :key="i" class="phase-dot"
                    :class="{ active: currentPhaseIdx === i, done: currentPhaseIdx > i }"></span>
            </div>
            <p class="loading-phase">{{ loadingPhase }}</p>
          </div>

          <el-progress
            :percentage="50"
            :indeterminate="true"
            :stroke-width="4"
            :duration="3"
            :show-text="false"
            class="classify-progress"
          />
        </div>
      </div>

      <!-- 结果展示 -->
      <div class="results-area" v-if="classified && result">
        <!-- 面签照网格 -->
        <div class="face-gallery" v-if="result.face_signing_images.length > 0">
          <h3>
            筛选结果 — 共 {{ result.face_signing_images.length }} 张面签合影照片
            <span v-if="!showAll && result.face_signing_images.length > previewCount" class="preview-tag">
              (预览前 {{ previewCount }} 张)
            </span>
          </h3>
          <div class="image-grid">
            <div
              v-for="img in displayedImages"
              :key="img.image_id"
              class="image-card"
            >
              <el-image
                :src="getImageUrl(img.file_path)"
                fit="cover"
                class="face-image"
                lazy
                :preview-src-list="[getImageUrl(img.file_path)]"
                :preview-teleported="true"
              >
                <template #error>
                  <div class="image-error">
                    <el-icon :size="32"><PictureFilled /></el-icon>
                  </div>
                </template>
              </el-image>
              <div class="image-info">
                <p class="img-loan">{{ img.loan_id }}</p>
              </div>
            </div>
          </div>
          <!-- 展开/折叠按钮 -->
          <div class="toggle-bar" v-if="result.face_signing_images.length > previewCount">
            <el-button
              type="primary"
              text
              @click="showAll = !showAll"
              class="toggle-btn"
            >
              <el-icon><component :is="showAll ? 'ArrowUp' : 'ArrowDown'" /></el-icon>
              {{ showAll ? '收起' : `展开全部 (${result.face_signing_images.length} 张)` }}
            </el-button>
          </div>
        </div>

        <!-- 空状态 -->
        <el-empty v-else description="未检测到包含人物的面签照" />

        <!-- 操作按钮 -->
        <div class="result-actions" v-if="result.face_signing_images.length > 0">
          <el-button @click="goBack" size="large">
            <el-icon><ArrowLeft /></el-icon>
            返回上传
          </el-button>
          <el-button
            type="warning"
            size="large"
            @click="goToSimilarity"
            class="btn-breathe-warning"
          >
            <el-icon><Search /></el-icon>
            可疑交易检索
          </el-button>
        </div>
        <div class="result-actions" v-else>
          <el-button @click="goBack" size="large">
            <el-icon><ArrowLeft /></el-icon>
            返回上传
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Camera, InfoFilled, MagicStick, ArrowLeft, ArrowUp, ArrowDown, Search, PictureFilled } from '@element-plus/icons-vue'
import { runClassify, getFileUrl } from '../api'
import { ElMessage } from 'element-plus'

const props = defineProps({
  sessionId: { type: String, required: true },
  autoStart: { type: Boolean, default: false },
})

const emit = defineEmits(['go-similarity', 'go-back', 'classification-start', 'classification-success', 'classification-failed'])

const loading = ref(false)
const classified = ref(false)
const result = ref(null)
const showAll = ref(false)
const previewCount = 10
const loadingPhase = ref('')
const currentPhaseIdx = ref(0)

const displayedImages = computed(() => {
  if (!result.value?.face_signing_images) return []
  if (showAll.value) return result.value.face_signing_images
  return result.value.face_signing_images.slice(0, previewCount)
})

// 加载阶段文案轮换
const phaseTexts = ['扫描目录结构', '加载 YOLO 模型', '逐张检测人物', '分析置信度', '汇总筛选结果']
let phaseTimer = null

const startPhaseCycle = () => {
  currentPhaseIdx.value = 0
  loadingPhase.value = phaseTexts[0]
  phaseTimer = setInterval(() => {
    currentPhaseIdx.value = (currentPhaseIdx.value + 1) % phaseTexts.length
    loadingPhase.value = phaseTexts[currentPhaseIdx.value]
  }, 2500)
}

const stopPhaseCycle = () => {
  if (phaseTimer) {
    clearInterval(phaseTimer)
    phaseTimer = null
  }
}

const detectionRate = computed(() => {
  if (!result.value) return 0
  return parseFloat(((result.value.person_detected / result.value.total_images) * 100).toFixed(1))
})

const getImageUrl = (filePath) => {
  return getFileUrl(props.sessionId, filePath)
}

const runClassification = async () => {
  loading.value = true
  emit('classification-start')
  startPhaseCycle()
  try {
    const res = await runClassify(props.sessionId)
    result.value = res.data
    classified.value = true
    emit('classification-success', res.data.face_signing_images || [])
    ElMessage.success(res.message || '筛选完成')
  } catch (e) {
    emit('classification-failed', e)
    ElMessage.error('筛选失败：' + (e.message || '未知错误'))
  } finally {
    loading.value = false
    stopPhaseCycle()
  }
}

onMounted(() => {
  if (props.autoStart) runClassification()
})

const goToSimilarity = () => {
  if (result.value && result.value.face_signing_images) {
    emit('go-similarity', result.value.face_signing_images)
  }
}

const goBack = () => {
  emit('go-back')
}
</script>

<style scoped>
.classify-section {
  max-width: 1200px;
  margin: 0 auto;
}

.classify-card {
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  background: var(--bg-card);
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  transition: color 0.3s ease;
}

/* 操作区 */
.action-area {
  text-align: center;
  padding: 40px 20px;
}

.action-hint {
  margin-bottom: 24px;
}

.action-hint p {
  font-size: 15px;
  color: var(--text-secondary);
  margin-top: 12px;
  transition: color 0.3s ease;
}

.action-hint .sub-hint {
  font-size: 13px;
  color: var(--text-muted);
  transition: color 0.3s ease;
}

.classify-btn {
  min-width: 200px;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
}

/* ============================================
   加载中 — 扫描动画
   ============================================ */
.loading-area {
  padding: 60px 20px 50px;
  text-align: center;
  position: relative;
  overflow: hidden;
}

/* 浮动粒子 */
.scan-particles {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.scan-dot {
  position: absolute;
  border-radius: 50%;
  background: var(--accent);
  opacity: 0;
  animation: dot-float 3s ease-in-out infinite;
}

@keyframes dot-float {
  0% { opacity: 0; transform: translateY(0) scale(0); }
  20% { opacity: 0.6; }
  50% { opacity: 0.2; transform: translateY(-30px) scale(1.4); }
  100% { opacity: 0; transform: translateY(-60px) scale(0); }
}

.loading-content {
  max-width: 420px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

/* 扫描器 */
.scanner {
  position: relative;
  width: 160px;
  height: 160px;
  margin: 0 auto 24px;
}

.scanner-ring-outer {
  position: absolute;
  inset: 0;
  width: 160px;
  height: 160px;
  animation: spin 6s linear infinite;
}

.scanner-arc {
  animation: arc-dash 2.5s ease-in-out infinite;
}

.scanner-arc-rev {
  animation: arc-dash 3s ease-in-out infinite reverse;
}

@keyframes arc-dash {
  0% { stroke-dashoffset: 0; }
  50% { stroke-dashoffset: 180; }
  100% { stroke-dashoffset: 0; }
}

.scanner-ring-mid {
  position: absolute;
  inset: 0;
  width: 160px;
  height: 160px;
  animation: spin 10s linear infinite reverse;
}

.scanner-dots {
  animation: dot-spin 1.5s steps(12) infinite;
}

@keyframes dot-spin {
  from { stroke-dashoffset: 0; }
  to { stroke-dashoffset: -72; }
}

.scanner-core {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.scanner-pulse {
  position: absolute;
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background: var(--accent);
  opacity: 0.08;
  animation: core-pulse 2s ease-in-out infinite;
}

@keyframes core-pulse {
  0%, 100% { transform: scale(0.8); opacity: 0.04; }
  50% { transform: scale(1.4); opacity: 0.12; }
}

.scanner-icon {
  position: relative;
  z-index: 1;
  width: 48px;
  height: 48px;
}

.pulse-lens {
  animation: lens-glow 2s ease-in-out infinite;
}

@keyframes lens-glow {
  0%, 100% { opacity: 0.6; r: 5; }
  50% { opacity: 1; r: 6; }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 标题 */
.loading-content h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 6px;
}

.loading-hint {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 24px;
}

/* 阶段指示器 */
.phase-indicator {
  margin-bottom: 20px;
}

.phase-dots {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 12px;
}

.phase-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--border-color);
  transition: all 0.4s ease;
}

.phase-dot.active {
  background: var(--accent);
  box-shadow: 0 0 8px var(--accent-glow);
  transform: scale(1.4);
}

.phase-dot.done {
  background: var(--accent);
  opacity: 0.4;
}

.loading-phase {
  font-size: 13px;
  color: var(--accent);
  font-weight: 500;
  animation: phase-fade 2.5s ease-in-out infinite;
}

@keyframes phase-fade {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

.classify-progress {
  max-width: 300px;
  margin: 0 auto;
}

/* 统计卡片 */
.stats-row {
  display: flex;
  gap: 20px;
  margin-bottom: 28px;
  padding: 20px;
  background: var(--stat-gradient-1);
  border-radius: var(--radius-md);
  flex-wrap: wrap;
  transition: background 0.3s ease;
}

.stats-row > * {
  flex: 1;
  min-width: 120px;
  text-align: center;
}

/* 面签照网格 */
.face-gallery h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
  transition: color 0.3s ease;
}

.preview-tag {
  font-size: 13px;
  font-weight: 400;
  color: var(--text-muted);
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.image-card {
  position: relative;
  border-radius: var(--radius-sm);
  overflow: hidden;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  transition: all 0.3s;
}

.image-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.face-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.image-error {
  width: 100%;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--border-light);
  color: var(--text-muted);
  transition: background-color 0.3s ease;
}

.image-info {
  padding: 10px 12px;
}

.img-loan {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  transition: color 0.3s ease;
}

.img-conf {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 2px;
  transition: color 0.3s ease;
}

.img-tag {
  position: absolute;
  top: 8px;
  right: 8px;
}

.toggle-bar {
  text-align: center;
  margin-top: 20px;
}

.toggle-btn {
  font-size: 14px;
  font-weight: 500;
}

.result-actions {
  margin-top: 28px;
  display: flex;
  gap: 12px;
  justify-content: center;
}
</style>
