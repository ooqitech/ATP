import request from '@/plugin/axios'

/**
 * 获取公共变量列表
 */

export function fetchPublicvariableList(data) {
  return request({
    url: '/atp/auto/apiPublicVariable/list',
    method: 'get',
    params: data
  })
}

/**
 * 增加公共变量列表
 */

export function addPublicvariable(data) {
  return request({
    url: '/atp/auto/apiPublicVariable/addVariable',
    method: 'post',
    data
  })
}

/**
 * 获取已支持的变量列表
 */

export function querySupportPubVariables(data) {
  return request({
    url: '/atp/auto/apiPublicVariable/querySupportPubVariables',
    method: 'post',
    data
  })
}
/**
 * 编辑公共变量
 */

export function editPublicvariable(data) {
  return request({
    url: '/atp/auto/apiPublicVariable/edit',
    method: 'post',
    data
  })
}

/**
 * 删除公共变量
 */
export function deleteVariable(data) {
  return request({
    url: '/atp/auto/apiPublicVariable/delete',
    method: 'post',
    data
  })
}

/**
 * 根据用例id查询用例(包含前置)的公共变量列表
 */
export function queryPubVarsByTcList(data) {
  return request({
    url: '/atp/auto/apiPublicVariable/queryPubVariablesByTestcaseList',
    method: 'post',
    data
  })
}
