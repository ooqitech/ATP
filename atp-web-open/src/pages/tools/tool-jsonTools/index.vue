<template>
  <d2-container>
    <div class="table_container">
      <el-tabs type="border-card">
        <el-tab-pane label="去掉json键值中空格">
          <el-form :model="delBlankSpaceForm" ref="delBlankSpaceForm" label-width="100px" size="small">
            <el-form-item label="原始json" prop="oriJson" :rules="[{ required: true, message: '原始json必填', trigger: 'blur' }]">
              <el-input
                v-model="delBlankSpaceForm.oriJson"
                type="textarea"
                placeholder="请输入原始json"
                :autosize="{ minRows: 12, maxRows: 12}"
                auto-complete="off"
                style="width: 1000px"
              ></el-input>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="convertJson('delBlankSpaceForm')">转换</el-button>
              <el-button @click="resetForm('delBlankSpaceForm')">重置</el-button>
            </el-form-item>
            <el-form-item prop="desJson">
              <div style="color: #303133;width: 1000px;line-height: 25px;font-size: 13px">
                <span>{{delBlankSpaceForm.desJson}}</span>
              </div>
              <!--<el-input v-model="delBlankSpaceForm.desJson" type="textarea" :autosize="{ minRows: 12, maxRows: 12}" auto-complete="off" style="width: 1000px"></el-input>-->
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </div>
  </d2-container>
</template>

<script>
import { isJsonString } from '@/libs/common'

export default {
  name: 'jsonTools',
  data() {
    return {
      delBlankSpaceForm: {
        oriJson: '',
        desJson: ''
      }
    }
  },
  methods: {
    // 开始转换
    convertJson(formName) {
      this.delBlankSpaceForm.desJson = ''
      this.$refs[formName].validate(valid => {
        if (valid) {
          if (isJsonString(this.delBlankSpaceForm.oriJson)) {
            let oriObj = JSON.parse(this.delBlankSpaceForm.oriJson)
            let desObj = {}
            Object.keys(oriObj).forEach(item => {
              desObj[item.replace(/\s*/g, '')] = oriObj[item]
            })
            this.delBlankSpaceForm.desJson = desObj
          } else {
            this.$message.warning('请输入json非法')
          }
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

<style lang="scss">
</style>
