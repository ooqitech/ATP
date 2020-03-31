<template>
  <d2-container>
    <el-form :model="form" ref="uaaLogDecrypt" label-width="100px" size="small" inline>
      <el-row>
        <el-form-item label="mmrid" prop="mmrid" :rules="[{ required: true, message: 'mmrid必填', trigger: 'blur' }]">
          <el-input v-model="form.mmrid" placeholder="请输入mmrid" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item label="mmts" prop="mmts" :rules="[{ required: true, message: 'mmts必填', trigger: 'blur' }]">
          <el-input v-model="form.mmts" placeholder="请输入mmts" auto-complete="off"></el-input>
        </el-form-item>
      </el-row>
      <el-row>
        <el-form-item label="salt" prop="salt" :rules="[{ required: true, message: 'salt必填', trigger: 'blur' }]">
          <el-input v-model="form.salt" placeholder="请输入salt" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item label="ec" prop="ec">
          <el-input v-model="form.ec" placeholder="请输入ec" auto-complete="off"></el-input>
        </el-form-item>
      </el-row>
      <el-row>
        <el-form-item label="加密文本" prop="cipherText" :rules="[{ required: true, message: '加密文本必填', trigger: 'blur' }]">
          <el-input
            v-model="form.cipherText"
            type="textarea"
            placeholder="请输入加密文本"
            :autosize="{ minRows: 6, maxRows: 6}"
            auto-complete="off"
            style="width: 1000px"
          ></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitForm('uaaLogDecrypt')">解密</el-button>
          <el-button @click="resetForm('uaaLogDecrypt')">重置</el-button>
        </el-form-item>
      </el-row>
    </el-form>
    <div style="margin-top: 10px;margin-left: 20px">
      <pre>{{originText}}</pre>
    </div>
  </d2-container>
</template>
<script>
import { uaaLogDecrypt } from '@/api/tools/tool-uaaLogDecrypt'

export default {
  data() {
    return {
      form: {
        mmts: '',
        mmrid: '',
        salt: 'cpBuIYyWbVw4gCL83SujDbt9nSuVmyDE',
        cipherText: '',
        ec: ''
      },
      originText: ''
    }
  },
  methods: {
    // 提交表单事件
    submitForm(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          let params = {
            mmrid: this.form.mmrid,
            mmts: this.form.mmts,
            salt: this.form.salt,
            ec: this.form.ec,
            cipherText: this.form.cipherText
          }
          this.originText = ''
          uaaLogDecrypt(params).then(resp => {
            this.$message.success(resp.desc)
            this.originText = resp.data
          })
        } else {
          return false
        }
      })
    },
    // 重置表单
    resetForm(formName) {
      this.$refs[formName].resetFields()
    }
  }
}
</script>
<style scoped lang="scss">
pre {
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
