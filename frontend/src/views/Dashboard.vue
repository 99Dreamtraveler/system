<template>
  <section class="dashboard-page">
    <div class="page-heading">
      <div>
        <h2>风险监测概览</h2>
        <p>实时掌握影像检测任务、异常影像及风险案件情况</p>
      </div>
    </div>

    <section class="dashboard-overview" aria-label="智能检测入口与风险概览">
      <el-card class="detection-entry-card" shadow="never">
        <div class="entry-copy">
          <p class="entry-eyebrow">INTELLIGENT IMAGE RISK CONTROL</p>
          <h3>发起影像检测</h3>
          <p>导入业务影像，自动完成面签筛选、相似度分析和风险定位。</p>
          <el-button class="entry-button" size="large" @click="goToDetection"><el-icon><Search /></el-icon>开始检测</el-button>
          <span class="entry-support">支持：面签照片 / 身份证 / 合同 / 银行流水</span>
        </div>
        <div class="entry-visual" aria-hidden="true"><div class="entry-orbit"><el-icon :size="38"><Search /></el-icon></div></div>
      </el-card>

      <el-card class="overview-card" shadow="never">
        <template #header><div class="panel-header"><span>当前风险概览</span><el-tag type="success" effect="light"><el-icon><CircleCheckFilled /></el-icon>系统运行正常</el-tag></div></template>
        <div class="overview-metrics">
          <div v-for="item in metricCards" :key="item.key" class="overview-metric">
            <div class="metric-icon" :class="item.tone"><el-icon :size="20"><component :is="item.icon" /></el-icon></div>
            <div><p>{{ item.label }}</p><strong>{{ formatNumber(item.value) }}</strong></div>
          </div>
        </div>
      </el-card>
    </section>

    <section class="chart-grid">
      <el-card class="panel-card trend-panel" shadow="never">
        <template #header><div class="panel-header"><span>近7日检测趋势</span><div class="chart-legend"><i class="detection-dot"/>检测任务<i class="abnormal-dot"/>异常影像</div></div></template>
        <svg class="trend-chart" viewBox="0 0 720 260" preserveAspectRatio="none" role="img" aria-labelledby="trend-title trend-description">
          <title id="trend-title">近7日检测趋势</title><desc id="trend-description">展示每日创建的检测任务数量和异常影像数量。</desc>
          <g class="chart-grid-lines"><line v-for="line in gridLines" :key="line" x1="46" :y1="line" x2="696" :y2="line"/></g>
          <g class="axis-labels"><text v-for="value in yAxisValues" :key="value" x="4" :y="yCoordinate(value) + 4">{{ value }}</text></g>
          <path class="detection-area" :d="detectionAreaPath"/><path class="detection-line" :d="detectionPath"/>
          <path class="abnormal-line" :d="abnormalPath"/>
          <g v-for="(point, index) in detectionPoints" :key="point.date"><circle class="detection-point" :cx="point.x" :cy="point.y" r="4"/><circle class="abnormal-point" :cx="point.x" :cy="abnormalPoints[index].y" r="4"/><text class="x-label" :x="point.x" y="244">{{ point.date }}</text></g>
        </svg>
      </el-card>

      <el-card class="panel-card risk-panel" shadow="never">
        <template #header><div class="panel-header"><span>风险等级分布</span></div></template>
        <div class="risk-content">
          <div class="donut" :style="{ background: donutGradient }"><div class="donut-center"><strong>{{ riskTotal }}</strong><span>检测任务</span></div></div>
          <div class="risk-legend"><div v-for="item in riskItems" :key="item.key"><span class="legend-dot" :class="item.key"/><span>{{ item.label }}</span><strong>{{ item.value }}</strong></div></div>
        </div>
      </el-card>
    </section>

    <section class="lower-grid">
      <el-card class="panel-card task-panel" shadow="never">
        <template #header><div class="panel-header"><span>最近检测任务</span><el-button link type="primary" @click="router.push('/tasks')">查看全部</el-button></div></template>
        <el-table :data="recentTasks" size="small" class="tasks-table" :header-cell-style="tableHeaderStyle">
          <el-table-column prop="id" label="任务编号" min-width="165"/>
          <el-table-column prop="detectedAt" label="检测时间" min-width="150"/>
          <el-table-column label="风险等级" min-width="105"><template #default="{ row }"><el-tag :type="riskTagType(row.riskLevel)" size="small">{{ row.riskLevel }}</el-tag></template></el-table-column>
          <el-table-column label="状态" min-width="95"><template #default="{ row }"><el-tag :type="statusTagType(row.status)" effect="plain" size="small">{{ row.status }}</el-tag></template></el-table-column>
          <el-table-column label="操作" width="90" fixed="right"><template #default="{ row }"><el-button link type="primary" size="small" @click="openTask(row.id)">查看详情</el-button></template></el-table-column>
        </el-table>
      </el-card>

      <el-card class="panel-card case-panel" shadow="never">
        <template #header><div class="panel-header"><span>近期高风险案件</span><el-button link type="primary" @click="router.push('/risk-cases')">查看全部</el-button></div></template>
        <div class="case-list"><div v-for="item in highRiskCases" :key="item.id" class="case-row"><div><strong>{{ item.id }}</strong><p>{{ item.foundAt }} · {{ item.status }}</p></div><div class="case-risk"><span>相似度 {{ (item.similarity * 100).toFixed(1) }}%</span><el-tag type="danger" size="small">高风险</el-tag></div><el-button type="primary" plain size="small" @click="openCase(item.id)">查看案件</el-button></div></div>
      </el-card>

    </section>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Picture, UserFilled, WarningFilled, CircleCloseFilled, Calendar, Finished, CircleCheckFilled, Search } from '@element-plus/icons-vue'
