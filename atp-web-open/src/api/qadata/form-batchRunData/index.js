import request from '@/plugin/axios'
/**
 * 查询所有跑批自动化项目接口
 */

export function queryBatchRunProject(data) {
  return request({
    url: '/atp/qa/queryBatchRunProject',
    method: 'post',
    data
  })
}

/**
 * 获取自动化定时跑批数据
 */

export function queryBatchRunData(data) {
  return request({
    url: '/atp/qa/queryBatchRunData',
    method: 'post',
    data
  })
}
