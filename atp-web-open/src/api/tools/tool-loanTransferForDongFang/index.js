import request from '@/plugin/axios'
/**
 * 一键放款接口
 */

export function executeLoan(data) {
  return request({
    url: '/atp/qa/executeLoan',
    method: 'post',
    data
  })
}
