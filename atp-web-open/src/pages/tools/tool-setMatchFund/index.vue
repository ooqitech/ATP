<template>
  <d2-container>
    <el-form :model="form" ref="setMatchFund" label-width="120px" size="small" inline>
      <el-form-item label="测试环境" prop="env" :rules="[{ required: true, message: '测试环境必填', trigger: 'change'}]">
        <el-select v-model="form.env" placeholder="请选择">
          <el-option v-for="item in envOptions" :key="item.value" :label="item.label" :value="item.value"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="refresh" :loading="loadingVisible">刷新</el-button>
        <el-button type="primary" @click="handleAdd">新增规则</el-button>
      </el-form-item>
    </el-form>
    <el-table
      :data="tableData"
      border
      style="width: 100%;margin-top: 15px"
      ref="multipleTable"
      :header-cell-style="{color:'black',background:'#eef1f6'}"
      @selection-change="handleSelectionChange"
      height="560"
      size="medium"
      :row-class-name="tableRowClassName"
    >
      <el-table-column type="selection" width="55"></el-table-column>
      <el-table-column prop="id" label="序号" width="80"></el-table-column>
      <el-table-column prop="applyAmount" label="订单金额"></el-table-column>
      <el-table-column prop="termNo" label="订单期数"></el-table-column>
      <el-table-column prop="fundId" label="资方编号"></el-table-column>
      <el-table-column prop="creator" label="创建人"></el-table-column>
      <el-table-column prop="createTime" label="创建时间"></el-table-column>
      <el-table-column prop="isModified" label="是否被修改">
        <template slot-scope="scope">
          <span v-if="scope.row.isModified">是</span>
          <span v-else>否</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template slot-scope="scope">
          <el-button type="text" @click="handleDelete(scope.$index, scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <!-- 编辑弹出框 -->
    <el-dialog title="配置" :visible.sync="editVisible" width="30%" :close-on-click-modal="false" :close-on-press-escape="false" ref="editDialog">
      <el-form :model="editForm" ref="setMatchFund" label-width="120px" size="small">
        <el-form-item
          label="订单金额(分)"
          prop="applyAmount"
          :rules="[
        { required: true, message: '订单金额必填', trigger: 'blur'},
        { type: 'number', message: '订单金额必须为数字', trigger: 'blur'}]"
        >
          <el-input type="applyAmount" v-model.number="editForm.applyAmount" placeholder="请输入订单金额" auto-complete="off" style="width: 210px"></el-input>
        </el-form-item>
        <el-form-item label="订单期数" prop="termNo" :rules="[{ required: true, message: '订单期数必填', trigger: 'change'}]">
          <el-select v-model="editForm.termNo" placeholder="请选择">
            <el-option v-for="item in termNoOptions" :key="item" :label="item" :value="item"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="资方编号" prop="fundId" :rules="[{ required: true, message: '资方编号必填', trigger: 'change'}]">
          <el-select v-model="editForm.fundId" placeholder="请选择">
            <el-option v-for="item in fundIdOptions" :key="item" :label="item" :value="item"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitForm('setMatchFund')">提交</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>
  </d2-container>
</template>
<script>
import { setFundMatch, queryFundMatchSettings, deleteFundMatch } from '@/api/tools/tool-setMatchFund'

export default {
  data() {
    return {
      form: {
        env: 'ALIUAT'
      },
      // 配置表单默认值
      editForm: {
        applyAmount: '',
        termNo: '',
        fundId: ''
      },
      // 表格数据
      tableData: [],
      // 测试环境选项
      envOptions: [
        {
          value: 'ALIUAT',
          label: 'ALIUAT'
        }
      ],
      editVisible: false,
      loadingVisible: false,
      // 期数选项
      termNoOptions: [3, 6, 9, 12, 18, 24],
      // 资方编号选项
      fundIdOptions: [
        '030-小雨点',
        '038-汇鑫',
        '039-微神马',
        '043-颖东',
        '044-苏宁小贷',
        '045-龙信',
        '046-微神马现金贷',
        '047-晋商',
        '048-东方小贷',
        '049-东方小贷现金贷',
        '051-海尔云贷',
        '052-苏宁现金贷',
        '053-苏宁小雨点',
        '055-海尔云贷现金贷',
        '056-苏宁微神马现金贷'
      ]
    }
  },
  mounted() {
    this.queryExistConfig()
  },
  methods: {
    // 查询已配置的资方匹配规则
    queryExistConfig() {
      return new Promise((resolve, reject) => {
        queryFundMatchSettings({ env: this.form.env }).then(res => {
          this.tableData = res.data
          resolve(1)
        })
      })
    },
    // 刷新
    refresh() {
      this.loadingVisible = true
      this.tableData = []
      this.queryExistConfig().then(() => {
        this.loadingVisible = false
        this.$message.success('刷新成功')
      })
    },
    handleSelectionChange() {},
    handleAdd() {
      this.editVisible = true
      this.$nextTick(function() {
        this.$refs.setMatchFund.resetFields()
      })
    },
    // 提交表单事件
    submitForm(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          setFundMatch({
            env: this.form.env,
            applyAmount: this.editForm.applyAmount,
            termNo: this.editForm.termNo,
            fundId: this.editForm.fundId.split('-')[0]
          }).then(resp => {
            this.editVisible = false
            this.queryExistConfig()
            this.$message.success(resp.desc)
          })
        } else {
          return false
        }
      })
    },
    handleDelete(index, row) {
      this.$confirm('此操作将永久删除该配置, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
        .then(() => {
          deleteFundMatch({ env: this.form.env, id: row.id }).then(res => {
            this.queryExistConfig()
            this.$message.success(res.desc)
          })
        })
        .catch(() => {
          this.$message({
            type: 'info',
            message: '已取消'
          })
        })
    },
    tableRowClassName({ row, rowIndex }) {
      if (row.isModified) {
        return 'warning-row'
      }
      return ''
    }
  }
}
</script>
<style scoped lang="scss">
/deep/.el-table .warning-row {
  background: oldlace;
  color: red;
}
</style>
