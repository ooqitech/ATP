<template>
  <div class="fillcontain">
    <el-form v-show="caseFormShow" size="mini">
      <el-collapse v-model="activeNames">
        <el-collapse-item v-show="tabVisible[0].value" name="1">
          <template slot="title">
            <span>添加页面元素</span>
            <el-tooltip placement="top" content="添加" effect="light">
              <el-button type="primary" size="mini" style="margin-left: 20px" icon="el-icon-plus" @click.stop="addPageObject()" plain></el-button>
            </el-tooltip>
          </template>
          <el-card class="box-card" v-if="cardShow">
            <div slot="header">
              <span>编辑元素</span>
            </div>
            <el-form :ref="tableData[cardIndex].formRef" :model="tableData[cardIndex]" label-width="100px" inline>
              <el-form-item label="元素名称" prop="object_name" :rules="[{required: true, message: '保存变量不能为空', trigger: 'blur'}]">
                <el-input type="textarea" autosize style="width: 100%" v-model="tableData[cardIndex].object_name"></el-input>
              </el-form-item>
              <el-form-item label="定位方式" prop="object_by" :rules="[{required: true, message: '保存变量不能为空', trigger: 'blur'}]">
                <el-select v-model="tableData[cardIndex].object_by" placeholder="请选择操作类型" style="width: 100%">
                  <el-option label="xpath" value="xpath"></el-option>
                  <el-option label="text" value="text"></el-option>
                  <el-option label="id" value="id"></el-option>
                  <el-option label="tagname" value="tagname"></el-option>
                  <el-option label="classname" value="classname"></el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="输入值" prop="object_value">
                <el-input type="textarea" autosize style="width: 50%" v-model="tableData[cardIndex].object_value"></el-input>
                <el-tooltip placement="top" content="移除" effect="light">
                  <el-button type="info" size="mini" style="margin-left: 20px" icon="el-icon-minus" @click.prevent="removePageObject()" plain></el-button>
                </el-tooltip>
                <el-tooltip placement="top" content="保存" effect="light">
                  <el-button type="info" size="mini" style="margin-left: 20px" icon="el-icon-circle-check" @click.prevent="savePageObject()" plain>保存</el-button>
                </el-tooltip>
              </el-form-item>
            </el-form>
          </el-card>
        </el-collapse-item>
      </el-collapse>
      <el-table
        :data="tableData"
        border
        style="width: 100%;margin-top: 5px"
        ref="multipleTable"
        :header-cell-style="{color:'black',background:'#eef1f6'}"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="80"></el-table-column>
        <el-table-column prop="id" label="元素编号" width="100"></el-table-column>
        <el-table-column prop="object_name" label="元素名称" width="auto"></el-table-column>
        <el-table-column prop="object_by" label="定位方式" width="100"></el-table-column>
        <el-table-column prop="object_value" label="value" width="auto"></el-table-column>
        <el-table-column prop="simple_desc" label="描述信息" width="auto"></el-table-column>
        <el-table-column label="操作" fixed="right" width="200">
          <template slot-scope="scope">
            <el-button size="mini" type="primary" icon="el-icon-edit" @click="handleEditElement(scope.$index, scope.row)" plain></el-button>
            <el-button size="mini" style="margin-left: 10px" type="danger" icon="el-icon-delete" @click="handleDeleteElement(scope.$index, scope.row)" plain></el-button>
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
    </el-form>
    <!-- 删除提示框 -->
    <el-dialog title="提示" :visible.sync="delVisible" width="300px" center>
      <div class="del-dialog-cnt">删除不可恢复，是否确定删除？</div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="delVisible = false">取 消</el-button>
        <el-button type="danger" icon="el-icon-warning" @click="deletePageObject()">删 除</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { mapState, mapMutations } from 'vuex'
