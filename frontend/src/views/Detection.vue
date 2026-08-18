<template>
  <section class="detection-page">
    <header class="page-heading">
      <div><h2>智能影像检测</h2><p>上传金融业务影像文件夹，系统将自动完成面签照片筛选、相似度分析和可疑交易检索。</p></div>
    </header>

    <el-card class="steps-card" shadow="never">
      <el-steps :active="currentStep" align-center finish-status="success">
        <el-step title="01 上传影像" description="上传影像文件夹"/>
        <el-step title="02 智能分类" description="贷款记录管理"/>
        <el-step title="03 可疑交易检索" description="完成相似度分析"/>
      </el-steps>
    </el-card>

    <section class="upload-block">
      <FolderUpload v-if="!uploadInfo" @upload-success="onUploadSuccess"/>
      <el-card v-else class="upload-complete-card" shadow="never">
        <div class="upload-complete-main"><el-icon :size="28" color="var(--success)"><CircleCheckFilled /></el-icon><div><h3>上传影像文件夹</h3><p>文件夹名称：<strong>{{ uploadInfo.folderName }}</strong></p></div></div>
        <div class="upload-meta"><div><span>文件数量</span><strong>{{ uploadInfo.totalFiles }}</strong></div><div><span>上传状态</span><el-tag type="success" effect="light">上传完成</el-tag></div></div>
        <div class="upload-actions"><el-button type="primary" size="large" @click="resetTask">重新上传</el-button><el-button type="primary" size="large" :loading="processing" :disabled="processing" @click="startDetection"><el-icon><VideoPlay /></el-icon>{{ processing ? '分类中...' : (classified ? '分类完毕' : '开始分类') }}</el-button></div>
      </el-card>
    </section>

    <section v-if="taskSummary" class="result-summary-grid">
      <el-card class="summary-card" shadow="never"><template #header><div class="section-title"><el-icon><DocumentChecked /></el-icon><span>任务概要</span></div></template><dl><div><dt>检测任务ID</dt><dd>{{ taskSummary.taskId }}</dd></div><div><dt>检测时间</dt><dd>{{ taskSummary.detectedAt }}</dd></div><div><dt>检测耗时</dt><dd>{{ taskSummary.duration }}</dd></div></dl></el-card>
      <el-card class="summary-card" shadow="never"><template #header><div class="section-title"><el-icon><DataAnalysis /></el-icon><span>相似度检测统计</span></div></template><div class="similarity-stat"><strong>{{ formatSimilarity(similaritySummary.maxSimilarity) }}</strong><span>最高相似度</span><p>发现 {{ similaritySummary.groupCount }} 个相似组</p></div></el-card>
      <el-card class="summary-card" shadow="never"><template #header><div class="section-title"><el-icon><WarningFilled /></el-icon><span>风险统计</span></div></template><div class="risk-stats"><div><strong>{{ riskCounts.high }}</strong><span>高风险</span></div><div><strong>{{ riskCounts.medium }}</strong><span>中风险</span></div><div><strong>{{ riskCounts.low }}</strong><span>低风险</span></div></div></el-card>
    </section>

    <div class="detection-content">
      <LoanRecordTable v-if="currentStep === 1" :session-id="sessionId" :auto-start="processing" @scan-success="onScanSuccess" @scan-failed="onDetectionFailed" @detect-start="onDetectStart" @detect-success="onSimilaritySuccess" @detect-failed="onDetectionFailed" @go-back="resetTask"/>
      <SimilaritySearch v-if="currentStep >= 2" :session-id="sessionId" :face-images="faceImages" :auto-start="true" @search-success="onSimilaritySuccess" @search-failed="onDetectionFailed" @go-back="currentStep = 1"/>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import { CircleCheckFilled, VideoPlay, DocumentChecked, DataAnalysis, WarningFilled } from '@element-plus/icons-vue'
import FolderUpload from '../components/FolderUpload.vue'
import LoanRecordTable from '../components/LoanRecordTable.vue'
import SimilaritySearch from '../components/SimilaritySearch.vue'

const currentStep = ref(0)
const sessionId = ref('')
const faceImages = ref([])
const uploadInfo = ref(null)
const processing = ref(false)
const classified = ref(false)
const taskSummary = ref(null)
const similarityResult = ref(null)
const startedAt = ref(null)

