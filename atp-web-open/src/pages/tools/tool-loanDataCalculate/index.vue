<style scoped lang="scss">
.bg-purple {
  background: #d3dce6;
}
.grid-content {
  border-radius: 4px;
  min-height: 36px;
  font-size: 16px;
  line-height: 36px;
  text-align: center;
}
.limit-width {
  font-weight: bold;
}
</style>
<template>
  <d2-container>
    <el-form class="limit-width" :inline="true" :model="loanDataCalculate" size="small">
      <el-form-item label="请选择公式类型" prop="category" label-width="150px" :rules="[{ required: true, message: '请选择', trigger: 'change' }]">
        <el-select v-model="loanDataCalculate.category" placeholder="请选择" @change="isselected">
          <el-option v-for="item in categoryOptions" :key="item.key" :label="item.label" :value="item.value"></el-option>
        </el-select>
      </el-form-item>
    </el-form>
    <el-form class="limit-width" :inline="true" :model="repayPlanBS" ref="repayPlanBS" size="small">
      <el-form-item
        label="贷款总金额"
        prop="totalAmt"
        label-width="100px"
        v-show="repayPlanBS.isShow"
        :rules="[{ required: true, message: '请输入贷款金额，单位元', trigger: 'blur' }]"
      >
        <el-input v-model="repayPlanBS.totalAmt"></el-input>
      </el-form-item>
      <el-form-item label="期数" prop="term" label-width="50px" v-show="repayPlanBS.isShow" :rules="[{ required: true, message: '请输入期数', trigger: 'blur' }]">
        <el-input v-model="repayPlanBS.term"></el-input>
      </el-form-item>
      <el-form-item
        label="年化利率(%)"
        prop="apr"
        label-width="100px"
        v-show="repayPlanBS.isShow"
        :rules="[{ required: true, message: '请输入年化利率', trigger: 'blur' }]"
      >
        <el-input v-model="repayPlanBS.apr"></el-input>
      </el-form-item>
      <el-form-item
        label="放款日期"
        prop="transferDate"
        label-width="100px"
        v-show="repayPlanBS.isShow"
        :rules="[{ required: true, message: '请选择放款日期', trigger: 'change' }]"
      >
        <el-date-picker v-model="repayPlanBS.transferDate" type="date" placeholder="选择日期"></el-date-picker>
      </el-form-item>
      <el-form-item v-show="repayPlanBS.isShow">
        <el-button type="primary" @click="submitForm('repayPlanBS')">生成</el-button>
        <el-button @click="resetForm('repayPlanBS')">重置</el-button>
      </el-form-item>
      <div style="margin-top:15px" v-show="repayPlanBS.isShow">
        <el-table
          :data="repayPlanBS.tableData"
          style="width: 100%"
          :default-sort="{prop: 'date', order: 'descending'}"
          width="180"
          :header-cell-style="{color:'black',background:'#eef1f6'}"
          size="small"
        >
          <el-table-column prop="term" label="还款期数" sortable></el-table-column>
          <el-table-column prop="plan_start_date" label="计息开始时间" sortable></el-table-column>
          <el-table-column prop="plan_end_date" label="计息结束时间"></el-table-column>
          <el-table-column prop="repay_date" label="还款日期"></el-table-column>
          <el-table-column prop="repay_amount" label="计划还款总金额"></el-table-column>
          <el-table-column prop="repay_principal" label="计划还款本金"></el-table-column>
          <el-table-column prop="repay_interest" label="计划还款利息"></el-table-column>
          <el-table-column prop="principal_current" label="期初本金"></el-table-column>
          <el-table-column prop="principal_remain" label="期末本金"></el-table-column>
        </el-table>
      </div>
    </el-form>
    <el-form class="limit-width" :inline="true" :model="buyBackAll" ref="buyBackAll" v-show="buyBackAll.isShow" size="small">
      <el-form-item label="贷款编号" prop="loanId" label-width="100px" :rules="[{ required: true, message: '请输入贷款编号', trigger: 'blur' }]">
        <el-input v-model="buyBackAll.loanId"></el-input>
      </el-form-item>
      <el-form-item label="测试环境" prop="env" :rules="[{ required: true, message: '请输选择测试环境', trigger: 'change' }]">
        <el-select v-model="buyBackAll.env" placeholder="请选择">
          <el-option v-for="item in envOptions" :key="item.key" :label="item.label" :value="item.value"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submitForm('buyBackAll')">计算</el-button>
        <el-button @click="resetForm('buyBackAll')">重置</el-button>
      </el-form-item>
      <hr />
      <el-row :gutter="20">
        <b style="margin-left: 15px; color: blue">回购金额:</b>
        <b style="color: red">{{buyBackAll.buybackAllAmt}}</b>
      </el-row>
      <el-row :gutter="20">
        <b style="margin-left: 15px; color: blue">回购金额计算公式:</b>
        <b>{{buyBackAll.buybackDetail}}</b>
      </el-row>
      <el-row :gutter="20" style="margin-top: 20px">
        <b style="margin-left: 15px; color: blue">回购本金:</b>
        <b>{{buyBackAll.buybackBaseAmt}}</b>
      </el-row>
      <el-row :gutter="20">
        <b style="margin-left: 15px; color: blue">回购本金计算公式:</b>
        <b>{{buyBackAll.buybackBaseDetail}}</b>
      </el-row>
      <el-row :gutter="20" style="margin-top: 20px">
        <b style="margin-left: 15px; color: blue">回购手续费:</b>
        <b>{{buyBackAll.buybackPoundage}}</b>
        <el-row :gutter="20">
          <b style="margin-left: 25px; color: blue">回购手续费计算公式:</b>
          <b>{{buyBackAll.buybackPoundageDetail}}</b>
        </el-row>
      </el-row>
      <hr />
      <el-row :gutter="20">
        <el-col :span="8">
          <div class="grid-content bg-purple">
            <b>====商户回购配置=====</b>
          </div>
          <div>
            <p>回购手续费基数: {{buyBackAll.buybackPoundageType}}</p>
            <p>回购手续费率: {{buyBackAll.poundageRate}}</p>
            <p>无偿回购天数: {{buyBackAll.buyBackFreeDays}}</p>
            <p>回购本金基数: {{buyBackAll.buybackBaseDetail}}</p>
          </div>
        </el-col>
        <el-col :span="16">
          <div class="grid-content bg-purple">
            <b>=====贷款信息=====</b>
          </div>
          <el-col :span="12">
            <div>
              <p>贷款总额: {{buyBackAll.loanSumAmt}}</p>
              <p>放款总额: {{buyBackAll.lendingSumAmt}}</p>
              <p>前收: {{buyBackAll.loanFee}}</p>
              <p>分期期数: {{buyBackAll.termTotal}}</p>
              <p>放款时间: {{buyBackAll.loanDate}}</p>
            </div>
          </el-col>
          <el-col :span="12">
            <div>
              <p>是否在免息期内: {{buyBackAll.isInFreeDays}}</p>
              <p>未还款期数（含正常和逾期状态）: {{buyBackAll.termUnpaid}}</p>
              <p>剩余本金: {{buyBackAll.unpaidLoanAmt}}</p>
              <p>逾期利息: {{buyBackAll.interestOverdue}}</p>
              <p>罚息: {{buyBackAll.lateCharge}}</p>
            </div>
          </el-col>
        </el-col>
      </el-row>
    </el-form>
  </d2-container>
