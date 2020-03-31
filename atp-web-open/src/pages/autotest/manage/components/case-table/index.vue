<template>
  <div class="fillcontain">
    <el-form :model="interfaceProp" class="case-table" size="mini" v-show="interfaceProp.show" ref="interfaceProp">
      <el-form class="case-table-expand" v-if="interfaceProp.type === 'HTTP'" labelWidth="90px">
        <el-row>
          <el-col :span="8">
            <el-form-item label="中文名：">
              <el-scrollbar wrap-class="caseTabelScrolllist" view-class="view-box" :native="false">
                <span class="text">{{ interfaceProp.intfChineseName }}</span>
              </el-scrollbar>
            </el-form-item>
          </el-col>
          <el-col :span="10">
            <el-form-item label="接口uri：">
              <el-scrollbar wrap-class="caseTabelScrolllist" view-class="view-box" :native="false">
                <span class="text">{{ interfaceProp.apiUrl }}</span>
              </el-scrollbar>
            </el-form-item>
          </el-col>
          <el-col :span="3">
            <el-form-item label="接口类型：">
              <span class="text">{{ interfaceProp.type }}</span>
            </el-form-item>
          </el-col>
          <el-col :span="3">
            <el-form-item label="请求方法：">
              <span class="text">{{ interfaceProp.method }}</span>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-form-item label="接口头域：">
            <el-scrollbar wrap-class="caseTabelScrolllist" view-class="view-box" :native="false">
              <span class="text">{{ interfaceProp.headers }}</span>
            </el-scrollbar>
          </el-form-item>
        </el-row>
      </el-form>
      <el-form class="case-table-expand" v-if="interfaceProp.type === 'DUBBO'">
        <el-row>
          <el-col :span="8">
            <el-form-item label="中文名：">
              <el-scrollbar wrap-class="caseTabelScrolllist" view-class="view-box" :native="false">
                <span class="text">{{ interfaceProp.intfChineseName }}</span>
              </el-scrollbar>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="服务名：">
              <el-scrollbar wrap-class="caseTabelScrolllist" view-class="view-box" :native="false">
                <span class="text">{{ interfaceProp.dubboService }}</span>
              </el-scrollbar>
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="接口类型：">
              <span class="text">{{ interfaceProp.type }}</span>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="8">
            <el-form-item label="方法名：">
              <el-scrollbar wrap-class="caseTabelScrolllist" view-class="view-box" :native="false">
                <span class="text">{{ interfaceProp.dubboMethod }}</span>
              </el-scrollbar>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="参数类型：">
              <el-scrollbar wrap-class="caseTabelScrolllist" view-class="view-box" :native="false">
                <span class="text">{{ interfaceProp.parameterTypes }}</span>
              </el-scrollbar>
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="接口版本：">
              <span class="text">{{ interfaceProp.version }}</span>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <el-form class="case-table-expand" v-if="interfaceProp.type === 'MQ'">
        <el-row>
          <el-col :span="6">
            <el-form-item label="中文名：">
              <el-scrollbar wrap-class="caseTabelScrolllist" view-class="view-box" :native="false">
                <span class="text">{{ interfaceProp.intfChineseName }}</span>
              </el-scrollbar>
            </el-form-item>
          </el-col>
          <el-col :span="3">
            <el-form-item label="接口类型：">
              <span class="text">{{ interfaceProp.type }}</span>
            </el-form-item>
          </el-col>
          <el-col :span="7">
            <el-form-item label="topic：">
              <el-scrollbar wrap-class="caseTabelScrolllist" view-class="view-box" :native="false">
                <span class="text">{{ interfaceProp.topic }}</span>
              </el-scrollbar>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="tag：">
              <el-scrollbar wrap-class="caseTabelScrolllist" view-class="view-box" :native="false">
                <span class="text">{{ interfaceProp.tag }}</span>
              </el-scrollbar>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <el-table
        :data="tableData"
        style="width: 100%;margin-top: 15px"
        ref="multipleTable"
        :row-class-name="tableRowClassName"
        :header-cell-style="{color:'black',background:'#eef1f6'}"
        @selection-change="handleSelectionChange"
        height="560"
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
          label="运行状态"
          align="center"
          width="90"
          :filters="[{ text: '成功', value: '成功' }, { text: '失败', value: '失败' }, { text: '未运行', value: '未运行' }]"
          :filter-method="filterLastRun"
          filter-placement="bottom-end"
        >
          <template slot-scope="scope">
            <el-popover trigger="hover" placement="top">
              <span style="font-size: 12px">点击 - 刷新运行结果</span>
              <p style="font-size: 12px">运行结果: {{ scope.row.last_run }}</p>
              <p style="font-size: 12px">运行时间: {{ scope.row.lastRunTime }}</p>
              <div slot="reference" class="name-wrapper">
                <el-tag
                  size="mini"
                  effect="dark"
                  :type="scope.row.last_run === '成功' ? 'success' : (scope.row.last_run === '失败' ? 'danger':'info')"
                  style="cursor: pointer;"
                  @click="getTestCaseListByIntfId(intfId, currentPage, pageSize)"
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
                <el-popover placement="left" width="100%" trigger="click">
                  <el-table :data="testcaseChainData" max-height="750">
                    <el-table-column width="90" property="chain_no" label="调用顺序"></el-table-column>
                    <el-table-column width="60" property="preCaseId" label="用例ID"></el-table-column>
                    <el-table-column width="300" property="preCaseName" label="用例标题"></el-table-column>
                    <el-table-column width="100" property="preCaseType" label="用例类型"></el-table-column>
                    <el-table-column width="350" property="preIntfName" label="所属接口"></el-table-column>
                    <el-table-column width="200" property="preSystemName" label="所属工程"></el-table-column>
                    <el-table-column width="200" property="extract_v_names" label="提取的用例变量"></el-table-column>
                    <el-table-column width="200" property="public_v_names" label="用到的公共变量"></el-table-column>
                  </el-table>
                  <el-dropdown-item @click.native="handleQueryChain(scope.$index, scope.row)" slot="reference">查看调用链</el-dropdown-item>
                </el-popover>
                <el-dropdown-item @click.native="viewSetupCase(scope.$index, scope.row)">查看关联用例</el-dropdown-item>
                <!--<el-dropdown-item @click.native="addTag(scope.$index, scope.row)">设置标签</el-dropdown-item>-->
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
          :page-size="pageSize"
        ></el-pagination>
      </div>
      <div style="text-align: center; margin-top: 5px">
        <el-button style="float: inherit" size="small" type="primary" icon="el-icon-caret-right" @click="handleRunCase()">执行用例</el-button>
      </div>
    </el-form>

    <!--弹框显示被前置的用例列表-->
    <el-dialog title="关联的用例列表（前置了本用例）" :visible.sync="drawer" width="75%" @close="clearCache">
      <el-table :data="gridData" height="600" :header-cell-style="{color:'black',background:'#eef1f6'}">
        <el-table-column prop="id" label="用例编号" width="80"></el-table-column>
        <el-table-column prop="testcaseName" label="用例标题" width="400"></el-table-column>
        <el-table-column prop="intfName" label="接口URL" width="400"></el-table-column>
        <el-table-column label="用例标签" width="150">
          <template slot-scope="scope">
            <el-tag :key="tag" v-for="tag in gridData[scope.$index].tags_name" :disable-transitions="false" size="mini">{{tag}}</el-tag>
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
                  :type="scope.row.status === '启用中' ? 'primary' : 'danger'"
                  @click="handleUpdateStatus(scope.$index, scope.row)"
                >{{scope.row.status}}</el-tag>
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
                  @click="getTestCaseListByIntfId(intfId, currentPage, pageSize)"
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

    <!--执行测试报告选择环境页面-->
    <el-dialog title="运行测试" :visible.sync="runReportVisible" width="45%">
      <el-form ref="runReportFormValid" :model="runReportForm" label-width="100px">
        <el-form-item label="运行环境" prop="envName" :rules="[{ required: true, message: '环境必选', trigger: 'change' }]">
          <el-select v-model="runReportForm.envName" placeholder="请选择">
            <el-option v-for="item in runReportForm.supportEnv" :key="item.id" :label="item.envName" :value="item.envName"></el-option>
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

    <!-- 新版：新增编辑测试用例弹出框  -->
    <el-dialog
      title="配置接口用例"
      :visible.sync="caseEditVisible"
      width="70%"
      center
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      top="2vh"
      ref="caseEditDialog"
      class="caseEditDialog"
    >
      <el-divider></el-divider>
      <el-row :gutter="5">
        <el-col :span="17">
          <el-scrollbar wrap-class="caseEditScrolllist" view-class="view-box" :native="false">
            <div class="intfCaseBasic">
              <el-card>
                <div slot="header" style="background: #EBEEF5;">
                  <span class="text-header">前置执行用例</span>
                  <el-tooltip placement="top" content="添加" effect="light">
                    <el-button type="primary" size="mini" style="margin-left: 20px" icon="el-icon-plus" plain @click="clickSetupCaseBtn"></el-button>
                  </el-tooltip>
                  <el-popover placement="left" width="100%" trigger="click" class="popover">
                    <el-table :data="testcaseChainData" max-height="750">
                      <el-table-column width="90" property="chain_no" label="调用顺序"></el-table-column>
                      <el-table-column width="60" property="preCaseId" label="用例ID"></el-table-column>
                      <el-table-column width="300" property="preCaseName" label="用例标题"></el-table-column>
                      <el-table-column width="100" property="preCaseType" label="用例类型"></el-table-column>
                      <el-table-column width="350" property="preIntfName" label="所属接口"></el-table-column>
                      <el-table-column width="200" property="preSystemName" label="所属工程"></el-table-column>
                      <el-table-column width="200" property="extract_v_names" label="提取的用例变量"></el-table-column>
                      <el-table-column width="200" property="public_v_names" label="用到的公共变量"></el-table-column>
                    </el-table>
                    <el-button type="text" style="margin-left: 20px;" slot="reference" @click="viewChain">查看前置链路</el-button>
                  </el-popover>
                </div>
                <div>
                  <el-form :model="preExeForm" v-if="preExeForm.preExeFormVisible" ref="preExeForm">
                    <el-form-item label="前置用例类型" prop="preExeType">
                      <el-radio-group v-model="preExeForm.preExeType">
                        <el-radio :label="1">前置接口用例</el-radio>
                        <el-radio :label="2">前置全链路用例</el-radio>
                      </el-radio-group>
                    </el-form-item>
                    <el-form-item label="选择全链路用例" prop="selectedFullLinkOptions" v-if="preExeForm.preExeType === 2">
                      <el-cascader
                        placeholder="请在此选择全链路用例，可输入关键字搜索"
                        :options="preExeForm.preExeSetupFullLinkOptions"
                        filterable
                        clearable
                        @change="selectFLL"
                        size="small"
                      ></el-cascader>
                    </el-form-item>
                    <el-form-item label="选择接口用例" prop="selectedIntfCaseOptions" v-if="preExeForm.preExeType === 1">
                      <el-cascader
                        placeholder="请在此选择接口用例，可输入关键字搜索"
                        :options="preExeForm.preExeSetupCaseOptions"
                        filterable
                        clearable
                        @change="handleChangeSetupCase"
                        size="small"
                      ></el-cascader>
                    </el-form-item>
                  </el-form>
                  <!--前置全链路用例数据列表-->
                  <el-table
                    :data="preExeForm.preExeTableData"
                    border
                    lazy
                    style="width: 100%"
                    ref="multipleTable1"
                    v-if="preExeForm.preExeTableData.length !== 0"
                    :load="getSetupCase"
                    :tree-props="{children: 'children', hasChildren: 'hasChildren'}"
                    row-key="id"
                    max-height="500"
                  >
                    <el-table-column type="index"></el-table-column>
                    <el-table-column prop="preCaseType" label="前置用例类型" width="120"></el-table-column>
                    <el-table-column prop="preCaseId" label="前置用例ID" width="100"></el-table-column>
                    <el-table-column prop="preCaseName" label="前置用例名称"></el-table-column>
                    <el-table-column prop="preOthers" label="其他">
                      <template slot-scope="scope">
                        <span v-if="scope.row.preCaseType === '接口用例'">{{scope.row.preIntfName}}</span>
                        <span v-else>{{scope.row.customFlowName}}</span>
                      </template>
                    </el-table-column>
                    <el-table-column label="操作" fixed="right" width="120">
                      <template slot-scope="scope" v-if="scope.row.id < 100">
                        <el-button type="text" @click="handMoveUp(scope.$index, scope.row)" v-if="scope.$index !== 0">上移</el-button>
                        <el-button
                          type="text"
                          @click="handMoveDown(scope.$index, scope.row)"
                          v-if="scope.row.id !== preExeForm.preExeTableData.slice(preExeForm.preExeTableData.length-1)[0].id "
                        >下移</el-button>
                        <el-button type="text" @click="handSetFlow(scope.$index, scope.row)" v-if="scope.row.preCaseType === '全链路用例'">设置</el-button>
                        <el-button type="text" @click="handDeleteSetupCase(scope.$index, scope.row)">移除</el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
              </el-card>
              <div style="margin-top: 20px">
                <case-edit :test-case-info="testCaseInfo" ref="caseEdit" @update-data="updateData"></case-edit>
              </div>
            </div>
          </el-scrollbar>
        </el-col>
        <el-col :span="7">
          <el-scrollbar wrap-class="caseEditScrolllist" view-class="view-box" :native="false">
            <div class="intfCaseBasic">
              <span style="color: red;margin-left: 20px;font-style: italic">用例标题自动生成，拼接方式：{用例场景}_{预期结果}</span>
              <el-form ref="caseBasicForm" class="intfCaseBasicForm" :model="caseBasicForm" label-position="right" label-width="80px">
                <el-form-item
                  label="用例场景"
                  prop="caseName"
                  :rules="[{ required: true, message: '用例场景必填', trigger: 'blur' },{ max: 100, message: '长度最多100 个字符', trigger: 'blur' }]"
                >
                  <el-input
                    type="textarea"
                    v-model="caseBasicForm.caseName"
                    placeholder="请输入用例场景"
                    maxlength="100"
                    :autosize="{ minRows: 6, maxRows: 6}"
                    show-word-limit
                  ></el-input>
                </el-form-item>
                <el-form-item
                  label="预期结果"
                  prop="caseExpectResult"
                  :rules="[{ required: true, message: '预期结果必填', trigger: 'blur' },{ max: 100, message: '长度最多100 个字符', trigger: 'blur' }]"
                >
                  <el-input
                    type="textarea"
                    v-model="caseBasicForm.caseExpectResult"
                    placeholder="请输入预期结果"
                    maxlength="100"
                    :autosize="{ minRows: 6, maxRows: 6}"
                    show-word-limit
                  ></el-input>
                </el-form-item>
                <el-form-item label="用例描述" prop="caseDesc" :rules="[{ max: 1000, message: '长度最多1000 个字符', trigger: 'blur' }]">
                  <el-input
                    type="textarea"
                    v-model="caseBasicForm.caseDesc"
                    placeholder="请输入用例描述"
                    maxlength="1000"
                    :autosize="{ minRows: 6, maxRows: 6}"
                    show-word-limit
                  ></el-input>
                </el-form-item>
                <el-form-item
                  :label="item.label"
                  :prop="'tagOptions.' + index + '.value'"
                  v-for="(item,index) in caseBasicForm.tagOptions"
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
        <el-button type="primary" @click="getMyEvent">保存接口用例</el-button>
      </span>
    </el-dialog>

    <!--设置前置全链路运行链路弹框-->
    <el-dialog title="设置流程链路" :visible.sync="setFlowVisible" width="300px" center>
      <el-select v-model="setFlowForm.flowId" clearable placeholder="请选择">
        <el-option v-for="(item, index) in setFlowForm.flowList" :key="index" :label="item.flowName" :value="item.flowId"></el-option>
      </el-select>
      <span slot="footer" class="dialog-footer">
        <el-button type="primary" @click="setFlow(setFlowForm.idx)">保 存</el-button>
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
    <el-dialog title="复制用例/结构" :visible.sync="copyVisible" width="20%" center>
      <template>
        <div>
          <el-radio-group v-model="copyCaseRadio">
            <el-radio-button label="1">仅复制本用例数据</el-radio-button>
            <el-radio-button label="2">复制用例</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <el-input-number v-model="copynum" @change="handleChange" :min="1" :max="10" style="margin-top: 5px" v-if="copyCaseRadio==='2'"></el-input-number>
      <el-input v-if="copyCaseRadio==='1'" v-model="copyiedCaseId" placeholder="用例id列表，逗号隔开" style="width: 260px;margin-top: 5px"></el-input>
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
  </div>
