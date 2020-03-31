<style scoped lang="scss">
.desc {
  margin-top: 20px;
  margin-bottom: 20px;
  width: 720px;
}

.contentlist {
  font-size: 14px;
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
    <el-alert title="注意事项" description="缺陷统计数据请访问下面链接至jira系统查看。" type="error" show-icon></el-alert>
    <el-row :span="24" class="desc">
      <el-col :span="6" class="contentlist">生产缺陷统计：</el-col>
      <el-col :span="18">
        <a
          :span="24"
          class="contentlist"
          href="http://99.48.46.160:8080/secure/Dashboard.jspa?selectPageId=11101"
          target="view_window"
        >http://99.48.46.160:8080/secure/Dashboard.jspa?selectPageId=11101</a>
      </el-col>
    </el-row>
    <el-row :span="24" class="desc">
      <el-col :span="6" class="contentlist">迭代内缺陷统计：</el-col>
      <el-col :span="18">
        <a
          :span="24"
          class="contentlist"
          href="http://99.48.46.160:8080/secure/Dashboard.jspa?selectPageId=11100"
          target="view_window"
        >http://99.48.46.160:8080/secure/Dashboard.jspa?selectPageId=11100</a>
      </el-col>
    </el-row>
  </d2-container>
</template>
<script>
export default {
  data() {
    return {}
  }
}
</script>
