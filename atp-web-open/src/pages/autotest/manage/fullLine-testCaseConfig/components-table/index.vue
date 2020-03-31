<template>
  <div class="fillcontain">
    <el-form :model="produceLineProp" v-show="produceLineProp.show" class="full-line" ref="produceLineProp">
      <el-table
        :data="tableData"
        style="width: 100%;margin-top: 15px"
        ref="multipleTable"
        :row-class-name="tableRowClassName"
        :header-cell-style="{color:'black',background:'#eef1f6'}"
        @selection-change="handleSelectionChange"
        height="630"
        size="medium"
      >
        <el-table-column type="selection" width="55"></el-table-column>
        <el-table-column prop="id" label="用例编号" width="80"></el-table-column>
        <el-table-column prop="testcase_name" label="用例标题" min-width="300">
          <template slot-scope="scope">
            <a href="javascript:void(0)" v-on:click="handleEdit(scope.$index, scope.row)" style="color: #409EFF">{{scope.row.testcase_name}}</a>
          </template>
        </el-table-column>
        <!--<el-table-column prop="expectResult" label="预期结果" width="auto">
        </el-table-column>-->
        <el-table-column label="用例标签" width="150">
          <template slot-scope="scope">
            <el-tag
              :key="tag"
              v-for="tag in tableData[scope.$index].tags_name"
              effect="plain"
              type="warning"
              style="cursor: pointer;"
              size="mini"
              @click="addTag(scope.$index, scope.row)"
            >{{tag}}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="status"
          label="用例状态"
          :filters="[{ text: '启用中', value: '启用中' }, { text: '已停用', value: '已停用' }]"
          :filter-method="filterTag"
          filter-placement="bottom-end"
        >
          <template slot-scope="scope">
            <el-popover trigger="hover" placement="top">
              <span style="font-size: 12px">点击 - 修改用例状态</span>
              <div slot="reference" class="name-wrapper">
                <el-tag
                  size="mini"
                  :type="scope.row.status === '启用中' ? '' : 'danger'"
                  style="cursor: pointer;"
                  @click="handleUpdateStatus(scope.$index, scope.row)"
                >{{scope.row.status}}</el-tag>
              </div>
            </el-popover>
          </template>
        </el-table-column>
        <el-table-column
          prop="last_run"
          label="最近运行"
          align="center"
          width="100"
          :filters="[{ text: '成功', value: '成功' }, { text: '失败', value: '失败' }, { text: '未运行', value: '未运行' }]"
          :filter-method="filterLastRun"
          filter-placement="bottom-end"
        >
          <template slot-scope="scope">
            <el-popover trigger="hover" placement="top">
              <span style="font-size: 12px">点击 - 刷新运行结果</span>
              <p style="font-size: 12px">最近运行: {{ scope.row.last_run }}</p>
              <p style="font-size: 12px">运行时间: {{ scope.row.lastRunTime }}</p>
              <div slot="reference" class="name-wrapper">
                <el-tag
                  size="mini"
                  effect="dark"
                  :type="scope.row.last_run === '成功' ? 'success' : (scope.row.last_run === '失败' ? 'danger':'info')"
                  style="cursor: pointer;"
                  @click="queryTestCases()"
                >{{scope.row.last_run}}</el-tag>
              </div>
            </el-popover>
          </template>
        </el-table-column>
        <!--<el-table-column prop="lastRunTime" label="最近运行时间" width="160"></el-table-column>-->
        <el-table-column prop="creator" label="创建人" width="100">
          <template slot-scope="scope">
            <el-popover trigger="hover" placement="top">
              <p style="font-size: 12px">创建时间: {{ scope.row.createTime }}</p>
              <div slot="reference" class="name-wrapper">
                <span>{{ scope.row.creator }}</span>
              </div>
            </el-popover>
          </template>
        </el-table-column>
        <!--<el-table-column prop="createTime" label="创建时间" width="160"></el-table-column>-->
        <el-table-column prop="last_modifier" label="最后修改人" width="100">
          <template slot-scope="scope">
            <el-popover trigger="hover" placement="top">
              <p style="font-size: 12px">修改时间: {{ scope.row.updateTime }}</p>
              <div slot="reference" class="name-wrapper">
                <span>{{ scope.row.last_modifier }}</span>
              </div>
            </el-popover>
          </template>
        </el-table-column>
        <!--<el-table-column prop="updateTime" label="最后修改时间" width="160"></el-table-column>-->
        <el-table-column label="操作" width="160">
          <template slot-scope="scope">
            <el-button type="primary" plain size="mini" @click="handleCopy(scope.$index, scope.row)">复制</el-button>
            <el-dropdown style="margin-left: 1px">
              <el-button size="mini" plain>
                更多
                <i class="el-icon-arrow-down el-icon--right"></i>
              </el-button>
              <el-dropdown-menu slot="dropdown">
                <!--<el-dropdown-item @click.native="handleEdit(scope.$index, scope.row)">编辑</el-dropdown-item>-->
                <!--<el-dropdown-item @click.native="handleCopy(scope.$index, scope.row)">复制</el-dropdown-item>-->
                <!--<el-dropdown-item @click.native="addTag(scope.$index, scope.row)">设置标签</el-dropdown-item>-->
                <el-dropdown-item @click.native="viewSetupCase(scope.$index, scope.row)">查看关联用例</el-dropdown-item>
                <el-dropdown-item @click.native="setFlowConfig(scope.$index, scope.row)">设置可运行链路</el-dropdown-item>
                <el-dropdown-item @click.native="handleDelete(scope.$index, scope.row)">删除</el-dropdown-item>
              </el-dropdown-menu>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination">
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
      <div style="text-align: center;">
        <el-button style="float: inherit" size="small" type="primary" icon="el-icon-caret-right" @click="handleRunCase()">执行用例</el-button>
      </div>
    </el-form>

    <!--执行测试报告选择环境页面-->
    <el-dialog title="运行测试" :visible.sync="runReportVisible" width="45%">
      <el-form ref="runReportFormValid" :model="runReportForm" label-width="100px">
        <el-form-item label="运行环境" prop="envName" :rules="[{ required: true, message: '环境必选', trigger: 'change' }]">
          <el-select v-model="runReportForm.envName" placeholder="请选择">
            <el-option v-for="item in runReportForm.supportEnv" :key="item.id" :label="item.envName" :value="item.envName"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="流程名称" prop="flowId">
          <el-select v-model="runReportForm.flowId" placeholder="请选择">
            <el-option v-for="item in runReportForm.flowList" :key="item.flowId" :label="item.flowName" :value="item.flowId"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="公共变量调试" v-if="debugPubVar">
          <template>
            <el-table :data="pubVariaTabledata" border style="width: 100%">
              <el-table-column prop="name" label="变量名" width="100"></el-table-column>
              <el-table-column prop="type" label="类型" width="60"></el-table-column>
              <el-table-column prop="value" label="变量原值" width="auto"></el-table-column>
              <el-table-column label="可选值" width="auto">
                <template slot-scope="scope">
                  <el-select v-model="temporaryVariables[scope.$index].optionValue" placeholder="请选择">
                    <el-option v-for="item in pubVariaTabledata[scope.$index].optionValues" :key="item" :label="item" :value="item"></el-option>
                  </el-select>
                </template>
              </el-table-column>
              <el-table-column label="调试值" width="auto">
                <template slot-scope="scope">
                  <el-input v-model="temporaryVariables[scope.$index].tmpValue" placeholder="请输入调试值"></el-input>
                </template>
              </el-table-column>
            </el-table>
          </template>
          <span>
            <strong>说明:本次运行可以指定公共变量的调试值，不填默认不修改变量原值</strong>
          </span>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="runReportVisible = false">取 消</el-button>
        <el-button type="primary" @click="RunCase('runReportFormValid')">运 行</el-button>
      </span>
    </el-dialog>

    <!-- 新版：新增编辑全链路用例弹出框  -->
    <el-dialog
      title="配置全链路用例"
      :visible.sync="caseEditVisible"
      width="70%"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      top="2vh"
      ref="fullLineCaseEditDialog"
      class="fullLineCaseEditDialog"
      center
    >
      <div style="margin-left: 20px">
        <el-radio-group v-model="handleSwitch">
          <el-radio :label="1">接口用例</el-radio>
          <el-radio :label="2">全链路用例</el-radio>
        </el-radio-group>
        <el-cascader
          placeholder="点此选择接口用例，支持搜索"
          :options="subCaseOptions"
          filterable
          clearable
          v-model="selectSubcaseList"
          @change="handleChangeSubCase"
          size="small"
          :debounce="1000"
          v-show="handleSwitch === 1"
          ref="intfSubCase"
          style="margin-left: 20px;margin-right: 20px"
        ></el-cascader>
        <el-cascader
          placeholder="点此选择全链路用例，支持搜索"
          :options="fullLineCaseOptions"
          filterable
          clearable
          v-model="selectfullLineCaseList"
          @change="handleChangeFullLineCase"
          size="small"
          :debounce="1000"
          v-show="handleSwitch === 2"
          ref="fullLineCase"
          style="margin-left: 20px;margin-right: 20px"
        ></el-cascader>
        <el-select
          v-model="selectfullLineSubCaseList"
          multiple
          collapse-tags
          clearable
          filterable
          style="margin-right: 20px"
          placeholder="请选择"
          v-show="handleSwitch === 2"
          ref="fullLineSubCase"
          @change="addMode=''"
        >
          <el-option v-for="item in fullLineSubCaseOptions" :key="item.value" :label="item.label" :value="item.value"></el-option>
        </el-select>
        <el-radio-group v-model="addMode" v-if="handleSwitch === 2" @change="selectMode">
          <el-radio :label="1">引用</el-radio>
          <el-radio :label="2">复制</el-radio>
        </el-radio-group>
      </div>
      <el-row :gutter="5" style="margin-top: 5px">
        <el-col :span="16">
          <el-scrollbar wrap-class="fullLineCaseEditScrolllist" view-class="view-box" :native="false">
            <div class="fullLineCaseBasic">
              <el-row>
                <!--左树-->
                <el-card>
                  <div slot="header" style="background: #EBEEF5">
                    <span class="text-header">接口调用链</span>
                    <span style="fone-size: 10px;font-style: italic;color: cornflowerblue">（注意：接口前的红色五星表示该接口已被复用，修改数据会同时影响其他用例，右键可查看复用的用例）</span>
                  </div>
                  <el-scrollbar wrap-class="fullLineCaseEditScrolllist" view-class="view-box" :native="false">
                    <div class="caseSteps">
                      <el-tree
                        :data="subCasetreeData"
                        node-key="id"
                        :props="defaultProps"
                        :default-expanded-keys="nodeKeys"
                        :highlight-current="true"
                        @node-click="handleNodeClick"
                        @node-contextmenu="rightClick"
                        @node-drag-end="handleDragEnd"
                        :allow-drop="allowDrop"
                        :allow-drag="allowDrag"
                        draggable
                        ref="tree"
                      >
                        <span slot-scope="{ node, data }">
                          <el-tooltip placement="top-start" effect="light" :content="node.label" :open-delay="500">
                            <span style="font-size: 14px">
                              <i class="el-icon-star-on" style="color: red" v-if="data.isMultiQuote"></i>
                              <i class="el-icon-star-on" style="color: rgba(255, 255, 255, 0.5)" v-else></i>
                              {{ node.label }}
                            </span>
                          </el-tooltip>
                        </span>
                      </el-tree>
                    </div>
                  </el-scrollbar>
                </el-card>
                <!--左树-->
                <!--右表-->
                <!--<el-col :span="16">
                  <el-scrollbar wrap-class="fullLineCaseEditScrolllist" view-class="view-box" :native="false">
                    <div class="caseSteps">
                      <case-edit :test-case-info="testCaseInfo" ref="caseEdit" @update-data="updateData"
                                 v-show="subCaseEditVisible"></case-edit>
                    </div>
                  </el-scrollbar>
                </el-col>-->
                <!--右表-->
              </el-row>
              <el-row style="margin-top: 10px">
                <el-card>
                  <div slot="header" style="background: #EBEEF5">
                    <span class="text-header">独立后置操作</span>
                    <el-tooltip placement="top" content="添加" effect="light">
                      <el-button
                        type="primary"
                        size="mini"
                        style="margin-left: 20px"
                        icon="el-icon-plus"
                        plain
                        @click.stop="caseTeardownForm.caseTeardownFormVisible=!caseTeardownForm.caseTeardownFormVisible"
                      ></el-button>
                    </el-tooltip>
                  </div>
                  <div>
                    <!--独立后置操作配置表单-->
                    <el-form
                      ref="caseTeardownForm"
                      :model="caseTeardownForm"
                      v-if="caseTeardownForm.caseTeardownFormVisible"
                      label-position="right"
                      label-width="120px"
                    >
                      <el-form-item label="函数类型" prop="caseTeardownFuncType" :rules="[{ required: true, message: '函数类型必选', trigger: 'change' }]">
                        <el-select v-model="caseTeardownForm.caseTeardownFuncType" placeholder="请选择函数类型" @change="selectCustomTeardownHooks()">
                          <el-option v-for="item in caseTeardownForm.supportTeardownFuncs" :key="item.key" :label="item.description" :value="item.name"></el-option>
                        </el-select>
                      </el-form-item>
                      <el-form-item
                        v-for="(item, index) in caseTeardownForm.caseTeardownFuncParam"
                        :label="item.label"
                        :key="item.key"
                        :prop="'caseTeardownFuncParam.' + index + '.value'"
                        :rules="{required: true, message: item.label + '不能为空', trigger: 'blur'}"
                      >
                        <el-input type="textarea" autosize v-model="item.value"></el-input>
                      </el-form-item>
                      <el-form-item>
                        <el-button type="primary" size="mini" @click="saveCaseTeardownForm(caseTeardownForm.idx)">保存</el-button>
                        <el-button size="mini" @click="resetCaseTeardownForm()">重置</el-button>
                      </el-form-item>
                    </el-form>
                    <!--独立后置操作数据列表-->
                    <el-table
                      :data="caseTeardownForm.caseTeardownFormDataForView"
                      border
                      style="width: 100%"
                      ref="multipleTable"
                      v-if="caseTeardownForm.caseTeardownFormDataForView.length !== 0"
                    >
                      <el-table-column type="index" width="40"></el-table-column>
                      <el-table-column prop="caseTeardownFuncType" label="函数类型" width="150px"></el-table-column>
                      <el-table-column prop="caseTeardownFuncParam" label="参数"></el-table-column>
                      <el-table-column label="操作" fixed="right" width="160">
                        <template slot-scope="scope">
                          <el-button type="text" @click="handleCaseTeardownFormEdit(scope.$index, scope.row)">编辑</el-button>
                          <el-button type="text" @click="handMoveUpTeardown(scope.$index, scope.row)" v-if="scope.$index !== 0">上移</el-button>
                          <el-button
                            type="text"
                            @click="handMoveDownTeardown(scope.$index, scope.row)"
                            v-if="scope.$index !== caseTeardownForm.caseTeardownFormDataForView.length-1"
                          >下移</el-button>
                          <el-button type="text" @click="handleCaseTeardownFormDel(scope.$index, scope.row)">删除</el-button>
                        </template>
                      </el-table-column>
                    </el-table>
                  </div>
                </el-card>
              </el-row>
            </div>
          </el-scrollbar>
        </el-col>
        <el-col :span="8">
          <el-scrollbar wrap-class="fullLineCaseEditScrolllist" view-class="view-box" :native="false">
            <div class="fullLineCaseBasic">
              <span style="color: red;margin-left: 20px;font-style: italic">用例标题自动生成，拼接方式：{用例场景}_{预期结果}</span>
              <el-form class="fullLineCaseBasicForm" ref="fullLineCaseBasicForm" :model="fullLineCaseBasicForm" label-width="80px">
                <el-form-item
                  label="用例场景"
                  prop="caseName"
                  :rules="[{ required: true, message: '用例场景必填', trigger: 'blur' },{ max: 100, message: '长度最多100 个字符', trigger: 'blur' }]"
                >
                  <el-input
                    type="textarea"
                    v-model="fullLineCaseBasicForm.caseName"
                    placeholder="请输入全链路用例场景"
                    maxlength="100"
                    :autosize="{ minRows: 4, maxRows: 4}"
                    show-word-limit
                  ></el-input>
                </el-form-item>
                <el-form-item
                  label="预期结果"
                  prop="expectResult"
                  :rules="[{ required: true, message: '预期结果必填', trigger: 'blur' },{ max: 100, message: '长度最多100 个字符', trigger: 'blur' }]"
                >
                  <el-input
                    type="textarea"
                    v-model="fullLineCaseBasicForm.expectResult"
                    placeholder="请输入预期结果"
                    maxlength="100"
                    :autosize="{ minRows: 4, maxRows: 4}"
                    show-word-limit
                  ></el-input>
                </el-form-item>
                <el-form-item label="用例描述" prop="caseDesc" :rules="[{ max: 1000, message: '长度最多1000 个字符', trigger: 'blur' }]">
                  <el-input
                    type="textarea"
                    v-model="fullLineCaseBasicForm.caseDesc"
                    placeholder="请输入用例描述"
                    maxlength="1000"
                    :autosize="{ minRows: 6, maxRows: 6}"
                    show-word-limit
                  ></el-input>
                </el-form-item>
                <el-form-item
                  :label="item.label"
                  :prop="'tagOptions.' + index + '.value'"
                  v-for="(item,index) in fullLineCaseBasicForm.tagOptions"
                  :key="index"
                  :rules="[{ required: true, message: '必选', trigger: 'change' }]"
                >
                  <el-radio-group v-model="item.value">
                    <el-radio :label="subItem.tagId" v-for="(subItem,index) in item.tagList" :key="index">{{subItem.tagName}}</el-radio>
                  </el-radio-group>
                </el-form-item>
              </el-form>
            </div>
          </el-scrollbar>
        </el-col>
      </el-row>
      <el-divider></el-divider>
      <span slot="footer" class="dialog-footer">
        <el-button @click="caseEditVisible = false">取 消</el-button>
        <el-button type="primary" @click="saveFullLineCaseEdit('fullLineCaseBasicForm')">保存全链路用例</el-button>
        <span style="font-weight: bold; color: red">(注意：点击“取消”按钮或直接关闭弹框，任何修改都不会保存)</span>
      </span>
    </el-dialog>

    <!-- 删除提示框 -->
    <el-dialog title="提示" :visible.sync="delVisible" width="300px" center>
      <div class="del-dialog-cnt">删除不可恢复，是否确定删除？</div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="delVisible = false">取 消</el-button>
        <el-button type="danger" icon="el-icon-warning" @click="deleteRow">删 除</el-button>
      </span>
    </el-dialog>

    <!-- 复制提示框 -->
    <el-dialog title="复制全链路用例" :visible.sync="copyVisible" width="20%" center>
      <el-form :model="copyForm">
        <el-form-item label="复制数量">
          <el-input-number v-model="copyForm.copyNum" size="mini" @change="handleChange" :min="1" :max="10" style="margin-top: 5px"></el-input-number>
        </el-form-item>
        <el-form-item label="复制类型">
          <el-radio v-model="copyForm.copyRadio" label="1">引用</el-radio>
          <el-radio v-model="copyForm.copyRadio" label="2">复制</el-radio>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="copyVisible = false">取 消</el-button>
        <el-button type="primary" icon="el-icon-warning" @click="copyRow">确 定</el-button>
      </span>
    </el-dialog>
    <!--新增标签弹框-->
    <el-dialog title="新增标签" :visible.sync="addTagVisible" width="20%" center>
      <el-form :model="tagForm" label-width="80px" ref="tagForm">
        <el-form-item
          :label="item.label"
          :prop="'tagOptions.' + index + '.value'"
          v-for="(item,index) in tagForm.tagOptions"
          :key="index"
          :rules="[{ required: true, message: '必选', trigger: 'change' }]"
        >
          <el-radio-group v-model="item.value">
            <el-radio :label="subItem.tagId" v-for="(subItem,index) in item.tagList" :key="index">{{subItem.tagName}}</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button type="primary" size="small" @click="saveSetTag()">保存</el-button>
      </span>
    </el-dialog>
    <!--树形控件右键菜单_一级接口-->
    <div>
      <v-contextmenu ref="contextMenuInterface">
        <v-contextmenu-item @click="deleteIntroIntf">删除接口</v-contextmenu-item>
        <v-contextmenu-item @click="viewRelatedMainCase">查看关联的用例</v-contextmenu-item>
        <v-contextmenu-item divider></v-contextmenu-item>
      </v-contextmenu>
    </div>
    <!--抽屉组件显示子用例关联的主用例列表-->
    <el-drawer :title="subCaseTitle" :visible.sync="drawer" direction="rtl" size="50%">
      <el-table :data="gridData" maxHeight="800px">
        <el-table-column property="testcaseId" label="编号" width="80"></el-table-column>
        <el-table-column property="testcaseName" label="标题" width="400"></el-table-column>
        <el-table-column property="productLineDesc" label="产品线"></el-table-column>
      </el-table>
    </el-drawer>
    <!--抽屉组件显示子用例编辑页面-->
    <el-drawer :title="subCaseTitle" :visible.sync="drawer2" direction="rtl" size="50%">
      <div class="demo-drawer__content">
        <el-scrollbar wrap-class="subCaseEditForm" view-class="view-box" :native="false">
          <div class="caseSteps">
            <case-edit :test-case-info="testCaseInfo" ref="caseEdit" @update-data="updateData" v-show="subCaseEditVisible"></case-edit>
          </div>
        </el-scrollbar>
      </div>
    </el-drawer>
    <!--弹框显示被前置的用例列表-->
    <el-dialog title="关联的用例列表（前置了本用例）" :visible.sync="drawerForSteupCase" width="75%" @close="clearCache">
      <el-table :data="gridDataForSteupCase" height="600" :header-cell-style="{color:'black',background:'#eef1f6'}">
        <el-table-column prop="id" label="用例编号" width="80"></el-table-column>
        <el-table-column prop="testcaseName" label="用例标题" width="400"></el-table-column>
        <el-table-column prop="intfName" label="接口URL" width="400"></el-table-column>
        <el-table-column label="用例标签" width="150">
          <template slot-scope="scope">
            <el-tag :key="tag" v-for="tag in gridDataForSteupCase[scope.$index].tags_name" :disable-transitions="false" size="mini">{{tag}}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="status"
          label="用例状态"
          :filters="[{ text: '启用中', value: '启用中' }, { text: '已停用', value: '已停用' }]"
          :filter-method="filterTag"
          filter-placement="bottom-end"
        >
          <template slot-scope="scope">
            <el-popover trigger="hover" placement="top">
              <p>点击 - 修改用例状态</p>
              <div slot="reference" class="name-wrapper">
                <el-button
                  size="mini"
                  plain
                  :type="scope.row.status === '启用中' ? 'primary' : 'danger'"
                  @click="handleUpdateStatus(scope.$index, scope.row)"
                >{{scope.row.status}}</el-button>
              </div>
            </el-popover>
          </template>
        </el-table-column>
        <el-table-column
          prop="testcaseLastRun"
          label="运行状态"
          align="center"
          :filters="[{ text: '成功', value: '成功' }, { text: '失败', value: '失败' }, { text: '未运行', value: '未运行' }]"
          :filter-method="filterLastRun"
          filter-placement="bottom-end"
        >
          <template slot-scope="scope">
            <el-popover trigger="hover" placement="top">
              <span style="font-size: 12px">点击 - 刷新运行结果</span>
              <p style="font-size: 12px">最近运行: {{ scope.row.testcaseLastRun }}</p>
              <p style="font-size: 12px">运行时间: {{ scope.row.lastRunTime }}</p>
              <div slot="reference" class="name-wrapper">
                <el-button
                  size="mini"
                  circle
                  :icon="scope.row.testcaseLastRun === '成功' ? 'el-icon-check' : (scope.row.testcaseLastRun === '失败' ? 'el-icon-close':'el-icon-minus')"
                  :type="scope.row.testcaseLastRun === '成功' ? 'success' : (scope.row.testcaseLastRun === '失败' ? 'danger':'info')"
                  disable-transitions
                  @click="queryTestCases(true)"
                ></el-button>
              </div>
            </el-popover>
          </template>
        </el-table-column>
        <!--<el-table-column prop="testcaseLastRunTime" label="最近运行时间" width="150"></el-table-column>-->
        <el-table-column prop="testcaseCreator" label="创建人">
          <template slot-scope="scope">
            <el-popover trigger="hover" placement="top">
              <p style="font-size: 12px">创建时间: {{ scope.row.createTime }}</p>
              <div slot="reference" class="name-wrapper">
                <span>{{ scope.row.creator }}</span>
              </div>
            </el-popover>
          </template>
        </el-table-column>
        <!--<el-table-column prop="testcaseCreateTime" label="创建时间" width="150"></el-table-column>-->
        <el-table-column prop="testcaseLasModifier" label="最后修改人">
          <template slot-scope="scope">
            <el-popover trigger="hover" placement="top">
              <p style="font-size: 12px">修改时间: {{ scope.row.updateTime }}</p>
              <div slot="reference" class="name-wrapper">
                <span>{{ scope.row.last_modifier }}</span>
              </div>
            </el-popover>
          </template>
        </el-table-column>
        <!--<el-table-column prop="testcaseUpdateTime" label="最后修改时间" width="150"></el-table-column>-->
      </el-table>
    </el-dialog>
    <!--设置可运行链路页面-->
    <el-dialog title="配置可运行链路" :visible.sync="flowConfigVisible" class="flowConfigDialog" width="50%">
      <!--配置表单-->
      <el-form class="flowConfigForm" ref="flowConfigForm" :model="flowConfigForm" labelWidth="120px" labelPosition="right">
        <el-form-item label="流程名称" prop="flowName" :rules="[{ required: true, message: '流程名称必填', trigger: 'blur' }]">
          <el-input v-model="flowConfigForm.flowName" placeholder="请输入流程名称"></el-input>
        </el-form-item>
        <el-form-item label="流程链路" prop="selectedItem" :rules="[{ required: true, message: '流程链路必填', trigger: 'change' }]">
          <el-select v-model="flowConfigForm.selectedItem" multiple collapse-tags clearable filterable placeholder="请选择" ref="fullLineSubCase">
            <el-option v-for="item in flowConfigForm.subCaseList" :key="item.value" :label="item.label" :value="item.value"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveFlowConfigForm(flowConfigForm.idx)">保存</el-button>
          <el-button @click="resetFlowConfigForm">重置</el-button>
        </el-form-item>
      </el-form>
      <!--数据列表-->
      <el-table :data="flowConfigForm.tableData" border style="width: 100%" ref="multipleTable" height="300">
        <el-table-column type="index" width="40"></el-table-column>
        <el-table-column prop="flowName" label="流程名称"></el-table-column>
        <el-table-column label="操作" fixed="right" width="160">
          <template slot-scope="scope">
            <el-button type="text" @click="handleFlowConfigEdit(scope.$index, scope.row)">编辑</el-button>
            <el-button type="text" @click.native.prevent="handleFlowConfigDel(scope.$index, flowConfigForm.tableData)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <span slot="footer" class="dialog-footer">
        <el-button type="primary" size="small" @click="saveFlowConfig()">保存</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { subtreeIntfCase, subtreeProductLine } from '@/api/autotest/manage/resource-apiManage/company'
