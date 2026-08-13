<template>
  <div class="loan-section">
    <el-card class="loan-card" shadow="never">
      <template #header>
        <div class="card-header">
          <el-icon :size="22" color="var(--accent)"><Grid /></el-icon>
          <span>贷款记录管理</span>
          <el-tag v-if="totalRecords > 0" type="info" effect="plain">{{ totalRecords }} 条记录</el-tag>
        </div>
      </template>

      <!-- 加载中 -->
      <div class="loading-area" v-if="loading">
        <el-icon :size="48" class="loading-icon"><Loading /></el-icon>
        <p>正在扫描贷款目录...</p>
      </div>

      <!-- 空状态 -->
      <div class="empty-area" v-else-if="!scanned && !loading">
        <div class="action-hint">
          <el-icon :size="48" color="var(--accent)"><FolderOpened /></el-icon>
          <p>上传文件夹已完成，点击下方按钮扫描贷款记录</p>
          <p class="sub-hint">系统将扫描文件夹中 loan 开头的子目录，每个目录作为一条贷款记录</p>
        </div>
        <el-button type="primary" size="large" @click="doScan" class="scan-btn btn-breathe">
          <el-icon><MagicStick /></el-icon>
          智能分类
        </el-button>
      </div>

      <!-- 记录表格 -->
      <div class="results-area" v-if="scanned && !loading">
        <div class="table-toolbar">
          <el-button type="primary" @click="showAddDialog = true">
            <el-icon><Plus /></el-icon>新增记录
          </el-button>
          <el-button type="primary" plain @click="doScan">
            <el-icon><Refresh /></el-icon>重新扫描
          </el-button>
        </div>

        <el-table :data="records" stripe border style="width: 100%" max-height="600" row-key="loan_id">
          <el-table-column label="贷款编号" width="100" sortable fixed="left">
            <template #default="{ row }">{{ formatLoanId(row.loan_id) }}</template>
          </el-table-column>
          <el-table-column v-for="col in columns" :key="col.key" :label="col.label" min-width="160" align="center">
            <template #default="{ row }">
              <div class="cell-thumb-wrap">
                <el-image
                  v-if="row.fields[col.key]?.exists"
                  :src="getImageUrl(row.fields[col.key].file_path)"
                  fit="cover"
                  class="cell-thumb"
                  :preview-src-list="[getImageUrl(row.fields[col.key].file_path)]"
                  :preview-teleported="true"
                >
                  <template #error>
                    <div class="cell-error"><el-icon :size="20"><PictureFilled /></el-icon></div>
                  </template>
                </el-image>
                <div v-else class="cell-missing">
                  <el-icon :size="20"><PictureFilled /></el-icon>
                  <span>缺失</span>
                </div>
                <el-upload
                  class="cell-upload-overlay"
                  :auto-upload="false"
                  :show-file-list="false"
                  accept="image/*"
                  :on-change="(file) => handleFieldUpload(row.loan_id, col.key, file)"
                >
                  <div class="cell-upload-mask">
                    <el-icon :size="14"><Upload /></el-icon>
                    <span>替换</span>
                  </div>
                </el-upload>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right" align="center">
            <template #default="{ row }">
              <el-popconfirm
                title="确定删除该贷款记录及其所有文件？"
                confirm-button-text="确认删除"
                cancel-button-text="取消"
                @confirm="handleDelete(row.loan_id)"
              >
                <template #reference>
                  <el-button type="danger" size="small" text :icon="Delete">删除</el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>

        <div class="result-actions">
          <el-button @click="goBack" size="large">
            <el-icon><ArrowLeft /></el-icon>
            返回上传
          </el-button>
          <el-button type="warning" size="large" :loading="detecting" :disabled="detecting" @click="goToDetection" class="btn-breathe-warning">
            <el-icon><Search /></el-icon>
            {{ detecting ? '检测中...' : '检测' }}
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 新增记录弹窗 -->
    <el-dialog v-model="showAddDialog" title="新增贷款记录" width="520px" destroy-on-close>
      <el-form :model="addForm" label-width="100px" label-position="left">
        <el-form-item label="贷款编号" required>
          <el-input v-model="addForm.loan_id" placeholder="如: loan_075" />
        </el-form-item>
        <el-form-item label="上传文件">
          <el-upload
            ref="addUploadRef"
            multiple
            drag
            :auto-upload="false"
            :show-file-list="true"
            accept="image/*"
            :on-change="onAddFilesChange"
          >
            <div class="upload-placeholder-mini">
              <el-icon :size="28"><UploadFilled /></el-icon>
              <p>点击或拖拽图片文件</p>
            </div>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAddRecord">确定新增</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  Grid, MagicStick, Plus, Refresh, Delete, ArrowLeft, Search,
  Loading, FolderOpened, UploadFilled, PictureFilled, Upload,
} from '@element-plus/icons-vue'
import { scanRecords, createRecord, deleteRecord, uploadRecordField, getFileUrl } from '../api'
import { ElMessage } from 'element-plus'

const props = defineProps({
  sessionId: { type: String, required: true },
  autoStart: { type: Boolean, default: false },
})

const emit = defineEmits(['go-back', 'detect-start', 'detect-success', 'detect-failed'])

const loading = ref(false)
const scanned = ref(false)
const detecting = ref(false)
const records = ref([])
const showAddDialog = ref(false)
const addForm = ref({ loan_id: '' })
const addFiles = ref([])

const columns = [
  { key: 'bank_statement', label: '银行流水' },
  { key: 'contract', label: '合同' },
  { key: 'face_signing', label: '面签照' },
  { key: 'id_card_back', label: '身份证背面' },
  { key: 'id_card_front', label: '身份证正面' },
]

