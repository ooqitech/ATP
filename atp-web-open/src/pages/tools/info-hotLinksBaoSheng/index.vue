<style scoped lang="scss">
  .desc {
    margin-top: 20px;
    margin-left: 20px;
  }

  .contentlist {
    font-size: 14px;
  }

  .row-title {
    color: red;
    font-weight: bold;
  }
</style>
<template>
  <d2-container>
    <el-alert
      title="工时录入"
      description=""
      type="success"
      show-icon>
    </el-alert>
    <el-alert
      title="点击按钮跳转对应系统"
      type="info"
      show-icon>
    </el-alert>
    <!--<div class="desc">
      <a class="contentlist" href="https://ethercalc.org/ewiusd2wbolj" target="view_window">
        <el-button type="primary" plain>工时录入系统</el-button>
      </a>
      <a class="contentlist" href="https://www.ethercalc.org/qjn6md4zbfq2" target="view_window">
        <el-button type="primary" plain>工时录入系统(旧-废弃)</el-button>
      </a>
    </div>-->
    <div class="desc">
      <a class="contentlist"
         href="http://jira.immd.cn/secure/RapidBoard.jspa?rapidView=154&projectKey=BAOSHENG&view=detail&selectedIssue=BAOSHENG-10"
         target="view_window">
        <el-button type="primary" plain>JIRA</el-button>
      </a>
      <a class="contentlist" href="https://wiki.memedai.cn/pages/viewpage.action?pageId=6524778" target="view_window">
        <el-button type="primary" plain>Confluence</el-button>
      </a>
      <a class="contentlist" href="http://192.168.10.40:8100/org/productline.do?id=3" target="view_window">
        <el-button type="primary" plain>RAP</el-button>
      </a>
      <a class="contentlist" href="http://njgitrepo/QA/AutoTestCase-baosheng" target="view_window">
        <el-button type="primary" plain>自动化git库</el-button>
      </a>
      <a class="contentlist" href="http://bsjenkins.immd.cn/" target="view_window">
        <el-button type="primary" plain>Jenkins</el-button>
      </a>
    </div>
    <div class="desc">
      <a class="contentlist" href="https://wiki.memedai.cn/pages/viewpage.action?pageId=6524861" target="view_window">
        <el-button type="primary" plain>内网映射信息</el-button>
      </a>
      <a class="contentlist" href="https://wiki.memedai.cn/pages/viewpage.action?pageId=6524912" target="view_window">
        <el-button type="primary" plain>数据库账号映射表</el-button>
      </a>
      <a class="contentlist" href="https://wiki.memedai.cn/pages/viewpage.action?pageId=6525254" target="view_window">
        <el-button type="primary" plain>服务器账号映射表</el-button>
      </a>
    </div>
    <div class="desc">
      <a class="contentlist" href="http://bsgit.immd.cn" target="view_window">
        <el-button type="primary" plain>GitLab</el-button>
      </a>
      <a class="contentlist" href="http://bsnexus.immd.cn/nexus/" target="view_window">
        <el-button type="primary" plain>Maven私服</el-button>
      </a>
      <a class="contentlist" href="https://bs-disconf-uat.memedai.cn/main.html" target="view_window">
        <el-button type="primary" plain>Disconf平台(admin/admin)</el-button>
      </a>
      <a class="contentlist" href="https://bs-uat.memedai.cn/dubboadmin/" target="view_window">
        <el-button type="primary" plain>Dubbo控制台(root/root)</el-button>
      </a>
      <a class="contentlist" href="https://bs-uat.memedai.cn/ejc/registry_center_page" target="view_window">
        <el-button type="primary" plain>Elastic-job平台(root/root)</el-button>
      </a>
    </div>
  </d2-container>
</template>
<script>
export default {
  data () {
    return {}
  }
}
</script>
