import request from '@/plugin/axios'
/**
 * 查询已支持的前置操作hooks函数
 */

export function queryCustomSetupHooks(data) {
  return request({
    url: '/atp/auto/support/queryCustomSetupHooks',
    method: 'post',
    data
  })
}

/**
 * 查询已支持的参数化变量类型
 */

export function querySupportVariableTypes(data) {
  return request({
    url: '/atp/auto/support/querySupportVariableTypes',
    method: 'post',
    data
  })
}

/**
 * 查询已支持的自定义变量函数
 */

export function queryCustomFunctions(data) {
  return request({
    url: '/atp/auto/support/queryCustomFunctions',
    method: 'post',
    data
  })
}

/**
 * 查询已支持的加签函数
 */

export function querySignFunctions(data) {
  return request({
    url: '/atp/auto/support/querySignFunctions',
    method: 'post',
    data
  })
}

/**
 * 查询已支持的断言类型
 */

export function queryCustomComparators(data) {
  return request({
    url: '/atp/auto/support/queryCustomComparators',
    method: 'post',
    data
  })
}

/**
 * 查询已支持的后置操作hooks函数
 */

export function queryCustomTeardownHooks(data) {
  return request({
    url: '/atp/auto/support/queryCustomTeardownHooks',
    method: 'post',
    data
  })
}

/**
 * 标签列表
 */

export function queryTagList(data) {
  return request({
    url: '/atp/auto/tag/list',
    method: 'post',
    data
  })
}
