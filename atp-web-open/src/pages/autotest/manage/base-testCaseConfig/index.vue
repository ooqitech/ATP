<template>
  <d2-container>
    <div class="table_container">
      <div class="handle-box">
        <el-form ref="baseForm" :model="baseForm" label-width="80px" inline>
          <el-form-item label="公司名称" prop="projectId" :rules="[{ required: true, message: '请选择公司', trigger: 'change' }]">
            <el-select v-model="baseForm.projectId" filterable placeholder="请选择">
              <el-option v-for="item in baseForm.projectOptions" :key="item.projectName" :label="item.projectName" :value="item.id"></el-option>
            </el-select>
          </el-form-item>
          <el-button type="primary" icon="el-icon-search" @click="search('baseForm')" :loading="searchLoading">搜 索</el-button>
          <el-button type="primary" icon="el-icon-refresh" @click="syncCase()" :loading="synLoading">同步最新git用例</el-button>
        </el-form>
      </div>
      <el-row :gutter="20">
        <!--左树-->
        <el-col :span="6">
          <div v-show="treeVisible" class="example">
            <!--搜索框-->
            <div class="navigation-filter">
              <el-row :gutter="10">
                <el-col :span="20">
                  <el-input placeholder="输入系统/模块关键字" v-model="filterText"></el-input>
                </el-col>
              </el-row>
            </div>
            <!--树状结构-->
            <el-scrollbar wrap-class="list" view-class="view-box" :native="false">
              <div class="category">
                <el-tree
                  :data="treeData"
                  node-key="id"
                  :props="defaultProps"
                  :default-expanded-keys="nodeKeys"
                  :highlight-current="true"
                  :filter-node-method="filterNode"
                  @node-click="handleNodeClick"
                  @node-contextmenu="rightClick"
                  ref="tree"
                >
                  <!--<span class="custom-tree-node" slot-scope="{ node, data }">
                    <span class="span">
                      &lt;!&ndash;<svg-icon icon-class="folder_open_directory_category_browse" class-name="card-panel-icon" v-show="!node.isLeaf"/>&ndash;&gt;
                      &lt;!&ndash;<svg-icon icon-class="catalog" class-name="card-panel-icon" v-show="node.isLeaf"/>&ndash;&gt;
                      <span>{{node.label}}</span>
                    </span>
                  </span>-->
                  <span slot-scope="{ node, data }">
                    <el-tooltip placement="top-start" effect="light" :content="node.label" :open-delay="500">
                      <span style="font-size: 14px">{{ node.label }}</span>
                    </el-tooltip>
                  </span>
                </el-tree>
              </div>
            </el-scrollbar>
          </div>
        </el-col>
        <!--右表-->
        <el-col :span="18">
          <div v-show="treeVisible" class="example">
            <case-table></case-table>
          </div>
        </el-col>
      </el-row>
    </div>

    <!--树形控件右键菜单_一级系统-->
    <div>
      <v-contextmenu ref="contextMenuSystem">
        <v-contextmenu-item @click="handExportModules()">选择模块导出用例</v-contextmenu-item>
        <v-contextmenu-item @click="exportExcel()">导出整个系统用例</v-contextmenu-item>
        <v-contextmenu-item divider></v-contextmenu-item>
      </v-contextmenu>
    </div>
    <!-- 导出整个系统弹出框 -->
    <el-dialog title="导出整个系统用例excel" :visible.sync="exportVisible" width="300px" center>
      <div class="ecport" style="margin-left: 10%">
        <el-button type="primary" @click="exported">导出整个系统用例excel</el-button>
      </div>
    </el-dialog>
    <!-- 选择1-n个模块弹出框 -->
    <el-dialog title="选择模块导出用例excel" :visible.sync="exportModuleVisible" width="50%" center>
      <el-scrollbar wrap-class="list" :native="false">
        <div class="category">
          <el-tree :data="modulesTreeData" show-checkbox default-expand-all node-key="id" ref="tree1" highlight-current :props="defaultProps"></el-tree>
        </div>
      </el-scrollbar>
      <div class="ecportModule" style="margin-left: 30px;margin-top: 10px">
        <el-button type="primary" @click="exportedModules">导出excel</el-button>
      </div>
    </el-dialog>
  </d2-container>
</template>

<script>
import { fetchBaseProjectList, subtreeBaseProject } from '@/api/autotest/manage/resource-projectManage'
import { queryByTestsuiteId } from '@/api/autotest/manage/testcase-testCaseConfig/testcase'
import { mapMutations } from 'vuex'
import { compare } from '@/libs/common'
import { exportSystemCaseExcel, exportModulesCaseExcel, syncBaselineCase } from '@/api/autotest/manage/testcase-testCaseConfig/system'

