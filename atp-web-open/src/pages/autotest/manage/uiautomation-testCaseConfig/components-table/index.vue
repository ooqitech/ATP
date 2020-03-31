<template>
  <div class="fillcontain">
    <el-form v-show="caseFormShow" size="mini">
      <el-form inline class="demo-table-expand" style="width: 100%">
        <el-form-item label="系统类型：" style="width: 50%">
          <span>{{systemType}}</span>
        </el-form-item>
        <el-form-item label="URL/包名：" style="width: 50%">
          <span>{{systemUrl}}</span>
        </el-form-item>
        <el-form-item style="float: left;margin-top: 10px;margin-bottom: 10px">
          <el-button type="primary" icon="el-icon-edit" @click="handAddUiCase" size="mini">新增测试用例</el-button>
        </el-form-item>
        <el-form-item style="float: right;margin-top: 10px;margin-bottom: 10px" v-if="systemType==='web'">
          <el-switch
            v-model="switchValue"
            active-color="#ff4949"
            inactive-color="#13ce66"
            active-text="本地浏览器启动"
            inactive-text="服务器上启动"
            @change="switchRunEnv()"
          ></el-switch>
        </el-form-item>
      </el-form>
      <el-table
        :data="tableData"
        border
        style="width: 100%;margin-top: 30px"
        ref="multipleTable"
        :header-cell-style="{color:'black',background:'#eef1f6'}"
        @selection-change="handleSelectionChange"
        v-loading="loadingVisible"
        element-loading-text="正在执行用例"
        element-loading-spinner="el-icon-loading"
        element-loading-background="rgba(0, 0, 0, 0.8)"
      >
        <el-table-column type="selection" width="80"></el-table-column>
        <el-table-column prop="id" label="用例编号" width="100"></el-table-column>
        <el-table-column prop="testcase_name" label="用例标题" width="auto"></el-table-column>
        <el-table-column prop="test_type" label="用例类型" width="100"></el-table-column>

        <el-table-column label="操作" fixed="right" width="260">
          <template slot-scope="scope">
            <el-button size="mini" type="primary" icon="el-icon-edit" @click="handleEditCase(scope.$index, scope.row)" plain></el-button>
            <el-button size="mini" style="margin-left: 10px" type="danger" icon="el-icon-delete" @click="handleDelete(scope.$index, scope.row)" plain></el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination" style="margin-top: 5px">
        <el-pagination
          @current-change="handleCurrentChange"
          @size-change="handleSizeChange"
          layout="total, sizes, prev, pager, next, jumper"
          :total="totalCount"
          :current-page="currentPage"
          :page-sizes="[10, 20, 30, 40]"
          :page-size="pagesize"
        ></el-pagination>
      </div>
      <div style="text-align: center; margin-top: 20px">
        <el-button style="float: inherit" size="small" type="primary" icon="el-icon-caret-right" v-show="runCaseVisible" @click="RunCase()">执行用例</el-button>
        <a class="reporturl" :href="reportUrl" target="view_window" style="margin-left: 30px" v-if="reportUrlVisible">
          <el-button size="small" round type="primary">查看报告</el-button>
        </a>
      </div>
    </el-form>
    <!--用例详情编辑弹窗-->
    <el-dialog
      title="配置测试用例"
      :visible.sync="caseEditVisible"
      width="50%"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      ref="caseEditDialog"
      class="caseEditDialog"
    >
      <el-collapse v-model="activeNames">
        <!--基本信息-->
        <el-collapse-item title="基本信息" name="1">
          <el-form ref="caseBasicForm" :model="caseBasicForm" label-width="120px">
            <el-form-item label="用例标题" prop="caseName" :rules="[{ required: true, message: '用例标题必填', trigger: 'blur' }]">
              <el-input style="width: 80%" v-model="caseBasicForm.caseName" placeholder="请输入用例标题"></el-input>
            </el-form-item>
            <el-form-item label="用例描述" prop="caseDesc" :rules="[{ required: true, message: '用例描述必填', trigger: 'blur' }]">
              <el-input type="textarea" autosize style="width: 80%" v-model="caseBasicForm.caseDesc" placeholder="请输入用例描述"></el-input>
            </el-form-item>
          </el-form>
        </el-collapse-item>
        <!--前置操作-->
        <el-collapse-item v-show="tabVisible[0].value" name="2">
          <template slot="title">
            <span>前置操作</span>
            <el-tooltip placement="top" content="添加" effect="light">
              <el-button type="primary" size="mini" style="margin-left: 20px" icon="el-icon-plus" @click.stop="addSetup()" plain></el-button>
            </el-tooltip>
          </template>
          <el-card class="box-card" v-for="(item, index) in makeSetupData" :key="item.index" v-if="item.formShow">
            <div slot="header">
              <span>{{item.formName}}-{{index + 1}}</span>
            </div>
            <el-form :ref="item.formRef" :model="item.formModel" inline width="auto">
              <el-form-item label="前置操作" prop="setupType" :rules="[{required: true, message: '保存变量不能为空', trigger: 'blur'}]" width="auto">
                <el-select v-model="item.formModel.setupType" placeholder="请选择操作类型" style="width: auto">
                  <el-option label="前置用例" value="setupcase"></el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="用例id" prop="caseId" width="auto">
                <el-input type="text" autosize style="width: 50%" v-model="item.formModel.caseId"></el-input>
                <el-tooltip placement="top" content="移除" effect="light">
                  <el-button type="info" size="mini" style="margin-left: 20px" icon="el-icon-minus" @click.prevent="removeStepUps(item)" plain></el-button>
                </el-tooltip>
              </el-form-item>
            </el-form>
          </el-card>
        </el-collapse-item>
        <!--操作步骤-->
        <el-collapse-item v-show="tabVisible[0].value" name="3">
          <template slot="title">
            <span>操作步骤</span>
            <el-tooltip placement="top" content="添加" effect="light">
              <el-button type="primary" size="mini" style="margin-left: 20px" icon="el-icon-plus" @click.stop="addSteps()" plain></el-button>
            </el-tooltip>
          </template>
          <el-card class="box-card" v-for="(item, index) in makeStepsData" :key="item.index" v-if="item.formShow">
            <div slot="header">
              <span>{{item.formName}}-{{index + 1}}</span>
              <el-tooltip placement="top" content="移除" effect="light">
                <el-button type="info" size="mini" style="margin-left: 20px" icon="el-icon-minus" @click.prevent="removeSteps(item)" plain></el-button>
              </el-tooltip>
              <el-tooltip placement="top" content="保存" effect="light">
                <el-button type="info" size="mini" style="margin-left: 20px" icon="el-icon-circle-check" @click.prevent="saveSteps(item)" plain>保存</el-button>
              </el-tooltip>
            </div>
            <el-form :ref="item.formRef" :model="item.formModel" inline width="auto">
              <el-form-item label="操作方式" prop="operation" :rules="[{required: true, message: '保存变量不能为空', trigger: 'blur'}]" width="auto">
                <el-select v-model="item.formModel.operation" placeholder="请选择操作类型" @change="chooseOperation(item.formModel.operation)" style="width: auto">
                  <el-option label="点击元素" value="click"></el-option>
                  <el-option label="输入" value="input"></el-option>
                  <el-option label="切换frame" value="switchFrame"></el-option>
                  <el-option label="鼠标移动至元素上" value="move"></el-option>
                  <el-option label="执行js" value="js"></el-option>
                  <el-option label="执行接口用例" value="runApiCase"></el-option>
                  <el-option label="扫描二维码" value="ScanQRcode"></el-option>
                  <el-option label="点击通用文本元素" value="clickCommonEle"></el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="页面" prop="pageId" width="auto" v-show="options.selectEleVisible">
                <el-select v-model="item.formModel.pageId" @change="chooseObject(item.formModel.pageId)">
                  <el-option v-for="pageitem in pageOptions" :key="pageitem.pageName" :label="pageitem.pageName" :value="pageitem.id"></el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="元素" prop="element" width="auto" v-show="options.selectEleVisible">
                <el-select v-model="item.formModel.element">
                  <el-option
                    v-for="objectitem in pageObjectOptions"
                    :key="objectitem.object_name"
                    :label="objectitem.object_name"
                    :value="objectitem.object_name"
                  ></el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="输入值" prop="value" width="auto" v-show="options.sendKeysVisible">
                <el-input type="text" autosize style="width: 50%" v-model="item.formModel.value"></el-input>
              </el-form-item>
              <!--上传文件-->
              <el-form-item label="上传图片列表" v-if="options.uploadVisible" prop="value" :rules="[{ required: true, message: '请上传一个文件', trigger: 'blur' }]">
                <el-upload
                  class="upload-demo"
                  :action="importFileUrl"
                  name="file"
                  :on-preview="handlePreview"
                  :on-remove="handleRemove"
                  :on-success="handSuccess"
                  list-type="picture"
                  :file-list="options.filelist"
                >
                  <el-button size="small" type="primary">点击上传</el-button>
                </el-upload>
              </el-form-item>
              <!--上传文件-->
            </el-form>
          </el-card>
        </el-collapse-item>
        <!--预期结果-->
        <el-collapse-item v-show="tabVisible[0].value" name="4">
          <template slot="title">
            <span>预期结果</span>
            <el-tooltip placement="top" content="添加" effect="light">
              <el-button type="primary" size="mini" style="margin-left: 20px" icon="el-icon-plus" @click.stop="addExpectResult()" plain></el-button>
            </el-tooltip>
          </template>
          <el-card class="box-card" v-for="(item, index) in makeExpectResultData" :key="item.index" v-if="item.formShow">
            <div slot="header">
              <span>{{item.formName}}-{{index + 1}}</span>
            </div>
            <el-form :ref="item.formRef" :model="item.formModel" inline width="auto">
              <el-form-item label="页面" prop="pageId" width="auto">
                <el-select v-model="item.formModel.pageId" @change="chooseObject(item.formModel.pageId)">
                  <el-option v-for="pageitem in pageOptions" :key="pageitem.pageName" :label="pageitem.pageName" :value="pageitem.id"></el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="元素" prop="element" width="auto">
                <el-select v-model="item.formModel.element">
                  <el-option
                    v-for="objectitem in pageObjectOptions"
                    :key="objectitem.object_name"
                    :label="objectitem.object_name"
                    :value="objectitem.object_name"
                  ></el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="元素在页面可见次数" prop="expected" width="auto">
                <el-input type="text" autosize style="width: 50%" v-model="item.formModel.expected"></el-input>
                <el-tooltip placement="top" content="移除" effect="light">
                  <el-button type="info" size="mini" style="margin-left: 20px" icon="el-icon-minus" @click.prevent="removeExpectResult(item)" plain></el-button>
                </el-tooltip>
                <el-tooltip placement="top" content="保存" effect="light">
                  <el-button type="info" size="mini" style="margin-left: 20px" icon="el-icon-circle-check" @click.prevent="saveExpectResult(item)" plain>保存</el-button>
                </el-tooltip>
              </el-form-item>
            </el-form>
          </el-card>
        </el-collapse-item>
      </el-collapse>
      <!--详情以表格展示-->
      <el-table :data="makeStepsData" border style="width: 100%" ref="multipleTable" :header-cell-style="{color:'black',background:'#eef1f6'}">
        <el-table-column prop="formModel.stepsNo" label="操作步骤" width="70"></el-table-column>
        <el-table-column prop="formModel.operation" label="操作方式" width="130"></el-table-column>
        <el-table-column prop="formModel.element" label="元素名称" width="130"></el-table-column>
        <el-table-column prop="formModel.pageName" label="页面名称" width="130"></el-table-column>
        <el-table-column prop="formModel.value" label="输入值" width="auto"></el-table-column>
        <el-table-column label="操作" fixed="right" width="240">
          <template slot-scope="scope">
            <el-button size="mini" type="primary" icon="el-icon-edit" @click="editSteps(scope.$index, scope.row)" plain></el-button>
            <el-button size="mini" style="margin-left: 10px" type="danger" icon="el-icon-delete" @click="deleteSteps(scope.$index, scope.row)" plain></el-button>
            <el-button size="mini" style="margin-left: 10px" type="primary" icon="el-icon-arrow-up" @click="moveUpStep(scope.$index, scope.row)" plain></el-button>
            <el-button size="mini" style="margin-left: 10px" type="primary" icon="el-icon-arrow-down" @click="moveDownStep(scope.$index, scope.row)" plain></el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-table
        :data="makeExpectResultData"
        border
        style="width: 100%;margin-top: 5px"
        ref="multipleTable"
        :header-cell-style="{color:'black',background:'#eef1f6'}"
      >
        <el-table-column prop="formModel.stepsNo" label="预期结果" width="80"></el-table-column>
        <el-table-column prop="formModel.element" label="元素名称" width="auto"></el-table-column>
        <el-table-column prop="formModel.pageName" label="页面名称" width="auto"></el-table-column>
        <el-table-column prop="formModel.expected" label="元素预期出现次数" width="auto"></el-table-column>
        <el-table-column label="操作" fixed="right" width="160">
          <template slot-scope="scope">
            <el-button size="mini" type="primary" icon="el-icon-edit" @click="editSteps(scope.$index, scope.row)" plain></el-button>
            <el-button size="mini" style="margin-left: 10px" type="danger" icon="el-icon-delete" @click="removeExpectResult(scope.$index, scope.row)" plain></el-button>
          </template>
        </el-table-column>
      </el-table>
      <span slot="footer" class="dialog-footer">
        <el-button @click="caseEditVisible = false">取 消</el-button>
        <el-button size="mini" type="primary" @click="saveCaseEdit('caseEditForm')">保存</el-button>
      </span>
    </el-dialog>
    <!-- 删除提示框 -->
    <el-dialog title="提示" :visible.sync="delVisible" width="300px" center>
      <div class="del-dialog-cnt">删除不可恢复，是否确定删除？</div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="delVisible = false">取 消</el-button>
        <el-button type="danger" icon="el-icon-warning" @click="deleteCase">删 除</el-button>
      </span>
    </el-dialog>
    <!-- mobile选择测试机弹窗 -->
    <el-dialog title="选择运行的手机" :visible.sync="runEnvVisible" width="300px" center>
      <el-select v-model="mobileRemoteUrl" placeholder="请选择测试机">
        <el-option key="99.48.92.139:7912" label="VIVO" value="99.48.92.139:7912"></el-option>
      </el-select>
      <span slot="footer" class="dialog-footer">
        <el-button @click="runEnvVisible = false">取 消</el-button>
        <el-button type="primary" @click="runMobileTestCase">确 定</el-button>
      </span>
    </el-dialog>
    <!-- 本地浏览器运行操作提示 -->
    <el-dialog title="配置本地浏览器启动环境(推荐再服务器运行)" :visible.sync="congifBrowser" width="30%">
      <strong>
        <span style="text-align: center">如果是第一次启动本地，请按照步骤操作</span>
      </strong>
      <span style="display:block">1.电脑已安装谷歌浏览器，已有jdk环境，</span>
      <span>
        2.下载配置文件，将其保存解压到C盘
        <strong>根目录</strong>
      </span>
      <a :href="downloadConfigDocs">
        <el-button type="primary">下载配置文件</el-button>
      </a>
      <span style="display:block">3.运行里面的；run.bat文件</span>
      <strong>
        <span>下次再启动可以跳过第1,2步骤，直接运行C盘里的run.bat文件即可</span>
      </strong>
      <span slot="footer" class="dialog-footer">
        <el-button type="primary" @click="congifBrowser = false">确 定</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { mapState, mapMutations } from 'vuex'
