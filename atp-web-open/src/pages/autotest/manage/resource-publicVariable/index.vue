<template>
  <d2-container>
    <div class="table_container">
      <div class="handle-box">
        <el-form ref="baseForm" :modle="baseForm" class="demo-form-inline" label-width="80px" inline>
          <el-form-item label="变量名称">
            <el-input placeholder="请输入变量名称、类型、值搜索" v-model="searchKeywords" class="handle-input mr10"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="el-icon-search" @click="queryData()" :loading="searchLoading">搜 索</el-button>
            <el-button type="primary" @click="addvariable()">新增变量</el-button>
          </el-form-item>
        </el-form>
      </div>
      <el-table :data="tableData" border style="width: 100%" ref="multipleTable" :header-cell-style="{color:'black',background:'#eef1f6'}" size="medium">
        <el-table-column type="index" width="50"></el-table-column>
        <el-table-column prop="name" label="变量名称" sortable width="250">
          <template slot-scope="scope">
            <span style="font-weight: bold;color: red" v-if="/^[A-Z_][A-Z0-9_]*$/.test(scope.row.name)">{{ scope.row.name }}</span>
            <span v-else>{{ scope.row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="type_desc" label="变量类型" width="100"></el-table-column>
        <el-table-column prop="value" label="变量的值" width="600"></el-table-column>
        <el-table-column prop="simple_Desc" label="说明" width="250"></el-table-column>
        <el-table-column prop="system_name" label="所属工程"></el-table-column>
        <el-table-column prop="company_name" label="所属公司"></el-table-column>
        <el-table-column prop="creator" label="创建者"></el-table-column>
        <el-table-column label="操作">
          <template slot-scope="scope">
            <el-button type="text" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
            <el-button type="text" @click="handleDelete(scope.$index, scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <!--分页-->
      <div class="pagination" style="margin-top: 20px">
        <el-pagination
          @current-change="handleCurrentChange"
          @size-change="handleSizeChange"
          layout="total, sizes, prev, pager, next, jumper"
          :total="totalCount"
          :current-page="currentPage"
          :page-sizes="[5, 10, 15, 20]"
          :page-size="pagesize"
        ></el-pagination>
      </div>
    </div>
    <!--编辑变量框-->
    <el-dialog title="编辑变量" :visible.sync="editVisible" width="40%" :close-on-click-modal="false" :close-on-press-escape="false" ref="editDialog">
      <el-form ref="editForm" :model="editForm" label-width="120px">
        <el-form-item label="公司名称" prop="companyId" :rules="[{ required: true, message: '公司名称必填', trigger: 'change' }]">
          <el-select v-model="editForm.companyId" placeholder="请选择" @change="getSystem(editForm.companyId)">
            <el-option v-for="item in baseForm.companyOptions" :key="item.companyName" :label="item.companyName" :value="item.companyId"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="工程名称" prop="systemId">
          <el-select v-model="editForm.systemId" placeholder="请选择" clearable filterable>
            <el-option v-for="item in baseForm.systemOptions" :key="item.label" :label="item.label" :value="item.systemId"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="变量名称" prop="variable_name" :rules="[{ required: true, message: '变量名称必填', trigger: 'blur' }]">
          <el-input v-model="editForm.variable_name" style="width: 80%"></el-input>
        </el-form-item>
        <el-form-item label="变量类型" prop="variable_type" :rules="[{ required: true, message: '变量类型必选', trigger: 'change' }]">
          <el-select v-model="editForm.variable_type" placeholder="请选择变量类型" @change="selectVariableType()">
            <el-option label="key-value" value="constant"></el-option>
            <el-option label="数据库操作" value="db"></el-option>
            <el-option label="特定函数" value="function"></el-option>
            <el-option label="文件类型" value="files"></el-option>
          </el-select>
        </el-form-item>
        <!--函数支持下拉选择 -->
        <el-form ref="funtionFormRef" :model="editForm" v-show="customFunsData.show" label-width="120px">
          <el-form-item label="函数类型" prop="functionName" :rules="[{ required: true, message: '请选择函数类型', trigger: 'change'}]">
            <el-select v-model="editForm.functionName" placeholder="请选择" @change="selectCustomFuns">
              <el-option v-for="item in customFunsData.customVariableFunctions" :key="item.key" :label="item.description" :value="item.name"></el-option>
            </el-select>
            <el-popover placement="right" width="600" trigger="hover" style="margin-left: 20px" v-if="editForm.functionName !== ''">
              <el-form labelWidth="100px" labelPosition="left" labelSuffix=":">
                <el-form-item v-for="(item, index) in customFunInstructions" :label="item.label" :key="index">
                  <span>{{item.value}}</span>
                </el-form-item>
              </el-form>
              <el-button type="text" slot="reference">使用说明</el-button>
            </el-popover>
          </el-form-item>
          <!--函数的参数-->
          <el-form-item
            v-for="(param, index) in customFunsData.parameters"
            :label="param.label"
            :key="param.index"
            :rules="{required: true, message: param.label + '不能为空', trigger: 'blur'}"
          >
            <el-input type="textarea" autosize style="width: 80%" v-model="param.value"></el-input>
          </el-form-item>
        </el-form>
        <!--函数支持下拉选择-->
        <el-form-item
          label="变量的值"
          v-if="editForm.constantVisible"
          prop="variable_value"
          :rules="[{ required: editForm.constantVisible, message: '变量的值必填', trigger: 'blur' }]"
        >
          <el-input type="textarea" autosize v-model="editForm.variable_value" style="width: 80%"></el-input>
        </el-form-item>
        <el-form-item
          label="变量值类型"
          prop="variableValueType"
          :rules="[{ required: true, message: '变量值类型必选', trigger: 'change' }]"
          v-if="editForm.variable_type === 'constant'"
        >
          <el-select v-model="editForm.variableValueType" placeholder="请选择变量值类型">
            <el-option label="数字" value="num"></el-option>
            <el-option label="字符串" value="str"></el-option>
            <el-option label="布尔型" value="bool"></el-option>
            <el-option label="数组" value="list"></el-option>
            <el-option label="对象" value="dict"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="描述信息" prop="simpleDesc">
          <el-input v-model="editForm.simpleDesc" type="textarea" :autosize="{ minRows: 2, maxRows: 5}" style="width: 80%"></el-input>
        </el-form-item>
        <!--上传文件-->
        <el-form-item label="上传图片列表" v-if="editForm.fileVisible" prop="variable_value" :rules="[{ required: true, message: '请上传一个文件', trigger: 'blur' }]">
          <el-upload
            class="upload-demo"
            :action="importFileUrl"
            name="file"
            :on-preview="handlePreview"
            :on-remove="handleRemove"
            :on-success="handSuccess"
            list-type="picture"
            :file-list="editForm.filelist"
          >
            <el-button size="small" type="primary">点击上传</el-button>
          </el-upload>
        </el-form-item>
        <!--上传文件-->
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="editVisible = false">取 消</el-button>
        <el-button type="primary" @click="saveEdit('editForm')">确 定</el-button>
      </div>
    </el-dialog>
    <!--删除提示框-->
    <el-dialog title="提示" :visible.sync="delVisible" width="300px" center>
      <div class="del-dialog-cnt">删除不可恢复，是否确定删除？</div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="delVisible = false">取 消</el-button>
        <el-button type="primary" @click="deleteRow()">确 定</el-button>
      </span>
    </el-dialog>
  </d2-container>
</template>
<script>
import { fetchPublicvariableList, addPublicvariable, editPublicvariable, deleteVariable } from '@/api/autotest/manage/resource-publicVariable'
/* import {fetchProjectList,subtreeProject} from '@/api/autotest/manage/resource-projectManage'*/
import { fetchCompanyList, subtree } from '@/api/autotest/manage/resource-apiManage/company'
import { compare, isJsonString } from '@/libs/common'
import { queryCustomFunctions } from '@/api/autotest/manage/testcase-testCaseConfig/testcase'

export default {
  name: 'publicVariable',
  data() {
    return {
      importFileUrl: '/atp/auto/file/upload',
      customFunsData: {
        customVariableFunctions: [],
        funcName: '',
        show: false,
        parameters: []
      },
      baseForm: {
        variable_name: '',
        companyOptions: [],
        systemOptions: []
      },
      currentPage: 1,
      pagesize: 10,
      totalCount: 100,
      searchKeywords: '',
      editVisible: false,
      delVisible: false,
      editForm: {
        variable_name: '',
        variable_value: '',
        simpleDesc: '',
        variable_type: '',
        variable_id: '',
        inputValue: '',
        filelist: [], // 编辑框中，展示文件列表
        companyId: '',
        systemId: '',
        functionName: '',
        args: {},
        isNotFile: true,
        constantVisible: true,
        fileVisible: false,
        variableValueType: '' // 如果变量类型为constant，用于标记变量值所属的数据类型
      },
      idx: -1,
      searchLoading: false,
      tableData: [],
      customFunInstructions: [] // 自定义函数使用说明
    }
  },
  mounted() {
    this.queryData()
    this.getCompany() // 获取公司列表
    this.queryCustomFunctions()
  },
  /* computed: {
            tableData () {
                // 在vuex,getters获取数据
                return this.$store.getters['d2admin/casetable/PublicVariabletableData']
            },
        },*/
  methods: {
    /* ...mapMutations({setPublicVariable: 'd2admin/casetable/setPublicVariable'}),*/
    // 查询自定义函数
    queryCustomFunctions() {
      queryCustomFunctions({}).then(res => {
        this.customFunsData.customVariableFunctions = res.data
      })
    },
    // 选择自定义函数触发参数输入框个数
    selectCustomFuns(val) {
      this.customFunsData.parameters = []
      const item = this.customFunsData.customVariableFunctions.find(element => element.name === this.editForm.functionName)
      item.parameters.forEach(name => {
        this.customFunsData.parameters.push({
          label: name,
          value: ''
        })
      })
      let idx = this.customFunsData.customVariableFunctions.findIndex(c => c.name === val)
      this.customFunInstructions = this.customFunsData.customVariableFunctions[idx].introduction
    },
    addvariable() {
      // this.resetForm('baseForm')
      this.editVisible = true
      this.editForm.variable_name = ''
      this.editForm.variable_type = ''
      this.editForm.variable_value = ''
      this.editForm.variableValueType = ''
      this.editForm.simpleDesc = ''
      this.editForm.filelist = []
      this.editForm.companyId = ''
      this.editForm.systemId = ''
      this.editForm.functionName = ''
      this.editForm.args = {}
      this.editForm.constantVisible = true
      this.editForm.fileVisible = false
      this.customFunsData.show = false
      this.idx = -1
      this.customFunsData.parameters = []
    },
    /* 选择变量类型触发事件*/
    selectVariableType() {
      if (this.editForm.variable_type === 'function') {
        this.editForm.constantVisible = false
        this.editForm.fileVisible = false
        this.customFunsData.show = true
      } else if (this.editForm.variable_type === 'files') {
        this.editForm.fileVisible = true
        this.editForm.constantVisible = false
        this.customFunsData.show = false
      } else {
        this.editForm.constantVisible = true
        this.customFunsData.show = false
        this.editForm.fileVisible = false
      }
    },
    // 获取公司列表
    getCompany() {
      fetchCompanyList({}).then(res => {
        this.baseForm.companyOptions = res.companyList.sort(compare('companyName'))
      })
    },
    getSystem(id) {
      subtree({ companyId: id }).then(res => {
        this.baseForm.systemOptions = res.data
      })
    },
    // 删除文件触发事件
    handleRemove(file, fileList) {
      this.editForm.variable_value.splice(this.editForm.variable_value.indexOf(file.name), 1)
    },
    handlePreview(file) {},
    // 上传成功,忽略文件列表已存在文件
    handSuccess(response, file, fileList) {
      console.log(this.editForm.variable_value)
      if (this.editForm.variable_value.length === 0) {
        this.editForm.variable_value = []
      }
      if (this.editForm.variable_value.indexOf(response.desc) === -1) {
        this.editForm.variable_value.push(response.desc)
      }
    },
    // 搜索
    queryData() {
      this.currentPage = 1
      this.searchLoading = true
      this.tableData = []
      this.getPublicDataList().then(res => {
        this.searchLoading = false
      })
    },
    getPublicDataList() {
      return new Promise((resolve, reject) => {
        fetchPublicvariableList({ page: this.currentPage, num: this.pagesize, keywords: this.searchKeywords }).then(res => {
          this.totalCount = res.total
          this.tableData = res.desc
          //                        this.setPublicVariable(res.desc)
          resolve(1)
        })
      })
    },
    handleEdit(index, row) {
      this.editVisible = true
      this.idx = index
      const item = this.tableData[index]
      const filelistVisible = []
      if (item.type === 'files') {
        item.value.forEach(file => {
          var pictureUrl = 'http://192.168.10.54:8899/upload/' + file.slice(-14)
          filelistVisible.push({ name: file, url: pictureUrl })
        })
        this.editForm.fileVisible = true
        this.editForm.constantVisible = false
      } else if (item.type === 'function') {
        this.customFunsData.show = true
        this.editForm.constantVisible = false
        this.editForm.fileVisible = false
        this.editForm.functionName = item.value
        // 回填函数类型和参数
        this.customFunsData.parameters = []
        const argsList = this.customFunsData.customVariableFunctions.find(element => element.name === item.value)
        argsList.parameters.forEach(name => {
          this.customFunsData.parameters.push({
            label: name,
            value: item.args[name]
          })
        })
      } else if (item.type === 'db' || item.type === 'constant') {
        this.editForm.constantVisible = true
        this.editForm.fileVisible = false
      }
      this.getSystem(item.company_id)
      this.editForm.variable_name = item.name
      this.editForm.variable_type = item.type
      this.editForm.variable_value = item.value
      this.editForm.variable_id = item.variable_id
      this.editForm.filelist = filelistVisible
      this.editForm.companyId = item.company_id
      this.editForm.systemId = item.system_id
      this.editForm.simpleDesc = item.simple_Desc
      this.editForm.args = {}
      if (this.editForm.variable_type === 'constant') {
        this.editForm.variableValueType = item.saveAs
      }
    },
    handleDelete(index, row) {
      this.idx = index
      const item = this.tableData[index]
      this.editForm = {
        variable_id: item.variable_id
      }
      this.delVisible = true
    },
    saveEdit(formName) {
      this.$refs[formName].validate(valid => {
        this.customFunsData.parameters.forEach(item => {
          this.editForm.args[item.label] = item.value
        })
        if (this.editForm.variable_type === 'function') {
          this.editForm.variable_value = this.editForm.functionName
        }
        if (valid) {
          if (this.idx === -1) {
            let args = {}
            if (this.editForm.variable_type === 'constant') {
              if (this.editForm.caseVarValueType === 'num' && isNaN(Number(this.editForm.variable_value))) {
                this.$message.warning('变量值请输入数字')
                return false
              }
              if (this.editForm.caseVarValueType === 'bool' && this.editForm.variable_value !== 'True' && this.editForm.variable_value !== 'False') {
                this.$message.warning('变量值请输入True/False')
                return false
              }
              if (this.editForm.caseVarValueType === 'list') {
                if (!isJsonString(this.editForm.variable_value)) {
                  this.$message.warning('变量值请输入list格式')
                  return false
                } else if (Object.prototype.toString.call(JSON.parse(this.editForm.variable_value)).toLowerCase() !== '[object array]') {
                  this.$message.warning('变量值请输入list格式')
                  return false
                }
              }
              if (this.editForm.caseVarValueType === 'dict') {
                if (!isJsonString(this.editForm.variable_value)) {
                  this.$message.warning('变量值请输入dict格式')
                  return false
                } else if (Object.prototype.toString.call(JSON.parse(this.editForm.variable_value)).toLowerCase() !== '[object object]') {
                  this.$message.warning('变量值请输入dict格式')
                  return false
                }
              }
              args.variableName = this.editForm.variable_name
              args.variableType = this.editForm.variable_type
              args.value = this.editForm.variable_value
              args.saveAs = this.editForm.variableValueType
              args.simpleDesc = this.editForm.simpleDesc
              args.companyId = this.editForm.companyId
              args.systemId = this.editForm.systemId
              args.args = this.editForm.args
            } else {
              args.variableName = this.editForm.variable_name
              args.variableType = this.editForm.variable_type
              args.value = this.editForm.variable_value
              args.simpleDesc = this.editForm.simpleDesc
              args.companyId = this.editForm.companyId
              args.systemId = this.editForm.systemId
              args.args = this.editForm.args
            }
            addPublicvariable(args).then(res => {
              this.$message.success(res.desc)
              this.editVisible = false
              this.getPublicDataList()
              // this.$store.commit("addPublicVariable",this.editForm)
            })
          } else {
            let args = {}
            if (this.editForm.variable_type === 'constant') {
              if (this.editForm.variableValueType === 'num' && isNaN(Number(this.editForm.variable_value))) {
                this.$message.warning('变量值请输入数字')
                return false
              }
              if (this.editForm.variableValueType === 'bool' && this.editForm.variable_value !== 'True' && this.editForm.variable_value !== 'False') {
                this.$message.warning('变量值请输入True/False')
                return false
              }
              if (this.editForm.variableValueType === 'list') {
                if (!isJsonString(this.editForm.variable_value)) {
                  this.$message.warning('变量值请输入list格式')
                  return false
                } else if (Object.prototype.toString.call(JSON.parse(this.editForm.variable_value)).toLowerCase() !== '[object array]') {
                  this.$message.warning('变量值请输入list格式')
                  return false
                }
              }
              if (this.editForm.variableValueType === 'dict') {
                if (!isJsonString(this.editForm.variable_value)) {
                  this.$message.warning('变量值请输入dict格式')
                  return false
                } else if (Object.prototype.toString.call(JSON.parse(this.editForm.variable_value)).toLowerCase() !== '[object object]') {
                  this.$message.warning('变量值请输入dict格式')
                  return false
                }
              }
              args.id = this.editForm.variable_id
              args.variableName = this.editForm.variable_name
              args.variableType = this.editForm.variable_type
              args.value = this.editForm.variable_value
              args.saveAs = this.editForm.variableValueType
              args.simpleDesc = this.editForm.simpleDesc
              args.companyId = this.editForm.companyId
              args.systemId = this.editForm.systemId
              args.args = this.editForm.args
            } else {
              args.id = this.editForm.variable_id
              args.variableName = this.editForm.variable_name
              args.variableType = this.editForm.variable_type
              args.value = this.editForm.variable_value
              args.simpleDesc = this.editForm.simpleDesc
              args.companyId = this.editForm.companyId
              args.systemId = this.editForm.systemId
              args.args = this.editForm.args
            }
            editPublicvariable(args).then(res => {
              this.$message.success(res.desc)
              this.editVisible = false
              this.getPublicDataList()
            })
          }
        }
      })
    },
    deleteRow() {
      deleteVariable({
        variableId: this.editForm.variable_id
        /* systemId:this.editForm.systemId*/
      }).then(res => {
        this.$message.success(res.desc)
        this.getPublicDataList()
      })
      this.delVisible = false
    },
    handleSizeChange(val) {
      this.pagesize = val
      this.getPublicDataList()
    },
    handleCurrentChange(val) {
      this.currentPage = val
      this.getPublicDataList()
    },
    // 重置表单
    resetForm(formName) {
      this.$refs[formName].resetFields()
    }
  }
}
</script>

<style lang="scss" scoped>
.table_container {
  padding: 10px;
}

.handle-box {
  margin-bottom: 20px;
}

.handle-input {
  width: 260px;
  display: inline-block;
}

/*.demo-form-inline{*/
/*padding: 20px;*/
/*}*/
</style>
