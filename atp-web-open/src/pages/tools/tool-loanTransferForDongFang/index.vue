<style lang="scss">
.limit-width {
  margin-top: 20px;
  font-weight: bold;
  .el-input {
    width: 300px;
  }
}

.row-title {
  color: red;
  font-weight: bold;
}
</style>
<template>
  <d2-container>
    <div class="limit-width">
      <el-form :inline="true" :model="form" ref="loanTransfer" size="small">
        <el-form-item label="资方订单号" prop="capitalApplyNo" :rules="[{ required: true, message: '资方订单号必填', trigger: 'blur' }]" label-width="100px">
          <el-input v-model="form.capitalApplyNo" placeholder="请输入资方订单号" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitForm('loanTransfer')">一键放款</el-button>
          <el-button @click="resetForm('loanTransfer')">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 确认提示框 -->
    <el-dialog title="提示" :visible.sync="confVisible" width="30%" center>
      <div class="del-dialog-cnt">执行放款操作，是否确定？</div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="confVisible = false">取 消</el-button>
        <el-button type="primary" @click="submit">确 定</el-button>
      </span>
    </el-dialog>
  </d2-container>
</template>
<script>
import { executeLoan } from '@/api/tools/tool-loanTransferForDongFang'

export default {
  data() {
    return {
      form: {
        capitalApplyNo: ''
      },
      confVisible: false
    }
  },
  methods: {
    submitForm(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          this.confVisible = true
        } else {
          return false
        }
      })
    },
    submit() {
      this.confVisible = false
      executeLoan({ capitalApplyNo: this.form.capitalApplyNo, fundId: '049' }).then(res => {
        this.$message.success(res.desc)
      })
    },
    resetForm(formName) {
      this.$refs[formName].resetFields()
    }
  }
}
</script>