</template>
<script>
import { generalRepayPlanBS, calcBuybackAll } from '@/api/tools/tool-loanDataCalculate'

export default {
  data() {
    return {
      loanDataCalculate: {
        category: ''
      },
      categoryOptions: [{ label: '等额本息按日计息-宝生', value: '0' }, { label: '全额回购计算', value: '1' }],
      repayPlanBS: {
        isShow: false,
        totalAmt: '',
        term: '',
        apr: '',
        transferDate: '',
        tableData: []
      },
      buyBackAll: {
        isShow: false,
        loanId: '',
        env: '',
        buybackDetail: '',
        buybackAllAmt: '',
        buybackBaseDetail: '',
        buybackBaseAmt: '',
        buybackPoundageDetail: '',
        buybackPoundage: '',
        buybackPoundageType: '',
        poundageRate: '',
        buyBackFreeDays: '',
        loanSumAmt: '',
        lendingSumAmt: '',
        loanFee: '',
        termTotal: '',
        loanDate: '',
        isInFreeDays: '',
        termUnpaid: '',
        unpaidLoanAmt: '',
        interestOverdue: '',
        lateCharge: ''
      },
      envOptions: [
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
      ]
    }
  },
  methods: {
    isselected(value) {
      if (value === '0') {
        this.repayPlanBS.isShow = true
        this.buyBackAll.isShow = false
      } else if (value === '1') {
        this.repayPlanBS.isShow = false
        this.buyBackAll.isShow = true
      }
    },
    loadDataRepayPlanBS(totalAmt, term, apr, transferDate) {
      generalRepayPlanBS({
        totalAmt: totalAmt,
        term: term,
        apr: apr,
        transferDate: transferDate
      }).then(resp => {
        if (resp.tableData === 'no data') {
          this.repayPlanBS.tableData = []
        } else {
          this.repayPlanBS.tableData = resp.tableData
        }
      })
    },
    loadDataBuyBackAll(loanId, env) {
      calcBuybackAll({
        loanId: loanId,
        env: env
      }).then(resp => {
        this.buyBackAll.buybackDetail = resp.result.buyback_detail
        this.buyBackAll.buybackAllAmt = resp.result.buyback_all_amt
        this.buyBackAll.buybackBaseDetail = resp.result.buyback_base_detail.slice(resp.result.buyback_base_detail.indexOf(',') + 1)
        this.buyBackAll.buybackBaseAmt = resp.result.buyback_base_amt
        this.buyBackAll.buybackPoundageDetail = resp.result.buyback_poundage_detail.slice(resp.result.buyback_poundage_detail.indexOf(',') + 1)
        this.buyBackAll.buybackPoundage = resp.result.buyback_poundage
        this.buyBackAll.buybackPoundageType = resp.result.buyback_poundage_type.slice(resp.result.buyback_poundage_type.indexOf(',') + 1)
        this.buyBackAll.poundageRate = resp.result.poundage_rate
        this.buyBackAll.buyBackFreeDays = resp.result.buyback_free_days
        this.buyBackAll.loanSumAmt = resp.result.loan_sum_amt
        this.buyBackAll.lendingSumAmt = resp.result.lending_sum_amt
        this.buyBackAll.loanFee = resp.result.loan_fee
        this.buyBackAll.termTotal = resp.result.term_total
        this.buyBackAll.loanDate = resp.result.loan_date
        this.buyBackAll.isInFreeDays = resp.result.is_in_free_days
        this.buyBackAll.termUnpaid = resp.result.term_unpaid
        this.buyBackAll.unpaidLoanAmt = resp.result.unpaid_loan_amt
        this.buyBackAll.interestOverdue = resp.result.interest_overdue
        this.buyBackAll.lateCharge = resp.result.late_charge
      })
    },
    submitForm(formName) {
      this.$refs[formName].validate(valid => {
        if (valid && formName === 'repayPlanBS') {
          this.loadDataRepayPlanBS(
            parseInt(this.repayPlanBS.totalAmt, 10),
            parseInt(this.repayPlanBS.term, 10),
            parseFloat(this.repayPlanBS.apr, 10),
            this.repayPlanBS.transferDate.getTime()
          )
        } else if (valid && formName === 'buyBackAll') {
          this.loadDataBuyBackAll(this.buyBackAll.loanId, this.buyBackAll.env)
        } else {
          return false
        }
      })
    },
    resetForm(formName) {
      this.$refs[formName].resetFields()
    }
  }
}
</script>
