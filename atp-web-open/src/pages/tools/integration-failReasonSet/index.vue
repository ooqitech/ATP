<style scoped lang="scss">
.col-title {
  text-align: right;
}

.desc {
  margin-bottom: 20px;
}

.context {
  font-size: 16px;
}

.limit-width {
  width: 720px;
  margin-top: 35px;
  font-weight: bold;
}

.row-title {
  color: red;
  font-weight: bold;
}
</style>
<template>
  <d2-container>
    <el-alert title="注意事项" description="请如实记录本次构建号下冒烟测试执行失败原因，问题大类如有缺失，请及时反馈。" type="error" show-icon></el-alert>
    <div class="limit-width">
      <el-form :model="form" :rules="rules" ref="greenchannelSet" label-width="100px" size="small">
        <el-form-item label="项目名" prop="projectname" required>
          <el-select v-model="form.projectname" @change="isselected">
            <el-option v-for="item in pnoptions" :key="item" :label="item" :value="item"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="构建号" prop="buildnumber" required>
          <el-input v-model="form.buildnumber" :disabled="true" style="width: 220px"></el-input>
        </el-form-item>
        <el-form-item label="问题大类" prop="failuretype" required>
          <el-select v-model="form.failuretype" placeholder="请选择">
            <el-option v-for="item in failureoptions" :key="item" :label="item" :value="item"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="原因描述" prop="failurerecord" required>
          <el-input
            type="textarea"
            :autosize="{ minRows: 4,maxRows: 10}"
            v-model="form.failurerecord"
            placeholder="请输入冒烟测试失败详细原因"
            auto-complete="off"
            style="width: 300px"
          ></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitForm('greenchannelSet')">提交</el-button>
          <el-button @click="resetForm('greenchannelSet')">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
  </d2-container>
</template>
<script>
import { queryRecentFailPush, recordFailure } from '@/api/tools/integration-failReasonSet'

export default {
  data() {
    return {
      // 表单默认值
      form: {
        projectname: '请选择',
        buildnumber: '',
        failuretype: '',
        failurerecord: ''
      },
      pnoptions: [],
      alloptions: [],
      failureoptions: ['代码问题', '案例问题', '环境问题', '自动化框架问题'],
      // 校验规则
      rules: {
        projectname: [
          {
            validator: (rule, value, callback) => {
              if (this.form.projectname === '') {
                callback(new Error('请选择项目名称'))
              } else {
                callback()
              }
            },
            trigger: 'blur,change'
          }
        ],
        failuretype: [
          {
            validator: (rule, value, callback) => {
              if (this.form.failuretype === '') {
                callback(new Error('请选择问题大类'))
              } else {
                callback()
              }
            },
            trigger: 'blur,change'
          }
        ],
        failurerecord: [
          {
            validator: (rule, value, callback) => {
              if (value === '') {
                callback(new Error('请输入具体的失败原因'))
              } else {
                callback()
              }
            },
            trigger: 'blur,change'
          }
        ]
      }
    }
  },
  methods: {
    isselected(value) {
      this.form.buildnumber = this.alloptions[value]
    },
    // 提交表单
    submitForm(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          recordFailure({
            projectName: this.form.projectname,
            buildNumber: this.form.buildnumber,
            failureType: this.form.failuretype,
            failureRecord: this.form.failurerecord
          }).then(resp => {
            this.$message.success(resp.desc.toString())
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
  },
  mounted() {
    queryRecentFailPush({}).then(resp => {
      this.alloptions = resp.desc
      for (let i in this.alloptions) {
        this.pnoptions.push(i)
      }
    })
  }
}
</script>