import { addPageElement, editPageElement, deletePageElement, fetchPageElements } from '@/api/autotest/manage/testcase-testCaseConfig/pageobject'
export default {
  name: 'index',
  data() {
    return {
      cardShow: false,
      cardIndex: '',
      reportUrl: '',
      reportUrltest: 'http://99.48.58.241:8899/reports/uireport/test-2018-12-19-10-59.html',
      selectedItem: [],
      testcaseId: '',
      baseForm: '',
      tableData: [],
      caseEditVisible: false,
      currentPage: 1,
      totalCount: 10,
      pagesize: 100,
      caseFormShow: false,
      searchKeywords: '',
      activeNames: ['1'],
      tabVisible: [{ label: 'steps', displayName: '操作步骤', value: true }],
      makeStepsData: [],
      makeStepsTableData: [],
      caseInfo: {},
      multipleSelection: [],
      testcaseList: [],
      reportUrlVisible: false,
      idx: -1,
      delVisible: false
    }
  },

  computed: {
    ...mapState('d2admin/casetable', ['pageObjectTable', 'addUiCaseVisible'])
  },
  methods: {
    ...mapMutations({
      addUiCase: 'd2admin/casetable/addUiCase'
    }),
    queryPageObject() {
      fetchPageElements({
        pageId: this.pageObjectTable.pageId
      }).then(res => {
        this.tableData = res.desc
      })
    },

    // 分页导航
    handleCurrentChange(val) {
      this.currentPage = val
      this.queryPageObject()
    },
    handleSizeChange(val) {
      this.pagesize = val
      this.queryPageObject()
    },
    // 添加页面对象
    addPageObject() {
      this.idx = -1
      this.cardIndex = this.tableData.length
      this.cardShow = true
      this.tableData.push({
        id: '',
        object_name: '',
        object_by: '',
        object_value: '',
        simple_desc: '',
        page_id: '',
        formRef: 'formStepFirst'
      })
    },
    // 移除操作步骤
    removePageObject() {
      if (this.cardIndex !== -1) {
        this.tableData.splice(this.cardIndex, 1)
      }
      this.cardShow = false
    },
    // 编辑元素
    handleEditElement(index, row) {
      this.cardShow = true
      this.cardIndex = index
      this.idx = row.id
    },
    // 删除元素
    handleDeleteElement(index, row) {
      this.cardIndex = index
      this.delVisible = true
    },
    // 保存操作步骤
    savePageObject() {
      this.cardShow = false
      if (this.idx === -1) {
        addPageElement({
          objectName: this.tableData[this.cardIndex].object_name,
          objectValue: this.tableData[this.cardIndex].object_value,
          objectBy: this.tableData[this.cardIndex].object_by,
          pageId: this.pageObjectTable.pageId,
          simpleDesc: ''
        }).then(res => {
          this.$message.success(res.desc)
          this.queryPageObject()
        })
      } else {
        editPageElement({
          objectId: this.idx,
          objectName: this.tableData[this.cardIndex].object_name,
          objectValue: this.tableData[this.cardIndex].object_value,
          objectBy: this.tableData[this.cardIndex].object_by,
          pageId: this.pageObjectTable.pageId,
          simpleDesc: ''
        }).then(res => {
          this.$message.success(res.desc)
          this.queryPageObject()
        })
      }
    },
    saveCaseEdit() {
      this.caseEditVisible = false
    },

    // 删除操作步骤
    deleteSteps(index, row) {
      if (index !== -1) {
        this.makeStepsData.splice(index, 1)
      }
    },

    // 编辑操作步骤
    editSteps(index, row) {
      row.formShow = true
    },
    initial() {
      this.makeStepsData = []
    },

    // 测试用例列表选择要运行的测试用例
    handleSelectionChange(val) {
      this.multipleSelection = val
      this.testcaseList = []
      this.multipleSelection.forEach(item => {
        this.testcaseList.push(item.id.toString())
      })
    },
    // 确定删除
    deletePageObject() {
      deletePageElement({
        pageId: this.pageObjectTable.pageId,
        objectName: this.tableData[this.cardIndex].object_name
      }).then(res => {
        this.$message.success(res.desc)
      })
      this.delVisible = false
      this.queryPageObject()
    }
  },
  watch: {
    'pageObjectTable.pageId': function(newValue) {
      if (newValue) {
        this.caseFormShow = true
        this.queryPageObject()
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

<style scoped>
</style>
