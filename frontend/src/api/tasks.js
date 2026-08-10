import { detectionTasksMock } from '../mock/tasks'

const pause = () => new Promise((resolve) => setTimeout(resolve, 220))

const matchesDate = (createdAt, dateRange) => {
  if (!dateRange?.length) return true
  const date = createdAt.slice(0, 10)
  return date >= dateRange[0] && date <= dateRange[1]
}

// TODO: replace with GET /api/history/tasks after the backend contract is confirmed.
export const getDetectionTasks = async (filters = {}) => {
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

// TODO: replace with GET /api/history/tasks/{taskId} after the backend contract is confirmed.
export const getDetectionTask = async (taskId) => {
  await pause()
  const task = detectionTasksMock.find((item) => item.taskId === taskId)
  if (!task) throw new Error('未找到检测任务')
  return { code: 200, mock: true, data: task }
}
