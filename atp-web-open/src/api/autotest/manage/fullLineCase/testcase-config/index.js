import request from '@/plugin/axios'
/**
 * 新增用例
 */

export function addFullLineCase(data) {
  return request({
    url: '/atp/auto/apiTestcaseMain/add',
    method: 'post',
    data
  })
}

/**
 * 修改用例
 */

export function editFullLineCase(data) {
  return request({
    url: '/atp/auto/apiTestcaseMain/edit',
    method: 'post',
    data
  })
}

/**
 * 删除用例
 */

export function deleteFullLineCase(data) {
  return request({
    url: '/atp/auto/apiTestcaseMain/delete',
    method: 'post',
    data
  })
}

/**
 * 查询用例详情
 */

export function queryFullLineCaseDetail(data) {
  return request({
    url: '/atp/auto/apiTestcaseMain/detail',
    method: 'post',
    data
  })
}

/**
 * 根据产品线id查询用例列表
 */

export function queryCaseByProduceId(data) {
  return request({
    url: '/atp/auto/apiTestcaseMain/queryByProductLine',
    method: 'post',
    data
  })
}

/**
 * 拖拽子用例的顺序
 */

export function changeFullLineCaseParent(data) {
  return request({
    url: '/atp/auto/apiTestcaseMain/changeParent',
    method: 'post',
    data
  })
}

/**
 * 改变全链路用例的状态
 */

export function changeFullLineCaseStatus(data) {
  return request({
    url: '/atp/auto/apiTestcaseMain/changeStatus',
    method: 'post',
    data
  })
}

/**
 * 复制用例
 */

export function copyFullLineCase(data) {
  return request({
    url: '/atp/auto/apiTestcaseMain/copy',
    method: 'post',
    data
  })
}

/**
 * 设置标签
 */

export function setTags(data) {
  return request({
    url: '/atp/auto/apiTestcaseMain/setTag',
    method: 'post',
    data
  })
}

/**
 * 根据子用例查询关联的主用例列表
 */

export function getRelatedMainCaseBySubCaseId(data) {
  return request({
    url: '/atp/auto/apiTestcaseMain/queryRelatedCasesBySubId',
    method: 'post',
    data
  })
}

/**
 * 根据全链路用例id查询自定义链路信息
 */

export function getCustomFlows(data) {
  return request({
    url: '/atp/auto/apiTestcaseMain/getCustomFlows',
    method: 'post',
    data
  })
}

/**
 * 保存自定义链路
 */

export function saveCustomFlows(data) {
  return request({
    url: '/atp/auto/apiTestcaseMain/saveCustomFlows',
    method: 'post',
    data
  })
}
