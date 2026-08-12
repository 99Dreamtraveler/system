import { riskCasesMock } from '../mock/cases'
import api from './index'
import { useMockData } from './dataSource'

const pause = () => new Promise((resolve) => setTimeout(resolve, 180))
const records = riskCasesMock.map((item) => ({ ...item, businessA: { ...item.businessA }, businessB: { ...item.businessB } }))

export const getRiskCases = async (filters = {}) => {
  if (!useMockData()) {
    const res = await api.get('/risk/cases', { params: { caseId: filters.caseId || undefined, businessId: filters.businessId || undefined, startTime: filters.dateRange?.[0], endTime: filters.dateRange?.[1], riskLevel: filters.riskLevel || undefined, status: filters.status || undefined } })
    return { ...res, mock: false }
  }
  await pause()
  const keyword = filters.caseId?.trim().toLowerCase()
  const businessId = filters.businessId?.trim().toLowerCase()
  const [startDate, endDate] = filters.dateRange || []
  const items = records.filter((item) => (
    (!keyword || item.caseId.toLowerCase().includes(keyword))
    && (!businessId || item.businessA.businessId.toLowerCase().includes(businessId) || item.businessB.businessId.toLowerCase().includes(businessId) || item.businessA.loanId.toLowerCase().includes(businessId) || item.businessB.loanId.toLowerCase().includes(businessId))
    && (!filters.riskLevel || item.riskLevel === filters.riskLevel)
    && (!filters.status || item.status === filters.status)
    && (!startDate || item.discoveredAt.slice(0, 10) >= startDate)
    && (!endDate || item.discoveredAt.slice(0, 10) <= endDate)
  ))
  return { code: 200, mock: true, data: { records: items, total: items.length } }
}

export const getRiskCase = async (caseId) => {
  if (!useMockData()) {
    return { ...(await api.get(`/risk/cases/${encodeURIComponent(caseId)}`)), mock: false }
  }
  await pause()
  const item = records.find((record) => record.caseId === caseId)
  if (!item) throw new Error('风险案件不存在')
  return { code: 200, mock: true, data: item }
}

export const updateRiskCaseStatus = async (caseId, status) => {
  if (!useMockData()) {
    const endpoint = { '核查中': 'review', '已确认': 'confirm', '已排除': 'dismiss' }[status]
    if (endpoint) return { ...(await api.post(`/risk/cases/${encodeURIComponent(caseId)}/${endpoint}`)), mock: false }
  }
  await pause()
  const item = records.find((record) => record.caseId === caseId)
  if (!item) throw new Error('风险案件不存在')
  item.status = status
  return { code: 200, mock: true, data: item }
}
