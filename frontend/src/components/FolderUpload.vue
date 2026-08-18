<template>
  <div class="upload-section">
    <el-card class="upload-card" shadow="never">
      <template #header>
        <div class="card-header">
          <el-icon :size="22" color="var(--accent)"><FolderAdd /></el-icon>
          <span>上传影像文件夹</span>
        </div>
      </template>

      <!-- 拖拽上传区 -->
      <el-upload
        ref="uploadRef"
        class="upload-area"
        drag
        multiple
        :auto-upload="false"
        :show-file-list="false"
        :on-change="onFileChange"
        :directory="true"
        accept="image/*"
      >
        <div class="upload-placeholder" v-if="selectedFiles.length === 0">
          <el-icon :size="64" color="var(--text-muted)"><UploadFilled /></el-icon>
          <div class="upload-text">
            <p class="upload-title">点击或拖拽文件夹到此区域</p>
            <p class="upload-hint">支持选择整个文件夹，系统将按照子目录结构进行解析</p>
            <p class="upload-hint">每个子目录应包含：面签合影照、身份证正反面、银行流水、合同文档</p>
          </div>
        </div>
        <div class="upload-placeholder has-files" v-else>
          <el-icon :size="48" color="#67c23a"><CircleCheckFilled /></el-icon>
          <div class="upload-text">
            <p class="upload-title success">
              已选择 <strong>{{ selectedFiles.length }}</strong> 个文件
            </p>
            <p class="upload-hint">
              共 <strong>{{ subdirCount }}</strong> 个贷款目录，包含
              <strong>{{ imageCount }}</strong> 张图片
            </p>
          </div>
        </div>
      </el-upload>

      <div class="upload-actions">
        <el-button
          type="primary"
          size="large"
          :loading="uploading"
          :disabled="selectedFiles.length === 0"
          @click="handleUpload"
          class="upload-btn btn-breathe"
        >
          <el-icon><Upload /></el-icon>
          上传文件夹
        </el-button>
        <el-button type="primary" size="large" class="upload-btn btn-breathe" @click="resetUpload" :disabled="selectedFiles.length === 0">
          重置
        </el-button>
      </div>

      <!-- 上传进度 -->
      <div class="upload-progress" v-if="uploading">
        <el-progress
          :percentage="uploadProgress"
          :status="uploadProgress === 100 ? 'success' : ''"
          :stroke-width="8"
        />
        <p>{{ uploadStatusText }}</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { FolderAdd, UploadFilled, CircleCheckFilled, Folder, Upload } from '@element-plus/icons-vue'
import { uploadFolder } from '../api'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const emit = defineEmits(['upload-success'])

const uploadRef = ref(null)
const selectedFiles = ref([])
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadStatusText = ref('')

const subdirs = computed(() => {
  const dirs = new Set()
  selectedFiles.value.forEach(f => {
    const path = f.webkitRelativePath || f.raw?.webkitRelativePath || f.name
    const parts = path.replace(/\\/g, '/').split('/')
    if (parts.length > 1) dirs.add(parts[0])
  })
  return [...dirs].sort()
})

const subdirCount = computed(() => subdirs.value.length)
const imageCount = computed(() => {
  return selectedFiles.value.filter(f => {
    const name = (f.webkitRelativePath || f.raw?.webkitRelativePath || f.name).toLowerCase()
    return name.match(/\.(jpg|jpeg|png|bmp|gif|webp)$/)
  }).length
})

const onFileChange = (file, fileList) => {
  selectedFiles.value = [...fileList]
}

