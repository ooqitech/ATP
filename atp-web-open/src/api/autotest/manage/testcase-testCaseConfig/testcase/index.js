import request from '@/plugin/axios'

/**
 * 查询已支持的变量列表
 */

export function queryVariables(data) {
  return request({
    url: '/atp/auto/publicvariable/queryvariables',
    method: 'post',
    data
  })
}

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
 * 新增用例
 */

export function addTestCase(data) {
  return request({
    url: '/atp/auto/testcase/add',
    method: 'post',
    data
  })
}

/**
 * 复制用例
 */

export function copyTestCase(data) {
  return request({
    url: '/atp/auto/testcase/copy',
    method: 'post',
    data
  })
}

/**
 * 复制用例数据结构，(不复制用例名称)
 */

export function copyTestCaseData(data) {
  return request({
    url: '/atp/auto/testcase/copyBytestcaseData',
    method: 'post',
    data
  })
}

/**
 * 修改用例
 */

export function editTestCase(data) {
  return request({
    url: '/atp/auto/testcase/edit',
    method: 'post',
    data
  })
}

/**
 * 删除用例
 */

export function deleteTestCase(data) {
  return request({
    url: '/atp/auto/testcase/delete',
    method: 'post',
    data
  })
}

/**
 * 上升用例
 */

export function upTestCase(data) {
  return request({
    url: '/atp/auto/testcase/up',
    method: 'post',
    data
  })
}

/**
 * 下降用例
 */

export function downTestCase(data) {
  return request({
    url: '/atp/auto/testcase/down',
    method: 'post',
    data
  })
}

/**
 * 更新用例状态
 */

export function changeTestCaseStatus(data) {
  return request({
    url: '/atp/auto/testcase/changeStatus',
    method: 'post',
    data
  })
}

/**
 * 查询用例调用链
 */

export function queryTestCaseChain(data) {
  return request({
    url: '/atp/auto/testcase/queryByCallchain',
    method: 'post',
    data
  })
}

/**
 * 查询用例详情
 */

export function queryTestCaseDetail(data) {
  return request({
    url: '/atp/auto/testcase/detail',
    method: 'post',
    data
  })
}

/**
 * 根据测试集ID查询接口测试用例列表
 */

export function queryByTestsuiteId(data) {
  return request({
    url: '/atp/auto/testcase/queryByTestsuiteId',
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

/**
 * 设置标签
 */

export function setTags(data) {
  return request({
    url: '/atp/auto/testcase/setTag',
    method: 'post',
    data
  })
}
/**
 * 根据模块Id查询模块下的业务用例列表
 */

export function queryCaseListByModuleId(data) {
  return request({
    url: '/atp/auto/testcase/queryByModuleId',
    method: 'post',
    data
  })
}

/**
 * 查询业务用例详情
 */
export function detailBaseCase(data) {
  return request({
    url: '/atp/auto/testcase/detailBaseCase',
    method: 'post',
    data
  })
}

/**
 * 根据模块Id查询模块下的UI自动化用例列表
 */

export function queryUiCaseListByModuleId(data) {
  return request({
    url: '/atp/auto/testcase/queryUiCaseByModuleId',
    method: 'post',
    data
  })
}

/**
 * ui自动化用例详情
 */
export function detailUiTestCase(data) {
  return request({
    url: '/atp/auto/testcase/detailUiTestCase',
    method: 'post',
    data
  })
}

/**
 * 新增ui自动化用例
 */
export function addUiTestCase(data) {
  return request({
    url: '/atp/auto/uitestcase/add',
    method: 'post',
    data
  })
}

/**
 * 编辑ui自动化用例
 */
export function editUiTestCase(data) {
  return request({
    url: '/atp/auto/uitestcase/edit',
    method: 'post',
    data
  })
}

/**
 * 删除ui自动化用例
 */
export function deleteUiTestCase(data) {
  return request({
    url: '/atp/auto/uitestcase/delete',
    method: 'post',
    data
  })
}

/**
 * 移动用例
 */

export function changeSuiteParent(data) {
  return request({
    url: '/atp/auto/testcase/changeParent',
    method: 'post',
    data
  })
}
