import request from '@/plugin/axios'

/**
 * 添加环境
 */

export function addEnv(data) {
  return request({
    url: '/atp/auto/env/add',
    method: 'post',
    data
  })
}

/**
 * 修改环境
 */

export function editEnv(data) {
  return request({
    url: '/atp/auto/env/edit',
    method: 'post',
    data
  })
}

/**
 * 删除环境
 */

export function deleteEnv(data) {
  return request({
    url: '/atp/auto/env/delete',
    method: 'post',
    data
  })
}

/**
 * 获取环境列表
 */

export function fetchEnvList(data) {
  return request({
    url: '/atp/auto/env/list',
    method: 'post',
    data
  })
}
