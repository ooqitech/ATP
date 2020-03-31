<style scoped lang='scss'>
.limit-width {
  margin-top: 35px;
  font-weight: bold;
}

.test {
  position: relative;
  &:before {
    content: '*';
    color: red;
    position: absolute;
    left: 20px;
    top: 10px;
  }
}

.row-title {
  color: red;
  font-weight: bold;
}
</style>
<template>
  <d2-container>
    <el-alert title="注意事项" description="因会员数据是基础数据，需要从会员表查询会员编号来删除其他数据，请不要单独删除会员数据，否则其他数据将不能删除。了解更多请查阅【帮助文档】" type="warning" show-icon></el-alert>
    <el-tooltip placement="right">
      <div slot="content">点我查看</div>
      <a href="https://wiki.memedai.cn/pages/viewpage.action?pageId=8225571" target="view_window">
        <el-button round plain type="primary" icon="el-icon-document">帮助文档</el-button>
      </a>
    </el-tooltip>
    <el-row style="height: 35px;">&nbsp;</el-row>
    <hr />
    <div class="limit-width">
      <el-form ref="dataClean" :rules="rules" :model="form" label-width="100px" size="small">
        <el-form-item label="测试环境" prop="env" required>
          <el-select v-model="form.env" placeholder="请选择">
            <el-option v-for="item in options" :key="item.value" :label="item.label" :value="item.value"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="手机号" prop="mobile" required>
          <el-input v-model="form.mobile" placeholder="请输入手机号码" auto-complete="off" style="width: 300px"></el-input>
        </el-form-item>
        <el-form-item class="test" label="数据类型" prop="dataType">
          <el-checkbox :indeterminate="form.isIndeterminate" v-model="form.checkAll" @change="handleCheckAllChange">全选</el-checkbox>
          <div style="margin: 15px 0;"></div>
          <el-checkbox-group v-model="form.checkedTypes" @change="handleCheckedTypesChange">
            <el-checkbox v-for="type in form.types" :label="type" :key="type">{{type}}</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitForm('dataClean')">提交</el-button>
          <el-button @click="resetForm('dataClean')">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
  </d2-container>
</template>
<script>
import { regObj } from '@/libs/common'
import { clearData } from '@/api/tools/tool-dataClean'

const dataOptions = ['会员数据', '钱包数据', '征信数据', '账务数据', '现金贷数据', '资金方数据', 'sdk数据', '微信绑定关系', '农批宝数据']
export default {
  data() {
    return {
      // 表单默认值
      form: {
        checkAll: false,
        checkedTypes: [],
        types: dataOptions,
        isIndeterminate: false,
        mobile: '',
        env: ''
      },
      // 测试环境选项
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
        dataType: [
          {
            validator: (rule, value, callback) => {
              if (this.form.checkedTypes.length === 0) {
                callback(new Error('请选择要删除的数据'))
              } else {
                callback()
              }
            },
            trigger: 'blur,change'
          }
        ],
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
              if (this.form.mobile === '') {
                callback(new Error('请输入手机号码'))
              } else if (regObj.mobile.test(this.form.mobile)) {
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
    // 选择全部或取消选择全部
    handleCheckAllChange(val) {
      this.form.checkedTypes = this.form.checkAll ? dataOptions : []
      this.form.isIndeterminate = false
    },
    // 选择指定条件
    handleCheckedTypesChange(value) {
      let checkedCount = this.form.checkedTypes.length
      this.form.checkAll = checkedCount === this.form.types.length
      this.form.isIndeterminate = checkedCount > 0 && checkedCount < this.form.types.length
    },
    // 提交表单
    submitForm(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          this.$confirm('此操作将永久删除数据, 是否继续?', '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
            center: true
          })
            .then(() => {
              clearData({
                phone: this.form.mobile,
                type: this.form.checkedTypes,
                env: this.form.env
              }).then(resp => {
                this.$message.success(resp.desc.toString())
              })
            })
            .catch(() => {
              this.$message({
                type: 'info',
                message: '已取消删除'
              })
            })
        } else {
          return false
        }
      })
    },
    // 重置表单
    resetForm(formName) {
      this.$refs[formName].resetFields()
      this.form.checkedTypes = []
      this.form.isIndeterminate = false
    }
  }
}
</script>
