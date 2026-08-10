<template>
  <div class="similarity-section">
    <el-card class="similarity-card" shadow="never">
      <template #header>
        <div class="card-header">
          <el-icon :size="22" color="var(--warning)"><WarningFilled /></el-icon>
          <span>可疑交易检索 — 面签照相似度检测</span>
        </div>
      </template>

      <!-- 操作区 -->
      <div class="action-area" v-if="!searched && !loading">
        <div class="action-hint">
          <el-icon :size="48" color="var(--warning)"><Search /></el-icon>
          <p>已筛选出 <strong>{{ faceImages.length }}</strong> 张面签合影照片</p>
          <p class="sub-hint">
            系统将使用 CLIP + LoRA 多模态大模型提取图像特征，计算面签照之间的相似度，
            发现可疑的相似交易
          </p>
        </div>
        <el-button
          type="warning"
          size="large"
          @click="runSearch"
          class="search-btn btn-breathe-warning"
        >
          <el-icon><Search /></el-icon>
          开始检索
        </el-button>
      </div>

      <!-- 检索进行中 -->
      <div class="loading-area" v-if="loading">
        <div class="loading-content">
          <!-- 旋转光环动画 -->
          <div class="loading-ring">
            <svg viewBox="0 0 120 120" class="loading-ring-svg">
              <circle cx="60" cy="60" r="52" fill="none" stroke="#f59e0b"
                      stroke-width="3" stroke-linecap="round" opacity="0.3"/>
              <circle cx="60" cy="60" r="52" fill="none" stroke="#f59e0b"
                      stroke-width="3" stroke-linecap="round"
                      stroke-dasharray="80 250" class="loading-ring-arc-warn"/>
            </svg>
            <el-icon :size="36" class="loading-icon-inner" color="var(--warning)"><Connection /></el-icon>
          </div>
          <h3>正在提取特征 & 计算相似度...</h3>
          <p class="loading-hint">使用 CLIP + LoRA 多模态大模型分析 {{ faceImages.length }} 张图像，检测可疑相似交易</p>
          <div class="search-progress-wrap">
            <el-progress
              :percentage="50"
              :indeterminate="true"
              :stroke-width="6"
              :duration="2"
              :show-text="false"
              color="#f59e0b"
              class="search-progress"
            />
            <p class="loading-phase">{{ loadingPhase }}</p>
          </div>
        </div>
      </div>

      <!-- 结果区 -->
      <div class="results-area" v-if="searched && result">
        <!-- 相似组展示 -->
        <div class="groups-section" v-if="result.similar_groups.length > 0">
          <h3>
            <el-icon :size="20" color="var(--warning)"><Connection /></el-icon>
            相似组列表 — 共 {{ result.similar_groups.length }} 组
          </h3>

          <el-collapse v-model="activeGroups" accordion>
            <el-collapse-item
              v-for="group in result.similar_groups"
              :key="group.group_id"
              :name="group.group_id"
            >
              <template #title>
                <div class="group-title">
                  <el-tag type="danger" size="large">{{ group.group_id }}</el-tag>
                  <span class="group-summary">
                    {{ group.count }} 张面签照 ·
                    平均相似度 {{ (group.avg_similarity * 100).toFixed(1) }}%
                  </span>
                  <el-tag
                    :type="group.avg_similarity > 0.9 ? 'danger' : group.avg_similarity > 0.8 ? 'warning' : 'info'"
                    size="small"
                    effect="dark"
                  >
                    {{ group.avg_similarity > 0.9 ? '高危' : group.avg_similarity > 0.8 ? '可疑' : '待确认' }}
                  </el-tag>
                </div>
              </template>

              <!-- 组内图片 -->
              <div class="group-images">
                <el-card
                  v-for="img in group.images"
                  :key="img.image_id"
                  class="group-image-card"
                  shadow="hover"
                >
                  <div class="group-image-header">
                    <el-tag type="primary" size="small">{{ img.loan_id }}</el-tag>
                    <span class="img-conf-label">
                      置信度 {{ (img.person_confidence * 100).toFixed(0) }}%
                    </span>
                  </div>

                  <el-image
                    :src="getImageUrl(img.file_path)"
                    fit="cover"
                    class="group-face-image"
                    :preview-src-list="[getImageUrl(img.file_path)]"
                    :preview-teleported="true"
                  >
                    <template #error>
                      <div class="image-error-sm">
                        <el-icon :size="24"><PictureFilled /></el-icon>
                      </div>
                    </template>
                  </el-image>

                  <el-button
                    type="primary"
                    size="small"
                    text
                    class="view-related-btn"
                    @click="viewRelated(img.loan_id)"
                  >
                    <el-icon><Link /></el-icon>
                    查看关联文档
                  </el-button>
                </el-card>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>

        <!-- 无可疑组 -->
        <el-empty
          v-else
          description="未发现可疑相似组，所有面签照均为独立交易"
        />

        <section v-if="result.suspicious_pairs?.length" class="pairs-section">
          <h3>相似度明细</h3>
          <el-table :data="result.suspicious_pairs" size="small" stripe>
            <el-table-column prop="image_1" label="图片 A" min-width="160" />
            <el-table-column prop="image_2" label="图片 B" min-width="160" />
            <el-table-column label="相似度" width="130">
              <template #default="{ row }">{{ (row.similarity * 100).toFixed(2) }}%</template>
            </el-table-column>
          </el-table>
        </section>

        <!-- 操作按钮 -->
        <div class="result-actions">
          <el-button @click="goBack" size="large">
            <el-icon><ArrowLeft /></el-icon>
            返回筛选
          </el-button>
          <el-button @click="runSearch" size="large" class="btn-breathe-warning">
            <el-icon><Refresh /></el-icon>
            重新检索
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 关联文档弹窗 -->
    <el-dialog
      v-model="relatedDialogVisible"
      :title="'关联文档 — ' + currentLoanId"
      width="90%"
      top="5vh"
      destroy-on-close
    >
      <div class="related-files" v-if="relatedFiles.length > 0">
        <el-row :gutter="16">
          <el-col
            v-for="file in relatedFiles"
            :key="file.filename"
            :xs="24" :sm="12" :md="8" :lg="6"
          >
            <el-card class="related-file-card" shadow="hover">
              <template #header>
                <div class="related-file-header">
                  <el-tag
                    :type="getFileTagType(file.image_type)"
                    size="small"
                    effect="dark"
                  >
                    {{ file.label }}
                  </el-tag>
                </div>
              </template>
              <el-image
                :src="getImageUrl(file.file_path)"
                fit="contain"
                class="related-image"
                :preview-src-list="[getImageUrl(file.file_path)]"
                :preview-teleported="true"
              >
                <template #error>
                  <div class="image-error-md">
                    <el-icon :size="32"><PictureFilled /></el-icon>
                    <p>无法加载</p>
                  </div>
                </template>
              </el-image>
              <p class="related-filename">{{ file.filename }}</p>
            </el-card>
          </el-col>
        </el-row>
      </div>
      <el-empty v-else description="未找到关联文档" />

      <template #footer>
        <el-button @click="relatedDialogVisible = false" size="large">
          关闭
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  WarningFilled, Search, Connection, ArrowLeft, Refresh,
  Link, PictureFilled,
} from '@element-plus/icons-vue'
import { runSimilarity, getRelatedFiles, getFileUrl } from '../api'
import { ElMessage } from 'element-plus'

