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
      <el-form-item label="业务中心" prop="businesscenter" label-width="80px">
        <el-select v-model="form.businesscenter" placeholder="请选择" @change="isselected">
          <el-option v-for="item in bcoptions" :key="item" :label="item" :value="item"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="项目名称" prop="projectname" label-width="70px">
        <el-select v-model="form.projectname" placeholder="请选择">
          <el-option v-for="item in pnoptions" :key="item" :label="item" :value="item"></el-option>
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
        <el-table-column prop="businessCenter" label="所属中心" sortable width="180"></el-table-column>
        <el-table-column prop="projectName" label="项目名" sortable width="360"></el-table-column>
        <el-table-column prop="interfaceTotal" label="接口总数" width="180"></el-table-column>
        <el-table-column prop="testcaseTotal" label="案例总数" width="180"></el-table-column>
        <el-table-column prop="testcaseSmoking" label="冒烟案例数" width="180"></el-table-column>
        <el-table-column prop="lastTestApr" label="冒烟案例最近一次成功率(%)"></el-table-column>
        <el-table-column prop="lastStartTime" label="冒烟案例最近一次运行时间"></el-table-column>
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
          :page-size="pagesize"
        ></el-pagination>
      </div>
    </div>
  </d2-container>
</template>
<script>
import { queryAutotestDetails } from '@/api/qadata/form-autoTestData'
import { queryAutotestProject } from '@/api/qadata/chart-successRateCount'

export default {
  data() {
    return {
      form: {
        businesscenter: '全部',
        projectname: '全部'
      },
      bcoptions: ['全部'],
      pnoptions: ['全部'],
      alloptions: [],
      // 表格当前页数据
      tableData: [],
      // 默认每页数据量
      pagesize: 10,
      // 当前页码
      currentPage: 1,
      // 默认数据总数
      totalCount: 0,
      rules: {
        businesscenter: [
          {
            validator: (rule, value, callback) => {
              if (this.form.businesscenter === '') {
                callback(new Error('请选择业务中心'))
              } else {
                callback()
              }
            },
            trigger: 'blur,change'
          }
        ],
        projectname: [
          {
            validator: (rule, value, callback) => {
              if (this.form.projectname === '') {
                callback(new Error('请选择项目名称'))
              } else {
                callback()
              }
            },
            trigger: 'blur,change'
          }
        ]
      }
    }
  },
  methods: {
    isselected(value) {
      this.form.projectname = ''
      this.pnoptions = ['全部']
      if (value === '全部') {
        for (let i in this.alloptions) {
          this.pnoptions = this.pnoptions.concat(this.alloptions[i])
        }
        this.form.projectname = '全部'
      } else {
        this.pnoptions = this.pnoptions.concat(this.alloptions[value])
        this.form.projectname = '全部'
      }
    },
    loadData(projectname, businesscenter, pagesize, currentpage) {
      queryAutotestDetails({
        projectName: projectname,
        businessCenter: businesscenter,
        pageSize: pagesize,
        pageNo: currentpage
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
          this.loadData(this.form.projectname, this.form.businesscenter, this.pagesize, this.currentPage)
        } else {
          return false
        }
      })
    },
    handleSizeChange(val) {
      this.pagesize = val
      this.currentPage = 1
      this.loadData(this.form.projectname, this.form.businesscenter, this.pagesize, this.currentPage)
    },
    handleCurrentChange(val) {
      this.currentPage = val
      this.loadData(this.form.projectname, this.form.businesscenter, this.pagesize, this.currentPage)
    },
    resetForm(formName) {
      this.$refs[formName].resetFields()
    }
  },
  mounted() {
    queryAutotestProject({}).then(resp => {
      this.alloptions = resp.desc
      for (let i in this.alloptions) {
        this.bcoptions.push(i)
        this.pnoptions = this.pnoptions.concat(this.alloptions[i])
      }
    })
    this.loadData(this.form.projectname, this.form.businesscenter, this.pagesize, this.currentPage)
  }
}
</script>
