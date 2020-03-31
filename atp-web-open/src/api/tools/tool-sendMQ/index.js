import request from '@/plugin/axios'
/**
 * 获取短信验证码接口
 */

export function sendMQ(data) {
  return request({
    url: '/atp/qa/sendMQ',
    method: 'post',
    data
  })
}
