<template>
  <d2-container>
    <div class="table_container">
      <div class="handle-box">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form ref="baseForm" :model="baseForm" label-width="80px" inline>
              <el-form-item label="公司名称" prop="companyId" :rules="[{ required: true, message: '请选择公司', trigger: 'change' }]">
                <el-select v-model="baseForm.companyId" filterable placeholder="请选择">
                  <el-option v-for="item in baseForm.companyOptions" :key="item.companyId" :label="item.companyName" :value="item.companyId"></el-option>
                </el-select>
              </el-form-item>
              <el-button type="primary" icon="el-icon-search" @click="search('baseForm')" :loading="searchLoading">搜 索</el-button>
              <el-button type="primary" icon="el-icon-plus" @click="handleAddProject()">新增项目</el-button>
            </el-form>
          </el-col>
          <el-col :span="16">
            <el-form ref="searchForm" :model="searchForm" label-width="80px" inline>
              <el-form-item label="搜索条件" prop="filterCondition" :rules="[{ required: true, message: '请选择搜索条件', trigger: 'change' }]">
                <el-select v-model="searchForm.filterCondition" filterable placeholder="请选择">
                  <el-option v-for="item in searchForm.filterConditions" :key="item" :label="item" :value="item"></el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="搜索值" prop="keyword" :rules="[{ required: true, message: '搜索值必填', trigger: 'blur' }]">
                <el-input v-model="searchForm.keyword" placeholder="请输入搜索值" style="width: 400px"></el-input>
              </el-form-item>
              <el-button type="primary" icon="el-icon-search" @click="queryTestCaseByKeyword('searchForm')">查询用例</el-button>
            </el-form>
          </el-col>
        </el-row>
      </div>
      <el-row>
        <el-col :span="6">
          <div class="example-intf">
            <el-scrollbar wrap-class="intfScrolllist" view-class="view-box" :native="false">
              <div class="category">
                <el-tree
                  :data="treeDataAll"
                  node-key="id"
                  lazy
                  :load="loadNode"
                  :props="props"
                  :default-expanded-keys="nodeKeys"
                  :highlight-current="true"
                  @node-click="handleNodeClick"
                  @node-contextmenu="rightClick"
                  @node-drag-end="handleDragEnd"
                  draggable
                  :allow-drop="allowDrop"
                  :allow-drag="allowDrag"
                  ref="treeAll"
                >
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
        <el-col :span="18">
          <div class="example-intf" v-show="caseTableVisible">
            <case-table :intf-info="intfInfo" ref="caseTable" @update-data="updateData"></case-table>
          </div>
        </el-col>
      </el-row>
    </div>

    <!--树形控件右键菜单_一级项目-->
    <div>
      <v-contextmenu ref="contextMenuProject">
        <v-contextmenu-item @click="handleEditProject()">编辑项目</v-contextmenu-item>
        <v-contextmenu-item @click="handleDeleteProject()">删除项目</v-contextmenu-item>
        <v-contextmenu-item @click="handleIntroduceSystem()">引入工程</v-contextmenu-item>
        <v-contextmenu-item divider></v-contextmenu-item>
        <v-contextmenu-item @click="exportXmindByProject()">导出用例</v-contextmenu-item>
        <!--<v-contextmenu-item @click="exportXmindBySystem()">导出系统</v-contextmenu-item>-->
        <!--<v-contextmenu-item @click="handleUpSystem()">上移</v-contextmenu-item>-->
        <!--<v-contextmenu-item @click="handleDownSystem()">下移</v-contextmenu-item>-->
      </v-contextmenu>
    </div>
    <!--树形控件右键菜单_二级工程-->
    <div>
      <v-contextmenu ref="contextMenuSystem">
        <v-contextmenu-item @click="handleIntroduceInterface()">引入接口</v-contextmenu-item>
        <v-contextmenu-item @click="handleDeleteSyetem()">删除工程</v-contextmenu-item>
        <v-contextmenu-item divider></v-contextmenu-item>
      </v-contextmenu>
    </div>

    <!--树形控件右键菜单_三级接口-->
    <div>
      <v-contextmenu ref="contextMenuSuite">
        <v-contextmenu-item @click="handleAddCase()">添加测试用例</v-contextmenu-item>
        <v-contextmenu-item @click="handleDeleteInterface()" v-if="this.projectId !== -1">删除引入接口</v-contextmenu-item>
        <v-contextmenu-item divider></v-contextmenu-item>
        <!--<v-contextmenu-item @click="handleEditSuite()">修改测试集</v-contextmenu-item>-->
        <!--<v-contextmenu-item @click="handleDelSuite()">删除测试集</v-contextmenu-item>-->
        <!--<v-contextmenu-item @click="refreshSubtree('testsuite')">刷新</v-contextmenu-item>-->
      </v-contextmenu>
    </div>
    <!--树形控件右键菜单_四级用例-->
    <div>
      <v-contextmenu ref="contextMenuCase">
        <v-contextmenu-item @click="handleDelCase()">删除测试用例</v-contextmenu-item>
        <!--<v-contextmenu-item @click="handleUpTestCase()">上移</v-contextmenu-item>-->
        <!--<v-contextmenu-item @click="handleDownTestCase()">下移</v-contextmenu-item>-->
        <!--<v-contextmenu-item @click="refreshSubtree('testcase')">刷新</v-contextmenu-item>-->
      </v-contextmenu>
    </div>
    <!-- 新增编辑项目弹出框 -->
    <el-dialog title="配置项目" :visible.sync="projectEditVisible" width="30%" :close-on-click-modal="false" :close-on-press-escape="false" ref="projectEditDialog">
      <el-form ref="projectEditForm" :model="projectEditForm" label-width="100px">
        <el-form-item label="项目名称" prop="projectName" :rules="[{ required: true, message: '项目名称必填', trigger: 'blur' }]">
          <el-input v-model="projectEditForm.projectName" placeholder="请输入项目名称"></el-input>
        </el-form-item>
        <!--<el-form-item label="项目描述" prop="desc">-->
        <!--<el-input v-model="projectEditForm.desc" placeholder="请输入项目描述"></el-input>-->
        <!--</el-form-item>-->
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="projectEditVisible = false">取 消</el-button>
        <el-button type="primary" @click="saveProjectEdit('projectEditForm')">确 定</el-button>
      </span>
    </el-dialog>

    <!--引入工程弹窗-->
    <el-dialog title="引入工程" :visible.sync="systemEditVisible" width="45%" :close-on-click-modal="false" :close-on-press-escape="false" ref="systemEditDialog">
      <el-row>
        <el-col :span="22">
          <el-form size="mini" style="float: left">
            <el-form ref="systemEditForm" :model="systemEditForm" style="float: left">
              <el-form-item>
                <div class="example_tree">
                  <div class="navigation-filter">
                    <el-input placeholder="输入系统关键字筛选" v-model="filterSystemText"></el-input>
                  </div>
                  <el-scrollbar wrap-class="tree-list" view-class="view-box" :native="false">
                    <div class="category">
                      <el-tree
                        :data="systemEditForm.systemOptions"
                        show-checkbox
                        default-expand-all
                        node-key="systemId"
                        ref="tree1"
                        highlight-current
                        :props="defaultProps"
                        @check-change="handCheckSystemChange"
                        :filter-node-method="filterNode"
                      ></el-tree>
                    </div>
                  </el-scrollbar>
                </div>
              </el-form-item>
            </el-form>
            <!--已经引入的工程表格-->
            <el-table :data="systemEditForm.tableData" border style="width: 100%; margin-top: 20px" height="300">
              <el-table-column prop="systemId" label="工程ID" width="180"></el-table-column>
              <el-table-column prop="label" label="工程名称"></el-table-column>
            </el-table>
          </el-form>
        </el-col>
        <el-col :span="2">
          <el-button @click="setCheckedSystems">{{systemEditForm.btnName}}</el-button>
        </el-col>
      </el-row>
      <span slot="footer" class="dialog-footer">
        <el-button @click="systemEditVisible = false">取 消</el-button>
        <el-button type="primary" @click="saveIntroduceSystem('systemEditForm')">确 定</el-button>
      </span>
    </el-dialog>

    <!--引入接口弹窗-->
    <el-dialog
      title="引入接口"
      :visible.sync="interfaceEditVisible"
      width="45%"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      ref="interfaceEditDialog"
    >
      <el-row>
        <el-col :span="22">
          <el-form size="mini" style="float: left">
            <el-form ref="interfaceEditForm" :model="interfaceEditForm" style="float: left" inline>
              <el-form-item>
                <div class="example_tree">
                  <div class="navigation-filter">
                    <el-input placeholder="输入接口关键字筛选" v-model="filterInterfaceText"></el-input>
                  </div>
                  <el-scrollbar wrap-class="tree-list" view-class="view-box" :native="false">
                    <div class="category">
                      <!--:default-checked-keys="interfaceEditForm.treeData"-->
                      <el-tree
                        :data="interfaceEditForm.interfaceOptions"
                        show-checkbox
                        default-expand-all
                        node-key="intfId"
                        ref="tree2"
                        highlight-current
                        :props="defaultProps"
                        @check-change="handCheckInterfaceChange"
                        :filter-node-method="filterNode"
                      ></el-tree>
                    </div>
                  </el-scrollbar>
                </div>
              </el-form-item>
              <!--<el-form-item style="margin-left: 30px">-->
              <!--<el-button @click="saveCheckedKeysInterface">保 存</el-button>-->
              <!--</el-form-item>-->
            </el-form>
            <!--已经引入的接口表格-->
            <el-table :data="interfaceEditForm.tableData" border style="width: 100%; margin-top: 20px" height="300">
              <el-table-column prop="intfId" label="接口ID" width="180"></el-table-column>
              <el-table-column prop="label" label="接口名称"></el-table-column>
            </el-table>
          </el-form>
        </el-col>
        <el-col :span="2">
          <el-button @click="setCheckedInterface">{{interfaceEditForm.btnName}}</el-button>
        </el-col>
      </el-row>
      <span slot="footer" class="dialog-footer">
        <el-button @click="interfaceEditVisible = false">取 消</el-button>
        <el-button type="primary" @click="saveIntroduceInterface('interfaceEditForm')">确 定</el-button>
      </span>
    </el-dialog>
    <!-- 删除提示框 -->
    <el-dialog title="提示" :visible.sync="delVisible" width="300px" center>
      <div class="del-dialog-cnt">删除不可恢复，是否确定删除？</div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="delVisible = false">取 消</el-button>
        <el-button type="danger" icon="el-icon-warning" @click="saveDelete(deleteId)">删 除</el-button>
      </span>
    </el-dialog>
    <!-- 导出框 -->
    <el-dialog title="导出xmind" :visible.sync="exportVisible" width="300px" center>
      <div class="ecport-xmind" style="margin-left: 10%">
        <a :href="downloadXmindTempUrl">
          <el-button type="primary" @click="exported">导出节点下所有用例</el-button>
        </a>
      </div>
    </el-dialog>
  </d2-container>
