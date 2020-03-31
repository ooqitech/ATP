<template>
  <d2-container>
    <!--<el-alert
      title="操作说明"
      description="请在左侧树节点上使用右键操作“新增接口”，“删除系统”，“新增mock场景”，“测试mock配置”"
      type="success"
      show-icon>
    </el-alert>-->
    <!--树形控件右键菜单_一级系统-->
    <div>
      <v-contextmenu ref="contextMenuSystem">
        <v-contextmenu-item @click="handleEditProject()">修改系统</v-contextmenu-item>
        <v-contextmenu-item @click="delProject()">删除系统</v-contextmenu-item>
        <v-contextmenu-item divider></v-contextmenu-item>
        <v-contextmenu-item @click="handleAddInterface()">新增接口</v-contextmenu-item>
      </v-contextmenu>
    </div>
    <!--树形控件右键菜单_二级接口-->
    <div>
      <v-contextmenu ref="contextMenuInterface">
        <v-contextmenu-item @click="handleEditInterface()">修改接口</v-contextmenu-item>
        <v-contextmenu-item @click="handleDelInterface()">删除接口</v-contextmenu-item>
        <v-contextmenu-item divider></v-contextmenu-item>
        <v-contextmenu-item @click="handleClick">新增mock场景</v-contextmenu-item>
        <v-contextmenu-item @click="testClick">测试mock配置</v-contextmenu-item>
      </v-contextmenu>
    </div>
    <!--主体页面-->
    <el-row :gutter="15">
      <el-col :span="6">
        <div class="example">
          <!--搜索框-->
          <div class="navigation-filter">
            <el-row :gutter="10">
              <el-col :span="20">
                <el-input placeholder="输入关键字进行过滤" v-model="filterText"></el-input>
              </el-col>
              <el-col :span="4">
                <el-tooltip content="新增系统" placement="bottom" effect="light">
                  <el-button icon="el-icon-plus" @click="handleAddProject"></el-button>
                </el-tooltip>
              </el-col>
            </el-row>
          </div>
          <!--展示树-->
          <el-scrollbar wrap-class="mockScrolllist" view-class="view-box" :native="false">
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
              ></el-tree>
            </div>
          </el-scrollbar>
        </div>
      </el-col>
      <el-col :span="18">
        <!--展示接口信息-->
        <div class="example">
          <el-form :model="interfaceProp" class="formStyle" size="mini" v-show="interfaceProp.show" ref="interfaceProp">
            <el-row style="margin-bottom: 10px">
              <el-col :span="3">
                <span class="titleStyle">mock前URL:</span>
              </el-col>
              <el-col :span="18">
                <span class="itemStyle">{{ interfaceProp.realUrl }}</span>
              </el-col>
            </el-row>
            <el-row style="margin-bottom: 10px">
              <el-col :span="3">
                <span class="titleStyle">mock后URL:</span>
              </el-col>
              <el-col :span="18">
                <span class="itemStyle">{{ interfaceProp.mockUrl }}</span>
              </el-col>
            </el-row>
            <el-row style="margin-bottom: 10px" type="flex" justify="left">
              <el-col :span="3">
                <span class="titleStyle">Request Method:</span>
              </el-col>
              <el-col :span="3">
                <span class="itemStyle">{{ interfaceProp.httpMethod }}</span>
              </el-col>
              <el-col :span="3">
                <span class="titleStyle">Content-Type:</span>
              </el-col>
              <el-col :span="12">
                <span class="itemStyle">{{ interfaceProp.contentType }}</span>
              </el-col>
              <el-col :span="3" style="text-align:right;">
                <el-button size="mini" type="primary" @click="handleClick">新增</el-button>
                <el-button size="mini" type="info" @click="testClick">测试</el-button>
              </el-col>
            </el-row>
            <!--展示接口场景-->
            <el-table
              :data="tableData"
              border
              style="width: 100%"
              :default-sort="{prop: 'date', order: 'descending'}"
              tooltip-effect="light"
              :header-cell-style="{color:'black',background:'#eef1f6'}"
            >
              <el-table-column type="expand" width="20%">
                <template slot-scope="props">
                  <el-form label-position="right" class="formStyle">
                    <el-form-item label="请求报文: ">
                      <span class="itemStyle">{{ props.row.requestBody }}</span>
                    </el-form-item>
                    <el-form-item label="响应报文: ">
                      <span class="itemStyle">{{ props.row.responseBody }}</span>
                    </el-form-item>
                  </el-form>
                </template>
              </el-table-column>
              <el-table-column prop="id" label="场景ID" width="auto" show-overflow-tooltip></el-table-column>
              <el-table-column prop="comment" label="场景名称" width="auto" show-overflow-tooltip></el-table-column>
              <el-table-column prop="requestBody" label="请求报文" width="auto" show-overflow-tooltip></el-table-column>
              <el-table-column prop="responseBody" label="响应报文" width="auto" show-overflow-tooltip></el-table-column>
              <el-table-column prop="createTime" label="创建时间" width="150" show-overflow-tooltip></el-table-column>
              <el-table-column prop="operator" label="创建人" width="80"></el-table-column>
              <el-table-column label="操作" width="100">
                <template slot-scope="scope">
                  <el-tooltip content="编辑" placement="top" effect="light">
                    <el-button size="mini" type="primary" icon="el-icon-edit" circle @click="handleEdit(scope.row)"></el-button>
                  </el-tooltip>
                  <el-tooltip content="删除" placement="top" effect="light">
                    <el-button
                      size="mini"
                      type="danger"
                      icon="el-icon-delete"
                      circle
                      @click="handleDelete(scope.row)"
                      v-show="!(scope.row.requestBody === '{}' || scope.row.requestBody === empty)"
                    ></el-button>
                  </el-tooltip>
                </template>
              </el-table-column>
            </el-table>
            <div align="left">
              <el-pagination
                layout="total, sizes, prev, pager, next, jumper"
                :total="totalCount"
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
                :current-page="currentPage"
                :page-sizes="[10, 20, 30, 40]"
                :page-size="pageSize"
              ></el-pagination>
            </div>
          </el-form>
        </div>
      </el-col>
    </el-row>
    <!--新增系统界面-->
    <el-dialog id="addProjectForm" title="配置系统" width="30%" :visible.sync="addProjectFormVisible" :close-on-click-modal="false" :close-on-press-escape="false">
      <el-form :model="addProjectForm" ref="addProjectForm" size="small" label-width="80px">
        <el-form-item label="系统名称" prop="projectName" :rules="[{ required: true, message: '请输入系统名称', trigger: 'blur' }]">
          <el-input v-model="addProjectForm.projectName" placeholder="请输入系统名称"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="addProjectFormVisible = false" size="small">取 消</el-button>
        <el-button type="primary" @click="addProject('addProjectForm')" size="small">确 定</el-button>
      </div>
    </el-dialog>
    <!--新增接口界面-->
    <el-dialog id="addInterfaceForm" title="配置接口数据" :visible.sync="addInterfaceFormVisible" :close-on-click-modal="false" :close-on-press-escape="false">
      <el-form :model="addInterfaceForm" ref="addInterfaceForm" size="small" :label-width="formLabelWidth">
        <el-form-item label="接口中文描述" prop="interfaceDesc" :rules="[{ required: true, message: '必填，请输入', trigger: 'blur' }]">
          <el-input v-model="addInterfaceForm.interfaceDesc" auto-complete="off" placeholder="请输入mock接口中文描述"></el-input>
        </el-form-item>
        <el-form-item
          label="接口完整URL"
          prop="realUrl"
          :rules="[{ required: true, message: '必填，请输入', trigger: 'blur' },
                      {pattern: /(http|https):\/\/([\w.]+\/?)\S*/, message: '请检查URL是否正确', trigger: 'blur'}]"
        >
          <el-input
            v-model="addInterfaceForm.realUrl"
            auto-complete="off"
            placeholder="请输入联调环境完整接口URL，如https://lt-aquarius.wsmtec.com:11443/OLM/index.php"
            style="width:100%;"
          ></el-input>
        </el-form-item>
        <el-form-item label="Request Method" prop="httpMethod" :rules="[{ required: true, message: '请选择', trigger: 'change' }]">
          <el-select v-model="addInterfaceForm.httpMethod" placeholder="请选择">
            <el-option v-for="item in httpMethodOptions" :key="item.key" :label="item" :value="item"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item
          label="Content-Type"
          prop="contentType"
          v-if="addInterfaceForm.httpMethod === 'POST'"
          :rules="[{ required: true, message: '请选择', trigger: 'change' }]"
        >
          <el-select v-model="addInterfaceForm.contentType" placeholder="请选择">
            <el-option v-for="item in contentTypeOptions" :key="item.key" :label="item" :value="item"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="请求报文" prop="requestBody" v-if="idx === -1">
          <span style="color: red">此处不需要填写，默认会匹配到任意请求，未命中其他场景的都会使用下面的响应报文返回</span>
        </el-form-item>
        <el-form-item label="响应报文" prop="responseBody" :rules="[{ required: true, message: '请输入响应报文', trigger: 'blur' }]" v-if="idx === -1">
          <el-input type="textarea" :autosize="{ minRows: 4, maxRows: 6}" placeholder="请输入响应报文" v-model="addInterfaceForm.responseBody"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="addInterfaceFormVisible = false" size="small">取 消</el-button>
        <el-button type="primary" @click="addInterface('addInterfaceForm')" size="small">确 定</el-button>
        <el-button @click="resetForm('addInterfaceForm')">重 置</el-button>
      </div>
    </el-dialog>
    <!--新增场景界面-->
    <el-dialog id="addSceneForm" title="配置mock场景数据" :visible.sync="addSceneFormVisible" :close-on-click-modal="false" :close-on-press-escape="false">
      <el-form :model="addSceneForm" ref="addSceneForm" size="small" :label-width="formLabelWidth">
        <el-form-item label="场景描述" prop="comment" :rules="[{ required: true, message: '必填，请输入', trigger: 'blur' }]">
          <el-input v-model="addSceneForm.comment" auto-complete="off" placeholder="请输入场景描述" style="width:90%;"></el-input>
        </el-form-item>
        <el-form-item label="请求报文" prop="requestBody" :rules="[{ required: true, message: '请输入请求报文', trigger: 'blur' }]">
          <el-input type="textarea" :autosize="{ minRows: 2, maxRows: 4}" placeholder="请输入请求报文" v-model="addSceneForm.requestBody" style="width:90%;"></el-input>
        </el-form-item>
        <el-form-item label="响应报文" prop="responseBody" :rules="[{ required: true, message: '请输入响应报文', trigger: 'blur' }]">
          <el-input type="textarea" :autosize="{ minRows: 4, maxRows: 6}" placeholder="请输入响应报文" v-model="addSceneForm.responseBody" style="width:90%;"></el-input>
        </el-form-item>
        <el-form-item label="是否延时返回" prop="isDelay">
          <el-checkbox v-model="addSceneForm.isDelay" @change="isChanged"></el-checkbox>
        </el-form-item>
        <el-form-item label="延时时间(秒)" prop="delaySeconds" v-if="addSceneForm.isDelay" :rules="[{ required: true, message: '请输入延时时间', trigger: 'blur' }]">
          <el-input placeholder="请输入延时时间" v-model="addSceneForm.delaySeconds" auto-complete="off" style="width:90%;"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="addSceneFormVisible = false" size="small">取 消</el-button>
        <el-button type="primary" @click="configScene('addSceneForm')" size="small">确 定</el-button>
        <el-button @click="resetForm('addSceneForm')">重 置</el-button>
      </div>
    </el-dialog>
    <!--测试mock配置界面-->
    <el-dialog id="testForm" title="测试mock配置" :visible.sync="testInterfaceFormVisible" :close-on-click-modal="false" :close-on-press-escape="false">
      <el-form :model="testForm" ref="testForm" label-position="right" size="small" :label-width="formLabelWidth">
        <el-form-item label="Request Method: ">
          <span class="itemStyle">{{ testForm.httpMethod }}</span>
        </el-form-item>
        <el-form-item label="Content-Type: " v-if="testForm.httpMethod === 'POST'">
          <span class="itemStyle">{{ testForm.contentType }}</span>
        </el-form-item>
        <el-form-item label="请求报文" prop="requestBody" :rules="[{ required: true, message: '请输入请求报文', trigger: 'blur' }]">
          <el-input type="textarea" :autosize="{ minRows: 2, maxRows: 4}" placeholder="请输入请求报文" v-model="testForm.requestBody" style="width:90%;"></el-input>
        </el-form-item>
        <el-form-item label="响应报文: ">
          <span class="itemStyle">{{ testForm.responseBody }}</span>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click="test('testForm')" size="small">测 试</el-button>
        <el-button @click="resetForm('testForm')">重 置</el-button>
      </div>
    </el-dialog>
  </d2-container>
