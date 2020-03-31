import db from './modules/db'
import user from './modules/user'
import menu from './modules/menu'
import theme from './modules/theme'
import account from './modules/account'
import ua from './modules/ua'
import gray from './modules/gray'
import page from './modules/page'
import transition from './modules/transition'
import casetable from './modules/casetable'
import testreport from './modules/testreport'
import interfaces from './modules/interfaces'
import fulllinecase from './modules/fulllinecase'
export default {
  namespaced: true,
  modules: {
    db,
    user,
    menu,
    theme,
    account,
    ua,
    gray,
    page,
    transition,
    casetable,
    interfaces,
    testreport,
    fulllinecase
  }
}
