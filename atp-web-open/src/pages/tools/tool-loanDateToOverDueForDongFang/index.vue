<template>
  <d2-container>
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span class="text-header">使用说明</span>
      </div>
      <div class="text item">1、dongfang.FSS_LOAN表中有记录且LOAN_STATUS是已放款（50）/已逾期（60）</div>
      <div class="text item">2、dongfang.fss_channel_repay_plan和dongfang.fss_user_repay_plan表有与期数相同数量的记录</div>
      <div class="text item">3、东方订单编号为capital.apply_main表中的capital_apply_no</div>
    </el-card>
    <!--更新还款计划-->
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span class="text-header">构造逾期数据</span>
      </div>
      <el-form :model="firstForm" ref="firstForm" label-width="100px" size="small" class="firstForm">
        <el-form-item label="测试环境" prop="env" :rules="[{ required: true, message: '测试环境必填', trigger: 'change' }]">
          <el-select v-model="firstForm.env" placeholder="请选择测试环境">
            <el-option v-for="item in envOptions" :key="item" :label="item" :value="item"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="订单编号" prop="loanId" :rules="[{ required: true, message: '订单编号必填', trigger: 'blur' }]">
          <el-input v-model="firstForm.loanId" placeholder="请输入订单编号" auto-complete="off" clearable></el-input>
        </el-form-item>
        <el-form-item label="放款时间" prop="loanDate" :rules="[{ required: true, message: '放款时间必填', trigger: 'blur' }]">
          <el-date-picker v-model="firstForm.loanDate" align="right" type="date" value-format="timestamp" placeholder="选择日期" :picker-options="pickerOptions"></el-date-picker>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitFirstForm('firstForm')">提交</el-button>
          <el-button @click="resetForm('firstForm')">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 确认提示框 -->
    <el-dialog title="提示" :visible.sync="confVisible" width="30%" center>
      <div class="del-dialog-cnt" v-if="flag === 1">更新账务数据为指定的放款时间，是否确定？</div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="delVisible = false">取 消</el-button>
        <el-button type="primary" @click="submit">确 定</el-button>
      </span>
    </el-dialog>
  </d2-container>
</template>
<script>
import { updateLoanPlan } from '@/api/tools/tool-loanDateToOverDueForDongFang'

export default {
  data() {
    return {
      firstForm: {
        env: 'dfxd-uat',
        loanId: '',
        loanDate: ''
      },
      envOptions: ['dfxd-uat'],
      pickerOptions: {
        disabledDate(time) {
          return time.getTime() > Date.now() - 3600 * 1000 * 24
        }
      },
      confVisible: false,
      flag: 1 // 确认提示框显示什么内容，1-第一表单提交按钮；2-第二表单提交按钮
    }
  },
  methods: {
    // 提交表单事件
    submitFirstForm(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          this.flag = 1
          this.confVisible = true
        } else {
          return false
        }
      })
    },
    // 请求后台接口
    submit() {
      this.confVisible = false
      if (this.flag === 1) {
        let params = {
          env: this.firstForm.env,
          loanId: this.firstForm.loanId,
          loanDate: this.firstForm.loanDate / 1000
        }
        updateLoanPlan(params).then(resp => {
          this.$message.success(resp.desc)
        })
      }
    },
    // 重置表单
    resetForm(formName) {
      this.$refs[formName].resetFields()
    }
  }
}
</script>
<style lang="scss">
.firstForm .el-input {
  width: 300px;
}

.secondForm .el-input {
  width: 300px;
}

.box-card .el-card__header {
  padding: 10px 20px;
}

.box-card .el-card__body {
  padding: 10px 20px;
}

.text-header {
  color: #606266;
}

.text {
  font-size: 14px;
  color: #606266;
}

.item {
  margin-bottom: 12px;
}

.clearfix:before,
.clearfix:after {
  display: table;
  content: '';
}

.clearfix:after {
  clear: both;
}

.box-card {
  width: 100%;
  margin-bottom: 20px;
}
</style>
