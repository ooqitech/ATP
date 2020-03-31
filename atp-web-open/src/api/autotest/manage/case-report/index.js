import request from '@/plugin/axios'
/**
 * 获取任务运行summary数据
 */

export function getSummary(data) {
  return request({
    url: '/atp/auto/apiTask/getSummary',
    method: 'post',
    data
  })
}

/**
 * 查询用例执行具体数据
 */

export function getRunDataByTestcase(data) {
  return request({
    url: '/atp/auto/apiTask/getRunDataByTestcase',
    method: 'post',
    data
  })
}