import { getAnalyticsStatistics } from '../api/analytics'

const router = useRouter()
const statistics = ref({ detectionTrend: [], riskDistribution: { high: 0, medium: 0, low: 0 }, tasks: [], cases: [] })
let statisticsTimer = null
const detectionTrend = computed(() => statistics.value.detectionTrend.map((item) => ({ date: item.date.slice(5), detections: item.detectionCount, abnormalImages: item.abnormalCount })))
const distribution = computed(() => statistics.value.riskDistribution)
const recentTasks = computed(() => statistics.value.tasks.slice(0, 5).map((task) => ({ id: task.taskId, detectedAt: task.detectedAt || task.createdAt, riskLevel: task.riskLevel, status: task.status })))
const highRiskCases = computed(() => statistics.value.cases.filter((item) => item.riskLevel === '高风险').slice(0, 5).map((item) => ({ id: item.caseId, similarity: item.similarity / 100, foundAt: item.discoveredAt, status: item.status })))
const metrics = computed(() => ({ totalImages: statistics.value.detectionTrend.reduce((sum, item) => sum + item.detectionCount, 0), affectedCount: statistics.value.tasks.reduce((sum, item) => sum + (item.interviewImages || 0), 0), abnormalImages: statistics.value.detectionTrend.reduce((sum, item) => sum + item.abnormalCount, 0), highRiskCases: distribution.value.high, todayTasks: statistics.value.tasks.filter((item) => item.createdAt?.startsWith(new Date().toISOString().slice(0, 10))).length, completedTasks: statistics.value.tasks.filter((item) => item.status === '已完成').length }))
const chartWidth = 650
const chartLeft = 46
const chartTop = 20
const chartHeight = 180
const yMax = computed(() => Math.max(1, ...detectionTrend.value.flatMap((item) => [item.detections, item.abnormalImages])))
const gridLines = [20, 65, 110, 155, 200]
const yAxisValues = computed(() => [yMax.value, Math.ceil(yMax.value * .75), Math.ceil(yMax.value * .5), Math.ceil(yMax.value * .25), 0])
const xCoordinate = (index) => detectionTrend.value.length < 2 ? chartLeft + chartWidth / 2 : chartLeft + (index * chartWidth) / (detectionTrend.value.length - 1)
const yCoordinate = (value) => chartTop + chartHeight - (value / yMax.value) * chartHeight
const toPoints = (key) => detectionTrend.value.map((item, index) => ({ ...item, x: xCoordinate(index), y: yCoordinate(item[key]) }))
const createPath = (points) => points.map((point, index) => `${index === 0 ? 'M' : 'L'} ${point.x} ${point.y}`).join(' ')
const detectionPoints = computed(() => toPoints('detections'))
const abnormalPoints = computed(() => toPoints('abnormalImages'))
const detectionPath = computed(() => createPath(detectionPoints.value))
const abnormalPath = computed(() => createPath(abnormalPoints.value))
const detectionAreaPath = computed(() => detectionPoints.value.length ? `${detectionPath.value} L ${detectionPoints.value[detectionPoints.value.length - 1].x} 200 L ${detectionPoints.value[0].x} 200 Z` : '')
const riskItems = computed(() => [
  { key: 'high', label: '高风险', value: distribution.value.high }, { key: 'medium', label: '中风险', value: distribution.value.medium }, { key: 'low', label: '低风险', value: distribution.value.low },
])
const riskTotal = computed(() => riskItems.value.reduce((sum, item) => sum + item.value, 0))
const donutGradient = computed(() => {
  if (!riskTotal.value) return 'conic-gradient(#e5e7eb 0deg 360deg)'
  const highEnd = (distribution.value.high / riskTotal.value) * 360
  const mediumEnd = highEnd + (distribution.value.medium / riskTotal.value) * 360
  return `conic-gradient(#ef4444 0deg ${highEnd}deg, #f59e0b ${highEnd}deg ${mediumEnd}deg, #10b981 ${mediumEnd}deg 360deg)`
})
const metricCards = computed(() => [
  { key: 'totalImages', label: '累计处理影像', value: metrics.value.totalImages, icon: Picture, tone: 'blue' },
  { key: 'affectedCount', label: '累计面签影像', value: metrics.value.affectedCount, icon: UserFilled, tone: 'indigo' },
  { key: 'abnormalImages', label: '疑似异常影像', value: metrics.value.abnormalImages, icon: WarningFilled, tone: 'amber' },
  { key: 'highRiskCases', label: '高风险案件', value: metrics.value.highRiskCases, icon: CircleCloseFilled, tone: 'red' },
  { key: 'todayTasks', label: '今日检测任务', value: metrics.value.todayTasks, icon: Calendar, tone: 'cyan' },
  { key: 'completedTasks', label: '完成检测任务', value: metrics.value.completedTasks, icon: Finished, tone: 'green' },
])
const tableHeaderStyle = { background: 'var(--bg-card-hover)', color: 'var(--text-secondary)', fontWeight: '600' }
const formatNumber = (value) => new Intl.NumberFormat('zh-CN').format(value)
const riskTagType = (level) => ({ 待检测: 'info', 高风险: 'danger', 中风险: 'warning', 低风险: 'success' }[level] || 'info')
const statusTagType = (status) => ({ 待检测: 'info', 检测中: 'primary', 已完成: 'success', 检测失败: 'danger' }[status] || 'info')
const openTask = (id) => router.push(`/tasks/${id}`)
const openCase = (id) => router.push(`/cases/${id}`)
const goToDetection = () => router.push('/detection')
const refreshStatistics = async () => {
  try {
    const res = await getAnalyticsStatistics('7d')
    statistics.value = res.data
  } catch {
    // Keep the last successful snapshot visible while the next poll retries.
  }
}
onMounted(() => { refreshStatistics(); statisticsTimer = window.setInterval(refreshStatistics, 5000) })
onBeforeUnmount(() => { if (statisticsTimer) clearInterval(statisticsTimer) })
</script>

