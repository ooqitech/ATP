import request from '@/plugin/axios'
/**
 * 清理测试数据接口
 */

export function clearData(data) {
  return request({
    url: '/atp/qa/clearData',
    method: 'post',
    data
  })
}
