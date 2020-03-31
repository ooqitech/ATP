<template>
  <d2-container>
    <div class="home-page">
      <el-card class="box-card">
        <div slot="header" class="clearfix">
          <span class="text-header">平台使用说明</span>
        </div>
        <div class="text item">新用户首次使用，请至系统管理-个人中心下修改密码</div>
        <div class="text item">本平台用于测试辅助，集成常用便捷工具以及web自动化框架</div>
        <div class="text item">使用中遇到问题和建议，请第一时间联系 查道庆（daoqing.zha@ooqi.cn）</div>
        <div class="text item">
          <a :href="downloadAutoTestDocs">
            <el-button type="text">下载自动化帮助文档</el-button>
          </a>
        </div>
      </el-card>
      <el-card class="box-card">
        <div slot="header" class="clearfix">
          <span class="text-header">热门模块导航</span>
        </div>
        <div class="text item">
          工具集-数据清理
          <el-button type="text" style="margin-left: 30px" @click="goToTools">立即前往</el-button>
        </div>
        <div class="text item">
          自动化管理-接口用例管理
          <el-button type="text" style="margin-left: 30px" @click="goToAutoTest">立即前往</el-button>
        </div>
        <div class="text item">
          mock管理-mock配置
          <el-button type="text" style="margin-left: 30px" @click="goToMock">立即前往</el-button>
        </div>
      </el-card>
      <el-card class="box-card">
        <div slot="header" class="clearfix">
          <span class="text-header">待办事项</span>
        </div>
        <div class="text item">TODO</div>
      </el-card>
      <el-card class="box-card">
        <div slot="header" class="clearfix">
          <span class="text-header">个人日志</span>
        </div>
        <div class="text item">TODO</div>
      </el-card>
    </div>
  </d2-container>
</template>

<script>
import router from '@/router'

export default {
  name: 'DashboardAdmin',
  data() {
    return {
      downloadAutoTestDocs: '/atp/download/atp平台—自动化指导规范.docx'
    }
  },
  methods: {
    goToTools() {
      router.push({
        name: 'tools-tool-dataClean'
      })
    },
    goToAutoTest() {
      router.push({
        name: 'autotest-manage-interface-testCaseConfig'
      })
    },
    goToMock() {
      router.push({
        name: 'mock-mock-config'
      })
    }
  }
}
</script>

<style lang="scss">
.home-page {
  .box-card .el-card__header {
    padding: 10px 20px;
    text-align: center;
  }

  .box-card .el-card__body {
    padding: 10px 20px;
  }

  .text-header {
    color: #606266;
    font-size: 20px;
    font-weight: bolder;
  }

  .text {
    font-size: 14px;
    color: #606266;
    text-align: center;
  }

  .item {
    margin-bottom: 12px;
  }

  .clearfix:before,
  .clearfix:after {
    display: table;
    content: '';
  }

  .clearfix:after {
    clear: both;
  }

  .box-card {
    width: 100%;
    margin-bottom: 20px;
    .el-button--small,
    .el-button--small.is-round {
      padding: 0;
    }
  }
}
</style>