</template>
<script>
import { addMockProject, editMockProject, delMockProject, queryMockInterfaces } from '@/api/mock/mock-config/project'
import { addMockScene, editMockScene, deleteMock, queryMockDetails, testMockPost, testMockGet } from '@/api/mock/mock-config/scene'
import { addMockInterface, editMockInterface, delMockInterface, queryMockInterfaceDetail } from '@/api/mock/mock-config/interface'
import { sortListByItem } from '@/libs/common'
import { mapState } from 'vuex'

export default {
  name: 'mock',
  data() {
    return {
      empty: '""',
      formLabelWidth: '130px',
      /* 选中树节点的系统和接口数据*/
      mockConfig: {
        projectName: '',
        interfaceName: ''
      },
      /* 系统列表*/
      projectOptions: [],
      /* 接口列表*/
      interfaceOptions: [],
      /* http方法枚举*/
      httpMethodOptions: ['POST', 'GET'],
      /* http请求contentType枚举*/
      contentTypeOptions: ['application/json;charset=UTF-8', 'application/x-www-form-urlencoded;charset=UTF-8', 'text/xml;charset=GBK'],
      /* 配置系统页面是否可见开关*/
      addProjectFormVisible: false,
      /* 配置系统页面参数*/
      addProjectForm: {
        projectName: '',
        oldProjectName: ''
      },
      /* 配置mock接口页面是否可见开关*/
      addInterfaceFormVisible: false,
      /* 配置mock接口页面参数*/
      addInterfaceForm: {
        id: '',
        projectName: '',
        interfaceDesc: '',
        httpMethod: '',
        contentType: '',
        requestBody: '',
        responseBody: '',
        realUrl: '',
        commentDefault: '默认场景',
        comment: ''
      },
      /* 配置mock场景页面是否可见开关*/
      addSceneFormVisible: false,
      /* 配置mock场景页面参数*/
      addSceneForm: {
        requestBody: '',
        responseBody: '',
        comment: '',
        rowId: '',
        isDelay: false,
        delaySeconds: ''
      },
      /* 测试mock接口配置页面是否可见开关*/
      testInterfaceFormVisible: false,
      /* 测试mock接口配置页面参数*/
      testForm: {
        projectName: '',
        interfaceName: '',
        requestBody: '',
        responseBody: '',
        hostInfo: '',
        contentType: '',
        httpMethod: '',
        interfaceOptions: []
      },
      /* 接口公共属性，第三方url和mockurl*/
      interfaceProp: {
        show: false,
        realUrl: '',
        mockUrl: '',
        httpMethod: '',
        contentType: '',
        interfaceId: ''
      },
      allOptions: [],
      /* 表格数据集合*/
      tableData: [],
      // 默认每页数据量
      pageSize: 10,
      // 当前页码
      currentPage: 1,
      // 默认数据总数
      totalCount: 0,
      filterText: '',
      treeData: [],
      defaultProps: {
        children: 'children',
        label: 'label'
      },
      nodeKeys: [],
      nodeKey: '',
      idx: -1
    }
  },
  computed: {
    ...mapState('d2admin/user', ['info'])
  },
  methods: {
    /* 新增系统*/
    handleAddProject() {
      this.addProjectFormVisible = true
      this.$nextTick(function() {
        this.resetForm('addProjectForm')
      })
      this.idx = -1
    },
    /* 编辑系统*/
    handleEditProject() {
      this.addProjectFormVisible = true
      this.$nextTick(function() {
        this.clearForm('addProjectForm')
      })
      this.idx = 1
      this.addProjectForm.oldProjectName = this.addProjectForm.projectName
    },
    /* 右键菜单新增系统触发事件*/
    handleAddInterface() {
      this.addInterfaceFormVisible = true
      this.addInterfaceForm.realUrl = ''
      this.addInterfaceForm.httpMethod = ''
      this.addInterfaceForm.contentType = ''
      this.addInterfaceForm.interfaceDesc = ''
      this.addInterfaceForm.responseBody = ''
      this.$nextTick(function() {
        this.clearForm('addInterfaceForm')
      })
      this.idx = -1
    },
    /* 右键菜单编辑系统触发事件*/
    handleEditInterface() {
      queryMockInterfaceDetail({ interfaceId: this.interfaceProp.interfaceId }).then(res => {
        this.addInterfaceForm.realUrl = res.detail.realUrl
        this.addInterfaceForm.httpMethod = res.detail.httpMethod
        this.addInterfaceForm.contentType = res.detail.contentType
        this.addInterfaceForm.interfaceDesc = res.detail.interfaceDesc
        this.addInterfaceFormVisible = true
        this.$nextTick(function() {
          this.clearForm('addInterfaceForm')
        })
        this.idx = 1
      })
    },
    /* 新增系统绑定事件*/
    addProject(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          if (this.idx === -1) {
            addMockProject({
              projectName: this.addProjectForm.projectName
            }).then(resp => {
              this.addProjectFormVisible = false
              this.$message.success('新增成功')
              this.refreshTree()
            })
          } else {
            editMockProject({
              projectNameOld: this.addProjectForm.oldProjectName,
              projectNameNew: this.addProjectForm.projectName
            }).then(resp => {
              this.addProjectFormVisible = false
              this.$message.success('编辑成功')
              this.refreshTree()
            })
          }
        } else {
          return false
        }
      })
    },
    /* 删除系统绑定事件*/
    delProject() {
      this.$confirm('确认删除<' + this.$refs.tree.getCurrentNode().label + '>？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        center: true
      })
        .then(() => {
          delMockProject({
            projectName: this.$refs.tree.getCurrentNode().label
          }).then(resp => {
            this.$message.success('删除成功')
            this.refreshTree()
          })
        })
        .catch(() => {
          this.$message.info('已取消删除')
        })
    },
    /* 删除接口*/
    handleDelInterface() {
      console.log(this.addInterfaceForm.id)
      this.$confirm('确认删除<' + this.$refs.tree.getCurrentNode().label + '>？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        center: true
      })
        .then(() => {
          delMockInterface({
            interfaceId: this.$refs.tree.getCurrentNode().intfId
          }).then(resp => {
            this.$message.success('删除成功')
            this.refreshTree()
            this.nodeKey = this.addInterfaceForm.id
            this.nodeKeys = []
            this.nodeKeys.push(this.nodeKey)
          })
        })
        .catch(() => {
          this.$message.info('已取消删除')
        })
    },
    /* 配置mock接口页面确定按钮绑定事件*/
    addInterface(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          if (this.idx === -1) {
            this.addMockInterface(
              this.addInterfaceForm.projectName,
              this.addInterfaceForm.interfaceDesc,
              this.addInterfaceForm.httpMethod,
              this.addInterfaceForm.contentType,
              this.addInterfaceForm.responseBody,
              this.addInterfaceForm.realUrl,
              this.info.name,
              this.addInterfaceForm.commentDefault
            ).then(val => {
              if (val === '000') {
                this.refreshTree()
                this.interfaceProp.show = false
                let obj = this.treeData.find(c => c.label === this.addInterfaceForm.projectName)
                this.nodeKey = obj.id
                this.nodeKeys = []
                this.nodeKeys.push(this.nodeKey)
              } else {
                return false
              }
            })
          } else {
            this.editMockInterface(
              this.interfaceProp.interfaceId,
              this.addInterfaceForm.interfaceDesc,
              this.addInterfaceForm.httpMethod,
              this.addInterfaceForm.contentType,
              this.addInterfaceForm.realUrl,
              this.info.name
            ).then(val => {
              if (val === '000') {
                this.refreshTree()
                this.interfaceProp.show = false
                let obj = this.treeData.find(c => c.label === this.addInterfaceForm.projectName)
                this.nodeKey = obj.id
                this.nodeKeys = []
                this.nodeKeys.push(this.nodeKey)
              } else {
                return false
              }
            })
          }
        } else {
          return false
        }
      })
    },
    /* 新增mock接口入口函数*/
    addMockInterface(projectName, interfaceDesc, httpMethod, contentType, responseBody, realUrl, operator, comment) {
      responseBody = responseBody.replace(/[\r\n\t]/g, '')
      if (contentType === 'application/json;charset=UTF-8') {
        try {
          responseBody = JSON.parse(responseBody)
        } catch (e) {
          this.$message.error('响应报文非json格式')
          return false
        }
      }
      if (httpMethod === 'POST') {
        return addMockInterface({
          projectName: projectName,
          interfaceDesc: interfaceDesc,
          httpMethod: httpMethod,
          contentType: contentType,
          responseBody: responseBody,
          realUrl: realUrl,
          operator: operator,
          comment: comment
        }).then(resp => {
          this.addInterfaceFormVisible = false
          this.$message.success('配置成功')
          return resp.code
        })
      } else {
        return addMockInterface({
          projectName: projectName,
          interfaceDesc: interfaceDesc,
          httpMethod: httpMethod,
          responseBody: responseBody,
          realUrl: realUrl,
          operator: operator,
          comment: comment
        }).then(resp => {
          this.addInterfaceFormVisible = false
          this.$message.success('配置成功')
          return resp.code
        })
      }
    },
    /* 修改mock接口入口函数*/
    editMockInterface(interfaceId, interfaceDesc, httpMethod, contentType, realUrl, operator) {
      if (httpMethod === 'POST') {
        return editMockInterface({
          interfaceId: interfaceId,
          interfaceDesc: interfaceDesc,
          httpMethod: httpMethod,
          contentType: contentType,
          realUrl: realUrl,
          operator: operator
        }).then(resp => {
          this.addInterfaceFormVisible = false
          this.$message.success('配置成功')
          return resp.code
        })
      } else {
        return editMockInterface({
          interfaceId: interfaceId,
          interfaceDesc: interfaceDesc,
          httpMethod: httpMethod,
          realUrl: realUrl,
          operator: operator
        }).then(resp => {
          this.addInterfaceFormVisible = false
          this.$message.success('配置成功')
          return resp.code
        })
      }
    },
    isSelectedTestMethod() {
      queryMockDetails({
        projectName: this.testForm.projectName,
        interfaceId: this.interfaceProp.interfaceId,
        pageSize: 10,
        currentPage: 1
      }).then(resp => {
        this.testForm.httpMethod = resp.tableData[0].httpMethod
        this.testForm.contentType = resp.tableData[0].contentType
      })
    },
    /* 从后台查询mock接口数据函数*/
    queryMockData(projectName, interfaceId, pageSize, currentPage) {
      this.loadData(projectName, interfaceId, pageSize, currentPage)
    },
    /* 主页面查询接口入口函数*/
    loadData(projectName, interfaceId, pageSize, currentPage) {
      return queryMockDetails({
        projectName: projectName,
        interfaceId: interfaceId,
        pageSize: pageSize,
        currentPage: currentPage
      }).then(resp => {
        if (resp.tableData === 'no data') {
          this.tableData = []
          this.totalCount = resp.totalNum
        } else {
          this.tableData = resp.tableData
          this.totalCount = resp.totalNum
          this.interfaceProp.show = true
          this.interfaceProp.mockUrl = this.tableData[0].mockUrl
          this.interfaceProp.realUrl = this.tableData[0].realUrl
          this.interfaceProp.httpMethod = this.tableData[0].httpMethod
          this.interfaceProp.contentType = this.tableData[0].contentType
        }
      })
    },
    /* 切换表格每页显示记录数逻辑*/
    handleSizeChange(val) {
      this.pageSize = val
      this.currentPage = 1
      this.queryMockData(this.mockConfig.projectName, this.interfaceProp.interfaceId, this.pageSize, this.currentPage)
    },
    /* 切换表格页码逻辑*/
    handleCurrentChange(val) {
      this.currentPage = val
      this.queryMockData(this.mockConfig.projectName, this.interfaceProp.interfaceId, this.pageSize, this.currentPage)
    },
    /* 配置mock场景页面确定按钮绑定事件*/
    configScene(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          this.configMockScene(
            this.mockConfig.projectName,
            this.interfaceProp.interfaceId,
            this.addSceneForm.requestBody,
            this.addSceneForm.responseBody,
            this.info.name,
            this.addSceneForm.comment,
            this.addSceneForm.rowId,
            this.addSceneForm.delaySeconds
          ).then(val => {
            if (val === '000') {
              this.queryMockData(this.mockConfig.projectName, this.interfaceProp.interfaceId, 10, 1)
            } else {
              return false
            }
          })
        } else {
          return false
        }
      })
    },
    /* 配置mock场景入口函数*/
    configMockScene(projectName, interfaceId, requestBody, responseBody, operator, comment, rowId, delaySeconds) {
      requestBody = requestBody.replace(/[\r\n\t]/g, '')
      responseBody = responseBody.replace(/[\r\n\t]/g, '')
      if (rowId === '') {
        return addMockScene({
          projectName: projectName,
          interfaceId: interfaceId,
          requestBody: requestBody,
          responseBody: responseBody,
          operator: operator,
          comment: comment,
          delaySeconds: delaySeconds
        }).then(resp => {
          this.addSceneFormVisible = false
          this.$message.success('配置成功')
          return resp.code
        })
      } else {
        return editMockScene({
          projectName: projectName,
          interfaceId: interfaceId,
          requestBody: requestBody,
          responseBody: responseBody,
          operator: operator,
          comment: comment,
          id: rowId,
          delaySeconds: delaySeconds
        }).then(resp => {
          this.addSceneFormVisible = false
          this.$message.success('配置成功')
          return resp.code
        })
      }
    },
    /* 新增场景 逻辑*/
    handleClick() {
      this.addSceneForm.requestBody = ''
      this.addSceneForm.responseBody = ''
      this.addSceneForm.comment = ''
      this.addSceneForm.rowId = ''
      this.addSceneForm.delaySeconds = ''
      this.addSceneForm.isDelay = false
      this.addSceneFormVisible = true
      this.$nextTick(function() {
        this.clearForm('addSceneForm')
      })
    },
    /* 表格操作列 编辑按钮 逻辑*/
    handleEdit(row) {
      this.addSceneForm.requestBody = row.requestBody
      this.addSceneForm.responseBody = row.responseBody
      this.addSceneForm.comment = row.comment
      this.addSceneForm.rowId = row.id
      this.addSceneForm.delaySeconds = row.delaySeconds
      this.addSceneForm.isDelay = row.delaySeconds !== 0
      this.addSceneFormVisible = true
      this.$nextTick(function() {
        this.clearForm('addSceneForm')
      })
    },
    /* 表格操作列 删除按钮 逻辑*/
    handleDelete(row) {
      this.$confirm('确认删除？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        center: true
      })
        .then(() => {
          this.deleteMockScence(row.id).then(val => {
            if (val === '000') {
              this.queryMockData(this.mockConfig.projectName, this.interfaceProp.interfaceId, 10, 1)
            } else {
              return false
            }
          })
        })
        .catch(() => {
          this.$message.info('已取消删除')
        })
    },
    /* 删除mock场景入口函数*/
    deleteMockScence(id) {
      return deleteMock({
        id: id.toString()
      }).then(resp => {
        this.$message.success('删除成功')
        return resp.code
      })
    },
    /* 打开测试场景页面*/
    testClick() {
      this.testInterfaceFormVisible = true
      this.testForm.requestBody = ''
      this.testForm.responseBody = ''
      this.isSelectedTestMethod()
    },
    /* 测试mock接口页面测试按钮绑定事件*/
    test(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          this.testForm.responseBody = ''
          this.testMockInterface(
            this.testForm.projectName,
            this.testForm.interfaceName,
            this.testForm.requestBody,
            this.testForm.httpMethod,
            this.testForm.contentType
          )
        } else {
          return false
        }
      })
    },
    /* 测试mock接口入口函数*/
    testMockInterface(projectName, interfaceName, requestBody, httpMethod, contentType) {
      requestBody = requestBody.replace(/[\r\n\t]/g, '')
      try {
        requestBody = JSON.parse(requestBody)
      } catch (e) {
        console.log(e)
      }
      if (httpMethod === 'POST') {
        testMockPost({
          projectName: projectName,
          interfaceName: interfaceName,
          requestBody: requestBody,
          contentType: contentType
        }).then(resp => {
          if (resp) {
            if (Object.prototype.toString.call(resp) === '[object String]' || !('mockCode' in resp)) {
              this.testForm.responseBody = resp
            } else {
              this.$message.error(resp.desc)
            }
          }
        })
      } else {
        testMockGet({
          projectName: projectName,
          interfaceName: interfaceName,
          requestBody: requestBody
        }).then(resp => {
          if (resp) {
            if (Object.prototype.toString.call(resp) === '[object String]' || !('mockCode' in resp)) {
              this.testForm.responseBody = resp
            } else {
              this.$message.error(resp.desc)
            }
          }
        })
      }
    },
    refreshTree() {
      /* 页面加载时从后台获取全部已配置的接口数据用于展示节点数*/
      queryMockInterfaces().then(resp => {
        this.testForm.hostInfo = resp.host
        this.allOptions = resp.desc
        this.projectOptions = []
        this.treeData = []
        let key = 1
        for (let i in this.allOptions) {
          this.projectOptions.push(i)
          let treeItem = {}
          treeItem.id = key++
          treeItem.label = i
          treeItem.children = []
          if (this.allOptions[i].length > 0) {
            for (let j = 0, len = this.allOptions[i].length; j < len; j++) {
              let childItem = {}
              childItem.id = key++
              childItem.label = this.allOptions[i][j].interface_desc + '__' + this.allOptions[i][j].interface_name
              childItem.name = this.allOptions[i][j].interface_name
              childItem.intfId = this.allOptions[i][j].interface_id
              treeItem.children.push(childItem)
            }
            treeItem.children.sort(sortListByItem('label'))
          }
          this.treeData.push(treeItem)
        }
        this.treeData.sort(sortListByItem('label'))
      })
    },
    handleNodeClick(data, node) {
      if (!data.children) {
        this.interfaceProp.show = true
        this.mockConfig.projectName = node.parent.data.label
        this.mockConfig.interfaceName = data.name
        this.testForm.projectName = node.parent.data.label
        this.testForm.interfaceName = data.name
        this.interfaceProp.interfaceId = data.intfId
        this.queryMockData(this.mockConfig.projectName, this.interfaceProp.interfaceId, 10, 1)
      } else {
        this.interfaceProp.show = false
      }
    },
    rightClick(event, object, value, element) {
      this.$refs.tree.setCurrentKey(value.key)
      if (value.level === 1) {
        const position = {
          top: event.clientY,
          left: event.clientX + 20
        }
        this.$refs['contextMenuInterface'].hide()
        this.$refs['contextMenuSystem'].show(position)
        this.addProjectForm.projectName = value.label
        this.addInterfaceForm.projectName = value.label
      } else if (value.level === 2) {
        const position = {
          top: event.clientY,
          left: event.clientX + 20
        }
        this.$refs['contextMenuSystem'].hide()
        this.$refs['contextMenuInterface'].show(position)
        this.addInterfaceForm.id = value.parent.data.id
        this.addInterfaceForm.projectName = value.parent.label
        this.addInterfaceForm.interfaceName = value.data.name
        this.addInterfaceForm.interfaceDesc = value.label
        this.mockConfig.projectName = value.parent.label
        this.mockConfig.interfaceName = value.data.name
        this.testForm.projectName = value.parent.label
        this.testForm.interfaceName = value.data.name
        this.interfaceProp.interfaceId = value.data.intfId
      }
      /* console.log("右键被点击的event:",event);
                 console.log("右键被点击的object:",object);
                 console.log("右键被点击的value:",value);
                 console.log("右键被点击的element:",element);*/
    },
    filterNode(value, data) {
      if (!value) {
        return true
      }
      return data.label.indexOf(value) !== -1
    },
    // 勾选是否延时
    isChanged() {
      this.addSceneForm.delaySeconds = ''
    },
    // 重置表单
    resetForm(formName) {
      if (this.$refs[formName] !== undefined) {
        this.$refs[formName].resetFields()
        if (formName === 'testForm') {
          this.testForm.responseBody = ''
        }
      }
    },
    // 重置校验规则
    clearForm(formName) {
      if (this.$refs[formName] !== undefined) {
        this.$refs[formName].clearValidate()
      }
    }
  },
  watch: {
    filterText(val) {
      this.$refs.tree.filter(val)
    }
  },
  mounted() {
    this.refreshTree()
  }
}
</script>
<style lang="scss">
.example {
  padding: 10px;
  height: 100%;
  min-height: 720px;
  margin-top: 20px;
  box-shadow: 0 1px 12px 3px rgba(0, 0, 0, 0.1);
}

.category {
  .el-tree-node__content {
    height: 30px;
  }
}

.mockScrolllist {
  max-height: 680px;
}

.filter-field {
  display: block;
  width: 100%;
  padding: 3px;
}

.formStyle {
  font-weight: bold;
}

.itemStyle {
  color: #66b1ff;
  word-wrap: break-word;
  font-size: 13px;
}

.titleStyle {
  font-size: 13px;
  color: #606266;
}

.custom-tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  padding-right: 8px;
}

.el-tree--highlight-current .el-tree-node.is-current > .el-tree-node__content {
  background-color: #3a8ee62b;
}

.header-icon {
  color: #66b1ff;
}
</style>
