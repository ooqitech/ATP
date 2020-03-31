import request from '@/plugin/axios'
/**
 * 获取系统实时状态
 */

export function getSystemStatus(data) {
  return request({
    url: '/atp/monitor/businessStatus/list',
    method: 'post',
    data
  })
}

/**
 * 重启故障系统
 */

export function rebootSystem(data) {
  return request({
    url: '/atp/monitor/businessStatus/reboot',
    method: 'post',
    data
  })
}

/**
 * 获取最近一次系统状态
 */

export function getLastStatus(data) {
  return request({
    url: '/atp/monitor/businessStatus/getLastStatus',
    method: 'post',
    data
  })
}

/**
 * 获取当前所有历史监控记录
 */

export function getCurrentDayHis(data) {
  return request({
    url: '/atp/monitor/businessStatus/getCurrentDayHis',
    method: 'post',
    data
  })
}
