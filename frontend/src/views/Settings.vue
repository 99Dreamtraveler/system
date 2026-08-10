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

    <el-card shadow="never" class="model-card">
      <template #header><div class="card-title"><el-icon><Cpu /></el-icon>模型信息</div></template>
      <el-table :data="models" size="default" :header-cell-style="tableHeaderStyle">
        <el-table-column prop="name" label="模型组件" min-width="160" />
        <el-table-column prop="purpose" label="用途" min-width="260" />
        <el-table-column prop="source" label="模型来源" min-width="200" />
        <el-table-column label="状态" width="120"><template #default><el-tag type="success" size="small">本地配置</el-tag></template></el-table-column>
      </el-table>
      <p class="model-note">模型由现有后端程序加载；本页不提供模型管理、上传、选择或训练操作。</p>
    </el-card>

    <el-card shadow="never" class="log-card">
      <template #header><div class="card-title"><el-icon><List /></el-icon>操作日志 <el-tag size="small" type="info" effect="plain">前端演示数据</el-tag></div></template>
      <el-timeline>
        <el-timeline-item v-for="log in operationLogsMock" :key="log.id" :type="log.type" :timestamp="log.occurredAt" placement="top">
          <strong>{{ log.action }}</strong><p>{{ log.detail }}</p>
        </el-timeline-item>
      </el-timeline>
    </el-card>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { CircleCheckFilled, Cpu, List, Monitor, UserFilled } from '@element-plus/icons-vue'
import { operationLogsMock } from '../mock/settings'

const readCurrentUser = () => {
  try { return JSON.parse(localStorage.getItem('user') || '{}') } catch { return {} }
}
const currentUser = readCurrentUser()
const user = computed(() => ({
  username: currentUser.username || 'anonymous',
  role: currentUser.role || '待确认',
  loginTime: currentUser.loginTime || currentUser.loginAt || '当前代码未记录',
}))

const models = [
  { name: 'YOLO26n', purpose: '面签照片人物筛选', source: '本地模型权重' },
  { name: 'CLIP + LoRA + Projection', purpose: '面签照片特征提取与相似度计算', source: '本地训练权重' },
]
const tableHeaderStyle = { background: 'var(--bg-card-hover)', color: 'var(--text-secondary)', fontWeight: 600 }
</script>

<style scoped>
.settings-page{max-width:1400px;margin:0 auto}.page-heading{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;margin:4px 0 20px}.page-heading h2{margin:0 0 7px;color:var(--text-primary);font-size:24px}.page-heading p{margin:0;color:var(--text-secondary);font-size:14px}.page-heading .el-tag{display:flex;gap:6px;align-items:center}.info-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px;margin-bottom:20px}.info-card,.model-card,.log-card{border-color:var(--border-color);border-radius:var(--radius-md);background:var(--bg-card)}.model-card{margin-bottom:20px}.card-title{display:flex;align-items:center;gap:8px;color:var(--text-primary);font-size:16px;font-weight:600}.card-title .el-icon{color:var(--accent)}.card-title .el-tag{margin-left:4px;font-weight:400}.model-note{margin:14px 0 0;color:var(--text-muted);font-size:13px}.log-card :deep(.el-timeline-item__timestamp){color:var(--text-muted);font-size:12px}.log-card strong{color:var(--text-primary);font-size:14px}.log-card p{margin:6px 0 0;color:var(--text-secondary);font-size:13px}@media(max-width:850px){.info-grid{grid-template-columns:1fr}.page-heading{flex-direction:column}.model-card :deep(.el-table){overflow-x:auto}}@media(max-width:560px){.settings-page{min-width:0}.page-heading .el-tag{max-width:100%}.info-card :deep(.el-descriptions__label){width:88px}}
</style>
