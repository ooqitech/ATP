import request from '@/plugin/axios'
/**
 * 新增task
 */

export function addTask(data) {
  return request({
    url: '/atp/auto/apiTask/add',
    method: 'post',
    data
  })
}
/**
 * 编辑task
 */

export function editTask(data) {
  return request({
    url: '/atp/auto/apiTask/edit',
    method: 'post',
    data
  })
}
/**
 * 删除task
 */

export function deleteTask(data) {
  return request({
    url: '/atp/auto/apiTask/delete',
    method: 'post',
    data
  })
}
/**
 * 运行task
 */

export function runTask(data) {
  return request({
    url: '/atp/auto/apiTask/run',
    method: 'post',
    data
  })
}

/**
 * task详情
 */

export function detailTask(data) {
  return request({
    url: '/atp/auto/apiTask/detail',
    method: 'post',
    data
  })
}

/**
 * 查询任务列表
 */

export function listTask(data) {
  return request({
    url: '/atp/auto/apiTask/list',
    method: 'post',
    data
  })
}

/**
 * 查询任务进度
 */

export function getProgress(data) {
  return request({
    url: '/atp/auto/apiTask/getProgress',
    method: 'post',
    data
  })
}

/**
 * 获取任务运行历史列表
 */

export function runHistory(data) {
  return request({
    url: '/atp/auto/apiTask/runHistory',
    method: 'post',
    data
  })
}

/**
 * 获取任务未覆盖的接口信息
 */

export function getUncoveredInfo(data) {
  return request({
    url: '/atp/auto/apiTask/getUncoveredInfo',
    method: 'post',
    data
  })
}

/**
 * 标签列表
 */

export function listForTask(data) {
  return request({
    url: '/atp/auto/tag/listForTask',
    method: 'post',
    data
  })
}

/**
 * 重新触发收集测试结果
 */

export function reCollectTaskResult(data) {
  return request({
    url: '/atp/auto/apiTask/reCollectTaskResult',
    method: 'post',
    data
  })
}
