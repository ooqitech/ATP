<template>
  <d2-container>
    <div class="table_container">
      <div class="handle-box">
        <el-form ref="baseForm" label-width="80px" class="demo-form-inline" inline :model="baseForm">
          <el-form-item label="公司名称" prop="companyId">
            <el-select v-model="baseForm.companyId" placeholder="请选择" clearable @change="getProject(baseForm.companyId)">
              <el-option v-for="item in baseForm.companyOptions" :key="item.companyName" :label="item.companyName" :value="item.companyId"></el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="项目名称" prop="projectId">
            <el-select v-model="baseForm.projectId" placeholder="请选择" clearable filterable>
              <el-option v-for="item in baseForm.projectOptions" :key="item.projectName" :label="item.projectName" :value="item.projectId"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label=" 执行人" prop="executor">
            <el-select v-model="baseForm.executor" filterable placeholder="请选择" clearable>
              <el-option v-for="item in baseForm.userOptions" :key="item.nickname" :label="item.nickname" :value="item.username"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="开始时间">
            <el-col :span="11">
              <el-date-picker v-model="baseForm.startTime" type="datetime" placeholder="选择日期时间" align="right" :picker-options="pickerOptions1"></el-date-picker>
            </el-col>
          </el-form-item>
          <el-form-item label="结束时间">
            <el-col :span="11">
              <el-date-picker v-model="baseForm.endTime" type="datetime" placeholder="选择日期时间" align="right" :picker-options="pickerOptions1"></el-date-picker>
            </el-col>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="searchreport()">搜 索</el-button>
          </el-form-item>
        </el-form>
      </div>
      <el-table
        ref="multipleTable"
        :data="tableData"
        tooltip-effect="dark"
        border
        style="width: 100%"
        @selection-change="handleSelectionChange"
        :row-class-name="tableRowClassName"
        :header-cell-style="{color:'black',background:'#eef1f6'}"
      >
        <el-table-column type="selection" width="60"></el-table-column>
        <el-table-column prop="id" label="报告ID" width="80"></el-table-column>
        <el-table-column prop="createTime" label="测试时间" width="auto"></el-table-column>
        <el-table-column prop="duration" label="运行时间" width="auto"></el-table-column>
        <el-table-column prop="reportStatus" label="测试结果" width="auto" show-overflow-tooltip></el-table-column>
        <el-table-column prop="creator" label="执行人" width="auto" show-overflow-tooltip></el-table-column>

        <el-table-column label="操作" width="auto" show-overflow-tooltip>
          <template slot-scope="scope" style="float: left">
            <a class="reporturl" :href="tableData[scope.$index].reportUrl" target="view_window" style="float: left">
              <el-button style="float: left" size="small" round type="text">查看报告</el-button>
            </a>
            <el-button size="small" type="text" @click="handleDelete(scope.$index, scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-form class="demo-form-inline" inline style="margin-top: 20px">
        <!--<el-form-item>-->
        <!--<el-button type="primary" @click="toggleSelection()">发送邮件</el-button>-->
        <!--</el-form-item>-->
        <el-form-item style="float: left">
          <div class="pagination">
            <el-pagination
              @current-change="handleCurrentChange"
              @size-change="handleSizeChange"
              layout="total, sizes, prev, pager, next, jumper"
              :total="totalNum"
              :current-page="currentPage"
              :page-sizes="[5, 10, 15, 20]"
              :page-size="pagesize"
            ></el-pagination>
          </div>
        </el-form-item>
      </el-form>
    </div>
    <!--删除提示框-->
    <el-dialog title="提示" :visible.sync="delVisible" width="300px" center>
      <div class="del-dialog-cnt">删除不可恢复，是否确定删除？</div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="delVisible = false">取 消</el-button>
        <el-button type="primary" @click="deleteReport()">确 定</el-button>
      </span>
    </el-dialog>
  </d2-container>
</template>

<script>
import { fetchCompanyList } from '@/api/autotest/manage/resource-apiManage/company'
import { queryProjectByCompanyId } from '@/api/autotest/manage/resource-apiManage/project'
import { queryReport, deletereport } from '@/api/autotest/manage/report-testReport'
import { compare } from '@/libs/common'
import { fetchUsertList } from '@/api/sys/user'

