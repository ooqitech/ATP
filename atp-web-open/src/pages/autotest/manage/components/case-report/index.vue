<template>
  <d2-container>
    <div style="text-align: center;font-size: 20px;font-weight: 900;color: #2f74ff">
      <span>测试报告通用模板</span>
      <el-button @click="collapseAll">全部折叠</el-button>
    </div>
    <!-- 测试报告基础模板  -->
    <div class="caseReportForm">
      <el-form ref="baseForm" :model="baseForm" inline>
        <el-form-item label="任务名称：" style="margin-left: 10px">
          <span>{{baseForm.taskName}}</span>
        </el-form-item>
        <el-form-item label="测试结论：">
          <span style="color: red;font-weight: bolder" v-if="baseForm.testResult === '失败'">{{baseForm.testResult}}</span>
          <span style="color: forestgreen;font-weight: bolder" v-if="baseForm.testResult === '成功'">{{baseForm.testResult}}</span>
        </el-form-item>
        <el-form-item label="总用例数：">
          <span>{{baseForm.totalCaseNum}}</span>
        </el-form-item>
        <el-form-item label="成功用例数：">
          <span>{{baseForm.succCaseNum}}</span>
        </el-form-item>
        <el-form-item label="失败用例数：">
          <span>{{baseForm.failCaseNum}}</span>
        </el-form-item>
        <el-form-item label="成功率：">
          <span>{{baseForm.succRate}}</span>
        </el-form-item>
        <el-form-item label="运行开始时间：">
          <span>{{baseForm.testStartTime}}</span>
        </el-form-item>
        <el-form-item label="运行结束时间：">
          <span>{{baseForm.testEndTime}}</span>
        </el-form-item>
      </el-form>
      <div class="source">
        <el-tabs type="border-card">
          <el-tab-pane label="接口用例">
            <el-collapse v-model="systemActiveNames" v-for="(item, index) in intfSummary" :key="index">
              <el-collapse-item :name="index">
                <template slot="title">
                  <el-row style="width: 100%">
                    <el-col :span="18">{{item.systemName}}</el-col>
                    <el-col :span="6">
                      <div style="text-align:right; width: 100%">
                        <span style="margin-right: 10px;color: black;font-size: 15px">用例总数：{{item.runCaseNum}}</span>
                        <span style="margin-right: 10px;color: green;font-size: 15px">成功数：{{item.succCaseNum}}</span>
                        <span style="margin-right: 10px;color: red;font-size: 15px">失败数：{{item.failCaseNum}}</span>
                        <span style="margin-right: 10px;font-size: 15px">成功率：{{item.succRate}}</span>
                      </div>
                    </el-col>
                  </el-row>
                </template>
                <div class="source">
                  <el-collapse v-model="intfActiveNames" v-for="(subItem, subIndex) in item.children" :key="subIndex">
                    <el-collapse-item :name="index + subIndex">
                      <template slot="title">
                        <el-row style="width: 100%">
                          <el-col :span="18">{{subItem.intfName}}</el-col>
                          <el-col :span="6">
                            <div style="text-align:right; width: 100%">
                              <span style="margin-right: 10px;color: black;font-size: 13px">用例总数：{{subItem.runCaseNum}}</span>
                              <span style="margin-right: 10px;color: green;font-size: 13px">成功数：{{subItem.succCaseNum}}</span>
                              <span style="margin-right: 10px;color: red;font-size: 13px">失败数：{{subItem.failCaseNum}}</span>
                              <span style="margin-right: 10px;font-size: 13px">成功率：{{subItem.succRate}}</span>
                            </div>
                          </el-col>
                        </el-row>
                      </template>
                      <div class="source">
                        <el-table :data="subItem.tableData" style="width: 100%" max-height="600" :header-cell-style="{color:'black',background:'#eef1f6'}">
                          <el-table-column prop="caseId" label="用例编号"></el-table-column>
                          <el-table-column prop="caseName" label="用例名称"></el-table-column>
                          <el-table-column prop="testResult" label="运行结果">
                            <template slot-scope="scope">
                              <span style="color: red" v-if="scope.row.testResult === '失败'">{{scope.row.testResult}}</span>
                              <span v-else>{{scope.row.testResult}}</span>
                            </template>
                          </el-table-column>
                          <el-table-column prop="failReason" label="错误原因"></el-table-column>
                          <el-table-column label="操作" fixed="right">
                            <template slot-scope="scope">
                              <el-button type="text" @click="getIntfTestResult(scope.$index, scope.row)">查看运行数据</el-button>
                              <el-button type="text" @click="getIntfCaseRunLog(scope.$index, scope.row)">查看运行日志</el-button>
                            </template>
                          </el-table-column>
                        </el-table>
                      </div>
                    </el-collapse-item>
                  </el-collapse>
                </div>
              </el-collapse-item>
            </el-collapse>
          </el-tab-pane>
          <el-tab-pane label="全链路用例">
            <el-collapse v-model="productLineNames" v-for="(item, index) in fullLinkSummary" :key="index">
              <el-collapse-item :name="index">
                <template slot="title">
                  {{item.productLineName}}
                  <span style="margin-left: 30px;color: black;font-size: 15px">用例总数：{{item.runCaseNum}}</span>
                  <span style="margin-left: 10px;color: green;font-size: 15px">成功数：{{item.succCaseNum}}</span>
                  <span style="margin-left: 10px;color: red;font-size: 15px">失败数：{{item.failCaseNum}}</span>
                  <span style="margin-left: 10px;font-size: 15px">成功率：{{item.succRate}}</span>
                </template>
                <div class="source">
                  <el-table :data="item.tableData" style="width: 100%" max-height="600" :header-cell-style="{color:'black',background:'#eef1f6'}">
                    <el-table-column prop="caseId" label="用例编号"></el-table-column>
                    <el-table-column prop="caseName" label="用例名称"></el-table-column>
                    <el-table-column prop="testResult" label="运行结果">
                      <template slot-scope="scope">
                        <span style="color: red" v-if="scope.row.testResult === '失败'">{{scope.row.testResult}}</span>
                        <span v-else>{{scope.row.testResult}}</span>
                      </template>
                    </el-table-column>
                    <el-table-column prop="failReason" label="错误原因"></el-table-column>
                    <el-table-column label="操作" fixed="right">
                      <template slot-scope="scope">
                        <el-button type="text" @click="getFullTestResult(scope.$index, scope.row)">查看运行数据</el-button>
                        <el-button type="text" @click="getFullCaseRunLog(scope.$index, scope.row)">查看运行日志</el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
              </el-collapse-item>
            </el-collapse>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
    <!--运行数据界面-->
    <el-dialog title="运行数据" :visible.sync="runDataVisible" width="80%">
      <el-tabs tab-position="left">
        <el-tab-pane type="border-card" v-for="(item, index) in runData" :key="index">
          <template slot="label">
            <div class="label-view" :title="item.name" v-if="item.failReason === '无'">{{item.name}}</div>
            <div class="label-view" style="color: red" :title="item.name" v-if="item.failReason !== '无'">{{item.name}}</div>
          </template>
          <el-form ref="runDataForm" label-width="150px">
            <el-form-item label="请求request：" prop="request">
              <pre class="pre-style">{{item.request}}</pre>
            </el-form-item>
            <el-form-item label="响应response：" prop="response">
              <pre class="pre-style">{{item.response}}</pre>
            </el-form-item>
            <el-form-item label="校验validators：" prop="validators">
              <el-table :data="item.validators" style="width: 100%" max-height="500" :header-cell-style="tableHeaderColor" :row-style="tableRowStyle">
                <el-table-column prop="comparator" label="断言类型" width="100%"></el-table-column>
                <el-table-column prop="check" label="校验内容"></el-table-column>
                <el-table-column prop="check_value" label="实际值" width="400px"></el-table-column>
                <el-table-column prop="expect" label="期望值" width="400px"></el-table-column>
                <el-table-column prop="check_result" label="校验结果">
                  <template slot-scope="scope">
                    <span v-if="scope.row.check_result === 'pass'" style="color: green">{{scope.row.check_result}}</span>
                    <span v-else style="color: red">{{scope.row.check_result}}</span>
                  </template>
                </el-table-column>
              </el-table>
            </el-form-item>
            <el-form-item label="错误原因failReason：" prop="failReason">
              <pre class="pre-style">{{item.failReason}}</pre>
            </el-form-item>
            <el-form-item label="错误详情failDetail：" prop="failDetail">
              <pre class="pre-style">{{item.failDetail}}</pre>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      <span slot="footer" class="dialog-footer">
        <el-button type="primary" @click="runDataVisible = false">关 闭</el-button>
      </span>
    </el-dialog>
  </d2-container>
