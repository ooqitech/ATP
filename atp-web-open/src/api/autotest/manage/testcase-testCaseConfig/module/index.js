import request from '@/plugin/axios'

/**
 * 添加模块
 */

export function addModule(data) {
  return request({
    url: '/atp/auto/module/add',
    method: 'post',
    data
  })
}

/**
 * 修改模块
 */

export function editModule(data) {
  return request({
    url: '/atp/auto/module/edit',
    method: 'post',
    data
  })
}

/**
 * 删除模块
 */

export function deleteModule(data) {
  return request({
    url: '/atp/auto/module/delete',
    method: 'post',
    data
  })
}

/**
 * 根据系统ID查询模块
 */

export function queryBySystemId(data) {
  return request({
    url: '/atp/auto/module/queryBySystemId',
    method: 'post',
    data
  })
}

/**
 * 导出模块的用例生成xmind
 */

export function exportMoudleCase(data) {
  return request({
    url: '/atp/auto/download/xmindApi',
    method: 'post',
    data
  })
}

/**
 * 查询模块
 */

export function queryModule(data) {
  return request({
    url: '/atp/auto/module/detail',
    method: 'post',
    data
  })
}

/**
 * 移动模块
 */

export function changeSystemParent(data) {
  return request({
    url: '/atp/auto/module/changeParent',
    method: 'post',
    data
  })
}