export default {
  name: 'testReport',
  data() {
    return {
      Token: '', // superuser token测试数据
      currentPage: 1,
      pagesize: 10,
      delVisible: false,
      baseForm: {
        companyId: '',
        companyOptions: [],
        projectId: '',
        projectOptions: [],
        executor: '',
        userOptions: [],
        startTime: '',
        endTime: ''
      },
      editForm: {
        reportId: ''
      },
      pageSize: 10,
      tableData: [],
      totalNum: 0,
      multipleSelection: [],
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
      }
    }
  },
  created() {
    this.getCompany()
    this.getUserlist()
  },
  methods: {
    // 获取公司列表
    getCompany() {
      fetchCompanyList({}).then(res => {
        this.baseForm.companyOptions = res.companyList.sort(compare('companyName'))
        this.baseForm.companyId = this.baseForm.companyOptions[0].companyId
        this.getProject(this.baseForm.companyId)
        this.searchreport()
      })
    },
    // 根据公司ID获取项目列表
    getProject(companyId) {
      queryProjectByCompanyId({ companyId: companyId }).then(res => {
        this.baseForm.projectOptions = res.projectList.sort(compare('projectName'))
      })
    },
    getUserlist() {
      fetchUsertList({ pageNo: '1', pageSize: '30' }).then(res => {
        this.baseForm.userOptions = res.tableData.sort(compare('username'))
        this.baseForm.userOptions.push({
          id: 0,
          nickname: '测试计划',
          username: '测试计划'
        })
      })
    },
    searchreport() {
      if (this.baseForm.startTime) {
        this.formattime()
      }
      queryReport({
        companyId: this.baseForm.companyId,
        projectId: this.baseForm.projectId,
        pageNo: this.currentPage,
        pageSize: this.pagesize,
        startTime: this.baseForm.startTime,
        endTime: this.baseForm.endTime,
        executor: this.baseForm.executor
      }).then(res => {
        this.tableData = res.tableData
        this.totalNum = res.totalNum
      })
    },
    formattime() {
      var start = new Date(this.baseForm.startTime)
      var end = new Date(this.baseForm.endTime)
      this.baseForm.startTime
        = start.getFullYear()
        + '-'
        + (start.getMonth() + 1)
        + '-'
        + start.getDate()
        + ' '
        + start.getHours()
        + ':'
        + start.getMinutes()
        + ':'
        + start.getSeconds()
      this.baseForm.endTime
        = end.getFullYear() + '-' + (end.getMonth() + 1) + '-' + end.getDate() + ' ' + end.getHours() + ':' + end.getMinutes() + ':' + end.getSeconds()
    },
    handleDelete(index, row) {
      this.delVisible = true
      console.log('reportid', row.id)
      this.editForm.reportId = row.id
    },
    deleteReport() {
      deletereport({
        reportId: this.editForm.reportId
      }).then(res => {
        this.$message.success(res.desc)
        this.getProject()
      })
      this.delVisible = false
    },
    handleSizeChange(val) {
      this.pagesize = val
      this.searchreport()
    },
    handleCurrentChange(val) {
      this.currentPage = val
      this.searchreport()
    },
    //   toggleSelection(rows) {
    //   if (rows) {
    //     rows.forEach(row => {
    //       this.$refs.multipleTable.toggleRowSelection(row);
    //     });
    //   } else {
    //     this.$refs.multipleTable.clearSelection();
    //   }
    // },
    handleSelectionChange(val) {
      this.multipleSelection = val
    },
    tableRowClassName({ row, rowIndex }) {
      if (row.reportStatus === 'fail') {
        return 'warning-row'
      } else if (row.reportStatus === 'success') {
        return 'success-row'
      }
      return ''
    }
  }
}
</script>

<style lang="scss">
.table_container {
  padding: 10px;
}

/*.el-table .success-row {*/
/*background: #b3e19d;*/
/*}*/
.el-table .warning-row {
  background: oldlace;
}
</style>
