<template>
  <d2-container>
    <el-form :model="sendMQForm" ref="sendMQForm" label-width="100px" size="small">
      <el-form-item label="公司" prop="company" :rules="[{ required: true, message: 'company必选', trigger: 'change' }]">
        <el-select v-model="sendMQForm.company" placeholder="请选择company">
          <el-option v-for="item in companyOptions" :key="item.value" :label="item.label" :value="item.value"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="env" prop="env" :rules="[{ required: true, message: 'env必选', trigger: 'change' }]">
        <el-select v-model="sendMQForm.env" placeholder="请选择env">
          <el-option v-for="item in envOptions" :key="item.value" :label="item.label" :value="item.value"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="topic" prop="topic" :rules="[{ required: true, message: 'topic必填', trigger: 'blur' }]">
        <el-input v-model="sendMQForm.topic" placeholder="请输入topic" auto-complete="off" style="width: 400px"></el-input>
      </el-form-item>
      <el-form-item label="tag" prop="tag" :rules="[{ required: true, message: 'tag必填', trigger: 'blur' }]">
        <el-input v-model="sendMQForm.tag" placeholder="请输入tag" auto-complete="off" style="width: 400px"></el-input>
      </el-form-item>
      <el-form-item label="msg" prop="msg" :rules="[{ required: true, message: 'msg必填', trigger: 'blur' }]">
        <el-input
          v-model="sendMQForm.msg"
          placeholder="请输入msg"
          type="textarea"
          :autosize="{ minRows: 12, maxRows: 12}"
          auto-complete="off"
          style="width: 1000px"
        ></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="processSendMQ('sendMQForm')">发送</el-button>
        <el-button @click="resetForm('sendMQForm')">重置</el-button>
      </el-form-item>
    </el-form>
    <div style="margin-top: 10px;margin-left: 20px">
      <pre>{{respMsg}}</pre>
    </div>
  </d2-container>
</template>
<script>
import { sendMQ } from '@/api/tools/tool-sendMQ'
import { isJsonString } from '@/libs/common'

export default {
  data() {
    return {
      sendMQForm: {
        company: 'mime',
        env: 'aliuat',
        topic: '',
        tag: '',
        msg: ''
      },
      envOptions: [
        {
          label: 'aliuat',
          value: 'aliuat'
        },
        {
          label: 'sit',
          value: 'sit'
        }
      ],
      companyOptions: [
        {
          label: '米么',
          value: 'mime'
        },
        {
          label: '宝生',
          value: 'baosheng'
        }
      ],
      respMsg: ''
    }
  },
  methods: {
    // 发送MQ消息
    processSendMQ(formName) {
      this.respMsg = ''
      this.$refs[formName].validate(valid => {
        if (valid) {
          if (isJsonString(this.sendMQForm.msg)) {
            let params = {
              company: this.sendMQForm.company,
              env: this.sendMQForm.env,
              topic: this.sendMQForm.topic,
              tag: this.sendMQForm.tag,
              msg: this.sendMQForm.msg
            }
            sendMQ(params).then(resp => {
              this.respMsg = resp
            })
          } else {
            this.$message.warning('消息体不是合法的json格式')
          }
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
