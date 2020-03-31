![ATP图标](http://git.immd.cn/chengyun.liu/atpForOpen/raw/master/images/atp2.png)



## **ATP简介**
- ATP是基于python开发的测试服务平台，为公司测试团队提供各类接口的测试入口、测试数据构造，mock第三方测试平台。
- ATP平台采用Vue.js+Flask的前后端分离的架构，数据存储用到了MySQL和Redis。
- ATP的优势是它可以统一接口测试方法，统一管理所有接口测试用例，统一规划测试回归范围，可操作界面，降低全员的学习成本。

## **ATP产品价值**
- 降低工具开发成本
- 降低用例维护成本
- 降低bug定位成本
- 降低工具学习成本
- 提高接口测试效率

## **ATP优势**
- 一套平台的环境可对接测试多套业务系统的测试环
- 多套测试环境共用一套接口测试用例
- 可测试全链路接口，符合业务场景需求
- 平台内的公共变量可用于所有业务系统用例

##  **ATP工程模块说明**
[工程说明](http://99.48.58.207/chengyun.liu/atpForOpen/wikis/projectSpecification)
- ATP-Web前端页面工程使用Vue.js和Element-ui，用到Element-ui是因为它基于Vue2.0，有丰富的成熟组件拿来即用，非常适合网站页面快速成型。
- ATP-Core后端核心服务使用Flask作为服务端提供纯RESTful接口，选用Flask同样是因为Flask框架现在非常成熟，而且不重，也有丰富的第三方模块，生态良好。

##  **ATP功能模块说明**
[模块说明](http://git.immd.cn/chengyun.liu/atpForOpen/wikis/function)
- 环境配置：配置多套测试环境，分离测试用例和测试环境，可以保证一套用例多套环境使用。
- 变量配置：公共变量和用例变量配置，公共变量可以使用在所有接口里，用例变量只能用在当前用例中。
- 用例管理：设计用例，包括用例变量、前置用例、接口基本信息、入参、检查点。
- 用例执行：可以选择指定环境执行用例。
- 日志推送：多用于调试用例，一般用例执行失败原因可在平台日志中打印，无需多翻阅业务系统日志。

##  **ATP主要页面介绍**

[ATP主要页面介绍](http://git.immd.cn/chengyun.liu/atpForOpen/wikis/functionForATP)

##  **ATP快速部署文档**

[快速部署文档](http://git.immd.cn/chengyun.liu/atpForOpen/wikis/deployment)

