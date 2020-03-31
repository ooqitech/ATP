import request from '@/plugin/axios'
/**
 * 获取加价策略数据
 */

export function queryFareIncreaseServiceConfig(data) {
  return request({
    url: '/atp/qa/queryFareIncreaseServiceConfig',
    method: 'post',
    data
  })
}

/**
 * 获取加价策略字段字典
 */

export function getFareIncreaseServiceMappingList(data) {
  return request({
    url: '/atp/qa/getFareIncreaseServiceMappingList',
    method: 'post',
    data
  })
}

/**
 * 配置现金贷加价策略
 */

export function setCashLoanConfig(data) {
  return request({
    url: '/atp/qa/setCashLoanConfig',
    method: 'post',
    data
  })
}

/**
 * 配置大额首单现金贷加价策略
 */

export function setBigFirstOrderConfig(data) {
  return request({
    url: '/atp/qa/setBigFirstOrderConfig',
    method: 'post',
    data
  })
}

/**
 * 配置不等贷加价策略
 */

export function setNoWaitLoanConfig(data) {
  return request({
    url: '/atp/qa/setNoWaitLoanConfig',
    method: 'post',
    data
  })
}

/**
 * 配置医美加价策略
 */

export function setMedicalConfig(data) {
  return request({
    url: '/atp/qa/setMedicalConfig',
    method: 'post',
    data
  })
}
