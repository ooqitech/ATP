import request from '@/plugin/axios'

/**
 * 执行api测试用例
 */

export function run(data) {
  return request({
    url: '/atp/auto/run',
    method: 'post',
    data
  })
}

/**
 * 执行UI自动化
 */

export function runUiCase(data) {
  return request({
    url: '/atp/auto/run_ui',
    method: 'post',
    data
  })
}

/**
 * 查询api测试报告
 */

export function queryReportById(data) {
  return request({
    url: '/atp/auto/apiReport/queryReportById',
    method: 'post',
    data
  })
}
