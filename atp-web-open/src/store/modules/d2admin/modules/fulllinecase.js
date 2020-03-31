export default {
  namespaced: true,
  state: {
    // 全链路用例列表数据
    caseTable: {
      productLineId: '',
      testcaseId: '',
      id: 0
    },
    // 支持函数表数据
    supportTable: {
      supportSetupFuncs: [],
      supportVariableType: [],
      customVariableFunctions: [],
      supportSignFuncs: [],
      supportCustomComparators: [],
      supportTeardownFuncs: []
    },
    // 是否点击添加测试用例菜单
    addCaseVisible: false,
    baseTable: {
      companyId: 1
    }

  },
  getters: {
  },
  // 用例树上切换不同节点，展示相应的用例数据
  mutations: {
    changeFullLineCaseTable(state, caseTableInfo) {
      state.caseTable = {
        productLineId: caseTableInfo.productLineId,
        testcaseId: caseTableInfo.testcaseId,
        id: caseTableInfo.id
      }
    },
    changeSupportTable(state, supportTableInfo) {
      state.supportTable = {
        supportSetupFuncs: supportTableInfo.supportSetupFuncs,
        supportVariableType: supportTableInfo.supportVariableType,
        customVariableFunctions: supportTableInfo.customVariableFunctions,
        supportSignFuncs: supportTableInfo.supportSignFuncs,
        supportCustomComparators: supportTableInfo.supportCustomComparators,
        supportTeardownFuncs: supportTableInfo.supportTeardownFuncs
      }
    },
    addCase(state, addCaseVisible) {
      state.addCaseVisible = addCaseVisible
    },

    changeCompanyId(state, companyId) {
      state.baseTable = {
        companyId: companyId
      }
    }

  }
}
