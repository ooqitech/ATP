export default {
  namespaced: true,
  state: {
    // 测试报告信息
    info: {}
  },
  actions: {
    setReportId({ commit }) {
      commit('load')
    }
  },
  mutations: {
    // 存储测试报告信息
    set(state, info) {
      // store 赋值
      state.info = info
      // 持久化
      this.dispatch('d2admin/db/set', {
        dbName: 'sys',
        path: 'report.info',
        value: state.info,
        user: true
      })
    },
    // 读取测试报告信息
    async load(state) {
      // store 赋值
      state.info = await this.dispatch('d2admin/db/get', {
        dbName: 'sys',
        path: 'report.info',
        defaultValue: {},
        user: true
      })
    }
  }
}
