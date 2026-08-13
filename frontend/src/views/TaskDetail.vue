<template>
  <section class="task-detail-page">
    <header class="page-heading"><div><el-button link type="primary" @click="router.push('/tasks')"><el-icon><ArrowLeft /></el-icon>返回任务列表</el-button><h2>检测任务详情</h2><p>查看任务基本信息、统计数据及检测结果。</p></div><el-tag v-if="isMock" type="info" effect="plain">MOCK · 后端无数据时展示</el-tag></header>
    <div v-if="loading" class="loading-panel"><el-skeleton :rows="8" animated /></div>
    <div v-else-if="error" class="state-panel"><el-alert title="检测任务加载失败，请稍后重试。" type="error" :closable="false" show-icon /><el-button type="primary" @click="loadTask">重新加载</el-button></div>
    <template v-else-if="task">
      <el-card class="panel-card" shadow="never"><template #header><div class="panel-title">任务基本信息</div></template><dl class="task-info"><div><dt>任务编号</dt><dd>{{ task.taskId }}</dd></div><div><dt>创建时间</dt><dd>{{ task.createdAt }}</dd></div><div><dt>相似度</dt><dd class="similarity-value">{{ formatSimilarity(task.similarity) }}</dd></div><div><dt>风险等级</dt><dd><el-tag :type="riskTagType(task.riskLevel)" effect="light">{{ task.riskLevel }}</el-tag></dd></div><div><dt>状态</dt><dd><el-tag :type="statusTagType(task.status)" effect="light">{{ task.status }}</el-tag></dd></div></dl></el-card>
      <section class="stats-grid"><el-card class="panel-card" shadow="never"><template #header><div class="panel-title">影像统计</div></template><div class="stat-line"><span>已解析影像</span><strong>{{ task.imageStats.valid }}</strong></div></el-card><el-card class="panel-card" shadow="never"><template #header><div class="panel-title">面签筛选统计</div></template><div class="stat-line"><span>面签照片</span><strong>{{ task.screeningStats.interviewPhotos }}</strong></div></el-card><el-card class="panel-card" shadow="never"><template #header><div class="panel-title">相似度统计</div></template><div class="stat-line"><span>最高相似度</span><strong>{{ formatSimilarity(task.similarityStats.maxSimilarity) }}</strong></div><div class="stat-line"><span>相似组</span><strong>{{ task.similarityStats.similarGroups }}</strong></div></el-card><el-card class="panel-card" shadow="never"><template #header><div class="panel-title">风险统计</div></template><div class="risk-line"><span>高 {{ task.riskStats.high }}</span><span>中 {{ task.riskStats.medium }}</span><span>低 {{ task.riskStats.low }}</span></div></el-card></section>
      <el-card class="panel-card" shadow="never"><template #header><div class="panel-title">异常影像</div></template><el-table v-if="task.abnormalImages.length" :data="task.abnormalImages"><el-table-column prop="name" label="影像文件" min-width="220"/><el-table-column prop="reason" label="检测结果" min-width="260"/><el-table-column label="相似度" width="130"><template #default="{ row }">{{ formatSimilarity(row.similarity) }}</template></el-table-column></el-table><el-empty v-else description="暂无异常影像" :image-size="72" /></el-card>
    </template>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { getDetectionTask } from '../api/tasks'

const route = useRoute(); const router = useRouter(); const task = ref(null); const loading = ref(true); const error = ref(false); const isMock = ref(false)
const formatSimilarity = (value) => (typeof value === 'number' ? `${value.toFixed(2)}%` : '--')
const riskTagType = (level) => ({ 待检测: 'info', 高风险: 'danger', 中风险: 'warning', 低风险: 'success' }[level] || 'info')
const statusTagType = (status) => ({ 待检测: 'info', 检测中: 'primary', 已完成: 'success', 检测失败: 'danger' }[status] || 'info')
const loadTask = async () => { loading.value = true; error.value = false; try { const res = await getDetectionTask(route.params.id); task.value = res.data; isMock.value = Boolean(res.mock) } catch { error.value = true; task.value = null } finally { loading.value = false } }
onMounted(loadTask)
</script>

<style scoped>
.task-detail-page{max-width:1400px;margin:0 auto}.page-heading{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;margin:4px 0 20px}.page-heading h2{margin:10px 0 7px;color:var(--text-primary);font-size:24px}.page-heading p{color:var(--text-secondary);font-size:14px}.panel-card,.loading-panel{margin-bottom:20px;border-color:var(--border-color);border-radius:var(--radius-md);background:var(--bg-card)}.loading-panel{padding:24px}.panel-title{color:var(--text-primary);font-size:16px;font-weight:600}.task-info{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:16px}.task-info div{min-width:0}.task-info dt{margin-bottom:8px;color:var(--text-muted);font-size:12px}.task-info dd{margin:0;overflow:hidden;color:var(--text-primary);font-size:14px;font-weight:600;text-overflow:ellipsis;white-space:nowrap}.task-info .similarity-value{color:var(--accent);font-size:20px}.stats-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:20px}.stat-line{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:5px 0;color:var(--text-secondary);font-size:13px}.stat-line strong{color:var(--text-primary);font-size:19px}.risk-line{display:flex;justify-content:space-between;gap:8px;color:var(--text-secondary);font-size:13px}.state-panel{display:flex;align-items:center;gap:16px}.state-panel .el-alert{flex:1}@media(max-width:1000px){.task-info{grid-template-columns:repeat(3,minmax(0,1fr))}.stats-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:620px){.page-heading{flex-direction:column}.task-info,.stats-grid{grid-template-columns:1fr}.state-panel{align-items:stretch;flex-direction:column}}
</style>