</template>

<script>
import { fetchCompanyList, getFilterConditions, subtreeFilter } from '@/api/autotest/manage/resource-apiManage/company'
import { queryByCompanyId } from '@/api/autotest/manage/resource-apiManage/system'
import { queryByProjectId } from '@/api/autotest/manage/resource-apiManage/api'
import {
  addApiProject,
  editApiProject,
  deleteApiProject,
  introduceSystem,
  introduceInterface,
  excludeIntf,
  excludeSystem
} from '@/api/autotest/manage/resource-projectManage'
import { deleteTestCase, changeSuiteParent, exportTestCase } from '@/api/autotest/manage/testcase-apiManage/config'
import { queryProjectByCompanyId, getSubTreeByProjectId } from '@/api/autotest/manage/resource-apiManage/project'
import { isJsonString } from '@/libs/common'

export default {
  name: 'caseManage',
  components: {
    'case-table': () => import('../components/case-table')
  },
  data() {
    var headersValidatePass = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('头域必填'))
      } else if (!isJsonString(value)) {
        callback(new Error('非法json格式'))
      } else {
        callback()
      }
    }
    return {
      intfInfo: null, // 传递给子组件的接口信息
      caseTableVisible: false, // 用例表单是否显示
      editProjectIdx: -1,
      // 基础表单
      baseForm: {
        companyId: '', // 公司ID
        companyOptions: []
      },
      // 搜索表单
      searchForm: {
        filterConditions: [], // 搜索条件集合
        filterCondition: '', // 搜索条件值
        keyword: '' // 搜索值
      },
      projectId: '', // 项目ID
      systemId: '', // 工程ID
      intfId: '', // 接口ID
      caseId: '', // 用例ID
      projectEditVisible: false,
      introduceInterVisible: true,
      systemEditVisible: false,
      projectEditForm: {
        projectName: '',
        desc: ''
      },
      systemEditForm: {
        systemId: '',
        systemName: '',
        systemOptions: [],
        treeData: [],
        tableData: [],
        selectFlag: false,
        btnName: '全选'
      },
      interfaceEditForm: {
        interfaceOptions: [],
        interfaceIdList: [],
        treeData: [],
        tableData: [],
        selectFlag: false,
        btnName: '全选'
      },
      deleteId: '',
      deleteIdx: '',
      importFileUrl: '/atp/file/upload',
      downloadXmindTempUrl: '',
      delVisible: false,
      exportVisible: false,
      exportMoudleName: '',
      interfaceEditVisible: false,
      props: {
        label: 'label',
        children: 'children',
        isLeaf: 'leaf'
      },
      defaultProps: {
        children: 'children',
        label: 'label'
      },
      filterSystemText: '',
      filterInterfaceText: '',
      treeDataAll: [], // 默认结果树
      nodeKeys: [],
      parentNodeKey: '',
      rules: {
        interfaceType: [{ required: true, message: '接口类型必填', trigger: 'blur' }],
        apiUrl: [{ required: true, message: 'API URL必填', trigger: 'blur' }],
        headers: [{ required: true, validator: headersValidatePass, trigger: 'blur' }],
        method: [{ required: true, message: '请求方法必填', trigger: 'blur' }],
        dubboService: [{ required: true, message: '服务名必填', trigger: 'blur' }],
        dubboMethod: [{ required: true, message: '方法名必填', trigger: 'blur' }],
        parameterTypes: [{ required: true, message: '参数类型必填', trigger: 'blur' }],
        version: [{ required: false, message: '版本号必填', trigger: 'blur' }],
        topic: [{ required: true, message: 'topic必填', trigger: 'blur' }],
        tag: [{ required: true, message: 'tag必填', trigger: 'blur' }]
      },
      id: 0,
      searchLoading: false,
      subTreeData: null, // 某个项目下的子节点数据
      node: null, // 树节点数据
      isSearching: false // 是否进入搜索模式
    }
  },
  mounted() {
    this.getCompany()
  },
  watch: {
    filterSystemText(val) {
      this.$refs.tree1.filter(val)
    },
    filterInterfaceText(val) {
      this.$refs.tree2.filter(val)
    }
  },
  methods: {
    // 子组件（用例列表）主动触发父组件更新
    updateData() {
      if (this.isSearching) {
        if ('addCaseVisible' in this.intfInfo) {
          //                        this.refreshTreeData(this.node.parent.parent)
          subtreeFilter({
            companyId: this.baseForm.companyId,
            filter: this.searchForm.filterCondition,
            keyword: this.searchForm.keyword
          }).then(res => {
            this.treeDataAll = res.data
            this.node.expanded = true
          })
        } else {
          if (this.node.level === 3) {
            if (this.node.parent.parent.data.label === '未归属到任何项目') {
              subtreeFilter({
                companyId: this.baseForm.companyId,
                filter: this.searchForm.filterCondition,
                keyword: this.searchForm.keyword
              }).then(res => {
                this.treeDataAll = res.data
                this.node.expanded = true
              })
            } else {
              this.refreshTreeData(this.node.parent.parent)
            }
          } else if (this.node.level === 4) {
            if (this.node.parent.parent.parent.data.label === '未归属到任何项目') {
              subtreeFilter({
                companyId: this.baseForm.companyId,
                filter: this.searchForm.filterCondition,
                keyword: this.searchForm.keyword
              }).then(res => {
                this.treeDataAll = res.data
                this.node.parent.expanded = true
              })
            } else {
              this.refreshTreeData(this.node.parent.parent.parent)
            }
          }
        }
      } else {
        if (this.node.level === 3) {
          this.refreshTreeData(this.node.parent.parent)
        } else if (this.node.level === 4) {
          this.refreshTreeData(this.node.parent.parent.parent)
        }
      }
    },
    // 获取公司数据
    getCompany() {
      fetchCompanyList({}).then(res => {
        this.baseForm.companyOptions = res.companyList
        if (res.code === '000') {
          this.baseForm.companyId = res.companyList[0].companyId
          this.getProjectSubTreeByCompanyId(this.baseForm.companyId)
          this.getTestCaseFilterConditions()
        }
      })
    },
    // 获取用例查询关键字
    getTestCaseFilterConditions() {
      getFilterConditions({}).then(res => {
        this.searchForm.filterConditions = res.conditions
        this.searchForm.filterCondition = res.conditions[0]
      })
    },
    // 根据关键字查询用例
    queryTestCaseByKeyword(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          this.$nextTick(function() {
            this.$refs.caseTable.pageLoad({ interfacePropShow: false })
            this.$refs.treeAll.store.root.store.lazy = false
            this.$refs.treeAll.store.root.store.defaultExpandAll = true
          })
          this.treeDataAll = []
          this.isSearching = true
          subtreeFilter({
            companyId: this.baseForm.companyId,
            filter: this.searchForm.filterCondition,
            keyword: this.searchForm.keyword
          }).then(res => {
            this.treeDataAll = res.data
          })
        }
      })
    },
    // 根据公司ID查询项目列表
    getProjectSubTreeByCompanyId(id) {
      return new Promise((resolve, reject) => {
        queryProjectByCompanyId({ companyId: id }).then(res => {
          let num = 10000
          for (var i = 0, len = res.projectList.length; i < len; i++) {
            res.projectList[i].label = `${res.projectList[i].projectName}` + '(' + res.projectList[i].testcaseNum + ')'
            res.projectList[i].leaf = !res.projectList[i].hasChildren
            res.projectList[i].id = num
            num += 1
          }
          this.treeDataAll = res.projectList
          resolve(1)
        })
      })
    },
    // 页面搜索操作
    search(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          this.$nextTick(function() {
            this.$refs.caseTable.pageLoad({ interfacePropShow: false })
            this.$refs.treeAll.store.root.store.lazy = true
            this.$refs.treeAll.store.root.store.defaultExpandAll = false
          })
          this.treeDataAll = []
          this.isSearching = false
          this.searchLoading = true
          this.getProjectSubTreeByCompanyId(this.baseForm.companyId).then(res => {
            this.searchLoading = false
          })
        }
      })
    },
    // 树节点懒加载逻辑
    loadNode(node, resolve) {
      if (node.level === 1) {
        this.getDataByProjectId(node.data.projectId).then(res => {
          resolve(res)
        })
      }
      if (node.level === 2) {
        let subTreeData = JSON.parse(sessionStorage.getItem(node.parent.data.projectId.toString()))
        let idx = subTreeData.findIndex(c => c.systemId === node.data.systemId)
        resolve(subTreeData[idx].children)
        /* this.getDataByProjectId(node.parent.data.projectId).then((res) => {
                        let idx = this.subTreeData.findIndex(c => c.systemId === node.data.systemId)
                        resolve(this.subTreeData[idx].children)
                    })*/
      }
      if (node.level === 3) {
        node.data.children.forEach(i => {
          i.leaf = true
        })
        let subTreeData = JSON.parse(sessionStorage.getItem(node.parent.parent.data.projectId.toString()))
        let idx = subTreeData.findIndex(c => c.systemId === node.parent.data.systemId)
        let subIdx = subTreeData[idx].children.findIndex(d => d.intfId === node.data.intfId)
        resolve(subTreeData[idx].children[subIdx].children)
        /* this.getDataByProjectId(node.parent.parent.data.projectId).then((res) => {
                        let idx = this.subTreeData.findIndex(c => c.systemId === node.parent.data.systemId);
                        let subIdx = this.subTreeData[idx].children.findIndex(d => d.intfId === node.data.intfId);
                       resolve(this.subTreeData[idx].children[subIdx].children)
                    })*/
      }
    },
    // 根据项目ID查询项目数据
    getDataByProjectId(id) {
      return new Promise((resolve, reject) => {
        getSubTreeByProjectId({ projectId: id }).then(res => {
          res.data.forEach(i => {
            i.leaf = i.children.length === 0
            if (i.children.length !== 0) {
              i.children.forEach(j => {
                j.leaf = j.children.length === 0
                if (j.children.length !== 0) {
                  j.children.forEach(k => {
                    k.leaf = true
                  })
                }
              })
            }
          })
          sessionStorage.setItem(id.toString(), JSON.stringify(res.data))
          this.subTreeData = res.data
          resolve(res.data)
        })
      })
    },
    // 在树节点上进行新增、修改、删除操作后刷新树节点数据
    refreshTreeData(node) {
      console.log('操作的node', node)
      this.getDataByProjectId(node.data.projectId).then(res => {
        this.refreshLazyTree(node, res)
      })
    },
    // 重置树节点数据
    refreshLazyTree(node, children) {
      let theChildren = node.childNodes
      theChildren.splice(0, theChildren.length)
      node.doCreateChildren(children)

      this.$nextTick(function() {
        if (this.isSearching) {
          for (var i = 0; i < this.$refs.treeAll.store._getAllNodes().length; i++) {
            this.$refs.treeAll.store._getAllNodes()[i].expanded = false
          }
        }
        if (node.level === 1 && (node.expanded === false || node.childNodes.length === 0)) {
          this.getProjectSubTreeByCompanyId(this.baseForm.companyId)
        }
        if (this.node.level === 2) {
          let idx = node.childNodes.findIndex(c => c.data.systemId === this.node.data.systemId)
          if (idx !== -1) {
            node.childNodes[idx].expanded = true
          }
        }
        if (this.node.level === 3) {
          let idx = node.childNodes.findIndex(c => c.data.systemId === this.node.parent.data.systemId)
          if (idx !== -1) {
            node.childNodes[idx].expanded = true
            let subIdx = node.childNodes[idx].childNodes.findIndex(c => c.data.intfId === this.node.data.intfId)
            if (subIdx !== -1) {
              node.childNodes[idx].childNodes[subIdx].expanded = true
            }
          }
        }
        if (this.node.level === 4) {
          let idx = node.childNodes.findIndex(c => c.data.systemId === this.node.parent.parent.data.systemId)
          if (idx !== -1) {
            node.childNodes[idx].expanded = true
            let subIdx = node.childNodes[idx].childNodes.findIndex(c => c.data.intfId === this.node.parent.data.intfId)
            if (subIdx !== -1) {
              node.childNodes[idx].childNodes[subIdx].expanded = true
            }
          }
        }
      })
    },
    // 鼠标左键点击树节点
    handleNodeClick(data, node) {
      this.$refs['contextMenuSuite'].hide()
      this.$refs['contextMenuSystem'].hide()
      this.$refs['contextMenuProject'].hide()
      this.$refs['contextMenuCase'].hide()
      let intfId = ''
      let testcaseId = ''
      this.node = node
      if ('projectId' in data) {
        this.projectId = data.projectId
        this.$refs.caseTable.pageLoad({ interfacePropShow: false })
      }
      if ('systemId' in data) {
        this.$refs.caseTable.pageLoad({ interfacePropShow: false })
      }
      if ('intfId' in data) {
        intfId = data.intfId
        this.intfInfo = {
          projectId: this.projectId,
          intfId: intfId,
          companyId: this.baseForm.companyId,
          interfacePropShow: true
        }
        this.caseTableVisible = true
        this.$refs.caseTable.pageLoad(this.intfInfo)
      }
      if ('testcaseId' in data) {
        testcaseId = data.testcaseId
        intfId = node.parent.data.intfId
        this.intfInfo = {
          projectId: this.projectId,
          intfId: intfId,
          testcaseId: testcaseId,
          companyId: this.baseForm.companyId,
          interfacePropShow: true
        }
        this.caseTableVisible = true
        this.$refs.caseTable.pageLoad(this.intfInfo)
      }
    },
    // 鼠标右键点击树节点
    rightClick(event, object, value, element) {
      this.$refs.treeAll.setCurrentKey(value.key)
      this.node = value
      if (value.level === 1 && object.projectId !== -1) {
        let position = {
          top: event.clientY,
          left: event.clientX + 20
        }
        this.$refs['contextMenuSuite'].hide()
        this.$refs['contextMenuSystem'].hide()
        this.$refs['contextMenuCase'].hide()
        this.$refs['contextMenuProject'].show(position)
        this.projectId = object.projectId
        this.projectEditForm.projectName = object.label
      } else if (value.level === 2 && value.parent.data.projectId !== -1) {
        let position = {
          top: event.clientY,
          left: event.clientX + 20
        }
        this.$refs['contextMenuProject'].hide()
        this.$refs['contextMenuSuite'].hide()
        this.$refs['contextMenuCase'].hide()
        this.$refs['contextMenuSystem'].show(position)
        this.projectId = value.parent.data.projectId
        this.systemId = object.systemId
      } else if (value.level === 3) {
        let position = {
          top: event.clientY,
          left: event.clientX + 20
        }
        this.$refs['contextMenuProject'].hide()
        this.$refs['contextMenuSystem'].hide()
        this.$refs['contextMenuCase'].hide()
        this.$refs['contextMenuSuite'].show(position)
        this.intfId = value.data.intfId
        this.projectId = value.parent.parent.data.projectId
        this.intfInfo = {
          projectId: this.projectId,
          intfId: this.intfId,
          companyId: this.baseForm.companyId
        }
        this.caseTableVisible = true
        this.$refs.caseTable.pageLoad(this.intfInfo)
      } else if (value.level === 4) {
        let position = {
          top: event.clientY,
          left: event.clientX + 20
        }
        this.$refs['contextMenuProject'].hide()
        this.$refs['contextMenuSystem'].hide()
        this.$refs['contextMenuSuite'].hide()
        this.$refs['contextMenuCase'].show(position)
        this.caseId = value.data.testcaseId
      }
      this.deleteIdx = value.level
    },
    // 引入工程、接口弹框页面的树节点过滤
    filterNode(value, data) {
      if (!value) {
        return true
      }
      return data.label.indexOf(value) !== -1
    },
    // 处理新增项目
    handleAddProject() {
      this.projectEditVisible = true
      this.projectEditForm.projectName = ''
      // this.resetForm('projectEditForm')
      this.editProjectIdx = -1
    },
    // 处理编辑项目
    handleEditProject() {
      this.projectEditVisible = true
      this.editProjectIdx = 1
      this.projectEditForm.projectName = this.projectEditForm.projectName.split('(')[0]
    },
    // 处理删除项目
    handleDeleteProject() {
      this.delVisible = true
      this.deleteId = this.projectId
    },
    // 获取公司下引用/未引用系统，
    queryByCompanyId() {
      queryByCompanyId({ companyId: this.baseForm.companyId, projectId: this.projectId }).then(res => {
        this.systemEditForm.systemOptions = res.systemList
        this.systemEditForm.tableData = res.includeSystemList
      })
    },
    // 全选或取消全选系统
    setCheckedSystems() {
      this.systemEditForm.selectFlag = !this.systemEditForm.selectFlag
      if (this.systemEditForm.selectFlag) {
        this.systemEditForm.btnName = '取消全选'
        this.$refs.tree1.setCheckedNodes(this.systemEditForm.systemOptions)
      } else {
        this.systemEditForm.btnName = '全选'
        this.$refs.tree1.setCheckedNodes([])
      }
    },
    // 获取系统下引用/未引用接口
    getInterfaceList() {
      queryByProjectId({ systemId: this.systemId, projectId: this.projectId }).then(res => {
        this.interfaceEditForm.interfaceOptions = res.intfList
        this.interfaceEditForm.tableData = res.includeIntfList
      })
    },
    // 全选或取消全选接口
    setCheckedInterface() {
      this.interfaceEditForm.selectFlag = !this.interfaceEditForm.selectFlag
      if (this.interfaceEditForm.selectFlag) {
        this.interfaceEditForm.btnName = '取消全选'
        this.$refs.tree2.setCheckedNodes(this.interfaceEditForm.interfaceOptions)
      } else {
        this.interfaceEditForm.btnName = '全选'
        this.$refs.tree2.setCheckedNodes([])
      }
    },
    // 处理右键菜单：引入系统
    handleIntroduceSystem() {
      this.systemEditVisible = true
      this.systemEditForm.treeData = []
      this.queryByCompanyId()
    },
    // 处理右键菜单：删除引入的系统
    handleDeleteSyetem() {
      this.delVisible = true
      this.deleteId = this.systemId
    },
    // 处理右键菜单：引入接口
    handleIntroduceInterface() {
      this.interfaceEditVisible = true
      this.interfaceEditForm.treeData = []
      this.getInterfaceList()
    },
    // 处理右键菜单：删除引入的接口
    handleDeleteInterface() {
      this.delVisible = true
      this.deleteId = this.intfId
    },
    // 引入工程复选框触发事件
    handCheckSystemChange(data, isCheck) {
      if (isCheck === true) {
        this.systemEditForm.tableData.push(data)
        this.systemEditForm.treeData.push(data.systemId)
      } else {
        this.systemEditForm.tableData = this.systemEditForm.tableData.filter(i => {
          return i !== data
        })
        this.systemEditForm.treeData = this.systemEditForm.treeData.filter(i => {
          return i !== data.systemId
        })
      }
    },
    // 引入接口复选框触发事件
    handCheckInterfaceChange(data, isCheck) {
      if (isCheck === true) {
        this.interfaceEditForm.tableData.push(data)
        this.interfaceEditForm.treeData.push(data.intfId)
      } else {
        this.interfaceEditForm.tableData = this.interfaceEditForm.tableData.filter(i => {
          return i !== data
        })
        this.interfaceEditForm.treeData = this.interfaceEditForm.treeData.filter(i => {
          return i !== data.intfId
        })
      }
    },
    // 重置所选
    resetChecked() {
      this.$refs.tree.setCheckedKeys([])
    },
    // 保存引入工程
    saveIntroduceSystem(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          introduceSystem({
            projectId: this.projectId,
            systemIdList: this.systemEditForm.treeData
          }).then(res => {
            this.$message.success(res.desc)
            this.systemEditVisible = false
            this.refreshTreeData(this.node)
          })
        }
      })
    },
    // 保存引入接口
    saveIntroduceInterface(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          introduceInterface({
            projectId: this.projectId,
            intfIdList: this.interfaceEditForm.treeData
          }).then(res => {
            this.$message.success(res.desc)
            this.interfaceEditVisible = false
            this.refreshTreeData(this.node.parent)
          })
        }
      })
    },
    // 导出用例
    exportXmindByProject() {
      exportTestCase({ projectId: this.projectId }).then(res => {
        this.downloadXmindTempUrl = '/atp/download/' + res.desc
        // this.exportMoudleName =this.downloadXmindTempUrl.slice(17,-16)
        this.exportVisible = true
      })
    },
    exported() {
      this.exportVisible = false
    },
    // 点击新增用例菜单
    handleAddCase() {
      this.caseTableVisible = true
      this.intfInfo['addCaseVisible'] = true
      this.$refs.caseTable.pageLoad(this.intfInfo)
    },
    // 点击删除用例触发的事件
    handleDelCase() {
      this.delVisible = true
      this.deleteId = this.caseId
    },
    // 保存编辑项目
    saveProjectEdit(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          this.projectEditVisible = false
          if (this.editProjectIdx === -1) {
            addApiProject({
              companyId: this.baseForm.companyId,
              projectName: this.projectEditForm.projectName,
              simpleDesc: this.projectEditForm.desc
            }).then(res => {
              this.$message.success(res.desc)
              if (res.code === '000') {
                this.getProjectSubTreeByCompanyId(this.baseForm.companyId)
              }
            })
          } else if (this.editProjectIdx === 1) {
            editApiProject({
              projectId: this.projectId,
              projectName: this.projectEditForm.projectName,
              simpleDesc: this.projectEditForm.desc
            }).then(res => {
              this.$message.success(res.desc)
              this.getProjectSubTreeByCompanyId(this.baseForm.companyId)
            })
          }
        } else {
          return false
        }
      })
    },
    // 删除项目、引入的系统、引入的接口、测试用例
    saveDelete(id) {
      this.delVisible = false
      this.$refs.caseTable.pageLoad({ interfacePropShow: false })
      if (id === this.projectId && this.deleteIdx === 1) {
        deleteApiProject({ projectId: this.projectId }).then(res => {
          this.$message.success(res.desc)
          this.getProjectSubTreeByCompanyId(this.baseForm.companyId)
        })
      } else if (id === this.systemId && this.deleteIdx === 2) {
        excludeSystem({
          projectId: this.projectId,
          systemId: this.systemId
        }).then(res => {
          this.$message.success(res.desc)
          this.refreshTreeData(this.node.parent)
        })
      } else if (id === this.intfId && this.deleteIdx === 3) {
        excludeIntf({
          projectId: this.projectId,
          intfId: this.intfId
        }).then(res => {
          this.$message.success(res.desc)
          this.refreshTreeData(this.node.parent.parent)
        })
      } else if (id === this.caseId && this.deleteIdx === 4) {
        deleteTestCase({
          testcaseId: id
        }).then(res => {
          this.$message.success(res.desc)
          this.refreshTreeData(this.node.parent.parent.parent)
        })
      }
    },
    // 重置表单
    resetForm(formName) {
      if (this.$refs[formName] !== undefined) {
        this.$refs[formName].resetFields()
      }
    },
    beforeAvatarUpload(file) {
      let extension = file.name.split('.')[1] === 'xmind'
      let isLt2M = file.size / 1024 / 1024 < 1
      if (!extension) {
        console.log('上传模板只能是 xmind格式!')
      }
      if (!isLt2M) {
        console.log('上传模板大小不能超过1M!')
      }
      return extension && isLt2M
    },
    openSuiteNameDesc() {
      this.$message({
        // title: '说明',
        showClose: true,
        dangerouslyUseHTMLString: true,
        message:
          '<br><strong><i>说明</i></strong></br>测试集名称以 <strong>[文本]</strong> 格式配置，通常写成被测接口的中文名称。<p><br><strong><i>样例</i></strong></br>获取用户申请信息<p>',
        duration: 15000,
        type: 'info'
      })
    },
    openApiUrlDesc() {
      this.$message({
        // title: '说明',
        showClose: true,
        dangerouslyUseHTMLString: true,
        message:
          '<br><strong><i>说明</i></strong></br>HTTP接口URL以 <strong>[文本]</strong> 格式配置，无需填写host部分。<p><br><strong><i>样例</i></strong></br>/wallet-web/home/queryWalletV3<p>',
        duration: 15000,
        type: 'info'
      })
    },
    openHeaderDesc() {
      this.$message({
        // title: '说明',
        showClose: true,
        dangerouslyUseHTMLString: true,
        message:
          '<br><strong><i>说明</i></strong></br>HTTP请求头域以 <strong>[JSON]</strong> 格式配置，可参数化替换。<p><br><strong><i>样例</i></strong></br>{"Content-Type":"application/json","mmTicket":"$token"}<p>',
        duration: 15000,
        type: 'info'
      })
    },
    openParameterTypesDesc() {
      this.$message({
        // title: '说明',
        showClose: true,
        dangerouslyUseHTMLString: true,
        message:
          '<br><strong><i>说明</i></strong></br>DUBBO参数类型以 <strong>[列表]</strong> 格式配置。<p><br><strong><i>样例</i></strong></br>["java.lang.String","cn.memedai.wallet.facade.forms.ApplyRequiredInfoForm"]<p>',
        duration: 15000,
        type: 'info'
      })
    },
    openVersionDesc() {
      this.$message({
        // title: '说明',
        showClose: true,
        dangerouslyUseHTMLString: true,
        message:
          '<br><strong><i>说明</i></strong></br>DUBBO版本号以 <strong>[文本]</strong> 格式配置，没有版本号则不填。<p><br><strong><i>样例</i></strong></br>1.0.0<p>',
        duration: 15000,
        type: 'info'
      })
    },
    // 拖拽节点
    handleDragEnd(draggingNode, dropNode, dropType, ev) {
      let dragId = ''
      if (dropType === 'inner') {
        if (draggingNode.data.testcaseId) {
          dragId = draggingNode.data.testcaseId
          if (dropNode) {
            let newParentId = dropNode.data.intfId
            console.log('调用移动测试用例接口', dragId, newParentId)
            changeSuiteParent({
              testcaseId: dragId,
              newParentId: newParentId
            }).then(res => {
              this.$message.success(res.desc)
            })
          }
        }
      } else {
        this.$message.warning('移动失败')
      }
    },
    handleDrop(draggingNode, dropNode, dropType, ev) {
      console.log('tree drop: ', dropNode.label, dropType)
    },
    allowDrop(draggingNode, dropNode, type) {
      if (draggingNode.data.testcaseId) {
        if (dropNode.data.systemId || dropNode.data.projectId || dropNode.data.testcaseId) {
          return false
        } else if (dropNode.data.intfId) {
          return type === 'inner'
        }
      }
    },
    allowDrag(draggingNode) {
      if (draggingNode.data.systemId || draggingNode.data.projectId || draggingNode.data.intfId) {
        this.$message.warning('项目、系统和接口层级不能移动')
        return false
      } else {
        return draggingNode
      }
    }
  }
}
</script>

<style lang="scss">
.example-intf {
  padding: 10px;
  height: 100%;
  min-height: 700px;
  max-height: 700px;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.1);
}

.example_tree {
  padding: 10px;
  height: 100%;
  width: 100%;
  min-height: 330px;
  min-width: 650px;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.1);
}

.table_container {
  padding: 10px;
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
  padding: 10px 23px;
}

/*.custom-tree-node {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    font-size: 14px;
    padding-right: 8px;
  }*/

.category-description {
  text-indent: 2em;
}

.category {
  margin-bottom: 20px;
}

.navigation-filter {
  padding: 5px 10px;
}

.intfScrolllist {
  max-height: 700px;
}

.tree-list {
  max-height: 350px;
}

/*.span {
    .card-panel-icon {
      float: left;
      font-size: 18px;
      color: #ffab0c
    }
  }*/
</style>