const props = defineProps({
  sessionId: { type: String, required: true },
  faceImages: { type: Array, required: true },
  autoStart: { type: Boolean, default: false },
})

const emit = defineEmits(['go-back', 'search-start', 'search-success', 'search-failed'])

const loading = ref(false)
const searched = ref(false)
const result = ref(null)
const activeGroups = ref([])
const loadingPhase = ref('')

const phaseTexts = ['加载 CLIP 视觉编码器...', '提取面签照图像特征...', 'LoRA 微调特征对齐...', '计算余弦相似度矩阵...', '聚类分析相似组...']
let phaseTimer = null

const startPhaseCycle = () => {
  let i = 0
  loadingPhase.value = phaseTexts[0]
  phaseTimer = setInterval(() => {
    i = (i + 1) % phaseTexts.length
    loadingPhase.value = phaseTexts[i]
  }, 2500)
}

const stopPhaseCycle = () => {
  if (phaseTimer) {
    clearInterval(phaseTimer)
    phaseTimer = null
  }
}

const relatedDialogVisible = ref(false)
const currentLoanId = ref('')
const relatedFiles = ref([])

const getImageUrl = (filePath) => {
  return getFileUrl(props.sessionId, filePath)
}

const runSearch = async () => {
  if (props.faceImages.length < 2) {
    ElMessage.warning('面签照数量不足，至少需要2张')
    emit('search-failed', new Error('面签照数量不足'))
    return
  }

  loading.value = true
  emit('search-start')
  startPhaseCycle()
  try {
    const res = await runSimilarity(props.sessionId, props.faceImages, 0.90)
    result.value = res.data
    searched.value = true
    emit('search-success', res.data)
    ElMessage.success(res.message || '检索完成')
  } catch (e) {
    emit('search-failed', e)
    ElMessage.error('检索失败：' + (e.message || '未知错误'))
  } finally {
    loading.value = false
    stopPhaseCycle()
  }
}

onMounted(() => {
  if (props.autoStart) runSearch()
})

