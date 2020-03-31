<template>
  <d2-container>
    <div style="padding: 0px;margin-left: 50px">
      <el-progress v-if="hasError" :percentage="currentPercentage" status="exception"></el-progress>
      <el-progress v-else-if="currentPercentage===100&&jumpToEndVisible" :percentage="currentPercentage" status="success"></el-progress>
      <el-progress v-else :percentage="currentPercentage"></el-progress>
    </div>
    <div style="padding: 10px;margin-left: 40px">
      <span style="font-size: 20px;color: royalblue;font-weight:bold;margin-right: 5px">日志导航 >></span>
      <!-- <el-tooltip :content="'点击展开/关闭'" placement="top"> -->
      <el-switch v-model="isExpand" active-color="#409EFF" inactive-color="#DCDFE6" active-text="展开"></el-switch>
      <!-- </el-tooltip> -->
      <a href="#start">
        <el-button v-show="jumpToStartVisible" style="float: inherit;margin-left: 10px" size="small" round icon="el-icon-arrow-up">顶部</el-button>
      </a>
      <a :href="item.loc" v-for="(item, index) in caseIdList" :key="index">
        <span v-if="item.loc.indexOf('newCase') > -1 && isExpand" style="float: inherit;margin-left: 10px">|</span>
        <el-button
          v-if="item.loc.indexOf('newCase') > -1"
          style="float: inherit;margin-left: 10px"
          size="small"
          round
          type="primary"
          icon="el-icon-tickets"
        >{{item.show}}</el-button>
        <el-button v-else-if="isExpand" style="float: inherit;margin-left: 10px" size="small" plain round type="primary">{{item.show}}</el-button>
      </a>
      <a href="#end">
        <el-button v-show="jumpToEndVisible" style="float: inherit;margin-left: 10px" size="small" round icon="el-icon-arrow-down">底部</el-button>
      </a>
      <span v-if="hasError" style="float: inherit;margin-left: 10px;">|</span>
      <el-dropdown v-show="hasError" trigger="click">
        <el-button class="el-dropdown-link" style="float: inherit;margin-left: 10px" size="small" plain round type="danger">
          存在错误
          <i class="el-icon-caret-bottom el-icon--right"></i>
        </el-button>
        <el-dropdown-menu slot="dropdown">
          <a href="#checkError">
            <el-tooltip class="item" effect="light" content="点击跳转到首个【验证错误】" placement="right">
              <el-dropdown-item class="clearfix" v-show="jumpToCheckErrorVisible">
                验 证
                <el-badge class="mark" :value="checkErrorCount" />
              </el-dropdown-item>
            </el-tooltip>
          </a>
          <a href="#extractError">
            <el-tooltip class="item" effect="light" content="点击跳转到首个【提取错误】" placement="right">
              <el-dropdown-item class="clearfix" v-show="jumpToExtractErrorVisible">
                提 取
                <el-badge class="mark" :value="extractErrorCount" />
              </el-dropdown-item>
            </el-tooltip>
          </a>
          <a href="#otherError">
            <el-tooltip class="item" effect="light" content="点击跳转到首个【其它错误】" placement="right">
              <el-dropdown-item class="clearfix" v-show="jumpToOtherErrorVisible">
                其 它
                <el-badge class="mark" :value="otherErrorCount" />
              </el-dropdown-item>
            </el-tooltip>
          </a>
        </el-dropdown-menu>
      </el-dropdown>
      <i v-if="!(jumpToEndVisible)" class="el-icon-loading" style="float: inherit;margin-left: 10px"></i>
    </div>
    <div style="padding: 0px;margin-left: 50px">
      <div class="c-chat">
        <p v-html="message" style="line-height: 180%;font-size: 14px;white-space:nowrap;"></p>
        <el-backtop target=".c-chat" :bottom="100">
          <div
            style="{
              height: 100%;
              width: 100%;
              background-color: #f2f5f6;
              box-shadow: 0 0 6px rgba(0,0,0, .12);
              text-align: center;
              line-height: 40px;
              color: #1989fa;
              font-size: 14px;
            }"
          >回到顶部</div>
        </el-backtop>
      </div>
    </div>
    <!--<div style="text-align: center; margin-top: 5px">
      <span v-show="succVisible" style="font-size: 18px;color: green;font-weight:bold">{{succDesc}}</span>
      <a class="contentlist"
         :href="reportUrl"
         target="view_window">
        <el-button style="float: inherit;margin-left: 10px" size="small" round type="primary"
                   v-show="doneVisible">查看报告
        </el-button>
      </a>
      <span v-show="errorVisible" style="font-size: 18px;color: red;font-weight:bold">{{errDesc}}</span>
      <span v-show="runVisible" style="font-size: 18px;color: royalblue;font-weight:bold">{{runDesc}}</span>
    </div>-->
  </d2-container>