</template>

<script>
import {
  addTestCase,
  editTestCase,
  deleteTestCase,
  changeTestCaseStatus,
  queryTestCaseChain,
  queryTestCaseDetail,
  copyTestCase,
  copyTestCaseData,
  setTags,
  queryCaseByIntfId,
  queryListBySetupCase
} from '@/api/autotest/manage/testcase-apiManage/config'
import { getCustomFlows } from '@/api/autotest/manage/fullLineCase/testcase-config'
import { subtreeIntfCase, subtreeProductLine } from '@/api/autotest/manage/resource-apiManage/company'
import { queryTagList } from '@/api/autotest/manage/testcase-apiManage/support'
import { queryApiDetail } from '@/api/autotest/manage/resource-apiManage/api'
import { run } from '@/api/autotest/manage/testcase-apiManage/run'
import { fetchEnvList } from '@/api/autotest/manage/resource-envManage'
import { queryPubVarsByTcList } from '@/api/autotest/manage/resource-publicVariable'
import { isJsonString } from '@/libs/common'

export default {
  name: 'caseTable',
  components: {
    'case-edit': () => import('../case-edit')
  },
  // 父组件通过props属性传递进来的数据,包括intfInfo
  props: {
    intfInfo: {
      type: Object,
      default: () => {
        return null
      }
    }
  },
  data() {
    var headersValidatePass = (rule, value, callback) => {
      if (!isJsonString(value)) {
        callback(new Error('非法json格式'))
      } else {
        callback()
      }
    }
    return {
      caseBasicForm: {
        caseName: '',
        caseExpectResult: '',
        caseDesc: '',
        tagOptions: []
      },
      preExeForm: {
        // 前置执行用例模块数据模型
        preExeFormVisible: false, // 前置执行用例添加表单是否显示
        preExeSetupCaseOptions: [], // 保存查询的接口用例数据
        preExeSetupFullLinkOptions: [], // 保存查询的全链路用例数据
        preExeTableData: [], // 前置执行用例表格数据
        preExeType: 1, // 前置执行用例类型，1代表接口用例，2代表全链路用例
        //                    setupCaseChainData: [],  // 保存前置 接口用例的调用链 数据
        oid: 1, // 原始id，无业务含义
        preCaseName: '' // 前置用例名称
      },
      intfInfoTmp: null, // 缓存父组件传递过过来的接口信息
      testCaseInfo: null, // 传递给子组件的测试用例信息
      nodeKeys: [],
      intfId: null,
      interfaceProp: {
        show: false,
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
      tableData: [],
      currentPage: 1, // 测试用例列表当前所处页
      pageSize: 10, // 测试用例列表每页数量
      totalCount: 10, // 测试用例列表记录数
      radio: '1',
      copyCaseRadio: '2',
      idx: -1,
      testcaseId: '',
      delVisible: false,
      copyVisible: false,
      copynum: '1', // 复制用例默认值
      copyiedCaseId: '', // 复制哪个用例的结构
      caseEditVisible: false,
      activeNamesPre: ['1'], // 独立前置操作面板
      multipleSelection: [],
      testcaseList: [],
      reportId: '',
      reportUrl: '',
      reportGeneratedStatus: false,
      timer: '',
      runReportVisible: false,
      runReportForm: {
        envName: '',
        supportEnv: []
      },
      pubVariaTabledata: [], // 临时公共变量tabledata
      temporaryVariables: [], // 更改公共变量后，run接口参数
      pubVariableChanges: [],
      testcaseChainData: [], // 用例调用链数据
      chainVisible: false,
      debugPubVar: false,
      rules: {
        requestInfo: [{ required: true, validator: headersValidatePass, trigger: 'blur' }],
        signFunc: [{ required: true, message: '加签函数必填', trigger: 'blur' }]
      },
      addTagVisible: false,
      tagForm: {
        tagOptions: [],
        addTagcaseId: ''
      },
      flag: false, // 标记字段，如果为true，则代表用例编辑页面点击保存操作
      drawer: false, // 抽屉组件关联用例列表是否显示
      gridData: [], // 子用例关联的主用例数据
      setFlowVisible: false, // 设置前置全链路用例的流程链路弹框是否显示
      setFlowForm: {
        // 前置全链路用例的流程链路弹框表单信息
        flowId: null,
        flowList: [],
        idx: -1
      }
    }
  },
  mounted() {
    // 获取用例标签列表
    this.queryTagList()
    this.pageLoad(this.intfInfo)
  },
  methods: {
    // 页面初始化
    pageLoad(obj) {
      this.intfInfoTmp = null
      this.intfInfoTmp = obj
    },
    // 获取前置用例可选择options
    subtreeSetupCase() {
      subtreeIntfCase({ companyId: this.intfInfoTmp.companyId }).then(res => {
        this.preExeForm.preExeSetupCaseOptions = res.data
      })
    },
    // 获取前置全链路用例可选择options
    queryFullLineList() {
      subtreeProductLine({ companyId: this.intfInfoTmp.companyId }).then(res => {
        this.traversalObject(res.data)
        this.preExeForm.preExeSetupFullLinkOptions = res.data
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
    // 选择前置全链路触发的事件
    selectFLL(val) {
      if (val.length !== 0) {
        this.findName(this.preExeForm.preExeSetupFullLinkOptions, val)
        this.preExeForm.oid = this.preExeForm.preExeTableData.length + 1
        this.preExeForm.preExeTableData.push({
          id: this.preExeForm.oid,
          preCaseType: '全链路用例',
          preCaseId: val[val.length - 1],
          preCaseName: this.preExeForm.preCaseName
        })
        this.preExeForm.oid += 1
      }
      //                console.log('前置用例列表', this.preExeForm.preExeTableData)
    },
    findName(obj, val) {
      obj.some(item => {
        if (item.children === undefined && item.value === val[val.length - 1]) {
          this.preExeForm.preCaseName = item.label
          return true
        } else if (item.children !== undefined) {
          return this.findName(item.children, val)
        }
      })
    },
    // 根据用例id查询前置用例列表
    getSetupCaseListByCaseId(caseId) {
      return new Promise((resolve, reject) => {
        queryTestCaseChain({ testcaseId: caseId }).then(res => {
          resolve(res.data)
        })
      })
    },
    // 选择前置接口用例触发的事件
    handleChangeSetupCase(val) {
      if (val.length === 0) {
        return false
      }
      let itemSystem = this.preExeForm.preExeSetupCaseOptions.find(c => c.value === val[0])
      let itemIntf = itemSystem['children'].find(c => c.value === val[1])
      let itemCase = itemIntf['children'].find(c => c.value === val[2])
      this.preExeForm.oid = this.preExeForm.preExeTableData.length + 1
      this.getSetupCaseListByCaseId(val[2]).then(res => {
        if (res.find(c => c.preCaseId === this.testcaseId)) {
          this.$message.warning('无法将用例本身作为前置用例，将导致执行死循环')
          return false
        }
        if (res.length > 1) {
          this.$confirm('引入的用例存在前置, 是否保留前置?', '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
            center: true,
            showClose: false
          })
            .then(() => {
              let tempId = this.preExeForm.oid * 100 + 1
              res.slice(0, res.length - 1).forEach(item => {
                item['id'] = tempId
                tempId += 1
              })
              this.preExeForm.preExeTableData.push({
                id: this.preExeForm.oid,
                preCaseType: '接口用例',
                preCaseId: val[2],
                preCaseName: itemCase.label.slice(itemCase.label.indexOf('_') + 1),
                preIntfName: itemIntf.label,
                children: [],
                extract_v_names: res[res.length - 1].extract_v_names,
                hasChildren: true
              })
              this.preExeForm.oid += 1
            })
            .catch(() => {
              this.preExeForm.preExeTableData.push({
                id: this.preExeForm.oid,
                preCaseType: '接口用例',
                preCaseId: val[2],
                preCaseName: itemCase.label.slice(itemCase.label.indexOf('_') + 1),
                preIntfName: itemIntf.label,
                children: [],
                extract_v_names: res[res.length - 1].extract_v_names,
                hasChildren: false
              })
              this.preExeForm.oid += 1
            })
        } else {
          this.preExeForm.preExeTableData.push({
            id: this.preExeForm.oid,
            preCaseType: '接口用例',
            preCaseId: val[2],
            preCaseName: itemCase.label.slice(itemCase.label.indexOf('_') + 1),
            preIntfName: itemIntf.label,
            children: [],
            extract_v_names: res[res.length - 1].extract_v_names,
            hasChildren: false
          })
          this.preExeForm.oid += 1
        }
        console.log('前置用例列表', this.preExeForm.preExeTableData)
      })
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
    // 前置用例列表中上移操作
    handMoveUp(index, row) {
      let idx = this.preExeForm.preExeTableData.indexOf(row)
      this.preExeForm.preExeTableData.splice(idx, 1)
      this.preExeForm.preExeTableData.splice(idx - 1, 0, row)
    },
    // 前置用例列表中下移操作
    handMoveDown(index, row) {
      let idx = this.preExeForm.preExeTableData.indexOf(row)
      this.preExeForm.preExeTableData.splice(idx, 1)
      this.preExeForm.preExeTableData.splice(idx + 1, 0, row)
    },
    // 移除前置用例
    handDeleteSetupCase(index, row) {
      let idx = this.preExeForm.preExeTableData.indexOf(row)
      this.preExeForm.preExeTableData.splice(idx, 1)
    },
    getMyEvent() {
      this.$refs['caseBasicForm'].validate(valid => {
        if (valid) {
          this.flag = true
          this.$refs.caseEdit.saveTestCaseInfo()
        }
      })
    },
    updateData(caseInfo) {
      if (this.flag) {
        // console.log('子组件传给父组件', caseInfo)
        let setupCases = []
        for (let i = 0, len = this.preExeForm.preExeTableData.length; i < len; i++) {
          if (this.preExeForm.preExeTableData[i].preCaseType === '全链路用例') {
            setupCases.push({
              testcaseId: this.preExeForm.preExeTableData[i].preCaseId,
              caseType: this.preExeForm.preExeTableData[i].preCaseType,
              customFlowId: this.preExeForm.preExeTableData[i].customFlowId
            })
          } else {
            setupCases.push({
              testcaseId: this.preExeForm.preExeTableData[i].preCaseId,
              caseType: this.preExeForm.preExeTableData[i].preCaseType,
              hasChildren: this.preExeForm.preExeTableData[i].hasChildren
            })
          }
        }
        caseInfo['setupCases'] = setupCases
        caseInfo.base['intfId'] = this.intfId
        // 保存标签信息
        let tagIdList = []
        for (let i = 0, len = this.caseBasicForm.tagOptions.length; i < len; i++) {
          if (this.caseBasicForm.tagOptions[i].value) {
            tagIdList.push(this.caseBasicForm.tagOptions[i].value)
          }
        }
        caseInfo.base['tagIdList'] = tagIdList

        // 处理子用例详情中requestInfo
        let requestInfo = {}
        requestInfo['isMerge'] = caseInfo.steps[0].requestInfo.isMerge
        if (this.interfaceProp.type === 'HTTP') {
          requestInfo['json'] = JSON.parse(caseInfo.steps[0].requestInfo.json)
          requestInfo['type'] = 1
          if (caseInfo.steps[0].requestInfo.type === 2) {
            requestInfo['sign'] = caseInfo.steps[0].requestInfo.sign.name
          }
        } else if (this.interfaceProp.type === 'DUBBO') {
          requestInfo['args'] = JSON.parse(caseInfo.steps[0].requestInfo.json)
          requestInfo['type'] = 2
        } else if (this.interfaceProp.type === 'MQ') {
          requestInfo['msg'] = caseInfo.steps[0].requestInfo.json
          requestInfo['type'] = 3
        } else {
          alert('接口类型为定义')
        }
        caseInfo.steps[0].requestInfo = requestInfo
        // 更新用户标题等基本信息
        caseInfo.base['testcaseName'] = this.caseBasicForm.caseName.replace(/[\r\n]/g, '').trim()
        caseInfo.base['expectResult'] = this.caseBasicForm.caseExpectResult.replace(/[\r\n]/g, '').trim()
        caseInfo.base['testcaseDesc'] = this.caseBasicForm.caseDesc
        console.log('提交表单数据', caseInfo)
        if (this.idx === -1) {
          addTestCase(caseInfo).then(res => {
            this.$message.success(res.desc)
            this.caseEditVisible = false
            this.testCaseInfo = null
            this.queryTestCasesForAddCase(this.intfId)
            // 刷新左侧树节点
            this.$emit('update-data')
          })
        } else {
          caseInfo.base['testcaseId'] = this.testcaseId
          editTestCase(caseInfo).then(res => {
            this.$message.success(res.desc)
            this.caseEditVisible = false
            this.testCaseInfo = null
            this.queryTestCasesForEditCase(this.intfId)
            // 刷新左侧树节点
            this.$emit('update-data')
          })
        }
      }
    },
    // 分页导航
    handleCurrentChange(val) {
      this.currentPage = val
      this.getTestCaseListByIntfId(this.intfId, this.currentPage, this.pageSize)
    },
    handleSizeChange(val) {
      this.pageSize = val
      this.getTestCaseListByIntfId(this.intfId, this.currentPage, this.pageSize)
    },
    // 点击新增测试用例按钮触发的事件
    handleAddCase() {
      this.flag = false
      this.caseEditVisible = true
      this.idx = -1
      this.chainVisible = false
      this.testcaseId = null
      this.testCaseInfo = null
      let _this = this
      _this.$nextTick(function() {
        _this.preExeForm.preExeFormVisible = false
        _this.preExeForm.preExeTableData = []
        _this.preExeForm.oid = 1
        _this.caseBasicForm.caseName = ''
        _this.caseBasicForm.caseExpectResult = ''
        _this.caseBasicForm.caseDesc = ''
        for (var i = 0, len = _this.caseBasicForm.tagOptions.length; i < len; i++) {
          _this.caseBasicForm.tagOptions[i].value = ''
        }
        _this.$refs.caseEdit.pageLoad(this.testCaseInfo)
        _this.resetForm('caseBasicForm')
      })
    },
    // 点击修改测试用例按钮触发的事件
    handleEdit(index, row) {
      this.flag = false
      this.idx = index
      this.testcaseId = row.id
      this.$nextTick(function() {
        this.preExeForm.preExeFormVisible = false
        this.preExeForm.preExeTableData = []
      })
      // 获取新用例详情接口
      queryTestCaseDetail({ testcaseId: row.id }).then(res => {
        this.caseEditVisible = true
        this.preExeForm.oid = 1
        // 回填标签信息
        this.caseBasicForm.tagOptions.forEach(item => {
          for (var i in row.tags) {
            if (row.tags[i].length !== 0) {
              if (item.label === i) {
                item.value = row.tags[i][0].tagId
              }
            }
          }
        })
        this.caseBasicForm.caseName = res.data.base.testcaseName
        this.caseBasicForm.caseExpectResult = res.data.base.expectResult
        this.caseBasicForm.caseDesc = res.data.base.testcaseDesc
        this.testCaseInfo = res.data
        if (res.data.setupCases.length !== 0) {
          let idx = 1
          res.data.setupCases.forEach(item => {
            item['id'] = idx
            idx += 1
          })
          this.preExeForm.preExeTableData = res.data.setupCases
        }
        //                    console.log("传给子组件的主用例信息", this.testCaseInfo)
        this.testCaseInfo.caseBasicFormVisible = false
        this.$nextTick(function() {
          this.$refs.caseEdit.pageLoad(this.testCaseInfo)
          this.$refs.caseBasicForm.clearValidate()
        })
      })
    },
    // 点击删除用例触发的事件
    handleDelete(index, row) {
      this.idx = index
      this.testcaseId = row.id
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
      //                this.tagForm.tagIdList = this.tableData[index].tags_id
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
            this.getTestCaseListByIntfId(this.intfId, this.currentPage, this.pageSize)
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
          id++
        }
        this.tagForm.tagOptions = tagOptions
        this.caseBasicForm.tagOptions = tagOptions
      })
    },
    // 点击复制用例触发的事件
    handleCopy(index, row) {
      this.idx = index
      this.testcaseId = row.id
      this.copyVisible = true
      this.copyiedCaseId = ''
    },
    handleChange(value) {
      value = this.copynum
    },
    // 确定复制用例
    copyRow() {
      if (this.copyCaseRadio === '2') {
        // 全部复制，多少份用例
        copyTestCase({
          id: this.testcaseId,
          copyNum: this.copynum
        }).then(res => {
          this.$message.success(res.desc)
          this.getTestCaseListByIntfId(this.intfId, this.currentPage, this.pageSize)
        })
        this.copyVisible = false
        this.copynum = 1
      } else {
        // 批量复制用例的数据结构
        var copyIdList = []
        copyIdList = this.copyiedCaseId.split(',')
        copyTestCaseData({
          copyIdList: copyIdList,
          copiedId: this.testcaseId
        }).then(res => {
          this.$message.success(res.desc)
        })
        this.copyVisible = false
      }
    },
    // 确定删除
    deleteRow() {
      deleteTestCase({
        testcaseId: this.testcaseId
      }).then(res => {
        this.$message.success(res.desc)
        this.queryTestCasesForDelCase(this.intfId)
        this.$emit('update-data')
      })
      this.delVisible = false
    },
    // 用例编辑界面查看前置调用链
    viewChain() {
      this.handleQueryChain(null, { id: this.testcaseId })
    },
    // 点击查询用例调用链
    handleQueryChain(index, row) {
      this.testcaseChainData = []
      this.getSetupCaseListByCaseId(row.id).then(res => {
        res.forEach(item => {
          item.chain_no = (res.indexOf(item) + 1).toString()
          if (res.indexOf(item) === res.length - 1) {
            item.chain_no = item.chain_no + '<--当前用例'
          }
          if (item.hasOwnProperty('extract_v_names') && item.extract_v_names !== '') {
            item.extract_v_names = item.extract_v_names.replace(/, /g, '\n')
          }
        })
        this.testcaseChainData = res
      })
    },
    // 更新测试用例状态
    handleUpdateStatus(index, row) {
      changeTestCaseStatus({
        id: row.id
      }).then(res => {
        this.getTestCaseListByIntfId(this.intfId, this.currentPage, this.pageSize)
      })
    },
    // 重置表单
    resetForm(formName) {
      if (this.$refs[formName] !== undefined) {
        this.$refs[formName].resetFields()
      }
    },
    // 根据接口ID查询测试用例列表
    getTestCaseListByIntfId(intfId, pageNo, pageSize) {
      return new Promise((resolve, reject) => {
        queryCaseByIntfId({
          intfId: intfId,
          pageNo: pageNo,
          pageSize: pageSize
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
          if (this.$route.name === 'autotest-manage-interface-testCaseConfig') {
            sessionStorage.setItem('testCaseListCache', JSON.stringify(res.desc))
            sessionStorage.setItem('IntfIdCache', intfId)
            sessionStorage.setItem('TotalNumCache', res.totalNum)
          }
          this.currentPage = pageNo
          this.pageSize = pageSize === 1000 ? 10 : pageSize
          this.tableData = res.desc
          this.totalCount = res.totalNum
          resolve(1)
        })
      })
    },
    // 点击树节点接口层不同场景下刷新用例数据逻辑
    queryTestCasesByNodeClick(intfId, caseId) {
      if (intfId && !caseId) {
        this.getTestCaseListByIntfId(intfId, 1, 10)
      } else if (caseId) {
        // 点击树节点用例层
        let IntfIdCache = sessionStorage.getItem('IntfIdCache')
        if (intfId === parseInt(IntfIdCache)) {
          // 如果对应的接口ID在缓存中，直接获取缓存中的用例列表数据
          let testCaseListCache = JSON.parse(sessionStorage.getItem('testCaseListCache'))
          let item = testCaseListCache.find(c => c.id === caseId)
          if (item) {
            // 缓存中找到用例数据
            this.tableData = []
            this.tableData.push(item)
            this.totalCount = 1
            sessionStorage.setItem('TotalNumCache', 1)
          } else {
            // 缓存中找不到用例数据
            this.getTestCaseListByIntfId(intfId, 1, 1000).then(res => {
              let testCaseListCache = JSON.parse(sessionStorage.getItem('testCaseListCache'))
              let item = testCaseListCache.find(c => c.id === caseId)
              this.tableData = []
              this.tableData.push(item)
              this.totalCount = 1
              sessionStorage.setItem('TotalNumCache', 1)
            })
          }
        } else {
          // 缓存数据不匹配
          this.getTestCaseListByIntfId(intfId, 1, 1000).then(res => {
            let testCaseListCache = JSON.parse(sessionStorage.getItem('testCaseListCache'))
            let item = testCaseListCache.find(c => c.id === caseId)
            this.tableData = []
            this.tableData.push(item)
            this.totalCount = 1
            sessionStorage.setItem('TotalNumCache', 1)
          })
        }
      }
    },
    // 树节点新增测试用例后刷新逻辑
    queryTestCasesForAddCase(intfId) {
      this.getTestCaseListByIntfId(intfId, 1, 10)
    },
    // 用例列表操作栏编辑测试用例后刷新逻辑
    queryTestCasesForEditCase(intfId) {
      let TotalNumCache = sessionStorage.getItem('TotalNumCache')
      if (parseInt(TotalNumCache) === 1 && this.$route.name === 'autotest-manage-interface-testCaseConfig') {
        this.getTestCaseListByIntfId(intfId, 1, 1000).then(res => {
          let testCaseListCache = JSON.parse(sessionStorage.getItem('testCaseListCache'))
          let item = testCaseListCache.find(c => c.id === this.testcaseId)
          this.tableData = []
          this.tableData.push(item)
          this.totalCount = 1
          sessionStorage.setItem('TotalNumCache', 1)
        })
      } else {
        this.getTestCaseListByIntfId(intfId, this.currentPage, this.pageSize)
      }
    },
    // 用例列表操作栏删除测试用例后刷新逻辑
    queryTestCasesForDelCase(intfId) {
      let TotalNumCache = sessionStorage.getItem('TotalNumCache')
      if (parseInt(TotalNumCache) === 1) {
        this.tableData = []
      } else {
        this.getTestCaseListByIntfId(intfId, this.currentPage, this.pageSize)
      }
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
        this.runReportVisible = true
        fetchEnvList({ envName: '' }).then(res => {
          this.runReportForm.supportEnv = res.desc
        })
        // 临时公共变量处理
        this.debugPubVar = false
        this.temporaryVariables = []
        queryPubVarsByTcList({ testcaseList: this.testcaseList }).then(resp => {
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
      } else {
        this.$message.error('请选择要运行的测试用例')
      }
    },
    // 运行测试用例
    RunCase(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          run({
            // 第一个run接口，返回reportid
            projectId: this.intfInfoTmp.projectId,
            env: this.runReportForm.envName,
            testcaseList: this.testcaseList,
            pubVariableChanges: this.temporaryVariables // run接口新增参数，临时公共变量列表
          }).then(res => {
            this.runReportVisible = false
            this.reportId = res.reportId
            let totalProgress = res.totalProgress
            run({
              // 第二个run接口，触发接口用例运行
              projectId: this.intfInfoTmp.projectId,
              env: this.runReportForm.envName,
              testcaseList: this.testcaseList,
              reportId: this.reportId,
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
    // 查询该用例被前置的用例列表
    viewSetupCase(index, row) {
      this.drawer = true
      queryListBySetupCase({ testcaseId: row.id }).then(res => {
        res.dataList.forEach(item => {
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
        this.gridData = res.dataList
      })
    },
    // 清理缓存
    clearCache() {
      this.gridData = []
    },
    // 懒加载前置用例的前置用例
    getSetupCase(row, treeNode, resolve) {
      this.getSetupCaseListByCaseId(row.preCaseId).then(res => {
        let tempId = this.preExeForm.oid * 100 + 1
        for (var i = 0, len = res.length; i < len; i++) {
          res[i]['id'] = tempId
          tempId += 1
        }
        this.preExeForm.oid += 1
        resolve(res.slice(0, res.length - 1))
      })
    },
    // 点击添加前置用例按钮
    clickSetupCaseBtn() {
      this.preExeForm.preExeFormVisible = !this.preExeForm.preExeFormVisible
      if (this.preExeForm.preExeSetupCaseOptions.length === 0) {
        this.subtreeSetupCase()
      }
      if (this.preExeForm.preExeSetupFullLinkOptions.length === 0) {
        this.queryFullLineList()
      }
    },
    // 设置前置全链路的流程链路
    handSetFlow(index, row) {
      this.setFlowVisible = true
      this.setFlowForm.idx = index
      this.$nextTick(function() {
        this.setFlowForm.flowId = null
      })
      // 获取支持运行的流程链路列表
      getCustomFlows({ testcaseId: row.preCaseId }).then(res => {
        this.setFlowForm.flowList = res.flowList
      })
    },
    setFlow(idx) {
      this.setFlowVisible = false
      let idx1 = this.setFlowForm.flowList.findIndex(c => c.flowId === this.setFlowForm.flowId)
      let id = this.preExeForm.preExeTableData[this.setFlowForm.idx].id
      let preCaseId = this.preExeForm.preExeTableData[this.setFlowForm.idx].preCaseId
      let preCaseType = this.preExeForm.preExeTableData[this.setFlowForm.idx].preCaseType
      let preCaseName = this.preExeForm.preExeTableData[this.setFlowForm.idx].preCaseName
      // 更新前置列表中数据
      this.$set(this.preExeForm.preExeTableData, idx, {
        customFlowId: this.setFlowForm.flowId,
        customFlowName: this.setFlowForm.flowId ? this.setFlowForm.flowList[idx1].flowName : '',
        id: id,
        preCaseId: preCaseId,
        preCaseType: preCaseType,
        preCaseName: preCaseName
      })
    }
  },
  watch: {
    intfInfoTmp: function(newValue) {
      this.interfaceProp.show = !(newValue.hasOwnProperty('interfacePropShow') && !newValue.interfacePropShow)
      if (newValue.hasOwnProperty('addCaseVisible') && newValue.addCaseVisible) {
        this.handleAddCase()
      } else if (newValue.hasOwnProperty('intfId') && !newValue.hasOwnProperty('testcaseId')) {
        if (this.intfId !== newValue.intfId) {
          queryApiDetail({ intfId: newValue.intfId }).then(res => {
            this.interfaceProp.type = res.data.type
            this.interfaceProp.intfChineseName = res.data.intfChineseName
            const info = res.data.info
            for (let obj in info) {
              this.interfaceProp[obj] = info[obj]
            }
          })
        }
        this.intfId = newValue.intfId
        this.queryTestCasesByNodeClick(this.intfId, null)
      } else if (newValue.hasOwnProperty('testcaseId')) {
        if (this.intfId !== newValue.intfId) {
          queryApiDetail({ intfId: newValue.intfId }).then(res => {
            this.interfaceProp.type = res.data.type
            this.interfaceProp.intfChineseName = res.data.intfChineseName
            const info = res.data.info
            for (let obj in info) {
              this.interfaceProp[obj] = info[obj]
            }
          })
        }
        this.intfId = newValue.intfId
        this.testcaseId = newValue.testcaseId
        this.queryTestCasesByNodeClick(this.intfId, this.testcaseId)
      }
    }
  }
}
</script>

<style lang="scss">
.el-table .warning-row {
  background: oldlace;
}

.case-table-expand {
  font-size: 0;
  .text {
    color: #606266;
  }
}

.case-table-expand label {
  width: 90px;
  color: #99a9bf;
}

.case-table-expand .el-form-item {
  margin-right: 0;
  margin-bottom: 0;
  width: 100%;
}

/* 用例编辑页面各元素样式 */

.caseEditDialog .el-dialog__body {
  padding: 10px 20px;
}

.box-card {
  margin-bottom: 10px;
}

.el-card__header {
  padding: 5px 10px;
}

.el-collapse-item__content .el-card__body {
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

.el-input--medium .el-input__inner {
  height: 36px;
  line-height: 36px;
  width: 400px;
}

.caseEditDialog {
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
        left: 20px;
        top: 54px;
        bottom: 0;
        right: 10px;
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
  .caseEditScrolllist {
    max-height: 750px;
  }
  .intfCaseBasic {
    border: 1px solid #ebebeb;
    height: 750px;
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
  .intfCaseBasicForm {
    margin: 10px;
  }
}

/*.case-table .el-table .cell {
    white-space: pre-line;
  }*/

.caseTabelScrolllist {
  overflow: scroll;
  white-space: nowrap;
}

.case-table .el-table__header tr,
.el-table__header th {
  padding: 0;
  height: 40px;
}

.case-table .el-table__body tr,
.el-table__body td {
  padding: 5px 0;
  height: 50px;
}
</style>
