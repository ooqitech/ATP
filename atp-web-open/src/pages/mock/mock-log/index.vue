<template>
  <d2-container>
    <el-form :model="form" ref="mockLogView" label-width="100px" inline>
      <el-form-item label="显示日志行数" prop="maxLineNum">
        <el-input v-model="form.maxLineNum" placeholder="请输入，默认显示当天所有日志" auto-complete="off" style="width: 300px"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submitForm">查看</el-button>
      </el-form-item>
    </el-form>
    <div style="padding: 0px;margin-left: 20px">
      <div class="c-chat">
        <p v-html="message" style="line-height: 150%;font-size: 14px;word-wrap:break-word;"></p>
      </div>
    </div>
  </d2-container>
</template>
<script>
import { getMockHistory } from '@/api/mock/mock-log'

export default {
  data() {
    return {
      // 当前表单默认值
      form: {
        maxLineNum: null
      },
      message: ''
    }
  },
  methods: {
    // 提交表单事件
    submitForm() {
      let parmas = this.form.maxLineNum ? { maxLineNum: parseInt(this.form.maxLineNum) } : {}
      getMockHistory(parmas).then(resp => {
        if (resp.count === 0) {
          this.$message.success('没有查询到当天的mock日志')
        } else {
          this.message = resp.history
        }
      })
    }
  }
}
</script>
<style scoped lang="scss">
.c-chat {
  position: relative;
  height: 700px;
  overflow: auto;
}
</style>