</template>

<script>
import Stomp from 'stompjs'
import { MQTT_SERVICE, MQTT_USERNAME, MQTT_PASSWORD } from '../../../config/mqtt.js'
import { getRunLog, getTestReportRunLog } from '@/api/autotest/real-time-log'

export default {
  name: 'realTimeLog',
  data() {
    return {
      message: '',
      doneVisible: false,
      timer: '',
      reportUrl: '',
      errorVisible: false,
      errDesc: '',
      succVisible: false,
      succDesc: '',
      runVisible: false,
      runDesc: '',
      caseIdList: [],
      jumpToStartVisible: false,
      jumpToEndVisible: false,
      jumpToCheckErrorVisible: false,
      jumpToOtherErrorVisible: false,
      jumpToExtractErrorVisible: false,
      isExpand: false,
      checkErrorCount: 0,
      otherErrorCount: 0,
      extractErrorCount: 0,
      totalProgress: 0,
      currentProgress: 0,
      currentPercentage: 0,
      hasError: false,
      reportId: null,
      client: null,
      queue: '',
      arguments: {},
      //                pageSize: 1,
      //                msg: "",
      postParams: null
    }
  },
  mounted() {
    this.reportId = this.$router.currentRoute.query.reportId
    this.totalProgress = this.$router.currentRoute.query.totalProgress
    this.postParams = this.$router.currentRoute.query.postParams
    this.message = ''
    if (this.postParams) {
      let postParams = JSON.parse(this.postParams)
      this.getReportRunLog(postParams)
    } else {
      this.getRealTimeLog(this.reportId)
    }
  },
  updated() {
    // 保持滚动到底部
    let div = document.querySelector('.c-chat')
    div.scrollTop = div.scrollHeight
  },
  beforeDestroy() {
    if (this.client) {
      // 如果存在连接 直接关闭
      this.client.disconnect() // 关闭
    }
  },
  methods: {
    /* 建立连接*/
    connect: function() {
      var ws = new WebSocket(MQTT_SERVICE[process.env.VUE_APP_V_HOST])
      this.client = Stomp.over(ws)
      var vHost = process.env.VUE_APP_V_HOST
      var headers = {
        login: MQTT_USERNAME[process.env.VUE_APP_V_HOST],
        passcode: MQTT_PASSWORD[process.env.VUE_APP_V_HOST],
        host: vHost
      }
      this.client.connect(headers, this.onConnected, this.onFailed)
    },
    /* 订阅消息队列*/
    onConnected: function(frame) {
      console.log('Connected: ' + frame)
      var topic = '/queue/' + this.queue
      this.client.subscribe(topic, this.responseCallback, this.arguments)
      var date = new Date()
      var seperator1 = '-'
      var seperator2 = ':'
      var month = date.getMonth() + 1 < 10 ? '0' + (date.getMonth() + 1) : date.getMonth() + 1
      var strDate = date.getDate() < 10 ? '0' + date.getDate() : date.getDate()
      var currentdate
        = date.getFullYear()
        + seperator1
        + month
        + seperator1
        + strDate
        + '&nbsp'
        + date.getHours()
        + seperator2
        + date.getMinutes()
        + seperator2
        + date.getSeconds()
        + ',000'
      this.message
        = '<span style="font-family:sansserif">['
        + currentdate
        + '] [INFO ]<span style="font-weight:bold;background-color:#2949ca;color:White" id="start">【任务已分发，即将开始运行......】</span></span>'
      this.jumpToStartVisible = true
      this.hasError = false
    },
    /* 连接失败*/
    onFailed: function(frame) {
      console.log('Failed: ' + frame)
    },
    /* 消息队列消费回调*/
    responseCallback: function(frame) {
      //                console.log('responseCallback msg=>' + frame.body);
      let _this = this
      _this.message = _this.message + '<br/>' + frame.body
      let msgList = frame.body.split('<br/>')
      msgList.forEach(item => {
        if (item.indexOf('id="checkError"') > -1) {
          _this.jumpToCheckErrorVisible = true
          _this.checkErrorCount += 1
          _this.hasError = true
        }
        if (item.indexOf('id="otherError"') > -1 && item.indexOf('【runner.summary】:') < 0) {
          _this.jumpToOtherErrorVisible = true
          _this.otherErrorCount += 1
          _this.hasError = true
        }
        if (item.indexOf('id="extractError"') > -1 && item.indexOf('【runner.summary】:') < 0) {
          _this.jumpToExtractErrorVisible = true
          _this.extractErrorCount += 1
          _this.hasError = true
        }
        /* if (item.indexOf('【START】测试开始!') > -1) {
                        _this.jumpToStartVisible = true
                        _this.hasError = false
                    }*/
        if (item.indexOf('【开始执行用例】') > -1) {
          var tmp = item.substr(item.indexOf('id="') + 4)
          var flag = '#'
          flag += tmp.substr(0, tmp.indexOf('"'))
          // _this.caseIdList.push(flag)
          var showName = flag.substr(flag.indexOf('-') + 1)
          showName = showName.substr(0, showName.indexOf(','))
          _this.caseIdList.push({ loc: flag, show: showName })
          // 计算最新的执行进度
          if (_this.totalProgress) {
            _this.currentProgress += 1
            _this.currentPercentage = Math.round((100 * _this.currentProgress) / _this.totalProgress)
            console.log('接收到服务端消息', _this.currentPercentage)
          }
        }
        if (item.indexOf('【用例ID】:') > -1) {
          tmp = item.substr(item.indexOf('id="') + 4)
          flag = '#'
          flag += tmp.substr(0, tmp.indexOf('"'))
          showName = flag.substr(flag.indexOf('newCase') + 7)
          _this.caseIdList.push({ loc: flag, show: showName })
        }
        if (item.indexOf('【END】测试结束！') > -1) {
          _this.jumpToEndVisible = true
          _this.disconnect()
        }
      })
      /* _this.pageSize += 1
                _this.msg = _this.msg + '<br/>' + frame.body
                if (_this.pageSize > 20) {
                    _this.message = _this.message + _this.msg
                    _this.msg = ""
                    _this.pageSize = 1
                }
                if (frame.body.indexOf('【END】测试结束！') > -1) {
                    _this.jumpToEndVisible = true
                    _this.message = _this.message + _this.msg
                    _this.disconnect()
                }*/
    },
    /* 断开连接*/
    disconnect: function() {
      this.client.disconnect()
    },
    /* 请求后台接口获取推送日志*/
    getRealTimeLog(id) {
      getRunLog({ reportId: id }).then(res => {
        this.queue = res.queue
        this.arguments = res.arguments
        this.connect()
      })
    },
    /* 请求后台接口获取推送日志*/
    getReportRunLog(params) {
      getTestReportRunLog(params).then(res => {
        this.queue = res.queue
        this.arguments = res.arguments
        this.connect()
      })
    }
  }
}
</script>
<style lang='scss'>
.c-chat {
  position: relative;
  height: 800px;
  overflow: auto;
}

a {
  text-decoration: none;
}

.c-chat .el-backtop {
  width: 80px;
  bottom: 150px !important;
}
</style>
