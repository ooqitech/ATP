<style scoped lang="scss">
.limit-width {
  margin-top: 15px;
  font-weight: bold;
}
</style>
<template>
  <d2-container>
    <div class="limit-width">
      <el-form :inline="true" :model="form" :rules="rules" ref="updateLogisticsInfo" size="small">
        <el-form-item label="测试环境" prop="env" required label-width="80px">
          <el-select v-model="form.env" placeholder="请选择" style="width: 150px">
            <el-option v-for="item in options" :key="item.value" :label="item.label" :value="item.value"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="手机号" prop="mobile" required label-width="80px">
          <el-input v-model="form.mobile" placeholder="请输入手机号码" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="search('updateLogisticsInfo')">查询待发货商城订单</el-button>
          <el-button @click="resetForm('updateLogisticsInfo')">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
    <div style="margin-top:10px">
      <el-table
        ref="multipleTable"
        :data="tableData"
        style="width: 100%"
        tooltip-effect="dark"
        @selection-change="handleSelectionChange"
        :header-cell-style="{color:'black',background:'#eef1f6'}"
        size="small"
      >
        <el-table-column type="selection" width="55"></el-table-column>
        <el-table-column prop="orderNo" label="订单编号" width="200"></el-table-column>
        <el-table-column prop="merchandiseName" label="主商品名称" width="600"></el-table-column>
        <el-table-column prop="merchantId" label="所属商户ID" width="100"></el-table-column>
        <el-table-column prop="merchantName" label="所属商户名称" width="150"></el-table-column>
        <el-table-column prop="amount" label="订单金额（分）" width="150"></el-table-column>
        <el-table-column prop="createdDateTime" label="订单创建时间" width="180"></el-table-column>
        <el-table-column prop="status" label="订单状态"></el-table-column>
      </el-table>
    </div>
    <div style="margin-top: 30px">
      <el-button type="primary" @click="submitForm('updateLogisticsInfo')" style="margin-left: 30px" size="small">一键发货</el-button>
      <el-button @click="toggleSelection()" size="small">取消选择</el-button>
    </div>
    <div>
      <el-row style="height: 35px;">&nbsp;</el-row>
    </div>
  </d2-container>
</template>
<script>
import { regObj } from '@/libs/common'
import { queryCollBackOrders, collOrdersDeliver } from '@/api/tools/tool-updateLogisticsInfo'

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
    // 一键发货
    submitForm(formName) {
      if (this.multipleSelection.length === 0) {
        this.$msgbox({
          title: '提示',
          type: 'warning',
          message: '请选择需要发货的订单',
          closeOnPressEscape: true,
          confirmButtonText: '确定'
        })
      } else {
        var orderno = []
        var merchantid = []
        var len = this.multipleSelection.length
        for (var i = 0; i < len; i++) {
          orderno.push(this.multipleSelection[i].orderNo.toString())
          merchantid.push(this.multipleSelection[i].merchantId.toString())
        }
        collOrdersDeliver({
          orderNo: orderno,
          merchantId: merchantid,
          env: this.form.env
        }).then(resp => {
          this.$message.success(resp.desc.toString())
        })
      }
    },
    // 获取待放款订单数据
    loadData(mobile, env) {
      queryCollBackOrders({
        phone: mobile,
        env: env
      }).then(resp => {
        if (resp.tableData.length === 0) {
          this.tableData = []
          this.totalCount = resp.totalNum
          this.$message.warning('未查询到待发货的订单')
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
    }
  }
}
</script>
