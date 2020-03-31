<template>
  <d2-container>
    <div class="table_container">
      <el-tabs type="border-card" @tab-click="handleClick">
        <el-tab-pane v-for="(item, index) in companyList" :key="index" :label="item.companyName">
          <el-table :data="resultData[index]" style="width: 100%" max-height="650" size="medium">
            <el-table-column prop="totalCaseNum" label="总用例数"></el-table-column>
            <el-table-column prop="runCaseNum" label="运行用例数"></el-table-column>
            <el-table-column prop="notRunCaseNum" label="未运行用例数"></el-table-column>
            <el-table-column prop="succCaseNum" label="运行成功用例数"></el-table-column>
            <el-table-column prop="failCaseNum" label="运行失败用例数"></el-table-column>
            <el-table-column prop="succRate" label="运行成功率"></el-table-column>
            <el-table-column prop="runTaskNum" label="运行任务数"></el-table-column>
            <el-table-column prop="runStatusDesc" label="运行结果">
              <template slot-scope="scope">
                <span style="color: red" v-if="scope.row.runStatusDesc === '失败'">{{scope.row.runStatusDesc}}</span>
                <span style="color: forestgreen" v-else>{{scope.row.runStatusDesc}}</span>
              </template>
            </el-table-column>
            <el-table-column prop="runDate" label="运行日期"></el-table-column>
            <el-table-column label="操作" fixed="right">
              <template slot-scope="scope">
                <el-button type="text" @click="viewRunDetail(scope.$index, scope.row)">查看详情</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
      <!--查看任务详情运行数据界面-->
      <el-dialog title="运行详情" :visible.sync="runDetailVisible" width="70%">
        <el-table :data="runDetailData" style="width: 100%" max-height="500" @selection-change="handleSelectionChange" size="medium">
          <el-table-column type="selection" width="55"></el-table-column>
          <el-table-column prop="taskName" label="测试任务名称"></el-table-column>
          <el-table-column prop="projectName" label="所属项目"></el-table-column>
          <el-table-column prop="taskType" label="测试范围">
            <template slot-scope="scope">
              <span v-if="scope.row.taskType === 1">人工指定</span>
              <span v-else>基于代码变更</span>
            </template>
          </el-table-column>
          <el-table-column prop="totalCaseNum" label="总用例数"></el-table-column>
          <el-table-column prop="runCaseNum" label="运行用例数"></el-table-column>
          <el-table-column prop="notRunCaseNum" label="未运行用例数"></el-table-column>
          <el-table-column prop="succCaseNum" label="成功用例数"></el-table-column>
          <el-table-column prop="failCaseNum" label="失败用例数"></el-table-column>
          <el-table-column prop="successRate" label="成功率"></el-table-column>
          <el-table-column prop="envName" label="运行环境"></el-table-column>
          <el-table-column prop="duration" label="运行耗时"></el-table-column>
          <el-table-column prop="runTime" label="运行开始时间"></el-table-column>
          <el-table-column prop="executor" label="执行者"></el-table-column>
          <el-table-column label="操作" fixed="right">
            <template slot-scope="scope">
              <el-button type="text" @click="getTestReport(scope.$index, scope.row)">查看测试报告</el-button>
            </template>
          </el-table-column>
        </el-table>
        <span slot="footer" class="dialog-footer">
          <el-button type="primary" @click="exportExcel">导出EXCEL</el-button>
          <el-button type="primary" @click="runDetailVisible = false">关 闭</el-button>
        </span>
      </el-dialog>
    </div>
  </d2-container>
</template>

<script>
import { fetchCompanyList } from '@/api/autotest/manage/resource-apiManage/company'
import { getRunResults, getRunResultBySingleDay, exportSummaryToExcel } from '@/api/autotest/manage/dataAnalysis-regressionResult'

export default {
  name: 'regressionResult',
  data() {
    return {
      companyList: [],
      companyId: '',
      resultData: [],
      runDetailData: [],
      runDetailVisible: false,
      multipleSelection: [],
      runDate: ''
    }
  },
  mounted() {
    this.getCompanyList()
  },
  methods: {
    // 获取公司列表
    getCompanyList() {
      fetchCompanyList({}).then(res => {
        this.companyList = res.companyList
        res.companyList.forEach(() => {
          this.resultData.push([])
        })
        if (res.code === '000') {
          this.companyId = res.companyList[0].companyId
          this.getRunResultByCompanyId(0)
        } else {
          this.$message.error(res.desc)
        }
      })
    },
    // 根据公司id获取测试任务运行结果
    getRunResultByCompanyId(index) {
      getRunResults({ companyId: this.companyId }).then(res => {
        this.resultData.splice(index, 1, res.dataList)
      })
    },
    // TAB切换
    handleClick(tab, event) {
      this.companyId = this.companyList[tab.index].companyId
      this.getRunResultByCompanyId(tab.index)
    },
    // 查看运行详情
    viewRunDetail(index, row) {
      this.runDate = row.runDate
      this.$message.info('数据获取中，请稍候...')
      getRunResultBySingleDay({ companyId: this.companyId, runDate: row.runDate }).then(res => {
        this.runDetailVisible = true
        this.runDetailData = res.dataList
      })
    },
    // 运行详情列表多选
    handleSelectionChange(val) {
      this.multipleSelection = []
      val.forEach(item => {
        this.multipleSelection.push(item.taskRunId)
      })
    },
    // 查看测试报告
    getTestReport(index, row) {
      const { href } = this.$router.resolve({
        name: 'viewTestReport',
        query: {
          taskRunId: row.taskRunId
        }
      })
      window.open(href, '_blank')
    },
    // 导出执行结果
    exportExcel() {
      this.$message.info('正在导出，请稍候...')
      exportSummaryToExcel({ runDate: this.runDate, taskRunIdList: this.multipleSelection }).then(res => {
        window.open('/atp/download/' + res.fileName)
      })
    }
  }
}
</script>

<style lang="scss">
.scroll-view {
  max-height: 650px;
}
</style>
