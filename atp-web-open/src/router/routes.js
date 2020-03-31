// layout
import layoutHeaderAside from '@/layout/header-aside'

const meta = { requiresAuth: true, keepAlive: true }
/**
 * 在主框架内显示
 */
const frameIn = [
  {
    path: '/',
    redirect: { name: 'index' },
    component: layoutHeaderAside,
    children: [
      {
        path: 'index',
        name: 'index',
        meta,
        component: () => import('@/pages/index')
      }
    ]
  },
  {
    path: '/tools',
    name: 'tools',
    meta,
    redirect: { name: 'tools-tool-smsCodeQuery' },
    component: layoutHeaderAside,
    children: (pre => [
      {
        path: 'tool-smsCodeQuery',
        name: `${pre}tool-smsCodeQuery`,
        component: () => import('@/pages/tools/tool-smsCodeQuery'),
        meta: { ...meta, title: '查看验证码' }
      },
      {
        path: 'tool-dataClean',
        name: `${pre}tool-dataClean`,
        component: () => import('@/pages/tools/tool-dataClean'),
        meta: { ...meta, title: '数据清理' }
      },
      {
        path: 'tool-creditWhiteList',
        name: `${pre}tool-creditWhiteList`,
        component: () => import('@/pages/tools/tool-creditWhiteList'),
        meta: { ...meta, title: '征信白名单' }
      },
      {
        path: 'tool-creditAuditQuery',
        name: `${pre}tool-creditAuditQuery`,
        component: () => import('@/pages/tools/tool-creditAuditQuery'),
        meta: { ...meta, title: '征信审核结果查询' }
      },
      {
        path: 'tool-loanDataCalculate',
        name: `${pre}tool-loanDataCalculate`,
        component: () => import('@/pages/tools/tool-loanDataCalculate'),
        meta: { ...meta, title: '账务计算公式' }
      },
      {
        path: 'tool-loanTransfer',
        name: `${pre}tool-loanTransfer`,
        component: () => import('@/pages/tools/tool-loanTransfer'),
        meta: { ...meta, title: '一键放款' }
      },
      {
        path: 'tool-updateLogisticsInfo',
        name: `${pre}tool-updateLogisticsInfo`,
        component: () => import('@/pages/tools/tool-updateLogisticsInfo'),
        meta: { ...meta, title: '一键发货' }
      },
      {
        path: 'tool-batchGenerateCardNo',
        name: `${pre}tool-batchGenerateCardNo`,
        component: () => import('@/pages/tools/tool-batchGenerateCardNo'),
        meta: { ...meta, title: '一键生成银行卡号' }
      },
      {
        path: 'tool-xmindToExcel',
        name: `${pre}tool-xmindToExcel`,
        component: () => import('@/pages/tools/tool-xmindToExcel'),
        meta: { ...meta, title: 'xmind转excel' }
      },
      {
        path: 'tool-uaaLogDecrypt',
        name: `${pre}tool-uaaLogDecrypt`,
        component: () => import('@/pages/tools/tool-uaaLogDecrypt'),
        meta: { ...meta, title: '埋点日志解密' }
      },
      {
        path: 'tool-loanDateToOverDue',
        name: `${pre}tool-loanDateToOverDue`,
        component: () => import('@/pages/tools/tool-loanDateToOverDue'),
        meta: { ...meta, title: '构造账务逾期数据' }
      },
      {
        path: 'tool-loanDateToOverDueForCapitalHub',
        name: `${pre}tool-loanDateToOverDueForCapitalHub`,
        component: () => import('@/pages/tools/tool-loanDateToOverDueForCapitalHub'),
        meta: { ...meta, title: '构造账务逾期数据CH' }
      },
      {
        path: 'tool-loanDateToOverDueForDongFang',
        name: `${pre}tool-loanDateToOverDueForDongFang`,
        component: () => import('@/pages/tools/tool-loanDateToOverDueForDongFang'),
        meta: { ...meta, title: '构造东方逾期数据' }
      },
      {
        path: 'tool-loanTransferForDongFang',
        name: `${pre}tool-loanTransferForDongFang`,
        component: () => import('@/pages/tools/tool-loanTransferForDongFang'),
        meta: { ...meta, title: '一键放款' }
      },
      {
        path: 'tool-setMatchFund',
        name: `${pre}tool-setMatchFund`,
        component: () => import('@/pages/tools/tool-setMatchFund'),
        meta: { ...meta, title: '设置资方匹配规则' }
      },
      {
        path: 'tool-jsonTools',
        name: `${pre}tool-jsonTools`,
        component: () => import('@/pages/tools/tool-jsonTools'),
        meta: { ...meta, title: 'json工具集' }
      },
      {
        path: 'tool-sendMQ',
        name: `${pre}tool-sendMQ`,
        component: () => import('@/pages/tools/tool-sendMQ'),
        meta: { ...meta, title: '发送MQ' }
      },
      {
        path: 'tool-fareIncreaseService',
        name: `${pre}tool-fareIncreaseService`,
        component: () => import('@/pages/tools/tool-fareIncreaseService'),
        meta: { ...meta, title: '现金贷加价策略配置' }
      },
      {
        path: 'info-qrCodeApp',
        name: `${pre}info-qrCodeApp`,
        component: () => import('@/pages/tools/info-qrCodeApp'),
        meta: { ...meta, title: '客户端二维码' }
      },
      {
        path: 'info-hotLinksBaoSheng',
        name: `${pre}info-hotLinksBaoSheng`,
        component: () => import('@/pages/tools/info-hotLinksBaoSheng'),
        meta: { ...meta, title: '宝生系统导航' }
      }
    ])('tools-')
  },
  {
    path: '/autotest/manage',
    name: 'autotest-manage',
    meta,
    redirect: { name: 'autotest-manage-resource-projectManage' },
    component: layoutHeaderAside,
    children: (pre => [
      {
        path: 'resource-interfaceManage',
        name: `${pre}resource-interfaceManage`,
        component: () => import('@/pages/autotest/manage/resource-interfaceManage'),
        meta: { ...meta, title: '接口管理' }
      },
      {
        path: 'resource-envManage',
        name: `${pre}resource-envManage`,
        component: () => import('@/pages/autotest/manage/resource-envManage'),
        meta: { ...meta, title: '环境配置' }
      },
      {
        path: 'resource-publicVariable',
        name: `${pre}resource-publicVariable`,
        component: () => import('@/pages/autotest/manage/resource-publicVariable'),
        meta: { ...meta, title: '公共变量' }
      },

      {
        path: 'interface-testCaseConfig',
        name: `${pre}interface-testCaseConfig`,
        component: () => import('@/pages/autotest/manage/interface-testCaseConfig'),
        meta: { ...meta, title: '接口用例配置' }
      },
      {
        path: 'fullLine-testCaseConfig',
        name: `${pre}fullLine-testCaseConfig`,
        component: () => import('@/pages/autotest/manage/fullLine-testCaseConfig'),
        meta: { ...meta, title: '全链路用例配置' }
      },
      {
        path: 'base-testCaseConfig',
        name: `${pre}base-testCaseConfig`,
        component: () => import('@/pages/autotest/manage/base-testCaseConfig'),
        meta: { ...meta, title: '业务用例管理' }
      },
      {
        path: 'testTask-smokingTest',
        name: `${pre}testTask-smokingTest`,
        component: () => import('@/pages/autotest/manage/testTask-smokingTest'),
        meta: { ...meta, title: 'CI冒烟测试' }
      },
      {
        path: 'testTask-regressionTest',
        name: `${pre}testTask-regressionTest`,
        component: () => import('@/pages/autotest/manage/testTask-regressionTest'),
        meta: { ...meta, title: 'CI回归测试' }
      },
      {
        path: 'testTask-manualConfig',
        name: `${pre}testTask-manualConfig`,
        component: () => import('@/pages/autotest/manage/testTask-manualConfig'),
        meta: { ...meta, title: '人工配置' }
      },
      {
        path: 'report-view',
        name: `${pre}report-view`,
        component: () => import('@/pages/autotest/manage/components/case-report'),
        meta: { ...meta, title: '测试报告展示' }
      },
      {
        path: 'dataAnalysis-coverageRate',
        name: `${pre}dataAnalysis-coverageRate`,
        component: () => import('@/pages/autotest/manage/dataAnalysis-coverageRate'),
        meta: { ...meta, title: '自动化覆盖率' }
      },
      {
        path: 'dataAnalysis-reuseRate',
        name: `${pre}dataAnalysis-reuseRate`,
        component: () => import('@/pages/autotest/manage/dataAnalysis-reuseRate'),
        meta: { ...meta, title: '自动化复用率' }
      },
      {
        path: 'dataAnalysis-regressionResult',
        name: `${pre}dataAnalysis-regressionResult`,
        component: () => import('@/pages/autotest/manage/dataAnalysis-regressionResult'),
        meta: { ...meta, title: '回归测试结果' }
      }
    ])('autotest-manage-')
  }, {
    path: '/mock',
    name: 'mock',
    meta,
    redirect: { name: 'mock-mock-config' },
    component: layoutHeaderAside,
    children: (pre => [
      {
        path: 'mock-config',
        name: `${pre}mock-config`,
        component: () => import('@/pages/mock/mock-config'),
        meta: { ...meta, title: 'mock配置' }
      },
      {
        path: 'mock-log',
        name: `${pre}mock-log`,
        component: () => import('@/pages/mock/mock-log'),
        meta: { ...meta, title: 'mock日志' }
      }
    ])('mock-')
  }, {
    path: '/monitor',
    name: 'monitor',
    meta,
    redirect: { name: 'monitor-businessStatus' },
    component: layoutHeaderAside,
    children: (pre => [
      {
        path: 'businessStatus',
        name: `${pre}businessStatus`,
        component: () => import('@/pages/monitor/businessStatus'),
        meta: { ...meta, title: '业务应用在线状态' }
      }
    ])('monitor-')
  }, {
    path: '/qadata',
    name: 'qadata',
    meta,
    redirect: { name: 'qadata-form-autoTestData' },
    component: layoutHeaderAside,
    children: (pre => [
      {
        path: 'form-autoTestData',
        name: `${pre}form-autoTestData`,
        component: () => import('@/pages/qadata/form-autoTestData'),
        meta: { ...meta, title: '自动化运行汇总数据' }
      },
      {
        path: 'form-batchRunData',
        name: `${pre}form-batchRunData`,
        component: () => import('@/pages/qadata/form-batchRunData'),
        meta: { ...meta, title: '自动化定时跑批数据' }
      },
      {
        path: 'form-bugDataStatistics',
        name: `${pre}form-bugDataStatistics`,
        component: () => import('@/pages/qadata/form-bugDataStatistics'),
        meta: { ...meta, title: '缺陷统计数据' }
      },
      {
        path: 'chart-successRateCount',
        name: `${pre}chart-successRateCount`,
        component: () => import('@/pages/qadata/chart-successRateCount'),
        meta: { ...meta, title: '按执行成功率统计' }
      }
    ])('qadata-')
  },
  {
    path: '/sys/manage',
    name: 'sys-manage',
    meta,
    redirect: { name: 'sys-manage-user-info' },
    component: layoutHeaderAside,
    children: (pre => [
      {
        path: 'user-info',
        name: `${pre}user-info`,
        component: () => import('@/pages/sys/manage/user-info'),
        meta: { ...meta, title: '个人中心' }
      },
      {
        path: 'user-manage',
        name: `${pre}user-manage`,
        component: () => import('@/pages/sys/manage/user-manage'),
        meta: { ...meta, title: '用户管理' }
      }
    ])('sys-manage-')
  }
]

/**
 * 在主框架之外显示
 */
const frameOut = [
  // 登陆
  {
    path: '/login',
    name: 'login',
    component: () => import('@/pages/login')
  },
  // 查看用例执行日志
  {
    path: '/viewReport',
    name: 'viewReport',
    component: () => import('@/pages/viewReport')
  },
  // 查看用例执行日志
  {
    path: '/realTimeLog',
    name: 'realTimeLog',
    component: () => import('@/pages/autotest/real-time-log')
  },
  // 查看测试报告
  {
    path: '/viewTestReport',
    name: 'viewTestReport',
    component: () => import('@/pages/autotest/manage/components/case-report')
  }
]

/**
 * 错误页面
 */
const errorPage = [
  // 404
  {
    path: '*',
    name: '404',
    component: () => import('@/pages/error-page-404')
  }
]

// 导出需要显示菜单的
export const frameInRoutes = frameIn

// 重新组织后导出
export default [
  ...frameIn,
  ...frameOut,
  ...errorPage
]
