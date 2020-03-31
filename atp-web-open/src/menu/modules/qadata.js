export default {
  path: '/qadata',
  title: '质量管理',
  icon: 'pie-chart',
  children: (pre => [
    {
      path: `${pre}form`,
      title: '表格',
      icon: 'bar-chart',
      children: [
        { path: `${pre}form-autoTestData`, title: '自动化运行汇总数据' },
        { path: `${pre}form-batchRunData`, title: '自动化定时跑批数据' },
        { path: `${pre}form-bugDataStatistics`, title: '缺陷统计数据' }
      ]
    },
    {
      path: `${pre}chart`,
      title: '图表',
      icon: 'area-chart',
      children: [
        { path: `${pre}chart-successRateCount`, title: '按执行成功率统计' }
      ]
    }
  ])('/qadata/')
}
