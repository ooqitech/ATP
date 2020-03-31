import request from '@/plugin/axios'
/**
 * 获取report
 */

export function queryReport(data) {
  return request({
    url: '/atp/auto/apiReport/pagingQueryReportList',
    method: 'post',
    data
  })
}

export function deletereport(data) {
  return request({
    url: '/atp/auto/apiReport/delete',
    method: 'post',
    data
  })
}