</template>

<script>
import { getSummary, getRunDataByTestcase } from '@/api/autotest/manage/case-report'

export default {
  name: 'caseReport',
  // 父组件通过props属性传递进来的数据,包括reportId
  props: {
    reportId: {
      type: Number,
      default: () => {
        return null
      }
    }
  },
  data() {
    return {
      taskRunId: null,
      baseForm: {
        taskName: '',
        testResult: '',
        totalCaseNum: '',
        succCaseNum: '',
        failCaseNum: '',
        succRate: '',
        testStartTime: '',
        testEndTime: ''
      },
      systemActiveNames: [],
      intfActiveNames: [],
      intfSummary: [],
      productLineNames: [],
      fullLinkSummary: [],
      runDataVisible: false,
      runData: []
    }
  },
  mounted() {
    this.taskRunId = this.$router.currentRoute.query.taskRunId
    this.getSummary(this.taskRunId)
  },
  methods: {
    // 修改table header的背景色
    tableHeaderColor({ row, column, rowIndex, columnIndex }) {
      if (rowIndex === 0) {
        return 'color:black;background:#eef1f6'
      }
    },
    // 修改table tr行的背景色
    tableRowStyle({ row, rowIndex }) {
      if (row.check_result !== 'pass') {
        return 'background-color: pink;'
      }
    },
    // 根据测试报告ID查询测试报告详情
    getSummary(id) {
      getSummary({ taskRunId: parseInt(id) }).then(res => {
        this.intfSummary = res.intfSummary
        this.fullLinkSummary = res.fullLinkSummary
        this.baseForm = res.base
        if (res.base.succRate === '100%') {
          this.baseForm['testResult'] = '成功'
        } else {
          this.baseForm['testResult'] = '失败'
        }
      })
    },
    // 折叠全部
    collapseAll() {
      this.systemActiveNames = []
      this.intfActiveNames = []
      this.productLineNames = []
    },
    // 查看接口用例运行数据
    getIntfTestResult(index, row) {
      this.runData = []
      getRunDataByTestcase({
        taskRunId: parseInt(this.taskRunId),
        testcaseId: row.caseId
      }).then(res => {
        this.runDataVisible = true
        let runData = res.runData
        runData.forEach(item => {
          item['request'] = JSON.stringify(item['request'], null, 4)
          item['response'] = JSON.stringify(item['response'], null, 4)
          item['failReason'] = item['failReason'] ? item['failReason'] : '无'
          item['failDetail'] = item['failDetail'] ? item['failDetail'] : '无'
          item['validators'].forEach(subItem => {
            subItem['check_value'] = JSON.stringify(subItem['check_value'], null, 0)
            subItem['expect'] = JSON.stringify(subItem['expect'], null, 0)
          })
        })
        this.runData = runData
      })
    },
    // 查看全链路用例运行数据
    getFullTestResult(index, row) {
      this.runData = []
      getRunDataByTestcase({
        taskRunId: parseInt(this.taskRunId),
        testcaseMainId: row.caseId
      }).then(res => {
        this.runDataVisible = true
        let runData = res.runData
        runData.forEach(item => {
          item['request'] = JSON.stringify(item['request'], null, 4)
          item['response'] = JSON.stringify(item['response'], null, 4)
          item['failReason'] = item['failReason'] ? item['failReason'] : '无'
          item['failDetail'] = item['failDetail'] ? item['failDetail'] : '无'
          item['validators'].forEach(subItem => {
            subItem['check_value'] = JSON.stringify(subItem['check_value'], null, 0)
            subItem['expect'] = JSON.stringify(subItem['expect'], null, 0)
          })
        })
        this.runData = runData
      })
    },
    // 查询接口用例运行日志
    getIntfCaseRunLog(index, row) {
      let intfId = null
      // eslint-disable-next-line no-labels
      flag: for (var i = 0, len = this.intfSummary.length; i < len; i++) {
        for (var j = 0, subLen = this.intfSummary[i].children.length; j < subLen; j++) {
          let obj = this.intfSummary[i].children[j].tableData.find(c => c.caseId === row.caseId)
          console.log(this.intfSummary[i].children[j])
          if (obj) {
            intfId = this.intfSummary[i].children[j].intfId
            break flag
          }
        }
      }
      let postParams = {
        taskRunId: this.taskRunId,
        intfId: intfId,
        testcaseId: row.caseId,
        isMain: false
      }
      const { href } = this.$router.resolve({
        name: 'realTimeLog',
        query: {
          postParams: JSON.stringify(postParams)
        }
      })
      window.open(href, '_blank')
    },
    // 查询全链路用例运行日志
    getFullCaseRunLog(index, row) {
      let postParams = {
        taskRunId: this.taskRunId,
        testcaseId: row.caseId,
        isMain: true
      }
      const { href } = this.$router.resolve({
        name: 'realTimeLog',
        query: {
          postParams: JSON.stringify(postParams)
        }
      })
      window.open(href, '_blank')
    }
  }
}
</script>

