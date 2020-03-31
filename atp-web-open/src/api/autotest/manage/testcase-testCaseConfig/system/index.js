import request from '@/plugin/axios'

/**
 * 添加系统
 */

export function addSystem(data) {
  return request({
    url: '/atp/auto/system/add',
    method: 'post',
    data
  })
}

/**
 * 修改系统
 */

export function editSystem(data) {
  return request({
    url: '/atp/auto/system/edit',
    method: 'post',
    data
  })
}

/**
 * 删除系统
 */

export function deleteSystem(data) {
  return request({
    url: '/atp/auto/system/delete',
    method: 'post',
    data
  })
}

/**
 * 查询系统
 */

export function querySystem(data) {
  return request({
    url: '/atp/auto/system/detail',
    method: 'post',
    data
  })
}

/**
 * 上升系统
 */

export function upSystem(data) {
  return request({
    url: '/atp/auto/system/up',
    method: 'post',
    data
  })
}

/**
 * 下降系统
 */

export function downSystem(data) {
  return request({
    url: '/atp/auto/system/down',
    method: 'post',
    data
  })
}

/**
 * 根据项目ID查询系统
 */

export function queryByProjectId(data) {
  return request({
    url: '/atp/auto/system/queryByProjectId',
    method: 'post',
    data
  })
}

/**
 * 导出系统基线用例生成xmind
 */

export function exportSystemCase(data) {
  return request({
    url: '/atp/auto/download/xmindBase',
    method: 'post',
    data
  })
}

/**
 * 根据系统id:导出系统基线用例生成excel
 */

export function exportSystemCaseExcel(data) {
  return request({
    url: '/atp/auto/download/excel',
    method: 'post',
    data
  })
}

/**
 * 根据模块id列表：导出系统基线用例生成excel
 */

export function exportModulesCaseExcel(data) {
  return request({
    url: '/atp/auto/download/excelModules',
    method: 'post',
    data
  })
}

/**
 * 同步git最新基线用例
 */

export function syncBaselineCase(data) {
  return request({
    url: '/atp/auto/support/syncBaseline',
    method: 'post',
    data
  })
}

/**
 * 配置系统url/远程url
 */

export function addSystemUrl(data) {
  return request({
    url: '/atp/auto/system/addUrl',
    method: 'post',
    data
  })
}
/**
 * 系统url/远程url详情
 */

export function systemConfigDetail(data) {
  return request({
    url: '/atp/auto/system/config_detail',
    method: 'post',
    data
  })
}
