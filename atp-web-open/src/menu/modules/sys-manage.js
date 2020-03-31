export default {
  path: '/sys/manage',
  title: '系统管理',
  icon: 'cog',
  children: (pre => [
    { path: `${pre}user-info`, title: '个人中心', icon: 'user-circle-o' },
    { path: `${pre}user-manage`, title: '用户管理', icon: 'male' }
  ])('/sys/manage/')
}
