import UaParser from 'ua-parser-js'
// import {getIPs} from '@/libs/common'

export default {
  namespaced: true,
  state: {
    // 用户 UA
    data: {},
    ip: '0.0.0.0'
  },
  getters: {
    ip: state => state.ip
  },
  mutations: {
    /**
     * @description 记录 UA
     * @param {Object} state vuex state
     */
    get(state) {
      state.data = new UaParser().getResult()
      /* getIPs(function(ip){
          state.ip = ip
      })*/
    }
  }
}
