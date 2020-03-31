import request from '@/plugin/axios'

/**
 * 获取项目列表
 */

export function fetchProjectList(data) {
  return request({
    url: '/atp/auto/project/list',
    method: 'post',
    data
  })
}

/**
 * 添加项目
 */

export function addProject(data) {
  return request({
    url: '/atp/auto/project/add',
    method: 'post',
    data
  })
}

/**
 * 修改项目
 */

export function editProject(data) {
  return request({
    url: '/atp/auto/project/edit',
    method: 'post',
    data
  })
}

/**
 * 删除项目
 */

export function deleteProject(data) {
  return request({
    url: '/atp/auto/project/delete',
    method: 'post',
    data
  })
}

/**
 * 查询项目下所有系统、模块和接口
 */

export function subtreeProject(data) {
  return request({
    url: '/atp/auto/project/subtree',
    method: 'post',
    data
  })
}

/**
 * 查询项目下所有系统、模块、接口、用例
 */

export function subtreeProjectWithCase(data) {
  return request({
    url: '/atp/auto/project/subtreeWithCase',
    method: 'post',
    data
  })
}

/**
 * 查询业务项目list
 */

export function fetchBaseProjectList(data) {
  return request({
    url: '/atp/auto/project/baseList',
    method: 'post',
    data
  })
}
/**
 * 查询UI项目list
 */

export function fetchUiProjectList(data) {
  return request({
    url: '/atp/auto/project/uiList',
    method: 'post',
    data
  })
}

/**
 * 查询业务项目下所有系统、模块1~n
 */

export function subtreeBaseProject(data) {
  return request({
    url: '/atp/auto/project/baseSubtree',
    method: 'post',
    data
  })
}

/**
 * 查询业务项目下所有系统、模块1~n
 */

export function subtreeUiProject(data) {
  return request({
    url: '/atp/auto/project/uiSubtree',
    method: 'post',
    data
  })
}

/**
 * UI自动化：查询系统下所有页面tree
 */

export function subtreePage(data) {
  return request({
    url: '/atp/auto/project/pageSubtree',
    method: 'post',
    data
  })
}

/**
 * 新版本：项目新增
 */

export function addApiProject(data) {
  return request({
    url: '/atp/auto/apiProject/add',
    method: 'post',
    data
  })
}

/**
 * 新版本：项目编辑
 */

export function editApiProject(data) {
  return request({
    url: '/atp/auto/apiProject/edit',
    method: 'post',
    data
  })
}

/**
 * 新版本：项目删除
 */

export function deleteApiProject(data) {
  return request({
    url: '/atp/auto/apiProject/delete',
    method: 'post',
    data
  })
}

/**
 * 新版本：项目引入工程
 */

export function introduceSystem(data) {
  return request({
    url: '/atp/auto/apiProject/includeSystem',
    method: 'post',
    data
  })
}

/**
 * 新版本：项目引入接口
 */

export function introduceInterface(data) {
  return request({
    url: '/atp/auto/apiProject/includeIntf',
    method: 'post',
    data
  })
}

/**
 * 新版本：排除项目已经引入的系统
 */

export function excludeSystem(data) {
  return request({
    url: '/atp/auto/apiProject/excludeSystem',
    method: 'post',
    data
  })
}

/**
 * 新版本：排除项目已经引入的系统
 */

export function excludeIntf(data) {
  return request({
    url: '/atp/auto/apiProject/excludeIntf',
    method: 'post',
    data
  })
}
