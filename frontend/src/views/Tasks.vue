<template>
  <section class="tasks-page">
    <header class="page-heading"><div><h2>检测任务</h2><p>查看历史影像检测任务及检测结果。</p></div><el-tag v-if="isMock" type="info" effect="plain">MOCK · 后端无数据时展示</el-tag></header>

    <el-card class="filter-card" shadow="never">
      <el-form :model="filters" class="task-filter" @submit.prevent="queryTasks">
        <el-form-item label="任务编号"><el-input v-model="filters.taskId" clearable placeholder="请输入任务编号" /></el-form-item>
        <el-form-item label="日期范围"><el-date-picker v-model="filters.dateRange" type="daterange" value-format="YYYY-MM-DD" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" /></el-form-item>
        <el-form-item label="任务状态"><el-select v-model="filters.status" clearable placeholder="全部"><el-option v-for="item in statusOptions" :key="item" :label="item" :value="item" /></el-select></el-form-item>
        <el-form-item label="风险等级"><el-select v-model="filters.riskLevel" clearable placeholder="全部"><el-option v-for="item in riskOptions" :key="item" :label="item" :value="item" /></el-select></el-form-item>
        <div class="filter-actions"><el-button type="primary" native-type="submit" :loading="loading"><el-icon><Search /></el-icon>查询</el-button><el-button @click="resetFilters">重置</el-button></div>
      </el-form>
    </el-card>

    <el-card class="table-card" shadow="never">
      <template #header><div class="table-title"><span>任务列表</span><span class="table-count">共 {{ filteredTasks.length }} 条</span></div></template>
      <div v-if="error" class="state-panel"><el-alert title="检测任务加载失败，请稍后重试。" type="error" :closable="false" show-icon /><el-button type="primary" @click="queryTasks">重新加载</el-button></div>
      <el-table v-else-if="filteredTasks.length || loading" v-loading="loading" :data="pageTasks" class="tasks-table" :header-cell-style="tableHeaderStyle">
        <el-table-column prop="taskId" label="任务编号" min-width="190" />
        <el-table-column prop="createdAt" label="创建时间" min-width="165" />
        <el-table-column label="相似度" min-width="115"><template #default="{ row }">{{ formatSimilarity(row.similarity) }}</template></el-table-column>
        <el-table-column label="风险等级" min-width="110"><template #default="{ row }"><el-tag :type="riskTagType(row.riskLevel)" effect="light">{{ row.riskLevel }}</el-tag></template></el-table-column>
        <el-table-column label="状态" min-width="110"><template #default="{ row }"><el-tag :type="statusTagType(row.status)" effect="light">{{ row.status }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="160" fixed="right"><template #default="{ row }"><el-button link type="primary" @click="openDetail(row.taskId)">查看详情</el-button><el-button link type="primary" @click="retryTask">重新检测</el-button></template></el-table-column>
      </el-table>
      <el-empty v-else description="暂无检测任务"><el-button type="primary" @click="resetFilters">重置筛选</el-button></el-empty>
      <div v-if="filteredTasks.length > pageSize" class="pagination"><el-pagination v-model:current-page="currentPage" :page-size="pageSize" layout="prev, pager, next" :total="filteredTasks.length" /></div>
    </el-card>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { getDetectionTasks } from '../api/tasks'

const router = useRouter()
const filters = reactive({ taskId: '', dateRange: [], status: '', riskLevel: '' })
const statusOptions = ['检测中', '已完成', '检测失败']
const riskOptions = ['高风险', '中风险', '低风险']
const loading = ref(false)
const isMock = ref(false)
const error = ref(false)
const filteredTasks = ref([])
const currentPage = ref(1)
const pageSize = 5
const pageTasks = computed(() => filteredTasks.value.slice((currentPage.value - 1) * pageSize, currentPage.value * pageSize))
const tableHeaderStyle = { background: 'var(--bg-card-hover)', color: 'var(--text-secondary)', fontWeight: 600 }
const formatSimilarity = (value) => (typeof value === 'number' ? `${value.toFixed(2)}%` : '--')
const riskTagType = (level) => ({ 高风险: 'danger', 中风险: 'warning', 低风险: 'success' }[level] || 'info')
const statusTagType = (status) => ({ 检测中: 'primary', 已完成: 'success', 检测失败: 'danger' }[status] || 'info')
const queryTasks = async () => { loading.value = true; error.value = false; currentPage.value = 1; try { const res = await getDetectionTasks(filters); filteredTasks.value = res.data.records || []; isMock.value = Boolean(res.mock) } catch { error.value = true; filteredTasks.value = [] } finally { loading.value = false } }
const resetFilters = () => { filters.taskId = ''; filters.dateRange = []; filters.status = ''; filters.riskLevel = ''; queryTasks() }
const openDetail = (taskId) => router.push(`/tasks/${taskId}`)
const retryTask = async () => { try { await ElMessageBox.confirm('将返回智能影像检测页面重新提交检测任务。', '重新检测', { confirmButtonText: '前往检测', cancelButtonText: '取消', type: 'warning' }); router.push('/detection') } catch {} }
onMounted(queryTasks)
</script>

<style scoped>
.tasks-page{max-width:1400px;margin:0 auto}.page-heading{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;margin:4px 0 20px}.page-heading h2{margin:0 0 7px;color:var(--text-primary);font-size:24px}.page-heading p{color:var(--text-secondary);font-size:14px}.filter-card,.table-card{margin-bottom:20px;border-color:var(--border-color);border-radius:var(--radius-md);background:var(--bg-card)}.task-filter{display:flex;align-items:flex-end;flex-wrap:wrap;gap:0 16px}.task-filter :deep(.el-form-item){margin-bottom:0}.task-filter :deep(.el-input){width:210px}.task-filter :deep(.el-date-editor){width:280px}.task-filter :deep(.el-select){width:140px}.filter-actions{display:flex;gap:10px;padding-bottom:0}.table-title{display:flex;align-items:center;justify-content:space-between;font-size:16px;font-weight:600;color:var(--text-primary)}.table-count{font-size:13px;font-weight:400;color:var(--text-muted)}.tasks-table{width:100%}.state-panel{display:flex;align-items:center;gap:16px}.state-panel .el-alert{flex:1}.pagination{display:flex;justify-content:flex-end;margin-top:18px}@media(max-width:900px){.task-filter{align-items:stretch}.task-filter :deep(.el-input),.task-filter :deep(.el-date-editor),.task-filter :deep(.el-select){width:100%}.task-filter :deep(.el-form-item){width:calc(50% - 8px)}.filter-actions{width:100%;padding-top:4px}}@media(max-width:620px){.page-heading{flex-direction:column}.task-filter :deep(.el-form-item){width:100%}.filter-actions .el-button{flex:1}.state-panel{align-items:stretch;flex-direction:column}}
</style>
