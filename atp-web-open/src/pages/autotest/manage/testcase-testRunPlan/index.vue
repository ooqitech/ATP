<template>
  <d2-container>
    <div class="table_container">
      <div class="handle-box">
        <el-form ref="baseForm" :modle="baseForm" class="demo-form-inline" label-width="80px" inline>
          <el-button type="primary" @click="handaddPlan()">新增测试计划</el-button>
          <el-form-item style="margin-left: 20px">
            <el-input placeholder="请输入计划名称搜索" v-model="searchKeywords" class="handle-input mr10"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="fetchPlanList()">搜 索</el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-table :data="tableData" border style="width: 100%" ref="multipleTable" :header-cell-style="{color:'black',background:'#eef1f6'}">
        <el-table-column prop="PlanId" label="计划ID" sortable width="100"></el-table-column>
        <el-table-column prop="planName" label="计划名称" sortable width="200"></el-table-column>
        <el-table-column prop="projectName" label="所属项目" width="200"></el-table-column>
        <el-table-column prop="envName" label="运行环境" style="width: auto"></el-table-column>
        <el-table-column prop="crontab" label="定时任务" style="width: auto"></el-table-column>
        <el-table-column prop="simpleDesc" label="说明" width="200"></el-table-column>
        <el-table-column prop="creator" label="创建者" width="200"></el-table-column>
        <el-table-column prop="lastModifier" label="最后修改人" width="200"></el-table-column>
        <el-table-column label="操作" width="180">
          <template slot-scope="scope">
            <el-button size="small" type="text" @click="handleViewLog(scope.$index, scope.row)">最新运行日志</el-button>
            <el-button size="small" type="text" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
            <el-button size="small" type="text" @click="handleDelete(scope.$index, scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!--编辑测试计划框-->
    <el-dialog title="测试计划" :visible.sync="editPlanVisible" width="50%" :close-on-click-modal="false" :close-on-press-escape="false" ref="editDialog">
      <el-form ref="editForm" :model="editForm">
        <!--计划名称-->
        <el-form-item label="计划名称" prop="planName" :rules="[{ required: true, message: '计划名称必填', trigger: 'blur' }]">
          <el-input v-model="editForm.planName" auto-complete="off" style="width: auto" placeholder="请输入计划名称"></el-input>
        </el-form-item>
        <!--定时任务-->
        <el-form-item label="定时任务" prop="crontab" :rules="[{ required: true, message: '时间必填', trigger: 'blur' }]">
          <el-input v-model="editForm.crontab" auto-complete="off" style="width: auto" placeholder="30 23 * * 1-5"></el-input>
        </el-form-item>

        <!--选择环境-->
        <el-form-item label="运行环境" prop="envId" :rules="[{ required: true, message: '环境必选', trigger: 'blur' }]">
          <el-select v-model="editForm.envId" placeholder="请选择">
            <el-option v-for="item in baseForm.EnvOptions" :key="item.envName" :label="item.envName" :value="item.id"></el-option>
          </el-select>
        </el-form-item>

        <!--选择项目-->
        <el-form-item label="项目名称" prop="projectId" :rules="[{ required: true, message: '项目必选', trigger: 'blur' }]">
          <el-select v-model="editForm.projectId" placeholder="请选择" @change="selectSubTree()">
            <el-option v-for="item in baseForm.projectOptions" :key="item.projectName" :label="item.projectName" :value="item.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-row :gutter="20">
            <el-col :span="10">
              <div class="example" v-show="editForm.projectId">
                <div class="navigation-filter">
                  <el-row :gutter="20">
                    <el-col :span="12">
                      <el-input placeholder="输入用例标签筛选" v-model="filterText"></el-input>
                    </el-col>
                    <el-col :span="4">
                      <el-button size="mini" type="text" icon="el-icon-search" @click="searchTag">搜索</el-button>
                    </el-col>
                    <el-col :span="4">
                      <el-button size="mini" type="text" icon="el-icon-delete" @click="resetChecked">清空</el-button>
                    </el-col>
                  </el-row>
                </div>
                <!--:filter-node-method="filterNode"-->
                <div class="category">
                  <el-tree
                    :data="treeData"
                    show-checkbox
                    default-expand-all
                    node-key="testcaseId"
                    ref="tree"
                    highlight-current
                    :default-checked-keys="editForm.subtree"
                    :props="defaultProps"
                  ></el-tree>
                </div>
              </div>
            </el-col>
          </el-row>
        </el-form-item>
        <!--说明-->
        <el-form-item label="计划说明" prop="simpleDesc" style="margin-left: 10px">
          <el-input v-model="editForm.simpleDesc" placeholder="请输入计划说明" auto-complete="off" style="width: auto"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="editPlanVisible = false">取 消</el-button>
        <el-button type="primary" @click="savePlanEdit('editForm')">确 定</el-button>
      </div>
    </el-dialog>

    <!--删除提示框-->
    <el-dialog title="提示" :visible.sync="delPlanVisible" width="300px" center>
      <div class="del-dialog-cnt">删除不可恢复，是否确定删除？</div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="delPlanVisible = false">取 消</el-button>
        <el-button type="primary" @click="deletePlan()">确 定</el-button>
      </span>
    </el-dialog>
  </d2-container>