import {
  queryUiCaseListByModuleId,
  detailUiTestCase,
  addUiTestCase,
  editUiTestCase,
  deleteUiTestCase
} from '@/api/autotest/manage/testcase-testCaseConfig/testcase'
import { runUiCase } from '@/api/autotest/manage/testcase-run'
import { fetchPageList, fetchPageElements } from '@/api/autotest/manage/testcase-testCaseConfig/pageobject'

export default {
  name: 'index',
  data() {
    return {
      caseBasicForm: {
        testcaseId: '',
        caseName: '',
        caseDesc: ''
      },
      systemUrl: '',
      systemType: '',
      mobileRemoteUrl: '',
      reportUrl: '',
      selectedItem: [],
      idx: -1,
      testcaseId: '',
      baseForm: '',
      tableData: [],
      caseEditVisible: false,
      currentPage: 1,
      totalCount: 100,
      pagesize: 100,
      caseFormShow: false,
      searchKeywords: '',
      activeNames: ['1'],
      tabVisible: [{ label: 'steps', displayName: '操作步骤', value: true }],
      makeSetupData: [],
      makeStepsData: [],
      makeVariableData: [],
      makeExpectResultData: [],
      caseInfo: {},
      multipleSelection: [],
      testcaseList: [],
      reportUrlVisible: false,
      runCaseVisible: true,
      runEnvVisible: false,
      inx: -1,
      delVisible: false,
      pageObjectOptions: [],
      pageOptions: [],
      loadingVisible: false,
      resData: '',
      importFileUrl: '/atp/file/upload',
      downloadConfigDocs: '/atp/download/chromeConfig.zip',
      options: {
        uploadVisible: false,
        sendKeysVisible: false,
        selectEleVisible: false,
        filelist: [], // 编辑框中，展示文件后缀名
        uploadList: [], // 上传文件列表的传参
        delList: []
      },
      uploadIdx: '', // 第几个操作步骤为上传二维码
      switchValue: false,
      congifBrowser: false
    }
  },

  computed: {
    ...mapState('d2admin/casetable', ['uiCaseTable', 'addUiCaseVisible', 'uiRunEnvForm'])
  },
  methods: {
    ...mapMutations({
      addUiCase: 'd2admin/casetable/addUiCase'
    }),
    // 切换运行环境，本地，服务器headless
    switchRunEnv() {
      if (this.switchValue === true) {
        this.congifBrowser = true
      } else {
        this.congifBrowser = false
      }
    },
    // 选择页面元素
    chooseObject(id) {
      fetchPageElements({
        pageId: id
      }).then(res => {
        this.pageObjectOptions = res.desc
      })
    },
    // 查询UI测试用例by模块id
    queryTestCases() {
      queryUiCaseListByModuleId({
        moduleId: this.uiCaseTable.moduleId,
        pageNo: this.currentPage,
        pageSize: this.pagesize
      }).then(res => {
        this.tableData = res.desc
        this.systemUrl = res.systemUrl
        this.totalCount = res.totalNum
        this.systemType = res.systemType
      })
    },
    // 获取系统下的所有页面列表
    fetchSystemPageList() {
      fetchPageList({
        systemId: this.uiCaseTable.systemId
      }).then(res => {
        this.pageOptions = res.desc
      })
    },
    // 选择不同的操作方式触发的时间
    chooseOperation(operate) {
      if (operate === 'ScanQRcode') {
        this.options.uploadVisible = true
        this.options.selectEleVisible = false
        this.options.sendKeysVisible = false
      } else if (operate === 'click' || operate === 'move') {
        this.options.uploadVisible = false
        this.options.selectEleVisible = true
        this.options.sendKeysVisible = false
      } else if (operate === 'input') {
        this.options.uploadVisible = false
        this.options.selectEleVisible = true
        this.options.sendKeysVisible = true
      } else if (operate === 'js' || operate === 'runApiCase' || operate === 'switchFrame' || operate === 'clickCommonEle') {
        this.options.uploadVisible = false
        this.options.selectEleVisible = false
        this.options.sendKeysVisible = true
      }
    },

    // 分页导航
    handleCurrentChange(val) {
      this.currentPage = val
      this.queryTestCases()
    },
    handleSizeChange(val) {
      this.pagesize = val
      this.queryTestCases()
    },
    // 添加操作步骤
    addSteps() {
      const index = this.makeStepsData.length
      this.uploadIdx = index
      this.makeStepsData.push({
        key: Date.now(),
        formRef: 'formStepFirst',
        formModel: { value: '', operation: '', element: '', expected: '', stepsNo: index + 1, pageName: '', pageId: '', uploadUrl: [] },
        formShow: true,
        formName: '操作步骤'
      })
    },
    // 添加前置操作
    addSetup() {
      const index = this.makeSetupData.length
      this.makeSetupData.push({
        key: Date.now(),
        formRef: 'formSetUpFirst',
        formModel: { setupType: '', caseId: '' },
        formShow: true,
        formName: '前置操作'
      })
    },
    // 添加预期结果
    addExpectResult() {
      const index = this.makeExpectResultData.length
      this.makeExpectResultData.push({
        key: Date.now(),
        formRef: 'formExpecFirst',
        formModel: {
          element: '',
          expected: '',
          stepsNo: index + 1,
          pageName: '',
          pageId: ''
        },
        formShow: true,
        formName: '预期结果'
      })
    },
    saveCaseEdit() {
      this.caseEditVisible = false
      const requestBody = {}
      const baseInfo = {}
      const setupInfo = []
      const include = ''
      const validateInfo = []
      const variableInfo = []
      const steps = []
      // 基础信息
      baseInfo['systemId'] = this.uiCaseTable.systemId
      baseInfo['moduleId'] = this.uiCaseTable.moduleId
      baseInfo['testcaseName'] = this.caseBasicForm.caseName
      baseInfo['testcaseDesc'] = this.caseBasicForm.caseDesc
      baseInfo['id'] = this.testcaseId
      // 前置操作
      this.makeSetupData.forEach(item => {
        const setup = {}
        setup['setup_type'] = item.formModel.setupType
        setup['setup_args'] = item.formModel.caseId
        setupInfo.push(setup)
      })

      // 操作步骤
      this.makeStepsData.forEach(item => {
        const step = {}
        step['page_id'] = item.formModel.pageId
        step['page_name'] = item.formModel.pageName
        step['element'] = item.formModel.element
        step['action'] = item.formModel.operation
        step['send_value'] = item.formModel.value
        step['validates'] = item.formModel.expected
        steps.push(step)
      })
      // 用例级预期结果
      this.makeExpectResultData.forEach(item => {
        const expectResult = {}
        expectResult['page_id'] = item.formModel.pageId
        expectResult['page_name'] = item.formModel.pageName
        expectResult['element'] = item.formModel.element
        expectResult['times'] = item.formModel.expected
        validateInfo.push(expectResult)
      })
      requestBody['base'] = baseInfo
      requestBody['steps'] = steps
      requestBody['setupInfo'] = setupInfo
      requestBody['include'] = include
      requestBody['validateInfo'] = validateInfo
      requestBody['variableInfo'] = variableInfo
      if (this.idx === -1) {
        addUiTestCase(requestBody).then(res => {
          this.$message.success(res.desc)
        })
      } else {
        editUiTestCase(requestBody).then(res => {
          this.$message.success(res.desc)
        })
      }
      this.caseEditVisible = false
      this.queryTestCases()
    },
    // 移除操作步骤
    removeSteps(item) {
      const index = this.makeStepsData.indexOf(item)
      if (index !== -1) {
        this.makeStepsData.splice(index, 1)
      }
    },

    // 移除前置步骤
    removeStepUps(item) {
      const index = this.makeSetupData.indexOf(item)
      if (index !== -1) {
        this.makeSetupData.splice(index, 1)
      }
    },
    // 移除预期结果
    removeExpectResult(index, row) {
      if (index !== -1) {
        this.makeExpectResultData.splice(index, 1)
      }
    },
    // 删除操作步骤
    deleteSteps(index, row) {
      if (index !== -1) {
        this.makeStepsData.splice(index, 1)
      }
    },
    // 保存操作步骤
    saveSteps(item) {
      const index = this.makeStepsData.indexOf(item)
      this.makeStepsData[index].formShow = false
    },
    // 操作步骤上移
    moveUpStep(index, row) {
      if (index !== 0) {
        this.makeStepsData[index] = this.makeStepsData.splice(index - 1, 1, this.makeStepsData[index])[0]
      } else {
        this.makeStepsData.push(this.makeStepsData.shift())
      }
      this.$message.success('操作步骤上移成功')
    },
    // 操作步骤下移
    moveDownStep(index, row) {
      if (index !== this.makeStepsData.length - 1) {
        this.makeStepsData[index] = this.makeStepsData.splice(index + 1, 1, this.makeStepsData[index])[0]
      } else {
        this.makeStepsData.unshift(this.makeStepsData.splice(index, 1)[0])
      }
      this.$message.success('操作步骤下移成功')
    },

    // 保存预期结果
    saveExpectResult(item) {
      const index = this.makeExpectResultData.indexOf(item)
      this.makeExpectResultData[index].formShow = false
    },

    // 编辑操作步骤
    editSteps(index, row) {
      this.uploadIdx = index
      const operate = row.formModel.operation
      this.chooseOperation(operate)
      row.formShow = true
    },
    initial() {
      this.makeStepsData = []
      this.makeSetupData = []
      this.makeExpectResultData = []
      this.fetchSystemPageList()
    },
    // 新增测试用例
    handAddUiCase() {
      this.caseEditVisible = true
      this.idx = -1
      this.caseBasicForm.caseName = ''
      this.caseBasicForm.caseDesc = ''
      this.initial()
    },
    // 删除测试用例
    handleDelete(index, row) {
      this.idx = index
      this.testcaseId = row.id
      this.delVisible = true
    },
    // 编辑用例
    handleEditCase(index, row) {
      this.idx = index
      this.testcaseId = row.id
      this.caseEditVisible = true
      this.initial()
      detailUiTestCase({ id: row.id }).then(res => {
        const caseInfo = res.data
        // 基础信息
        this.caseBasicForm.caseDesc = caseInfo.baseInfo.caseDesc
        this.caseBasicForm.caseName = caseInfo.baseInfo.caseName
        // 前置操作
        caseInfo.setupInfo.forEach(item => {
          this.makeSetupData.push({
            key: Date.now(),
            formRef: 'formSetUpFirst',
            formModel: { setupType: item.setup_type, caseId: item.setup_caseid },
            formShow: true,
            formName: '前置操作'
          })
        })

        // 操作步骤
        caseInfo.steps.stepsInfo.forEach(item => {
          this.makeStepsData.push({
            key: Date.now(),
            formRef: 'formStepFirst',
            formModel: {
              stepsNo: item.stepsNo,
              operation: item.operation,
              element: item.element,
              expected: item.expected,
              value: item.value,
              pageOptions: [],
              pageObjectOptions: [],
              pageId: item.pageId,
              pageName: item.pageName
            },
            formShow: false,
            formName: '操作步骤'
          })
        })
        // 预期结果
        caseInfo.validateInfo.forEach(item => {
          this.makeExpectResultData.push({
            key: Date.now(),
            formRef: 'formExpecFirst',
            formModel: {
              element: item.element,
              expected: item.times,
              stepsNo: item.stepsNo,
              pageName: item.page_name,
              pageId: item.page_id
            },
            formShow: false,
            formName: '预期结果'
          })
        })
      })
    },
    // 测试用例列表选择要运行的测试用例
    handleSelectionChange(val) {
      this.multipleSelection = val
      this.testcaseList = []
      this.multipleSelection.forEach(item => {
        this.testcaseList.push(item.id.toString())
      })
    },
    // 删除用例
    // 确定删除
    deleteCase() {
      deleteUiTestCase({
        id: this.testcaseId
      }).then(res => {
        this.$message.success(res.desc)
        this.queryTestCases()
      })
      this.delVisible = false
    },
    // 执行web用例
    runWebTestCase() {
      runUiCase({ testaCases: this.testcaseList, localBrowser: this.switchValue }).then(res => {
        this.resData = res
      })
    },
    // 选择测试机弹窗
    handRunMobile() {
      this.runEnvVisible = true
    },
    // 执行Mobile用例
    runMobileTestCase() {
      this.loadingVisible = true
      runUiCase({ testaCases: this.testcaseList, remoteUrl: this.mobileRemoteUrl }).then(res => {
        this.resData = res
      })
      window.open('http://' + this.mobileRemoteUrl + '/remote', '_blank')
      this.runEnvVisible = false
    },
    // 循环查看用例是否执行成功timeout of 15s
    RunCase() {
      if (this.testcaseList.length > 0) {
        this.runCaseVisible = false
        this.reportUrlVisible = false
        let timesRun = 0
        if (this.systemType === 'mobile') {
          this.handRunMobile()
        } else {
          this.loadingVisible = true
          this.runWebTestCase()
        }
        this.timer = setInterval(() => {
          if (timesRun >= 50) {
            clearInterval(this.timer)
            this.loadingVisible = false
            this.$message.error('运行超过50s，请稍后再刷新')
            return
          }
          if (this.resData.code === '000') {
            this.$message.success(this.resData.desc)
            clearInterval(this.timer)
            this.loadingVisible = false
            this.reportUrlVisible = true
            this.runCaseVisible = true
            this.reportUrl = this.resData.reportUrl
          } else if (this.resData.code === '200') {
            this.$message.error('请检查环境，如需本地浏览器运行，请运行bat文件')
            clearInterval(this.timer)
            this.loadingVisible = false
            this.runCaseVisible = true
          }
          timesRun += 1
        }, 1000)
      } else {
        this.$message.warning('请勾选测试用例')
      }
    },
    // 删除文件触发事件
    handleRemove(file, fileList) {
      this.options.delList = []
      fileList.forEach(file => {
        if (this.options.delList.indexOf(file.name) === -1) {
          this.options.delList.push(file.name)
        }
      })
      this.makeStepsData[this.uploadIdx].formModel.uploadUrl = this.options.delList
    },
    handlePreview(file) {
      console.log('文件列表02', file)
    },
    // 上传成功,忽略文件列表已存在文件
    handSuccess(response, file, fileList) {
      if (this.options.uploadList.indexOf(response.desc) === -1) {
        // this.options.uploadList.push(response.desc)
        this.makeStepsData[this.uploadIdx].formModel.value = response.desc
      }
      // this.makeStepsData[this.uploadIdx].formModel.uploadUrl=this.options.uploadList
    }
  },
  watch: {
    'uiCaseTable.moduleId': function(newValue) {
      if (newValue) {
        this.caseFormShow = true
        this.queryTestCases()
        this.runCaseVisible = true
        this.reportUrlVisible = false
      } else {
        this.caseFormShow = false
      }
    },
    addUiCaseVisible: function(newValue) {
      if (newValue === true) {
        this.handAddUiCase()
        this.addUiCase(false)
      }
    }
  }
}
</script>

<style lang="scss">
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
</style>
