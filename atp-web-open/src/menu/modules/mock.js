export default {
  path: '/mock',
  title: 'mock管理',
  icon: 'get-pocket',
  children: (pre => [
    { path: `${pre}mock-config`, title: 'mock配置', icon: 'edit' },
    { path: `${pre}mock-log`, title: 'mock日志', icon: 'file-text-o' }
  ])('/mock/')
}
