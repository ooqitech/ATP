import request from '@/plugin/axios'
/**
 * 获取短信验证码接口
 */

export function uaaLogDecrypt(data) {
  return request({
    url: '/atp/qa/uaaLogDecrypt',
    method: 'post',
    data
  })
}