import {
  addFullLineCase,
  editFullLineCase,
  deleteFullLineCase,
  copyFullLineCase,
  queryFullLineCaseDetail,
  queryCaseByProduceId,
  changeFullLineCaseStatus,
  getRelatedMainCaseBySubCaseId,
  getCustomFlows,
  saveCustomFlows,
  setTags
} from '@/api/autotest/manage/fullLineCase/testcase-config'
import { queryDetailWithSetup, queryListBySetupCase } from '@/api/autotest/manage/testcase-apiManage/config'
import { queryTagList, queryCustomTeardownHooks } from '@/api/autotest/manage/testcase-apiManage/support'
import { run } from '@/api/autotest/manage/testcase-apiManage/run'
import { fetchEnvList } from '@/api/autotest/manage/resource-envManage'
import { queryPubVarsByTcList } from '@/api/autotest/manage/resource-publicVariable'
import { mapState, mapMutations } from 'vuex'
import { sortNumber } from '@/libs/common'

export default {
  name: 'fullLineCaseConfig',
  components: {
    'case-edit': () => import('../../components/case-edit')
  },
  data() {
    return {
      flowConfigVisible: false, // 配置可运行链路页面是否显示
      flowConfigForm: {
        // 配置可运行链路页面 配置表单
        flowName: '', // 流程名称
        idx: -1, // 编辑数据的索引
        tableData: [], // 列表数据
        subCaseList: [], // 子用例列表
        selectedItem: [] // 选中的子用例
      },
      delIntroduceCaseId: '',
      delSubId: '',
      testCaseInfo: {
        base: {
          testcaseName: '',
          expectResult: ''
        },
        steps: [
          {
            setupInfo: [],
            variableInfo: [],
            requestInfo: [],
            teardownInfo: [],
            validateInfo: [],
            extractInfo: [],
            requestTeardownInfo: []
          }
        ]
      },
      produceLineProp: {
        show: false
      },
      fullLineCaseBasicForm: {
        caseName: '',
        caseDesc: '',
        expectResult: '',
        tagOptions: ''
      },
      interfaceProp: {
        type: '',
        apiUrl: '',
        headers: '',
        method: '',
        dubboService: '',
        dubboMethod: '',
        parameterTypes: '',
        version: '',
        topic: '',
        tag: '',
        intfChineseName: ''
      },
      subCasetreeData: [],
      filterText: '',
      subCaseOptions: [],
      fullLineCaseOptions: [], // 缓存全链路用例节点树
      selectSubcaseList: [],
      selectfullLineCaseList: [], // 缓存已选择的全链路用例列表
      selectfullLineSubCaseList: [], // 缓存已选择的全链路用例子用例列表
      fullLineSubCaseOptions: [], // 缓存全链路子用例节点数
      fullLineCaseInfo: [], // 缓存根据全链路用例查询到的所有子用例信息
      defaultProps: {
        children: 'children',
        label: 'label'
      },
      subCaseEditVisible: false,
      nodeKeys: [],
      tableData: [],
      lastTestCaseId: 0,
      currentPage: 1,
      pagesize: 10,
      totalCount: 10,
      handleSwitch: 1, // 接口用例和全链路切换标志，1-接口用例，2-全链路用例
      addMode: null, // 全链路用添加模式，1-引用，2-复制
      copyCaseRadio: '1',
      editCaseIdx: -1,
      editSubCaseIdx: -1,
      intfId: '',
      fullLineTestCaseId: '',
      subTestCaseId: '',
      introduceCaseId: '',
      delVisible: false,
      copyForm: {
        copyNum: '1', // 复制数量
        copyRadio: '1' // 1:复制主用例，引用子用例 2:复制主用例和子用例
      },
      copyVisible: false,
      caseEditVisible: false,
      caseTeardownForm: {
        caseTeardownFormVisible: false,
        caseTeardownFuncType: '',
        supportTeardownFuncs: [],
        caseTeardownFuncParam: [],
        idx: -1,
        caseTeardownFormDataForView: [],
        caseTeardownFormData: []
      },
      multipleSelection: [],
      testcaseList: [],
      reportId: '',
      runReportVisible: false,
      runReportForm: {
        envName: '',
        supportEnv: [],
        flowId: null, // 可运行的流程链路id
        flowList: [] // 支持的可运行流程链路列表
      },
      pubVariaTabledata: [], // 临时公共变量tabledata
      temporaryVariables: [], // 更改公共变量后，run接口参数
      pubVariableChanges: [],
      testcaseChainData: [], // 用例调用链数据
      chainVisible: false,
      debugPubVar: false,
      addTagVisible: false,
      fullLineRequestSteps: [],
      tagForm: {
        // 设置标签表单
        tagOptions: [],
        addTagcaseId: ''
      },
      drawer: false, // 抽屉组件关联用例列表是否显示
      gridData: [], // 子用例关联的主用例数据
      drawer2: false, // 抽屉组件编辑子用例页面是否显示
      subCaseTitle: '', // 抽屉组件标题
      subCaseId: null, // 接口调用链中子用例ID
      drawerForSteupCase: false, // 抽屉组件关联用例列表是否显示
      gridDataForSteupCase: [] // 子用例关联的主用例数据
    }
  },
  computed: {
    ...mapState('d2admin/fulllinecase', ['caseTable', 'addCaseVisible', 'baseTable'])
  },
  mounted() {
    this.queryTagList()
  },
  methods: {
    ...mapMutations({
      addCase: 'd2admin/fulllinecase/addCase'
    }),
    /* getMyEvent () {
                this.$refs.caseEdit.saveTestCaseInfo();
            },*/
    // 编辑子用例后更新主用例缓存
    updateData(subCaseInfo) {
      const baseInfo = {}
      baseInfo['intfId'] = this.intfId
      baseInfo['subName'] = subCaseInfo.base.testcaseName
      baseInfo['subDesc'] = subCaseInfo.base.testcaseDesc
      baseInfo['subExpectResult'] = subCaseInfo.base.expectResult
      // 编辑的是已经引入过的
      if (this.subTestCaseId) {
        baseInfo['subId'] = this.subTestCaseId
      }
      // 编辑的是新引入还未保存的
      if (this.introduceCaseId) {
        baseInfo['introduceCaseId'] = this.introduceCaseId
      }
      // 处理子用例详情中requestInfo
      const requestInfo = {}
      requestInfo['isMerge'] = subCaseInfo.steps[0].requestInfo.isMerge
      if (this.interfaceProp.type === 'HTTP') {
        requestInfo['json'] = JSON.parse(subCaseInfo.steps[0].requestInfo.json)
        requestInfo['type'] = 1
        if (subCaseInfo.steps[0].requestInfo.type === 2) {
          requestInfo['sign'] = subCaseInfo.steps[0].requestInfo.sign.name
        }
      } else if (this.interfaceProp.type === 'DUBBO') {
        requestInfo['args'] = JSON.parse(subCaseInfo.steps[0].requestInfo.json)
        requestInfo['type'] = 2
      } else if (this.interfaceProp.type === 'MQ') {
        requestInfo['msg'] = subCaseInfo.steps[0].requestInfo.json
        requestInfo['type'] = 3
      } else {
        alert('接口类型为定义')
      }
      const subRequestBody = {}
      subRequestBody['base'] = baseInfo
      subRequestBody['setupInfo'] = subCaseInfo.steps[0].setupInfo
      subRequestBody['variableInfo'] = subCaseInfo.steps[0].variableInfo
      subRequestBody['teardownInfo'] = subCaseInfo.steps[0].teardownInfo
      subRequestBody['requestInfo'] = requestInfo
      subRequestBody['validateInfo'] = subCaseInfo.steps[0].validateInfo
      subRequestBody['extractInfo'] = subCaseInfo.steps[0].extractInfo
      subRequestBody['requestTeardownInfo'] = subCaseInfo.steps[0].requestTeardownInfo
      let itemSubCaseId = this.fullLineRequestSteps.find(c => c.base.subId === this.subTestCaseId)
      let itemIntroduceCaseId = this.fullLineRequestSteps.find(c => c.base.introduceCaseId === this.introduceCaseId)
      if (itemSubCaseId !== undefined || itemIntroduceCaseId !== undefined) {
        let index = ''
        if (this.introduceCaseId) {
          index = this.findIndex(this.fullLineRequestSteps, itemIntroduceCaseId)
        } else if (this.subTestCaseId) {
          index = this.findIndex(this.fullLineRequestSteps, itemSubCaseId)
        }
        this.fullLineRequestSteps[index] = subRequestBody
        //                    this.$message.success('编辑子用例成功')
      } else if (itemSubCaseId === undefined && itemIntroduceCaseId === undefined) {
        this.fullLineRequestSteps.push(subRequestBody)
        this.$message.success('新增子用例成功')
      }
    },
    // 点击主用例步骤，展示子用例详情
    handleNodeClick(data, node) {
      this.drawer2 = true
      this.subCaseTitle = data.label
      console.log('data:', data)
      this.$refs['contextMenuInterface'].hide()
      let subCaseId = ''
      this.intfId = data.intfId
      this.subCaseEditVisible = true
      this.interfaceProp.type = data.type
      this.interfaceProp.intfChineseName = data.intfChineseName
      this.subTestCaseId = ''
      this.introduceCaseId = ''
      let signObj = {}
      if ('subId' in data && data.subId !== '') {
        subCaseId = data.subId
        this.editSubCaseIdx = subCaseId
        this.subTestCaseId = subCaseId
        let itemCaseId = this.fullLineRequestSteps.find(c => c.base.subId === subCaseId)
        if (itemCaseId !== undefined) {
          // 回填子用例基本信息
          if (itemCaseId.requestInfo.type === 1 && itemCaseId.requestInfo.sign) {
            if (!itemCaseId.requestInfo.sign.name) {
              signObj['name'] = itemCaseId.requestInfo.sign
              itemCaseId.requestInfo.sign = signObj
            }
          }
          let steps = {
            setupInfo: itemCaseId.setupInfo,
            variableInfo: itemCaseId.variableInfo,
            teardownInfo: itemCaseId.teardownInfo,
            requestInfo: itemCaseId.requestInfo,
            validateInfo: itemCaseId.validateInfo,
            extractInfo: itemCaseId.extractInfo,
            requestTeardownInfo: itemCaseId.requestTeardownInfo
          }
          let base = {
            testcaseName: itemCaseId.base.subName,
            testcaseDesc: itemCaseId.base.subDesc,
            expectResult: itemCaseId.base.subExpectResult
          }
          this.testCaseInfo['base'] = base
          this.testCaseInfo['steps'][0] = steps
          console.log('父组件传给子组件testCaseInfo信息，子组件回填，', this.testCaseInfo)
          this.$refs.caseEdit.pageLoad(this.testCaseInfo)
        }
      } else if ('introduceCaseId' in data && data.introduceCaseId !== '') {
        subCaseId = data.introduceCaseId
        this.introduceCaseId = subCaseId
        this.editSubCaseIdx = subCaseId
        let introduceCaseItem = this.fullLineRequestSteps.find(c => c.base.introduceCaseId === subCaseId)
        if (introduceCaseItem !== undefined) {
          // 回填引入的原接口用例基本信息
          if (introduceCaseItem.requestInfo.type === 1 && introduceCaseItem.requestInfo.sign) {
            if (!introduceCaseItem.requestInfo.sign.name) {
              signObj['name'] = introduceCaseItem.requestInfo.sign
              introduceCaseItem.requestInfo['sign'] = signObj
            }
          }
          let steps = {
            setupInfo: introduceCaseItem.setupInfo,
            variableInfo: introduceCaseItem.variableInfo,
            teardownInfo: introduceCaseItem.teardownInfo,
            requestInfo: introduceCaseItem.requestInfo,
            validateInfo: introduceCaseItem.validateInfo,
            extractInfo: introduceCaseItem.extractInfo,
            requestTeardownInfo: introduceCaseItem.requestTeardownInfo
          }
          let base = {
            testcaseName: introduceCaseItem.base.subName,
            expectResult: introduceCaseItem.base.subExpectResult
          }
          this.testCaseInfo.base = base
          this.testCaseInfo.steps[0] = steps
          console.log('父组件传给子组件testCaseInfo信息，子组件回填(新引入的接口)，', this.testCaseInfo)
          this.$refs.caseEdit.pageLoad(this.testCaseInfo)
        }
      } else {
        this.editSubCaseIdx = -1
      }
    },
    rightClick(event, object, value) {
      this.subCaseTitle = object.label
      this.subCaseId = object.subId
      console.log(object)
      this.$refs.tree.setCurrentKey(value.key)
      if (value.level === 1) {
        const position = {
          top: event.clientY,
          left: event.clientX + 20
        }
        this.$refs['contextMenuInterface'].show(position)
        this.delIntroduceCaseId = ''
        this.delSubId = ''
        if (object.introduceCaseId) {
          this.delIntroduceCaseId = object.introduceCaseId
        } else if (object.subId) {
          this.delSubId = object.subId
        }
      }
    },
    // 移除引入的接口子用例
    deleteIntroIntf() {
      if (this.delIntroduceCaseId) {
        let item = this.subCasetreeData.find(c => c.introduceCaseId === this.delIntroduceCaseId)
        if (item !== undefined) {
          const index = this.findIndex(this.subCasetreeData, item)
          this.subCasetreeData.splice(index, 1)
          for (let i = index; i < this.subCasetreeData.length; i++) {
            console.log(i)
            let idx = this.subCasetreeData[i].label.indexOf('.')
            this.subCasetreeData[i].label = (i + 1).toString() + this.subCasetreeData[i].label.slice(idx)
          }
          this.subCaseEditVisible = false
        }
        let itemIntroduceCaseId = this.fullLineRequestSteps.find(c => c.base.introduceCaseId === this.delIntroduceCaseId)
        if (itemIntroduceCaseId !== undefined) {
          const index = this.findIndex(this.fullLineRequestSteps, itemIntroduceCaseId)
          this.fullLineRequestSteps.splice(index, 1)
        }
      } else if (this.delSubId) {
        let item = this.subCasetreeData.find(c => c.subId === this.delSubId)
        if (item !== undefined) {
          let index = this.findIndex(this.subCasetreeData, item)
          this.subCasetreeData.splice(index, 1)
          for (let i = index; i < this.subCasetreeData.length; i++) {
            console.log(i)
            let idx = this.subCasetreeData[i].label.indexOf('.')
            this.subCasetreeData[i].label = (i + 1).toString() + this.subCasetreeData[i].label.slice(idx)
          }
          this.subCaseEditVisible = false
        }
        let itemSubId = this.fullLineRequestSteps.find(c => c.base.subId === this.delSubId)
        if (itemSubId !== undefined) {
          const index = this.findIndex(this.fullLineRequestSteps, itemSubId)
          this.fullLineRequestSteps.splice(index, 1)
        }
      }
    },
    // 获取对象索引
    findIndex(arr, obj) {
      var objStr = JSON.stringify(obj)
      return arr.reduce((index, ele, i) => {
        if (JSON.stringify(ele) === objStr) {
          return i
        } else {
          return index
        }
      }, -1)
    },
    // 处理选择接口流程子用例触发的事件:前端缓存数据
    handleChangeSubCase(value) {
      if (value.length !== 0) {
        let introduceCaseId = ''
        if (value.length === 3) {
          introduceCaseId = value[2]
          this.copySubCase(introduceCaseId)
        }
      }
    },
    // 处理选择全链路流程子用例触发的事件:前端缓存数据
    handleChangeFullLineCase(value) {
      if (value.length !== 0) {
        queryFullLineCaseDetail({ testcaseId: value[value.length - 1] }).then(res => {
          if (res.data.steps) {
            this.fullLineCaseInfo = res.data.steps
            this.fullLineSubCaseOptions = []
            res.data.steps.forEach(item => {
              this.fullLineSubCaseOptions.push({
                value: item.base.subId,
                label: item.base.intfName + '（' + item.base.subName + '）'
              })
            })
          }
        })
      }
      let obj = {}
      obj.stopPropagation = () => {}
      this.$refs.fullLineSubCase.handleClearClick(obj)
    },
    // 添加全链路子用例，引用或复制
    selectMode() {
      console.log(this.fullLineCaseInfo)
      if (this.addMode === 1) {
        this.selectfullLineSubCaseList.forEach(item => {
          this.introduceFullLineSubCase(item)
        })
      } else if (this.addMode === 2) {
        this.selectfullLineSubCaseList.forEach(item => {
          this.copyFullLineSubCase(item)
        })
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
    // 点击新增全链路测试用例按钮触发的事件
    handleAddCase() {
      this.queryCustomFuncsData()
      this.caseEditVisible = true
      this.editCaseIdx = -1
      this.subCaseEditVisible = false
      this.fullLineCaseBasicForm.caseName = ''
      this.fullLineCaseBasicForm.caseDesc = ''
      this.fullLineCaseBasicForm.expectResult = ''
      this.fullLineCaseBasicForm.tagOptions.forEach(item => {
        item.value = ''
      })
      this.caseTeardownForm.caseTeardownFormData = []
      this.caseTeardownForm.caseTeardownFormVisible = []
      this.subCasetreeData = []
      this.fullLineRequestSteps = []
      this.subCaseOptions = []
      this.fullLineCaseOptions = []
      this.subtreeIntfCase()
      this.getFullLineSubTree()
      this.handleSwitch = 1
      this.$nextTick(() => {
        this.$refs.fullLineCase.handleClear()
        this.$refs.intfSubCase.handleClear()
        let obj = {}
        obj.stopPropagation = () => {}
        this.$refs.fullLineSubCase.handleClearClick(obj)
        this.resetForm('fullLineCaseBasicForm')
      })
    },
    // 点击修改测试用例按钮触发的事件
    handleEdit(index, row) {
      this.$message({
        message: '数据加载中...',
        type: 'info',
        duration: 1000
      })
      this.queryCustomFuncsData()
      this.editCaseIdx = index
      this.fullLineTestCaseId = row.id
      this.subCaseEditVisible = false
      this.subCaseOptions = []
      this.fullLineCaseOptions = []
      this.fullLineRequestSteps = []
      this.caseTeardownForm.caseTeardownFormData = []
      this.caseTeardownForm.caseTeardownFormDataForView = []
      this.caseTeardownForm.caseTeardownFormVisible = false
      // 回填标签信息
      this.fullLineCaseBasicForm.tagOptions.forEach(item => {
        for (var i in row.tags) {
          if (row.tags[i].length !== 0) {
            if (item.label === i) {
              item.value = row.tags[i][0].tagId
            }
          }
        }
      })
      this.fullLineCaseDetail(row.id).then(res => {
        this.handleSwitch = 1
        this.$nextTick(() => {
          this.$refs.fullLineCase.handleClear()
          this.$refs.intfSubCase.handleClear()
          let obj = {}
          obj.stopPropagation = () => {}
          this.$refs.fullLineSubCase.handleClearClick(obj)
          this.$refs.fullLineCaseBasicForm.clearValidate()
        })
      })
    },
    // 查询系统支持的后置函数
    queryCustomFuncsData() {
      if (this.caseTeardownForm.supportTeardownFuncs.length === 0) {
        queryCustomTeardownHooks({}).then(res => {
          this.caseTeardownForm.supportTeardownFuncs = res.data
        })
      }
    },
    // 获取全链路用例可选择的接口子用例
    subtreeIntfCase() {
      subtreeIntfCase({ companyId: this.baseTable.companyId }).then(res => {
        this.subCaseOptions = res.data
      })
    },
    // 获取全链路用例可选择的全链路子用例
    getFullLineSubTree() {
      subtreeProductLine({ companyId: this.baseTable.companyId }).then(res => {
        this.traversalObject(res.data)
        this.fullLineCaseOptions = res.data
      })
    },
    traversalObject(obj) {
      obj.forEach(item => {
        if (item.children.length !== 0) {
          this.traversalObject(item.children)
          item['value'] = item.productLineId
          delete item.productLineId
        } else if ('productLineId' in item) {
          item['value'] = item.productLineId
          delete item.productLineId
        } else {
          item['value'] = item.testcaseId
          delete item.testcaseId
          delete item.children
        }
      })
    },
    // 获取全链路用例详情
    fullLineCaseDetail(id) {
      return new Promise((resolve, reject) => {
        queryFullLineCaseDetail({ testcaseId: id }).then(res => {
          this.fullLineCaseBasicForm.caseName = res.data.base.testcaseName
          this.fullLineCaseBasicForm.caseDesc = res.data.base.testcaseDesc
          this.fullLineCaseBasicForm.expectResult = res.data.base.expectResult
          this.subCasetreeData = []
          res.data.steps.forEach(item => {
            this.subCasetreeData.push({
              label: (res.data.steps.indexOf(item) + 1).toString() + '.' + item.base.intfName + '（' + item.base.subName + '）',
              intfId: item.base.intfId,
              subId: item.base.subId,
              type: item.base.requestType,
              isMultiQuote: item.base.isMultiQuote
            })
          })
          // 回填独立后置信息
          let mainTeardownInfo = res.data.base.mainTeardownInfo
          mainTeardownInfo.forEach(item => {
            let caseTeardownFuncParam = ''
            if (item.args) {
              Object.keys(item.args).forEach(function(key) {
                caseTeardownFuncParam = caseTeardownFuncParam ? caseTeardownFuncParam + '||' + key + '=' + item.args[key] : key + '=' + item.args[key]
              })
            }
            // 用于列表展示数据
            this.caseTeardownForm.caseTeardownFormDataForView.push({
              caseTeardownFuncType: item.desc,
              caseTeardownFuncParam: caseTeardownFuncParam || '无'
            })
            // 用于提交接口数据
            this.caseTeardownForm.caseTeardownFormData.push({
              name: item.name,
              desc: item.desc,
              args: item.args
            })
          })
          this.fullLineRequestSteps = res.data.steps
          this.caseEditVisible = true
          this.subtreeIntfCase()
          this.getFullLineSubTree()
          resolve(1)
        })
      })
    },
    // 全链路用例级联选择后触发，复制原接口用例
    copySubCase(introduceCaseId) {
      queryDetailWithSetup({ testcaseId: introduceCaseId, forQll: true }).then(res => {
        const infoWithSetup = res.dataList
        let index = 1
        infoWithSetup.forEach(item => {
          this.subCasetreeData.push({
            label: (this.subCasetreeData.length + 1).toString() + '.' + item.base.intfName + '（' + item.base.subName + '）',
            intfId: item.base.intfId,
            introduceCaseId: index,
            type: item.base.requestType
          })
          // fullLineRequestSteps 缓存列表添加新引入接口用例
          const baseInfo = {}
          baseInfo['intfId'] = item.base.intfId
          baseInfo['introduceCaseId'] = index
          baseInfo['subName'] = item.base.subName
          baseInfo['subDesc'] = item.base.subDesc
          baseInfo['subExpectResult'] = item.base.subExpectResult
          const subRequestBody = {}
          // 处理子用例详情中requestInfo
          const requestInfo = item.requestInfo
          if (requestInfo.type === 1) {
            if (requestInfo.sign) {
              requestInfo['sign'] = requestInfo.sign.name
            }
            if (requestInfo.emptyCheckParamList) {
              requestInfo['emptyCheckParamList'] = requestInfo.emptyCheckParamList
            }
          } else if (requestInfo.type === 2) {
            requestInfo['args'] = requestInfo.args
          } else if (requestInfo.type === 3) {
            requestInfo['msg'] = requestInfo.msg
          } else {
            alert('接口类型未定义')
          }
          // 处理子用例详情中validateInfo
          const validateInfo = []
          item.validateInfo.forEach(itemVal => {
            const validate = {}
            validate['comparator'] = itemVal.comparator
            validate['check'] = itemVal.check
            validate['expect'] = itemVal.expect
            validate['comment'] = itemVal.comment
            validateInfo.push(validate)
          })
          subRequestBody['base'] = baseInfo
          subRequestBody['requestInfo'] = requestInfo
          subRequestBody['validateInfo'] = validateInfo
          subRequestBody['setupInfo'] = item.setupInfo
          subRequestBody['variableInfo'] = item.variableInfo
          subRequestBody['extractInfo'] = item.extractInfo
          subRequestBody['teardownInfo'] = item.teardownInfo
          subRequestBody['requestTeardownInfo'] = item.requestTeardownInfo
          this.fullLineRequestSteps.push(subRequestBody)
          index = index + 1
        })
      })
    },
    // 引用全链路用例
    introduceFullLineSubCase(fullLineSubCaseId) {
      let obj = this.fullLineCaseInfo.find(c => c.base.subId === fullLineSubCaseId)
      this.subCasetreeData.push({
        label: (this.subCasetreeData.length + 1).toString() + '.' + obj.base.intfName + '（' + obj.base.subName + '）',
        intfId: obj.base.intfId,
        subId: fullLineSubCaseId,
        type: obj.base.requestType
      })
      // fullLineRequestSteps 缓存列表添加新引入接口用例
      const baseInfo = {}
      baseInfo['intfId'] = obj.base.intfId
      baseInfo['subId'] = fullLineSubCaseId
      baseInfo['subName'] = obj.base.subName
      baseInfo['subDesc'] = obj.base.subDesc
      baseInfo['subExpectResult'] = obj.base.subExpectResult
      const subRequestBody = {}
      // 处理子用例详情中requestInfo
      const requestInfo = obj.requestInfo
      if (requestInfo.type === 1) {
        if (requestInfo.sign) {
          requestInfo['sign'] = requestInfo.sign.name
        }
        if (requestInfo.emptyCheckParamList) {
          requestInfo['emptyCheckParamList'] = requestInfo.emptyCheckParamList
        }
      } else if (requestInfo.type === 2) {
        requestInfo['args'] = requestInfo.args
      } else if (requestInfo.type === 3) {
        requestInfo['msg'] = requestInfo.msg
      } else {
        alert('接口类型未定义')
      }
      // 处理子用例详情中validateInfo
      const validateInfo = []
      obj.validateInfo.forEach(itemVal => {
        const validate = {}
        validate['comparator'] = itemVal.comparator
        validate['check'] = itemVal.check
        validate['expect'] = itemVal.expect
        validate['comment'] = itemVal.comment
        validateInfo.push(validate)
      })
      subRequestBody['base'] = baseInfo
      subRequestBody['requestInfo'] = requestInfo
      subRequestBody['validateInfo'] = validateInfo
      subRequestBody['setupInfo'] = obj.setupInfo
      subRequestBody['variableInfo'] = obj.variableInfo
      subRequestBody['extractInfo'] = obj.extractInfo
      subRequestBody['teardownInfo'] = obj.teardownInfo
      subRequestBody['requestTeardownInfo'] = obj.requestTeardownInfo
      this.fullLineRequestSteps.push(subRequestBody)
      console.log('缓存的用例信息：', this.fullLineRequestSteps)
    },
    // 复制全链路用例
    copyFullLineSubCase(copyCaseId) {
      let obj = this.fullLineCaseInfo.find(c => c.base.subId === copyCaseId)
      this.subCasetreeData.push({
        label: (this.subCasetreeData.length + 1).toString() + '.' + obj.base.intfName + '（' + obj.base.subName + '）',
        intfId: obj.base.intfId,
        introduceCaseId: copyCaseId,
        type: obj.base.requestType
      })
      // fullLineRequestSteps 缓存列表添加新引入接口用例
      const baseInfo = {}
      baseInfo['intfId'] = obj.base.intfId
      baseInfo['introduceCaseId'] = copyCaseId
      baseInfo['subName'] = obj.base.subName
      baseInfo['subDesc'] = obj.base.subDesc
      baseInfo['subExpectResult'] = obj.base.subExpectResult
      const subRequestBody = {}
      // 处理子用例详情中requestInfo
      const requestInfo = obj.requestInfo
      if (requestInfo.type === 1) {
        if (requestInfo.sign) {
          requestInfo['sign'] = requestInfo.sign.name
        }
        if (requestInfo.emptyCheckParamList) {
          requestInfo['emptyCheckParamList'] = requestInfo.emptyCheckParamList
        }
      } else if (requestInfo.type === 2) {
        requestInfo['args'] = requestInfo.args
      } else if (requestInfo.type === 3) {
        requestInfo['msg'] = requestInfo.msg
      } else {
        alert('接口类型未定义')
      }
      // 处理子用例详情中validateInfo
      const validateInfo = []
      obj.validateInfo.forEach(itemVal => {
        const validate = {}
        validate['comparator'] = itemVal.comparator
        validate['check'] = itemVal.check
        validate['expect'] = itemVal.expect
        validate['comment'] = itemVal.comment
        validateInfo.push(validate)
      })
      subRequestBody['base'] = baseInfo
      subRequestBody['requestInfo'] = requestInfo
      subRequestBody['validateInfo'] = validateInfo
      subRequestBody['setupInfo'] = obj.setupInfo
      subRequestBody['variableInfo'] = obj.variableInfo
      subRequestBody['extractInfo'] = obj.extractInfo
      subRequestBody['teardownInfo'] = obj.teardownInfo
      subRequestBody['requestTeardownInfo'] = obj.requestTeardownInfo
      this.fullLineRequestSteps.push(subRequestBody)
      console.log('缓存的用例信息：', this.fullLineRequestSteps)
    },
    // 点击删除用例触发的事件
    handleDelete(index, row) {
      this.editCaseIdx = index
      this.fullLineTestCaseId = row.id
      this.delVisible = true
    },
    // 新增用例标签
    addTag(index, row) {
      this.addTagVisible = true
      this.tagForm.addTagcaseId = row.id
      this.tagForm.tagOptions.forEach(item => {
        for (var i in row.tags) {
          if (item.label === i) {
            item.value = row.tags[i].length !== 0 ? row.tags[i][0].tagId : ''
          }
        }
      })
    },
    // 保存用例标签
    saveSetTag() {
      let tagIdList = []
      this.tagForm.tagOptions.forEach(i => {
        if (i.value) {
          tagIdList.push(i.value)
        }
      })
      this.$refs['tagForm'].validate(valid => {
        if (valid) {
          setTags({ testcaseId: this.tagForm.addTagcaseId, tagIdList: tagIdList }).then(res => {
            this.$message.success(res.desc)
            this.addTagVisible = false
            this.queryTestCases(true)
          })
        }
      })
    },
    // 删除用例标签，
    handleCloseTag(index, tag) {
      this.tableData[index].tags_name.splice(this.tableData[index].tags_name.indexOf(tag), 1)
    },
    // 获取标签list
    queryTagList() {
      queryTagList({}).then(res => {
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
        this.tagForm.tagOptions = tagOptions
        this.fullLineCaseBasicForm.tagOptions = tagOptions
      })
    },
    // 点击复制用例触发的事件
    handleCopy(index, row) {
      this.editCaseIdx = index
      this.fullLineTestCaseId = row.id
      this.copyVisible = true
    },
    handleChange(value) {
      this.copyForm.copyNum = value
    },
    // 确定复制用例
    copyRow() {
      copyFullLineCase({
        id: this.fullLineTestCaseId,
        copyNum: this.copyForm.copyNum,
        copyType: this.copyForm.copyRadio
      }).then(res => {
        this.$message.success(res.desc)
        this.queryTestCases()
      })
      this.copyVisible = false
      this.copyForm.copyNum = 1
    },
    // 确定删除
    deleteRow() {
      deleteFullLineCase({
        testcaseId: this.fullLineTestCaseId
      }).then(res => {
        this.$message.success(res.desc)
        this.queryTestCases()
      })
      this.delVisible = false
    },

    // 更新全链路用例状态
    handleUpdateStatus(index, row) {
      changeFullLineCaseStatus({
        id: row.id
      }).then(res => {
        // scope.row.status = 1;
        this.queryTestCases()
      })
    },
    // 保存全链路流程用例编辑表单内容
    saveFullLineCaseEdit(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          let baseInfo = {
            productLineId: this.caseTable.productLineId,
            testcaseName: this.fullLineCaseBasicForm.caseName.replace(/[\r\n]/g, '').trim(),
            testcaseDesc: this.fullLineCaseBasicForm.caseDesc,
            expectResult: this.fullLineCaseBasicForm.expectResult.replace(/[\r\n]/g, '').trim(),
            mainTeardownInfo: this.caseTeardownForm.caseTeardownFormData
          }
          if (this.editCaseIdx !== -1) {
            baseInfo['testcaseId'] = this.fullLineTestCaseId
          }
          // 保存标签信息
          let tagIdList = []
          this.fullLineCaseBasicForm.tagOptions.forEach(i => {
            if (i.value) {
              tagIdList.push(i.value)
            }
          })
          baseInfo['tagIdList'] = tagIdList
          // 完整的全链路用例请求内容
          let fullLineCaseRequestBody = {
            base: baseInfo,
            steps: this.fullLineRequestSteps
          }
          if (this.editCaseIdx === -1) {
            addFullLineCase(fullLineCaseRequestBody).then(res => {
              this.$message.success(res.desc)
              this.caseEditVisible = false
              this.queryTestCases()
              this.$message.success('新增全链路用例成功')
            })
          } else {
            editFullLineCase(fullLineCaseRequestBody).then(res => {
              this.$message.success(res.desc)
              this.caseEditVisible = false
              this.queryTestCases()
              this.$message.success('编辑全链路用例成功')
            })
          }
        } else {
          return false
        }
      })
    },
    // 拖拽节点
    allowDrop(draggingNode, dropNode, type) {
      return type !== 'inner'
    },
    allowDrag(draggingNode) {
      return draggingNode
    },
    handleDragEnd(draggingNode, dropNode) {
      if (draggingNode.data.subId) {
        let draggingId = draggingNode.data.subId
        let obj = this.subCasetreeData.find(c => c.subId === draggingId)
        let objIndex = this.subCasetreeData.indexOf(obj)

        let oriObj = this.fullLineRequestSteps.find(c => c.base.subId === draggingId)
        let oriObjIndex = this.fullLineRequestSteps.indexOf(oriObj)

        this.fullLineRequestSteps.splice(oriObjIndex, 1)
        this.fullLineRequestSteps.splice(objIndex, 0, oriObj)
      } else if (draggingNode.data.introduceCaseId) {
        let draggingId = draggingNode.data.introduceCaseId
        let obj = this.subCasetreeData.find(c => c.introduceCaseId === draggingId)
        let objIndex = this.subCasetreeData.indexOf(obj)

        let oriObj = this.fullLineRequestSteps.find(c => c.base.introduceCaseId === draggingId)
        let oriObjIndex = this.fullLineRequestSteps.indexOf(oriObj)

        this.fullLineRequestSteps.splice(oriObjIndex, 1)
        this.fullLineRequestSteps.splice(objIndex, 0, oriObj)
      }
    },
    // 重置表单
    resetForm(formName) {
      if (this.$refs[formName] !== undefined) {
        this.$refs[formName].resetFields()
      }
    },
    // 根据测试集ID查询测试用例列表
    queryTestCases() {
      if (this.lastTestCaseId === 0) {
        this.lastTestCaseId = this.caseTable.productLineId
      }
      if (this.lastTestCaseId !== this.caseTable.productLineId) {
        this.currentPage = 1
      }
      this.lastTestCaseId = this.caseTable.productLineId

      queryCaseByProduceId({
        productLineId: this.caseTable.productLineId,
        pageNo: this.currentPage,
        pageSize: this.pagesize
      }).then(res => {
        res.desc.forEach(item => {
          let tagNames = []
          for (var i in item.tags) {
            if (item.tags[i].length !== 0) {
              item.tags[i].forEach(subItem => {
                tagNames.push(subItem.tagName)
              })
            }
          }
          item.tags_name = tagNames
        })
        this.tableData = res.desc
        this.totalCount = res.totalNum
      })
    },
    // 根据测试用例状态显示不同颜色
    tableRowClassName({ row }) {
      if (row.status === '已停用') {
        // return 'warning-row'
        return ''
      }
      return ''
    },
    // 显示测试用例状态标签
    formatter(row, column) {
      return row.address
    },
    filterTag(value, row) {
      return row.status === value
    },
    filterLastRun(value, row) {
      return row.last_run === value
    },
    filterHandler(value, row, column) {
      const property = column['property']
      return row[property] === value
    },
    // 测试用例列表选择要运行的测试用例
    handleSelectionChange(val) {
      this.multipleSelection = val
      this.testcaseList = []
      this.multipleSelection.forEach(item => {
        this.testcaseList.push(item.id.toString())
      })
    },
    // 打开测试用例运行页面
    handleRunCase() {
      if (this.testcaseList.length > 0) {
        if (this.testcaseList.length > 1) {
          this.$message.error('只能选择一条用例')
        } else {
          this.runReportVisible = true
          this.$nextTick(function() {
            this.$refs.runReportFormValid.resetFields()
          })
          // 获取环境信息
          fetchEnvList({ envName: '' }).then(res => {
            this.runReportForm.supportEnv = res.desc
          })
          // 获取支持运行的流程链路列表
          getCustomFlows({ testcaseId: this.testcaseList[0] }).then(res => {
            this.runReportForm.flowList = res.flowList
          })
          // 临时公共变量处理
          this.debugPubVar = false
          this.temporaryVariables = []
          queryPubVarsByTcList({ testcaseMainList: this.testcaseList }).then(resp => {
            this.pubVariaTabledata = resp.pubVariablesList
            if (this.pubVariaTabledata.length > 0) {
              this.debugPubVar = true
            }
            resp.pubVariablesList.forEach(item => {
              this.temporaryVariables.push({
                pvId: item.id,
                name: item.name,
                tmpValue: '',
                type: item.type,
                optionValue: ''
              })
            })
          })
        }
      } else {
        this.$message.error('请选择要运行的测试用例')
      }
    },
    handleClose(done) {
      this.$confirm('关闭后子用例的信息将不会保存，确认关闭？')
        .then(_ => {
          done()
        })
        .catch(_ => {})
    },
    // 运行测试用例
    RunCase(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          run({
            projectId: this.caseTable.projectId,
            env: this.runReportForm.envName,
            testcaseMainList: this.testcaseList,
            pubVariableChanges: this.temporaryVariables // run接口新增参数，临时公共变量列表
          }).then(res => {
            this.runReportVisible = false
            this.reportId = res.reportId
            let totalProgress = res.totalProgress
            run({
              projectId: this.caseTable.projectId,
              env: this.runReportForm.envName,
              testcaseMainList: this.testcaseList,
              reportId: this.reportId,
              customFlowId: this.runReportForm.flowId, // 选择的流程链路Id
              pubVariableChanges: this.temporaryVariables // run接口新增参数，临时公共变量列表
            }).then(res => {
              const { href } = this.$router.resolve({
                name: 'realTimeLog',
                query: {
                  reportId: this.reportId,
                  totalProgress: totalProgress
                }
              })
              window.open(href, '_blank')
            })
          })
        }
      })
    },
    // 添加独立后置操作支持的函数类型
    selectCustomTeardownHooks() {
      this.caseTeardownForm.caseTeardownFuncParam = []
      let caseTeardownFuncType = this.caseTeardownForm.caseTeardownFuncType
      const caseTeardownFuncs = this.caseTeardownForm.supportTeardownFuncs.find(function(x) {
        return x.name === caseTeardownFuncType
      })
      caseTeardownFuncs.parameters.forEach(i => {
        this.caseTeardownForm.caseTeardownFuncParam.push({ label: i, value: '' })
      })
    },
    // 保存独立后置操作函数到列表中
    saveCaseTeardownForm(idx) {
      this.caseTeardownForm.caseTeardownFormVisible = false
      let caseTeardownFuncParam = ''
      let caseTeardownFuncParams = {}
      if (this.caseTeardownForm.caseTeardownFuncParam.length !== 0) {
        this.caseTeardownForm.caseTeardownFuncParam.forEach(i => {
          caseTeardownFuncParam = caseTeardownFuncParam
            ? caseTeardownFuncParam + '||' + i.label + '=' + i.value.replace(/[\r\n]/g, '').trim()
            : i.label + '=' + i.value.replace(/[\r\n]/g, '').trim()
          caseTeardownFuncParams[i.label] = i.value.replace(/[\r\n]/g, '').trim()
        })
      }
      let caseTeardownFuncType = ''
      this.caseTeardownForm.supportTeardownFuncs.forEach(i => {
        if (i.name === this.caseTeardownForm.caseTeardownFuncType) {
          caseTeardownFuncType = i.description
        }
      })
      // idx为-1 表示新增；非-1 表示编辑
      if (idx === -1) {
        // 用于列表展示数据
        this.caseTeardownForm.caseTeardownFormDataForView.push({
          caseTeardownFuncType: caseTeardownFuncType,
          caseTeardownFuncParam: caseTeardownFuncParam || '无'
        })
        // 用于提交接口数据
        this.caseTeardownForm.caseTeardownFormData.push({
          name: this.caseTeardownForm.caseTeardownFuncType,
          args: caseTeardownFuncParams,
          desc: caseTeardownFuncType
        })
      } else {
        // 用于列表展示数据
        this.$set(this.caseTeardownForm.caseTeardownFormDataForView, idx, {
          caseTeardownFuncType: caseTeardownFuncType,
          caseTeardownFuncParam: caseTeardownFuncParam || '无'
        })
        // 用于提交接口数据
        this.$set(this.caseTeardownForm.caseTeardownFormData, idx, {
          name: this.caseTeardownForm.caseTeardownFuncType,
          args: caseTeardownFuncParams,
          desc: caseTeardownFuncType
        })
      }
      // 保存后重置表单
      this.resetCaseTeardownForm()
    },
    // 重置独立后置操作配置表单内容
    resetCaseTeardownForm() {
      this.resetForm('caseTeardownForm')
      this.caseTeardownForm.caseTeardownFuncParam = []
      this.caseTeardownForm.caseTeardownFuncType = ''
      this.caseTeardownForm.idx = -1
    },
    // 修改独立后置操作列表中的某条数据
    handleCaseTeardownFormEdit(index, row) {
      this.caseTeardownForm.idx = index
      this.caseTeardownForm.caseTeardownFormVisible = true
      let e = this.caseTeardownForm.caseTeardownFormDataForView[index]
      let caseTeardownFuncType = ''
      this.caseTeardownForm.supportTeardownFuncs.forEach(i => {
        if (i.description === e.caseTeardownFuncType) {
          caseTeardownFuncType = i.name
        }
      })
      this.caseTeardownForm.caseTeardownFuncType = caseTeardownFuncType
      let caseTeardownFuncParams = []
      e.caseTeardownFuncParam.split('||').forEach(i => {
        caseTeardownFuncParams.push({
          label: i.split('=')[0],
          value: i.slice(i.indexOf('=') + 1)
        })
      })
      this.caseTeardownForm.caseTeardownFuncParam = caseTeardownFuncParams
    },
    // 上移
    handMoveUpTeardown(index, row) {
      let objMoveView = this.caseTeardownForm.caseTeardownFormDataForView[index]
      let objMove = this.caseTeardownForm.caseTeardownFormData[index]
      this.caseTeardownForm.caseTeardownFormDataForView.splice(index, 1)
      this.caseTeardownForm.caseTeardownFormData.splice(index, 1)
      this.caseTeardownForm.caseTeardownFormDataForView.splice(index - 1, 0, objMoveView)
      this.caseTeardownForm.caseTeardownFormData.splice(index - 1, 0, objMove)
    },
    // 下移
    handMoveDownTeardown(index, row) {
      let objMoveView = this.caseTeardownForm.caseTeardownFormDataForView[index]
      let objMove = this.caseTeardownForm.caseTeardownFormData[index]
      this.caseTeardownForm.caseTeardownFormDataForView.splice(index, 1)
      this.caseTeardownForm.caseTeardownFormData.splice(index, 1)
      this.caseTeardownForm.caseTeardownFormDataForView.splice(index + 1, 0, objMoveView)
      this.caseTeardownForm.caseTeardownFormData.splice(index + 1, 0, objMove)
    },
    // 删除独立后置操作列表中的一行数据
    handleCaseTeardownFormDel(index, row) {
      this.caseTeardownForm.caseTeardownFormDataForView.splice(index, 1)
      this.caseTeardownForm.caseTeardownFormData.splice(index, 1)
    },
    // 查看子用例关联的主用例列表
    viewRelatedMainCase() {
      this.drawer = true
      this.gridData = []
      getRelatedMainCaseBySubCaseId({ subId: this.subCaseId }).then(res => {
        this.gridData = res.data
      })
    },
    // 查询该用例被前置的用例列表
    viewSetupCase(index, row) {
      this.drawerForSteupCase = true
      queryListBySetupCase({ testcaseMainId: row.id }).then(res => {
        this.gridDataForSteupCase = res.dataList
      })
    },
    // 清理缓存
    clearCache() {
      this.gridDataForSteupCase = []
    },
    // 设置可运行链路（点击按钮）
    setFlowConfig(index, row) {
      this.flowConfigVisible = true
      this.$nextTick(function() {
        this.resetFlowConfigForm()
      })
      this.fullLineTestCaseId = row.id
      queryFullLineCaseDetail({ testcaseId: row.id }).then(res => {
        if (res.data.steps) {
          this.flowConfigForm.subCaseList = []
          res.data.steps.forEach(item => {
            this.flowConfigForm.subCaseList.push({
              value: item.base.subId,
              label: item.base.intfName + '（' + item.base.subName + '）'
            })
          })
        }
      })
      getCustomFlows({ testcaseId: row.id }).then(res => {
        this.flowConfigForm.tableData = res.flowList
      })
    },
    // 保存可运行链路配置到表格中
    saveFlowConfigForm(idx) {
      this.$refs.flowConfigForm.validate(valid => {
        if (valid) {
          let flowIndexlist = []
          this.flowConfigForm.selectedItem.forEach(item => {
            flowIndexlist.push(this.flowConfigForm.subCaseList.findIndex(c => c.value === item))
          })
          if (idx === -1) {
            // 新增逻辑
            this.flowConfigForm.tableData.push({
              flowId: null,
              flowName: this.flowConfigForm.flowName,
              flowIndexList: flowIndexlist.sort(sortNumber)
            })
          } else {
            // 修改逻辑
            this.$set(this.flowConfigForm.tableData, idx, {
              flowId: null,
              flowName: this.flowConfigForm.flowName,
              flowIndexList: flowIndexlist.sort(sortNumber)
            })
          }
          this.resetFlowConfigForm()
        }
      })
    },
    // 重置可运行链路配置表单
    resetFlowConfigForm() {
      this.$refs.flowConfigForm.resetFields()
    },
    // 编辑可运行链路表格中一条记录
    handleFlowConfigEdit(index, row) {
      this.flowConfigForm.idx = index
      this.resetFlowConfigForm()
      this.flowConfigForm.flowName = row.flowName
      row.flowIndexList.forEach(item => {
        this.flowConfigForm.selectedItem.push(this.flowConfigForm.subCaseList[item].value)
      })
    },
    // 删除可运行链路表格中一条记录
    handleFlowConfigDel(index, rows) {
      rows.splice(index, 1)
    },
    // 保存可运行链路
    saveFlowConfig() {
      if (this.flowConfigForm.tableData.length === 0) {
        this.$message.warning('没有可保存的流程链路信息')
      } else {
        saveCustomFlows({
          testcaseId: this.fullLineTestCaseId,
          flowList: this.flowConfigForm.tableData
        }).then(res => {
          this.flowConfigVisible = false
          this.$message.success(res.desc)
        })
      }
    }
  },
  watch: {
    filterText(val) {
      this.$refs.tree.filter(val)
    },
    handleSwitch(val) {
      if (val === 1) {
        this.$nextTick(() => {
          this.$refs.fullLineCase.handleClear()
          this.$refs.intfSubCase.handleClear()
          let obj = {}
          obj.stopPropagation = () => {}
          this.$refs.fullLineSubCase.handleClearClick(obj)
        })
      } else if (val === 2) {
        this.$nextTick(() => {
          this.$refs.intfSubCase.handleClear()
          this.$refs.fullLineCase.handleClear()
          let obj = {}
          obj.stopPropagation = () => {}
          this.$refs.fullLineSubCase.handleClearClick(obj)
        })
      }
    },
    'caseTable.id': function(newValue) {
      if (newValue) {
        this.produceLineProp.show = true
        this.queryTestCases()
      } else {
        this.produceLineProp.show = false
      }
    },
    addCaseVisible: function(newValue) {
      if (newValue === true) {
        this.handleAddCase()
        this.addCase(false)
      }
    }
  }
}
</script>

