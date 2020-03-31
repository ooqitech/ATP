<style scoped lang="scss">
.limit-width {
  margin-top: 20px;
  font-weight: bold;
}

.row-title {
  color: red;
  font-weight: bold;
}
</style>
<template>
  <d2-container>
    <el-alert title="成功放款的条件如下" description="1、资方是元玺、酷米、海尔（MERCHANT_NO=023、032、021）；2、贷款表里有数据且状态为等待放款（LOAN_STATUS=40）" type="success" show-icon></el-alert>
    <div class="limit-width">
      <el-form :inline="true" :model="form" :rules="rules" ref="loanTransfer" size="small">
        <el-form-item label="测试环境" prop="env" required label-width="80px">
          <el-select v-model="form.env" placeholder="请选择" style="width: 150px">
            <el-option v-for="item in options" :key="item.value" :label="item.label" :value="item.value"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="手机号" prop="mobile" required label-width="80px">
          <el-input v-model="form.mobile" placeholder="请输入手机号码" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="search('loanTransfer')">查询待放款订单</el-button>
          <el-button @click="resetForm('loanTransfer')">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
    <div style="margin-top:10px">
      <el-table ref="multipleTable" :data="tableData" style="width: 100%" tooltip-effect="dark" @selection-change="handleSelectionChange" size="small">
        <el-table-column type="selection" width="55"></el-table-column>
        <el-table-column prop="orderNo" label="订单编号" width="180"></el-table-column>
        <el-table-column prop="product_name" label="商品名称" width="720"></el-table-column>
        <el-table-column prop="amount" label="订单金额" width="100"></el-table-column>
        <el-table-column prop="repayment_periods" label="分期期数" width="100"></el-table-column>
        <el-table-column prop="created_datetime" label="订单创建时间" width="180"></el-table-column>
        <el-table-column prop="status" label="订单状态"></el-table-column>
        <el-table-column prop="merchant_no" label="资方"></el-table-column>
      </el-table>
    </div>
    <div style="margin-top: 30px;font-weight: bold">
      <span>放款时间</span>
      <el-date-picker v-model="transfertime" type="datetime" placeholder="默认为当前操作时间" align="right" :picker-options="pickerOptions1"></el-date-picker>
      <el-button type="primary" @click="submitForm('loanTransfer')" style="margin-left: 30px" size="small">一键放款</el-button>
      <el-button @click="toggleSelection()" size="small">取消选择</el-button>
    </div>
    <div>
      <el-row style="height: 35px;">&nbsp;</el-row>
    </div>
  </d2-container>
</template>
<script>
import { regObj } from '@/libs/common'
import { queryRecentOrders, loanTransferSucc } from '@/api/tools/tool-loanTransfer'

export default {
  data() {
    return {
      // 时间控件快捷操作选项
      pickerOptions1: {
        shortcuts: [
          {
            text: '今天',
            onClick(picker) {
              picker.$emit('pick', new Date())
            }
          },
          {
            text: '昨天',
            onClick(picker) {
              const date = new Date()
              date.setTime(date.getTime() - 3600 * 1000 * 24)
              picker.$emit('pick', date)
            }
          },
          {
            text: '一周前',
            onClick(picker) {
              const date = new Date()
              date.setTime(date.getTime() - 3600 * 1000 * 24 * 7)
              picker.$emit('pick', date)
            }
          }
        ]
      },
      transfertime: '',
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
      multipleSelection: [],
      tableData: [],
      // 默认每页数据量
      pagesize: 10,
      // 当前页码
      currentPage: 1,
      // 默认数据总数
      totalCount: 0,
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
    // 一键放款
    submitForm(formName) {
      var transfertime = ''
      if (this.transfertime !== '') {
        transfertime = this.transfertime.getTime()
      }
      var myDate = new Date()
      var currenttime = myDate.getTime()
      if (this.multipleSelection.length === 0) {
        this.$msgbox({
          title: '提示',
          type: 'warning',
          message: '请选择需要放款的订单',
          closeOnPressEscape: true,
          confirmButtonText: '确定'
        })
      } else if (transfertime !== '' && transfertime > currenttime) {
        this.$msgbox({
          title: '提示',
          type: 'warning',
          message: '放款时间不能晚于当前时间',
          closeOnPressEscape: true,
          confirmButtonText: '确定'
        })
      } else {
        var orderno = []
        var len = this.multipleSelection.length
        for (var i = 0; i < len; i++) {
          orderno.push(this.multipleSelection[i].orderNo.toString())
        }
        loanTransferSucc({
          orderNo: orderno,
          env: this.form.env,
          transferTime: transfertime
        }).then(resp => {
          this.$message.success(resp.desc.toString())
        })
      }
    },
    // 获取待放款订单数据
    loadData(mobile, env) {
      queryRecentOrders({
        phone: mobile,
        env: env
      }).then(resp => {
        if (resp.tableData.length === 0) {
          this.tableData = []
          this.totalCount = resp.totalNum
          this.$message.warning('未查询到待放款的订单')
        } else {
          this.tableData = resp.tableData
          this.totalCount = resp.totalNum
        }
      })
    },
    search(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          this.loadData(this.form.mobile, this.form.env)
        } else {
          return false
        }
      })
    },
    toggleSelection(rows) {
      if (rows) {
        rows.forEach(row => {
          this.$refs.multipleTable.toggleRowSelection(row)
        })
      } else {
        this.$refs.multipleTable.clearSelection()
      }
    },
    handleSelectionChange(val) {
      this.multipleSelection = val
    },
    resetForm(formName) {
      this.$refs[formName].resetFields()
      this.transfertime = ''
    }
  }
}
</script>
