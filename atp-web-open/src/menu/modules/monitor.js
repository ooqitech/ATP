export default {
  path: '/monitor',
  title: '统一监控',
  icon: 'heartbeat',
  children: (pre => [
    { path: `${pre}businessStatus`, title: '业务应用在线状态', icon: 'edit' }
  ])('/monitor/')
}
