<template>
  <!-- 新版：新增编辑测试用例弹出框  -->
  <el-scrollbar style="height: 100%;">
    <div class="caseEditForm">
      <div class="source">
        <el-row :gutter="20">
          <el-col :span="20">
            <el-checkbox-group v-model="selectedItem" size="small">
              <el-checkbox-button
                v-for="item in tabVisible"
                :label="item.displayName"
                :disabled="item.displayName === '基本信息' || item.displayName === '请求信息' || item.displayName === '结果验证' || (item.displayName === '用例变量' && caseVarConfForm.caseVarData.length !== 0) || (item.displayName === '请求前置' && caseSetupForm.caseSetupFormData.length !== 0) || (item.displayName === '用例后置' && caseTeardownForm.caseTeardownFormData.length !== 0) || (item.displayName === '提取变量' && caseExtractVarForm.caseExtractVarFormData.length !== 0) || (item.displayName === '请求后置' && requestTeardownForm.requestTeardownFormData.length !== 0)"
                :key="item.label"
                @change="item.value=!item.value"
              >{{item.displayName}}</el-checkbox-button>
            </el-checkbox-group>
          </el-col>
          <el-col :span="4" style="padding: 6px 5px">
            <el-tooltip placement="top" effect="light" content="请点击左侧按钮添加相应操作组件，灰色字体表示该步骤已经添加">
              <el-button class="header-icon el-icon-info" size="mini" type="text">说明</el-button>
            </el-tooltip>
          </el-col>
        </el-row>

        <el-collapse v-model="activeNames">
          <!--基本信息-->
          <el-collapse-item title="基本信息" name="1" v-if="caseBasicFormVisible">
            <el-form ref="caseBasicForm" :model="caseBasicForm" :label-position="labelPosition" :label-width="labelWidth">
              <el-form-item label="用例标题" prop="caseName" :rules="[{ required: true, message: '用例标题必填', trigger: 'blur' }]">
                <el-input v-model="caseBasicForm.caseName" placeholder="请输入用例标题"></el-input>
              </el-form-item>
              <el-form-item label="预期结果" prop="caseExpectResult" :rules="[{ required: true, message: '预期结果必填', trigger: 'blur' }]">
                <el-input type="textarea" autosize v-model="caseBasicForm.caseExpectResult" placeholder="请输入预期结果"></el-input>
              </el-form-item>
              <el-form-item label="用例描述" prop="caseDesc">
                <el-input type="textarea" autosize v-model="caseBasicForm.caseDesc" placeholder="请输入用例描述"></el-input>
              </el-form-item>
            </el-form>
          </el-collapse-item>
          <!--基本信息-->

          <!--用例变量-->
          <el-collapse-item name="2" v-show="tabVisible[1].value">
            <template slot="title">
              <span>用例变量</span>
              <el-tooltip placement="top" content="添加" effect="light">
                <el-button type="primary" size="mini" style="margin-left: 20px" icon="el-icon-plus" @click.stop="caseVarConfForm.caseVarVisible = true" plain></el-button>
              </el-tooltip>
            </template>
            <!--用例变量配置表单-->
            <el-dialog title="配置变量" :visible.sync="caseVarConfForm.caseVarVisible" width="40%" append-to-body destroy-on-close @close="resetCusVarConf">
              <el-form ref="caseVarConfForm" :model="caseVarConfForm" :label-position="labelPosition" :label-width="labelWidth">
                <el-form-item label="变量名称" prop="caseVarName" :rules="[{ required: true, message: '变量名称必填', trigger: 'blur' }]">
                  <el-input v-model="caseVarConfForm.caseVarName" placeholder="请输入变量名称"></el-input>
                </el-form-item>
                <el-form-item label="变量类型" prop="caseVarType" :rules="[{ required: true, message: '变量类型必选', trigger: 'change' }]">
                  <el-select v-model="caseVarConfForm.caseVarType" placeholder="请选择变量类型" @change="selectCusVarableType()">
                    <el-option v-for="item in cusFunsData.supportVariableType" :key="item.key" :label="item.description" :value="item.type"></el-option>
                  </el-select>
                </el-form-item>
                <el-form-item
                  label="变量值"
                  prop="caseVarValue"
                  :rules="[{required: true, message: '变量值不能为空', trigger: 'blur'}]"
                  v-if="caseVarConfForm.caseVarType === 'constant' || caseVarConfForm.caseVarType === 'db'"
                >
                  <el-input type="textarea" autosize v-model="caseVarConfForm.caseVarValue"></el-input>
                </el-form-item>
                <el-form-item
                  label="变量值类型"
                  prop="caseVarValueType"
                  :rules="[{required: true, message: '变量值类型不能为空', trigger: 'change'}]"
                  v-if="caseVarConfForm.caseVarType === 'constant'"
                >
                  <el-select v-model="caseVarConfForm.caseVarValueType" placeholder="请选择变量值类型">
                    <el-option label="数字" value="num"></el-option>
                    <el-option label="字符串" value="str"></el-option>
                    <el-option label="布尔型" value="bool"></el-option>
                    <el-option label="数组" value="list"></el-option>
                    <el-option label="对象" value="dict"></el-option>
                  </el-select>
                </el-form-item>
                <el-form-item
                  label="变量值"
                  prop="caseVarValue"
                  :rules="[{required: true, message: '变量值不能为空', trigger: 'change'}]"
                  v-if="caseVarConfForm.caseVarType === 'function'"
                >
                  <el-select v-model="caseVarConfForm.caseVarValue" placeholder="请选择" @change="selectCustomVariableFuncs">
                    <el-option v-for="item in cusFunsData.customVariableFunctions" :key="item.key" :label="item.description" :value="item.name"></el-option>
                  </el-select>
                  <el-popover placement="right" width="600" trigger="hover" style="margin-left: 20px" v-if="caseVarConfForm.caseVarValue !== ''">
                    <el-form labelWidth="100px" labelPosition="left" labelSuffix=":">
                      <el-form-item v-for="(item, index) in customFunInstructions" :label="item.label" :key="index">
                        <span>{{item.value}}</span>
                      </el-form-item>
                    </el-form>
                    <el-button type="text" slot="reference">使用说明</el-button>
                  </el-popover>
                </el-form-item>
                <el-form-item
                  v-for="(item, index) in caseVarConfForm.caseVarSupFunParams"
                  :label="item.label"
                  :key="item.key"
                  :prop="'caseVarSupFunParams.' + index + '.value'"
                  :rules="{required: true, message: item.label + '不能为空', trigger: 'blur'}"
                >
                  <el-input type="textarea" autosize v-model="item.value"></el-input>
                </el-form-item>
              </el-form>
              <span slot="footer" class="dialog-footer">
                <el-button type="primary" @click="saveCusVarConf(caseVarConfForm.idx)">保存</el-button>
                <el-button @click="cancelCaseVarConf">取消</el-button>
              </span>
            </el-dialog>
            <!--用例变量数据列表-->
            <el-table :data="caseVarConfForm.caseVarDataForView" border style="width: 100%" ref="multipleTable" tooltip-effect="light">
              <!--<el-table-column type="index" width="40">
              </el-table-column>-->
              <el-table-column prop="caseVarName" label="变量名" min-width="100"></el-table-column>
              <el-table-column prop="caseVarType" label="变量类型" width="100"></el-table-column>
              <el-table-column prop="caseVarValue" label="变量值" min-width="150"></el-table-column>
              <el-table-column prop="caseVarParam" label="参数" min-width="150"></el-table-column>
              <el-table-column label="操作" fixed="right" width="160">
                <template slot-scope="scope">
                  <el-button type="text" @click="handleCusVarEdit(scope.$index, scope.row)">编辑</el-button>
                  <el-button type="text" @click="handMoveUpVar(scope.$index, scope.row)" v-if="scope.$index !== 0">上移</el-button>
                  <el-button
                    type="text"
                    @click="handMoveDownVar(scope.$index, scope.row)"
                    v-if="scope.$index !== caseVarConfForm.caseVarDataForView.length-1"
                  >下移</el-button>
                  <el-button type="text" @click="handleCusVarDel(scope.$index, scope.row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-collapse-item>
          <!--用例变量-->

          <!--请求前置-->
          <el-collapse-item name="3" v-show="tabVisible[2].value">
            <template slot="title">
              <span>请求前置</span>
              <el-tooltip placement="top" content="添加" effect="light">
                <el-button
                  type="primary"
                  size="mini"
                  style="margin-left: 20px"
                  icon="el-icon-plus"
                  @click.stop="caseSetupForm.caseSetupFormVisible = true"
                  plain
                ></el-button>
              </el-tooltip>
            </template>
            <!--请求前置配置表单-->
            <el-dialog title="配置前置" :visible.sync="caseSetupForm.caseSetupFormVisible" width="40%" append-to-body destroy-on-close @close="resetCaseSetupForm">
              <el-form ref="caseSetupForm" :model="caseSetupForm" :label-position="labelPosition" :label-width="labelWidth">
                <el-form-item label="函数类型" prop="caseSetupFuncType" :rules="[{ required: true, message: '函数类型必选', trigger: 'change' }]">
                  <el-select v-model="caseSetupForm.caseSetupFuncType" placeholder="请选择函数类型" @change="selectCusSetupFuncType">
                    <el-option v-for="item in cusFunsData.supportSetupFuncs" :key="item.key" :label="item.description" :value="item.name"></el-option>
                  </el-select>
                  <el-popover placement="right" width="600" trigger="hover" style="margin-left: 20px" v-if="caseSetupForm.caseSetupFuncType !== ''">
                    <el-form labelWidth="100px" labelPosition="left" labelSuffix=":">
                      <el-form-item v-for="(item, index) in customFunInstructions" :label="item.label" :key="index">
                        <span>{{item.value}}</span>
                      </el-form-item>
                    </el-form>
                    <el-button type="text" slot="reference">使用说明</el-button>
                  </el-popover>
                </el-form-item>
                <el-form-item
                  v-for="(item, index) in caseSetupForm.caseSetupFuncParam"
                  :label="item.label"
                  :key="item.key"
                  :prop="'caseSetupFuncParam.' + index + '.value'"
                  :rules="{required: true, message: item.label + '不能为空', trigger: 'blur'}"
                >
                  <el-input type="textarea" autosize v-model="item.value"></el-input>
                </el-form-item>
              </el-form>
              <span slot="footer" class="dialog-footer">
                <el-button type="primary" @click="saveCaseSetupForm(caseSetupForm.idx)">保存</el-button>
                <el-button @click="cancelCaseSetupConf">取消</el-button>
              </span>
            </el-dialog>
            <!--请求前置数据列表-->
            <el-table :data="caseSetupForm.caseSetupFormDataForView" border style="width: 100%" ref="multipleTable" tooltip-effect="light">
              <!--<el-table-column type="index" width="40">
              </el-table-column>-->
              <el-table-column prop="caseSetupFuncType" label="函数类型" min-width="150"></el-table-column>
              <el-table-column prop="caseSetupFuncParam" label="参数" min-width="400"></el-table-column>
              <el-table-column label="操作" fixed="right" width="160">
                <template slot-scope="scope">
                  <el-button type="text" @click="handleCaseSetupFormEdit(scope.$index, scope.row)">编辑</el-button>
                  <el-button type="text" @click="handMoveUpSetup(scope.$index, scope.row)" v-if="scope.$index !== 0">上移</el-button>
                  <el-button
                    type="text"
                    @click="handMoveDownSetup(scope.$index, scope.row)"
                    v-if="scope.$index !== caseSetupForm.caseSetupFormDataForView.length-1"
                  >下移</el-button>
                  <el-button type="text" @click="handleCaseSetupFormDel(scope.$index, scope.row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-collapse-item>
          <!--请求前置-->

          <!--请求信息-->
          <el-collapse-item name="4">
            <template slot="title">
              <span>请求信息</span>
              <el-button type="primary" size="mini" style="margin-left: 20px" @click.stop="formatIntfParms()" plain>{{caseRequestForm.butLabel}}</el-button>
            </template>
            <el-form ref="caseRequestForm" :model="caseRequestForm" :rules="rules" status-icon :label-position="labelPosition" :label-width="labelWidth">
              <el-form-item label="请求体" prop="requestInfo">
                <el-input type="textarea" :autosize="{ minRows: 5, maxRows: 10}" style="width: 100%" v-model="caseRequestForm.requestInfo"></el-input>
              </el-form-item>
              <!--<el-form-item label="是否合并报文" prop="isMerge">
                <el-checkbox v-model="caseRequestForm.isMerge"></el-checkbox>
                <el-tooltip placement="top" effect="light">
                        <div slot="content">
                          实际请求报文默认会将请求体同接口基础报文进行合并，合并规则如下：<br/>
                          1.规则1：合并后为请求体和接口基础报文中入参的并集<br/>
                          2.规则2：对于必填参数，如果基础报文中存在，但是请求体中不存在，合并后会包含该参数<br/>
                          3.规则3：对于非必填参数，如果基础报文中存在，但是请求体中不存在，合并后舍弃该参数<br/>
                          4.规则4：请求体中存在的参数，合并后的参数值以请求体为准，否则取接口基础报文中参数值<br/>
                          示例：<br/>
                          请求体为{"a":1, "b":2}，接口基础报文为{"a":11, "c":33, "d":44}，其中c必填，d非必填<br/>
                          合并后的实际请求报文为{"a":1, "b":2, "c":33}<br/>
                      </div>
                  <el-button
                          class="header-icon el-icon-info" size="mini" type="text"> 说明
                  </el-button>
              </el-tooltip>
              </el-form-item>-->
              <el-form-item label="自动加签" v-if="interfaceProp.type === 'HTTP'" prop="isHasSign">
                <el-radio-group v-model="caseRequestForm.isHasSign" @change="selectSignFuncs">
                  <el-radio label="1">否</el-radio>
                  <el-radio label="2">是</el-radio>
                </el-radio-group>
              </el-form-item>
              <el-form-item label="加签函数" v-if="caseRequestForm.isHasSign === '2'" prop="signFunc">
                <el-select v-model="caseRequestForm.signFunc" placeholder="请选择加签函数" style="margin-left: 20px">
                  <el-option v-for="item in cusFunsData.supportSignFuncs" :key="item.key" :label="item.description" :value="item.name"></el-option>
                </el-select>
              </el-form-item>
            </el-form>
          </el-collapse-item>
          <!--请求信息-->

          <!--请求后置-->
          <el-collapse-item name="5" v-show="tabVisible[4].value">
            <template slot="title">
              <span>请求后置</span>
              <el-tooltip placement="top" content="添加" effect="light">
                <el-button
                  type="primary"
                  size="mini"
                  style="margin-left: 20px"
                  icon="el-icon-plus"
                  @click.stop="requestTeardownForm.requestTeardownFormVisible = true"
                  plain
                ></el-button>
              </el-tooltip>
            </template>
            <!--请求后置配置表单-->
            <el-dialog
              title="配置后置"
              :visible.sync="requestTeardownForm.requestTeardownFormVisible"
              width="40%"
              append-to-body
              destroy-on-close
              @close="resetRequestTeardownForm"
            >
              <el-form ref="requestTeardownForm" :model="requestTeardownForm" :label-position="labelPosition" :label-width="labelWidth">
                <el-form-item label="函数类型" prop="requestTeardownFuncType" :rules="[{ required: true, message: '函数类型必选', trigger: 'change' }]">
                  <el-select v-model="requestTeardownForm.requestTeardownFuncType" placeholder="请选择函数类型" @change="selectRequestTeardownHooks">
                    <el-option v-for="item in cusFunsData.supportTeardownFuncs" :key="item.key" :label="item.description" :value="item.name"></el-option>
                  </el-select>
                  <el-popover placement="right" width="600" trigger="hover" style="margin-left: 20px" v-if="requestTeardownForm.requestTeardownFuncType !== ''">
                    <el-form labelWidth="100px" labelPosition="left" labelSuffix=":">
                      <el-form-item v-for="(item, index) in customFunInstructions" :label="item.label" :key="index">
                        <span>{{item.value}}</span>
                      </el-form-item>
                    </el-form>
                    <el-button type="text" slot="reference">使用说明</el-button>
                  </el-popover>
                </el-form-item>
                <el-form-item
                  v-for="(item, index) in requestTeardownForm.requestTeardownFuncParam"
                  :label="item.label"
                  :key="item.key"
                  :prop="'requestTeardownFuncParam.' + index + '.value'"
                  :rules="{required: true, message: item.label + '不能为空', trigger: 'blur'}"
                >
                  <el-input type="textarea" autosize v-model="item.value"></el-input>
                </el-form-item>
              </el-form>
              <span slot="footer" class="dialog-footer">
                <el-button type="primary" @click="saveRequestTeardownForm(requestTeardownForm.idx)">保存</el-button>
                <el-button @click="cancelRequestTeardownConf">取消</el-button>
              </span>
            </el-dialog>
            <!--请求后置数据列表-->
            <el-table :data="requestTeardownForm.requestTeardownFormDataForView" border style="width: 100%" ref="multipleTable" tooltip-effect="light">
              <!--<el-table-column type="index" width="40">
              </el-table-column>-->
              <el-table-column prop="requestTeardownFuncType" label="函数类型" width="150"></el-table-column>
              <el-table-column prop="requestTeardownFuncParam" label="参数" min-width="400"></el-table-column>
              <el-table-column label="操作" fixed="right" width="160">
                <template slot-scope="scope">
                  <el-button type="text" @click="handleRequestTeardownFormEdit(scope.$index, scope.row)">编辑</el-button>
                  <el-button type="text" @click="handMoveUpRequestTeardown(scope.$index, scope.row)" v-if="scope.$index !== 0">上移</el-button>
                  <el-button
                    type="text"
                    @click="handMoveDownRequestTeardown(scope.$index, scope.row)"
                    v-if="scope.$index !== requestTeardownForm.requestTeardownFormDataForView.length-1"
                  >下移</el-button>
                  <el-button type="text" @click="handleRequestTeardownFormDel(scope.$index, scope.row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-collapse-item>
          <!--请求后置-->

          <!--提取变量-->
          <el-collapse-item name="6" v-show="tabVisible[5].value">
            <template slot="title">
              <span>提取变量</span>
              <el-tooltip placement="top" content="添加" effect="light">
                <el-button
                  type="primary"
                  size="mini"
                  style="margin-left: 20px"
                  icon="el-icon-plus"
                  @click.stop="caseExtractVarForm.caseExtractVarFormVisible = true"
                  plain
                ></el-button>
              </el-tooltip>
              <el-tooltip style="margin-left: 20px" placement="top-start" effect="light">
                <div slot="content">
                  【提取变量】是为了将【返回对象某个值 /用例内变量 /SQL查询结果】保存为变量，供后面的步骤和用例使用
                  <br />【提取内容】支持以下几种写法：
                  <br />1.提取返回对象中某个值（content代表返回报文，headers代表返回头，status_code代表状态码）
                  <br />例如 content.accessToken
                  <br />headers.content-type
                  <br />status_code
                  <br />2.提取用例内变量
                  <br />例如 $phoneNo
                  <br />3.提取SQL查询结果
                  <br />例如 SELECT NEXT_VALUE FROM user_db.sequence WHERE SEQ_NAME='MEMBER_ID';
                  <br />【截取】只想保留提取结果的一部分？在你的提取内容后加上截取表达式
                  <br />例如 content.accessToken[2:5]
                  <br />
                </div>
                <el-button class="header-icon el-icon-info" size="mini" type="text">说明</el-button>
              </el-tooltip>
            </template>
            <!--提取变量配置表单-->
            <el-dialog
              title="配置提取变量"
              :visible.sync="caseExtractVarForm.caseExtractVarFormVisible"
              width="40%"
              append-to-body
              destroy-on-close
              @close="resetCaseExtractVarForm"
            >
              <el-form ref="caseExtractVarForm" :model="caseExtractVarForm" :label-position="labelPosition" :label-width="labelWidth">
                <el-form-item label="提取内容" prop="extractVarName" :rules="[{required: true, message: '提取内容不能为空', trigger: 'blur'}]">
                  <el-input type="textarea" autosize v-model="caseExtractVarForm.extractVarName"></el-input>
                </el-form-item>
                <el-form-item label="保存变量" prop="savedVarName" :rules="[{required: true, message: '保存变量不能为空', trigger: 'blur'}]">
                  <el-input type="textarea" autosize v-model="caseExtractVarForm.savedVarName"></el-input>
                </el-form-item>
              </el-form>
              <span slot="footer" class="dialog-footer">
                <el-button type="primary" @click="saveCaseExtractVarForm(caseExtractVarForm.idx)">保存</el-button>
                <el-button @click="cancelCaseExtractVarConf">取消</el-button>
              </span>
            </el-dialog>
            <!--提取变量数据列表-->
            <el-table
              :data="caseExtractVarForm.caseExtractVarFormDataForView"
              size="mini"
              border
              style="width: 100%"
              ref="comparatorsTable"
              tooltip-effect="light"
            >
              <!--<el-table-column type="index">
              </el-table-column>-->
              <el-table-column prop="savedVarName" label="保存变量" min-width="100"></el-table-column>
              <el-table-column prop="extractVarName" label="提取内容" min-width="400"></el-table-column>
              <el-table-column label="操作" fixed="right" width="160">
                <template slot-scope="scope">
                  <el-button type="text" @click="handleCaseExtractVarFormEdit(scope.$index, scope.row)">编辑</el-button>
                  <el-button type="text" @click="handMoveUpExtract(scope.$index, scope.row)" v-if="scope.$index !== 0">上移</el-button>
                  <el-button
                    type="text"
                    @click="handMoveDownExtract(scope.$index, scope.row)"
                    v-if="scope.$index !== caseExtractVarForm.caseExtractVarFormDataForView.length-1"
                  >下移</el-button>
                  <el-button type="text" @click="handleCaseExtractVarFormDel(scope.$index, scope.row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-collapse-item>
          <!--提取变量-->

          <!--结果验证-->
          <el-collapse-item name="7">
            <template slot="title">
              <span>结果验证</span>
              <el-tooltip placement="top" content="添加" effect="light">
                <el-button
                  type="primary"
                  size="mini"
                  style="margin-left: 20px"
                  icon="el-icon-plus"
                  @click.stop="caseAssertForm.caseAssertFormVisible = true"
                  plain
                ></el-button>
              </el-tooltip>
            </template>
            <!--结果断言配置表单-->
            <el-dialog
              title="配置结果验证"
              :visible.sync="caseAssertForm.caseAssertFormVisible"
              width="40%"
              append-to-body
              destroy-on-close
              @close="resetCaseAssertForm"
            >
              <el-form ref="caseAssertForm" :model="caseAssertForm" :label-position="labelPosition" :label-width="labelWidth">
                <el-form-item label="断言类型" prop="assertType" :rules="[{ required: true, message: '断言类型必选', trigger: 'change' }]">
                  <el-select v-model="caseAssertForm.assertType" placeholder="请选择断言类型" @change="handleCurrentChangeComparators">
                    <el-option v-for="(item, index) in cusFunsData.supportCustomComparators" :key="index" :label="item.description" :value="item.name"></el-option>
                  </el-select>
                  <el-popover placement="right" width="600" trigger="hover" style="margin-left: 20px" v-if="caseAssertForm.assertType !== ''">
                    <el-form labelWidth="100px" labelPosition="left" labelSuffix=":">
                      <el-form-item v-for="(item, index) in customFunInstructions" :label="item.label" :key="index">
                        <span>{{item.value}}</span>
                      </el-form-item>
                    </el-form>
                    <el-button type="text" slot="reference">使用说明</el-button>
                  </el-popover>
                </el-form-item>
                <el-form-item label="待校验内容" prop="actualValue" :rules="[{required: true, message: '待校验内容不能为空', trigger: 'blur'}]">
                  <el-input type="textarea" autosize v-model="caseAssertForm.actualValue"></el-input>
                </el-form-item>
                <el-form-item label="期望值" prop="expectValue" :rules="[{required: true, message: '期望值不能为空', trigger: 'blur'}]">
                  <el-input type="textarea" autosize v-model="caseAssertForm.expectValue"></el-input>
                </el-form-item>
                <el-form-item label="备注" prop="comment">
                  <el-input type="textarea" autosize v-model="caseAssertForm.comment"></el-input>
                </el-form-item>
              </el-form>
              <span slot="footer" class="dialog-footer">
                <el-button type="primary" @click="saveCaseAssertForm(caseAssertForm.idx)">保存</el-button>
                <el-button @click="cancelCaseAssertConf">取消</el-button>
              </span>
            </el-dialog>
            <!--结果验证数据列表-->
            <el-table :data="caseAssertForm.tableDataComparatorsForView" size="mini" border style="width: 100%" ref="comparatorsTable" tooltip-effect="light">
              <!--<el-table-column type="index">
              </el-table-column>-->
              <el-table-column prop="assertType" label="断言类型" width="120"></el-table-column>
              <el-table-column prop="actualValue" label="待校验内容" min-width="200"></el-table-column>
              <el-table-column prop="expectValue" label="期望值" min-width="200"></el-table-column>
              <el-table-column prop="comment" label="备注" min-width="100"></el-table-column>
              <el-table-column label="操作" fixed="right" width="160">
                <template slot-scope="scope">
                  <el-button type="text" @click="handleCaseAssertFormEdit(scope.$index, scope.row)">编辑</el-button>
                  <el-button type="text" @click="handMoveUpAssert(scope.$index, scope.row)" v-if="scope.$index !== 0">上移</el-button>
                  <el-button
                    type="text"
                    @click="handMoveDownAssert(scope.$index, scope.row)"
                    v-if="scope.$index !== caseAssertForm.tableDataComparatorsForView.length-1"
                  >下移</el-button>
                  <el-button type="text" @click="handleCaseAssertFormDel(scope.$index, scope.row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-collapse-item>
          <!--结果验证-->

          <!--用例后置-->
          <el-collapse-item name="8" v-show="tabVisible[7].value">
            <template slot="title">
              <span>用例后置</span>
              <el-tooltip placement="top" content="添加" effect="light">
                <el-button
                  type="primary"
                  size="mini"
                  style="margin-left: 20px"
                  icon="el-icon-plus"
                  @click.stop="caseTeardownForm.caseTeardownFormVisible = true"
                  plain
                ></el-button>
              </el-tooltip>
            </template>
            <!--用例后置配置表单-->
            <el-dialog
              title="配置后置"
              :visible.sync="caseTeardownForm.caseTeardownFormVisible"
              width="40%"
              append-to-body
              destroy-on-close
              @close="resetCaseTeardownForm"
            >
              <el-form ref="caseTeardownForm" :model="caseTeardownForm" :label-position="labelPosition" :label-width="labelWidth">
                <el-form-item label="函数类型" prop="caseTeardownFuncType" :rules="[{ required: true, message: '函数类型必选', trigger: 'change' }]">
                  <el-select v-model="caseTeardownForm.caseTeardownFuncType" placeholder="请选择函数类型" @change="selectCustomTeardownHooks">
                    <el-option v-for="item in cusFunsData.supportTeardownFuncs" :key="item.key" :label="item.description" :value="item.name"></el-option>
                  </el-select>
                  <el-popover placement="right" width="600" trigger="hover" style="margin-left: 20px" v-if="caseTeardownForm.caseTeardownFuncType !== ''">
                    <el-form labelWidth="100px" labelPosition="left" labelSuffix=":">
                      <el-form-item v-for="(item, index) in customFunInstructions" :label="item.label" :key="index">
                        <span>{{item.value}}</span>
                      </el-form-item>
                    </el-form>
                    <el-button type="text" slot="reference">使用说明</el-button>
                  </el-popover>
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
              </el-form>
              <span slot="footer" class="dialog-footer">
                <el-button type="primary" @click="saveCaseTeardownForm(caseTeardownForm.idx)">保存</el-button>
                <el-button @click="cancelCaseTeardownConf">取消</el-button>
              </span>
            </el-dialog>
            <!--用例后置数据列表-->
            <el-table :data="caseTeardownForm.caseTeardownFormDataForView" border style="width: 100%" ref="multipleTable" tooltip-effect="light">
              <!--<el-table-column type="index" width="40">
              </el-table-column>-->
              <el-table-column prop="caseTeardownFuncType" label="函数类型" width="150"></el-table-column>
              <el-table-column prop="caseTeardownFuncParam" label="参数" min-width="400"></el-table-column>
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
          </el-collapse-item>
          <!--用例后置-->
        </el-collapse>
      </div>
    </div>
  </el-scrollbar>
