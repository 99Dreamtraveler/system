export const useMockData = () => import.meta.env.VITE_DATA_SOURCE === 'mock'

export const hasRecords = (response) => Array.isArray(response?.data?.records) && response.data.records.length > 0
