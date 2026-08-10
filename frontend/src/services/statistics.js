import { detectionTasksMock } from '../mock/tasks'
import { riskCasesMock } from '../mock/cases'
import { imageCategoryByTaskId, imageCategoryLabels } from '../mock/analytics'

const referenceDate = '2026-08-07'
const rangeDays = { today: 1, '7d': 7, '30d': 30, '90d': 90 }
const riskKey = { 高风险: 'high', 中风险: 'medium', 低风险: 'low' }
const parseDate = (value) => new Date(`${value.slice(0, 10)}T00:00:00`)
// Keep the mock reporting calendar in local date terms; toISOString() would shift
// Asia/Shanghai midnight into the previous UTC date.
const formatDate = (date) => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const getRangeStart = (range) => {
  const start = parseDate(referenceDate)
  start.setDate(start.getDate() - (rangeDays[range] || 1) + 1)
  return formatDate(start)
}

const inRange = (value, range) => value.slice(0, 10) >= getRangeStart(range) && value.slice(0, 10) <= referenceDate
const dateSeries = (range) => {
  const dates = []
  const cursor = parseDate(getRangeStart(range))
  const end = parseDate(referenceDate)
  while (cursor <= end) { dates.push(formatDate(cursor)); cursor.setDate(cursor.getDate() + 1) }
  return dates
}

const sumCategories = (tasks) => Object.keys(imageCategoryLabels).reduce((result, key) => ({
  ...result,
  [key]: tasks.reduce((total, task) => total + (imageCategoryByTaskId[task.taskId]?.[key] || 0), 0),
}), {})

export const getStatisticsSnapshot = (range = 'today') => {
  const tasks = detectionTasksMock.filter((item) => inRange(item.createdAt, range))
  const cases = riskCasesMock.filter((item) => inRange(item.discoveredAt, range))
  const dates = dateSeries(range)
  const detectionTrend = dates.map((date) => {
    const dayTasks = tasks.filter((item) => item.createdAt.startsWith(date))
    return { date, detectionCount: dayTasks.reduce((sum, item) => sum + item.imageStats.valid, 0), abnormalCount: dayTasks.reduce((sum, item) => sum + item.abnormalImages.length, 0) }
  })
  const riskTrend = dates.map((date) => {
    const dayCases = cases.filter((item) => item.discoveredAt.startsWith(date))
    return { date, high: dayCases.filter((item) => item.riskLevel === '高风险').length, medium: dayCases.filter((item) => item.riskLevel === '中风险').length, low: dayCases.filter((item) => item.riskLevel === '低风险').length }
  })
  const similarityDistribution = [
    { label: '0~50%', min: 0, max: 50, count: 0 }, { label: '50~70%', min: 50, max: 70, count: 0 }, { label: '70~80%', min: 70, max: 80, count: 0 }, { label: '80~90%', min: 80, max: 90, count: 0 }, { label: '90~100%', min: 90, max: 100.01, count: 0 },
  ].map((bucket) => ({ ...bucket, count: cases.filter((item) => item.similarity >= bucket.min && item.similarity < bucket.max).length }))
  const riskDistribution = cases.reduce((result, item) => ({ ...result, [riskKey[item.riskLevel]]: result[riskKey[item.riskLevel]] + 1 }), { high: 0, medium: 0, low: 0 })
  return { range, tasks, cases, detectionTrend, riskTrend, similarityDistribution, imageCategoryDistribution: sumCategories(tasks), riskDistribution }
}

export const getDashboardSnapshot = () => getStatisticsSnapshot('7d')
