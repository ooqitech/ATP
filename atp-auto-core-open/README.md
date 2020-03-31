# atp-auto-core
基于flask、sqlalchemy、httprunner、celery等构建的自动化后台。

## 环境要求
```
python3.6
其他依赖包见requirement.txt
```

### 发布
```
部署目录 : /usr/local/src/atp/atp-auto-core
启动方式 : 通过supervisor启动flask_atp_auto、flask_atp_celery_default、flask_atp_celery_task服务，在supervisor配置文件中include项目目录下supervisor下所有配置文件
```

### 目录说明
```
atp : 代码目录
1、api : 公共处理函数
2、config : 不同环境配置文件
3、engine : 核心方法，如加载用例、celery任务等
4、httprunner : 第三方测试框架
5、jobs : celery定时任务
6、models : 模型文件
7、utils : 工具类，一些通用方法
8、views : 视图文件
gunicon : gunicon配置文件
supervisor : supervisor配置文件
flower_config.py celery控制台
run_celery.py  celery任务启动脚本
run_server.py  flask工程启动脚本
```
