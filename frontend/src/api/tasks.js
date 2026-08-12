import { detectionTasksMock } from '../mock/tasks'
import api from './index'
import { useMockData } from './dataSource'

const pause = () => new Promise((resolve) => setTimeout(resolve, 220))

const matchesDate = (createdAt, dateRange) => {
  if (!dateRange?.length) return true
  const date = createdAt.slice(0, 10)
  return date >= dateRange[0] && date <= dateRange[1]
}

export const getDetectionTasks = async (filters = {}) => {
  if (!useMockData()) {
    const res = await api.get('/history/tasks', { params: { taskId: filters.taskId || undefined, startTime: filters.dateRange?.[0], endTime: filters.dateRange?.[1], status: filters.status || undefined, riskLevel: filters.riskLevel || undefined } })
    return { ...res, mock: false }
  }
  await pause()
  const taskId = filters.taskId?.trim().toLowerCase() || ''
  const records = detectionTasksMock.filter((task) => (
    (!taskId || task.taskId.toLowerCase().includes(taskId))
    && matchesDate(task.createdAt, filters.dateRange)
    && (!filters.status || task.status === filters.status)
    && (!filters.riskLevel || task.riskLevel === filters.riskLevel)
  ))

  return { code: 200, mock: true, data: { records } }
}

export const getDetectionTask = async (taskId) => {
  if (!useMockData()) {
    return { ...(await api.get(`/history/tasks/${encodeURIComponent(taskId)}`)), mock: false }
  }
  await pause()
  const task = detectionTasksMock.find((item) => item.taskId === taskId)
  if (!task) throw new Error('未找到检测任务')
  return { code: 200, mock: true, data: task }
}
