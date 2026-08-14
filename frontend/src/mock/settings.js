// MOCK ONLY: replace with an audited operation-log API when it becomes available.
export const operationLogsMock = [
  { id: 'LOG_20260807001', username: '张三', action: '登录', detail: '用户登录系统', occurredAt: '2026-08-07 09:18:06', type: 'primary' },
  { id: 'LOG_20260807002', username: '张三', action: '上传影像', detail: '上传业务影像文件夹 LOAN_001', occurredAt: '2026-08-07 09:30:20', type: 'info' },
  { id: 'LOG_20260807003', username: '张三', action: '开始检测', detail: '提交影像筛选与相似度检测', occurredAt: '2026-08-07 09:31:04', type: 'warning' },
  { id: 'LOG_20260807004', username: '张三', action: '完成检测', detail: '检测任务 TASK_202608070001 已完成', occurredAt: '2026-08-07 09:34:18', type: 'success' },
  { id: 'LOG_20260807005', username: '李四', action: '查看案件', detail: '查看风险案件 CASE_202608070001', occurredAt: '2026-08-07 10:26:42', type: 'info' },
  { id: 'LOG_20260807006', username: '李四', action: '生成报告', detail: '发起检测报告生成预览', occurredAt: '2026-08-07 10:31:09', type: 'primary' },
]