<style lang="scss">
.el-table .warning-row {
  background: oldlace;
}

/* 用例编辑页面各元素样式 */

.fullLineCaseEditDialog .el-dialog__body {
  padding: 10px 20px;
}

.box-card {
  margin-bottom: 10px;
}

.fullLineCaseBasic .el-card__header {
  padding: 5px 10px;
}

.fullLineCaseBasic .el-card__body {
  padding: 5px;
}

.el-card__body .el-form .el-form-item--mini.el-form-item,
.el-card__body .el-form-item--small.el-form-item,
.el-collapse-item__content .el-form.el-form-item--mini.el-form-item,
.el-collapse-item__content .el-form .el-form-item--small.el-form-item {
  margin-bottom: 15px;
}

.header-icon {
  color: #409eff;
}

/* .example-editTree {
     padding: 10px;
     height: 100%;
     min-height: 720px;
     max-height: 720px;
     box-shadow: 0 1px 12px 3px rgba(0, 0, 0, .1);
   }*/

.table_container {
  padding: 10px;
}

.navigation-filter {
  padding: 6px 23px;
}

.el-input--medium .el-input__inner {
  height: 36px;
  line-height: 36px;
  width: 400px;
}

.category {
  margin-bottom: 20px;
}

.fullLineCaseEditDialog .el-select .el-tag {
  max-width: 120px !important;
  overflow: hidden;
  white-space: nowrap;
}

