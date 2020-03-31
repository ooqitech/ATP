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
    <el-alert title="注意事项" description="本操作仅限于因测试环境等外部因素导致不能发布，而上线需求很紧急的情况。常规测试过程中请勿使用该功能！！！" type="error" show-icon></el-alert>
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
        <el-form-item label="原因说明" prop="remark" required>
          <div style="margin: 10px 0;"></div>
          <el-input
            type="textarea"
            :autosize="{ minRows: 4,maxRows: 10}"
            v-model="form.remark"
            placeholder="请输入紧急构建原因说明"
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
import { setGreenchannel } from '@/api/tools/integration-greenChannelSet'
import { queryRecentFailPush } from '@/api/tools/integration-failReasonSet'

export default {
  data() {
    return {
      // 表单默认值
      form: {
        projectname: '请选择',
        buildnumber: '',
        remark: ''
      },
      pnoptions: [],
      alloptions: [],
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
        remark: [
          {
            validator: (rule, value, callback) => {
              if (value === '') {
                callback(new Error('请输入原因说明'))
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
          setGreenchannel({
            projectName: this.form.projectname,
            buildNumber: this.form.buildnumber,
            remark: this.form.remark
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
