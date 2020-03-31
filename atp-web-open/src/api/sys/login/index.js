import request from '@/plugin/axios'
/**
 * 登录接口
 */
export function AccountLogin(data) {
  return request({
    url: '/atp/auto/user/login',
    method: 'post',
    data
  })
}

/**
 * 登出接口
 */
export function AccountLogout(data) {
  return request({
    url: '/atp/auto/user/logout',
    method: 'post',
    data
  })
}
