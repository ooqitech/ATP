export default {
  path: '',
  title: '首页',
  icon: 'home',
  children: (pre => [
    { path: `${pre}index`, title: '首页', icon: 'home' }
  ])('/')
}
