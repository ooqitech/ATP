import request from '@/plugin/axios'

/**
 * 根据公司id查询 公司下所有的项目
 */

export function queryProjectByCompanyId(data) {
  return request({
    url: '/atp/auto/apiProject/list',
    method: 'post',
    data
  })
}

/**
 * 根据项目id获取引入的接口列表
 */

export function getIncludeIntfList(data) {
  return request({
    url: '/atp/auto/apiProject/getIncludeIntfList',
    method: 'post',
    data
  })
}

/**
 * 根据项目id查询系统、接口、用例树
 */

export function getSubTreeByProjectId(data) {
  return request({
    url: '/atp/auto/apiProject/subtree',
    method: 'post',
    data
  })
}
