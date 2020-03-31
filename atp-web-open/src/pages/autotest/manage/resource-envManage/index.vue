<template>
  <d2-container>
    <div class="table_container">
      <div class="handle-box">
        <el-form ref="baseForm" :model="baseForm" label-width="80px" inline>
          <el-form-item label="环境名称">
            <el-input v-model="baseForm.envName" placeholder="请输入环境名称，支持模糊查询" class="handle-input mr10" @keyup.enter.native="search"></el-input>
          </el-form-item>
          <el-button type="primary" icon="el-icon-search" @click="search()" :loading="searchLoading">搜 索</el-button>
          <el-button type="primary" @click="handleAdd()">新增环境</el-button>
        </el-form>
      </div>
      <el-table :data="tableData" border style="width: 100%" ref="multipleTable" :header-cell-style="{color:'black',background:'#eef1f6'}" size="medium">
        <el-table-column prop="envName" label="环境名称" sortable></el-table-column>
        <el-table-column prop="baseHost" label="域名"></el-table-column>
        <el-table-column prop="dubboZookeeper" label="ZK地址"></el-table-column>
        <el-table-column prop="mqKey" label="MQKey"></el-table-column>
        <el-table-column prop="dbConnect" label="DB连接"></el-table-column>
        <el-table-column prop="remoteHost" label="远程库地址"></el-table-column>
        <el-table-column prop="disconfHost" label="Disconf地址"></el-table-column>
        <el-table-column prop="redisConnect" label="Redis连接"></el-table-column>
        <el-table-column prop="serverAppMap" label="IP应用映射"></el-table-column>
        <el-table-column prop="serverDefaultUser" label="服务器账号"></el-table-column>
        <el-table-column prop="simpleDesc" label="环境描述"></el-table-column>
        <el-table-column prop="creator" label="创建者"></el-table-column>
        <el-table-column label="操作" fixed="right" width="100">
          <template slot-scope="scope">
            <el-button type="text" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
            <el-button type="text" @click="handleDelete(scope.$index, scope.row)">删除</el-button>
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
    </div>

    <!-- 编辑弹出框 -->
    <el-dialog title="配置" :visible.sync="editVisible" width="50%" :close-on-click-modal="false" :close-on-press-escape="false" ref="editDialog">
      <el-form ref="editForm" :model="editForm" label-width="120px">
        <el-form-item label="环境名称" prop="envName" :rules="[{ required: true, message: '必填，请输入', trigger: 'blur' }]">
          <el-input v-model="editForm.envName" placeholder="请输入环境名称，如ALIUAT"></el-input>
        </el-form-item>
        <el-form-item label="域名" prop="baseHost" :rules="[{ required: true, message: '必填，请输入', trigger: 'blur' }]">
          <el-input v-model="editForm.baseHost" placeholder="请输入域名，如https://xxx.xxx.cn"></el-input>
        </el-form-item>
        <el-form-item label="ZK地址" prop="dubboZookeeper" :rules="[{ required: true, message: '必填，请输入', trigger: 'blur' }]">
          <el-input v-model="editForm.dubboZookeeper" type="textarea" autosize placeholder="请输入ZK地址，如zookeeper://1.1.1.1:2181"></el-input>
        </el-form-item>
        <el-form-item label="MQKey" prop="mqKey" :rules="[{ required: true, message: '必填，请输入', trigger: 'blur' }]">
          <el-input v-model="editForm.mqKey" type="textarea" autosize placeholder="请输入MQKey，json格式，如{'ak': '1231', 'sk': '456'}"></el-input>
        </el-form-item>
        <el-form-item label="DB连接" prop="dbConnect" :rules="[{ required: true, message: '必填，请输入', trigger: 'blur' }]">
          <el-input
            v-model="editForm.dbConnect"
            type="textarea"
            autosize
            placeholder="请输入DB连接，如mysql+pymysql://username:password@1.1.1.1:3306/xxx?charset=utf8"
          ></el-input>
        </el-form-item>
        <el-form-item label="远程库地址" prop="remoteHost" :rules="[{ required: true, message: '必填，请输入', trigger: 'blur' }]">
          <el-input v-model="editForm.remoteHost" placeholder="请输入远程库地址，如http://1.1.1.1:18181"></el-input>
        </el-form-item>
        <el-form-item label="Disconf地址" prop="disconfHost" :rules="[{ required: true, message: '必填，请输入', trigger: 'blur' }]">
          <el-input v-model="editForm.disconfHost" placeholder="请输入Disconf地址，如http://1.1.1.1"></el-input>
        </el-form-item>
        <el-form-item label="Redis连接" prop="redisConnect" :rules="[{ required: true, message: '必填，请输入', trigger: 'blur' }]">
          <el-input
            v-model="editForm.redisConnect"
            type="textarea"
            autosize
            placeholder="请输入Redis连接，json格式，如{'host': '1.1.1.1', 'port': '6379', 'password': '12345'}"
          ></el-input>
        </el-form-item>
        <el-form-item label="IP应用映射" prop="serverAppMap">
          <el-input
            v-model="editForm.serverAppMap"
            type="textarea"
            autosize
            placeholder="请输入IP应用映射，json格式，如{'1.1.1.1': ['test1','test2'],'2.2.2.2': ['test3','test4']}"
          ></el-input>
        </el-form-item>
        <el-form-item label="服务器账号" prop="serverDefaultUser">
          <el-input v-model="editForm.serverDefaultUser" placeholder="请输入服务器账号，json格式，如{'user': 'test', 'password': '1234'}"></el-input>
        </el-form-item>
        <el-form-item label="环境描述">
          <el-input v-model="editForm.simpleDesc" type="textarea" :autosize="{ minRows: 2, maxRows: 5}" placeholder="请输入环境描述"></el-input>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="editVisible = false">取 消</el-button>
        <el-button type="primary" @click="saveEdit('editForm')">确 定</el-button>
      </span>
    </el-dialog>

    <!-- 删除提示框 -->
    <el-dialog title="提示" :visible.sync="delVisible" width="300px" center>
      <div class="del-dialog-cnt">删除不可恢复，是否确定删除？</div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="delVisible = false">取 消</el-button>
        <el-button type="primary" @click="deleteRow">确 定</el-button>
      </span>
    </el-dialog>
  </d2-container>
