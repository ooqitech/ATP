import request from '@/plugin/axios'
/**
 * 查询需要记录失败原因的项目及构建号接口
 */

export function queryRecentFailPush(data) {
  return request({
    url: '/atp/qa/queryRecentFailPush',
    method: 'post',
    data
  })
}

/**
 * 登记冒烟测试失败原因
 */

export function recordFailure(data) {
  return request({
    url: '/atp/qa/recordFailure',
    method: 'post',
    data
  })
}
