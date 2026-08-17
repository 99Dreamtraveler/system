<template>
  <section class="settings-page">
    <header class="page-heading">
      <div><h2>系统管理</h2><p>查看当前用户、系统运行信息和操作记录。</p></div>
      <el-tag type="success" effect="light" size="large"><el-icon><CircleCheckFilled /></el-icon>系统运行正常</el-tag>
    </header>

    <section class="info-grid">
      <el-card shadow="never" class="info-card">
        <template #header><div class="card-title"><el-icon><UserFilled /></el-icon>用户信息</div></template>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="用户名">{{ user.username }}</el-descriptions-item>
          <el-descriptions-item label="角色">{{ user.role }}</el-descriptions-item>
          <el-descriptions-item label="登录时间">{{ user.loginTime }}</el-descriptions-item>
        </el-descriptions>
      </el-card>
      <el-card shadow="never" class="info-card">
        <template #header><div class="card-title"><el-icon><Monitor /></el-icon>系统信息</div></template>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="系统名称">金融影像智能相似度检测系统</el-descriptions-item>
          <el-descriptions-item label="系统版本">v1.0.0</el-descriptions-item>
          <el-descriptions-item label="运行状态"><el-tag type="success" size="small">正常</el-tag></el-descriptions-item>
        </el-descriptions>
      </el-card>
    </section>

    <el-card shadow="never" class="log-card">
      <template #header><div class="card-title"><el-icon><List /></el-icon>操作日志</div></template>
      <div v-if="logsLoading" class="log-loading"><el-skeleton :rows="4" animated /></div>
      <div v-else-if="logsError" class="log-state"><el-alert title="操作日志加载失败，请稍后重试。" type="error" :closable="false" show-icon /><el-button type="primary" @click="loadLogs">重新加载</el-button></div>
      <el-timeline v-else-if="operationLogs.length">
        <el-timeline-item v-for="log in operationLogs" :key="log.id" :type="log.type" :timestamp="log.occurredAt" placement="top">
          <div class="log-entry"><strong>{{ log.action }}</strong><span class="log-user">操作用户：{{ log.username || 'anonymous' }}</span></div><p>{{ log.detail }}</p>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description="暂无操作日志" :image-size="70" />
      <div v-if="logTotal > logPageSize" class="log-pagination"><el-pagination v-model:current-page="logPage" :page-size="logPageSize" layout="prev, pager, next" :total="logTotal" @current-change="loadLogs" /></div>
    </el-card>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { CircleCheckFilled, List, Monitor, UserFilled } from '@element-plus/icons-vue'
import { getOperationLogs } from '../api/operationLogs'

const readCurrentUser = () => {
  try { return JSON.parse(localStorage.getItem('user') || '{}') } catch { return {} }
}
const currentUser = readCurrentUser()
const user = computed(() => ({
  username: currentUser.username || 'anonymous',
  role: '业务员',
  loginTime: currentUser.loginTime || '尚未登录',
}))

const operationLogs = ref([])
const logTotal = ref(0)
const logPage = ref(1)
const logPageSize = 10
const logsLoading = ref(false)
const logsError = ref(false)
const loadLogs = async () => {
  logsLoading.value = true
  logsError.value = false
  try {
    const res = await getOperationLogs({ page: logPage.value, pageSize: logPageSize })
    operationLogs.value = res.data.records || []
    logTotal.value = res.data.total || 0
  } catch {
    operationLogs.value = []
    logTotal.value = 0
    logsError.value = true
  } finally {
    logsLoading.value = false
  }
}
onMounted(loadLogs)
</script>

<style scoped>
.settings-page{max-width:1400px;margin:0 auto}.page-heading{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;margin:4px 0 20px}.page-heading h2{margin:0 0 7px;color:var(--text-primary);font-size:24px}.page-heading p{margin:0;color:var(--text-secondary);font-size:14px}.page-heading .el-tag{display:flex;gap:6px;align-items:center}.info-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px;margin-bottom:20px}.info-card,.log-card{border-color:var(--border-color);border-radius:var(--radius-md);background:var(--bg-card)}.card-title{display:flex;align-items:center;gap:8px;color:var(--text-primary);font-size:16px;font-weight:600}.card-title .el-icon{color:var(--accent)}.log-card :deep(.el-timeline-item__timestamp){color:var(--text-muted);font-size:12px}.log-card strong{color:var(--text-primary);font-size:14px}.log-card p{margin:6px 0 0;color:var(--text-secondary);font-size:13px}.log-loading{padding:8px 0}.log-state{display:flex;align-items:center;gap:16px}.log-state .el-alert{flex:1}.log-pagination{display:flex;justify-content:flex-end;margin-top:16px}@media(max-width:850px){.info-grid{grid-template-columns:1fr}.page-heading{flex-direction:column}}@media(max-width:560px){.settings-page{min-width:0}.page-heading .el-tag{max-width:100%}.info-card :deep(.el-descriptions__label){width:88px}.log-state{align-items:stretch;flex-direction:column}}
.log-entry{display:flex;align-items:center;gap:10px;flex-wrap:wrap}.log-user{color:var(--text-secondary);font-size:13px}
</style>
