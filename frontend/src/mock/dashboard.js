import { getDashboardSnapshot } from '../services/statistics'

const snapshot = getDashboardSnapshot()
const riskKey = { 高风险: 'high', 中风险: 'medium', 低风险: 'low' }
const taskStatus = { 已完成: 'completed', 检测中: 'running', 检测失败: 'failed' }

export const recentTasks = snapshot.tasks.map((task) => ({ id: task.taskId, detectedAt: task.createdAt, imageCount: task.imageStats.valid, affectedCount: task.screeningStats.interviewPhotos, abnormalImages: task.abnormalImages.length, riskLevel: riskKey[task.riskLevel], status: taskStatus[task.status] }))
export const detectionTrend = snapshot.detectionTrend.map((item) => ({ date: item.date.slice(5), detections: item.detectionCount, abnormalImages: item.abnormalCount }))

export const highRiskCases = snapshot.cases.filter((item) => item.riskLevel === '高风险').map((item) => ({ id: item.caseId, similarity: item.similarity / 100, riskLevel: 'high', foundAt: item.discoveredAt, status: item.status }))

export const getDashboardMetrics = () => {
  const completedTasks = recentTasks.filter((task) => task.status === 'completed')
  const todayTasks = recentTasks.filter((task) => task.detectedAt.startsWith('2026-08-07'))
  return {
    totalImages: completedTasks.reduce((sum, task) => sum + task.imageCount, 0),
    affectedCount: completedTasks.reduce((sum, task) => sum + task.affectedCount, 0),
    abnormalImages: completedTasks.reduce((sum, task) => sum + task.abnormalImages, 0),
    highRiskCases: highRiskCases.length,
    todayTasks: todayTasks.length,
    completedTasks: completedTasks.length,
  }
}

export const getRiskDistribution = () => ({
  high: snapshot.riskDistribution.high,
  medium: snapshot.riskDistribution.medium,
  low: snapshot.riskDistribution.low,
})
