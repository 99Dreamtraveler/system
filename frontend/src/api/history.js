import { historicalInterviewPhotosMock } from '../mock/historyInterviewPhotos'

// TODO: replace with GET /api/history/interview-photos after the backend contract is confirmed.
export const getHistoricalInterviewPhotos = async (params = {}) => {
  const page = Number(params.page) || 1
  const pageSize = Number(params.pageSize) || 20
  const records = historicalInterviewPhotosMock.slice((page - 1) * pageSize, page * pageSize)

  return {
    code: 200,
    message: 'MOCK data: historical interview photo service is pending backend implementation.',
    data: {
      total: historicalInterviewPhotosMock.length,
      page,
      pageSize,
      records,
    },
    mock: true,
  }
}