<style scoped>
.dashboard-page{max-width:1440px;margin:0 auto}.page-heading{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;margin:4px 0 20px}.page-heading h2{margin:0 0 7px;font-size:24px;color:var(--text-primary)}.page-heading p{color:var(--text-secondary);font-size:14px}.dashboard-overview{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(430px,.95fr);gap:20px;margin-bottom:20px}.detection-entry-card,.overview-card{overflow:hidden;border-color:var(--border-color);border-radius:var(--radius-md)}.detection-entry-card{background:var(--bg-card);border:1px solid var(--border-color)}.detection-entry-card :deep(.el-card__body){position:relative;display:flex;align-items:center;min-height:238px;padding:30px 36px}.entry-copy{position:relative;z-index:1;max-width:470px}.entry-eyebrow{margin:0 0 12px;color:var(--text-muted);font-size:11px;font-weight:700;letter-spacing:1.2px}.entry-copy h3{margin:0 0 10px;color:var(--text-primary);font-size:25px;line-height:1.2;background:none;-webkit-text-fill-color:currentColor}.entry-copy>p:not(.entry-eyebrow){margin:0;color:var(--text-secondary);font-size:14px;line-height:1.7}.entry-button{height:44px;margin-top:22px;padding:0 19px;border:1px solid var(--accent)!important;border-radius:6px;background:var(--accent)!important;box-shadow:none!important;color:#fff!important;font-weight:600;animation:none!important}.entry-button:hover{background:#2563eb!important;transform:translateY(-1px)}.entry-support{display:block;margin-top:14px;color:var(--text-muted);font-size:12px}.entry-visual{position:absolute;right:56px;top:50%;display:grid;place-items:center;width:116px;height:116px;transform:translateY(-50%);border:1px solid #d7e0e7;border-radius:50%;background:#fafcfd}.entry-visual::before{position:absolute;inset:13px;border:1px solid #e5ebef;border-radius:50%;content:""}.entry-orbit{position:relative;z-index:1;display:grid;place-items:center;width:54px;height:54px;color:var(--text-secondary);border-radius:50%;background:#f0f3f5}.overview-card{background:var(--bg-card)}.overview-card :deep(.el-card__header){padding:17px 22px 14px;border-bottom:1px solid var(--border-light)}.overview-card :deep(.el-card__body){padding:2px 22px 14px}.panel-header{display:flex;align-items:center;justify-content:space-between;gap:12px;font-size:16px;font-weight:600;color:var(--text-primary)}.panel-header .el-tag{gap:4px}.overview-metrics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr))}.overview-metric{display:flex;align-items:center;gap:10px;min-width:0;padding:16px 8px}.overview-metric:nth-child(n+4){border-top:1px solid var(--border-light)}.metric-icon{display:grid;flex:0 0 auto;place-items:center;width:38px;height:38px;border-radius:8px}.metric-icon.blue{color:#2563eb;background:#eff6ff}.metric-icon.indigo{color:#6366f1;background:#eef2ff}.metric-icon.amber{color:#d97706;background:#fffbeb}.metric-icon.red{color:#dc2626;background:#fef2f2}.metric-icon.cyan{color:#0891b2;background:#ecfeff}.metric-icon.green{color:#059669;background:#ecfdf5}.overview-metric p{overflow:hidden;margin:0 0 5px;color:var(--text-muted);font-size:12px;text-overflow:ellipsis;white-space:nowrap}.overview-metric strong{display:block;color:var(--text-primary);font-size:22px;line-height:1}.chart-grid{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(340px,.9fr);gap:20px;margin-bottom:20px}.lower-grid{margin-bottom:20px}.panel-card{border-color:var(--border-color);border-radius:var(--radius-md);background:var(--bg-card)}.chart-legend{display:flex;align-items:center;gap:7px;color:var(--text-muted);font-size:12px;font-weight:400}.chart-legend i,.legend-dot{display:inline-block;width:8px;height:8px;border-radius:50%}.detection-dot{background:#6366f1}.abnormal-dot{background:#ef4444}.trend-chart{width:100%;height:260px;overflow:visible}.chart-grid-lines line{stroke:var(--border-light);stroke-width:1}.axis-labels,.x-label{fill:var(--text-muted);font-size:11px}.detection-area{fill:rgba(99,102,241,.10)}.detection-line,.abnormal-line{fill:none;stroke-width:3}.detection-line{stroke:#6366f1}.abnormal-line{stroke:#ef4444;stroke-dasharray:5 4}.detection-point{fill:#fff;stroke:#6366f1;stroke-width:3}.abnormal-point{fill:#fff;stroke:#ef4444;stroke-width:3}.risk-content{display:flex;align-items:center;justify-content:center;gap:32px;min-height:260px}.donut{display:grid;place-items:center;width:166px;height:166px;border-radius:50%}.donut-center{display:flex;flex-direction:column;align-items:center;justify-content:center;width:112px;height:112px;border-radius:50%;background:var(--bg-card)}.donut-center strong{font-size:28px;color:var(--text-primary)}.donut-center span{margin-top:4px;font-size:12px;color:var(--text-muted)}.risk-legend{display:flex;flex-direction:column;gap:16px}.risk-legend>div{display:grid;grid-template-columns:10px 54px auto;align-items:center;gap:8px;font-size:13px;color:var(--text-secondary)}.risk-legend strong{color:var(--text-primary)}.legend-dot.high{background:#ef4444}.legend-dot.medium{background:#f59e0b}.legend-dot.low{background:#10b981}.tasks-table{width:100%}.tasks-table :deep(.el-table),.tasks-table :deep(.el-table tr),.tasks-table :deep(.el-table th.el-table__cell){background:transparent;color:var(--text-primary)}.tasks-table :deep(.el-table__inner-wrapper::before){display:none}.lower-grid{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(340px,.9fr);gap:20px}.case-list{display:flex;flex-direction:column}.case-row{display:grid;grid-template-columns:minmax(155px,1fr) auto auto;align-items:center;gap:14px;padding:14px 0;border-bottom:1px solid var(--border-light)}.case-row:first-child{padding-top:0}.case-row:last-child{padding-bottom:0;border-bottom:0}.case-row strong{font-size:13px;color:var(--text-primary)}.case-row p{margin-top:5px;font-size:12px;color:var(--text-muted)}.case-risk{display:flex;flex-direction:column;align-items:flex-end;gap:6px;font-size:12px;color:var(--text-secondary);white-space:nowrap}@media(max-width:1100px){.dashboard-overview,.chart-grid,.lower-grid{grid-template-columns:1fr}.overview-metrics{grid-template-columns:repeat(3,minmax(0,1fr))}.risk-panel{min-height:340px}}@media(max-width:700px){.page-heading{flex-direction:column}.detection-entry-card :deep(.el-card__body){min-height:0;padding:28px 24px}.entry-visual{display:none}.overview-metrics{grid-template-columns:repeat(2,minmax(0,1fr))}.overview-metric:nth-child(n+4){border-top:0}.overview-metric:nth-child(n+3){border-top:1px solid var(--border-light)}.chart-legend{display:none}.case-row{grid-template-columns:1fr auto}.case-row>button{grid-column:1/-1;justify-self:start}}@media(max-width:430px){.overview-metrics{grid-template-columns:1fr}.overview-metric:nth-child(n+2){border-top:1px solid var(--border-light)}}
</style>