const similaritySummary = computed(() => {
  const groups = similarityResult.value?.similar_groups || []
  const values = groups.map((group) => group.avg_similarity).filter((value) => typeof value === 'number')
  return { groupCount: groups.length, maxSimilarity: values.length ? Math.max(...values) : null }
})
const riskCounts = computed(() => {
  const groups = similarityResult.value?.similar_groups || []
  return groups.reduce((counts, group) => { const level = group.avg_similarity > .9 ? 'high' : group.avg_similarity > .8 ? 'medium' : 'low'; counts[level] += 1; return counts }, { high: 0, medium: 0, low: 0 })
})
const formatSimilarity = (value) => {
  if (typeof value !== 'number') return '--'
  return `${(value * 100).toFixed(2)}%`
}
const onUploadSuccess = (data) => { sessionId.value = data.session_id; uploadInfo.value = { folderName: data.folder_name || '已上传影像文件夹', totalFiles: data.total_files ?? data.selected_file_count ?? 0 } }
const startDetection = () => { processing.value = true; classified.value = false; taskSummary.value = null; similarityResult.value = null; startedAt.value = Date.now(); currentStep.value = 1 }
const onScanSuccess = () => { processing.value = false; classified.value = true }
const onDetectStart = (images) => { faceImages.value = images || []; currentStep.value = 2 }
const onSimilaritySuccess = (result) => { similarityResult.value = result || {}; const durationSeconds = Math.max(1, Math.round((Date.now() - startedAt.value) / 1000)); taskSummary.value = { taskId: sessionId.value, detectedAt: new Date().toLocaleString('zh-CN', { hour12: false }), duration: `${durationSeconds} 秒` }; currentStep.value = 3 }
const onDetectionFailed = () => { processing.value = false }
const resetTask = () => { currentStep.value = 0; sessionId.value = ''; faceImages.value = []; uploadInfo.value = null; processing.value = false; classified.value = false; taskSummary.value = null; similarityResult.value = null }
</script>

<style scoped>
.detection-page{max-width:1400px;margin:0 auto}.page-heading{margin:4px 0 20px}.page-heading h2{margin:0 0 7px;color:var(--text-primary);font-size:24px}.page-heading p{color:var(--text-secondary);font-size:14px}.steps-card,.upload-complete-card,.summary-card{margin-bottom:20px;border-color:var(--border-color);border-radius:var(--radius-md);background:var(--bg-card)}.steps-card :deep(.el-card__body){padding:26px 34px}.upload-complete-card :deep(.el-card__body){display:flex;align-items:center;gap:26px;padding:23px 28px}.upload-complete-main{display:flex;align-items:center;gap:12px;min-width:250px}.upload-complete-main h3{margin:0 0 7px;font-size:16px;color:var(--text-primary)}.upload-complete-main p{color:var(--text-secondary);font-size:13px}.upload-meta{display:flex;gap:34px;flex:1}.upload-meta>div{display:flex;flex-direction:column;gap:8px}.upload-meta span{font-size:12px;color:var(--text-muted)}.upload-meta strong{font-size:20px;color:var(--text-primary)}.upload-actions{display:flex;gap:10px}.section-title{display:flex;align-items:center;gap:8px;color:var(--text-primary);font-size:16px;font-weight:600}.result-summary-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px;margin-bottom:20px}.summary-card{margin-bottom:0}.summary-card dl{display:flex;flex-direction:column;gap:16px}.summary-card dl>div{display:flex;justify-content:space-between;gap:14px}.summary-card dt{color:var(--text-muted);font-size:13px}.summary-card dd{margin:0;color:var(--text-primary);font-size:13px;font-weight:600;text-align:right}.similarity-stat{display:flex;flex-direction:column;align-items:center;padding:8px 0}.similarity-stat strong{font-size:31px;color:var(--accent)}.similarity-stat span{margin-top:5px;color:var(--text-secondary);font-size:13px}.similarity-stat p{margin:13px 0 0;color:var(--text-muted);font-size:12px}.risk-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;text-align:center}.risk-stats div{display:flex;flex-direction:column;gap:7px;padding:12px 4px;border-radius:var(--radius-sm);background:var(--bg-card-hover)}.risk-stats strong{font-size:23px;color:var(--text-primary)}.risk-stats span{font-size:12px;color:var(--text-muted)}.detection-content{min-width:0}@media(max-width:1280px){.upload-complete-card :deep(.el-card__body){flex-wrap:wrap}.upload-actions{margin-left:auto}}@media(max-width:760px){.steps-card :deep(.el-card__body){padding:18px 12px}.result-summary-grid{grid-template-columns:1fr}.upload-meta{width:100%;justify-content:space-between}.upload-actions{width:100%;margin-left:0}.upload-actions .el-button{flex:1}}
</style>
