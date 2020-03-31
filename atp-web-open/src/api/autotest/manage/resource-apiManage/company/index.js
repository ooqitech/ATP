import request from '@/plugin/axios'
/**
 * 获取公司列表
 */

export function fetchCompanyList(data) {
  return request({
    url: '/atp/auto/apiCompany/list',
    method: 'post',
    data
  })
}

/**
 * 新增公司
 */

export function addCompany(data) {
  return request({
    url: '/atp/auto/apiCompany/add',
    method: 'post',
    data
  })
}

/**
 * 删除公司
 */

export function deleteCompany(data) {
  return request({
    url: '/atp/auto/apiCompany/delete',
    method: 'post',
    data
  })
}

/**
 * 编辑公司
 */

export function editCompany(data) {
  return request({
    url: '/atp/auto/apiCompany/edit',
    method: 'post',
    data
  })
}

/**
 * 公司id获取工程树结构
 */

export function subtree(data) {
  return request({
    url: '/atp/auto/apiCompany/subtree',
    method: 'post',
    data
  })
}

/**
 * 公司id获取项目树结构
 */

export function subtreeProject(data) {
  return request({
    url: '/atp/auto/apiCompany/projectSubtree',
    method: 'post',
    data
  })
}

/**
 * 公司id获取全链路用例树
 */

export function subtreeProductLine(data) {
  return request({
    url: '/atp/auto/apiCompany/productLineSubtree',
    method: 'post',
    data
  })
}

/**
 * 根据公司id查询，查询全链路用例可选择系统/接口/用例
 */

export function subtreeIntfCase(data) {
  return request({
    url: '/atp/auto/apiCompany/intfCaseSubtree',
    method: 'post',
    data
  })
}

/**
 * 获取用例查询条件
 */

export function getFilterConditions(data) {
  return request({
    url: '/atp/auto/apiCompany/getFilterConditions',
    method: 'post',
    data
  })
}

/**
 * 根据关键字查询用例
 */

export function subtreeFilter(data) {
  return request({
    url: '/atp/auto/apiCompany/subtreeFilter',
    method: 'post',
    data
  })
}