<style lang="scss">
/*页面边框*/
.caseReportForm {
  border: 1px solid #ebebeb;
  border-radius: 3px;
  transition: 0.2s;
  .source {
    padding: 5px;
  }
}

/* 用例编辑页面各元素样式 */
.caseReportForm .el-collapse {
  .el-collapse-item__header {
    margin-top: 10px;
    height: 30px;
    line-height: 30px;
    color: #2f74ff;
    cursor: pointer;
    /*border-bottom: 1px solid #ebeef5;*/
    font-size: 16px;
    font-weight: bold;
    background-color: #66b1ff1f;
    .el-collapse-item__arrow {
      line-height: 40px;
    }
  }
  .el-collapse-item__content {
    margin-top: 5px;
    padding-bottom: 0;
  }
}

.caseReportForm .el-collapse .el-collapse {
  .el-collapse-item__header {
    margin-top: 10px;
    height: 30px;
    line-height: 30px;
    color: #2f74ff;
    cursor: pointer;
    /*border-bottom: 1px solid #ebeef5;*/
    font-size: 14px;
    font-weight: bold;
    background-color: rgba(255, 203, 29, 0.11);
    .el-collapse-item__arrow {
      line-height: 40px;
    }
  }
  .el-collapse-item__content {
    margin-top: 5px;
    padding-bottom: 0;
  }
}

.caseReportForm .el-form-item {
  margin-left: 80px;
  font-weight: bold;
}

.caseReportForm .el-form-item .el-form-item__content {
  display: table;
  font-weight: normal;
}

.el-collapse-item__content .el-form.el-form-item--mini.el-form-item,
.el-collapse-item__content .el-form .el-form-item--small.el-form-item {
  margin-bottom: 15px;
}
.label-view:hover {
  height: auto;
  word-break: break-all;
  text-decoration: underline;
  cursor: pointer;
  white-space: nowrap;
}
.label-view {
  width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  text-align: left;
}

.pre-style {
  outline: 1px solid #ccc;
  padding: 5px;
  margin: 5px;
  line-height: normal;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.el-table__body tr:hover > td {
  background-color: initial !important;
}
</style>
