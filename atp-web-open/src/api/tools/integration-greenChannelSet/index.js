import request from '@/plugin/axios'
/**
 * 设置绿色通道接口
 */

export function setGreenchannel(data) {
  return request({
    url: '/atp/qa/greenChannel',
    method: 'post',
    data
  })
}
