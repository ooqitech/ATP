<template>
  <d2-container>
    <div class="table_container">
      <div class="handle-box">
        <el-form ref="baseForm" :model="baseForm" label-width="80px" inline>
          <el-form-item label="项目名称" prop="projectId" :rules="[{ required: true, message: '请选择项目', trigger: 'change' }]">
            <el-select v-model="baseForm.projectId" filterable placeholder="请选择">
              <el-option v-for="item in baseForm.projectOptions" :key="item.projectName" :label="item.projectName" :value="item.id"></el-option>
            </el-select>
          </el-form-item>
          <el-button type="primary" icon="el-icon-search" @click="search('baseForm')">搜 索</el-button>
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
                  <span class="custom-tree-node" slot-scope="{ node, data }">
                    <span class="span">
                      <!--<svg-icon icon-class="folder_open_directory_category_browse" class-name="card-panel-icon" v-show="!node.isLeaf"/>-->
                      <!--<svg-icon icon-class="catalog" class-name="card-panel-icon" v-show="node.isLeaf"/>-->
                      <span>{{node.label}}</span>
                    </span>
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
        <!--<v-contextmenu-item @click="addUrl()">新增域名</v-contextmenu-item>-->
        <!--<v-contextmenu-item @click="exportExcel()">导出系统用例Excel</v-contextmenu-item>-->
        <v-contextmenu-item divider></v-contextmenu-item>
      </v-contextmenu>
    </div>

    <!--树形控件右键菜单_模块-->
    <div>
      <v-contextmenu ref="contextMenuModule">
        <v-contextmenu-item @click="handAddUiCase()">新增自动化用例</v-contextmenu-item>
        <v-contextmenu-item divider></v-contextmenu-item>
      </v-contextmenu>
    </div>
    <!-- 导出框 -->
    <el-dialog title="导出系统所有用例" :visible.sync="exportVisible" width="300px" center>
      <div class="ecport" style="margin-left: 10%">
        <a :href="downloadXmindTempUrl">
          <el-button type="primary" @click="exported">导出模块下所有用例</el-button>
        </a>
      </div>
    </el-dialog>
  </d2-container>
</template>

<script>
import { fetchUiProjectList, subtreeUiProject } from '@/api/autotest/manage/resource-projectManage'
import { queryByTestsuiteId } from '@/api/autotest/manage/testcase-testCaseConfig/testcase'
import { mapMutations } from 'vuex'
import { compare } from '@/libs/common'
import { exportSystemCase, exportSystemCaseExcel } from '@/api/autotest/manage/testcase-testCaseConfig/system'
export default {
  name: 'uiautomation',
  components: {
    caseTable: () => import('./components-table')
  },
  data() {
    return {
      downloadXmindTempUrl: '',
      exportVisible: false,

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
      systemEditForm: { systemName: '', url: '' },
      suiteEditForm: { suiteName: '' },
      projectId: '',
      systemId: '',
      moduleId: '',
      suiteId: '',
      nodeKey: '',
      parentNodeKey: ''
    }
  },
  created() {
    this.getProject()
  },

  methods: {
    ...mapMutations({
      changeUiCaseTableStatus: 'd2admin/casetable/changeUiCaseTableStatus',
      addUiCase: 'd2admin/casetable/addUiCase'
    }),

    handAddUiCase() {
      this.addUiCase(true)
    },
    filterNode(value, data) {
      if (!value) return true
      return data.label.indexOf(value) !== -1
    },

    getProjectSubTree(id) {
      subtreeUiProject({ id: id }).then(res => {
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
      })
    },
    search(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          this.getProjectSubTree(this.baseForm.projectId)
          this.projectId = this.baseForm.projectId
        }
      })
    },
    getProject() {
      fetchUiProjectList({}).then(res => {
        this.baseForm.projectOptions = res.desc.sort(compare('projectName'))
      })
    },
    exportXmind() {
      exportSystemCase({ systemId: this.systemId, projectId: this.projectId }).then(res => {
        this.downloadXmindTempUrl = '/atp/download/' + res.desc
      })
      this.exportVisible = true
    },
    exportExcel() {
      exportSystemCaseExcel({ systemId: this.systemId }).then(res => {
        this.downloadXmindTempUrl = '/atp/download/' + res.desc
      })
      this.exportVisible = true
    },
    exported() {
      this.exportVisible = false
    },
    handleNodeClick(data, node) {
      this.$refs['contextMenuSystem'].hide()
      this.$refs['contextMenuModule'].hide()
      if ('systemId' in data) {
        this.systemId = data.systemId
      }
      let moduleId = ''
      if ('moduleId' in data) {
        moduleId = data.moduleId
        this.systemId = node.parent.data.systemId
      }
      let UiCaseTable = {
        systemId: this.systemId,
        moduleId: moduleId
      }
      this.changeUiCaseTableStatus(UiCaseTable)
    },
    rightClick(event, object, value, element) {
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
      } else if (value.isLeaf === true) {
        const position = {
          top: event.clientY,
          left: event.clientX + 20
        }
        this.$refs['contextMenuModule'].show(position)
        this.systemId = value.data.systemId
        this.systemEditForm.systemName = value.data.label
        this.nodeKey = value.key
        this.parentNodeKey = value.parent.key
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

<style scoped>
</style>
