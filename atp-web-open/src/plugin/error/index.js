export default {
  install(Vue, options) {
    Vue.config.errorHandler = function (err, vm, info) {
      Vue.nextTick(() => {
        // 只在开发模式下打印 log
        if (process.env.NODE_ENV === 'development') {
          console.log(info)
          console.log(vm)
          console.log(err)
        }
      })
    }
  }
}
