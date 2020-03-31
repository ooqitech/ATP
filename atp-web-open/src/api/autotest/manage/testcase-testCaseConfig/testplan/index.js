import request from '@/plugin/axios'

/**
 * 添加测试计划
 */

export function addTestPlan(data) {
  return request({
    url: '/atp/auto/testPlan/add',
    method: 'post',
    data
  })
}

/**
 * 测试计划列表
 */
export function fetchPlanList(data) {
  return request({
    url: '/atp/auto/testPlan/list',
    method: 'post',
    data
  })
}

/**
 * 测试计划详情
 */

export function queryTestPlan(data) {
  return request({
    url: '/atp/auto/testPlan/detail',
    method: 'post',
    data
  })
}

/**
 * 删除测试计划
 */

export function deleteTestPlan(data) {
  return request({
    url: '/atp/auto/testPlan/delete',
    method: 'post',
    data
  })
}

/**
 * 编辑测试计划
 */

export function editTestPlan(data) {
  return request({
    url: '/atp/auto/testPlan/edit',
    method: 'post',
    data
  })
}

/**
 * 查询测试计划最近一次运行报告ID
 */
export function queryTestPlanRecentReportId(data) {
  return request({
    url: '/atp/auto/testPlan/queryRecentReportId',
    method: 'post',
    data
  })
}
