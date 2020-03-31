<template>
  <d2-container>
    <div class="table_container">
      <!--<el-alert
              title="操作说明"
              description="请按公司名查询，然后在左侧树节点上使用右键操作“新增/修改/删除 工程”，可查看工程下所有接口以及接口测试用例"
              type="success"
              show-icon>
      </el-alert>-->
      <div class="handle-box">
        <el-form ref="companyForm" :model="baseForm" label-width="80px" inline>
          <el-form-item label="公司名称" prop="companyId" :rules="[{required:true,message:'请选择公司',trigger:'change'}]">
            <el-select v-model="baseForm.companyId" filterable placeholder="请选择公司">
              <el-option v-for="item in companyTableData" :key="item.companyId" :label="item.companyName" :value="item.companyId"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="el-icon-search" @click="search('companyForm')" :loading="searchLoading">搜 索</el-button>
            <el-button type="primary" style="margin-left: 10px" icon="el-icon-setting" @click="configCompany()">公司配置</el-button>
          </el-form-item>
          <el-form-item class="intf-radius">
            <el-form :model="summaryForm">
              <el-form-item>
                <span class="text">系统总数 - {{summaryForm.systemTotalNum}}</span>
                <el-divider direction="vertical"></el-divider>
                <span class="text">接口总数 - {{summaryForm.intfTotalNum}}</span>
                <el-divider direction="vertical"></el-divider>
                <span class="text">HTTP接口总数 - {{summaryForm.intfHttpNum}}</span>
                <el-divider direction="vertical"></el-divider>
                <span class="text">DUBBO接口总数 - {{summaryForm.intfDubboNum}}</span>
                <el-divider direction="vertical"></el-divider>
                <span class="text">MQ接口总数 - {{summaryForm.intfMqNum}}</span>
                <el-divider direction="vertical"></el-divider>
                <span class="text">用例总数 - {{summaryForm.caseTotalNum}}</span>
                <el-divider direction="vertical"></el-divider>
                <span class="text">可自动化用例总数 - {{summaryForm.caseAutoNum}}</span>
              </el-form-item>
            </el-form>
          </el-form-item>
        </el-form>
      </div>
      <el-row>
        <el-col :span="6">
          <div class="example-resintf">
            <div class="navigation-filter">
              <el-row :gutter="10">
                <el-col :span="16">
                  <el-input placeholder="输入关键字搜索" v-model="filterText"></el-input>
                </el-col>
                <el-col :span="4">
                  <el-tooltip content="新增工程" placement="bottom" effect="light">
                    <el-button icon="el-icon-plus" @click="handleAddProject()"></el-button>
                  </el-tooltip>
                </el-col>
                <el-col :span="4">
                  <el-tooltip :content="switchValue1" placement="bottom" effect="light">
                    <el-switch v-model="switchValue1" active-value="显示全部工程" inactive-value="只显示有接口工程" @change="valueSwitch(switchValue1)"></el-switch>
                  </el-tooltip>
                </el-col>
              </el-row>
            </div>
            <!--树状结构-->
            <el-scrollbar wrap-class="resIntfScrolllist" view-class="view-box" :native="false">
              <div class="resIntfList">
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
          <div class="example-resintf" v-show="caseTableVisible">
            <case-table :intf-info="intfInfo" ref="caseTable" @update-data="updateData"></case-table>
          </div>
        </el-col>
      </el-row>
    </div>
    <!--公司配置弹窗-->
    <el-dialog title="配置公司" :visible.sync="companyEditVisible" width="45%" :close-on-click-modal="false" :close-on-press-escape="false" ref="companyEditDialog">
      <el-form size="mini">
        <!--新增公司弹窗-->
        <el-form-item>
          <strong>
            <span>添加公司</span>
          </strong>
          <el-tooltip placement="top" content="添加" effect="light">
            <el-button type="primary" size="mini" style="margin-left: 20px" icon="el-icon-plus" @click.stop="addCompany()" plain></el-button>
          </el-tooltip>
        </el-form-item>
        <el-form ref="formCompanyFirst" :model="baseForm" label-width="100px" inline v-show="companyFormShow">
          <el-form-item label="公司名称" prop="companyName" :rules="[{required: true, message: '公司名称不能为空', trigger: 'blur'}]">
            <el-input type="textarea" autosize style="width: 100%" v-model="baseForm.companyName"></el-input>
          </el-form-item>
          <el-form-item label="描述信息" prop="desc">
            <el-input type="textarea" autosize style="width: 100%" v-model="baseForm.desc"></el-input>
          </el-form-item>
          <el-form-item>
            <el-tooltip placement="top" content="保存" effect="light">
              <el-button type="info" size="mini" style="margin-left: 20px" icon="el-icon-circle-check" @click.prevent="saveCompany()" plain>保存</el-button>
            </el-tooltip>
          </el-form-item>
        </el-form>
        <!--公司表格-->
        <el-table
          :data="companyTableData"
          border
          style="width: 100%;margin-top: 5px"
          ref="multipleTable"
          :header-cell-style="{color:'black',background:'#eef1f6'}"
        >
          <el-table-column prop="companyId" label="公司ID" width="100"></el-table-column>
          <el-table-column prop="companyName" label="公司名称" width="auto"></el-table-column>
          <el-table-column prop="simpleDesc" label="描述信息" width="auto"></el-table-column>
          <el-table-column label="操作" fixed="right" width="200">
            <template slot-scope="scope">
              <el-button size="mini" type="primary" icon="el-icon-edit" @click="handleEditCompany(scope.$index, scope.row)" plain></el-button>
              <el-button size="mini" style="margin-left: 10px" type="danger" icon="el-icon-delete" @click="handleDeleteCompany(scope.$index, scope.row)" plain></el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-form>
    </el-dialog>
    <!--工程配置弹窗-->
    <el-dialog title="配置工程" :visible.sync="projectEditVisible" width="30%" :close-on-click-modal="false" :close-on-press-escape="false" ref="projectEditDialog">
      <el-form ref="projectEditForm" :model="projectEditForm" label-width="100px">
        <el-form-item label="工程名称" prop="projectName" :rules="[{ required: true, message: '工程名称必填', trigger: 'blur' }]">
          <el-input v-model="projectEditForm.projectName" placeholder="请输入工程名称"></el-input>
        </el-form-item>
        <el-form-item label="git URL" prop="gitSshURL" :rules="[{ required: true, message: 'git URL必填', trigger: 'blur' }]">
          <el-input v-model="projectEditForm.gitSshURL" placeholder="示例git@git.immd.cn:QA/atp-qa-core.git"></el-input>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="projectEditVisible = false">取 消</el-button>
        <el-button type="primary" @click="saveProjectEdit('projectEditForm')">确 定</el-button>
      </span>
    </el-dialog>
    <!--接口配置弹窗-->
    <el-dialog
      title="配置接口"
      :visible.sync="editApiVisible"
      width="50%"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      ref="apiEditDialog"
      class="apiEditDialog"
    >
      <el-form ref="apiEditForm" :model="apiEditForm" label-width="100px" :rules="rules" class="apiEditForm">
        <el-form-item label="接口中文名" prop="apiNameInChinese">
          <el-input v-model="apiEditForm.apiNameInChinese" placeholder="请输入接口中文名"></el-input>
        </el-form-item>
        <el-form-item label="接口类型" prop="interfaceType">
          <el-select v-model="apiEditForm.interfaceType" placeholder="请选择接口类型">
            <el-option v-for="item in apiEditForm.interfaceTypeOptions" :key="item" :label="item" :value="item"></el-option>
          </el-select>
        </el-form-item>
        <div v-if="apiEditForm.interfaceType === 'HTTP'">
          <el-form-item label="API URL" prop="apiUrl">
            <el-row>
              <el-col :span="19">
                <el-input v-model="apiEditForm.apiUrl" placeholder="示例/atp/auto/support/generateIdCard" style="width: 100%"></el-input>
              </el-col>
              <el-col :span="5">
                <el-button type="text" icon="el-icon-question" @click="openApiUrlDesc" circle>说明</el-button>
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="头域" prop="headers">
            <el-row>
              <el-col :span="19">
                <el-input v-model="apiEditForm.headers" style="width: 100%"></el-input>
              </el-col>
              <el-col :span="5">
                <el-button type="text" icon="el-icon-question" @click="openHeaderDesc" circle>说明</el-button>
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="请求方法" prop="method">
            <el-select v-model="apiEditForm.method" placeholder="请选择">
              <el-option v-for="item in apiEditForm.methodOptions" :key="item" :label="item" :value="item"></el-option>
            </el-select>
          </el-form-item>
        </div>
        <div v-if="apiEditForm.interfaceType === 'DUBBO'">
          <el-form-item label="服务名" prop="dubboService">
            <el-input v-model="apiEditForm.dubboService" placeholder="示例cn.memedai.biis.facade.businesses.DubboSchoolInfoBusiness"></el-input>
          </el-form-item>
          <el-form-item label="方法名" prop="dubboMethod">
            <el-input v-model="apiEditForm.dubboMethod" placeholder="示例getProvinces"></el-input>
          </el-form-item>
          <el-form-item label="参数类型" prop="parameterTypes">
            <el-row>
              <el-col :span="19">
                <el-input
                  v-model="apiEditForm.parameterTypes"
                  placeholder="示例['java.lang.String','cn.memedai.wallet.facade.forms.ApplyRequiredInfoForm']"
                  style="width: 100%"
                ></el-input>
              </el-col>
              <el-col :span="5">
                <el-button type="text" icon="el-icon-question" @click="openParameterTypesDesc" circle>说明</el-button>
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="版本号" prop="version">
            <el-row>
              <el-col :span="19">
                <el-input v-model="apiEditForm.version" placeholder="示例1.0.0" style="width: 100%"></el-input>
              </el-col>
              <el-col :span="5">
                <el-button type="text" icon="el-icon-question" @click="openVersionDesc" circle>说明</el-button>
              </el-col>
            </el-row>
          </el-form-item>
        </div>
        <div v-if="apiEditForm.interfaceType === 'MQ'">
          <el-form-item label="topic" prop="topic">
            <el-input v-model="apiEditForm.topic" placeholder="示例TP_MIME_UNION_FUND"></el-input>
          </el-form-item>
          <el-form-item label="tag" prop="tag">
            <el-input v-model="apiEditForm.tag" placeholder="示例TAG_capital-mgmt-core_capitalResult"></el-input>
          </el-form-item>
          <el-form-item label="使用appId" prop="isAppId">
            <el-checkbox v-model="apiEditForm.isAppId"></el-checkbox>
          </el-form-item>
          <el-form-item label="appId" prop="appId" v-if="apiEditForm.isAppId">
            <el-input v-model="apiEditForm.appId" placeholder="请输入appId"></el-input>
          </el-form-item>
        </div>
        <el-form-item label="依赖接口列表" prop="intfRelation">
          <el-cascader
            id="el-cascader"
            v-model="apiEditForm.intfRelation"
            :options="apiEditForm.intfRelationOption"
            :props="{multiple: true, label: 'label', value: 'treeId'}"
            clearable
            style="width:100%"
          ></el-cascader>
        </el-form-item>
        <!--接口入参列表-->
        <el-collapse v-model="activeNames">
          <el-collapse-item title="接口入参列表" name="1">
            <el-form :model="apiParamsForm" label-width="100px" class="apiParamsForm" ref="apiParamsForm">
              <el-form-item label="接口入参" prop="apiParams" :rules="[{ required: true, message: '接口入参必填', trigger: 'blur' }]">
                <el-row :gutter="20" type="flex" justify="center">
                  <el-col :span="20">
                    <el-input
                      type="textarea"
                      v-model="apiParamsForm.apiParams"
                      :autosize="{ minRows: 7, maxRows: 10}"
                      placeholder="示例 http/mq {'timestamp':''} dubbo ['1',{'A':1}]"
                      style="width: 100%"
                      @blur="parseIntfParms"
                    ></el-input>
                  </el-col>
                  <el-col :span="4">
                    <el-button size="mini" plain @click="formatIntfParms()" style="margin-top: 30px">{{apiParamsForm.butLabel}}</el-button>
                    <!--<el-button size="mini" plain @click="parseIntfParms()" style="margin-top: 20px">解析入参</el-button>-->
                  </el-col>
                </el-row>
              </el-form-item>
            </el-form>
            <el-table
              :data="apiParamsForm.apiParamsTableData"
              border
              style="width: 100%"
              ref="apiParamsMultipleTable"
              row-key="id"
              max-height="350"
              show-overflow-tooltip
            >
              <el-table-column type="index"></el-table-column>
              <el-table-column prop="paramName" label="参数名称" width="200%"></el-table-column>
              <el-table-column prop="paramType" label="参数类型" width="80%"></el-table-column>
              <el-table-column prop="isRequired" label="是否必填" width="70" align="center">
                <template slot-scope="scope">
                  <el-checkbox v-model="scope.row.isRequired"></el-checkbox>
                </template>
              </el-table-column>
              <el-table-column prop="paramRule" label="参数规则"></el-table-column>
              <el-table-column prop="paramDefVal" label="默认值"></el-table-column>
              <el-table-column label="操作" fixed="right" width="60">
                <template slot-scope="scope">
                  <el-button
                    type="text"
                    @click="handEditApiParams(scope.$index, scope.row)"
                    v-if="!(scope.row.paramType === 'object' || scope.row.paramType === 'array')"
                  >编辑</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-collapse-item>
        </el-collapse>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="editApiVisible = false">取 消</el-button>
        <el-button type="primary" @click="saveApiEdit()">确 定</el-button>
      </span>
    </el-dialog>
    <!--编辑入参弹框-->
    <el-dialog
      title="配置入参规则"
      :visible.sync="apiParamsRuleForm.editApiParamsRuleVisible"
      width="30%"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      ref="apiParmsRuleEditDialog"
      class="apiParmsRuleEditDialog"
    >
      <el-form label-width="80px" ref="apiParamsRuleForm" :model="apiParamsRuleForm">
        <el-form-item label="入参名称" prop="apiParamsName">
          <el-input v-model="apiParamsRuleForm.apiParamsName" :disabled="true"></el-input>
        </el-form-item>
        <el-form-item label="入参类型" prop="apiParamsType">
          <el-input v-model="apiParamsRuleForm.apiParamsType" :disabled="true"></el-input>
        </el-form-item>
        <el-form-item label="规则类型" prop="apiParamsRuleType" :rules="[{ required: true, message: '入参规则必填', trigger: 'change' }]">
          <el-select v-model="apiParamsRuleForm.apiParamsRuleType" placeholder="请选择入参规则" @change="apiParamsRuleForm.apiParamsRuleVal = ''">
            <el-option v-for="item in apiParamsRuleForm.apiParamsRuleTypeOptions" :key="item.key" :label="item.label" :value="item.value"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="规则内容" prop="apiParamsRuleVal" :rules="[{ required: true, message: '规则内容必填', trigger: 'blur' }]">
          <el-input v-model="apiParamsRuleForm.apiParamsRuleVal" placeholder="请输入规则内容"></el-input>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="apiParamsRuleForm.editApiParamsRuleVisible = false">取 消</el-button>
        <el-button type="primary" @click="saveApiParamsRuleEdit('apiParamsRuleForm')">确 定</el-button>
      </span>
    </el-dialog>
    <!-- 删除公司提示框 -->
    <el-dialog title="提示" :visible.sync="delCompanyVisible" width="300px" center>
      <div class="del-dialog-cnt">删除不可恢复，是否确定删除公司？</div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="delCompanyVisible = false">取 消</el-button>
        <el-button type="danger" icon="el-icon-warning" @click="deleteCompany()">删 除</el-button>
      </span>
    </el-dialog>
    <!-- 删除工程提示框 -->
    <el-dialog title="提示" :visible.sync="delProjectVisible" width="300px" center>
      <div class="del-dialog-cnt">删除不可恢复，是否确定删除工程？</div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="delProjectVisible = false">取 消</el-button>
        <el-button type="danger" icon="el-icon-warning" @click="deleteApiSystem()">删 除</el-button>
      </span>
    </el-dialog>
    <!-- 删除接口提示框 -->
    <el-dialog title="提示" :visible.sync="delApiVisible" width="300px" center>
      <div class="del-dialog-cnt">删除不可恢复，是否确定删除工程？</div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="delApiVisible = false">取 消</el-button>
        <el-button type="danger" icon="el-icon-warning" @click="deleteApi()">删 除</el-button>
      </span>
    </el-dialog>
    <!--右键菜单-一级工程-->
    <div>
      <v-contextmenu ref="contextMenuProject">
        <v-contextmenu-item @click="handEditProject()">编辑工程</v-contextmenu-item>
        <v-contextmenu-item @click="handDeleteProject()">删除工程</v-contextmenu-item>
        <v-contextmenu-item divider></v-contextmenu-item>
        <v-contextmenu-item @click="handAddApi()">新增接口</v-contextmenu-item>
        <v-contextmenu-item @click="handExportCase()">导出用例</v-contextmenu-item>
      </v-contextmenu>
    </div>
    <!--右键菜单-二级接口-->
    <div>
      <v-contextmenu ref="contextMenuInterface">
        <v-contextmenu-item @click="handEditApi()">编辑接口</v-contextmenu-item>
        <v-contextmenu-item @click="handDeleteApi()">删除接口</v-contextmenu-item>
        <v-contextmenu-item divider></v-contextmenu-item>
        <v-contextmenu-item @click="handleAddCase()">新增用例</v-contextmenu-item>
      </v-contextmenu>
    </div>
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
import { compare, isJsonString } from '@/libs/common'
import { fetchCompanyList, deleteCompany, addCompany, editCompany, subtree } from '@/api/autotest/manage/resource-apiManage/company'
import { addApiSystem, editApiSystem, deleteApiSystem } from '@/api/autotest/manage/resource-apiManage/system'
import { addApi, editApi, deleteApi, queryApiDetail } from '@/api/autotest/manage/resource-apiManage/api'
import { getStatistics } from '@/api/autotest/manage/resource-apiManage/stat'
import { exportTestCase } from '@/api/autotest/manage/testcase-apiManage/config'

