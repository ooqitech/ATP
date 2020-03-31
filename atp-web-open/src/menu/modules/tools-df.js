export default {
  path: '/tools',
  title: '工具管理',
  icon: 'wrench',
  children: (pre => [
    {
      path: `${pre}tool`,
      title: '工具集',
      icon: 'key',
      children: [
        { path: `${pre}tool-loanDateToOverDueForDongFang`, title: '构造东方逾期数据' },
        { path: `${pre}tool-loanTransferForDongFang`, title: '一键放款' }
      ]
    }
  ])('/tools/')
}
