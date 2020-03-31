// 组件库
import autotestManage from './modules/autotest-manage'
import sysManage from './modules/sys-manage'
import tools from './modules/tools'
import mock from './modules/mock'
// import qadata from './modules/qadata'
import home from './modules/home'
import toolsDF from './modules/tools-df'
import monitor from './modules/monitor'

// 菜单 侧边栏
let menuAside = null
if (process.env.VUE_APP_CURRENTMODE === 'oq' || process.env.VUE_APP_CURRENTMODE === 'bf' || process.env.VUE_APP_CURRENTMODE === 'qj') {
  menuAside = [
    home,
    // tools,
    autotestManage,
    mock,
    // qadata,
    sysManage
  ]
} else if (process.env.VUE_APP_CURRENTMODE === 'df') {
  menuAside = [
    home,
    // tools,
    toolsDF,
    autotestManage,
    mock,
    // qadata,
    sysManage
  ]
} else {
  menuAside = [
    home,
    tools,
    autotestManage,
    mock,
    monitor,
    // qadata,
    sysManage
  ]
}
// 菜单 顶栏
let menuHeader = null
if (process.env.VUE_APP_CURRENTMODE === 'oq' || process.env.VUE_APP_CURRENTMODE === 'bf' || process.env.VUE_APP_CURRENTMODE === 'qj') {
  menuHeader = [
    {
      path: '/index',
      title: '首页',
      icon: 'home'
    },
    // tools,
    autotestManage,
    mock,
    // qadata,
    sysManage
  ]
} else if (process.env.VUE_APP_CURRENTMODE === 'df') {
  menuHeader = [
    {
      path: '/index',
      title: '首页',
      icon: 'home'
    },
    // tools,
    toolsDF,
    autotestManage,
    mock,
    // qadata,
    sysManage
  ]
} else {
  menuHeader = [
    {
      path: '/index',
      title: '首页',
      icon: 'home'
    },
    tools,
    autotestManage,
    mock,
    monitor,
    // qadata,
    sysManage
  ]
}

export { menuAside, menuHeader }

