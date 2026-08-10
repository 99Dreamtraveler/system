<template>
  <section class="detection-page">
    <header class="page-heading">
      <div><h2>智能影像检测</h2><p>上传金融业务影像文件夹，系统将自动完成面签照片筛选、相似度分析和可疑交易检索。</p></div>
    </header>

    <el-card class="steps-card" shadow="never">
      <el-steps :active="currentStep" align-center finish-status="success">
        <el-step title="01 上传影像" description="上传影像文件夹"/>
        <el-step title="02 面签照筛选" description="筛选待比对影像"/>
        <el-step title="03 可疑交易检索" description="完成相似度分析"/>
      </el-steps>
    </el-card>

    <section class="upload-block">
      <FolderUpload v-if="!uploadInfo" @upload-success="onUploadSuccess"/>
      <el-card v-else class="upload-complete-card" shadow="never">
        <div class="upload-complete-main"><el-icon :size="28" color="var(--success)"><CircleCheckFilled /></el-icon><div><h3>上传影像文件夹</h3><p>文件夹名称：<strong>{{ uploadInfo.folderName }}</strong></p></div></div>
        <div class="upload-meta"><div><span>文件数量</span><strong>{{ uploadInfo.totalFiles }}</strong></div><div><span>上传状态</span><el-tag type="success" effect="light">上传完成</el-tag></div></div>
        <div class="upload-actions"><el-button @click="resetTask">重新上传</el-button><el-button type="primary" size="large" :loading="processing" :disabled="processing" @click="startDetection"><el-icon><VideoPlay /></el-icon>{{ processing ? '检测中...' : '开始检测' }}</el-button></div>
      </el-card>
    </section>

    <el-card class="types-card" shadow="never">
      <template #header><div class="section-title"><el-icon><Files /></el-icon><span>支持的影像类型</span></div></template>
      <div class="type-list"><el-tag v-for="item in imageTypes" :key="item" effect="plain" size="large">{{ item }}</el-tag></div>
    </el-card>

    <el-card v-if="showProcess" class="process-card" shadow="never">
      <template #header><div class="section-title"><el-icon><Operation /></el-icon><span>检测处理流程</span></div></template>
      <div class="process-list"><div v-for="(item,index) in processSteps" :key="item.label" class="process-item" :class="processClass(index)"><span class="process-index">0{{ index + 1 }}</span><span class="process-label">{{ item.label }}</span><el-tag size="small" :type="processTagType(index)">{{ processStatus(index) }}</el-tag></div></div>
      <div v-if="failedStep !== null" class="process-error"><el-alert title="检测失败，请检查网络连接或上传文件夹后重新检测。" type="error" :closable="false" show-icon/><el-button type="primary" @click="startDetection">重新检测</el-button></div>
    </el-card>

    <section v-if="taskSummary" class="result-summary-grid">
      <el-card class="summary-card" shadow="never"><template #header><div class="section-title"><el-icon><DocumentChecked /></el-icon><span>任务概要</span></div></template><dl><div><dt>检测任务ID</dt><dd>{{ taskSummary.taskId }}</dd></div><div><dt>检测时间</dt><dd>{{ taskSummary.detectedAt }}</dd></div><div><dt>检测耗时</dt><dd>{{ taskSummary.duration }}</dd></div></dl></el-card>
      <el-card class="summary-card" shadow="never"><template #header><div class="section-title"><el-icon><DataAnalysis /></el-icon><span>相似度检测统计</span></div></template><div class="similarity-stat"><strong>{{ similaritySummary.maxSimilarity === null ? '--' : `${(similaritySummary.maxSimilarity * 100).toFixed(2)}%` }}</strong><span>最高相似度</span><p>发现 {{ similaritySummary.groupCount }} 个相似组</p></div></el-card>
      <el-card class="summary-card" shadow="never"><template #header><div class="section-title"><el-icon><WarningFilled /></el-icon><span>风险统计</span></div></template><div class="risk-stats"><div><strong>{{ riskCounts.high }}</strong><span>高风险</span></div><div><strong>{{ riskCounts.medium }}</strong><span>中风险</span></div><div><strong>{{ riskCounts.low }}</strong><span>低风险</span></div></div></el-card>
    </section>

    <section v-if="classificationCompleted" class="history-preview-card">
      <div class="history-preview-header"><div class="section-title"><el-icon><Clock /></el-icon><span>历史面签照片预览</span></div><el-tag type="info" effect="plain">MOCK · 待后端接入</el-tag></div>
      <p class="history-preview-note">当前仅展示接口契约 Mock 数据，不参与本次检测、相似度计算或风险统计。</p>
      <div v-if="historyLoading" class="history-preview-state">正在加载预览数据...</div>
      <div v-else-if="historicalPhotos.length" class="history-preview-list"><div v-for="photo in historicalPhotos" :key="photo.photoId" class="history-preview-item"><span class="history-photo-id">{{ photo.photoId }}</span><span>{{ photo.businessId }}</span><span>{{ photo.loanId }}</span><span>{{ photo.captureTime }}</span></div></div>
      <el-empty v-else description="暂无历史面签照片 Mock 数据" :image-size="54" />
    </section>

    <div class="detection-content">
      <ClassifyResults v-if="currentStep === 1" :session-id="sessionId" :auto-start="processing" @classification-start="onClassificationStart" @classification-success="onClassificationSuccess" @classification-failed="onDetectionFailed" @go-similarity="goToSimilarity" @go-back="resetTask"/>
      <SimilaritySearch v-if="currentStep === 2" :session-id="sessionId" :face-images="faceImages" :auto-start="processing" @search-start="onSimilarityStart" @search-success="onSimilaritySuccess" @search-failed="onDetectionFailed" @go-back="currentStep = 1"/>
    </div>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { CircleCheckFilled, VideoPlay, Files, Operation, DocumentChecked, DataAnalysis, WarningFilled, Clock } from '@element-plus/icons-vue'
