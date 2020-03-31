export default {
  namespaced: true,
  state: {
    // 用例列表数据
    caseTable: {
      projectId: '',
      // systemId: '',
      // moduleId: '',
      intfId: '',
      searchKeywords: '',
      testcaseId: '',
      id: 0
    },
    // 业务用例列表数据
    featureCaseTable: {
      systemId: '',
      moduleId: '',
      searchKeywords: ''

    },
    // UI用例表数据
    uiCaseTable: {
      systemId: '',
      moduleId: ''
    },
    // 页面对象表数据
    pageObjectTable: {
      systemId: '',
      pageId: ''
    },
    // 是否点击添加测试用例菜单
    addCaseVisible: false,

    // 添加UI自动化用例
    addUiCaseVisible: false,

    // UI运行环境配置
    uiRunEnvForm: {
      remoteUrl: ''
    },
    // 公共变量数据
    PublicVariabletableData: [],
    baseTable: {
      companyId: 1
    }
  },

  getters: {
    PublicVariabletableData: state => state.PublicVariabletableData
  },
  // 用例树上切换不同节点，展示相应的用例数据
  mutations: {
    changeCaseTableStatus(state, caseTableInfo) {
      state.caseTable = {
        projectId: caseTableInfo.projectId,
        // systemId: caseTableInfo.systemId,
        // moduleId: caseTableInfo.moduleId,
        intfId: caseTableInfo.intfId,
        testcaseId: caseTableInfo.testcaseId,
        id: caseTableInfo.id
      }
    },
    // 业务用例
    changeFeatureCaseTableStatus(state, featureCaseTable) {
      state.featureCaseTable = {
        systemId: featureCaseTable.systemId,
        moduleId: featureCaseTable.moduleId
      }
    },
    // Ui用例
    changeUiCaseTableStatus(state, uiCaseTable) {
      state.uiCaseTable = {
        systemId: uiCaseTable.systemId,
        moduleId: uiCaseTable.moduleId
      }
    },
    // 页面对象
    changePageObjectTableStatus(state, pageObjectTable) {
      state.pageObjectTable = {
        systemId: pageObjectTable.systemId,
        pageId: pageObjectTable.pageId
      }
    },
    addCase(state, addCaseVisible) {
      state.addCaseVisible = addCaseVisible
    },

    addUiCase(state, addUiCaseVisible) {
      state.addUiCaseVisible = addUiCaseVisible
    },

    // 同步UI自动化环境配置
    setUiRunEnv(state, envForm) {
      state.uiRunEnvForm = {
        remoteUrl: envForm.remoteUrl
      }
    },

    // 同步公共变量列表数据至state
    setPublicVariable(state, tabledata) {
      state.PublicVariabletableData = tabledata
    },

    changeCompanyId(state, companyId) {
      state.baseTable = {
        companyId: companyId
      }
    }
  }
}
