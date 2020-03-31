import request from '@/plugin/axios'
/**
 * 查询测试任务运行结果
 */

export function getRunResults(data) {
  return request({
    url: '/atp/auto/apiTask/getRunResults',
    method: 'post',
    data
  })
}

/**
 * 查询某一天的测试任务运行结果
 */

export function getRunResultBySingleDay(data) {
  return request({
    url: '/atp/auto/apiTask/getRunResultBySingleDay',
    method: 'post',
    data
  })
}

/**
 * 下载测试任务运行结果
 */

export function exportSummaryToExcel(data) {
  return request({
    url: '/atp/auto/apiTask/exportSummaryToExcel',
    method: 'post',
    data
  })
}
