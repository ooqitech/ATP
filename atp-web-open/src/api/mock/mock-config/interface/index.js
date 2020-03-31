import request from '@/plugin/axios'

/**
 * 新增mock接口
 */

export function addMockInterface(data) {
  return request({
    url: '/atp/mock/config/interface/add',
    method: 'post',
    data
  })
}

/**
 * 修改mock接口
 */

export function editMockInterface(data) {
  return request({
    url: '/atp/mock/config/interface/edit',
    method: 'post',
    data
  })
}

/**
 * 删除mock接口
 */

export function delMockInterface(data) {
  return request({
    url: '/atp/mock/config/interface/delete',
    method: 'post',
    data
  })
}

/**
 * 查询mock接口详情
 */

export function queryMockInterfaceDetail(data) {
  return request({
    url: '/atp/mock/config/interface/detail',
    method: 'post',
    data
  })
}
