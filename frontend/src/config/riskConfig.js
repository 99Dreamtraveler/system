export const riskConfig = {
  high: { label: '高风险', tagType: 'danger' },
  medium: { label: '中风险', tagType: 'warning' },
  low: { label: '低风险', tagType: 'success' },
  thresholds: {
    high: null,
    medium: null,
    note: '风险阈值待后端与业务规则确认；当前配置仅用于前端展示。',
  },
}

export const getRiskConfig = (level) => riskConfig[level] || { label: level || '待确认', tagType: 'info' }
