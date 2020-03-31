<template>
  <d2-container>
    <div class="table_container">
      <div class="handle-box">
        <el-form ref="baseForm" :model="baseForm" label-width="80px" inline>
          <el-form-item label="公司名称" prop="companyId" :rules="[{required:true,message:'请选择公司',trigger:'change'}]">
            <el-select v-model="baseForm.companyId" filterable placeholder="请选择公司" @change="search">
              <el-option v-for="item in companyTableData" :key="item.companyId" :label="item.companyName" :value="item.companyId"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-input v-model="baseForm.regressionName" placeholder="请输入回归测试名称过滤，支持模糊匹配" class="handle-input mr10"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button icon="el-icon-refresh" type="primary" @click="refreshRegress()" :loading="refreshLoading">查询</el-button>
          </el-form-item>
          <el-form-item>
            <el-button @click="downloadSmokingTestLog()" :loading="butStat">下载运行日志</el-button>
          </el-form-item>
        </el-form>
      </div>
      <el-table :data="tableData" border style="width: 100%" ref="multipleTable" :header-cell-style="{color:'black',background:'#eef1f6'}" size="medium">
        <el-table-column prop="taskId" label="任务ID" width="90" sortable></el-table-column>
        <el-table-column prop="taskName" label="任务名称" width="210" sortable></el-table-column>
        <!--<el-table-column prop="projectName" label="所属项目">-->
        <!--</el-table-column>-->
        <el-table-column prop="taskType" label="测试范围" width="80">
          <template slot-scope="scope">
            <span v-if="scope.row.taskType === 1">人工指定</span>
            <span v-else-if="scope.row.taskType === 3">冒烟用例</span>
            <span v-else>基于代码变更</span>
          </template>
        </el-table-column>
        <el-table-column prop="totalCaseNum" label="总用例数" width="80"></el-table-column>
        <!--<el-table-column prop="runCaseNum" label="执行用例数">
        </el-table-column>
        <el-table-column prop="successCaseNum" label="成功用例数">
        </el-table-column>
        <el-table-column prop="failCaseNum" label="失败用例数">
        </el-table-column>-->
        <el-table-column prop="successRate" label="最近一次成功率" width="120">
          <template slot-scope="scope">
            <span v-if="scope.row.successRate === '100%'">{{scope.row.successRate}}</span>
            <span v-else style="color: red;font-weight:bold;">{{scope.row.successRate}}</span>
          </template>
        </el-table-column>
        <el-table-column prop="envName" label="运行环境" width="80"></el-table-column>
        <el-table-column prop="lastDuration" label="运行耗时"></el-table-column>
        <el-table-column prop="lastRunStatus" label="任务状态" width="120">
          <template slot-scope="scope">
            <span v-if="scope.row.lastRunStatus === '运行完成'" style="color: limegreen">{{scope.row.lastRunStatus}}</span>
            <span v-if="scope.row.lastRunStatus === '未运行'" style="color: #333333">{{scope.row.lastRunStatus}}</span>
            <el-button
              type="text"
              v-if="scope.row.lastRunStatus === '运行中' || scope.row.lastRunStatus === '运行中(有任务异常退出)'"
              @click="refreshTaskStaus(scope.$index, scope.row)"
            >{{scope.row.lastRunStatus}}</el-button>
            <el-progress
              :percentage="parseInt(scope.row.runPercent.slice(0,-1))"
              :color="customColorMethod"
              v-if="scope.row.runPercent !== '' && scope.row.runPercent !== '100%'"
            ></el-progress>
          </template>
        </el-table-column>
        <el-table-column prop="lastRunTime" label="运行开始时间"></el-table-column>
        <!--<el-table-column prop="lastExecutor" label="执行者">
        </el-table-column>
        <el-table-column prop="creator" label="创建者">
        </el-table-column>-->
        <el-table-column prop="createTime" label="创建时间"></el-table-column>
        <el-table-column prop="updateTime" label="更新时间"></el-table-column>
        <el-table-column label="操作" width="150">
          <template slot-scope="scope">
            <el-button
              type="primary"
              plain
              size="mini"
              @click="handleRun(scope.$index, scope.row)"
              v-if="scope.row.taskStatus === 1 && scope.row.lastRunStatus !== '运行中'"
            >运行</el-button>
            <el-button type="primary" plain size="mini" @click="viewRunHis(scope.$index, scope.row)">结果</el-button>
          </template>
        </el-table-column>
      </el-table>
      <!--分页-->
      <div class="pagination" style="margin-top: 20px">
        <el-pagination
          @current-change="handleCurrentChange"
          @size-change="handleSizeChange"
          layout="total, sizes, prev, pager, next, jumper"
          :total="totalCount"
          :current-page="currentPage"
          :page-sizes="[5, 10, 15, 20]"
          :page-size="pagesize"
        ></el-pagination>
      </div>
    </div>
    <!--执行测试选择环境页面-->
    <el-dialog title="运行测试" :visible.sync="runVisible" width="45%">
      <el-form ref="runForm" :model="runForm" label-width="100px">
        <el-form-item label="运行环境" prop="envId" :rules="[{ required: true, message: '环境必选', trigger: 'change' }]">
          <el-select v-model="runForm.envId" placeholder="请选择">
            <el-option v-for="item in envList" :key="item.id" :label="item.envName" :value="item.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="运行模式" prop="runMode" :rules="[{ required: true, message: '运行模式必选', trigger: 'change' }]">
          <el-select v-model="runForm.runMode" placeholder="请选择">
            <el-option v-for="item in runForm.modeList" :key="item.index" :label="item.name" :value="item.value"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="运行次数" prop="runTimes">
          <el-input v-model="runForm.runTimes" placeholder="请输入运行次数" auto-complete="off" style="width: 220px"></el-input>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="runVisible = false">取 消</el-button>
        <el-button type="primary" @click="runRegTask()">运 行</el-button>
      </span>
    </el-dialog>
    <!--查看任务历史运行数据界面-->
    <el-dialog title="运行历史" :visible.sync="runHisVisible" width="80%">
      <el-table :data="runHisData" style="width: 100%" max-height="500">
        <el-table-column prop="taskRunId" label="运行任务ID"></el-table-column>
        <el-table-column prop="totalCaseNum" label="总用例数"></el-table-column>
        <el-table-column prop="runCaseNum" label="执行用例数"></el-table-column>
        <el-table-column prop="successCaseNum" label="成功用例数"></el-table-column>
        <el-table-column prop="failCaseNum" label="失败用例数"></el-table-column>
        <el-table-column prop="successRate" label="成功率"></el-table-column>
        <el-table-column prop="envName" label="运行环境"></el-table-column>
        <el-table-column prop="duration" label="运行耗时"></el-table-column>
        <el-table-column prop="startTime" label="运行开始时间"></el-table-column>
        <el-table-column prop="lastExecutor" label="执行者"></el-table-column>
        <el-table-column label="操作" fixed="right" width="200px">
          <template slot-scope="scope">
            <el-button type="text" @click="collectTaskResult(scope.$index, scope.row)">收集结果</el-button>
            <el-button type="text" @click="getTestReport(scope.$index, scope.row)">查看报告</el-button>
            <el-button type="text" @click="reRunFailCase(scope.$index, scope.row)" v-if="scope.row.failCaseNum > 0">失败重跑</el-button>
          </template>
        </el-table-column>
      </el-table>
      <span slot="footer" class="dialog-footer">
        <el-button type="primary" @click="runHisVisible = false">关 闭</el-button>
      </span>
    </el-dialog>
    <!--查看未覆盖接口数据界面-->
    <el-dialog title="未覆盖接口" :visible.sync="uncoveredVisible" width="50%">
      <el-table :data="uncoveredData" style="width: 100%" max-height="500">
        <el-table-column prop="type" label="接口类型" width="100%"></el-table-column>
        <el-table-column prop="intfName" label="接口名称"></el-table-column>
      </el-table>
      <span slot="footer" class="dialog-footer">
        <el-button type="primary" @click="uncoveredVisible = false">关 闭</el-button>
      </span>
    </el-dialog>
  </d2-container>
