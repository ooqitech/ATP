import request from '@/plugin/axios'
/**
 * 指定放款时间只生成还款计划
 */

export function updateLoanPlan(data) {
  return request({
    url: '/atp/qa/updateLoanPlanForDongFang',
    method: 'post',
    data
  })
}
