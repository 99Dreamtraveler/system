import { getStatisticsSnapshot } from '../services/statistics'
import api from './index'
import { useMockData } from './dataSource'

const pause = () => new Promise((resolve) => setTimeout(resolve, 220))

export const getAnalyticsStatistics = async (range) => {
  if (!useMockData()) {
    const end = new Date(); const start = new Date(end)
    start.setDate(start.getDate() - ({ today: 0, '7d': 6, '30d': 29, '90d': 89 }[range] || 0))
    const format = (date) => `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
    const params = range === 'all' ? { all: true, endDate: format(end) } : { startDate: format(start), endDate: format(end) }
    const res = await api.get('/statistics/analytics', { params })
    return { ...res, mock: false }
  }
  await pause()
  return { code: 200, mock: true, data: getStatisticsSnapshot(range) }
}
