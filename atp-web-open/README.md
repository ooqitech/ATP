# atp-platform-web
基于vue2.0, d2admin, element-ui 定制开发。

## 项目安装
```
npm install
```

### 启动本地调试
```
npm run serve
```

### 打包生产环境
```
npm run master
```

### 目录说明
```
public : 资源路径，存放一些图标、图片
src : 代码目录
1、api : 定义后台接口
2、assets : css样式（属于d2admin框架内容）
3、components : 自定义组件（属于d2admin框架内容）
4、config : mq配置文件，区分不同环境
5、icons : icons图标资源
6、layout : 整体布局（属于d2admin框架内容）
7、libs : 定义公共方法
8、menu : 配置菜单
9、pages : 定义具体页面
10、plugin : 通用插件，如axios请求拦截器等（属于d2admin框架内容）
11、router : 路由配置
.env.xxx 不同环境配置文件
package.json 打包命令及依赖包
vue.config.js webpack配置，如代理服务器devServer配置
```

<a href="https://github.com/d2-projects/d2-admin" target="_blank"><img src="https://raw.githubusercontent.com/FairyEver/d2-admin/master/doc/image/d2-admin@2x.png" width="200"></a>
