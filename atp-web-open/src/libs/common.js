/**
 * 对象数组根据key值排序
 */

export function keysrt(key, desc) {
  return function (a, b) {
    return desc ? ~~(a[key] < b[key]) : ~~(a[key] > b[key])
  }
}

export function compare(propertyName) {
  return function (obj1, obj2) {
    var value1 = obj1[propertyName]
    var value2 = obj2[propertyName]
    return value1.localeCompare(value2)
  }
}

/**
 * 判断是否为json字符串
 */
export function isJsonString(str) {
  try {
    if (typeof JSON.parse(str) === 'object') {
      return true
    }
  } catch (e) {
    return false
  }
  return false
}

/**
 * 获取客户端IP
 */
export function getIPs(callback) {
  // 创建RTCPeerConnection接口
  let conn = new RTCPeerConnection({
    iceServers: []
  })
  let noop = function () {
  }
  conn.onicecandidate = function (ice) {
    if (ice.candidate) {
      // 使用正则获取ip
      let ipRegex = /([0-9]{1,3}(\.[0-9]{1,3}){3}|[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7})/
      let ipAddr = ipRegex.exec(ice.candidate.candidate)[1]
      callback(ipAddr)
      conn.onicecandidate = noop
    }
  }
  // 随便创建一个叫狗的通道(channel)
  conn.createDataChannel('dog')
  // 创建一个SDP协议请求
  conn.createOffer(conn.setLocalDescription.bind(conn), noop)
}

/**
 * 一些常用的正则规则
 */
const arrExp = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2] // 加权因子
const arrValid = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2'] // 校验码

export const regObj = {
  'chsName': /^[\u4E00-\u9FFF]([\u4E00-\u9FFF]{0,3})[\u4E00-\u9FFF]$/, // 2-5汉字
  'vCode4': /^\d(\d{2})\d$/, // 4位验证码
  'vCode6': /^\d(\d{4})\d$/, // 6位验证码
  'mobile': /^1\d{10}$/, // 通用手机号
  'email': /^(\S+)*@(\S)+((\.\S+)+)$/, // 邮箱
  'amount': /^(-)?(([1-9]{1}\d{0,4})|([0]{1}))(\.(\d){1,2})?$/, // 金额
  'url': /(http|https):\/\/([\w.]+\/?)\S*/ // 通用url
}

export const regFunc = {
  idNum: (cid) => {
    if (/^\d{17}(\d|x|X)$/i.test(cid)) {
      let sum = 0
      let idx = 0
      for (var i = 0; i < cid.length - 1; i++) {
        // 对前17位数字与权值乘积求和
        sum += parseInt(cid.substr(i, 1), 10) * arrExp[i]
      }
      // 计算模（固定算法）
      idx = sum % 11
      // 检验第18为是否与校验码相等
      return arrValid[idx] === cid.substr(17, 1).toUpperCase()
    } else if (/^[1-9]\d{7}((0[1-9])|(1[0-2]))((0[1-9])|([1-2][0-9])|(3[0-1]))\d{3}$/.test(cid)) {
      return true
    } else {
      return false
    }
  }
}

/**
 * 日期格式化
 */

let date = null
let offSet = 60 * 1000 * (new Date(0)).getTimezoneOffset()
let week = {
  '0': '日',
  '1': '一',
  '2': '二',
  '3': '三',
  '4': '四',
  '5': '五',
  '6': '六'
}

export const dateFormatter = (datetime, fmt) => {
  date = new Date(datetime + offSet)
  let o = {
    'M+': date.getMonth() + 1, // 月份
    'd+': date.getDate(), // 日
    'h+': (date.getHours() % 12) === 0 ? 12 : (date.getHours() % 12), // 小时
    'H+': date.getHours(), // 小时
    'm+': date.getMinutes(), // 分
    's+': date.getSeconds(), // 秒
    'q+': Math.floor((date.getMonth() + 3) / 3), // 季度
    'S': date.getMilliseconds() // 毫秒
  }
  if (/(y+)/.test(fmt)) {
    fmt = fmt.replace(RegExp.$1, (date.getFullYear() + '').substr(4 - RegExp.$1.length))
  }
  if (/(E+)/.test(fmt)) {
    fmt = fmt.replace(RegExp.$1, ((RegExp.$1.length > 1) ? (RegExp.$1.length > 2 ? '星期' : '周') : '') + week[date.getDay() + ''])
  }
  for (var k in o) {
    if (new RegExp('(' + k + ')').test(fmt)) {
      fmt = fmt.replace(RegExp.$1, (RegExp.$1.length === 1) ? (o[k]) : (('00' + o[k]).substr(('' + o[k]).length)))
    }
  }
  return fmt
}

/**
 * 数组对象按指定属性排序
 */
export const sortListByItem = (item) => {
  return function (s1, s2) {
    let x1 = s1[item].toUpperCase()
    let x2 = s2[item].toUpperCase()
    if (x1 < x2) {
      return -1
    } else {
      return 0
    }
  }
}

export const debounce = (func, wait, immediate) => {
  let timeout, args, context, timestamp

  const later = function () {
    // 据上一次触发时间间隔
    const last = +new Date() - timestamp

    // 上次被包装函数被调用时间间隔last小于设定时间间隔wait
    if (last < wait && last > 0) {
      timeout = setTimeout(later, wait - last)
    } else {
      timeout = null
      // 如果设定为immediate===true，因为开始边界已经调用过了此处无需调用
      if (!immediate) {
        func.apply(context, args)
        if (!timeout) context = args = null
      }
    }
  }
}

/* 数组排序（元素为数字）*/
export const sortNumber = (a, b) => {
  return a - b
}

/* json格式化 */
export const getFormatJsonStrFromString = (jsonStr) => {
  var res = ''
  for (var i = 0, j = 0, k = 0, ii, ele; i < jsonStr.length; i++) { // k:缩进，j:""个数
    ele = jsonStr.charAt(i)
    if (j % 2 === 0 && ele === '}') {
      k--
      for (ii = 0; ii < k; ii++) ele = '    ' + ele
      ele = '\n' + ele
    } else if (j % 2 === 0 && ele === '{') {
      ele += '\n'
      k++
      for (ii = 0; ii < k; ii++) ele += '    '
    } else if (j % 2 === 0 && ele === ',') {
      ele += '\n'
      for (ii = 0; ii < k; ii++) ele += '    '
    } else if (ele === '"') j++
    res += ele
  }
  return res
}
