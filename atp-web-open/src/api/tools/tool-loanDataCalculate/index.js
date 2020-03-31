import request from '@/plugin/axios'
/**
 * 贷后常用计算公式-生成还款计划：等额本息按日计息
 */

export function generalRepayPlanBS(data) {
  return request({
    url: '/atp/qa/generalRepayPlanBS',
    method: 'post',
    data
  })
}

/**
 * 贷后常用计算公式-全额回购
 */

export function calcBuybackAll(data) {
  return request({
    url: '/atp/qa/calcBuybackAll',
    method: 'post',
    data
  })
}
