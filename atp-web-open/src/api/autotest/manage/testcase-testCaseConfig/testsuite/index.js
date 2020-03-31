import request from '@/plugin/axios'

/**
 * 添加测试集
 */

export function addSuite(data) {
  return request({
    url: '/atp/auto/testsuite/add',
    method: 'post',
    data
  })
}

/**
 * 修改测试集
 */

export function editSuite(data) {
  return request({
    url: '/atp/auto/testsuite/edit',
    method: 'post',
    data
  })
}

/**
 * 删除测试集
 */

export function deleteSuite(data) {
  return request({
    url: '/atp/auto/testsuite/delete',
    method: 'post',
    data
  })
}

/**
 * 查询测试集详情
 */

export function querySuite(data) {
  return request({
    url: '/atp/auto/testsuite/detail',
    method: 'post',
    data
  })
}

/**
 * 查询某个项目下所有用例集
 */

export function listByProjectId(data) {
  return request({
    url: '/atp/auto/testsuite/listByProjectId',
    method: 'post',
    data
  })
}

/**
 * 移动测试集
 */

export function changeModuleParent(data) {
  return request({
    url: '/atp/auto/testsuite/changeParent',
    method: 'post',
    data
  })
}
