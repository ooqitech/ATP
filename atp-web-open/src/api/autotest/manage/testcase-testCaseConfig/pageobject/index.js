import request from '@/plugin/axios'

/**
 * 添加页面
 */

export function addPage(data) {
  return request({
    url: '/atp/auto/page/add',
    method: 'post',
    data
  })
}

/**
 * 添加页面对象
 */

export function addPageElement(data) {
  return request({
    url: '/atp/auto/pageobject/add',
    method: 'post',
    data
  })
}

/**
 * 编辑页面对象
 */

export function editPageElement(data) {
  return request({
    url: '/atp/auto/pageobject/edit',
    method: 'post',
    data
  })
}

/**
 * 删除页面对象
 */

export function deletePageElement(data) {
  return request({
    url: '/atp/auto/pageobject/delete',
    method: 'post',
    data
  })
}

/**
 * 页面id，查询所以页面元素
 */

export function fetchPageElements(data) {
  return request({
    url: '/atp/auto/pageobject/queryByPageId',
    method: 'post',
    data
  })
}

/**
 * 系统id：查询所有页面
 */

export function fetchPageList(data) {
  return request({
    url: '/atp/auto/page/pageList',
    method: 'post',
    data
  })
}
