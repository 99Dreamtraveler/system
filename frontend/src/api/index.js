import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 600000, // 10分钟超时（CPU推理370张图需要较长时间）
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    if (user.token) {
      config.headers.Authorization = `Bearer ${user.token}`
    }
    const sessionId = localStorage.getItem('session_id')
    if (sessionId) {
      config.headers['X-Session-Id'] = sessionId
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API 错误:', error)
    return Promise.reject(error)
  }
)

// ============================================
// API 函数
// ============================================

// 认证
export const login = (username, password) =>
  api.post('/login', { username, password })

export const register = (username, password) =>
  api.post('/register', { username, password })

// 上传
export const uploadFolder = (formData) =>
  api.post('/upload/folder', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })

// 相似度检测
export const runSimilarity = (sessionId, faceImages, threshold) =>
  api.post('/similarity/detect', {
    session_id: sessionId,
    face_images: faceImages,
    threshold: threshold || 0.90,
  })

// 新增: folder_path 模式直接检测
export const runSimilarityByFolder = (folderPath, threshold) =>
  api.post('/similarity/detect', {
    folder_path: folderPath,
    threshold: threshold || 0.90,
  })

// 阈值扫描
export const runThresholdScan = (folderPath) =>
  api.post('/similarity/threshold-scan', { folder_path: folderPath })

// 获取关联文件
export const getRelatedFiles = (sessionId, loanId) =>
  api.get(`/similarity/related/${sessionId}/${loanId}`)

// 健康检查
export const healthCheck = () => api.get('/health')

// 获取文件URL
export const getFileUrl = (sessionId, filePath) =>
  `/api/file/${sessionId}/${filePath}`

// 贷款记录管理
export const scanRecords = (sessionId) =>
  api.get(`/scan/${sessionId}`)

export const createRecord = (sessionId, formData) =>
  api.post(`/records/${sessionId}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })

export const deleteRecord = (sessionId, loanId) =>
  api.delete(`/records/${sessionId}/${loanId}`)

export const uploadRecordField = (sessionId, loanId, field, formData) =>
  api.post(`/records/${sessionId}/${loanId}/${field}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })

export default api
