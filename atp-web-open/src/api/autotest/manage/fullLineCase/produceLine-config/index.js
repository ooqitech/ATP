import request from '@/plugin/axios'

/**
 * 添加产品线
 */

export function addProductLine(data) {
  return request({
    url: '/atp/auto/apiProductLine/add',
    method: 'post',
    data
  })
}

/**
 * 删除产品线
 */

export function deleteProductLine(data) {
  return request({
    url: '/atp/auto/apiProductLine/delete',
    method: 'post',
    data
  })
}

/**
 * 编辑产品线
 */

export function editProductLine(data) {
  return request({
    url: '/atp/auto/apiProductLine/edit',
    method: 'post',
    data
  })
}

/**
 * 变更目录结构
 */

export function changeParent(data) {
  return request({
    url: '/atp/auto/apiProductLine/changeParent',
    method: 'post',
    data
  })
}

