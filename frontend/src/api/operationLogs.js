import { operationLogsMock } from '../mock/settings'
import api from './index'
import { useMockData } from './dataSource'

const pause = () => new Promise((resolve) => setTimeout(resolve, 180))

export const getOperationLogs = async ({ page = 1, pageSize = 10 } = {}) => {
  if (!useMockData()) {
    const res = await api.get('/system/operation-logs', { params: { page, pageSize } })
    return { ...res, mock: false }
  }

  await pause()
  const start = (page - 1) * pageSize
  return {
    code: 200,
    mock: true,
    data: {
      total: operationLogsMock.length,
      page,
      pageSize,
      records: operationLogsMock.slice(start, start + pageSize),
    },
  }
}
