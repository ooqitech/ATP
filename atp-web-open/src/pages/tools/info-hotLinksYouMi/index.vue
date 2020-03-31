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
    <el-alert title="工时录入" description type="success" show-icon></el-alert>
    <el-alert title="点击按钮跳转对应系统" type="info" show-icon></el-alert>
    <div class="desc">
      <a class="contentlist" href="http://99.48.46.160:8080/secure/RapidBoard.jspa?rapidView=168&projectKey=YM" target="view_window">
        <el-button type="primary" plain>JIRA</el-button>
      </a>
      <a class="contentlist" href="https://wiki.memedai.cn/pages/viewpage.action?pageId=6526366" target="view_window">
        <el-button type="primary" plain>Confluence</el-button>
      </a>
      <a class="contentlist" href="http://njgitrepo/QA/AutoTestCase-youmi" target="view_window">
        <el-button type="primary" plain>自动化git库</el-button>
      </a>
      <a class="contentlist" href="http://ymjenkins.immd.cn" target="view_window">
        <el-button type="primary" plain>Jenkins</el-button>
      </a>
    </div>
    <div class="desc">
      <a class="contentlist" href="https://wiki.memedai.cn/pages/viewpage.action?pageId=6526431" target="view_window">
        <el-button type="primary" plain>内网映射信息</el-button>
      </a>
      <a class="contentlist" href="https://wiki.memedai.cn/pages/viewpage.action?pageId=6526440" target="view_window">
        <el-button type="primary" plain>数据库账号映射表(测试账号test_yql/TES!@#uat)</el-button>
      </a>
      <a class="contentlist" href="https://wiki.memedai.cn/pages/viewpage.action?pageId=6526474" target="view_window">
        <el-button type="primary" plain>服务器账号映射表</el-button>
      </a>
    </div>
    <div class="desc">
      <a class="contentlist" href="http://ymgit.immd.cn" target="view_window">
        <el-button type="primary" plain>GitLab</el-button>
      </a>
      <a class="contentlist" href="http://ymnexus.immd.cn/nexus/" target="view_window">
        <el-button type="primary" plain>Maven私服</el-button>
      </a>
      <a class="contentlist" href="https://ym-disconf-uat.memedai.cn/main.html" target="view_window">
        <el-button type="primary" plain>Disconf平台(账号admin/admin)</el-button>
      </a>
      <a class="contentlist" href="https://ym-uat.memedai.cn/dubboadmin/" target="view_window">
        <el-button type="primary" plain>Dubbo控制台(账号root/root)</el-button>
      </a>
      <a class="contentlist" href="https:/ym-uat.memedai.cn/ejc" target="view_window">
        <el-button type="primary" plain>Elastic-job平台(账号root/root)</el-button>
      </a>
    </div>
  </d2-container>
</template>
<script>
export default {
  data() {
    return {}
  }
}
</script>
