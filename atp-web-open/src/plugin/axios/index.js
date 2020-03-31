import axios from 'axios'
import { Message } from 'element-ui'
import util from '@/libs/util'
import router from '@/router'
// import store from '@/store/index'

// 创建一个错误
function errorCreat(msg) {
  const err = new Error(msg)
  errorLog(err)
  throw err
}

// 记录和显示错误
function errorLog(err) {
  // 打印到控制台
  if (process.env.NODE_ENV === 'development') {
    // console.log(err)
  }
  // 显示提示
  Message({
    message: err.message,
    type: 'error',
    duration: 5 * 1000
  })
}

// 创建一个 axios 实例
const service = axios.create({
  baseURL: process.env.VUE_APP_API,
  timeout: 50000 // 请求超时时间
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 在请求发送之前做一些处理
    if (!(/^https:\/\/|http:\/\//.test(config.url))) {
      const token = util.cookies.get('token')
      /* const cliIp = store.getters['d2admin/ua/ip']
      // 让每个请求携带客户端IP
      config.headers['X-IP'] = cliIp*/
      if (token && token !== 'undefined') {
        // 让每个请求携带token-- ['X-Token']为自定义key 请根据实际情况自行修改
        config.headers['X-Token'] = token
      }
    }
    return config
  },
  error => {
    // 发送失败
    //     console.log(error)
    Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    // dataAxios 是 axios 返回数据中的 data
    const dataAxios = response.data
    // 这个状态码是和后端约定的
    const { code } = dataAxios
    // 判断如果是mock测试url，直接返回mock接口，不对code进行判断
    if (response.config.url.indexOf('/mock/service/') !== -1) {
      return dataAxios
    }
    // 根据 code 进行判断
    if (code === undefined) {
      // 如果没有 code 代表这不是项目后端开发的接口 比如可能是 D2Admin 请求最新版本
      return dataAxios
    } else {
      // 有 code 代表这是一个后端接口 可以进行进一步的判断
      switch (code) {
        case '000':
          // code === 000 代表没有错误
          return dataAxios
        case '320':
          // code === 320 代表没有错误（查询测试用例运行报告专用错误码）
          return dataAxios
        case '330':
          // code === 330 代表没有错误（查询测试用例运行报告专用错误码）
          return dataAxios
        case '101':
          return dataAxios
        case 'xxx':
          // [ 示例 ] 其它和后台约定的 code
          errorCreat(`[ code: xxx ] ${dataAxios.desc}: ${response.config.url}`)
          break
        case '110':
          // 删除cookie
          util.cookies.remove('token')
          util.cookies.remove('uuid')
          router.push({
            name: 'login'
          })
          // errorCreat('会话超时，请重新登录')
          // errorCreat(`${dataAxios.desc}: ${response.config.url}`)
          break
        default:
          // 不是正确的 code
          errorCreat(`${dataAxios.desc}: ${response.config.url}`)
          break
      }
    }
  },
  error => {
    if (error && error.response) {
      switch (error.response.status) {
        case 400:
          error.message = '请求错误'
          break
        case 401:
          error.message = '未授权，请登录'
          break
        case 403:
          error.message = '拒绝访问'
          break
        case 404:
          error.message = `请求地址出错: ${error.response.config.url}`
          break
        case 408:
          error.message = '请求超时'
          break
        case 500:
          error.message = '服务器内部错误'
          break
        case 501:
          error.message = '服务未实现'
          break
        case 502:
          error.message = '网关错误'
          break
        case 503:
          error.message = '服务不可用'
          break
        case 504:
          error.message = '网关超时'
          break
        case 505:
          error.message = 'HTTP版本不受支持'
          break
        default:
          break
      }
    }
    errorLog(error)
    return Promise.reject(error)
  }
)

export default service
