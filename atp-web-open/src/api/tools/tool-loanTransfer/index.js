import request from '@/plugin/axios'
/**
 * 查询待放款订单接口
 */

export function queryRecentOrders(data) {
  return request({
    url: '/atp/qa/queryRecentOrders',
    method: 'post',
    data
  })
}

/**
 * 一键放款接口
 */

export function loanTransferSucc(data) {
  return request({
    url: '/atp/qa/loanTransferSucc',
    method: 'post',
    data
  })
}
