<template>
  <div class="fillcontain">
    <el-form v-show="caseFormShow" size="mini">
      <!--用例搜素-->
      <!--<el-form inline class="demo-table-expand">-->
      <!--<el-form-item style="float: left">-->
      <!--<el-input-->
      <!--v-model="searchKeywords"-->
      <!--placeholder="请输入用例名称，支持模糊查询"-->
      <!--class="handle-input mr10" @keyup.enter.native="search"-->
      <!--style="width: auto"-->
      <!--&gt;</el-input>-->
      <!--<el-button type="primary" icon="el-icon-search" style="margin-left: 5px">搜 索</el-button>-->
      <!--</el-form-item>-->
      <!--</el-form>-->
      <el-table
        :data="tableData"
        border
        style="width: 100%;margin-top: 5px"
        ref="multipleTable"
        :header-cell-style="{color:'black',background:'#eef1f6'}"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="80"></el-table-column>
        <el-table-column prop="id" label="用例编号" width="100"></el-table-column>
        <el-table-column prop="testcase_name" label="用例标题" width="auto"></el-table-column>
        <el-table-column prop="test_type" label="用例类型" width="100"></el-table-column>

        <el-table-column label="操作" fixed="right" width="260">
          <template slot-scope="scope">
            <el-button size="mini" type="primary" icon="el-icon-edit" @click="handleEditCase(scope.$index, scope.row)" plain></el-button>
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
      <!--详情以表格展示-->
      <el-table
        :data="makeStepsTableData"
        border
        style="width: 100%;margin-top: 5px"
        ref="multipleTable"
        :header-cell-style="{color:'black',background:'#eef1f6'}"
      >
        <el-table-column prop="stepNo" label="操作顺序" width="80"></el-table-column>
        <el-table-column prop="setup" label="前置条件" width="auto"></el-table-column>
        <el-table-column prop="operating" label="操作步骤" width="auto"></el-table-column>
        <el-table-column prop="expected" label="预期结果" width="auto"></el-table-column>
        <el-table-column prop="memo" label="备注" width="auto"></el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import { queryCaseListByModuleId, detailBaseCase } from '@/api/autotest/manage/testcase-testCaseConfig/testcase'
export default {
  name: 'index',
  data() {
    return {
      reportUrl: '',
      selectedItem: [],
      idx: -1,
      testcaseId: '',
      baseForm: '',
      tableData: [],
      caseEditVisible: false,
      currentPage: 1,
      totalCount: 100,
      pagesize: 10,
      caseFormShow: false,
      searchKeywords: '',
      activeNames: ['1'],
      tabVisible: [{ label: 'steps', displayName: '操作步骤', value: true }],
      makeStepsData: [],
      makeStepsTableData: [],
      caseInfo: {},
      multipleSelection: [],
      testcaseList: [],
      lastModuleId: 0
    }
  },
  computed: {
    ...mapState('d2admin/casetable', ['featureCaseTable'])
  },
  methods: {
    queryTestCases() {
      if (this.lastModuleId === 0) {
        this.lastModuleId = this.featureCaseTable.moduleId
      }
      if (this.lastModuleId !== this.featureCaseTable.moduleId) {
        this.currentPage = 1
      }
      this.lastModuleId = this.featureCaseTable.moduleId
      queryCaseListByModuleId({
        moduleId: this.featureCaseTable.moduleId,
        pageNo: this.currentPage,
        pageSize: this.pagesize
      }).then(res => {
        this.tableData = res.desc
        this.totalCount = res.totalNum
      })
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
    saveCaseEdit() {
      this.caseEditVisible = false
    },
    initial() {
      this.makeStepsTableData = []
    },
    // 编辑用例
    handleEditCase(index, row) {
      this.idx = index
      this.testcaseId = row.id
      this.caseEditVisible = true
      this.initial()
      detailBaseCase({ id: row.id }).then(res => {
        const caseInfo = res.data
        this.makeStepsTableData = caseInfo.steps.stepsInfo
      })
    },
    // 测试用例列表选择要运行的测试用例
    handleSelectionChange(val) {
      this.multipleSelection = val
      this.testcaseList = []
      this.multipleSelection.forEach(item => {
        this.testcaseList.push(item.id.toString())
      })
    }
  },
  watch: {
    'featureCaseTable.moduleId': function(newValue) {
      if (newValue) {
        this.caseFormShow = true
        this.queryTestCases()
      } else {
        this.caseFormShow = false
      }
    }
  }
}
</script>

<style lang="scss">
.el-table .warning-row {
  background: oldlace;
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

/* 用例编辑页面各元素样式 */

.caseEditDialog .el-dialog__body {
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

/* 可编辑表格 */

.el-tb-edit .el-input,
.el-tb-edit .el-select,
.el-tb-edit .el-form-item--small.el-form-item.is-success {
  display: none;
  width: 100%;
}

.el-tb-edit .current-row .el-input,
.el-tb-edit .current-row .el-select,
.el-tb-edit .current-row .el-form-item--small.el-form-item.is-success {
  display: inherit;
}

.el-tb-edit .current-row .el-input + span,
.el-tb-edit .current-row .el-select + span,
.el-tb-edit .current-row .el-form-item + span {
  display: none;
}

.test {
  margin-bottom: 20px;
  padding: 0;
}

.header-icon {
  color: #66b1ff;
}
</style>
