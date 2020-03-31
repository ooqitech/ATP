import request from '@/plugin/axios'
/**
 * 获取运行日志
 */

export function getRunLog(data) {
  return request({
    url: '/atp/auto/apiPushLog/push',
    method: 'post',
    data
  })
}

/**
 * 测试报告中获取运行日志
 */

export function getTestReportRunLog(data) {
  return request({
    url: '/atp/auto/apiPushLog/pushTaskLog',
    method: 'post',
    data
  })
}
