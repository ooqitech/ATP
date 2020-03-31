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
        <v-contextmenu-item @click="addPage()">添加页面</v-contextmenu-item>
        <v-contextmenu-item @click="configsystemUrl()">系统环境配置</v-contextmenu-item>
        <v-contextmenu-item divider></v-contextmenu-item>
      </v-contextmenu>
    </div>

    <!--树形控件右键菜单_模块-->
    <div>
      <v-contextmenu ref="contextMenuPage">
        <v-contextmenu-item divider></v-contextmenu-item>
      </v-contextmenu>
    </div>

    <!-- 编辑弹出框 -->
    <el-dialog title="页面配置" :visible.sync="editVisible" width="30%" :close-on-click-modal="false" :close-on-press-escape="false" ref="editDialog">
      <el-form ref="editForm" :model="editForm" label-width="100px">
        <el-form-item label="页面名称" prop="pageName" :rules="[{ required: true, message: '页面名称必填', trigger: 'blur' }]">
          <el-input v-model="editForm.pageName" placeholder="请输入页面名称"></el-input>
        </el-form-item>
        <el-form-item label="描述信息">
          <el-input v-model="editForm.simpleDesc" placeholder="请输入描述新"></el-input>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="editVisible = false">取 消</el-button>
        <el-button type="primary" @click="saveEdit('editForm')">确 定</el-button>
      </span>
    </el-dialog>
    <!-- 系统环境配置弹窗 -->
    <el-dialog title="配置URL" :visible.sync="editUrlVisible" width="40%" :close-on-click-modal="false" :close-on-press-escape="false" ref="editDialog">
      <el-form ref="editForm" :model="systemEditForm" label-width="100px">
        <el-form-item label="系统类型" prop="remoteUrl">
          <el-select v-model="systemEditForm.remoteUrl" placeholder="请选择系统类型">
            <el-option label="web" value="web"></el-option>
            <el-option label="mobile" value="mobile"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="URL/包名" prop="url" :rules="[{ required: true, message: 'URL/APP包名', trigger: 'blur' }]">
          <el-input v-model="systemEditForm.url" placeholder="请输入url"></el-input>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="editUrlVisible = false">取 消</el-button>
        <el-button type="primary" @click="saveEditUrl('editForm')">确 定</el-button>
      </span>
    </el-dialog>
  </d2-container>
</template>

<script>
import { fetchUiProjectList, subtreePage } from '@/api/autotest/manage/resource-projectManage'
import { mapMutations, mapState } from 'vuex'
import { compare } from '@/libs/common'
import { addPage } from '@/api/autotest/manage/testcase-testCaseConfig/pageobject'
import { addSystemUrl, systemConfigDetail } from '@/api/autotest/manage/testcase-testCaseConfig/system'
export default {
  name: 'page',
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
      editForm: {
        pageName: '',
        simpleDesc: ''
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
      systemEditForm: { systemName: '', url: '', remoteUrl: '', systemType: '', runType: '' },
      projectId: '',
      systemId: '',
      moduleId: '',
      suiteId: '',
      nodeKey: '',
      parentNodeKey: '',
      editVisible: false,
      editUrlVisible: false,
      idx: -1
    }
  },
  created() {
    this.getProject()
  },
  computed: {
    ...mapState('d2admin/casetable', ['uiRunEnvForm'])
  },
  methods: {
    ...mapMutations({
      changePageObjectTableStatus: 'd2admin/casetable/changePageObjectTableStatus',
      setUiRunEnv: 'd2admin/casetable/setUiRunEnv'
    }),
    addPage() {
      this.editVisible = true
    },
    // 配置系统运行环境，且同步至vuex
    configsystemUrl() {
      this.editUrlVisible = true
      systemConfigDetail({ systemId: this.systemId }).then(res => {
        this.systemEditForm.url = res.desc.base_host
        this.systemEditForm.remoteUrl = res.desc.remote_host
      })
      if (this.systemEditForm.remoteUrl) {
        let envForm = {
          remoteUrl: this.systemEditForm.remoteUrl
        }
        this.setUiRunEnv(envForm)
      }
    },
    saveEdit(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          if (this.idx === -1) {
            addPage({ pageName: this.editForm.pageName, systemId: this.systemId }).then(res => {
              this.$message.success(res.desc)
            })
          }
          this.editVisible = false
        }
        this.getProjectSubTree(this.projectId)
      })
    },
    saveEditUrl(formName) {
      addSystemUrl({ systemId: this.systemId, url: this.systemEditForm.url, remoteUrl: this.systemEditForm.remoteUrl }).then(res => {
        this.$message.success(res.desc)
      })
      this.editUrlVisible = false
    },
    filterNode(value, data) {
      if (!value) return true
      return data.label.indexOf(value) !== -1
    },

    getProjectSubTree(id) {
      subtreePage({ id: id }).then(res => {
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

    handleNodeClick(data, node) {
      this.$refs['contextMenuSystem'].hide()
      // this.$refs['contextMenuPage'].hide()
      let systemId = ''
      let pageId = ''
      if ('pageId' in data) {
        systemId = node.parent.data.systemId
        pageId = data.pageId
      }
      let pageObjectTable = {
        systemId: systemId,
        pageId: pageId
      }
      this.changePageObjectTableStatus(pageObjectTable)
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
      }
    }
  }
}
</script>

<style scoped>
</style>
