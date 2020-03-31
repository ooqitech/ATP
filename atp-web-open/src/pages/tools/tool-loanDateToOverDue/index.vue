<template>
  <d2-container>
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span class="text-header">使用说明</span>
      </div>
      <div class="text item">1、accounting.FSS_LOANS表中有记录且LOAN_STATUS是已放款（50）/已逾期（60）</div>
      <div
        class="text item"
      >2、accounting.FSS_LOANS表中MERCHANT_NO在范围内（龙信（045）东方医美（048）东方现金贷（049）小雨点（030）海尔云贷（051）苏宁医美（044）苏宁现金贷（052）微神马医美（039）汇鑫（038）苏宁小雨点（053）海尔云贷现金贷（055）苏宁微神马（056））</div>
      <div class="text item">3、accounting.FSS_LOAN_REPAY_PLAN表有与期数相同数量的记录</div>
      <div class="text item">
        4、当资方编号为（东方医美（048）东方现金贷（049））时，会返回capital.apply_main表中的capital_apply_no，用于在
        <a href="http://df-atp.immd.cn" target="_blank">东方ATP平台</a>操作东方库数据更新
      </div>
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
        <el-form-item label="贷款编号" prop="loanId" :rules="[{ required: true, message: '贷款编号必填', trigger: 'blur' }]">
          <el-input v-model="firstForm.loanId" placeholder="请输入贷款编号" auto-complete="off" clearable></el-input>
        </el-form-item>
        <el-form-item label="放款时间" prop="loanDate" :rules="[{ required: true, message: '放款时间必填', trigger: 'blur' }]">
          <el-date-picker v-model="firstForm.loanDate" align="right" type="date" value-format="timestamp" placeholder="选择日期" :picker-options="pickerOptions"></el-date-picker>
        </el-form-item>
        <el-form-item label="是否跑逾期" prop="runMode">
          <el-radio-group v-model="firstForm.runMode">
            <el-radio :label="1">否</el-radio>
            <el-radio :label="2">是</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitFirstForm('firstForm')">提交</el-button>
          <el-button @click="resetForm('firstForm')">重置</el-button>
        </el-form-item>
        <el-form-item label="东方订单编号" v-if="firstForm.capitalApplyNo">
          <span>{{firstForm.capitalApplyNo}}</span>
        </el-form-item>
      </el-form>
    </el-card>
    <!--逾期跑批-->
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span class="text-header">逾期跑批</span>
      </div>
      <el-form :model="secondForm" ref="secondForm" label-width="100px" size="small" class="secondForm">
        <el-form-item label="测试环境" prop="env" :rules="[{ required: true, message: '测试环境必填', trigger: 'change' }]">
          <el-select v-model="secondForm.env" placeholder="请选择测试环境">
            <el-option v-for="item in envOptions" :key="item" :label="item" :value="item"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="贷款编号" prop="loanId" :rules="[{ required: true, message: '贷款编号必填', trigger: 'blur' }]">
          <el-input v-model="secondForm.loanId" placeholder="请输入贷款编号" auto-complete="off" clearable></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitSecondForm('secondForm')">提交</el-button>
          <el-button @click="resetForm('secondForm')">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 确认提示框 -->
    <el-dialog title="提示" :visible.sync="confVisible" width="30%" center>
      <div class="del-dialog-cnt" v-if="flag === 1">更新账务数据为指定的放款时间，是否确定？</div>
      <div class="del-dialog-cnt" v-if="flag === 2">运行逾期跑批任务，是否确定？</div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="confVisible = false">取 消</el-button>
        <el-button type="primary" @click="submit">确 定</el-button>
      </span>
    </el-dialog>
  </d2-container>
</template>
<script>
import { createAccountingOverdue, updateLoanPlan, executeOverdue } from '@/api/tools/tool-loanDateToOverDue'

export default {
  data() {
    return {
      firstForm: {
        env: 'ALIUAT',
        loanId: '',
        loanDate: '',
        runMode: 1,
        capitalApplyNo: ''
      },
      secondForm: {
        env: 'ALIUAT',
        loanId: ''
      },
      envOptions: ['SIT', 'ALIUAT', 'BaoSheng'],
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
    // 提交表单事件
    submitSecondForm(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          this.flag = 2
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
        this.firstForm.capitalApplyNo = ''
        let params = {
          env: this.firstForm.env,
          loanId: this.firstForm.loanId,
          loanDate: this.firstForm.loanDate / 1000
        }
        if (this.firstForm.runMode === 1) {
          updateLoanPlan(params).then(resp => {
            this.$message.success(resp.desc)
            this.firstForm.capitalApplyNo = resp.data.capitalApplyNo
          })
        } else {
          createAccountingOverdue(params).then(resp => {
            this.$message.success(resp.desc)
            this.firstForm.capitalApplyNo = resp.data.capitalApplyNo
          })
        }
      } else {
        let params = {
          env: this.firstForm.env,
          loanId: this.firstForm.loanId
        }
        executeOverdue(params).then(resp => {
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

a:link {
  color: blue;
  text-decoration: underline;
}
a:visited {
  color: blue;
  text-decoration: none;
}
</style>
