import request from '@/plugin/axios'
/**
 * 获取用户列表
 */

export function getUserInfo(data) {
  return request({
    url: '/atp/auto/user/detail',
    method: 'post',
    data
  })
}

export function fetchUsertList(data) {
  return request({
    url: '/atp/auto/user/list',
    method: 'post',
    data
  })
}

// 新增用户
export function addUser(data) {
  return request({
    url: '/atp/auto/user/add',
    method: 'post',
    data
  })
}

// 删除用户
export function deleteUser(data) {
  return request({
    url: '/atp/auto/user/delete',
    method: 'post',
    data
  })
}

// 重置密码
export function resetUserPassword(data) {
  return request({
    url: '/atp/auto/user/resetPassword',
    method: 'post',
    data
  })
}

// 修改密码
export function changeUserPassword(data) {
  return request({
    url: '/atp/auto/user/changePassword',
    method: 'post',
    data
  })
}
