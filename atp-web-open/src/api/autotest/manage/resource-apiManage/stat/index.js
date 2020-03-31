import request from '@/plugin/axios'

/**
 * 统计接口用例数
 */

export function getStatistics(data) {
  return request({
    url: '/atp/auto/stat/getStatistics',
    method: 'post',
    data
  })
}