const handleUpload = async () => {
  if (selectedFiles.value.length === 0) {
    ElMessage.warning('请先选择文件夹')
    return
  }

  uploading.value = true
  const totalFiles = selectedFiles.value.length
  const firstPath = selectedFiles.value[0]?.webkitRelativePath || selectedFiles.value[0]?.raw?.webkitRelativePath || ''
  const folderName = firstPath ? firstPath.replace(/\\/g, '/').split('/')[0] : ''

  if (!folderName) {
    uploading.value = false
    ElMessage.error('无法识别上传文件夹名称，请重新选择文件夹')
    return
  }

  // 阶段1: 准备文件 (0-20%)
  uploadProgress.value = 5
  uploadStatusText.value = `正在准备 ${totalFiles} 个文件...`

  const formData = new FormData()
  selectedFiles.value.forEach((file, i) => {
    const path = file.webkitRelativePath || file.raw?.webkitRelativePath || file.name
    formData.append('files', file.raw, path)
  })
  formData.append('folder_name', folderName)

  await new Promise(r => setTimeout(r, 200))
  uploadProgress.value = 15
  uploadStatusText.value = `文件准备完成，开始上传 ${totalFiles} 个文件...`

  try {
    const uploadApi = axios.create({ baseURL: '/api', timeout: 600000 })
    uploadApi.interceptors.request.use(config => {
      const user = JSON.parse(localStorage.getItem('user') || '{}')
      if (user.token) config.headers.Authorization = `Bearer ${user.token}`
      const sessionId = localStorage.getItem('session_id')
      if (sessionId) config.headers['X-Session-Id'] = sessionId
      return config
    })

    // 阶段2: 实际上传 (15-80%)
    const res = await uploadApi.post('/upload/folder', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          const pct = 15 + Math.round((progressEvent.loaded / progressEvent.total) * 65)
          uploadProgress.value = pct
          uploadStatusText.value = `正在上传 ${totalFiles} 个文件... ${Math.round((progressEvent.loaded / progressEvent.total) * 100)}%`
        }
      },
    })

    // 阶段3: 后端处理中 (80-100%)
    uploadProgress.value = 85
    uploadStatusText.value = '正在处理文件结构...'
    await new Promise(r => setTimeout(r, 300))

    const data = res.data
    uploadProgress.value = 100
    uploadStatusText.value = `上传完成！共 ${totalFiles} 个文件`

    ElMessage.success(data.message || '上传成功')
    localStorage.setItem('session_id', data.data.session_id)

    setTimeout(() => {
      emit('upload-success', {
        ...data.data,
        folder_name: folderName || '已上传影像文件夹',
        selected_file_count: totalFiles,
      })
    }, 500)
  } catch (e) {
    const serverMessage = e.response?.data?.message
    ElMessage.error(serverMessage || ('上传失败：' + (e.message || '未知错误')))
    uploadProgress.value = 0
  } finally {
    uploading.value = false
  }
}

const resetUpload = () => {
  selectedFiles.value = []
  uploadProgress.value = 0
  uploadStatusText.value = ''
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}
</script>

<style scoped>
.upload-section {
  margin-bottom: 20px;
}

.upload-card {
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

.upload-area {
  width: 100%;
}

.upload-area :deep(.el-upload) {
  width: 100%;
}

.upload-area :deep(.el-upload-dragger) {
  width: 100%;
  min-height: 220px;
  border: 2px dashed var(--border-color);
  border-radius: var(--radius-md);
  background: var(--bg-card-hover);
  transition: all 0.3s;
}

.upload-area :deep(.el-upload-dragger:hover) {
  border-color: var(--accent);
  background: var(--accent-light);
}

.upload-placeholder {
  padding: 40px 20px;
  text-align: center;
}

.upload-placeholder.has-files {
  padding: 30px 20px;
}

.upload-title {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-top: 12px;
  transition: color 0.3s ease;
}

.upload-title.success {
  color: #67c23a;
}

.upload-hint {
  font-size: 13px;
  color: var(--text-muted);
  margin-top: 6px;
  line-height: 1.6;
  transition: color 0.3s ease;
}

.file-preview {
  margin-top: 20px;
  padding: 16px;
  background: var(--bg-card-hover);
  border-radius: var(--radius-sm);
  transition: background-color 0.3s ease;
}

.file-preview h3 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 10px;
  transition: color 0.3s ease;
}

.subdir-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.upload-actions {
  margin-top: 20px;
  display: flex;
  gap: 12px;
  justify-content: center;
}

.upload-btn {
  min-width: 160px;
  height: 48px;
  font-size: 15px;
  font-weight: 600;
}

.upload-progress {
  margin-top: 20px;
  text-align: center;
}

.upload-progress p {
  margin-top: 10px;
  font-size: 13px;
  color: var(--text-secondary);
  transition: color 0.3s ease;
}
</style>
