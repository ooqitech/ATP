import request from '@/plugin/axios'
/**
 * 设置资方匹配规则
 */

export function setFundMatch(data) {
  return request({
    url: '/atp/qa/setFundMatch',
    method: 'post',
    data
  })
}

/**
 * 查询已配置的资方匹配规则
 */

export function queryFundMatchSettings(data) {
  return request({
    url: '/atp/qa/queryFundMatchSettings',
    method: 'post',
    data
  })
}

/**
 * 删除资方匹配规则
 */

export function deleteFundMatch(data) {
  return request({
    url: '/atp/qa/deleteFundMatch',
    method: 'post',
    data
  })
}
