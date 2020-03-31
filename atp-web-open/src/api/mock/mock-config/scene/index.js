import request from '@/plugin/axios'

/**
 * 新增mock场景
 */

export function addMockScene(data) {
  return request({
    url: '/atp/mock/config/scene/add',
    method: 'post',
    data
  })
}

/**
 * 修改mock场景
 */

export function editMockScene(data) {
  return request({
    url: '/atp/mock/config/scene/edit',
    method: 'post',
    data
  })
}

/**
 * 删除已配置的mock接口
 */

export function deleteMock(data) {
  return request({
    url: '/atp/mock/config/scene/delete',
    method: 'post',
    data
  })
}

/**
 * 查询已配置的mock接口详情
 */

export function queryMockDetails(data) {
  return request({
    url: '/atp/mock/config/scene/query',
    method: 'post',
    data
  })
}

/**
 * 测试已配置的mock接口
 */

export function testMockPost(data) {
  let body = data.requestBody
  let headers = {
    'Content-Type': data.contentType,
    'Access-Control-Allow-Origin': '*'
  }
  return request({
    url: `/mock/service/${data.projectName}/${data.interfaceName}`,
    method: 'post',
    data: body,
    headers
  })
}

export function testMockGet(data) {
  let url = data.requestBody
  return request({
    url: `/mock/service/${data.projectName}/${data.interfaceName}` + '?' + url,
    method: 'get'
  })
}