</template>

<script>
import {
  addTask,
  editTask,
  deleteTask,
  runTask,
  detailTask,
  listSmokingTask,
  getProgress,
  runHistory,
  getUncoveredInfo,
  listForTask,
  reCollectTaskResult,
  exportSmokingTestLogToExcel
} from '@/api/autotest/manage/testTask-smokingTest'
import { fetchCompanyList, subtreeProductLine, subtree } from '@/api/autotest/manage/resource-apiManage/company'
import { queryProjectByCompanyId, getIncludeIntfList } from '@/api/autotest/manage/resource-apiManage/project'
import { getGitBranchNamesBySystemId, queryByCompanyId } from '@/api/autotest/manage/resource-apiManage/system'
import { fetchEnvList } from '@/api/autotest/manage/resource-envManage'
import { compare } from '@/libs/common'

export default {
  name: 'smokingTest',
  data() {
    return {
      idx: -1,
      intfTreeData: [],
      fullTreeData: [],
      tempIntfTreeData: [],
      tempFullTreeData: [],
      selectFullKey: null,
      nodeKeys: [],
      defaultProps: {
        children: 'children',
        label: 'label'
      },
      filterText: '',
      filterFullText: '',
      activeName: 'first',
      taskType: '1',
      taskId: null,
      cfgRegressVisible: false,
      baseForm: {
        companyId: '',
        regressionName: ''
      },
      companyTableData: [],
      regForm: {
        regName: '',
        projectId: '',
        projectOptions: [],
        systemOptions: [],
        branchOptions: [],
        changeSystemForm: {
          changeSystemId: '',
          gitUrl: '',
          changeBranchName: '',
          commitStartId: '',
          commitEndId: ''
        },
        changeSystemList: [],
        changeSystemListForView: [],
        isRelated: false,
        tagList: [],
        // isFilter: false,
        tagOptions: []
      },
      tableData: [], // 任务列表数据
      //                tableDataClone: [],//任务列表数据备份
      envList: [],
      delVisible: false,
      runVisible: false,
      runForm: {
        envId: '',
        runTimes: '',
        runMode: false,
        modeList: [
          {
            name: '顺序执行',
            value: false
          },
          {
            name: '并发执行',
            value: true
          }
        ]
      },
      isSelect: false,
      runHisVisible: false,
      runHisData: [],
      uncoveredVisible: false,
      uncoveredData: [],
      refreshLoading: false,
      failedRetry: false,
      taskRunId: null,
      currentPage: 1, // 当前页
      pagesize: 10, // 分页大小
      totalCount: 100, // 总记录数
      butStat: false // 导出按钮加载状态
    }
  },
  mounted() {
    this.getCompanyList()
    this.queryTagList()
  },
  watch: {
    // 树状筛选接口用例
    filterText(val) {
      this.$refs.intfTree.filter(val)
      // 清除过滤关键字后刷新树列表为初始状态
      if (!val) {
        for (var i = 0; i < this.$refs.intfTree.store._getAllNodes().length; i++) {
          this.$refs.intfTree.store._getAllNodes()[i].expanded = false
        }
      }
      //                if (!val) this.getCompanySubtree(this.baseForm.companyId) // 清除过滤关键字后刷新树列表为初始状态
    },
    // 树状筛选全链路用例
    filterFullText(val) {
      this.$refs.fullTree.filter(val)
      // 清除过滤关键字后刷新树列表为初始状态
      if (!val) {
        for (var i = 0; i < this.$refs.fullTree.store._getAllNodes().length; i++) {
          this.$refs.fullTree.store._getAllNodes()[i].expanded = false
        }
      }
      //                if (!val) this.getFullLineSubTree(this.baseForm.companyId) // 清除过滤关键字后刷新树列表为初始状态
    }
    // 模糊搜索列表中任务
    /* 'baseForm.regressName' (val) {
                if (!val) {
                    this.tableData = JSON.parse(JSON.stringify(this.tableDataClone))
                } else {
                    let match_list = []
                    this.tableDataClone.forEach((item) => {
                        if (item.taskName.indexOf(val) !== -1) {
                            match_list.push(item)
                        }
                    })
                    this.tableData = match_list
                }
            }*/
  },
  methods: {
    customColorMethod(percentage) {
      if (percentage < 30) {
        return '#909399'
      } else if (percentage < 70) {
        return '#e6a23c'
      } else {
        return '#67c23a'
      }
    },
    filterNode(value, data) {
      if (!value) return true
      return data.label.indexOf(value) !== -1
    },
    // 刷新列表数据
    refreshRegress() {
      this.tableData = []
      this.refreshLoading = true
      this.currentPage = 1
      this.pagesize = 10
      this.getTaskList(this.currentPage, this.pagesize, this.baseForm.companyId, this.baseForm.regressionName).then(res => {
        this.refreshLoading = false
      })
    },
    // 获取标签list
    queryTagList() {
      listForTask({}).then(res => {
        this.regForm.tagOptions = res.tags
      })
      /* queryTagList({}).then((res) => {
                    let tagOptions = []
                    let id = 1
                    for (var i in res.tags) {
                        tagOptions.push({
                            id: id,
                            label: i,
                            tagList: res.tags[i],
                            value: ''
                        })
                        id = id++
                    }
                    this.regForm.tagOptions = tagOptions
                })*/
    },
    // 测试范围切换操作
    isChanged() {
      if (this.taskType === '2') {
        this.regForm.isFilter = false
      }
    },
    /* // 是否根据标签过滤
            isFiltered () {
                if (!this.regForm.isFilter) {
                    this.regForm.tagOptions.forEach((i) => {
                        i.value = ''
                    })
                    this.fullTreeData = this.tempFullTreeData
                }
            },
            // 根据标签过滤
            fetchByTags () {
                let tagIdList = []
                this.regForm.tagOptions.forEach((i) => {
                    if (i.value) {
                        tagIdList.push(i.value)
                    }
                })
                subtreeProductLine({companyId: this.baseForm.companyId, tagIdList: tagIdList}).then((res) => {
                    res.data.forEach((i) => {
                        i.label = `${i.label}`
                        if (i.children) {
                            i.children.forEach((j) => {
                                j.label = `${j.label}`
                                if (j.children) {
                                    j.children.forEach((k) => {
                                        k.label = `${k.label}`
                                    })
                                }
                            })
                        }
                    })
                    this.fullTreeData = res.data
                })
            },*/
    // 添加变更系统信息
    handAddChangeSystem() {
      this.$refs.changeSystemForm.validate(valid => {
        this.$refs.changeSystemForm1.validate(valid1 => {
          if (valid && valid1) {
            let data = JSON.parse(JSON.stringify(this.regForm.changeSystemForm))
            let item = this.regForm.changeSystemList.find(c => c.changeSystemId === data.changeSystemId)
            if (item) {
              this.regForm.changeSystemList.splice(this.regForm.changeSystemList.indexOf(item), 1, data)
            } else {
              this.regForm.changeSystemList.push(data)
            }
            this.regForm.changeSystemListForView = JSON.parse(JSON.stringify(this.regForm.changeSystemList))
            this.regForm.changeSystemListForView.forEach(obj => {
              let item = this.regForm.systemOptions.find(c => c.systemId === obj.changeSystemId)
              obj.changeSystemId = item.label
            })
            this.resetForm('changeSystemForm')
            this.resetForm('changeSystemForm1')
            this.regForm.branchOptions = []
          } else {
            return false
          }
        })
      })
    },
    // 搜索功能
    search() {
      this.baseForm.regressionName = ''
      this.getProjectList(this.baseForm.companyId)
      this.getTaskList(1, 10, this.baseForm.companyId, this.baseForm.regressionName)
      this.getCompanySubtree(this.baseForm.companyId)
      this.getFullLineSubTree(this.baseForm.companyId)
      this.getSystem(this.baseForm.companyId)
    },
    // 切换项目触发的选择树重置
    changeProject() {
      this.regForm.isRelated = false
      this.$refs.intfTree.setCheckedNodes([])
    },
    // 关联项目下的接口用例
    isRelated() {
      if (this.regForm.isRelated) {
        getIncludeIntfList({ projectId: this.regForm.projectId }).then(res => {
          let defaultIntfList = res.includeIntfList
          let selectIntfKeys = []
          defaultIntfList.forEach(item => {
            this.intfTreeData.forEach(obj => {
              let val = obj.children.find(c => c.intfId === item)
              if (val !== undefined) {
                selectIntfKeys.push(val.id)
              }
            })
          })
          this.$nextTick(function() {
            this.$refs.intfTree.setCheckedKeys(selectIntfKeys)
          })
        })
      } else {
        this.$refs.intfTree.setCheckedNodes([])
      }
    },
    // 初始化回归测试弹窗
    inital() {
      let _this = this
      _this.filterText = ''
      _this.filterFullText = ''
      _this.fullTreeData = _this.tempFullTreeData
      return new Promise(function(resolve, reject) {
        //                    _this.baseForm.regressName = ''
        _this.taskType = '1'
        _this.$nextTick(function() {
          _this.regForm.changeSystemList = []
          _this.regForm.changeSystemListForView = []
          _this.regForm.branchOptions = []
          _this.regForm.isFilter = false
          _this.regForm.tagList = []
          const _that = _this
          Object.keys(this.regForm.changeSystemForm).forEach(function(key) {
            _that.regForm.changeSystemForm[key] = ''
          })
          _this.resetForm('regForm')
          _this.resetForm('changeSystemForm')
          _this.resetForm('changeSystemForm1')
          _this.$refs.intfTree.setCheckedNodes([])
          _this.$refs.fullTree.setCheckedNodes([])
          for (var i = 0; i < _this.$refs.intfTree.store._getAllNodes().length; i++) {
            _this.$refs.intfTree.store._getAllNodes()[i].expanded = false
          }
          for (var j = 0; i < _this.$refs.fullTree.store._getAllNodes().length; j++) {
            _this.$refs.fullTree.store._getAllNodes()[j].expanded = false
          }
          _this.activeName = 'first'
        })
        resolve(1)
      })
    },
    // 编辑回归测试
    handleEdit(index, row) {
      this.queryTagList()
      this.$message({
        message: '数据加载中...',
        type: 'info',
        duration: 1000
      })
      detailTask({ taskId: row.taskId }).then(res => {
        if (res.code === '000') {
          // 页面初始化
          this.idx = index
          this.cfgRegressVisible = true
          this.isSelect = true
          this.taskId = row.taskId
          const ret = this.inital()
          ret.then(() => {
            // 回填回归测试配置
            this.regForm.regName = res.taskName
            res.tags.forEach(item => {
              this.regForm.tagList.push(item.tagId)
            })
            this.taskType = res.taskType.toString()
            this.regForm.projectId = res.projectId
            if (this.taskType === '1') {
              let selectIntfKeys = []
              res.selectIntfTree.forEach(item => {
                this.intfTreeData.forEach(obj => {
                  let val = obj.children.find(c => c.intfId === item)
                  if (val !== undefined) {
                    selectIntfKeys.push(val.id)
                  }
                })
              })
              this.$nextTick(function() {
                this.$refs.intfTree.setCheckedKeys(selectIntfKeys)
              })
              let selectFullKeys = []
              res.selectFullTree.forEach(item => {
                this.findId(this.fullTreeData, item)
                // console.log(this.fullTreeData, item, this.selectFullKey)
                selectFullKeys.push(this.selectFullKey)
              })
              this.$nextTick(function() {
                this.$refs.fullTree.setCheckedKeys(selectFullKeys)
              })
            } else if (this.taskType === '2') {
              this.regForm.changeSystemList = res.gitDiff
              this.regForm.changeSystemListForView = JSON.parse(JSON.stringify(this.regForm.changeSystemList))
              this.regForm.changeSystemListForView.forEach(obj => {
                let item = this.regForm.systemOptions.find(c => c.systemId === obj.changeSystemId)
                obj.changeSystemId = item.label
              })
            }
          })
        } else {
          this.$message.error(res.desc)
          return false
        }
      })
    },
    findId(obj, val) {
      obj.some(item => {
        if (item.productLineId === val) {
          this.selectFullKey = item.id
          return true
        } else if (item.children.length !== 0) {
          return this.findId(item.children, val)
        }
      })
    },
    // 新增回归测试
    handleAddRegress() {
      this.idx = -1
      this.cfgRegressVisible = true
      this.isSelect = false
      this.queryTagList()
      this.inital()
    },
    // 选择运行环境
    handleRun(index, row) {
      this.runVisible = true
      this.taskId = row.taskId
      this.failedRetry = false
    },
    // 运行测试任务
    runRegTask() {
      this.$refs.runForm.validate(valid => {
        if (valid) {
          let requestParams = {}
          if (this.failedRetry) {
            requestParams = {
              taskId: this.taskId,
              envId: this.runForm.envId,
              runMainCaseInParallel: this.runForm.runMode,
              failedRetry: true,
              taskRunId: this.taskRunId
            }
          } else {
            if (this.runForm.runTimes) {
              requestParams = {
                taskId: this.taskId,
                envId: this.runForm.envId,
                times: this.runForm.runTimes,
                runMainCaseInParallel: this.runForm.runMode
              }
            } else {
              requestParams = {
                taskId: this.taskId,
                envId: this.runForm.envId,
                runMainCaseInParallel: this.runForm.runMode
              }
            }
          }
          this.$message({
            message: '回归任务即将开始运行，请稍候...',
            type: 'info',
            duration: 1000
          })
          this.runVisible = false
          runTask(requestParams).then(res => {
            if (res.code === '000') {
              this.runHisVisible = false
              this.tableData = []
              this.refreshLoading = true
              this.$message.success(res.desc)
              this.getTaskList(this.currentPage, this.pagesize, this.baseForm.companyId, this.baseForm.regressionName).then(res => {
                this.refreshLoading = false
              })
            } else {
              this.$message.error(res.desc)
              return false
            }
          })
        } else {
          return false
        }
      })
    },
    // 更新测试任务运行进度(针对运行中的任务)
    refreshTaskStaus(index, row) {
      getProgress({ taskId: row.taskId }).then(res => {
        this.$message.success('更新成功')
        row.runPercent = res.percent
        row.lastRunStatus = res.desc
        if (res.desc === '运行完成') {
          this.tableData = []
          this.refreshLoading = true
          this.getTaskList(this.currentPage, this.pagesize, this.baseForm.companyId, this.baseForm.regressionName).then(res => {
            this.refreshLoading = false
          })
        }
      })
    },
    // 删除回归测试
    handleDelete(index, row) {
      this.idx = index
      this.taskId = row.taskId
      this.delVisible = true
    },
    // 确定删除
    deleteRow() {
      deleteTask({
        taskId: this.taskId
      }).then(res => {
        if (res.code === '000') {
          this.$message.success(res.desc)
          this.getTaskList(this.currentPage, this.pagesize, this.baseForm.companyId, this.baseForm.regressionName)
        } else {
          this.$message.error(res.desc)
        }
      })
      this.delVisible = false
    },
    // 选择系统后获取该系统对应的分支号
    getBranch() {
      this.$refs.changeSystemForm.validate(valid => {
        if (valid) {
          getGitBranchNamesBySystemId({ gitUrl: this.regForm.changeSystemForm.gitUrl }).then(res => {
            this.regForm.branchOptions = res.data.gitBranchList
            this.$message.success('获取成功')
          })
        } else {
          return false
        }
      })
    },
    // 点击配置界面表格中编辑按钮
    handleEditChangeSys(index, row) {
      let data = JSON.parse(JSON.stringify(row))
      let item = this.regForm.systemOptions.find(c => c.label === data.changeSystemId)
      data.changeSystemId = item.systemId
      this.regForm.changeSystemForm = data
    },
    // 点击配置界面表格中删除按钮
    handleDeleteChangeSyS(index) {
      this.regForm.changeSystemList.splice(index, 1)
      this.regForm.changeSystemListForView.splice(index, 1)
    },
    // 获取公司下接口用例树
    getCompanySubtree(id) {
      subtree({ companyId: id }).then(res => {
        let num = 0
        res.data.forEach(i => {
          i.label = `${i.label}`
          if (i.children) {
            i.children.forEach(j => {
              j.label = `${j.label}`
              if (j.children) {
                j.children.forEach(k => {
                  k.label = `${k.label}`
                })
              }
            })
            i.label = i.label + '(' + i.children.length + ')'
          } else {
            i.label = i.label + '(0)'
          }
          num = num + i.children.length
        })
        let tempTreeData = res.data.sort(compare('label'))
        this.intfTreeData = tempTreeData.filter(function(x) {
          return x.children.length !== 0
        })
        this.tempIntfTreeData = JSON.parse(JSON.stringify(this.intfTreeData))
      })
    },
    // 获取公司全链路用例树
    getFullLineSubTree(id) {
      subtreeProductLine({ companyId: id, withoutTestcase: true }).then(res => {
        this.parseFullLineData(res.data)
        this.fullTreeData = res.data
        this.tempFullTreeData = JSON.parse(JSON.stringify(this.fullTreeData))
      })
    },
    parseFullLineData(data) {
      data.forEach(i => {
        if (i.children.length !== 0) {
          i.label = `${i.label}`
          this.parseFullLineData(i.children)
        }
      })
    },
    // 获取公司下系统列表
    getSystem(id) {
      queryByCompanyId({ companyId: id }).then(res => {
        this.regForm.systemOptions = res.allSystemList
      })
    },
    // 判断选择的系统是否存在git url
    changeSystem() {
      this.regForm.branchOptions = []
      this.regForm.changeSystemForm.gitUrl = ''
      this.resetForm('changeSystemForm1')
      let item = this.regForm.systemOptions.find(c => c.systemId === this.regForm.changeSystemForm.changeSystemId)
      if (item.gitUrl) {
        this.regForm.changeSystemForm.gitUrl = item.gitUrl
      }
    },
    // 保存编辑回归测试
    saveEditReg(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          // 基础信息
          const addPramars = {}
          addPramars['companyId'] = this.baseForm.companyId
          addPramars['projectId'] = this.regForm.projectId
          addPramars['taskName'] = this.regForm.regName
          addPramars['taskType'] = this.taskType
          addPramars['tagIdList'] = this.regForm.tagList
          // 人工指定
          if (this.taskType === '1') {
            // 选择的接口列表
            const IntfTree = this.$refs.intfTree.getCheckedNodes(true, false)
            const selectIntfTree = []
            IntfTree.forEach(item => {
              selectIntfTree.push(item.intfId)
            })
            // 选择的全链路用例列表
            const FullTree = this.$refs.fullTree.getCheckedNodes(true, false)
            const selectFullTree = []
            FullTree.forEach(item => {
              /* if ('testcaseId' in item) {
                                    selectFullTree.push(item.testcaseId)
                                }*/
              selectFullTree.push(item.productLineId)
            })
            console.log('接口树', IntfTree)
            console.log('全链路', FullTree)
            if (selectIntfTree.length === 0 && selectFullTree.length === 0) {
              this.$message.warning('请选择需要运行的接口用例或全链路用例')
              return false
            }
            addPramars['selectIntfTree'] = selectIntfTree
            addPramars['selectFullTree'] = selectFullTree
            console.log('回归测试入参', JSON.stringify(addPramars))
          } else {
            if (this.regForm.changeSystemList.length === 0) {
              this.$message.warning('请添加变更系统')
              return false
            }
            addPramars['gitDiff'] = this.regForm.changeSystemList
            console.log('回归测试入参', JSON.stringify(addPramars))
          }
          // 新增回归测试
          if (this.idx === -1) {
            addTask(JSON.parse(JSON.stringify(addPramars))).then(res => {
              if (res.code === '000') {
                this.$message.success(res.desc)
                this.cfgRegressVisible = false
                this.tableData = []
                this.refreshLoading = true
                this.getTaskList(this.currentPage, this.pagesize, this.baseForm.companyId, this.baseForm.regressionName).then(res => {
                  this.refreshLoading = false
                })
              } else {
                this.$message.error(res.desc)
              }
            })
          } else {
            // 编辑回归测试
            addPramars['taskId'] = this.taskId
            editTask(JSON.parse(JSON.stringify(addPramars))).then(res => {
              if (res.code === '000') {
                this.$message.success(res.desc)
                this.cfgRegressVisible = false
                this.tableData = []
                this.refreshLoading = true
                this.getTaskList(this.currentPage, this.pagesize, this.baseForm.companyId, this.baseForm.regressionName).then(res => {
                  this.refreshLoading = false
                })
              } else {
                this.$message.error(res.desc)
              }
            })
          }
        }
      })
    },
    // 获取公司列表
    getCompanyList() {
      fetchCompanyList({}).then(res => {
        this.companyTableData = res.companyList
        if (res.code === '000') {
          this.baseForm.companyId = res.companyList[0].companyId
          this.getProjectList(this.baseForm.companyId)
          this.getEnvList()
          /* this.getCompanySubtree(this.baseForm.companyId)
                        this.getFullLineSubTree(this.baseForm.companyId)
                        this.getSystem(this.baseForm.companyId)*/
        } else {
          this.$message.error(res.desc)
        }
      })
    },
    // 获取公司下项目
    getProjectList(id) {
      queryProjectByCompanyId({ companyId: id }).then(res => {
        if (res.code === '000') {
          this.regForm.projectOptions = res.projectList
        } else {
          this.$message.error(res.desc)
        }
      })
    },
    // 获取环境信息
    getEnvList() {
      fetchEnvList({ envName: '' }).then(res => {
        if (res.code === '000') {
          this.envList = res.desc
          let obj = this.envList.find(d => d.envName === 'ALIUAT')
          this.runForm.envId = obj.id
          this.getTaskList(1, 10, this.baseForm.companyId, this.baseForm.regressionName)
        } else {
          this.$message.error(res.desc)
        }
      })
    },
    // 获取公司下回归任务列表
    getTaskList(page, num, id, keyWords) {
      return new Promise((resolve, reject) => {
        listSmokingTask({ pageNo: page, pageSize: num, companyId: id, keyWords: keyWords }).then(res => {
          if (res.code === '000') {
            let taskList = res.taskList
            taskList.forEach(item => {
              // 项目id查项目名称
              let obj1 = this.regForm.projectOptions.find(function(x) {
                return x.projectId === item.projectId
              })
              item['projectName'] = obj1 ? obj1['projectName'] : ''
              // 环境id查环境名称
              let obj2 = this.envList.find(function(x) {
                return x.id === item.envId
              })
              item['envName'] = obj2 ? obj2['envName'] : ''
            })
            //                            this.tableDataClone = JSON.parse(JSON.stringify(taskList))
            this.tableData = taskList
            this.totalCount = res.total
          } else {
            this.$message.error(res.desc)
          }
          resolve(1)
        })
      })
    },
    // 查看运行历史
    viewRunHis(index, row) {
      this.taskId = row.taskId
      this.$message({
        message: '数据加载中，请稍候...',
        type: 'info',
        duration: 1000
      })
      runHistory({ taskId: row.taskId }).then(res => {
        this.runHisVisible = true
        let runHisData = res.runHistoryList
        runHisData.forEach(item => {
          // 环境id查环境名称
          let obj2 = this.envList.find(function(x) {
            return x.id === item.envId
          })
          item['envName'] = obj2 ? obj2['envName'] : ''
        })
        this.runHisData = runHisData
      })
    },
    // 查看未覆盖接口
    viewUncoveIntf(index, row) {
      this.$message({
        message: '数据加载中，请稍候...',
        type: 'info',
        duration: 1000
      })
      getUncoveredInfo({ taskId: row.taskId }).then(res => {
        this.uncoveredVisible = true
        this.uncoveredData = res.uncoveredList
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
    // 重新收集测试结果
    collectTaskResult(index, row) {
      this.$confirm('是否重新收集测试结果？', '确认信息', {
        type: 'warning',
        distinguishCancelAndClose: true,
        confirmButtonText: '确定',
        cancelButtonText: '取消'
      }).then(() => {
        this.$message({
          message: '数据加载中，请稍候...',
          type: 'info',
          duration: 1000
        })
        reCollectTaskResult({ taskRunId: row.taskRunId }).then(res => {
          this.$message.success(res.desc)
          runHistory({ taskId: this.taskId }).then(res => {
            let runHisData = res.runHistoryList
            runHisData.forEach(item => {
              // 环境id查环境名称
              let obj2 = this.envList.find(function(x) {
                return x.id === item.envId
              })
              item['envName'] = obj2 ? obj2['envName'] : ''
            })
            this.runHisData = runHisData
          })
        })
      })
    },
    // 重跑失败用例
    reRunFailCase(index, row) {
      this.runForm.envId = row.envId
      this.runForm.runMode = false
      this.failedRetry = true
      this.taskRunId = row.taskRunId
      this.runVisible = true
    },
    // 切换分页
    handleSizeChange(val) {
      this.pagesize = val
      this.getSmokingTestList()
    },
    // 切换分页
    handleCurrentChange(val) {
      this.currentPage = val
      this.getSmokingTestList()
    },
    // 触发分页查询
    getSmokingTestList() {
      return new Promise((resolve, reject) => {
        this.getTaskList(this.currentPage, this.pagesize, this.baseForm.companyId, this.baseForm.regressionName).then(res => {
          resolve(1)
        })
      })
    },
    // 下载运行日志
    downloadSmokingTestLog() {
      this.$message.info('正在导出，请稍候')
      this.butStat = true
      exportSmokingTestLogToExcel({
        pageNo: 1,
        pageSize: 10000,
        companyId: this.baseForm.companyId,
        keyWords: this.baseForm.regressionName
      }).then(res => {
        this.butStat = false
        window.open('/atp/download/' + res.fileName)
      })
    },
    // 重置表单
    resetForm(formName) {
      if (this.$refs[formName] !== undefined) {
        this.$refs[formName].resetFields()
      }
    }
  }
}
</script>

<style lang="scss">
.example_tree {
  padding: 10px;
  height: 100%;
  width: 100%;
  min-height: 330px;
  min-width: 650px;
  box-shadow: 0 1px 12px 3px rgba(0, 0, 0, 0.1);
}

.table_container {
  padding: 10px;
}

.handle-box {
  margin-bottom: 20px;
}

.handle-input {
  width: 300px;
  display: inline-block;
}

.del-dialog-cnt {
  font-size: 16px;
  text-align: center;
}

.list-regression {
  max-height: 400px;
}

.category {
  margin-bottom: 20px;
}
</style>