import FolderUpload from '../components/FolderUpload.vue'
import ClassifyResults from '../components/ClassifyResults.vue'
import SimilaritySearch from '../components/SimilaritySearch.vue'
import { getHistoricalInterviewPhotos } from '../api/history'

const currentStep = ref(0)
const sessionId = ref('')
const faceImages = ref([])
const uploadInfo = ref(null)
const processing = ref(false)
const activeProcessStep = ref(-1)
const failedStep = ref(null)
const taskSummary = ref(null)
const similarityResult = ref(null)
const startedAt = ref(null)
const classificationCompleted = ref(false)
const historicalPhotos = ref([])
const historyLoading = ref(false)
let similarityPhaseTimer = null

const imageTypes = ['面签照片', '身份证明正面', '身份证明反面', '银行流水', '合同文档']
const processSteps = [{ label: '文件夹解析' }, { label: '面签照片筛选' }, { label: '特征提取' }, { label: '相似度计算' }, { label: '可疑交易检索' }, { label: '检测完成' }]
const showProcess = computed(() => uploadInfo.value !== null)
const similaritySummary = computed(() => {
  const groups = similarityResult.value?.similar_groups || []
  const values = groups.map((group) => group.avg_similarity).filter((value) => typeof value === 'number')
  return { groupCount: groups.length, maxSimilarity: values.length ? Math.max(...values) : null }
})
const riskCounts = computed(() => {
  const groups = similarityResult.value?.similar_groups || []
  return groups.reduce((counts, group) => { const level = group.avg_similarity > .9 ? 'high' : group.avg_similarity > .8 ? 'medium' : 'low'; counts[level] += 1; return counts }, { high: 0, medium: 0, low: 0 })
})
const processClass = (index) => ({ done: failedStep.value === null && index < activeProcessStep.value, active: failedStep.value === null && index === activeProcessStep.value, failed: index === failedStep.value })
const processStatus = (index) => index === failedStep.value ? '检测失败' : index < activeProcessStep.value ? '已完成' : index === activeProcessStep.value ? '进行中' : '等待'
const processTagType = (index) => index === failedStep.value ? 'danger' : index < activeProcessStep.value ? 'success' : index === activeProcessStep.value ? 'primary' : 'info'
const onUploadSuccess = (data) => { sessionId.value = data.session_id; uploadInfo.value = { folderName: data.folder_name || '已上传影像文件夹', totalFiles: data.total_files ?? data.selected_file_count ?? 0 }; activeProcessStep.value = 1 }
const startDetection = () => { clearSimilarityTimer(); processing.value = true; failedStep.value = null; taskSummary.value = null; similarityResult.value = null; startedAt.value = Date.now(); activeProcessStep.value = 1; currentStep.value = 1 }
const onClassificationStart = () => { activeProcessStep.value = 1 }
const onClassificationSuccess = (images) => { faceImages.value = images || []; classificationCompleted.value = true; activeProcessStep.value = 2; currentStep.value = 2 }
const goToSimilarity = (images) => { faceImages.value = images; currentStep.value = 2 }
const onSimilarityStart = () => { activeProcessStep.value = 2; similarityPhaseTimer = window.setInterval(() => { if (activeProcessStep.value < 4) activeProcessStep.value += 1 }, 1800) }
const onSimilaritySuccess = (result) => { clearSimilarityTimer(); similarityResult.value = result || {}; activeProcessStep.value = 6; processing.value = false; const durationSeconds = Math.max(1, Math.round((Date.now() - startedAt.value) / 1000)); taskSummary.value = { taskId: sessionId.value, detectedAt: new Date().toLocaleString('zh-CN', { hour12: false }), duration: `${durationSeconds} 秒` } }
const onDetectionFailed = () => { clearSimilarityTimer(); failedStep.value = activeProcessStep.value; processing.value = false }
const clearSimilarityTimer = () => { if (similarityPhaseTimer) { clearInterval(similarityPhaseTimer); similarityPhaseTimer = null } }
const loadHistoricalPhotos = async () => { historyLoading.value = true; try { const res = await getHistoricalInterviewPhotos({ page: 1, pageSize: 4 }); historicalPhotos.value = res.data.records || [] } catch { historicalPhotos.value = [] } finally { historyLoading.value = false } }
const resetTask = () => { clearSimilarityTimer(); currentStep.value = 0; sessionId.value = ''; faceImages.value = []; uploadInfo.value = null; processing.value = false; activeProcessStep.value = -1; failedStep.value = null; taskSummary.value = null; similarityResult.value = null; classificationCompleted.value = false }
onMounted(loadHistoricalPhotos)
onBeforeUnmount(clearSimilarityTimer)
</script>