export default {
  name: 'interfaceManage',
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
      projectEditForm: {
        projectId: '',
        projectName: '',
        gitSshURL: ''
      },
      apiEditForm: {
        apiNameInChinese: '',
        interfaceType: '',
        apiId: '',
        interfaceTypeOptions: ['HTTP', 'DUBBO', 'MQ'],
        methodOptions: ['POST', 'GET'],
        apiUrl: '',
        headers: '',
        method: '',
        dubboService: '',
        dubboMethod: '',
        parameterTypes: '',
        version: '',
        topic: '',
        tag: '',
        isAppId: false,
        appId: '',
        apiParams: '',
        intfRelation: '', // 依赖接口列表
        intfRelationOption: [] // 系统所有系统接口数据
      },
      // 接口入参表单
      apiParamsForm: {
        apiParams: '', // 接口入参
        apiParamsTableData: [], // 接口入参列表数据
        apiParamsFormVisible: false, // 接口入参表单是否显示
        butLabel: '格式化入参', // 格式化入参按钮label
        butFlag: true // 格式化入参按钮状态标志
      },
      // 接口入参规则编辑表单
      apiParamsRuleForm: {
        apiParamsName: '', // 接口入参名称
        apiParamsType: '', // 接口入参类型
        editApiParamsRuleVisible: false, // 接口入参规则编辑表单是否显示
        apiParamsRuleType: '', // 接口入参规则类型
        apiParamsRuleVal: '', // 接口入参规则内容
        idx: null, // 接口入参规则编辑页面打开时带入的索引
        apiParamsRuleTypeOptions: [
          {
            // 接口入参规则支持的类型选项
            label: '长度',
            value: 'length'
          },
          {
            label: '最大值',
            value: 'maxVal'
          },
          {
            label: '最小值',
            value: 'minVal'
          }
        ]
      },
      // 统计表单
      summaryForm: {
        systemTotalNum: null,
        intfTotalNum: null,
        intfHttpNum: null,
        intfDubboNum: null,
        intfMqNum: null,
        caseAutoNum: null,
        caseTotalNum: null
      },
      baseForm: {
        companyId: '',
        companyName: '',
        desc: ''
      },
      companyFormShow: false,
      filterText: '',
      switchValue1: '显示全部工程',
      companyTableData: [],
      treeData: [],
      tempTreeData: [],
      defaultProps: {
        children: 'children',
        label: 'label'
      },
      nodeKeys: [],
      nodeKey: '',
      projectEditVisible: false,
      companyEditVisible: false,
      activeNames: ['1'],
      cardIndex: '',
      delCompanyVisible: false,
      delProjectVisible: false,
      delApiVisible: false,
      editApiVisible: false,
      editCompanyIdx: -1,
      editApiSystemIdx: 1,
      editApiIdx: 1,
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
        tag: [{ required: true, message: 'tag必填', trigger: 'blur' }],
        appId: [{ required: true, message: 'appId必填', trigger: 'blur' }]
      },
      id: 0,
      searchLoading: false, // 搜索状态
      downloadXmindTempUrl: '', // 导出操作是后台返回的文件url
      exportVisible: false // 导出弹框是否显示
    }
  },
  mounted() {
    this.getCompanyList()
  },
  watch: {
    // 树状筛选
    filterText(val) {
      this.$refs.tree.filter(val)
      // 清除过滤关键字后刷新树列表为初始状态
      if (!val) {
        for (var i = 0; i < this.$refs.tree.store._getAllNodes().length; i++) {
          this.$refs.tree.store._getAllNodes()[i].expanded = false
        }
      }
    }
  },
  methods: {
    // 点击树节点
    handleNodeClick(data, node) {
      this.$refs['contextMenuProject'].hide()
      this.$refs['contextMenuInterface'].hide()
      this.nodeKey = node.key
      if ('intfId' in data) {
        this.intfInfo = {}
        this.intfInfo['intfId'] = data.intfId
        this.intfInfo['companyId'] = this.baseForm.companyId
        this.caseTableVisible = true
        this.$refs.caseTable.pageLoad(this.intfInfo)
      }
    },
    // 右键树节点
    rightClick(event, object, value, element) {
      this.$refs.tree.setCurrentKey(value.key)
      if (value.level === 1) {
        const position = {
          top: event.clientY,
          left: event.clientX + 20
        }
        this.$refs['contextMenuInterface'].hide()
        this.$refs['contextMenuProject'].show(position)
        this.projectEditForm.projectName = object.label.split('(')[0]
        this.projectEditForm.gitSshURL = object.gitSshURL
        this.projectEditForm.projectId = object.systemId
        this.nodeKey = value.key
        this.parentNodeKey = value.parent.key
      } else if (value.level === 2) {
        const position = {
          top: event.clientY,
          left: event.clientX + 20
        }
        this.$refs['contextMenuProject'].hide()
        this.$refs['contextMenuInterface'].show(position)
        this.apiEditForm.apiId = object.intfId
        this.nodeKey = value.key
        this.parentNodeKey = value.parent.key
        this.intfInfo = {}
        this.intfInfo['intfId'] = object.intfId
        this.intfInfo['companyId'] = this.baseForm.companyId
        this.caseTableVisible = true
        this.$refs.caseTable.pageLoad(this.intfInfo)
      }
    },
    // 子组件触发父组件更新
    updateData() {
      this.refreshSubtree()
    },
    refreshSubtree() {
      this.getCompanySubtree(this.baseForm.companyId).then(res => {
        this.nodeKeys = []
        this.nodeKeys.push(this.nodeKey)
      })
    },
    // 点击新增用例菜单
    handleAddCase() {
      this.intfInfo['addCaseVisible'] = true
      this.$refs.caseTable.pageLoad(this.intfInfo)
    },
    // 显示和隐藏没有接口的工程
    valueSwitch(newValue) {
      if (newValue === '显示全部工程') {
        this.treeData = this.treeData.filter(function(x) {
          return x.children.length !== 0
        })
      } else {
        this.treeData = this.tempTreeData
      }
    },
    // 处理配置公司的弹窗显示
    configCompany() {
      this.companyEditVisible = true
    },
    // 获取公司列表
    getCompanyList() {
      fetchCompanyList({}).then(res => {
        this.companyTableData = res.companyList
        if (res.code === '000') {
          this.baseForm.companyId = res.companyList[0].companyId
          this.getCompanySubtree(this.baseForm.companyId)
          this.getStat(this.baseForm.companyId)
        }
      })
    },
    // 获取接口及用例统计数据
    getStat(id) {
      getStatistics({ companyId: id }).then(res => {
        this.summaryForm = res.data
      })
    },
    // 添加公司
    addCompany() {
      this.editCompanyIdx = -1
      this.companyFormShow = true
      this.baseForm.companyName = ''
      this.baseForm.desc = ''
    },
    // 处理删除公司
    handleDeleteCompany(index, row) {
      this.delCompanyVisible = true
      this.baseForm.companyId = row.companyId
    },
    // 确认删除公司
    deleteCompany() {
      deleteCompany({ companyId: this.baseForm.companyId }).then(res => {
        this.$message.success(res.desc)
        if (res.code === '000') {
          this.getCompanyList()
        }
      })
      this.delCompanyVisible = false
    },
    // 确认删除工程
    deleteApiSystem() {
      deleteApiSystem({ systemId: this.projectEditForm.projectId }).then(res => {
        this.$message.success(res.desc)
        if (res.code === '000') {
          this.getCompanySubtree(this.baseForm.companyId) // 请求subtree
        }
      })
      this.delProjectVisible = false
    },
    // 确认删除接口
    deleteApi() {
      deleteApi({ intfId: this.apiEditForm.apiId }).then(res => {
        this.$message.success(res.desc)
        if (res.code === '000') {
          this.refreshSubtree()
        }
      })
      this.delApiVisible = false
    },
    // 处理编辑公司
    handleEditCompany(index, row) {
      this.editCompanyIdx = 1
      this.companyFormShow = true
      this.baseForm.companyName = this.companyTableData[index].companyName
      this.baseForm.companyId = this.companyTableData[index].companyId
      this.baseForm.desc = this.companyTableData[index].simpleDesc
    },
    // 保存新增或编辑公司
    saveCompany() {
      if (this.editCompanyIdx === -1) {
        addCompany({ companyName: this.baseForm.companyName }).then(res => {
          this.$message.success(res.desc)
          if (res.code === '000') {
            this.getCompanyList()
          }
        })
      } else if (this.editCompanyIdx === 1) {
        editCompany({
          companyName: this.baseForm.companyName,
          companyId: this.baseForm.companyId,
          simpleDesc: this.baseForm.desc
        }).then(res => {
          this.$message.success(res.desc)
          if (res.code === '000') {
            this.getCompanyList()
          }
        })
      }
      this.companyFormShow = false
    },
    // 搜索公司下的工程以及用例树
    search(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          this.$nextTick(function() {
            this.$refs.caseTable.pageLoad({ interfacePropShow: false })
          })
          this.searchLoading = true
          this.treeData = []
          this.getCompanySubtree(this.baseForm.companyId).then(res => {
            this.searchLoading = false
          })
          this.getStat(this.baseForm.companyId)
        }
      })
    },
    // 获取公司下工程用例树
    getCompanySubtree(id) {
      return new Promise((resolve, reject) => {
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
          this.tempTreeData = res.data.sort(compare('label'))
          this.treeData = this.tempTreeData.filter(function(x) {
            return x.children.length !== 0
          })
          this.apiEditForm.intfRelationOption = this.tempTreeData.filter(function(x) {
            return x.children.length !== 0
          })
          this.apiEditForm.intfRelationOption.forEach(item => {
            item['treeId'] = item['systemId']
            item.children.forEach(element => {
              element['treeId'] = element['intfId']
            })
          })
          /* this.summaryForm.systemTotalNum = this.treeData.length
            this.summaryForm.intfTotalNum = num
            this.summaryForm.intfHttpNum = 0
            this.summaryForm.intfDubboNum = 0
            this.summaryForm.intfMqNum = 0
            this.treeData.forEach((item) => {
                item.children.forEach((subItem) => {
                    if (new RegExp("^\/.*$").test(subItem.label) || new RegExp("^http.*$").test(subItem.label)) {
                        this.summaryForm.intfHttpNum += 1
                    } else if (new RegExp("^cn.*$").test(subItem.label)) {
                        this.summaryForm.intfDubboNum += 1
                    } else {
                        this.summaryForm.intfMqNum += 1
                    }
                })
            })*/
          resolve(1)
        })
      })
    },
    // 保存工程编辑
    saveProjectEdit(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          if (this.editApiSystemIdx === -1) {
            editApiSystem({
              systemId: this.projectEditForm.projectId,
              systemName: this.projectEditForm.projectName,
              gitSshURL: this.projectEditForm.gitSshURL,
              simpleDesc: this.projectEditForm.desc
            }).then(res => {
              this.$message.success(res.desc)
              this.getCompanySubtree(this.baseForm.companyId) // 请求subtree
            })
          } else if (this.editApiSystemIdx === 1) {
            addApiSystem({
              companyId: this.baseForm.companyId,
              systemName: this.projectEditForm.projectName,
              gitSshURL: this.projectEditForm.gitSshURL,
              simpleDesc: this.projectEditForm.desc
            }).then(res => {
              this.$message.success(res.desc)
              this.getCompanySubtree(this.baseForm.companyId) // 请求subtree
            })
          }
          this.projectEditVisible = false
        }
      })
    },
    // 保存接口编辑
    saveApiEdit() {
      const newArr = []
      const _self = this

      function checkForm(arrName) {
        // 动态生成promise，再对其表单校验，都通过了再去做处理
        var result = new Promise(function(resolve, reject) {
          _self.$refs[arrName].validate(valid => {
            if (valid) {
              resolve()
            } else {
              reject(arrName + ' is not valid')
            }
          })
        })
        newArr.push(result) // push 得到promise的结果
      }

      checkForm('apiEditForm')
      checkForm('apiParamsForm')

      Promise.all(newArr)
        .then(function() {
          // 都通过了
          console.log('校验成功')
          _self.submit()
        })
        .catch(function(err) {
          console.error(err)
        })
    },
    submit() {
      let info = ''
      if (this.apiEditForm.interfaceType === 'HTTP') {
        info = JSON.stringify({
          apiUrl: this.apiEditForm.apiUrl,
          headers: this.apiEditForm.headers,
          method: this.apiEditForm.method
        })
      } else if (this.apiEditForm.interfaceType === 'DUBBO') {
        info = JSON.stringify({
          dubboService: this.apiEditForm.dubboService,
          dubboMethod: this.apiEditForm.dubboMethod,
          parameterTypes: this.apiEditForm.parameterTypes,
          version: this.apiEditForm.version
        })
      } else if (this.apiEditForm.interfaceType === 'MQ') {
        // 区分使用的是升级后的mq还是旧的
        if (!this.apiEditForm.isAppId) {
          info = JSON.stringify({ topic: this.apiEditForm.topic, tag: this.apiEditForm.tag })
        } else {
          info = JSON.stringify({
            topic: this.apiEditForm.topic,
            tag: this.apiEditForm.tag,
            appId: this.apiEditForm.appId
          })
        }
      }
      if (this.editApiIdx === 1) {
        addApi({
          systemId: this.projectEditForm.projectId,
          intfNameInChinese: this.apiEditForm.apiNameInChinese,
          type: this.apiEditForm.interfaceType,
          info: JSON.parse(info),
          request: JSON.parse(this.apiParamsForm.apiParams),
          requestDetail: this.apiParamsForm.apiParamsTableData,
          intfRelation: this.apiEditForm.intfRelation
        }).then(res => {
          this.$message.success(res.desc)
          this.editApiVisible = false
          this.refreshSubtree()
        })
      } else if (this.editApiIdx === -1) {
        editApi({
          intfId: this.apiEditForm.apiId,
          intfNameInChinese: this.apiEditForm.apiNameInChinese,
          type: this.apiEditForm.interfaceType,
          info: JSON.parse(info),
          request: JSON.parse(this.apiParamsForm.apiParams),
          requestDetail: this.apiParamsForm.apiParamsTableData,
          intfRelation: this.apiEditForm.intfRelation
        }).then(res => {
          this.$message.success(res.desc)
          this.editApiVisible = false
          this.refreshSubtree()
        })
      }
    },
    // 处理新增公司弹窗
    handleAddProject() {
      this.projectEditVisible = true
      this.$refs['projectEditForm'].clearValidate()
      this.editApiSystemIdx = 1
      this.projectEditForm.projectName = ''
      this.projectEditForm.gitSshURL = ''
    },
    filterNode(value, data) {
      if (!value) return true
      return data.label.indexOf(value) !== -1
    },
    // 处理编辑工程
    handEditProject() {
      this.projectEditVisible = true
      this.$refs['projectEditForm'].clearValidate()
      this.editApiSystemIdx = -1
    },
    // 处理删除工程
    handDeleteProject() {
      this.delProjectVisible = true
    },
    // 处理删除接口
    handDeleteApi() {
      this.delApiVisible = true
    },
    // 处理新增接口
    handAddApi() {
      this.editApiIdx = 1
      this.editApiVisible = true
      this.apiParamsForm.apiParams = ''
      this.apiParamsForm.apiParamsTableData = []
      this.apiParamsForm.butLabel = '格式化入参'
      this.apiParamsForm.butFlag = true
      const interfaceAddForm = {
        apiNameInChinese: '',
        interfaceType: '',
        apiId: '',
        interfaceTypeOptions: ['HTTP', 'DUBBO', 'MQ'],
        methodOptions: ['POST', 'GET'],
        apiUrl: '',
        headers: '{"Content-Type":"application/json"}',
        method: '',
        dubboService: '',
        dubboMethod: '',
        parameterTypes: '',
        version: '',
        topic: '',
        tag: '',
        isAppId: false,
        appId: '',
        intfRelation: []
      }
      for (var obj in interfaceAddForm) {
        this.apiEditForm[obj] = interfaceAddForm[obj]
      }
    },
    // 处理编辑接口
    handEditApi() {
      this.editApiVisible = true
      this.$nextTick(() => {
        this.resetForm('apiParamsForm')
        this.resetForm('apiEditForm')
      })
      this.editApiIdx = -1
      this.apiParamsForm.apiParams = ''
      this.apiParamsForm.apiParamsTableData = []
      this.apiParamsForm.butLabel = '格式化入参'
      this.apiParamsForm.butFlag = true
      queryApiDetail({ intfId: this.apiEditForm.apiId }).then(res => {
        this.apiEditForm.interfaceType = res.data.type
        this.apiEditForm.interfaceTypeOptions = [res.data.type]
        this.apiEditForm.apiNameInChinese = res.data.intfChineseName
        const info = res.data.info
        for (let obj in info) {
          this.apiEditForm[obj] = info[obj]
        }
        if ('appId' in info) {
          this.apiEditForm.isAppId = true
        } else {
          this.apiEditForm.isAppId = false
          this.apiEditForm.appId = ''
        }
        this.apiParamsForm.apiParams = JSON.stringify(res.data.request)
        this.apiParamsForm.apiParamsTableData = res.data.requestDetail
        this.apiEditForm.intfRelation = res.data.intfRelation
      })
    },
    // 说明
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
    // 解析入参并回填到接口入参列表中
    parseIntfParms() {
      this.$refs['apiParamsForm'].validate(valid => {
        if (valid) {
          let data = JSON.parse(this.apiParamsForm.apiParams)
          if (this.apiParamsForm.apiParamsTableData.length === 0) {
            let id = 1
            for (let key in data) {
              this.parseData(key, data[key], this.apiParamsForm.apiParamsTableData, id)
              id = id + 1
            }
          } else {
            let id = 1
            let tempData = []
            for (let key in data) {
              this.parseData(key, data[key], tempData, id)
              id = id + 1
            }
            this.mergeLogic(tempData, this.apiParamsForm.apiParamsTableData)
            this.apiParamsForm.apiParamsTableData = tempData
          }
          console.log('传递给接口的接口入参列表数据', JSON.stringify(this.apiParamsForm.apiParamsTableData))
        }
      })
    },
    // 重复解析时进行merge处理
    mergeLogic(oriObj, desObj) {
      oriObj.forEach(i => {
        desObj.forEach(j => {
          if (i.paramName === j.paramName) {
            i.paramRule = j.paramRule
            i.isRequired = j.isRequired
            if (i.hasOwnProperty('children') && j.hasOwnProperty('children')) {
              this.mergeLogic(i.children, j.children)
            }
          }
        })
      })
    },
    // 解析入参函数
    parseData(key, val, ret, index) {
      if (val instanceof Array && val !== null) {
        let temp1 = {}
        temp1['id'] = index
        temp1['paramName'] = key
        temp1['paramType'] = 'array'
        temp1['isRequired'] = false
        temp1['children'] = []
        let idx = index * 100 + 1
        for (let i in val) {
          this.parseData(i, val[i], temp1['children'], idx)
          idx = idx + 1
        }
        ret.push(temp1)
      } else if (val instanceof Object && val !== null) {
        let temp2 = {}
        temp2['id'] = index
        temp2['paramName'] = key
        temp2['paramType'] = 'object'
        temp2['isRequired'] = false
        temp2['children'] = []
        let idx = index * 100 + 1
        for (let i in val) {
          this.parseData(i, val[i], temp2['children'], idx)
          idx = idx + 1
        }
        ret.push(temp2)
      } else if (typeof val === 'string' || typeof val === 'number' || typeof val === 'boolean' || val === null) {
        let temp3 = {}
        temp3['id'] = index
        temp3['paramName'] = key
        temp3['paramType'] = typeof val
        temp3['paramRule'] = ''
        temp3['paramDefVal'] = String(val)
        temp3['isRequired'] = false
        ret.push(temp3)
      }
    },
    // 入参列表中点击编辑按钮触发入参规则编辑弹框
    handEditApiParams(index, row) {
      this.apiParamsRuleForm.editApiParamsRuleVisible = true
      this.resetForm('apiParamsRuleForm')
      this.apiParamsRuleForm.apiParamsName = row.paramName
      this.apiParamsRuleForm.apiParamsType = row.paramType
      this.apiParamsRuleForm.idx = row.id
    },
    // 入参规则编辑弹框点击确定按钮触发
    saveApiParamsRuleEdit(form) {
      this.$refs[form].validate(valid => {
        if (valid) {
          this.saveLogic(this.apiParamsForm.apiParamsTableData)
          this.apiParamsRuleForm.editApiParamsRuleVisible = false
        }
      })
    },
    // 编辑保存具体的函数
    saveLogic(obj) {
      obj.forEach(i => {
        if (i.id === this.apiParamsRuleForm.idx) {
          i.paramRule =
            this.apiParamsRuleForm.apiParamsRuleTypeOptions.find(c => c.value === this.apiParamsRuleForm.apiParamsRuleType).label +
            '=' +
            this.apiParamsRuleForm.apiParamsRuleVal
        } else if (i.hasOwnProperty('children')) {
          this.saveLogic(i.children)
        }
      })
    },
    // 重置表单
    resetForm(formName) {
      if (this.$refs[formName] !== undefined) {
        this.$refs[formName].resetFields()
      }
    },
    // 格式化入参函数
    formatIntfParms() {
      this.$refs['apiParamsForm'].validate(valid => {
        if (valid) {
          if (this.apiParamsForm.butFlag) {
            this.apiParamsForm.apiParams = JSON.stringify(JSON.parse(this.apiParamsForm.apiParams), null, 4)
            this.apiParamsForm.butLabel = '还原入参'
          } else {
            this.apiParamsForm.apiParams = JSON.stringify(JSON.parse(this.apiParamsForm.apiParams), null, 0)
            this.apiParamsForm.butLabel = '格式化入参'
          }
          this.apiParamsForm.butFlag = !this.apiParamsForm.butFlag
        }
      })
    },
    // 导出用例
    handExportCase() {
      exportTestCase({ systemId: this.projectEditForm.projectId }).then(res => {
        this.downloadXmindTempUrl = '/atp/download/' + res.desc
        this.exportVisible = true
      })
    },
    // 导出弹框
    exported() {
      this.exportVisible = false
    }
  }
}
</script>

