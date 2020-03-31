import request from '@/plugin/axios'

/**
 * 获取mock日志
 */

export function getMockHistory(data) {
  return request({
    url: '/atp/mock/support/getMockHistory',
    method: 'post',
    data
  })
}
