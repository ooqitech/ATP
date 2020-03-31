import request from '@/plugin/axios'

/**
 * 用例新增
 */

export function addTestCase(data) {
  return request({
    url: '/atp/auto/apiTestcase/add',
    method: 'post',
    data
  })
}

/**
 * 用例编辑
 */

export function editTestCase(data) {
  return request({
    url: '/atp/auto/apiTestcase/edit',
    method: 'post',
    data
  })
}

/**
 * 用例删除
 */

export function deleteTestCase(data) {
  return request({
    url: '/atp/auto/apiTestcase/delete',
    method: 'post',
    data
  })
}

/**
 * 根据接口id 获取所有测试用例
 */

export function queryCaseByIntfId(data) {
  return request({
    url: '/atp/auto/apiTestcase/queryByIntfId',
    method: 'post',
    data
  })
}

/**
 * 复制用例
 */

export function copyTestCase(data) {
  return request({
    url: '/atp/auto/apiTestcase/copy',
    method: 'post',
    data
  })
}

/**
 * 复制用例数据结构，(不复制用例名称)
 */

export function copyTestCaseData(data) {
  return request({
    url: '/atp/auto/apiTestcase/copyBytestcaseData',
    method: 'post',
    data
  })
}

/**
 * 上升用例
 */

export function upTestCase(data) {
  return request({
    url: '/atp/auto/apiTestcase/up',
    method: 'post',
    data
  })
}

/**
 * 下降用例
 */

export function downTestCase(data) {
  return request({
    url: '/atp/auto/apiTestcase/down',
    method: 'post',
    data
  })
}

/**
 * 更新用例状态
 */

export function changeTestCaseStatus(data) {
  return request({
    url: '/atp/auto/apiTestcase/changeStatus',
    method: 'post',
    data
  })
}

/**
 * 查询用例调用链
 */

export function queryTestCaseChain(data) {
  return request({
    url: '/atp/auto/apiTestcase/queryByCallchain',
    method: 'post',
    data
  })
}

/**
 * 查询用例详情
 */

export function queryTestCaseDetail(data) {
  return request({
    url: '/atp/auto/apiTestcase/detail',
    method: 'post',
    data
  })
}

/**
 * 查询包含前置接口用例详情
 */

export function queryDetailWithSetup(data) {
  return request({
    url: '/atp/auto/apiTestcase/detailWithSetup',
    method: 'post',
    data
  })
}

/**
 * 设置标签
 */

export function setTags(data) {
  return request({
    url: '/atp/auto/apiTestcase/setTag',
    method: 'post',
    data
  })
}

/**
 * 移动用例
 */

export function changeSuiteParent(data) {
  return request({
    url: '/atp/auto/apiTestcase/changeParent',
    method: 'post',
    data
  })
}

/**
 * 导出用例生成xmind
 */

export function exportTestCase(data) {
  return request({
    url: '/atp/auto/download/xmindApi',
    method: 'post',
    data
  })
}

/**
 * 新版查询用例详情
 */

export function queryTestCaseMainDetail(data) {
  return request({
    url: '/atp/auto/apiTestcaseMain/detail',
    method: 'post',
    data
  })
}

/**
 * 新版根据接口id 获取所有测试用例
 */

export function queryCaseMainByIntfId(data) {
  return request({
    url: '/atp/auto/apiTestcaseMain/queryByIntfId',
    method: 'post',
    data
  })
}

/**
 * 根据接口用例id或全链路用例id获取被前置的用例列表
 */

export function queryListBySetupCase(data) {
  return request({
    url: '/atp/auto/apiTestcase/queryListBySetupCase',
    method: 'post',
    data
  })
}
