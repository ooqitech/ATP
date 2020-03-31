import request from '@/plugin/axios'
/**
 * 获取短信验证码接口
 */

export function getSms(data) {
  return request({
    url: '/atp/qa/getSms',
    method: 'post',
    data
  })
}
