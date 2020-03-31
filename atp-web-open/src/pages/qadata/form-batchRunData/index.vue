<style scoped lang="scss">
.col-title {
  text-align: right;
}

.desc {
  margin-bottom: 20px;
}

.context {
  font-size: 16px;
  font-weight: bold;
}
</style>
<template>
  <d2-container>
    <el-form class="context" :inline="true" :model="form" :rules="rules" ref="autotestDataQuery" size="small">
      <el-form-item label="项目名称" prop="projectName" label-width="80px" :rules="[{ required: true, message: '请选择', trigger: 'change' }]">
        <el-select v-model="form.projectName" placeholder="请选择">
          <el-option v-for="item in pnOptions" :key="item" :label="item" :value="item"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item>
        <div style="margin-left:100px">
          <el-button type="primary" @click="search('autotestDataQuery')">查询</el-button>
          <el-button @click="resetForm('autotestDataQuery')">重置</el-button>
        </div>
      </el-form-item>
    </el-form>
    <div style="margin-top:15px">
      <el-table
        :data="tableData"
        style="width: 100%"
        :default-sort="{prop: 'date', order: 'descending'}"
        :header-cell-style="{color:'black',background:'#eef1f6'}"
        size="small"
      >
        <el-table-column prop="projectName" label="项目名称" sortable width="180"></el-table-column>
        <el-table-column prop="systemName" label="系统名称" sortable width="180"></el-table-column>
        <el-table-column prop="interfaceTotal" label="接口总数" width="180"></el-table-column>
        <el-table-column prop="testcaseTotal" label="自动化用例总数" width="180"></el-table-column>
        <el-table-column prop="testcaseSuccess" label="执行成功数" width="180"></el-table-column>
        <el-table-column prop="testcaseFail" label="执行失败数" width="180"></el-table-column>
        <el-table-column prop="lastTestApr" label="执行成功率(%)"></el-table-column>
        <el-table-column prop="lastStartTime" label="运行开始时间"></el-table-column>
        <el-table-column prop="lastEndTime" label="运行结束时间"></el-table-column>
      </el-table>
      <div align="right">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next, jumper"
          :total="totalCount"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-sizes="[10, 20, 30, 40]"
          :page-size="pageSize"
        ></el-pagination>
      </div>
    </div>
  </d2-container>
</template>
<script>
import { queryBatchRunProject, queryBatchRunData } from '@/api/qadata/form-batchRunData'

export default {
  data() {
    return {
      form: {
        projectName: '全部'
      },
      pnOptions: ['全部'],
      // 表格当前页数据
      tableData: [],
      // 默认每页数据量
      pageSize: 10,
      // 当前页码
      currentPage: 1,
      // 默认数据总数
      totalCount: 0,
      rules: {}
    }
  },
  methods: {
    loadData(projectName, pageSize, currentPage) {
      queryBatchRunData({
        projectName: projectName,
        pageSize: pageSize,
        pageNo: currentPage
      }).then(resp => {
        if (resp.tableData === 'no data') {
          this.tableData = []
          this.totalCount = resp.totalNum
        } else {
          this.tableData = resp.tableData
          this.totalCount = resp.totalNum
        }
      })
    },
    search(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          this.loadData(this.form.projectName, this.pageSize, this.currentPage)
        } else {
          return false
        }
      })
    },
    handleSizeChange(val) {
      this.pageSize = val
      this.currentPage = 1
      this.loadData(this.form.projectName, this.pageSize, this.currentPage)
    },
    handleCurrentChange(val) {
      this.currentPage = val
      this.loadData(this.form.projectName, this.pageSize, this.currentPage)
    },
    resetForm(formName) {
      this.$refs[formName].resetFields()
    }
  },
  mounted() {
    queryBatchRunProject({}).then(resp => {
      this.pnOptions = this.pnOptions.concat(resp.desc)
    })
    this.loadData(this.form.projectName, this.pageSize, this.currentPage)
  }
}
</script>
