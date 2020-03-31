<template>
  <d2-container>
    <div class="table_container">
      <!--<el-alert
        title="操作说明"
        description="请按公司名查询，然后在左侧树节点上使用右键操作，新增/修改/删除产品线→新增全链路用例"
        type="success"
        show-icon>
      </el-alert>-->
      <div class="handle-box">
        <el-form ref="baseForm" :model="baseForm" label-width="80px" inline>
          <el-form-item label="公司名称" prop="companyId" :rules="[{ required: true, message: '请选择公司', trigger: 'change' }]">
            <el-select v-model="baseForm.companyId" filterable placeholder="请选择">
              <el-option v-for="item in baseForm.companyOptions" :key="item.companyId" :label="item.companyName" :value="item.companyId"></el-option>
            </el-select>
          </el-form-item>
          <el-button type="primary" icon="el-icon-search" @click="search('baseForm')" :loading="searchLoading">搜 索</el-button>
        </el-form>
      </div>
      <el-row>
        <el-col :span="6">
          <div class="example-fullLink">
            <div class="navigation-filter">
              <el-row :gutter="10">
                <el-col :span="20">
                  <el-input placeholder="试试输入关键字" v-model="filterText"></el-input>
                </el-col>
                <el-col :span="4">
                  <el-tooltip content="新增目录" placement="top" effect="light">
                    <el-button icon="el-icon-plus" type="primary" plain @click="handleAddProduce()"></el-button>
                  </el-tooltip>
                </el-col>
              </el-row>
            </div>
            <el-scrollbar wrap-class="fullScrolllist" view-class="view-box" :native="false">
              <div class="fullList">
                <el-tree
                  :data="treeData"
                  node-key="id"
                  :props="defaultProps"
                  :default-expanded-keys="nodeKeys"
                  :filter-node-method="filterNode"
                  @node-click="handleNodeClick"
                  @node-contextmenu="rightClick"
                  @node-drag-end="handleDragEnd"
                  draggable
                  :allow-drop="allowDrop"
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
        <el-col :span="18">
          <div class="example-fullLink">
            <case-table></case-table>
          </div>
        </el-col>
      </el-row>
    </div>

    <!--树形控件右键菜单_一级产品线-->
    <div>
      <v-contextmenu ref="contextMenuProduce">
        <v-contextmenu-item @click="handleAddFolder()">新增目录</v-contextmenu-item>
        <v-contextmenu-item @click="handleEditProduce()">编辑目录</v-contextmenu-item>
        <v-contextmenu-item @click="handleDeleteProduce()">删除目录</v-contextmenu-item>
        <v-contextmenu-item @click="handleAddFulllineCase()" v-if="flag">新增全链路用例</v-contextmenu-item>
        <v-contextmenu-item divider></v-contextmenu-item>
      </v-contextmenu>
    </div>
    <!--树形控件右键菜单_二级全链路用例-->
    <div>
      <v-contextmenu ref="contextMenuTestCase">
        <v-contextmenu-item @click="handleDeleteFulllineCase()">删除全链路用例</v-contextmenu-item>
        <v-contextmenu-item divider></v-contextmenu-item>
      </v-contextmenu>
    </div>

    <!-- 新增编辑目录弹出框 -->
    <el-dialog title="配置目录" :visible.sync="produceEditVisible" width="30%" :close-on-click-modal="false" :close-on-press-escape="false" ref="produceEditDialog">
      <el-form ref="produceEditForm" :model="produceEditForm" label-width="100px">
        <el-form-item label="目录名称" prop="productLineName" :rules="[{ required: true, message: '目录名称必填', trigger: 'blur' }]">
          <el-input v-model="produceEditForm.productLineName" placeholder="目录名称"></el-input>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="produceEditVisible = false">取 消</el-button>
        <el-button type="primary" @click="saveProduceEdit('produceEditForm')">确 定</el-button>
      </span>
    </el-dialog>

    <!-- 删除提示框 -->
    <el-dialog title="提示" :visible.sync="delVisible" width="300px" center>
      <div class="del-dialog-cnt">删除不可恢复，是否确定删除？</div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="delVisible = false">取 消</el-button>
        <el-button type="danger" icon="el-icon-warning" @click="saveDelete(deleteId)">删 除</el-button>
      </span>
    </el-dialog>
  </d2-container>
