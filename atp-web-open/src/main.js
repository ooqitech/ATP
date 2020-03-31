// polyfill
import 'babel-polyfill'
// Vue
import Vue from 'vue'
import App from './App'
// store
import store from '@/store/index'
// 核心插件
import '@/icons'
import d2Admin from '@/plugin/d2admin'
// 菜单和路由设置
import router from './router'
import { menuHeader, menuAside } from '@/menu'
import { frameInRoutes } from '@/router/routes'
// 右键菜单插件
import contentmenu from 'v-contextmenu'
import 'v-contextmenu/dist/index.css'
Vue.use(contentmenu)
// 核心插件
Vue.use(d2Admin)

new Vue({
  router,
  store,
  render: h => h(App),
  created() {
    // 处理路由 得到每一级的路由设置
    this.$store.commit('d2admin/page/init', frameInRoutes)
    // 设置顶栏菜单
    this.$store.commit('d2admin/menu/headerSet', menuHeader)
  },
  mounted() {
    // 用户登录后从数据库加载一系列的设置
    this.$store.commit('d2admin/account/load')
    // 获取并记录用户 UA
    this.$store.commit('d2admin/ua/get')
  },
  watch: {
    // 监听路由 控制侧边栏显示
    '$route.matched'(val) {
      const _side = menuAside.filter(menu => menu.path === val[0].path)
      this.$store.commit('d2admin/menu/asideSet', _side.length > 0 ? _side[0].children : [])
    }
  }
}).$mount('#app')
