<style scoped lang="scss" >
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
.col-title {
  text-align: center;
}
</style>
<template>
  <d2-container>
    <el-form :model="form" ref="smscodeQuery">
      <el-form-item label="钱包APP二维码"></el-form-item>
      <el-row :span="24">
        <el-col :span="12" class="col-title">
          <img :src="`${$baseUrl}image/testtools/qrcode/钱包ALIUAT.png`" />
        </el-col>
        <el-col :span="12" class="col-title">
          <img :src="`${$baseUrl}image/testtools/qrcode/钱包生产.png`" />
        </el-col>
      </el-row>
      <el-row :span="24" class="col-title">
        <el-col :span="12">
          <a class="contentlist" href="https://fir.im/memedaiuat" target="view_window">https://fir.im/memedaiuat</a>
        </el-col>
        <el-col :span="12">
          <a class="contentlist" href="https://www.pgyer.com/memedai2" target="view_window">https://www.pgyer.com/memedai2</a>
        </el-col>
      </el-row>
      <el-row :span="24" class="col-title">
        <el-col :span="12" class="contentlist">密码：memedai</el-col>
        <el-col :span="12" class="contentlist">密码：memedai</el-col>
      </el-row>
      <div style="margin-top: 25px"></div>
      <el-form-item label="么么推手二维码"></el-form-item>
      <el-row :span="24">
        <el-col :span="12" class="col-title">
          <img :src="`${$baseUrl}image/testtools/qrcode/么么推手UAT体验版本.png`" />
        </el-col>
        <el-col :span="12" class="col-title">
          <img :src="`${$baseUrl}image/testtools/qrcode/么么推手生产体验版本.png`" />
        </el-col>
      </el-row>
      <div style="margin-top: 25px"></div>
      <el-form-item label="管家APP二维码"></el-form-item>
      <el-row :span="24">
        <el-col :span="12" class="col-title">
          <img :src="`${$baseUrl}image/testtools/qrcode/管家ALIUAT.png`" />
        </el-col>
        <el-col :span="12" class="col-title">
          <img :src="`${$baseUrl}image/testtools/qrcode/管家生产.png`" />
        </el-col>
      </el-row>
      <el-row :span="24" class="col-title">
        <el-col :span="12">
          <a class="contentlist" href="https://www.pgyer.com/mrsuat" target="view_window">https://www.pgyer.com/mrsuat</a>
        </el-col>
        <el-col :span="12">
          <a class="contentlist" href="https://www.pgyer.com/mrspro" target="view_window">https://www.pgyer.com/mrspro</a>
        </el-col>
      </el-row>
      <el-row :span="24" class="col-title">
        <el-col :span="12" class="contentlist">密码：memedai</el-col>
        <el-col :span="12" class="contentlist">密码：memedai</el-col>
      </el-row>
    </el-form>
  </d2-container>
</template>
<script>
export default {
  data() {
    return {
      form: {}
    }
  },
  methods: {}
}
</script>
