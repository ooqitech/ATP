import request from '@/plugin/axios'
/**
 * 查询待发货订单接口
 */

export function queryCollBackOrders(data) {
  return request({
    url: '/atp/qa/queryCollBackOrders',
    method: 'post',
    data
  })
}

/**
 * 发货接口
 */

export function collOrdersDeliver(data) {
  return request({
    url: '/atp/qa/collOrdersDeliver',
    method: 'post',
    data
  })
}
