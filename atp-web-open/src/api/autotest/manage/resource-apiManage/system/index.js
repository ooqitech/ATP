import request from '@/plugin/axios'

/**
 * 新增工程
 */

export function addApiSystem(data) {
  return request({
    url: '/atp/auto/apiSystem/add',
    method: 'post',
    data
  })
}

/**
 * 编辑工程
 */

export function editApiSystem(data) {
  return request({
    url: '/atp/auto/apiSystem/edit',
    method: 'post',
    data
  })
}

/**
 * 删除工程
 */

export function deleteApiSystem(data) {
  return request({
    url: '/atp/auto/apiSystem/delete',
    method: 'post',
    data
  })
}

/**
 * 根据公司id查询 公司下所有的系统
 */

export function queryByCompanyId(data) {
  return request({
    url: '/atp/auto/apiSystem/queryByCompanyId',
    method: 'post',
    data
  })
}

/**
 * 根据系统查询git分支号
 */

export function getGitBranchNamesBySystemId(data) {
  return request({
    url: '/atp/auto/apiSystem/getGitBranchNamesBySystemId',
    method: 'post',
    data
  })
}
