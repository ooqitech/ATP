<style scoped lang="scss" >
.col-title {
  text-align: right;
}
.desc {
  margin-bottom: 20px;
  width: 720px;
}
.context {
  font-size: 16px;
  color: red;
}
.contentlist {
  font-size: 14px;
}
.limit-width {
  width: 720px;
}
a:link {
  color: blue;
  text-decoration: underline;
}
a:visited {
  color: blue;
  text-decoration: none;
}
</style>
<template>
  <d2-container>
    <el-row :span="24" class="desc">
      <el-col :span="24" class="context">热门链接</el-col>
    </el-row>
    <el-row :span="24" class="desc">
      <el-col :span="6" class="contentlist">Jenkins：</el-col>
      <el-col :span="18">
        <a :span="24" class="contentlist" href="http://jenkins.immd.cn/" target="view_window">http://jenkins.immd.cn/</a>
      </el-col>
    </el-row>
    <el-row :span="24" class="desc">
      <el-col :span="6" class="contentlist">JIRA：</el-col>
      <el-col :span="18">
        <a
          :span="24"
          class="contentlist"
          href="http://99.48.46.160:8080/secure/Dashboard.jspa"
          target="view_window"
        >http://99.48.46.160:8080/secure/Dashboard.jspa</a>
      </el-col>
    </el-row>
    <el-row :span="24" class="desc">
      <el-col :span="6" class="contentlist">GitLab：</el-col>
      <el-col :span="18">
        <a :span="24" class="contentlist" href="http://njgitrepo/" target="view_window">http://njgitrepo/</a>
      </el-col>
    </el-row>
    <el-row :span="24" class="desc">
      <el-col :span="6" class="contentlist">RAP：</el-col>
      <el-col :span="18">
        <a
          :span="24"
          class="contentlist"
          href="http://192.168.10.40:8080/org/productline.do?id=3"
          target="view_window"
        >http://192.168.10.40:8080/org/productline.do?id=3</a>
      </el-col>
    </el-row>
    <el-row :span="24" class="desc">
      <el-col :span="6" class="contentlist">JAVADOC：</el-col>
      <el-col :span="18">
        <a :span="24" class="contentlist" href="http://javadoc.immd.cn/" target="view_window">http://javadoc.immd.cn/</a>
      </el-col>
    </el-row>
    <el-row :span="24" class="desc">
      <el-col :span="6" class="contentlist">DUBBO ADMIN：</el-col>
      <el-col :span="18">
        <el-col :span="24">
          <a class="contentlist" href="http://99.48.66.13:8080/dubbo/" target="view_window">http://99.48.66.13:8080/dubbo/（SIT）</a>
        </el-col>
        <el-col :span="24">
          <a class="contentlist" href="http://aliuat.memedai.cn/dubbo/" target="view_window">http://aliuat.memedai.cn/dubbo/（ALIUAT）</a>
        </el-col>
      </el-col>
    </el-row>
    <el-row :span="24" class="desc">
      <el-col :span="6" class="contentlist">diconf：</el-col>
      <el-col :span="18">
        <el-col :span="24">
          <a class="contentlist" href="http://99.48.66.250:8081/login.html" target="view_window">http://99.48.66.250:8081/login.html（SIT）</a>
        </el-col>
        <el-col :span="24">
          <a class="contentlist" href="http://192.168.10.3/main.html#" target="view_window">http://192.168.10.3/main.html#（ALIUAT）</a>
        </el-col>
      </el-col>
    </el-row>
    <el-row :span="24" class="desc">
      <el-col :span="6" class="contentlist">CAT：</el-col>
      <el-col :span="18">
        <el-col :span="24">
          <a class="contentlist" href="http://192.168.10.31:8888/cat/r/home" target="view_window">http://192.168.10.31:8888/cat/r/home（ALIUAT）</a>
        </el-col>
      </el-col>
    </el-row>
    <el-row :span="24" class="desc">
      <el-col :span="6" class="contentlist">elastic-job：</el-col>
      <el-col :span="18">
        <el-col :span="24">
          <a
            class="contentlist"
            href="http://aliuat.memedai.cn/elastic-job-lite-console/overview#"
            target="view_window"
          >http://aliuat.memedai.cn/elastic-job-lite-console/overview#（ALIUAT）</a>
        </el-col>
      </el-col>
    </el-row>
    <el-row :span="24" class="desc">
      <el-col :span="6" class="contentlist">应用服务器IP对照表：</el-col>
      <el-col :span="18">
        <el-col :span="24">
          <a
            class="contentlist"
            href="https://wiki.memedai.cn/pages/viewpage.action?pageId=5440282"
            target="view_window"
          >https://wiki.memedai.cn/pages/viewpage.action?pageId=5440282（SIT）</a>
          <div></div>
        </el-col>
        <el-col :span="24">
          <a
            class="contentlist"
            href="https://wiki.memedai.cn/pages/viewpage.action?pageId=4588482"
            target="view_window"
          >https://wiki.memedai.cn/pages/viewpage.action?pageId=4588482（ALIUAT）</a>
          <div></div>
        </el-col>
      </el-col>
    </el-row>
    <el-row :span="24" :gutter="10">&nbsp;</el-row>
    <el-row :span="24" :gutter="10">&nbsp;</el-row>
    <el-row :span="24" class="desc">
      <el-col :span="24" class="context">其他链接</el-col>
    </el-row>
    <el-collapse v-model="activeNames" accordion>
      <el-collapse-item name="1">
        <template slot="title">
          测试环境信息汇总
          <i class="header-icon el-icon-info"></i>
        </template>
        <div>包含：</div>
        <div>1. 常用系统url（包含sit uat）</div>
        <div>2.基础公共服务</div>
        <div>3.服务器IP及应用对照表（包含sit和uat）</div>
        <div>4.uat服务重启方法</div>
        <div>5.生产包归档后查看方法</div>
        <div>6.测试环境具体项目接口</div>
        <div>7.自动化执行机器</div>
        <a class="contentlist" href="https://wiki.memedai.cn/pages/viewpage.action?pageId=5442892" target="view_window">跳转链接</a>
      </el-collapse-item>
      <el-collapse-item name="2">
        <template slot="title">
          APP安装包获取地址
          <i class="header-icon el-icon-info"></i>
        </template>
        <div>各环境下APP安装包下载二维码</div>
        <a class="contentlist" href="https://wiki.memedai.cn/pages/viewpage.action?pageId=5444549" target="view_window">跳转链接</a>
      </el-collapse-item>
      <el-collapse-item name="3">
        <template slot="title">
          么么推手下载地址
          <i class="header-icon el-icon-info"></i>
        </template>
        <div>测试及生产环境么么推手下载说明</div>
        <a class="contentlist" href="https://wiki.memedai.cn/pages/viewpage.action?pageId=6524293" target="view_window">跳转链接</a>
      </el-collapse-item>
      <el-collapse-item name="4">
        <template slot="title">
          生产内测商户信息
          <i class="header-icon el-icon-info"></i>
        </template>
        <div>用于生产内测的商户</div>
        <div>包含商户号，商户名称，审核相关配置信息以及商户二维码</div>
        <a class="contentlist" href="https://wiki.memedai.cn/pages/viewpage.action?pageId=5442882" target="view_window">跳转链接</a>
      </el-collapse-item>
      <el-collapse-item name="5">
        <template slot="title">
          测试机汇总
          <i class="header-icon el-icon-info"></i>
        </template>
        <div>包含南京上海所有现存测试机汇总，型号，品牌及系统版本信息</div>
        <a class="contentlist" href="https://wiki.memedai.cn/pages/viewpage.action?pageId=5442811" target="view_window">跳转链接</a>
      </el-collapse-item>
    </el-collapse>
  </d2-container>
</template>
<script>
export default {
  data() {
    return {
      activeNames: []
    }
  }
}
</script>
