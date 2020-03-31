import request from '@/plugin/axios'
/**
 * 查询所有自动化项目详细信息接口
 */

export function queryAutotestDetails(data) {
  return request({
    url: '/atp/qa/queryAutotestDetails',
    method: 'post',
    data
  })
}
