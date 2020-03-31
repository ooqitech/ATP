import request from '@/plugin/axios'

/**
 * 新增需要配置mock数据的系统
 */

export function addMockProject(data) {
  return request({
    url: '/atp/mock/config/project/add',
    method: 'post',
    data
  })
}

/**
 * 修改需要配置mock数据的系统
 */

export function editMockProject(data) {
  return request({
    url: '/atp/mock/config/project/edit',
    method: 'post',
    data
  })
}

/**
 * 删除需要配置mock数据的系统
 */

export function delMockProject(data) {
  return request({
    url: '/atp/mock/config/project/delete',
    method: 'post',
    data
  })
}

/**
 * 查询已配置的mock接口列表
 */

export function queryMockInterfaces(data) {
  return request({
    url: '/atp/mock/config/project/query',
    method: 'post',
    data
  })
}
