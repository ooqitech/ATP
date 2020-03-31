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
      <!-- <a href="#checkError">
        <el-tooltip class="item" effect="light" content="点击跳转到首个验证点错误" placement="top">
          <el-badge :value="checkErrorCount" :max="99" v-show="jumpToCheckErrorVisible" class="item">
            <el-button v-show="jumpToCheckErrorVisible" style="float: inherit;margin-left: 10px" size="small" plain round type="danger">验证点错误</el-button>
          </el-badge>
        </el-tooltip>
      </a>
      <a href="#otherError">
        <el-tooltip class="item" effect="light" content="点击跳转到首个其它错误" placement="top">
          <el-badge :value="otherErrorCount" :max="99" v-show="jumpToOtherErrorVisible" class="item">
            <el-button v-show="jumpToOtherErrorVisible" style="float: inherit;margin-left: 10px" size="small" plain round type="danger">其它错误</el-button>
          </el-badge>
        </el-tooltip>
      </a>-->
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
      </div>
    </div>
    <div style="text-align: center; margin-top: 5px">
      <span v-show="succVisible" style="font-size: 18px;color: green;font-weight:bold">{{succDesc}}</span>
      <a class="contentlist" :href="reportUrl" target="view_window">
        <el-button style="float: inherit;margin-left: 10px" size="small" round type="primary" v-show="doneVisible">查看报告</el-button>
      </a>
      <span v-show="errorVisible" style="font-size: 18px;color: red;font-weight:bold">{{errDesc}}</span>
      <span v-show="runVisible" style="font-size: 18px;color: royalblue;font-weight:bold">{{runDesc}}</span>
    </div>
  </d2-container>
</template>

<script>
// webSocket
import io from 'socket.io-client'
import { queryReportById } from '@/api/autotest/manage/testcase-run'

var url = process.env.VUE_APP_API
var pushUrl = url.split(':')[0]

export default {
  name: 'viewReport',
  data() {
    return {
      socket: null,
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
      reportId: null
    }
  },
  mounted() {
    this.reportId = this.$router.currentRoute.query.reportId
    this.totalProgress = this.$router.currentRoute.query.totalProgress
    this.message = ''
    this.startWS()
  },
  updated() {
    // 保持滚动到底部
    let div = document.querySelector('.c-chat')
    div.scrollTop = div.scrollHeight
  },
  beforeDestroy() {
    if (this.timer) {
      // 如果定时器还在运行 直接关闭
      clearInterval(this.timer) // 关闭
    }
    if (this.socket) {
      // 如果存在socket连接 直接关闭
      this.socket.emit('disconnected') // 关闭
      this.socket.disconnect() // 关闭
    }
  },
  methods: {
    // 启动websocket连接
    startWS() {
      // this.socket = io('http://192.168.10.54:7500/test', {reconnection: false});
      this.socket = io('http:' + pushUrl + ':7500/test', { reconnection: false })
      let _this = this
      this.socket.on('connect', function() {
        _this.socket.emit('test', _this.reportId)
        console.log('接收到服务端消息reportId', _this.reportId)
        console.log('接收到服务端消息totalProgress', _this.totalProgress)
      })
      this.socket.on('server_response', function(data) {
        // console.log('接收到服务端消息', data);
        _this.message = _this.message + '<br/>' + data.time
        if (data.time.indexOf('id="checkError"') > -1) {
          _this.jumpToCheckErrorVisible = true
          _this.checkErrorCount += 1
          _this.hasError = true
        }
        if (data.time.indexOf('id="otherError"') > -1 && data.time.indexOf('【runner.summary】:') < 0) {
          _this.jumpToOtherErrorVisible = true
          _this.otherErrorCount += 1
          _this.hasError = true
        }
        if (data.time.indexOf('id="extractError"') > -1 && data.time.indexOf('【runner.summary】:') < 0) {
          _this.jumpToExtractErrorVisible = true
          _this.extractErrorCount += 1
          _this.hasError = true
        }
        if (data.time.indexOf('【START】测试开始!') > -1) {
          _this.jumpToStartVisible = true
          _this.hasError = false
        }
        if (data.time.indexOf('【开始执行用例】') > -1) {
          var tmp = data.time.substr(data.time.indexOf('id="') + 4)
          var flag = '#'
          flag += tmp.substr(0, tmp.indexOf('"'))
          // _this.caseIdList.push(flag)
          var showName = flag.substr(flag.indexOf('-') + 1)
          showName = showName.substr(0, showName.indexOf(','))
          _this.caseIdList.push({ loc: flag, show: showName })
          // 计算最新的执行进度
          _this.currentProgress += 1
          _this.currentPercentage = Math.round((100 * _this.currentProgress) / _this.totalProgress)
          console.log('接收到服务端消息', _this.currentPercentage)
        }
        if (data.time.indexOf('【用例ID】:') > -1) {
          tmp = data.time.substr(data.time.indexOf('id="') + 4)
          flag = '#'
          flag += tmp.substr(0, tmp.indexOf('"'))
          showName = flag.substr(flag.indexOf('newCase') + 7)
          _this.caseIdList.push({ loc: flag, show: showName })
        }
        if (data.time.indexOf('【END】测试结束！') > -1) {
          _this.jumpToEndVisible = true
          _this.socket.emit('disconnected')
          _this.socket.disconnect()
          _this.queryReport().then(res => {
            if (res.code === '000') {
              _this.runVisible = false
              _this.succVisible = true
              _this.succDesc = res.desc
              _this.reportUrl = res.reportUrl
              //                                _this.doneVisible = true
            } else if (res.code === '330') {
              _this.errDesc = res.desc
              _this.runVisible = false
              _this.errorVisible = true
            } else if (res.code === '320') {
              _this.runDesc = res.desc
              _this.runVisible = true
            }
          })
        }
      })
      //                this.viewReport()
    },
    // 轮询查看报告是否生成
    viewReport() {
      var executeTimes = 0
      var intervalTime = 5000
      var timeoutId = setTimeout(timeOutFun, intervalTime)
      function timeOutFun() {
        executeTimes++
        this.queryReport().then(res => {
          if (res.code === '000') {
            this.runVisible = false
            this.succVisible = true
            this.succDesc = res.desc
            this.reportUrl = res.reportUrl
            this.doneVisible = true
            executeTimes = 5
          } else if (res.code === '330') {
            this.errDesc = res.desc
            this.runVisible = false
            this.errorVisible = true
            executeTimes = 5
          } else if (res.code === '320') {
            this.runDesc = res.desc
            this.runVisible = true
          }
          if (executeTimes < 5) {
            // eslint-disable-next-line no-caller
            setTimeout(arguments.callee, intervalTime)
          }
        })
      }
      clearTimeout(timeoutId)
    },
    // 根据reportId从后台查询测试报告
    queryReport() {
      return queryReportById({ reportId: this.reportId }).then(res => {
        return res
      })
    },
    handleExpand() {
      if (this.isExpand) {
        this.isExpand = false
      } else {
        this.isExpand = true
      }
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
</style>