</template>

<script>
import { fetchEnvList, addEnv, editEnv, deleteEnv } from '@/api/autotest/manage/resource-envManage'

export default {
  name: 'envManage',
  data() {
    return {
      baseForm: {
        envName: ''
      },
      tableData: [],
      currentPage: 1,
      pagesize: 10,
      totalCount: 10,
      editVisible: false,
      delVisible: false,
      editForm: {
        id: '',
        envName: '',
        baseHost: '',
        dubboZookeeper: '',
        mqKey: '',
        dbConnect: '',
        remoteHost: '',
        disconfHost: '',
        redisConnect: '',
        serverAppMap: '',
        serverDefaultUser: '',
        simpleDesc: ''
      },
      idx: -1,
      searchLoading: false
    }
  },
  mounted() {
    this.getData()
  },
  methods: {
    handleAdd() {
      this.editVisible = true
      this.idx = -1
      this.editForm.envName = ''
      this.editForm.baseHost = ''
      this.editForm.dubboZookeeper = ''
      this.editForm.mqKey = ''
      this.editForm.dbConnect = ''
      this.editForm.remoteHost = ''
      this.editForm.disconfHost = ''
      this.editForm.redisConnect = ''
      this.editForm.simpleDesc = ''
    },
    // 分页导航
    handleCurrentChange(val) {
      this.currentPage = val
      this.getData()
    },
    handleSizeChange() {},
    // 查询项目数据
    getData() {
      return new Promise((resolve, reject) => {
        fetchEnvList({ envName: this.baseForm.envName }).then(res => {
          this.tableData = res.desc
          resolve(1)
        })
      })
    },
    search() {
      this.searchLoading = true
      this.tableData = []
      this.getData().then(res => {
        this.searchLoading = false
      })
    },
    handleEdit(index, row) {
      this.idx = index
      const item = this.tableData[index]
      this.editForm = {
        id: item.id,
        envName: item.envName,
        baseHost: item.baseHost,
        dubboZookeeper: item.dubboZookeeper,
        mqKey: item.mqKey,
        dbConnect: item.dbConnect,
        remoteHost: item.remoteHost,
        disconfHost: item.disconfHost,
        redisConnect: item.redisConnect,
        serverAppMap: item.serverAppMap,
        serverDefaultUser: item.serverDefaultUser,
        simpleDesc: item.simpleDesc
      }
      this.editVisible = true
    },
    handleDelete(index, row) {
      this.idx = index
      const item = this.tableData[index]
      this.editForm = {
        id: item.id
      }
      this.delVisible = true
    },
    // 保存编辑
    saveEdit(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          if (this.idx === -1) {
            addEnv({
              envName: this.editForm.envName,
              baseHost: this.editForm.baseHost,
              dubboZookeeper: this.editForm.dubboZookeeper,
              mqKey: this.editForm.mqKey,
              dbConnect: this.editForm.dbConnect,
              remoteHost: this.editForm.remoteHost,
              disconfHost: this.editForm.disconfHost,
              redisConnect: this.editForm.redisConnect,
              serverAppMap: this.editForm.serverAppMap,
              serverDefaultUser: this.editForm.serverDefaultUser,
              simpleDesc: this.editForm.simpleDesc
            }).then(res => {
              this.$message.success(res.desc)
              this.editVisible = false
              this.getData()
            })
          } else {
            editEnv({
              id: this.editForm.id,
              envName: this.editForm.envName,
              baseHost: this.editForm.baseHost,
              dubboZookeeper: this.editForm.dubboZookeeper,
              mqKey: this.editForm.mqKey,
              dbConnect: this.editForm.dbConnect,
              remoteHost: this.editForm.remoteHost,
              disconfHost: this.editForm.disconfHost,
              redisConnect: this.editForm.redisConnect,
              serverAppMap: this.editForm.serverAppMap,
              serverDefaultUser: this.editForm.serverDefaultUser,
              simpleDesc: this.editForm.simpleDesc
            }).then(res => {
              this.$message.success(res.desc)
              this.editVisible = false
              this.getData()
            })
          }
        } else {
          return false
        }
      })
    },
    // 确定删除
    async deleteRow() {
      deleteEnv({
        id: this.editForm.id
      }).then(res => {
        this.$message.success(res.desc)
        this.getData()
      })
      this.delVisible = false
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
  width: 300px;
  display: inline-block;
}

.del-dialog-cnt {
  font-size: 16px;
  text-align: center;
}
</style>
