import request from '@/plugin/axios'
/**
 * 获取自动化用例统计数据
 */

export function testcaseSummary(data) {
  return request({
    url: '/atp/auto/stat/testcaseSummary',
    method: 'post',
    data
  })
}