</template>

<script>
import {
  queryCustomSetupHooks,
  querySupportVariableTypes,
  queryCustomFunctions,
  querySignFunctions,
  queryCustomComparators,
  queryCustomTeardownHooks
} from '@/api/autotest/manage/testcase-apiManage/support'
import { isJsonString, getFormatJsonStrFromString } from '@/libs/common'

export default {
  name: 'caseConfig',
  // 父组件通过props属性传递进来的数据,包括testCaseInfo
  props: {
    testCaseInfo: {
      type: Object,
      default: () => {
        return null
      }
    }
  },
  data() {
    var headersValidatePass = (rule, value, callback) => {
      if (value.length === 0) {
        return callback(new Error('请输入请求信息'))
      } else if (!isJsonString(value)) {
        return callback(new Error('非法json格式'))
      } else {
        callback()
      }
    }
    return {
      interfaceProp: {
        type: 'HTTP' // 如果接口是HTTP类型，需要展示自动加签信息，其他则无
      },
      testCaseDetail: {}, // 用例编辑表单所有内容，用于回传给父组件数据
      /* 表单标签对齐方式*/
      labelPosition: 'right',
      labelWidth: '120px',
      /* 用例编辑页面上面控制条相关数据*/
      activeNames: ['1', '2', '3', '4', '5', '6', '7', '8'],
      selectedItem: [],
      tabVisible: [
        { label: 'baseInfo', displayName: '基本信息', value: true },
        { label: 'caseVar', displayName: '用例变量', value: false },
        { label: 'setupInfo', displayName: '请求前置', value: false },
        { label: 'requestInfo', displayName: '请求信息', value: true },
        { label: 'requestTeardown', displayName: '请求后置', value: true },
        { label: 'extractVar', displayName: '提取变量', value: false },
        { label: 'AssertInfo', displayName: '结果验证', value: true },
        { label: 'teardownInfo', displayName: '用例后置', value: false }
      ],
      caseBasicFormVisible: true, // 基本信息表单是否显示
      cusFunsData: {
        supportSetupFuncs: [], // 系统支持的前置函数
        supportTeardownFuncs: [], // 系统支持的后置函数
        supportVariableType: [], // 系统支持的变量类型
        customVariableFunctions: [], // 系统支持的自定义变量函数
        supportSignFuncs: [], // 系统支持的加签函数
        supportCustomComparators: [] // 系统支持的自定义断言类型
      },
      /* 用例基本信息*/
      caseBasicForm: {
        testcaseId: '',
        caseName: '',
        caseExpectResult: '',
        caseDesc: ''
      },
      /* 用例变量配置相关数据*/
      caseVarConfForm: {
        caseVarData: [], // 用例变量列表实际数据，需要提交后台
        caseVarDataForView: [], // 用例变量列表展示数据
        caseVarVisible: false, // 用例变量编辑页面是否显示
        caseVarName: '', // 用例变量名
        caseVarType: '', // 用例变量类型
        caseVarValue: '', // 用例变量值
        caseVarSupFunParams: [], // 用例变量值为函数类型，函数名及函数参数对象
        idx: -1, // 标记是新增 还是编辑
        caseVarValueType: '', // 变量类型为constant时，标识变量值的数据类型
        caseVarConfInstructions: [] // 自定义函数使用说明
      },
      /* 请求信息相关数据*/
      caseRequestForm: {
        requestInfo: '', // 请求体
        isHasSign: '1', // 是否自动加签
        signFunc: '', // 选择的加签函数
        requestDetail: {}, // 接口请求数据，用于请求后台接口
        butLabel: '格式化入参', // 格式化入参按钮label
        butFlag: true, // 格式化入参按钮状态标志
        isMerge: true
      },
      /* 请求后置相关数据*/
      requestTeardownForm: {
        requestTeardownFormVisible: false, // 请求后置编辑页面是否显示
        requestTeardownFuncType: '', // 选择的请求后置函数类型
        requestTeardownFuncParam: [], // 选择的请求后置函数对应的参数名称及参数值对象
        requestTeardownFormDataForView: [], // 请求后置列表数据，用于列表展示
        requestTeardownFormData: [], // 请求后置列表数据，用于接口请求
        idx: -1 // 标记是新增 还是编辑
      },
      /* 结果断言相关数据*/
      caseAssertForm: {
        caseAssertFormVisible: false, // 结果断言编辑页面是否显示
        assertType: '', // 选择的断言函数类型
        actualValue: '', // 待验证内容
        expectValue: '', // 期望结果
        comment: '', // 备注
        tableDataComparators: [], // 断言列表数据，用于接口请求
        tableDataComparatorsForView: [], // 断言列表数据，用于列表展示
        idx: -1, // 标记是新增 还是编辑
        caseAssertInstructions: [] // 自定义函数使用说明
      },
      /* 请求前置相关数据*/
      caseSetupForm: {
        caseSetupFormVisible: false, // 请求前置编辑页面是否显示
        caseSetupFuncType: '', // 选择的请求前置函数类型
        caseSetupFuncParam: [], // 选择的请求前置函数对应的参数名称及参数值对象
        caseSetupFormDataForView: [], // 请求前置列表数据，用于列表展示
        caseSetupFormData: [], // 请求前置列表数据，用于接口请求
        idx: -1, // 标记是新增 还是编辑
        caseSetupInstructions: [] // 自定义函数使用说明
      },
      /* 用例后置相关数据*/
      caseTeardownForm: {
        caseTeardownFormVisible: false, // 用例后置编辑页面是否显示
        caseTeardownFuncType: '', // 选择的用例后置函数类型
        caseTeardownFuncParam: [], // 选择的用例后置函数对应的参数名称及参数值对象
        caseTeardownFormDataForView: [], // 用例后置列表数据，用于列表展示
        caseTeardownFormData: [], // 用例后置列表数据，用于接口请求
        idx: -1 // 标记是新增 还是编辑
      },
      /* 提取变量相关数据*/
      caseExtractVarForm: {
        caseExtractVarFormVisible: false, // 提取变量编辑页面是否显示
        extractVarName: '', // 提取的内容
        savedVarName: '', // 保存的变量名称
        caseExtractVarFormDataForView: [], // 提取变量列表数据，用于列表展示
        caseExtractVarFormData: [], // 提取变量列表数据，用于接口请求
        idx: -1 // 标记是新增 还是编辑
      },
      rules: {
        requestInfo: [{ required: true, validator: headersValidatePass, trigger: 'blur' }],
        signFunc: [{ required: true, message: '加签函数必填', trigger: 'change' }]
      },
      customFunInstructions: [] // 自定义函数使用说明
    }
  },
  mounted() {
    this.queryCustomFuncsData(this.testCaseInfo)
  },
  methods: {
    // 查询系统支持的前置函数、用例变量类型、用例变量自定义函数、加签函数、断言类型、后置函数
    queryCustomFuncsData(obj) {
      let _self = this
      let newArr = []

      var res1 = new Promise(function(resolve, reject) {
        if (_self.cusFunsData.supportSetupFuncs.length === 0) {
          queryCustomSetupHooks({}).then(res => {
            _self.cusFunsData.supportSetupFuncs = res.data
            resolve(1)
          })
        } else {
          resolve(1)
        }
      })
      newArr.push(res1)

      var res2 = new Promise(function(resolve, reject) {
        if (_self.cusFunsData.supportTeardownFuncs.length === 0) {
          queryCustomTeardownHooks({}).then(res => {
            _self.cusFunsData.supportTeardownFuncs = res.data
            resolve(1)
          })
        } else {
          resolve(1)
        }
      })
      newArr.push(res2)

      var res3 = new Promise(function(resolve, reject) {
        if (_self.cusFunsData.supportVariableType.length === 0) {
          querySupportVariableTypes({}).then(res => {
            _self.cusFunsData.supportVariableType = res.data
            resolve(1)
          })
        } else {
          resolve(1)
        }
      })
      newArr.push(res3)

      var res4 = new Promise(function(resolve, reject) {
        if (_self.cusFunsData.customVariableFunctions.length === 0) {
          queryCustomFunctions({}).then(res => {
            _self.cusFunsData.customVariableFunctions = res.data
            resolve(1)
          })
        } else {
          resolve(1)
        }
      })
      newArr.push(res4)

      var res5 = new Promise(function(resolve, reject) {
        if (_self.cusFunsData.supportSignFuncs.length === 0) {
          querySignFunctions({}).then(res => {
            _self.cusFunsData.supportSignFuncs = res.data
            resolve(1)
          })
        } else {
          resolve(1)
        }
      })
      newArr.push(res5)

      var res6 = new Promise(function(resolve, reject) {
        if (_self.cusFunsData.supportCustomComparators.length === 0) {
          queryCustomComparators({}).then(res => {
            _self.cusFunsData.supportCustomComparators = res.data
            resolve(1)
          })
        } else {
          resolve(1)
        }
      })
      newArr.push(res6)
      Promise.all(newArr)
        .then(function() {
          // 都通过了
          console.log('校验成功')
          _self.pageLoad(obj)
        })
        .catch(function(err) {
          console.error(err)
        })
    },
    // 页面初始化
    pageLoad(obj) {
      this.caseVarConfForm.caseVarVisible = false
      this.caseAssertForm.caseAssertFormVisible = false
      this.caseSetupForm.caseSetupFormVisible = false
      this.caseTeardownForm.caseTeardownFormVisible = false
      this.caseExtractVarForm.caseExtractVarFormVisible = false
      // 回填前先初始化表单内容
      this.caseSetupForm.caseSetupFormDataForView = []
      this.caseSetupForm.caseSetupFormData = []
      this.caseTeardownForm.caseTeardownFormDataForView = []
      this.caseTeardownForm.caseTeardownFormData = []
      this.requestTeardownForm.requestTeardownFormDataForView = []
      this.requestTeardownForm.requestTeardownFormData = []
      this.caseVarConfForm.caseVarDataForView = []
      this.caseVarConfForm.caseVarData = []
      this.caseExtractVarForm.caseExtractVarFormDataForView = []
      this.caseExtractVarForm.caseExtractVarFormData = []
      this.caseAssertForm.tableDataComparatorsForView = []
      this.caseAssertForm.tableDataComparators = []
      this.resetForm('caseBasicForm')
      this.resetForm('caseRequestForm')
      this.caseRequestForm.butLabel = '格式化入参'
      this.caseRequestForm.butFlag = true
      console.log(obj)
      if (obj === null) {
        this.caseBasicFormVisible = false
        this.firstLoad()
      } else {
        if (obj.hasOwnProperty('caseBasicFormVisible')) {
          this.caseBasicFormVisible = obj.caseBasicFormVisible
        }
        this.caseDataLoad(obj)
      }
    },
    // 新增测试用例加载编辑页面
    firstLoad() {
      this.selectedItem = []
      this.tabVisible.forEach(item => {
        if (item.displayName !== '基本信息' || item.displayName !== '请求信息' || item.displayName !== '结果验证') {
          item.value = false
        }
      })
    },
    // 编辑测试用例页面加载测试用例数据
    caseDataLoad(obj) {
      const caseInfo = obj

      // 回填基本信息
      this.caseBasicForm.caseName = caseInfo.base.testcaseName
      this.caseBasicForm.caseExpectResult = caseInfo.base.expectResult
      this.caseBasicForm.caseDesc = caseInfo.base.testcaseDesc

      // 回填请求前置
      if (caseInfo.steps[0].setupInfo.length !== 0) {
        this.tabVisible[2].value = true
        this.selectedItem.push(this.tabVisible[2].displayName)
      } else {
        this.tabVisible[2].value = false
      }
      caseInfo.steps[0].setupInfo.forEach(item => {
        let caseSetupFuncParam = ''
        if (item.args) {
          Object.keys(item.args).forEach(function(key) {
            caseSetupFuncParam = caseSetupFuncParam ? caseSetupFuncParam + '||' + key + '=' + item.args[key] : key + '=' + item.args[key]
          })
        }
        // 用于列表展示数据
        this.caseSetupForm.caseSetupFormDataForView.push({
          caseSetupFuncType: item.desc,
          caseSetupFuncParam: caseSetupFuncParam || '无'
        })
        // 用于提交接口数据
        this.caseSetupForm.caseSetupFormData.push({
          name: item.name,
          desc: item.desc,
          args: item.args
        })
      })
      //                console.log('请求前置列表展示数据', this.caseSetupForm.caseSetupFormDataForView)
      //                console.log('请求前置接口提交数据', this.caseSetupForm.caseSetupFormData)

      // 回填用例后置
      if (caseInfo.steps[0].teardownInfo.length !== 0) {
        this.tabVisible[7].value = true
        this.selectedItem.push(this.tabVisible[6].displayName)
      } else {
        this.tabVisible[7].value = false
      }
      caseInfo.steps[0].teardownInfo.forEach(item => {
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
      //                console.log('用例后置列表展示数据', this.caseTeardownForm.caseTeardownFormDataForView)
      //                console.log('用例后置接口提交数据', this.caseTeardownForm.caseTeardownFormData)

      // 回填请求后置
      if (caseInfo.steps[0].requestTeardownInfo.length !== 0) {
        this.tabVisible[4].value = true
        this.selectedItem.push(this.tabVisible[6].displayName)
      } else {
        this.tabVisible[4].value = false
      }
      caseInfo.steps[0].requestTeardownInfo.forEach(item => {
        let requestTeardownFuncParam = ''
        if (item.args) {
          Object.keys(item.args).forEach(function(key) {
            requestTeardownFuncParam = requestTeardownFuncParam ? requestTeardownFuncParam + '||' + key + '=' + item.args[key] : key + '=' + item.args[key]
          })
        }
        // 用于列表展示数据
        this.requestTeardownForm.requestTeardownFormDataForView.push({
          requestTeardownFuncType: item.desc,
          requestTeardownFuncParam: requestTeardownFuncParam || '无'
        })
        // 用于提交接口数据
        this.requestTeardownForm.requestTeardownFormData.push({
          name: item.name,
          desc: item.desc,
          args: item.args
        })
      })
      //                console.log('请求后置列表展示数据', this.requestTeardownForm.requestTeardownFormDataForView)
      //                console.log('请求后置接口提交数据', this.requestTeardownForm.requestTeardownFormData)

      // 回填用户变量配置
      if (caseInfo.steps[0].variableInfo.length !== 0) {
        this.tabVisible[1].value = true
        this.selectedItem.push(this.tabVisible[1].displayName)
      } else {
        this.tabVisible[1].value = false
      }
      caseInfo.steps[0].variableInfo.forEach(item => {
        let caseVarParam = ''
        if (item.args) {
          Object.keys(item.args).forEach(function(key) {
            caseVarParam = caseVarParam ? caseVarParam + '||' + key + '=' + item.args[key] : key + '=' + item.args[key]
          })
        }
        if (item.type === 'constant') {
          caseVarParam = '变量值类型' + '=' + item.saveAs
        }
        let caseVarType = ''
        this.cusFunsData.supportVariableType.forEach(i => {
          if (i.type === item.type) {
            caseVarType = i.description
          }
        })
        let caseVarValue = ''
        this.cusFunsData.customVariableFunctions.forEach(i => {
          if (i.name === item.value) {
            caseVarValue = i.description
          }
        })
        // 用于列表展示数据
        this.caseVarConfForm.caseVarDataForView.push({
          caseVarType: caseVarType,
          caseVarName: item.name,
          caseVarValue: caseVarValue || item.value,
          caseVarParam: caseVarParam || '无'
        })
        // 用于提交接口数据
        if (item.type === 'constant') {
          this.caseVarConfForm.caseVarData.push({
            type: item.type,
            name: item.name,
            value: item.value,
            saveAs: item.saveAs
          })
        } else if (item.type === 'db') {
          this.caseVarConfForm.caseVarData.push({
            type: item.type,
            name: item.name,
            value: item.value
          })
        } else if (item.type === 'function') {
          this.caseVarConfForm.caseVarData.push({
            type: item.type,
            name: item.name,
            value: item.value,
            args: item.args
          })
        }
      })
      //                console.log('用例变量列表展示数据', this.caseVarConfForm.caseVarDataForView)
      //                console.log('用例变量接口提交数据', this.caseVarConfForm.caseVarData)

      // 回填提取变量
      if (caseInfo.steps[0].extractInfo.length !== 0) {
        this.tabVisible[5].value = true
        this.selectedItem.push(this.tabVisible[4].displayName)
      } else {
        this.tabVisible[5].value = false
      }
      caseInfo.steps[0].extractInfo.forEach(item => {
        // 用于列表展示数据
        this.caseExtractVarForm.caseExtractVarFormDataForView.push({
          extractVarName: item.check,
          savedVarName: item.saveAs
        })
        // 用于提交接口数据
        this.caseExtractVarForm.caseExtractVarFormData.push({
          check: item.check,
          saveAs: item.saveAs
        })
      })
      //                console.log('提取变量列表展示数据', this.caseExtractVarForm.caseExtractVarFormDataForView)
      //                console.log('提取变量接口提交数据', this.caseExtractVarForm.caseExtractVarFormData)

      // 回填请求信息
      if (caseInfo.steps[0].requestInfo.type === 1) {
        this.caseRequestForm.requestInfo = JSON.stringify(caseInfo.steps[0].requestInfo.json)
        this.caseRequestForm.isHasSign = '1'
        if (caseInfo.steps[0].requestInfo.sign) {
          this.caseRequestForm.isHasSign = '2'
          this.caseRequestForm.signFunc = caseInfo.steps[0].requestInfo.sign.name
        }
      } else if (caseInfo.steps[0].requestInfo.type === 2) {
        this.caseRequestForm.isHasSign = '1'
        this.caseRequestForm.requestInfo = JSON.stringify(caseInfo.steps[0].requestInfo.args)
      } else {
        this.caseRequestForm.isHasSign = '1'
        this.caseRequestForm.requestInfo = caseInfo.steps[0].requestInfo.msg
      }
      this.caseRequestForm.isMerge = caseInfo.steps[0].requestInfo.isMerge

      // 回填断言信息
      caseInfo.steps[0].validateInfo.forEach(item => {
        let assertType = ''
        this.cusFunsData.supportCustomComparators.forEach(i => {
          if (i.name === item.comparator) {
            assertType = i.description
          }
        })
        // 用于列表展示数据
        this.caseAssertForm.tableDataComparatorsForView.push({
          assertType: assertType,
          actualValue: item.check,
          expectValue: item.expect,
          comment: item.comment
        })
        // 用于提交接口数据
        this.caseAssertForm.tableDataComparators.push({
          comparator: item.comparator,
          desc: item.comparator,
          check: item.check,
          expect: item.expect,
          comment: item.comment
        })
      })
      //                console.log('结果断言列表展示数据', this.caseAssertForm.tableDataComparatorsForView)
      //                console.log('结果断言接口提交数据', this.caseAssertForm.tableDataComparators)
    },
    // 用例变量表单选择变量类型触发的change事件
    selectCusVarableType() {
      this.caseVarConfForm.caseVarValue = ''
      this.caseVarConfForm.caseVarSupFunParams = []
    },
    // 用例变量表单选择自定义函数触发的change事件
    selectCustomVariableFuncs(val) {
      this.caseVarConfForm.caseVarSupFunParams = []
      let caseVarValue = this.caseVarConfForm.caseVarValue
      const caseVarFuns = this.cusFunsData.customVariableFunctions.find(function(x) {
        return x.name === caseVarValue
      })
      caseVarFuns.parameters.forEach(i => {
        this.caseVarConfForm.caseVarSupFunParams.push({ label: i, value: '' })
      })
      let idx = this.cusFunsData.customVariableFunctions.findIndex(c => c.name === val)
      this.customFunInstructions = this.cusFunsData.customVariableFunctions[idx].introduction
    },
    // 保存用例变量到列表中
    saveCusVarConf(idx) {
      this.$refs['caseVarConfForm'].validate(valid => {
        if (valid) {
          let caseVarParam = ''
          let caseVarSupFunParams = {}
          if (this.caseVarConfForm.caseVarSupFunParams.length !== 0) {
            this.caseVarConfForm.caseVarSupFunParams.forEach(i => {
              caseVarParam = caseVarParam
                ? caseVarParam + '||' + i.label + '=' + i.value.replace(/[\r\n]/g, '').trim()
                : i.label + '=' + i.value.replace(/[\r\n]/g, '').trim()
              caseVarSupFunParams[i.label] = i.value.replace(/[\r\n]/g, '').trim()
            })
          }
          let caseVarType = ''
          this.cusFunsData.supportVariableType.forEach(i => {
            if (i.type === this.caseVarConfForm.caseVarType) {
              caseVarType = i.description
            }
          })
          let caseVarValue = ''
          this.cusFunsData.customVariableFunctions.forEach(i => {
            if (i.name === this.caseVarConfForm.caseVarValue) {
              caseVarValue = i.description
            }
          })
          // 当变量类型为constant时，判断选择的变量值类型和输入的变量值是否匹配
          if (this.caseVarConfForm.caseVarType === 'constant') {
            if (this.caseVarConfForm.caseVarValueType === 'num' && isNaN(Number(this.caseVarConfForm.caseVarValue))) {
              this.$message.warning('变量值请输入数字')
              return false
            }
            if (
              this.caseVarConfForm.caseVarValueType === 'bool' &&
              this.caseVarConfForm.caseVarValue !== 'True' &&
              this.caseVarConfForm.caseVarValue !== 'False'
            ) {
              this.$message.warning('变量值请输入True/False')
              return false
            }
            if (this.caseVarConfForm.caseVarValueType === 'list') {
              if (!isJsonString(this.caseVarConfForm.caseVarValue)) {
                this.$message.warning('变量值请输入list格式')
                return false
              } else if (Object.prototype.toString.call(JSON.parse(this.caseVarConfForm.caseVarValue)).toLowerCase() !== '[object array]') {
                this.$message.warning('变量值请输入list格式')
                return false
              }
            }
            if (this.caseVarConfForm.caseVarValueType === 'dict') {
              if (!isJsonString(this.caseVarConfForm.caseVarValue)) {
                this.$message.warning('变量值请输入dict格式')
                return false
              } else if (Object.prototype.toString.call(JSON.parse(this.caseVarConfForm.caseVarValue)).toLowerCase() !== '[object object]') {
                this.$message.warning('变量值请输入dict格式')
                return false
              }
            }
            caseVarParam = '变量值类型' + '=' + this.caseVarConfForm.caseVarValueType
          }
          // idx为-1 表示新增；非-1 表示编辑
          if (idx === -1) {
            // 用于列表展示数据
            this.caseVarConfForm.caseVarDataForView.push({
              caseVarType: caseVarType,
              caseVarName: this.caseVarConfForm.caseVarName.trim(),
              caseVarValue: caseVarValue || this.caseVarConfForm.caseVarValue.replace(/[\r\n]/g, '').trim(),
              caseVarParam: caseVarParam || '无'
            })
            // 用于提交接口数据
            this.caseVarConfForm.caseVarData.push({
              type: this.caseVarConfForm.caseVarType,
              name: this.caseVarConfForm.caseVarName.trim(),
              value: this.caseVarConfForm.caseVarValue.replace(/[\r\n]/g, '').trim(),
              args: caseVarSupFunParams,
              saveAs: this.caseVarConfForm.caseVarType === 'constant' ? this.caseVarConfForm.caseVarValueType : ''
            })
          } else {
            // 用于列表展示数据
            this.$set(this.caseVarConfForm.caseVarDataForView, idx, {
              caseVarType: caseVarType,
              caseVarName: this.caseVarConfForm.caseVarName.trim(),
              caseVarValue: caseVarValue || this.caseVarConfForm.caseVarValue.replace(/[\r\n]/g, '').trim(),
              caseVarParam: caseVarParam || '无'
            })
            // 用于提交接口数据
            this.$set(this.caseVarConfForm.caseVarData, idx, {
              type: this.caseVarConfForm.caseVarType,
              name: this.caseVarConfForm.caseVarName.trim(),
              value: this.caseVarConfForm.caseVarValue.replace(/[\r\n]/g, '').trim(),
              args: caseVarSupFunParams,
              saveAs: this.caseVarConfForm.caseVarType === 'constant' ? this.caseVarConfForm.caseVarValueType : ''
            })
          }
          // 关闭表单
          this.caseVarConfForm.caseVarVisible = false
          console.log(this.caseVarConfForm.caseVarData, this.caseVarConfForm.caseVarDataForView)
        }
      })
    },
    // 重置用例变量配置表单内容
    resetCusVarConf() {
      return new Promise((resolve, reject) => {
        this.resetForm('caseVarConfForm')
        this.caseVarConfForm.caseVarSupFunParams = []
        this.caseVarConfForm.caseVarType = ''
        this.caseVarConfForm.caseVarValue = ''
        this.caseVarConfForm.caseVarName = ''
        this.caseVarConfForm.idx = -1
        resolve(1)
      })
    },
    // 修改用例变量列表中的某条数据
    handleCusVarEdit(index, row) {
      this.resetCusVarConf()
      this.caseVarConfForm.idx = index
      this.caseVarConfForm.caseVarVisible = true
      let e = this.caseVarConfForm.caseVarDataForView[index]
      this.caseVarConfForm.caseVarName = e.caseVarName
      let caseVarType = ''
      this.cusFunsData.supportVariableType.forEach(i => {
        if (i.description === e.caseVarType) {
          caseVarType = i.type
        }
      })
      this.caseVarConfForm.caseVarType = caseVarType
      let caseVarValue = ''
      this.cusFunsData.customVariableFunctions.forEach(i => {
        if (i.description === e.caseVarValue) {
          caseVarValue = i.name
        }
      })
      this.caseVarConfForm.caseVarValue = caseVarValue || e.caseVarValue
      if (new RegExp('^变量值类型.*$').test(e.caseVarParam)) {
        this.caseVarConfForm.caseVarValueType = e.caseVarParam.split('=')[1]
      } else if (e.caseVarParam !== '无') {
        let caseVarSupFunParams = []
        e.caseVarParam.split('||').forEach(i => {
          caseVarSupFunParams.push({
            label: i.split('=')[0],
            value: i.slice(i.indexOf('=') + 1)
          })
        })
        this.caseVarConfForm.caseVarSupFunParams = caseVarSupFunParams
      } else {
        this.caseVarConfForm.caseVarSupFunParams = []
      }
      // 加载使用说明
      let idx = this.cusFunsData.customVariableFunctions.findIndex(c => c.name === this.caseVarConfForm.caseVarValue)
      this.customFunInstructions = this.cusFunsData.customVariableFunctions[idx].introduction
    },
    // 上移
    handMoveUpVar(index, row) {
      let objMoveView = this.caseVarConfForm.caseVarDataForView[index]
      let objMove = this.caseVarConfForm.caseVarData[index]
      this.caseVarConfForm.caseVarDataForView.splice(index, 1)
      this.caseVarConfForm.caseVarData.splice(index, 1)
      this.caseVarConfForm.caseVarDataForView.splice(index - 1, 0, objMoveView)
      this.caseVarConfForm.caseVarData.splice(index - 1, 0, objMove)
    },
    // 下移
    handMoveDownVar(index, row) {
      let objMoveView = this.caseVarConfForm.caseVarDataForView[index]
      let objMove = this.caseVarConfForm.caseVarData[index]
      this.caseVarConfForm.caseVarDataForView.splice(index, 1)
      this.caseVarConfForm.caseVarData.splice(index, 1)
      this.caseVarConfForm.caseVarDataForView.splice(index + 1, 0, objMoveView)
      this.caseVarConfForm.caseVarData.splice(index + 1, 0, objMove)
    },
    // 删除用例变量列表中的一行数据
    handleCusVarDel(index, row) {
      this.caseVarConfForm.caseVarDataForView.splice(index, 1)
      this.caseVarConfForm.caseVarData.splice(index, 1)
    },
    // 选择加签触发的事件
    selectSignFuncs() {
      if (this.caseRequestForm.isHasSign === '2' && this.cusFunsData.supportSignFuncs.length === 0) {
        this.submitQuery('signFuncs')
      }
      this.caseRequestForm.signFunc = ''
    },
    // 选择结果断言支持的函数
    handleCurrentChangeComparators(val) {
      this.caseAssertForm.actualValue = ''
      this.caseAssertForm.expectValue = ''
      let idx = this.cusFunsData.supportCustomComparators.findIndex(c => c.name === val)
      this.customFunInstructions = this.cusFunsData.supportCustomComparators[idx].introduction
    },
    // 保存结果断言到列表中
    saveCaseAssertForm(idx) {
      this.$refs['caseAssertForm'].validate(valid => {
        if (valid) {
          let assertType = ''
          this.cusFunsData.supportCustomComparators.forEach(i => {
            if (i.name === this.caseAssertForm.assertType) {
              assertType = i.description
            }
          })
          // idx为-1 表示新增；非-1 表示编辑
          if (idx === -1) {
            // 用于列表展示数据
            this.caseAssertForm.tableDataComparatorsForView.push({
              assertType: assertType,
              actualValue: this.caseAssertForm.actualValue.replace(/[\r\n]/g, '').trim(),
              expectValue: this.caseAssertForm.expectValue,
              comment: this.caseAssertForm.comment.replace(/[\r\n]/g, '').trim()
            })
            // 用于提交接口数据
            this.caseAssertForm.tableDataComparators.push({
              comparator: this.caseAssertForm.assertType,
              check: this.caseAssertForm.actualValue.replace(/[\r\n]/g, '').trim(),
              expect: this.caseAssertForm.expectValue,
              desc: this.caseAssertForm.assertType,
              comment: this.caseAssertForm.comment.replace(/[\r\n]/g, '').trim()
            })
          } else {
            // 用于列表展示数据
            this.$set(this.caseAssertForm.tableDataComparatorsForView, idx, {
              assertType: assertType,
              actualValue: this.caseAssertForm.actualValue.replace(/[\r\n]/g, '').trim(),
              expectValue: this.caseAssertForm.expectValue,
              comment: this.caseAssertForm.comment.replace(/[\r\n]/g, '').trim()
            })
            // 用于提交接口数据
            this.$set(this.caseAssertForm.tableDataComparators, idx, {
              comparator: this.caseAssertForm.assertType,
              check: this.caseAssertForm.actualValue.replace(/[\r\n]/g, '').trim(),
              expect: this.caseAssertForm.expectValue,
              desc: this.caseAssertForm.assertType,
              comment: this.caseAssertForm.comment.replace(/[\r\n]/g, '').trim()
            })
          }
          // 关闭表单
          this.caseAssertForm.caseAssertFormVisible = false
        }
      })
    },
    // 重置结果断言配置表单内容
    resetCaseAssertForm() {
      return new Promise((resolve, reject) => {
        this.resetForm('caseAssertForm')
        this.caseAssertForm.assertType = ''
        this.caseAssertForm.actualValue = ''
        this.caseAssertForm.expectValue = ''
        this.caseAssertForm.comment = ''
        this.caseAssertForm.idx = -1
        resolve(1)
      })
    },
    // 修改结果断言列表中的某条数据
    handleCaseAssertFormEdit(index, row) {
      this.caseAssertForm.idx = index
      this.caseAssertForm.caseAssertFormVisible = true
      let e = this.caseAssertForm.tableDataComparatorsForView[index]
      this.caseAssertForm.actualValue = e.actualValue
      this.caseAssertForm.expectValue = e.expectValue
      this.caseAssertForm.comment = e.comment
      let assertType = ''
      this.cusFunsData.supportCustomComparators.forEach(i => {
        if (i.description === e.assertType) {
          assertType = i.name
        }
      })
      this.caseAssertForm.assertType = assertType
      // 加载使用说明
      let idx = this.cusFunsData.supportCustomComparators.findIndex(c => c.name === this.caseAssertForm.assertType)
      this.customFunInstructions = this.cusFunsData.supportCustomComparators[idx].introduction
    },
    // 上移
    handMoveUpAssert(index, row) {
      let objMoveView = this.caseAssertForm.tableDataComparatorsForView[index]
      let objMove = this.caseAssertForm.tableDataComparators[index]
      this.caseAssertForm.tableDataComparatorsForView.splice(index, 1)
      this.caseAssertForm.tableDataComparators.splice(index, 1)
      this.caseAssertForm.tableDataComparatorsForView.splice(index - 1, 0, objMoveView)
      this.caseAssertForm.tableDataComparators.splice(index - 1, 0, objMove)
    },
    // 下移
    handMoveDownAssert(index, row) {
      let objMoveView = this.caseAssertForm.tableDataComparatorsForView[index]
      let objMove = this.caseAssertForm.tableDataComparators[index]
      this.caseAssertForm.tableDataComparatorsForView.splice(index, 1)
      this.caseAssertForm.tableDataComparators.splice(index, 1)
      this.caseAssertForm.tableDataComparatorsForView.splice(index + 1, 0, objMoveView)
      this.caseAssertForm.tableDataComparators.splice(index + 1, 0, objMove)
    },
    // 删除结果断言列表中的一行数据
    handleCaseAssertFormDel(index, row) {
      this.caseAssertForm.tableDataComparatorsForView.splice(index, 1)
      this.caseAssertForm.tableDataComparators.splice(index, 1)
    },
    // 选择请求前置函数类型触发的事件
    selectCusSetupFuncType(val) {
      this.caseSetupForm.caseSetupFuncParam = []
      let caseSetupFuncType = this.caseSetupForm.caseSetupFuncType
      const caseSetupFuncs = this.cusFunsData.supportSetupFuncs.find(function(x) {
        return x.name === caseSetupFuncType
      })
      caseSetupFuncs.parameters.forEach(i => {
        this.caseSetupForm.caseSetupFuncParam.push({ label: i, value: '' })
      })
      let idx = this.cusFunsData.supportSetupFuncs.findIndex(c => c.name === val)
      this.customFunInstructions = this.cusFunsData.supportSetupFuncs[idx].introduction
    },
    // 保存请求前置函数到列表中
    saveCaseSetupForm(idx) {
      this.$refs['caseSetupForm'].validate(valid => {
        if (valid) {
          let caseSetupFuncParam = ''
          let caseSetupFuncParams = {}
          if (this.caseSetupForm.caseSetupFuncParam.length !== 0) {
            this.caseSetupForm.caseSetupFuncParam.forEach(i => {
              caseSetupFuncParam = caseSetupFuncParam
                ? caseSetupFuncParam + '||' + i.label + '=' + i.value.replace(/[\r\n]/g, '').trim()
                : i.label + '=' + i.value.replace(/[\r\n]/g, '').trim()
              caseSetupFuncParams[i.label] = i.value.replace(/[\r\n]/g, '').trim()
            })
          }
          let caseSetupFuncType = ''
          this.cusFunsData.supportSetupFuncs.forEach(i => {
            if (i.name === this.caseSetupForm.caseSetupFuncType) {
              caseSetupFuncType = i.description
            }
          })
          // idx为-1 表示新增；非-1 表示编辑
          if (idx === -1) {
            // 用于列表展示数据
            this.caseSetupForm.caseSetupFormDataForView.push({
              caseSetupFuncType: caseSetupFuncType,
              caseSetupFuncParam: caseSetupFuncParam || '无'
            })
            // 用于提交接口数据
            this.caseSetupForm.caseSetupFormData.push({
              name: this.caseSetupForm.caseSetupFuncType,
              args: caseSetupFuncParams,
              desc: caseSetupFuncType
            })
          } else {
            // 用于列表展示数据
            this.$set(this.caseSetupForm.caseSetupFormDataForView, idx, {
              caseSetupFuncType: caseSetupFuncType,
              caseSetupFuncParam: caseSetupFuncParam || '无'
            })
            // 用于提交接口数据
            this.$set(this.caseSetupForm.caseSetupFormData, idx, {
              name: this.caseSetupForm.caseSetupFuncType,
              args: caseSetupFuncParams,
              desc: caseSetupFuncType
            })
          }
          // 关闭表单
          this.caseSetupForm.caseSetupFormVisible = false
        }
      })
    },
    // 重置请求前置配置表单内容
    resetCaseSetupForm() {
      return new Promise((resolve, reject) => {
        this.resetForm('caseSetupForm')
        this.caseSetupForm.caseSetupFuncParam = []
        this.caseSetupForm.caseSetupFuncType = ''
        this.caseSetupForm.idx = -1
        resolve(1)
      })
    },
    // 修改请求前置列表中的某条数据
    handleCaseSetupFormEdit(index, row) {
      this.caseSetupForm.idx = index
      this.caseSetupForm.caseSetupFormVisible = true
      let e = this.caseSetupForm.caseSetupFormDataForView[index]
      let caseSetupFuncType = ''
      this.cusFunsData.supportSetupFuncs.forEach(i => {
        if (i.description === e.caseSetupFuncType) {
          caseSetupFuncType = i.name
        }
      })
      this.caseSetupForm.caseSetupFuncType = caseSetupFuncType
      let caseSetupFuncParam = []
      e.caseSetupFuncParam.split('||').forEach(i => {
        caseSetupFuncParam.push({
          label: i.split('=')[0],
          value: i.slice(i.indexOf('=') + 1).replace(/;/g, ';\n')
        })
      })
      this.caseSetupForm.caseSetupFuncParam = caseSetupFuncParam
      // 加载使用说明
      let idx = this.cusFunsData.supportSetupFuncs.findIndex(c => c.name === this.caseSetupForm.caseSetupFuncType)
      this.customFunInstructions = this.cusFunsData.supportSetupFuncs[idx].introduction
    },
    // 上移
    handMoveUpSetup(index, row) {
      let objMoveView = this.caseSetupForm.caseSetupFormDataForView[index]
      let objMove = this.caseSetupForm.caseSetupFormData[index]
      this.caseSetupForm.caseSetupFormDataForView.splice(index, 1)
      this.caseSetupForm.caseSetupFormData.splice(index, 1)
      this.caseSetupForm.caseSetupFormDataForView.splice(index - 1, 0, objMoveView)
      this.caseSetupForm.caseSetupFormData.splice(index - 1, 0, objMove)
    },
    // 下移
    handMoveDownSetup(index, row) {
      let objMoveView = this.caseSetupForm.caseSetupFormDataForView[index]
      let objMove = this.caseSetupForm.caseSetupFormData[index]
      this.caseSetupForm.caseSetupFormDataForView.splice(index, 1)
      this.caseSetupForm.caseSetupFormData.splice(index, 1)
      this.caseSetupForm.caseSetupFormDataForView.splice(index + 1, 0, objMoveView)
      this.caseSetupForm.caseSetupFormData.splice(index + 1, 0, objMove)
    },
    // 删除请求前置列表中的一行数据
    handleCaseSetupFormDel(index, row) {
      this.caseSetupForm.caseSetupFormDataForView.splice(index, 1)
      this.caseSetupForm.caseSetupFormData.splice(index, 1)
    },
    // 添加用例后置支持的函数类型
    selectCustomTeardownHooks(val) {
      this.caseTeardownForm.caseTeardownFuncParam = []
      let caseTeardownFuncType = this.caseTeardownForm.caseTeardownFuncType
      const caseTeardownFuncs = this.cusFunsData.supportTeardownFuncs.find(function(x) {
        return x.name === caseTeardownFuncType
      })
      caseTeardownFuncs.parameters.forEach(i => {
        this.caseTeardownForm.caseTeardownFuncParam.push({ label: i, value: '' })
      })
      let idx = this.cusFunsData.supportTeardownFuncs.findIndex(c => c.name === val)
      this.customFunInstructions = this.cusFunsData.supportTeardownFuncs[idx].introduction
    },
    // 保存用例后置函数到列表中
    saveCaseTeardownForm(idx) {
      this.$refs['caseTeardownForm'].validate(valid => {
        if (valid) {
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
          this.cusFunsData.supportTeardownFuncs.forEach(i => {
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
          // 关闭表单
          this.caseTeardownForm.caseTeardownFormVisible = false
        }
      })
    },
    // 重置用例后置配置表单内容
    resetCaseTeardownForm() {
      return new Promise((resolve, reject) => {
        this.resetForm('caseTeardownForm')
        this.caseTeardownForm.caseTeardownFuncParam = []
        this.caseTeardownForm.caseTeardownFuncType = ''
        this.caseTeardownForm.idx = -1
        resolve(1)
      })
    },
    // 修改用例后置列表中的某条数据
    handleCaseTeardownFormEdit(index, row) {
      this.caseTeardownForm.idx = index
      this.caseTeardownForm.caseTeardownFormVisible = true
      let e = this.caseTeardownForm.caseTeardownFormDataForView[index]
      let caseTeardownFuncType = ''
      this.cusFunsData.supportTeardownFuncs.forEach(i => {
        if (i.description === e.caseTeardownFuncType) {
          caseTeardownFuncType = i.name
        }
      })
      this.caseTeardownForm.caseTeardownFuncType = caseTeardownFuncType
      let caseTeardownFuncParams = []
      e.caseTeardownFuncParam.split('||').forEach(i => {
        caseTeardownFuncParams.push({
          label: i.split('=')[0],
          value: i.slice(i.indexOf('=') + 1).replace(/;/g, ';\n')
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
    // 删除用例后置列表中的一行数据
    handleCaseTeardownFormDel(index, row) {
      this.caseTeardownForm.caseTeardownFormDataForView.splice(index, 1)
      this.caseTeardownForm.caseTeardownFormData.splice(index, 1)
    },
    // 保存提取变量到列表中
    saveCaseExtractVarForm(idx) {
      this.$refs['caseExtractVarForm'].validate(valid => {
        if (valid) {
          // idx为-1 表示新增；非-1 表示编辑
          if (idx === -1) {
            // 用于列表展示数据
            this.caseExtractVarForm.caseExtractVarFormDataForView.push({
              extractVarName: this.caseExtractVarForm.extractVarName.replace(/[\r\n]/g, '').trim(),
              savedVarName: this.caseExtractVarForm.savedVarName.replace(/[\r\n]/g, '').trim()
            })
            // 用于提交接口数据
            this.caseExtractVarForm.caseExtractVarFormData.push({
              check: this.caseExtractVarForm.extractVarName.replace(/[\r\n]/g, '').trim(),
              saveAs: this.caseExtractVarForm.savedVarName.replace(/[\r\n]/g, '').trim()
            })
          } else {
            // 用于列表展示数据
            this.$set(this.caseExtractVarForm.caseExtractVarFormDataForView, idx, {
              extractVarName: this.caseExtractVarForm.extractVarName.replace(/[\r\n]/g, '').trim(),
              savedVarName: this.caseExtractVarForm.savedVarName.replace(/[\r\n]/g, '').trim()
            })
            // 用于提交接口数据
            this.$set(this.caseExtractVarForm.caseExtractVarFormData, idx, {
              check: this.caseExtractVarForm.extractVarName.replace(/[\r\n]/g, '').trim(),
              saveAs: this.caseExtractVarForm.savedVarName.replace(/[\r\n]/g, '').trim()
            })
          }
          // 关闭表单
          this.caseExtractVarForm.caseExtractVarFormVisible = false
        }
      })
    },
    // 重置提取变量配置表单内容
    resetCaseExtractVarForm() {
      return new Promise((resolve, reject) => {
        this.resetForm('caseExtractVarForm')
        this.caseExtractVarForm.extractVarName = ''
        this.caseExtractVarForm.savedVarName = ''
        this.caseExtractVarForm.idx = -1
        resolve(1)
      })
    },
    // 修改提取变量列表中的某条数据
    handleCaseExtractVarFormEdit(index, row) {
      this.caseExtractVarForm.idx = index
      this.caseExtractVarForm.caseExtractVarFormVisible = true
      let e = this.caseExtractVarForm.caseExtractVarFormDataForView[index]
      this.caseExtractVarForm.extractVarName = e.extractVarName
      this.caseExtractVarForm.savedVarName = e.savedVarName
    },
    // 上移
    handMoveUpExtract(index, row) {
      let objMoveView = this.caseExtractVarForm.caseExtractVarFormDataForView[index]
      let objMove = this.caseExtractVarForm.caseExtractVarFormData[index]
      this.caseExtractVarForm.caseExtractVarFormDataForView.splice(index, 1)
      this.caseExtractVarForm.caseExtractVarFormData.splice(index, 1)
      this.caseExtractVarForm.caseExtractVarFormDataForView.splice(index - 1, 0, objMoveView)
      this.caseExtractVarForm.caseExtractVarFormData.splice(index - 1, 0, objMove)
    },
    // 下移
    handMoveDownExtract(index, row) {
      let objMoveView = this.caseExtractVarForm.caseExtractVarFormDataForView[index]
      let objMove = this.caseExtractVarForm.caseExtractVarFormData[index]
      this.caseExtractVarForm.caseExtractVarFormDataForView.splice(index, 1)
      this.caseExtractVarForm.caseExtractVarFormData.splice(index, 1)
      this.caseExtractVarForm.caseExtractVarFormDataForView.splice(index + 1, 0, objMoveView)
      this.caseExtractVarForm.caseExtractVarFormData.splice(index + 1, 0, objMove)
    },
    // 删除提取变量列表中的一行数据
    handleCaseExtractVarFormDel(index, row) {
      this.caseExtractVarForm.caseExtractVarFormDataForView.splice(index, 1)
      this.caseExtractVarForm.caseExtractVarFormData.splice(index, 1)
    },
    // 添加请求后置支持的函数类型
    selectRequestTeardownHooks(val) {
      this.requestTeardownForm.requestTeardownFuncParam = []
      let requestTeardownFuncType = this.requestTeardownForm.requestTeardownFuncType
      const requestTeardownFuncs = this.cusFunsData.supportTeardownFuncs.find(function(x) {
        return x.name === requestTeardownFuncType
      })
      requestTeardownFuncs.parameters.forEach(i => {
        this.requestTeardownForm.requestTeardownFuncParam.push({ label: i, value: '' })
      })
      let idx = this.cusFunsData.supportTeardownFuncs.findIndex(c => c.name === val)
      this.customFunInstructions = this.cusFunsData.supportTeardownFuncs[idx].introduction
    },
    // 保存请求后置函数到列表中
    saveRequestTeardownForm(idx) {
      this.$refs['requestTeardownForm'].validate(valid => {
        if (valid) {
          let requestTeardownFuncParam = ''
          let requestTeardownFuncParams = {}
          if (this.requestTeardownForm.requestTeardownFuncParam.length !== 0) {
            this.requestTeardownForm.requestTeardownFuncParam.forEach(i => {
              requestTeardownFuncParam = requestTeardownFuncParam
                ? requestTeardownFuncParam + '||' + i.label + '=' + i.value.replace(/[\r\n]/g, '').trim()
                : i.label + '=' + i.value.replace(/[\r\n]/g, '').trim()
              requestTeardownFuncParams[i.label] = i.value.replace(/[\r\n]/g, '').trim()
            })
          }
          let requestTeardownFuncType = ''
          this.cusFunsData.supportTeardownFuncs.forEach(i => {
            if (i.name === this.requestTeardownForm.requestTeardownFuncType) {
              requestTeardownFuncType = i.description
            }
          })
          // idx为-1 表示新增；非-1 表示编辑
          if (idx === -1) {
            // 用于列表展示数据
            this.requestTeardownForm.requestTeardownFormDataForView.push({
              requestTeardownFuncType: requestTeardownFuncType,
              requestTeardownFuncParam: requestTeardownFuncParam || '无'
            })
            // 用于提交接口数据
            this.requestTeardownForm.requestTeardownFormData.push({
              name: this.requestTeardownForm.requestTeardownFuncType,
              args: requestTeardownFuncParams,
              desc: requestTeardownFuncType
            })
          } else {
            // 用于列表展示数据
            this.$set(this.requestTeardownForm.requestTeardownFormDataForView, idx, {
              requestTeardownFuncType: requestTeardownFuncType,
              requestTeardownFuncParam: requestTeardownFuncParam || '无'
            })
            // 用于提交接口数据
            this.$set(this.requestTeardownForm.requestTeardownFormData, idx, {
              name: this.requestTeardownForm.requestTeardownFuncType,
              args: requestTeardownFuncParams,
              desc: requestTeardownFuncType
            })
          }
          // 关闭表单
          this.requestTeardownForm.requestTeardownFormVisible = false
        }
      })
    },
    // 重置请求后置配置表单内容
    resetRequestTeardownForm() {
      return new Promise((resolve, reject) => {
        this.resetForm('requestTeardownForm')
        this.requestTeardownForm.requestTeardownFuncParam = []
        this.requestTeardownForm.requestTeardownFuncType = ''
        this.requestTeardownForm.idx = -1
        resolve(1)
      })
    },
    // 修改请求后置列表中的某条数据
    handleRequestTeardownFormEdit(index, row) {
      this.requestTeardownForm.idx = index
      this.requestTeardownForm.requestTeardownFormVisible = true
      let e = this.requestTeardownForm.requestTeardownFormDataForView[index]
      let requestTeardownFuncType = ''
      this.cusFunsData.supportTeardownFuncs.forEach(i => {
        if (i.description === e.requestTeardownFuncType) {
          requestTeardownFuncType = i.name
        }
      })
      this.requestTeardownForm.requestTeardownFuncType = requestTeardownFuncType
      let requestTeardownFuncParams = []
      e.requestTeardownFuncParam.split('||').forEach(i => {
        requestTeardownFuncParams.push({
          label: i.split('=')[0],
          value: i.slice(i.indexOf('=') + 1).replace(/;/g, ';\n')
        })
      })
      this.requestTeardownForm.requestTeardownFuncParam = requestTeardownFuncParams
      // 加载使用说明
      let idx = this.cusFunsData.supportTeardownFuncs.findIndex(c => c.name === this.requestTeardownForm.requestTeardownFuncType)
      this.customFunInstructions = this.cusFunsData.supportTeardownFuncs[idx].introduction
    },
    // 上移
    handMoveUpRequestTeardown(index, row) {
      let objMoveView = this.requestTeardownForm.requestTeardownFormDataForView[index]
      let objMove = this.requestTeardownForm.requestTeardownFormData[index]
      this.requestTeardownForm.requestTeardownFormDataForView.splice(index, 1)
      this.requestTeardownForm.requestTeardownFormData.splice(index, 1)
      this.requestTeardownForm.requestTeardownFormDataForView.splice(index - 1, 0, objMoveView)
      this.requestTeardownForm.requestTeardownFormData.splice(index - 1, 0, objMove)
    },
    // 下移
    handMoveDownRequestTeardown(index, row) {
      let objMoveView = this.requestTeardownForm.requestTeardownFormDataForView[index]
      let objMove = this.requestTeardownForm.requestTeardownFormData[index]
      this.requestTeardownForm.requestTeardownFormDataForView.splice(index, 1)
      this.requestTeardownForm.requestTeardownFormData.splice(index, 1)
      this.requestTeardownForm.requestTeardownFormDataForView.splice(index + 1, 0, objMoveView)
      this.requestTeardownForm.requestTeardownFormData.splice(index + 1, 0, objMove)
    },
    // 删除请求后置列表中的一行数据
    handleRequestTeardownFormDel(index, row) {
      this.requestTeardownForm.requestTeardownFormDataForView.splice(index, 1)
      this.requestTeardownForm.requestTeardownFormData.splice(index, 1)
    },

    // 保存测试用例编辑表单内容
    saveTestCaseInfo() {
      const newArr = [] // 承接promise的返回结果
      const _self = this

      /* ['caseBasicForm', 'caseRequestForm'].forEach((item) => {
                    checkForm(item)
                })*/
      function checkForm(arrName) {
        // 动态生成promise，再对其表单校验，都通过了再去做处理
        var result = new Promise(function(resolve, reject) {
          if (_self.$refs[arrName] !== undefined) {
            _self.$refs[arrName].validate(valid => {
              if (valid) {
                resolve()
              } else {
                reject(arrName + ' is not valid')
              }
            })
          } else {
            resolve()
          }
        })
        newArr.push(result) // push 得到promise的结果
      }

      checkForm('caseBasicForm')
      checkForm('caseRequestForm')

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
      this.testCaseDetail = {}
      // 基础信息
      const baseInfo = {}
      baseInfo.testcaseName = this.caseBasicForm.caseName
      baseInfo.expectResult = this.caseBasicForm.caseExpectResult
      baseInfo.testcaseDesc = this.caseBasicForm.caseDesc
      this.testCaseDetail.base = baseInfo
      // 组装请求信息
      let sign = {}
      this.cusFunsData.supportSignFuncs.forEach(i => {
        if (i.name === this.caseRequestForm.signFunc) {
          sign.desc = i.description
          sign.name = i.name
        }
      })
      this.caseRequestForm.requestInfo = JSON.stringify(JSON.parse(this.caseRequestForm.requestInfo), null, 0)
      this.caseRequestForm.requestDetail = {
        json: this.caseRequestForm.requestInfo,
        sign: sign,
        type: this.caseRequestForm.isHasSign === '1' ? 1 : 2,
        isMerge: this.caseRequestForm.isMerge
      }
      // 处理结果断言
      const validateInfo = []
      this.caseAssertForm.tableDataComparators.forEach(item => {
        const validate = {}
        validate['comparator'] = item.comparator
        validate['check'] = item.check
        validate['expect'] = item.expect
        validate['desc'] = item.comparator
        validate['comment'] = item.comment
        validateInfo.push(validate)
      })
      this.testCaseDetail.steps = []
      this.testCaseDetail.steps.push({
        setupInfo: this.caseSetupForm.caseSetupFormData, // 请求前置
        variableInfo: this.caseVarConfForm.caseVarData, // 用例变量
        requestInfo: this.caseRequestForm.requestDetail, // 请求信息
        validateInfo: validateInfo, // 结果断言
        extractInfo: this.caseExtractVarForm.caseExtractVarFormData, // 提取变量
        teardownInfo: this.caseTeardownForm.caseTeardownFormData, // 用例后置
        requestTeardownInfo: this.requestTeardownForm.requestTeardownFormData // 请求后置
      })
      this.testCaseDetail.include = []
      this.$emit('update-data', this.testCaseDetail)
    },
    // 重置表单
    resetForm(formName) {
      if (this.$refs[formName] !== undefined) {
        this.$refs[formName].resetFields()
      }
    },
    // 格式化入参函数
    formatIntfParms() {
      this.$refs['caseRequestForm'].validate(valid => {
        if (valid) {
          if (this.caseRequestForm.butFlag) {
            // this.caseRequestForm.requestInfo = JSON.stringify(JSON.parse(this.caseRequestForm.requestInfo), null, 4)
            this.caseRequestForm.requestInfo = getFormatJsonStrFromString(this.caseRequestForm.requestInfo)
            this.caseRequestForm.butLabel = '还原入参'
          } else {
            // this.caseRequestForm.requestInfo = JSON.stringify(JSON.parse(this.caseRequestForm.requestInfo), null, 0)
            this.caseRequestForm.requestInfo = this.caseRequestForm.requestInfo.replace(/[\r\n]/g, '').replace(/{(\s*)"/g, '{"').replace(/,(\s*)"/g, ',"').trim()
            this.caseRequestForm.butLabel = '格式化入参'
          }
          this.caseRequestForm.butFlag = !this.caseRequestForm.butFlag
        }
      })
    },
    // 取消用例变量编辑操作
    cancelCaseVarConf() {
      this.resetCusVarConf().then(() => {
        this.caseVarConfForm.caseVarVisible = false
      })
    },
    // 取消请求前置编辑操作
    cancelCaseSetupConf() {
      this.resetCaseSetupForm().then(() => {
        this.caseSetupForm.caseSetupFormVisible = false
      })
    },
    // 取消提取变量编辑操作
    cancelCaseExtractVarConf() {
      this.resetCaseExtractVarForm().then(() => {
        this.caseExtractVarForm.caseExtractVarFormVisible = false
      })
    },
    // 取消结果验证编辑操作
    cancelCaseAssertConf() {
      this.resetCaseAssertForm().then(() => {
        this.caseAssertForm.caseAssertFormVisible = false
      })
    },
    // 取消用例后置编辑操作
    cancelCaseTeardownConf() {
      this.resetCaseTeardownForm().then(() => {
        this.caseTeardownForm.caseTeardownFormVisible = false
      })
    },
    // 取消请求后置编辑操作
    cancelRequestTeardownConf() {
      this.resetRequestTeardownForm().then(() => {
        this.requestTeardownForm.requestTeardownFormVisible = false
      })
    }
  },
  watch: {
    'caseBasicForm.caseName': function() {
      if (this.testCaseInfo && !this.testCaseInfo.base.hasOwnProperty('testcaseId')) {
        this.saveTestCaseInfo()
      }
    },
    'caseBasicForm.caseExpectResult': function() {
      if (this.testCaseInfo && !this.testCaseInfo.base.hasOwnProperty('testcaseId')) {
        this.saveTestCaseInfo()
      }
    },
    'caseBasicForm.caseDesc': function() {
      if (this.testCaseInfo && !this.testCaseInfo.base.hasOwnProperty('testcaseId')) {
        this.saveTestCaseInfo()
      }
    },
    'caseVarConfForm.caseVarData': function() {
      if (this.testCaseInfo && !this.testCaseInfo.base.hasOwnProperty('testcaseId')) {
        this.saveTestCaseInfo()
      }
    },
    'caseSetupForm.caseSetupFormData': function() {
      if (this.testCaseInfo && !this.testCaseInfo.base.hasOwnProperty('testcaseId')) {
        this.saveTestCaseInfo()
      }
    },
    'caseRequestForm.requestInfo': function() {
      if (this.testCaseInfo && !this.testCaseInfo.base.hasOwnProperty('testcaseId')) {
        this.saveTestCaseInfo()
      }
    },
    'caseRequestForm.isHasSign': function() {
      if (this.testCaseInfo && !this.testCaseInfo.base.hasOwnProperty('testcaseId')) {
        this.saveTestCaseInfo()
      }
    },
    'caseRequestForm.signFunc': function() {
      if (this.testCaseInfo && !this.testCaseInfo.base.hasOwnProperty('testcaseId')) {
        this.saveTestCaseInfo()
      }
    },
    'caseRequestForm.isMerge': function() {
      if (this.testCaseInfo && !this.testCaseInfo.base.hasOwnProperty('testcaseId')) {
        this.saveTestCaseInfo()
      }
    },
    'caseExtractVarForm.caseExtractVarFormData': function() {
      if (this.testCaseInfo && !this.testCaseInfo.base.hasOwnProperty('testcaseId')) {
        this.saveTestCaseInfo()
      }
    },
    'caseAssertForm.tableDataComparators': function() {
      if (this.testCaseInfo && !this.testCaseInfo.base.hasOwnProperty('testcaseId')) {
        this.saveTestCaseInfo()
      }
    },
    'caseTeardownForm.caseTeardownFormData': function() {
      if (this.testCaseInfo && !this.testCaseInfo.base.hasOwnProperty('testcaseId')) {
        this.saveTestCaseInfo()
      }
    }
  }
}
</script>

<style lang="scss">
/*页面边框*/
.caseEditForm {
  border: 1px solid #ebebeb;
  border-radius: 3px;
  transition: 0.2s;
  .source {
    padding: 15px;
  }
}

/*页面输入框样式*/
.caseEditForm .el-input,
.caseEditForm .el-textarea {
  width: 80%;
}

.caseEditForm .el-select .el-input {
  width: 100%;
}

/* 用例编辑页面各元素样式 */
.caseEditForm .el-collapse {
  .el-collapse-item__header {
    margin-top: 10px;
    height: 30px;
    line-height: 30px;
    color: #409eff;
    cursor: pointer;
    /*border-bottom: 1px solid #ebeef5;*/
    font-size: 14px;
    background-color: #ebeef5;
    .el-collapse-item__arrow {
      line-height: 40px;
    }
  }
  .el-collapse-item__content {
    margin-top: 10px;
    padding-bottom: 0;
  }
}

.el-table .warning-row {
  background: oldlace;
}

.el-collapse-item__content .el-form.el-form-item--mini.el-form-item,
.el-collapse-item__content .el-form .el-form-item--small.el-form-item {
  margin-bottom: 15px;
}

.header-icon {
  color: #409eff;
}
</style>
