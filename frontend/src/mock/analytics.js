// Stable analytics metadata keyed by existing detection task IDs. No random data is generated here.
export const imageCategoryByTaskId = {
  TASK_202608070001: { interview: 28, idCard: 56, bankStatement: 50, contract: 40, other: 10 },
  TASK_202608070002: { interview: 19, idCard: 40, bankStatement: 40, contract: 35, other: 7 },
  TASK_202608060003: { interview: 31, idCard: 70, bankStatement: 65, contract: 50, other: 9 },
  TASK_202608060004: { interview: 12, idCard: 30, bankStatement: 28, contract: 22, other: 5 },
  TASK_202608050005: { interview: 22, idCard: 50, bankStatement: 48, contract: 36, other: 8 },
  TASK_202608050006: { interview: 0, idCard: 22, bankStatement: 20, contract: 22, other: 4 },
}

export const imageCategoryLabels = {
  interview: '面签照片',
  idCard: '身份证',
  bankStatement: '银行流水',
  contract: '合同',
  other: '其他',
}