export default {
  name: 'featurescaseManage',
  components: {
    caseTable: () => import('./components-table')
  },
  data() {
    return {
      modulesTreeData: '',
      modulesList: [],
      downloadSystemTempUrl: '',
      downloadModuleTempUrl: '',
      exportVisible: false,
      exportModuleVisible: false,
      baseForm: {
        projectId: '',
        projectOptions: []
      },
      treeVisible: false,
      filterText: '',
      treeData: [],
      nodeKeys: [],
      currentPage: 1,
      pagesize: 100,
      defaultProps: {
        children: 'children',
        label: 'label'
      },
      moduleEditForm: { moduleName: '' },
      systemEditForm: { systemName: '' },
      suiteEditForm: { suiteName: '' },
      projectId: '',
      systemId: '',
      moduleId: '',
      suiteId: '',
      nodeKey: '',
      parentNodeKey: '',
      timer: '',
      resdata: '',
      searchLoading: false,
      synLoading: false
    }
  },
  created() {
    this.getProject()
  },
  watch: {
    filterText(val) {
      this.$refs.tree.filter(val)
    }
  },

  methods: {
    ...mapMutations({
      changeFeatureCaseTableStatus: 'd2admin/casetable/changeFeatureCaseTableStatus'
    }),
    filterNode(value, data) {
      if (!value) return true
      return data.label.indexOf(value) !== -1
    },
    getProjectSubTree(id) {
      return new Promise((resolve, reject) => {
        subtreeBaseProject({ id: id }).then(res => {
          this.treeVisible = true
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
            }
          })
          this.treeData = res.data.sort(compare('label'))
          resolve(1)
        })
      })
    },
    search(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          this.treeData = []
          this.searchLoading = true
          this.getProjectSubTree(this.baseForm.projectId).then(res => {
            this.searchLoading = false
          })
          this.projectId = this.baseForm.projectId
        }
      })
    },
    syncBaseCase() {
      return new Promise((resolve, reject) => {
        syncBaselineCase({}).then(res => {
          this.resdata = res
          resolve(1)
        })
        setTimeout(() => {
          resolve(0)
        }, 10000)
      })
    },
    // 循环查看是否同步成功timeout of 15s
    syncCase() {
      this.synLoading = true
      this.syncBaseCase().then(res => {
        this.synLoading = false
        if (this.resdata.code === '000') {
          this.$message.success('同步成功')
          clearInterval(this.timer)
          this.loadingVisible = false
        } else if (this.resdata.code === '200') {
          this.$message.success('距离上次同步不到5分钟，请稍后再试')
          clearInterval(this.timer)
          this.loadingVisible = false
        } else if (this.resdata.code === '300') {
          clearInterval(this.timer)
          this.loadingVisible = false
          this.$message.error('拉取失败')
        }
      })
    },
    getProject() {
      fetchBaseProjectList({}).then(res => {
        this.baseForm.projectOptions = res.desc.sort(compare('projectName'))
      })
    },
    exportExcel() {
      this.downloadSystemTempUrl = ''
      this.$message.info('正在导出,请稍等')
      exportSystemCaseExcel({ systemId: this.systemId }).then(res => {
        this.downloadSystemTempUrl = '/atp/download/' + res.desc
        if (res.code === '000') {
          this.exportVisible = true
        }
      })
    },
    exportedModules() {
      this.modulesList = []
      this.$refs.tree1.getCheckedNodes(false, false).forEach(item => {
        if (item.moduleId_last) {
          this.modulesList.push(item.moduleId_last)
        }
      })
      exportModulesCaseExcel({ systemId: this.systemId, moduleList: this.modulesList }).then(res => {
        this.exportModuleVisible = false
        this.downloadModuleTempUrl = '/atp/download/' + res.desc
        window.open(this.downloadModuleTempUrl)
      })
    },
    handExportModules() {
      this.exportModuleVisible = true
      this.downloadModuleTempUrl = ''
      this.modulesList = []
    },
    exported() {
      this.exportVisible = false
      window.open(this.downloadSystemTempUrl)
    },
    handleNodeClick(data, node) {
      this.$refs['contextMenuSystem'].hide()
      let systemId = ''
      let moduleId = ''
      if ('moduleId_last' in data) {
        systemId = node.parent.parent.data.systemId
        moduleId = data.moduleId_last
      }
      let featureCaseTable = {
        systemId: systemId,
        moduleId: moduleId
      }
      this.changeFeatureCaseTableStatus(featureCaseTable)
    },
    rightClick(event, object, value) {
      console.log(object, value)
      this.$refs.tree.setCurrentKey(value.key)
      if (value.level === 1) {
        const position = {
          top: event.clientY,
          left: event.clientX + 20
        }
        this.$refs['contextMenuSystem'].show(position)
        this.systemId = value.data.systemId
        this.systemEditForm.systemName = value.data.label
        this.nodeKey = value.key
        this.parentNodeKey = value.parent.key
        this.modulesTreeData = object.children
      }
    },
    // 根据测试集ID查询测试用例列表
    queryTestCases() {
      queryByTestsuiteId({
        testsuite_id: this.caseTable.suiteId,
        pageNo: this.currentPage,
        pageSize: this.pagesize
      }).then(res => {
        this.tableData = res.desc
        this.totalCount = res.totalNum
      })
    }
  }
}
</script>

<style lang="scss">
.example {
  padding: 10px;
  height: 100%;
  min-height: 720px;
  box-shadow: 0 1px 12px 3px rgba(0, 0, 0, 0.1);
}

.table_container {
  padding: 10px;
}

.handle-box {
  margin-bottom: 10px;
}

.handle-input {
  width: 300px;
  display: inline-block;
}

.del-dialog-cnt {
  font-size: 16px;
  text-align: center;
}

.demo-table-expand {
  font-size: 0;
}

.demo-table-expand label {
  width: 90px;
  color: #99a9bf;
}

.demo-table-expand .el-form-item {
  margin-right: 0;
  margin-bottom: 0;
  width: 50%;
}

.navigation-filter {
  padding: 5px 10px;
}

.list {
  max-height: 700px;
}

.category-description {
  text-indent: 2em;
}

.category {
  margin-bottom: 20px;
  .el-tree-node__content {
    height: 30px;
  }
}

.el-tree--highlight-current .el-tree-node.is-current > .el-tree-node__content {
  background-color: #3a8ee62b;
}

.el-tree-node > .el-tree-node__children {
  overflow: inherit;
}

.list {
  max-height: 700px;
}
</style>