</template>

<script>
import { fetchCompanyList, subtreeProductLine } from '@/api/autotest/manage/resource-apiManage/company'
import { addProductLine, deleteProductLine, editProductLine, changeParent } from '@/api/autotest/manage/fullLineCase/produceLine-config'
import { deleteFullLineCase, changeFullLineCaseParent } from '@/api/autotest/manage/fullLineCase/testcase-config'
import { mapMutations } from 'vuex'
import {
  queryCustomSetupHooks,
  querySupportVariableTypes,
  queryCustomFunctions,
  querySignFunctions,
  queryCustomComparators,
  queryCustomTeardownHooks
} from '@/api/autotest/manage/testcase-apiManage/support'

export default {
  name: 'fullLineCaseManage',
  components: {
    caseTable: () => import('./components-table')
  },
  data() {
    return {
      editProduceIdx: -1,
      baseForm: {
        companyId: '',
        companyOptions: []
      },
      productLineId: '',
      testcaseId: '',
      produceEditVisible: false,
      introduceInterVisible: true,
      systemEditVisible: false,
      produceEditForm: {
        productLineName: ''
      },
      deleteId: '',
      deleteIdx: '',
      importFileUrl: '/atp/file/upload',
      downloadXmindTempUrl: '',
      delVisible: false,
      exportVisible: false,
      exportMoudleName: '',
      interfaceEditVisible: false,
      defaultProps: {
        children: 'children',
        label: 'label'
      },
      filterText: '',
      filterSystemText: '',
      filterInterfaceText: '',
      treeData: [],
      nodeKeys: [],
      nodeKey: '',
      parentNodeKey: '',
      rules: {
        interfaceType: [{ required: true, message: '接口类型必填', trigger: 'blur' }]
      },
      customFunsData: {
        supportSetupFuncs: [],
        supportVariableType: [],
        customVariableFunctions: [],
        supportSignFuncs: [],
        supportCustomComparators: [],
        supportTeardownFuncs: []
      },
      flag: false,
      id: 0,
      searchLoading: false
    }
  },
  mounted() {
    this.getCompany()
  },
  watch: {
    filterText(val) {
      this.$refs.tree.filter(val)
      // 清除过滤关键字后刷新树列表为初始状态
      if (!val) {
        for (var i = 0; i < this.$refs.tree.store._getAllNodes().length; i++) {
          this.$refs.tree.store._getAllNodes()[i].expanded = false
        }
      }
    },
    filterSystemText(val) {
      this.$refs.tree1.filter(val)
    },
    filterInterfaceText(val) {
      this.$refs.tree2.filter(val)
    }
  },
  methods: {
    ...mapMutations({
      changeFullLineCaseTable: 'd2admin/fulllinecase/changeFullLineCaseTable',
      changeSupportTable: 'd2admin/fulllinecase/changeSupportTable',
      addCase: 'd2admin/fulllinecase/addCase',
      changeCompanyId: 'd2admin/fulllinecase/changeCompanyId'
    }),
    // 处理新增全链路用例
    handleAddFulllineCase() {
      this.addCase(true)
    },
    // 处理删除全链路用例
    handleDeleteFulllineCase() {
      this.delVisible = true
      this.deleteId = this.testcaseId
    },
    // 左键点击树
    handleNodeClick(data, node) {
      this.$refs['contextMenuProduce'].hide()
      this.$refs['contextMenuTestCase'].hide()
      let productLineId = ''
      let testcaseId = ''
      if ('productLineId' in data) {
        productLineId = data.productLineId
        this.productLineId = data.productLineId
        this.id += 1
      }
      if ('testcaseId' in data) {
        testcaseId = data.testcaseId
        this.testcaseId = testcaseId
        productLineId = node.parent.data.productLineId
        this.id += 1
      }
      let caseTableInfo = {
        testcaseId: testcaseId,
        productLineId: productLineId,
        id: this.id
      }
      console.log(node)
      if (node.isLeaf || node.childNodes[0].isLeaf) {
        this.changeFullLineCaseTable(caseTableInfo)
      }
    },
    // 右键点击树
    rightClick(event, object, value, element) {
      this.$refs.tree.setCurrentKey(value.key)
      let productLineId = ''
      if ('productLineId' in object) {
        if (value.isLeaf) {
          this.flag = true
        } else if ('testcaseId' in value.childNodes[0].data) {
          this.flag = true
        } else {
          this.flag = false
        }
        const position = {
          top: event.clientY,
          left: event.clientX + 20
        }
        this.$refs['contextMenuTestCase'].hide()
        this.$refs['contextMenuProduce'].show(position)
        this.productLineId = object.productLineId
        this.produceEditForm.productLineName = object.label
        this.nodeKey = value.key
        this.parentNodeKey = value.parent.key
        productLineId = object.productLineId
        this.changeFullLineCaseTable({
          testcaseId: '',
          productLineId: productLineId
        })
        this.deleteIdx = 1
      } else if ('testcaseId' in object) {
        const position = {
          top: event.clientY,
          left: event.clientX + 20
        }
        this.$refs['contextMenuProduce'].hide()
        this.$refs['contextMenuTestCase'].show(position)
        this.testcaseId = object.testcaseId
        this.nodeKey = value.key
        this.parentNodeKey = value.parent.key
        this.deleteIdx = 2
      }
    },
    filterNode(value, data) {
      if (!value) return true
      return data.label.indexOf(value) !== -1
    },
    search(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          this.searchLoading = true
          this.treeData = []
          this.getFullLineSubTree(this.baseForm.companyId).then(res => {
            this.searchLoading = false
          })
          this.changeCompanyId(this.baseForm.companyId)
        }
      })
    },
    // 处理新增产品线
    handleAddProduce() {
      this.produceEditVisible = true
      this.produceEditForm.productLineName = ''
      this.editProduceIdx = -1
    },
    // 处理新增目录
    handleAddFolder() {
      this.produceEditVisible = true
      this.produceEditForm.productLineName = ''
      this.editProduceIdx = -2
    },
    // 处理编辑产品线
    handleEditProduce() {
      this.produceEditVisible = true
      this.editProduceIdx = this.productLineId
      this.produceEditForm.productLineName = this.produceEditForm.productLineName.split('(')[0]
    },
    // 处理删除产品线
    handleDeleteProduce() {
      this.delVisible = true
      this.deleteId = this.productLineId
    },

    refreshSubtree(nodeLevel) {
      this.getProjectSubTree(this.projectId)
      this.nodeKeys = []
      if (nodeLevel === 'testsuite') {
        this.nodeKeys.push(this.nodeKey)
      } else if (nodeLevel === 'testcase') {
        this.nodeKeys.push(this.parentNodeKey)
      }
    },
    // 获取公司列表
    getCompany() {
      fetchCompanyList({}).then(res => {
        this.baseForm.companyOptions = res.companyList
        if (res.code === '000') {
          this.baseForm.companyId = res.companyList[0].companyId
          this.getFullLineSubTree(this.baseForm.companyId)
          // this.queryCustomFuncsData()
        }
      })
    },
    // 获取产品线subtree
    getFullLineSubTree(id) {
      return new Promise((resolve, reject) => {
        subtreeProductLine({ companyId: id }).then(res => {
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
          this.traversalObject(res.data)
          this.treeData = res.data
          resolve(1)
        })
      })
    },
    // 递归遍历项目数据，获取用例数并更新label
    traversalObject(lt) {
      let num = 0
      lt.forEach(obj => {
        if (obj.children.length === 0) {
          obj.label += '(0)'
        } else if (obj.children[0].hasOwnProperty('children') && obj.children[0].children.length !== 0) {
          let a = this.traversalObject(obj.children)
          obj.label += '(' + a + ')'
          num += a
        } else {
          obj.label += '(' + obj.children.length + ')'
          num += obj.children.length
        }
      })
      return num
    },
    // 保存编辑产品线
    saveProduceEdit(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          console.log(this.editProduceIdx)
          if (this.editProduceIdx === -1) {
            addProductLine({
              companyId: this.baseForm.companyId,
              productLineName: this.produceEditForm.productLineName
            }).then(res => {
              this.$message.success(res.desc)
              if (res.code === '000') {
                this.getFullLineSubTree(this.baseForm.companyId)
              }
            })
          } else if (this.editProduceIdx === -2) {
            addProductLine({
              parentId: this.productLineId,
              productLineName: this.produceEditForm.productLineName
            }).then(res => {
              this.$message.success(res.desc)
              if (res.code === '000') {
                this.getFullLineSubTree(this.baseForm.companyId)
              }
            })
          } else {
            editProductLine({
              productLineId: this.productLineId,
              productLineName: this.produceEditForm.productLineName
            }).then(res => {
              this.$message.success(res.desc)
              if (res.code === '000') {
                this.getFullLineSubTree(this.baseForm.companyId)
              }
            })
          }
          this.produceEditVisible = false
          this.nodeKeys = []
          this.nodeKeys.push(this.nodeKey)
        } else {
          return false
        }
      })
    },
    // 异步请求新增用例时需要读取的自定义函数类型及参数信息
    queryCustomFuncsData(obj) {
      let _self = this
      let newArr = []
      if (_self.customFunsData.supportSetupFuncs.length === 0) {
        var res1 = new Promise(function(resolve, reject) {
          queryCustomSetupHooks({}).then(res => {
            _self.customFunsData.supportSetupFuncs = res.data
            resolve(1)
          })
        })
      }
      newArr.push(res1)
      if (_self.customFunsData.supportTeardownFuncs.length === 0) {
        var res2 = new Promise(function(resolve, reject) {
          queryCustomTeardownHooks({}).then(res => {
            _self.customFunsData.supportTeardownFuncs = res.data
            resolve(1)
          })
        })
      }
      newArr.push(res2)
      if (_self.customFunsData.supportVariableType.length === 0) {
        var res3 = new Promise(function(resolve, reject) {
          querySupportVariableTypes({}).then(res => {
            _self.customFunsData.supportVariableType = res.data
            resolve(1)
          })
        })
      }
      newArr.push(res3)
      if (_self.customFunsData.customVariableFunctions.length === 0) {
        var res4 = new Promise(function(resolve, reject) {
          queryCustomFunctions({}).then(res => {
            _self.customFunsData.customVariableFunctions = res.data
            resolve(1)
          })
        })
      }
      newArr.push(res4)
      if (_self.customFunsData.supportSignFuncs.length === 0) {
        var res5 = new Promise(function(resolve, reject) {
          querySignFunctions({}).then(res => {
            _self.customFunsData.supportSignFuncs = res.data
            resolve(1)
          })
        })
      }
      newArr.push(res5)
      if (_self.customFunsData.supportCustomComparators.length === 0) {
        var res6 = new Promise(function(resolve, reject) {
          queryCustomComparators({}).then(res => {
            _self.customFunsData.supportCustomComparators = res.data
            resolve(1)
          })
        })
      }
      newArr.push(res6)
      Promise.all(newArr)
        .then(function() {
          // 都通过了
          const supportTableInfo = {
            supportSetupFuncs: _self.customFunsData.supportSetupFuncs,
            supportVariableType: _self.customFunsData.supportVariableType,
            customVariableFunctions: _self.customFunsData.customVariableFunctions,
            supportSignFuncs: _self.customFunsData.supportSignFuncs,
            supportCustomComparators: _self.customFunsData.supportCustomComparators,
            supportTeardownFuncs: _self.customFunsData.supportTeardownFuncs
          }
          _self.changeSupportTable(supportTableInfo)
        })
        .catch(function(err) {
          console.error(err)
        })
    },
    // 删除产品线、删除全链路用例
    saveDelete(id) {
      if (id === this.productLineId && this.deleteIdx === 1) {
        deleteProductLine({ productLineId: this.productLineId }).then(res => {
          this.$message.success(res.desc)
          this.getFullLineSubTree(this.baseForm.companyId)
        })
      } else if (id === this.testcaseId && this.deleteIdx === 2) {
        deleteFullLineCase({ testcaseId: this.testcaseId }).then(res => {
          this.$message.success(res.desc)
          this.getFullLineSubTree(this.baseForm.companyId)
        })
      }
      this.nodeKeys = []
      this.nodeKeys.push(this.parentNodeKey)
      this.delVisible = false
    },
    // 用例层级只能拖拽至产品线层级下
    allowDrop(draggingNode, dropNode, type) {
      if ('productLineId' in draggingNode.data) {
        if ('testcaseId' in dropNode.data) {
          return false
        } else {
          return type === 'inner'
        }
      }
      if ('testcaseId' in draggingNode.data) {
        if ('productLineId' in dropNode.data && (dropNode.childNodes.length === 0 || 'testcaseId' in dropNode.childNodes[0].data)) {
          return type === 'inner'
        } else {
          return false
        }
      }
    },
    // 产品线层级不能拖拽
    /* allowDrag (draggingNode) {
                console.log(draggingNode)
                if (draggingNode.data.productLineId) {
                    return false
                } else {
                    return draggingNode
                }

            },*/
    // draggingId表示拖拽用例id，draggedId表示拖拽至产品线productLineId
    handleDragEnd(draggingNode, dropNode, dropType, ev) {
      console.log(dropType)
      if (dropType !== 'none') {
        if ('testcaseId' in draggingNode.data) {
          let draggingId = draggingNode.data.testcaseId
          let draggedId = dropNode.data.productLineId
          console.log(draggingId, draggedId)
          changeFullLineCaseParent({ testcaseId: draggingId, newParentId: draggedId }).then(res => {
            this.$message.success(res.desc)
          })
        } else {
          let productLineId = draggingNode.data.productLineId
          let newParentId = dropNode.data.productLineId
          changeParent({ productLineId: productLineId, newParentId: newParentId }).then(res => {
            this.$message.success(res.desc)
          })
        }
      }
    }
  }
}
</script>

<style lang="scss">
.example-fullLink {
  padding: 10px;
  height: 100%;
  min-height: 700px;
  max-height: 700px;
  border-radius: 4px;
  /*border: 0.5px solid #d7dae2;*/
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.1);
}

.table_container {
  padding: 10px;
}

.del-dialog-cnt {
  font-size: 16px;
  text-align: center;
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

.navigation-filter {
  padding: 10px 23px;
}

.fullScrolllist {
  max-height: 680px;
}

/*.custom-tree-node {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    font-size: 14px;
    padding-right: 8px;
  }*/

.category-description {
  text-indent: 2em;
}

.fullList {
  margin-bottom: 20px;
}

.el-tree--highlight-current .el-tree-node.is-current > .el-tree-node__content {
  background-color: #3a8ee62b;
}

.navigation-filter {
  padding: 5px 10px;
}

.tree-list {
  max-height: 350px;
}

/*.span {
    .card-panel-icon {
      float: left;
      font-size: 18px;
      color: #ffab0c
    }
  }*/
</style>
