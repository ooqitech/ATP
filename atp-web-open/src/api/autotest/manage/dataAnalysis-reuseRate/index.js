import request from '@/plugin/axios'
/**
 * 查询用例复用记录汇总
 */

export function getReuseSummary(data) {
  return request({
    url: '/atp/auto/stat/getReuseSummary',
    method: 'post',
    data
  })
}

/**
 * 查询用例复用记录变化趋势
 */

export function getReuseTrend(data) {
  return request({
    url: '/atp/auto/stat/getReuseTrend',
    method: 'post',
    data
  })
}
