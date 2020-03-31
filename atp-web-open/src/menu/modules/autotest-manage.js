export default {
  path: '/autotest/manage',
  title: '自动化管理',
  icon: 'android',
  children: (pre => [
    {
      path: `${pre}resource`,
      title: '资源配置',
      icon: 'cube',
      children: [
        { path: `${pre}resource-interfaceManage`, title: '接口管理' },
        { path: `${pre}resource-envManage`, title: '环境配置' },
        { path: `${pre}resource-publicVariable`, title: '公共变量' }
      ]
    },
    {
      path: `${pre}intf-testcase`,
      title: '自动化用例',
      icon: 'car',
      children: [
        { path: `${pre}interface-testCaseConfig`, title: '接口用例配置' },
        { path: `${pre}fullLine-testCaseConfig`, title: '全链路用例配置' }
        // {path: `${pre}interface-test`, title: '测试编辑页面'},
      ]
    },
    {
      path: `${pre}func-testcase`,
      title: '业务用例',
      icon: 'bicycle',
      children: [
        { path: `${pre}base-testCaseConfig`, title: '业务用例管理' }
      ]
    },
    /* {
        path: `${pre}uitestcase`,
        title: 'UI自动化管理',
        icon: 'wrench',
        children: [
            { path: `${pre}uiautomation-testCaseConfig`, title: 'UI自动化用例配置' },
            { path: `${pre}uiautomation-pageObjectConfig`, title: '页面元素对象配置' },
        ]
    },*/
    {
      path: `${pre}testTask`,
      title: '自动化测试',
      icon: 'retweet',
      children: [
        { path: `${pre}testTask-smokingTest`, title: 'CI冒烟测试' },
        { path: `${pre}testTask-regressionTest`, title: 'CI回归测试' },
        { path: `${pre}testTask-manualConfig`, title: '人工配置' }
      ]
    },
    /* {
        path: `${pre}report`,
        title: '报告管理',
        icon: 'file-word-o',
        children: [
            // {path: `${pre}report-cronJob`, title: '定时任务测试报告'},
            {path: `${pre}report-view`, title: '测试报告展示'}
        ]
    },*/
    {
      path: `${pre}dataAnalysis`,
      title: '数据分析',
      icon: 'line-chart',
      children: [
        // {path: `${pre}dataAnalysis-coverageRate`, title: '自动化覆盖率'},
        { path: `${pre}dataAnalysis-regressionResult`, title: '回归测试结果' },
        { path: `${pre}dataAnalysis-reuseRate`, title: '自动化复用率' }
      ]
    }
  ])('/autotest/manage/')
}