</template>

<script>
import { fetchProjectList, subtreeProjectWithCase } from '@/api/autotest/manage/resource-projectManage'
import { fetchEnvList } from '@/api/autotest/manage/resource-envManage'
import {
  addTestPlan,
  fetchPlanList,
  queryTestPlan,
  deleteTestPlan,
  queryTestPlanRecentReportId,
  editTestPlan
} from '@/api/autotest/manage/testcase-testCaseConfig/testplan'
import { compare } from '@/libs/common'

export default {
  name: 'testRun',
  data() {
    return {
      tableData: [],
      baseForm: {
        systemName: '',
        projectOptions: [],
        systemOptions: '',
        EnvOptions: []
      },
      editForm: {
        planName: '',
        envId: '',
        projectId: '',
        planId: '',
        projectName: '',
        envName: '',
        subtree: [],
        crontab: '',
        simpleDesc: ''
      },
      searchKeywords: '',
      editPlanVisible: false,
      delPlanVisible: false,
      select: '',
      radio: '',
      treeData: [],
      idx: -1,
      currentPage: 1,
      pagesize: 10,
      totalCount: 100,
      defaultProps: {
        children: 'children',
        label: 'label'
      },
      filterText: ''
    }
  },
  created() {
    this.fetchPlanList()
    this.getProject()
    this.getEnv()
  },
  // tree搜索
  // watch: {
  //           filterText(val) {
  //             this.$refs.tree.filter(val);
  //           }
  //         },
  methods: {
    filterNode(value, data) {
      if (!value) return true
      return data.label.indexOf(value) !== -1
    },
    handaddPlan() {
      this.initial()
      this.editPlanVisible = true
      this.idx = -1
    },
    fetchPlanList() {
      fetchPlanList({
        page: this.currentPage,
        num: this.pagesize,
        searchKeywords: this.searchKeywords
      }).then(res => {
        this.tableData = res.tableData
        this.totalCount = res.totalNum
      })
    },
    testPlanDetail() {
      queryTestPlan({
        PlanId: this.editForm.planId
      }).then(res => {
        this.editForm.subtree = res.subtree
        this.radio = '2'
      })
    },
    getProject() {
      fetchProjectList({ projectName: '' }).then(res => {
        this.baseForm.projectOptions = res.desc.sort(compare('projectName'))
      })
    },
    getEnv() {
      fetchEnvList({}).then(res => {
        this.baseForm.EnvOptions = res.desc.sort(compare('envName'))
      })
    },
    initial() {
      this.editForm.crontab = ''
      this.editForm.planName = ''
      this.editForm.envId = ''
      this.editForm.projectId = ''
      this.editForm.subtree = []
      this.editForm.simpleDesc = ''
      this.radio = ''
    },
    // 获取用例层级subtree
    getProjectSubTree(id) {
      subtreeProjectWithCase({ id: id, tagName: this.filterText }).then(res => {
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
          }
        })
        this.treeData = res.data.sort(compare('label'))
      })
    },
    selectSubTree() {
      this.getProjectSubTree(this.editForm.projectId)
    },
    // 新增测试计划
    addTestPlanTree() {
      addTestPlan({
        planName: this.editForm.planName,
        envId: this.editForm.envId,
        crontab: this.editForm.crontab,
        projectId: this.editForm.projectId,
        simpleDesc: this.editForm.simpleDesc,
        subtree: this.editForm.subtree
      }).then(res => {
        this.editPlanVisible = false
        this.$message.success(res.desc)
        this.fetchPlanList()
      })
    },
    // 提交保存
    savePlanEdit(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          this.getCheckedKeysid() // 获取树状选择的用例列表
          // 新增计划
          if (this.idx === -1) {
            this.addTestPlanTree()
          } else {
            // 编辑计划
            editTestPlan({
              testPlanId: this.editForm.planId,
              planName: this.editForm.planName,
              subtree: this.editForm.subtree,
              crontab: this.editForm.crontab,
              envId: this.editForm.envId,
              simpleDesc: this.editForm.simpleDesc,
              projectId: this.editForm.projectId
            }).then(res => {
              this.$message.success(res.desc)
              this.editPlanVisible = false
              this.fetchPlanList()
            })
          }
        }
      })
    },
    // 获取用户选择的用例集列表
    getCheckedKeysid() {
      const subtreeList = []
      this.$refs.tree.getCheckedKeys().forEach(item => {
        if (item) {
          subtreeList.push(item)
        }
      })
      this.editForm.subtree = subtreeList
    },
    // 重置所选
    resetChecked() {
      this.$refs.tree.setCheckedKeys([])
      this.editForm.subtree = []
    },
    // 搜索带标签的用例
    searchTag() {
      this.selectSubTree()
    },
    // 编辑计划触发的初始化操作
    handleEdit(index, row) {
      this.idx = index
      const item = this.tableData[index]
      this.editForm.planName = item.planName
      this.editForm.crontab = item.crontab
      this.editForm.simpleDesc = item.simpleDesc
      this.editForm.planId = item.PlanId
      this.editForm.projectId = item.projectId
      this.editForm.envId = item.envId
      this.editPlanVisible = true
      this.testPlanDetail()
      this.selectSubTree()
      // this.$nextTick(() => {
      //     this.$refs['editForm'].clearValidate()
      //     this.$refs.tree.setCheckedKeys([200])
      // })
    },
    // 查看当前测试计划最近一次运行日志
    handleViewLog(index, row) {
      this.idx = index
      const item = this.tableData[index]
      queryTestPlanRecentReportId({
        testPlanId: item.PlanId
      }).then(res => {
        this.$store.commit('d2admin/testreport/set', { reportId: res.reportId }, { root: true })
        const { href } = this.$router.resolve({
          name: 'viewReport'
        })
        window.open(href, '_blank')
      })
    },
    setCheckedKeys() {
      this.$refs.tree.setCheckedKeys([200])
    },
    handleDelete(index, row) {
      this.idx = index
      const item = this.tableData[index]
      this.editForm.planId = item.PlanId
      this.delPlanVisible = true
    },
    deletePlan() {
      deleteTestPlan({
        testPlanId: this.editForm.planId
      }).then(res => {
        this.$message.success(res.desc)
        this.fetchPlanList()
      })
      this.delPlanVisible = false
    }
  }
}
</script>

<style scoped>
</style>