<style lang="scss">
.example-resintf {
  padding: 10px;
  height: 100%;
  min-height: 700px;
  max-height: 700px;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.1);
}

.table_container {
  padding: 10px;
}

.demo-table-expand .el-form-item {
  margin-right: 0;
  margin-bottom: 0;
  width: 50%;
}

.navigation-filter {
  padding: 5px 10px;
}

.resIntfScrolllist {
  max-height: 680px;
}

.apiEditDialog .el-dialog__body {
  padding: 10px 20px;
  .el-collapse-item__header {
    height: 40px;
    line-height: 40px;
    color: #2949ca;
    cursor: pointer;
    border-bottom: 1px solid #ebeef5;
    font-size: 15px;
    font-weight: 600;
    background-color: #e4e7ed;
    .el-collapse-item__arrow {
      line-height: 40px;
    }
  }
  .el-collapse-item__content {
    margin-top: 10px;
    padding-bottom: 0;
  }
}

/*页面输入框样式*/
.apiEditForm .el-input,
.apiEditForm .el-textarea {
  width: 80%;
}

.apiEditForm .el-select .el-input {
  width: 100%;
}

.apiParamsForm .el-input,
.apiParamsForm .el-textarea {
  width: 80%;
}

.apiParamsForm .el-select .el-input {
  width: 100%;
}

.intf-radius {
  height: 30px;
  width: 60%;
  border: 1px solid #d7dae2;
  border-radius: 4px;
  margin-bottom: 10px;
  .text {
    color: #606266;
  }
}

.resIntfList {
  margin-bottom: 20px;
}
</style>
