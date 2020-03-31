import request from '@/plugin/axios'
/**
 * 新增接口
 */

export function addApi(data) {
  return request({
    url: '/atp/auto/apiIntf/add',
    method: 'post',
    data
  })
}

/**
 * 编辑接口
 */

export function editApi(data) {
  return request({
    url: '/atp/auto/apiIntf/edit',
    method: 'post',
    data
  })
}

/**
 * 删除接口
 */

export function deleteApi(data) {
  return request({
    url: '/atp/auto/apiIntf/delete',
    method: 'post',
    data
  })
}

/**
 * 接口详情
 */

export function queryApiDetail(data) {
  return request({
    url: '/atp/auto/apiIntf/detail',
    method: 'post',
    data
  })
}

/**
 * 根据接口id 查询接口下所有的用例
 */

export function queryCaseByIntfId(data) {
  return request({
    url: '/atp/auto/apiTestcase/queryByIntfId',
    method: 'post',
    data
  })
}

/**
 * 根据工程id 查询工程下所有的接口
 */

export function queryByProjectId(data) {
  return request({
    url: '/atp/auto/apiIntf/queryBySystemId',
    method: 'post',
    data
  })
}
