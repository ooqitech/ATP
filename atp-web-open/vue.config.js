const path = require('path')
const Timestamp = new Date().getTime()

// 拼接路径
function resolve(dir) {
  return path.join(__dirname, dir)
}

// 基础路径 注意发布之前要先修改这里
const baseUrl = '/'

module.exports = {
  publicPath: baseUrl, // 根据你的实际情况更改这里
  outputDir: 'dist',
  lintOnSave: true,
  devServer: {
    publicPath: baseUrl, // 和 baseUrl 保持一致
    proxy: {
      '/auto': {
        target: 'http://XX.XX.XX.XX:7000/atp/auto',
        changeOrigin: true,
        ws: true,
        pathRewrite: {
          '^/atp/auto': ''
        }
      },
      '/download': {
        target: 'http://XX.XX.XX.XX:8899/atp/download',
        changeOrigin: true,
        ws: true,
        pathRewrite: {
          '^/atp/download': ''
        }
      },
      '/qa': {
        target: 'http://XX.XX.XX.XX:5000/atp/qa',
        changeOrigin: true,
        ws: true,
        pathRewrite: {
          '^/atp/qa': ''
        }
      },
      '/atp/mock': {
        target: 'http://XX.XX.XX.XX:6000/atp/mock',
        changeOrigin: true,
        ws: true,
        pathRewrite: {
          '^/atp/mock': ''
        }
      },
      '/mock/service': {
        target: 'http://XX.XX.XX.XX:6000/mock/service',
        changeOrigin: true,
        ws: true,
        pathRewrite: {
          '^/mock/service': ''
        }
      },
      '/monitor': {
        target: 'http://XX.XX.XX.XX:8000/atp/monitor',
        changeOrigin: true,
        ws: true,
        pathRewrite: {
          '^/atp/monitor': ''
        }
      }
    }
  },
  // 默认设置: https://github.com/vuejs/vue-cli/tree/dev/packages/%40vue/cli-service/lib/config/base.js
  chainWebpack: config => {
    // 解决 cli3 热更新失效 https://github.com/vuejs/vue-cli/issues/1559
    config.resolve
      .symlinks(true)
    // 重新设置 alias
    config.resolve.alias
      .set('@', resolve('src'))
    // babel-polyfill 加入 entry
    const entry = config.entry('app')
    entry
      .add('babel-polyfill')
      .end()
    // 修改svg规则file-loader排除svg图标目录
    config.module
      .rule('svg')
      .exclude.add(resolve('src/icons'))
      .end()
    // svg-sprite-loader
    config.module
      .rule('svgSpriteLoader')
      .test(/\.svg$/)
      .include.add(resolve('src/icons'))
      .end()
      .use('svg-sprite-loader')
      .loader('svg-sprite-loader')
      .options({
        symbolId: 'icon-[name]'
      })
      .end()
  },
  css: {
    // 增加版本号
    extract: {
      filename: `css/[name].[contenthash:8]-${process.env.VUE_APP_Version}.${Timestamp}.css`,
      chunkFilename: `css/[name].[contenthash:8]-${process.env.VUE_APP_Version}.${Timestamp}.css`
    }
  },
  configureWebpack: { // webpack 配置
    output: { // 输出重构  打包编译后的 文件名称  【模块名称.版本号.时间戳】
      filename: `[name]-${process.env.VUE_APP_Version}.${Timestamp}.js`,
      chunkFilename: `[name]-${process.env.VUE_APP_Version}.${Timestamp}.js`
    },
    performance: {
      // false | "error" | "warning" // 不显示性能提示 | 以错误形式提示 | 以警告...
      hints: 'warning',
      // 开发环境设置较大防止警告
      // 根据入口起点的最大体积，控制webpack何时生成性能提示,整数类型,以字节为单位
      maxEntrypointSize: 5000000,
      // 最大单个资源体积，默认250000 (bytes)
      maxAssetSize: 3000000
    }
  }
}
