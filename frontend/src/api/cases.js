import { riskCasesMock } from '../mock/cases'

const pause = () => new Promise((resolve) => setTimeout(resolve, 180))
const records = riskCasesMock.map((item) => ({ ...item, businessA: { ...item.businessA }, businessB: { ...item.businessB } }))

// MOCK ONLY: replace with risk-case APIs after the backend contract is available.
export const getRiskCases = async (filters = {}) => {
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
  await pause()
  const item = records.find((record) => record.caseId === caseId)
  if (!item) throw new Error('风险案件不存在')
  return { code: 200, mock: true, data: item }
}

export const updateRiskCaseStatus = async (caseId, status) => {
  await pause()
  const item = records.find((record) => record.caseId === caseId)
  if (!item) throw new Error('风险案件不存在')
  item.status = status
  return { code: 200, mock: true, data: item }
}
