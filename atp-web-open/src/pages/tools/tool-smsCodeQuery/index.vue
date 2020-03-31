<style scoped lang="scss" >
.limit-width {
  width: 720px;
  font-weight: bold;
}
</style>
<template>
  <d2-container>
    <el-form :model="form" :rules="rules" ref="smscodeQuery" label-width="100px" size="small">
      <el-form-item label="测试环境" prop="env" required>
        <el-select v-model="form.env" placeholder="请选择">
          <el-option v-for="item in options" :key="item.value" :label="item.label" :value="item.value"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="手机号" prop="mobile" required>
        <el-input v-model="form.mobile" placeholder="请输入手机号码" auto-complete="off" style="width: 300px"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submitForm('smscodeQuery')">立即获取</el-button>
        <el-button @click="resetForm('smscodeQuery')">重置</el-button>
      </el-form-item>
    </el-form>
  </d2-container>
</template>
<script>
import { regObj } from '@/libs/common'
import { getSms } from '@/api/tools/tool-smsCodeQuery'

export default {
  data() {
    return {
      // 当前表单默认值
      form: {
        mobile: '',
        env: ''
      },
      // 查询条件测试环境备选值
      options: [
        {
          value: 'SIT',
          label: 'SIT'
        },
        {
          value: 'ALIUAT',
          label: 'ALIUAT'
        },
        {
          value: 'BaoSheng',
          label: 'BaoSheng'
        }
      ],
      // 校验规则
      rules: {
        env: [
          {
            validator: (rule, value, callback) => {
              if (this.form.env === '') {
                callback(new Error('请选择测试环境'))
              } else {
                callback()
              }
            },
            trigger: 'blur,change'
          }
        ],
        mobile: [
          {
            validator: (rule, value, callback) => {
              if (value === '') {
                callback(new Error('请输入手机号码'))
              } else if (regObj.mobile.test(value)) {
                callback()
              } else {
                callback(new Error('请输入正确的手机号码'))
              }
            },
            trigger: 'blur,change'
          }
        ]
      }
    }
  },
  methods: {
    // 提交表单事件
    submitForm(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          getSms({
            phone: this.form.mobile,
            env: this.form.env
          }).then(resp => {
            this.$message.success(resp.sms.toString())
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