const totalRecords = computed(() => records.value.length)

const formatLoanId = (loanId) => {
  return parseInt(loanId.replace(/^loan_?/i, ''), 10) || loanId
}

const getImageUrl = (filePath) => {
  return getFileUrl(props.sessionId, filePath)
}

const doScan = async () => {
  loading.value = true
  try {
    const res = await scanRecords(props.sessionId)
    records.value = res.data.records || []
    scanned.value = true
    ElMessage.success(res.message || '扫描完成')
  } catch (e) {
    ElMessage.error('扫描失败：' + (e.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const handleDelete = async (loanId) => {
  try {
    await deleteRecord(props.sessionId, loanId)
    records.value = records.value.filter(r => r.loan_id !== loanId)
    ElMessage.success(`记录 ${loanId} 已删除`)
  } catch (e) {
    ElMessage.error('删除失败：' + (e.message || '未知错误'))
  }
}

const onAddFilesChange = (file) => {
  addFiles.value.push(file)
}

const handleAddRecord = async () => {
  const loanId = addForm.value.loan_id.trim()
  if (!loanId) {
    ElMessage.warning('请输入贷款编号')
    return
  }
  if (records.value.some(r => r.loan_id === loanId)) {
    ElMessage.warning('该贷款编号已存在')
    return
  }
  try {
    const fd = new FormData()
    fd.append('loan_id', loanId)
    addFiles.value.forEach(f => {
      fd.append('files', f.raw, f.name)
    })
    await createRecord(props.sessionId, fd)
    showAddDialog.value = false
    addForm.value = { loan_id: '' }
    addFiles.value = []
    ElMessage.success(`记录 ${loanId} 创建成功`)
    await doScan() // 重新扫描以获取最新状态
  } catch (e) {
    ElMessage.error('创建失败：' + (e.message || '未知错误'))
  }
}

const handleFieldUpload = async (loanId, field, file) => {
  const fd = new FormData()
  fd.append('file', file.raw, file.name)
  try {
    const res = await uploadRecordField(props.sessionId, loanId, field, fd)
    ElMessage.success(res.message || '更新成功')
    // 更新本地记录
    const record = records.value.find(r => r.loan_id === loanId)
    if (record) {
      record.fields[field] = {
        exists: true,
        file_path: res.data.file_path,
        filename: res.data.filename,
      }
    }
  } catch (e) {
    ElMessage.error('上传失败：' + (e.message || '未知错误'))
  }
}

const goToDetection = () => {
  // 收集所有 face_signing 图片
  const faceImages = []
  for (const record of records.value) {
    const fs = record.fields.face_signing
    if (fs && fs.exists) {
      faceImages.push({
        image_id: record.loan_id,
        file_path: fs.file_path,
        loan_id: record.loan_id,
        filename: fs.filename,
      })
    }
  }
  if (faceImages.length < 2) {
    ElMessage.warning('面签照数量不足（至少需要2张）')
    return
  }
  detecting.value = true
  emit('detect-start', faceImages)
}

const goBack = () => {
  emit('go-back')
}

onMounted(() => {
  if (props.autoStart) doScan()
})
</script>

<style scoped>
.loan-section { max-width: 1400px; margin: 0 auto; }
.loan-card { border-radius: var(--radius-md); border: 1px solid var(--border-color); background: var(--bg-card); margin-bottom: 20px; }
.card-header { display: flex; align-items: center; gap: 8px; font-size: 16px; font-weight: 600; color: var(--text-primary); }

.loading-area, .empty-area { text-align: center; padding: 60px 20px; }
.loading-area p, .action-hint p { font-size: 15px; color: var(--text-secondary); margin-top: 12px; }
.loading-icon { animation: spin 1.5s linear infinite; color: var(--accent); }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.sub-hint { font-size: 13px; color: var(--text-muted); }

.scan-btn { min-width: 200px; height: 48px; font-size: 16px; font-weight: 600; margin-top: 16px; }

.table-toolbar { display: flex; gap: 10px; margin-bottom: 16px; }
.results-area { min-width: 0; }

.cell-thumb-wrap {
  position: relative; display: inline-block; width: 100px; height: 70px;
  border-radius: 6px; overflow: hidden; cursor: pointer;
}
.cell-thumb { width: 100px; height: 70px; object-fit: cover; display: block; }
.cell-error { width: 100px; height: 70px; display: flex; align-items: center; justify-content: center; background: var(--border-light); color: var(--text-muted); }
.cell-missing { width: 100px; height: 70px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px; background: var(--border-light); border-radius: 6px; color: var(--text-muted); font-size: 12px; }
.cell-upload-overlay {
  position: absolute; inset: 0; opacity: 0; transition: opacity 0.2s;
}
.cell-upload-overlay :deep(.el-upload) { display: block; width: 100%; height: 100%; }
.cell-upload-mask {
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2px;
  width: 100%; height: 100%; background: rgba(0,0,0,0.5); color: #fff; font-size: 12px; cursor: pointer;
}
.cell-thumb-wrap:hover .cell-upload-overlay { opacity: 1; }

.result-actions { margin-top: 24px; display: flex; gap: 12px; justify-content: center; }

.upload-placeholder-mini { padding: 20px; text-align: center; color: var(--text-muted); }
.upload-placeholder-mini p { font-size: 13px; margin-top: 8px; }

@media (max-width: 900px) {
  .cell-thumb-wrap, .cell-thumb, .cell-error, .cell-missing { width: 70px; height: 52px; }
}
</style>
