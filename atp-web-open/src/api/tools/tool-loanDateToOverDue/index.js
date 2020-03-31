import request from '@/plugin/axios'
/**
 * 指定放款时间重新生成还款计划+逾期跑批
 */

export function createAccountingOverdue(data) {
  return request({
    url: '/atp/qa/createAccountingOverdue',
    method: 'post',
    data
  })
}

/**
 * 指定放款时间只生成还款计划
 */

export function updateLoanPlan(data) {
  return request({
    url: '/atp/qa/updateLoanPlan',
    method: 'post',
    data
  })
}

/**
 * 逾期跑批
 */

export function executeOverdue(data) {
  return request({
    url: '/atp/qa/executeOverdue',
    method: 'post',
    data
  })
}