<style scoped>
.detection-page{max-width:1400px;margin:0 auto}.page-heading{margin:4px 0 20px}.page-heading h2{margin:0 0 7px;color:var(--text-primary);font-size:24px}.page-heading p{color:var(--text-secondary);font-size:14px}.steps-card,.types-card,.process-card,.upload-complete-card,.summary-card,.history-preview-card{margin-bottom:20px;border-color:var(--border-color);border-radius:var(--radius-md);background:var(--bg-card)}.steps-card :deep(.el-card__body){padding:26px 34px}.upload-complete-card :deep(.el-card__body){display:flex;align-items:center;gap:26px;padding:23px 28px}.upload-complete-main{display:flex;align-items:center;gap:12px;min-width:250px}.upload-complete-main h3{margin:0 0 7px;font-size:16px;color:var(--text-primary)}.upload-complete-main p{color:var(--text-secondary);font-size:13px}.upload-meta{display:flex;gap:34px;flex:1}.upload-meta>div{display:flex;flex-direction:column;gap:8px}.upload-meta span{font-size:12px;color:var(--text-muted)}.upload-meta strong{font-size:20px;color:var(--text-primary)}.upload-actions{display:flex;gap:10px}.section-title{display:flex;align-items:center;gap:8px;color:var(--text-primary);font-size:16px;font-weight:600}.type-list{display:flex;flex-wrap:wrap;gap:11px}.process-list{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:10px}.process-item{display:flex;flex-direction:column;align-items:flex-start;gap:9px;min-height:105px;padding:15px;border:1px solid var(--border-color);border-radius:var(--radius-sm);background:var(--bg-card-hover)}.process-index{color:var(--text-muted);font-size:12px}.process-label{flex:1;color:var(--text-secondary);font-size:14px;font-weight:600}.process-item.done{border-color:rgba(16,185,129,.35);background:var(--success-light)}.process-item.done .process-index,.process-item.done .process-label{color:var(--success)}.process-item.active{border-color:rgba(99,102,241,.45);background:var(--accent-light);box-shadow:0 0 0 2px rgba(99,102,241,.08)}.process-item.active .process-label{color:var(--accent)}.process-item.failed{border-color:rgba(239,68,68,.45);background:var(--danger-light)}.process-error{display:flex;align-items:center;gap:16px;margin-top:16px}.process-error .el-alert{flex:1}.result-summary-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px;margin-bottom:20px}.summary-card{margin-bottom:0}.summary-card dl{display:flex;flex-direction:column;gap:16px}.summary-card dl>div{display:flex;justify-content:space-between;gap:14px}.summary-card dt{color:var(--text-muted);font-size:13px}.summary-card dd{margin:0;color:var(--text-primary);font-size:13px;font-weight:600;text-align:right}.similarity-stat{display:flex;flex-direction:column;align-items:center;padding:8px 0}.similarity-stat strong{font-size:31px;color:var(--accent)}.similarity-stat span{margin-top:5px;color:var(--text-secondary);font-size:13px}.similarity-stat p{margin:13px 0 0;color:var(--text-muted);font-size:12px}.risk-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;text-align:center}.risk-stats div{display:flex;flex-direction:column;gap:7px;padding:12px 4px;border-radius:var(--radius-sm);background:var(--bg-card-hover)}.risk-stats strong{font-size:23px;color:var(--text-primary)}.risk-stats span{font-size:12px;color:var(--text-muted)}.history-preview-card{padding:20px 24px;border:1px solid var(--border-color)}.history-preview-header{display:flex;align-items:center;justify-content:space-between;gap:12px}.history-preview-note{margin:10px 0 15px;color:var(--text-secondary);font-size:13px}.history-preview-state{color:var(--text-muted);font-size:13px}.history-preview-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.history-preview-item{display:grid;grid-template-columns:1.2fr 1fr 1fr 1.35fr;gap:8px;padding:12px;border:1px solid var(--border-color);border-radius:var(--radius-sm);color:var(--text-secondary);font-size:12px}.history-photo-id{color:var(--accent);font-weight:600}.detection-content{min-width:0}@media(max-width:1280px){.process-list{grid-template-columns:repeat(3,minmax(0,1fr))}.upload-complete-card :deep(.el-card__body){flex-wrap:wrap}.upload-actions{margin-left:auto}.history-preview-list{grid-template-columns:1fr}}@media(max-width:760px){.steps-card :deep(.el-card__body){padding:18px 12px}.process-list,.result-summary-grid{grid-template-columns:1fr}.upload-meta{width:100%;justify-content:space-between}.upload-actions{width:100%;margin-left:0}.upload-actions .el-button{flex:1}.process-error{align-items:stretch;flex-direction:column}.history-preview-header{align-items:flex-start;flex-direction:column}.history-preview-item{grid-template-columns:1fr 1fr}}
</style>
