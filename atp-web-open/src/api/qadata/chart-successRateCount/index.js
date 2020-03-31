import request from '@/plugin/axios'
/**
 * 查询所有自动化项目接口
 */

export function queryAutotestProject(data) {
  return request({
    url: '/atp/qa/queryAutotestProject',
    method: 'post',
    data
  })
}

/**
 * 按月查询自动化用例执行结果接口
 */

export function queryAutotestResultByMonth(data) {
  return request({
    url: '/atp/qa/queryAutotestResultByMonth',
    method: 'post',
    data
  })
}
