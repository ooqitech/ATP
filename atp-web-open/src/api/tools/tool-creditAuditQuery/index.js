import request from '@/plugin/axios'
/**
 * 获取短信验证码接口
 */

export function crediAuditQuery(data) {
  return request({
    url: '/atp/qa/crediAuditQuery',
    method: 'post',
    data
  })
}