.fullLineCaseEditDialog {
  .el-dialog .el-dialog__header {
    padding: 10px 20px 0 20px;
  }
  .el-dialog .el-dialog__footer {
    padding: 0 20px 10px 20px;
  }
  /*display: flex;
    justify-content: center;
    align-items: center;
    overflow: hidden;
    .el-dialog {
      margin: 0 auto !important;
      height: 90%;
      overflow: hidden;
      overflow-y: auto;
      .el-dialog__header {
        padding: 10px 20px 0 20px;
      }
      .el-dialog__body {
        !*position: absolute;*!
        left: 0;
        top: 0;
        bottom: 0;
        right: 0;
        padding: 0;
        z-index: 1;
        overflow: hidden;
        overflow-y: auto;
      }
    }*/
  .el-divider--horizontal {
    display: block;
    height: 1px;
    width: 100%;
    margin: 10px 0 10px 0;
  }
  .fullLineCaseEditScrolllist {
    max-height: 700px;
  }
  .fullLineCaseBasic {
    border: 1px solid #ebebeb;
    height: 700px;
    border-radius: 3px;
    transition: 0.2s;
    margin: 0 10px 0 5px;
    .source {
      padding: 15px;
    }
    .text-header {
      color: #409eff;
      font-size: 14px;
    }
  }
  .caseSteps {
    border: 1px solid #ebebeb;
    height: 500px;
    margin-bottom: 10px;
    border-radius: 3px;
    transition: 0.2s;
    .source {
      padding: 15px;
    }
    .el-tree-node__content > .el-tree-node__expand-icon {
      padding: 0;
    }
  }
  .fullLineCaseBasicForm {
    margin: 10px;
  }
  /*.el-tree-node__content>.el-tree-node__expand-icon {
      padding: 2px;
    }
    .el-tree-node__expand-icon.expanded {
      -webkit-transform: rotate(0deg);
      transform: rotate(0deg);
    }
   .el-icon-caret-right:before {
      content: "";
      font-size: 18px;
    }
   .el-tree-node__expand-icon.expanded.el-icon-caret-right:before {
      content: "";
      font-size: 18px;
    }*/
}

.demo-drawer__content {
  display: flex;
  flex-direction: column;
  height: 100%;
  .subCaseEditForm {
    max-height: 800px;
  }
}

.flowConfigForm .el-input {
  width: 80%;
}

.flowConfigForm .el-select {
  width: 70%;
}

.flowConfigDialog .el-select .el-tag {
  max-width: 400px !important;
  overflow: hidden;
  white-space: nowrap;
}

.full-line .el-table__header tr,
.el-table__header th {
  padding: 0;
  height: 40px;
}

.full-line .el-table__body tr,
.el-table__body td {
  padding: 5px 0;
  height: 50px;
}
</style>
