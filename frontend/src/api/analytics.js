import { getStatisticsSnapshot } from '../services/statistics'

const pause = () => new Promise((resolve) => setTimeout(resolve, 220))

// TODO: replace with GET /api/statistics/analytics after the backend contract is confirmed.
export const getAnalyticsStatistics = async (range) => {
  await pause()
  return { code: 200, mock: true, data: getStatisticsSnapshot(range) }
}
