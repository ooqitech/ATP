export default {
  namespaced: true,
  state: {

    // 业务用例列表数据
    interfaceTable: {
      interfaceId: '',
      id: 0
    },
    // 是否点击添加测试用例菜单
    addCaseVisible: false
  },

  // getters: {
  //   // PublicVariabletableData: state => state.PublicVariabletableData
  // },
  // 用例树上切换不同节点，展示相应的用例数据
  mutations: {
    changeInterfaceTableStatus(state, interfaceIdTable) {
      state.interfaceTable = {
        interfaceId: interfaceIdTable.interfaceId
      }
    },
    addCase(state, addCaseVisible) {
      state.addCaseVisible = addCaseVisible
    }
  }
}
