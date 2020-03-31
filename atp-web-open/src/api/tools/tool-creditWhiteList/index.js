import request from '@/plugin/axios'

/**
 * 配置白名单接口
 */

export function configCredit(data) {
  return request({
    url: '/atp/qa/configCredit',
    method: 'post',
    data
  })
}

/**
 * 查询白名单接口
 */

export function queryCredit(data) {
  return request({
    url: '/atp/qa/queryCredit',
    method: 'post',
    data
  })
}