const viewRelated = async (loanId) => {
  currentLoanId.value = loanId
  relatedDialogVisible.value = true

  try {
    const res = await getRelatedFiles(props.sessionId, loanId)
    relatedFiles.value = res.data.files || []
  } catch (e) {
    relatedFiles.value = []
  }
}

const getFileTagType = (imageType) => {
  const map = {
    face_signing: 'danger',
    id_card_front: 'primary',
    id_card_back: 'success',
    bank_statement: 'warning',
    contract: 'info',
  }
  return map[imageType] || ''
}

const goBack = () => {
  emit('go-back')
}
</script>

<style scoped>
.similarity-section {
  max-width: 1300px;
  margin: 0 auto;
}

.similarity-card {
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
  margin-bottom: 20px;
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

.search-btn {
  min-width: 200px;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
}

.pairs-section {
  margin-top: 24px;
}

.pairs-section h3 {
  margin: 0 0 12px;
  color: var(--text-primary);
  font-size: 15px;
}

/* 加载中 */
.loading-area {
  padding: 60px 20px;
  text-align: center;
}

.loading-content {
  max-width: 420px;
  margin: 0 auto;
}

/* 旋转光环 */
.loading-ring {
  position: relative;
  width: 120px;
  height: 120px;
  margin: 0 auto 20px;
}

.loading-ring-svg {
  width: 120px;
  height: 120px;
  animation: spin 3s linear infinite;
}

.loading-ring-arc-warn {
  animation: ring-dash-warn 2s ease-in-out infinite;
}

@keyframes ring-dash-warn {
  0% { stroke-dashoffset: 0; }
  50% { stroke-dashoffset: 160; }
  100% { stroke-dashoffset: 0; }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-icon-inner {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation: pulse-icon 1.5s ease-in-out infinite;
}

@keyframes pulse-icon {
  0%, 100% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 0.6; transform: translate(-50%, -50%) scale(1.1); }
}

.loading-content h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px;
  transition: color 0.3s ease;
}

.loading-hint {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 20px;
  transition: color 0.3s ease;
}

.search-progress-wrap {
  max-width: 300px;
  margin: 0 auto;
}

.search-progress {
  margin-bottom: 8px;
}

.loading-phase {
  font-size: 12px;
  color: var(--warning);
  font-weight: 500;
  transition: color 0.3s ease;
  animation: phase-fade 2.5s ease-in-out infinite;
}

@keyframes phase-fade {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

/* 统计区 */
.stats-row {
  display: flex;
  gap: 20px;
  margin-bottom: 28px;
  padding: 20px;
  background: var(--stat-gradient-2);
  border-radius: var(--radius-md);
  flex-wrap: wrap;
  transition: background 0.3s ease;
}

.stats-row > * {
  flex: 1;
  min-width: 120px;
  text-align: center;
}

/* 相似组 */
.groups-section h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
  transition: color 0.3s ease;
}

.group-title {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  width: 100%;
}

.group-summary {
  font-size: 14px;
  color: var(--text-secondary);
  transition: color 0.3s ease;
}

/* 组内图片网格 */
.group-images {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 14px;
  padding: 12px 0;
}

.group-image-card {
  border-radius: var(--radius-sm);
  transition: all 0.3s;
  background: var(--bg-card);
  border-color: var(--border-color);
}

.group-image-card:hover {
  transform: translateY(-2px);
}

.group-image-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.img-conf-label {
  font-size: 12px;
  color: var(--text-muted);
  transition: color 0.3s ease;
}

.group-face-image {
  width: 100%;
  height: 180px;
  object-fit: cover;
  border-radius: 6px;
  margin: 8px 0;
}

.image-error-sm {
  width: 100%;
  height: 180px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--border-light);
  color: var(--text-muted);
  border-radius: 6px;
  transition: background-color 0.3s ease;
}

.view-related-btn {
  width: 100%;
  margin-top: 4px;
}

.result-actions {
  margin-top: 28px;
  display: flex;
  gap: 12px;
  justify-content: center;
}

/* 关联文档弹窗 */
.related-files {
  padding: 8px 0;
}

.related-file-card {
  margin-bottom: 14px;
  border-radius: var(--radius-sm);
  background: var(--bg-card);
  border-color: var(--border-color);
}

.related-file-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.related-image {
  width: 100%;
  height: 220px;
  object-fit: contain;
  background: var(--bg-card-hover);
  border-radius: 6px;
  transition: background-color 0.3s ease;
}

.image-error-md {
  width: 100%;
  height: 220px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: var(--border-light);
  color: var(--text-muted);
  border-radius: 6px;
  transition: background-color 0.3s ease;
}

.related-filename {
  text-align: center;
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 8px;
  transition: color 0.3s ease;
}
</style>
