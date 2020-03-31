<template>
  <d2-container>
    <div class="table_container">
      <div class="handle-box">
        <el-form ref="baseForm" :modle="editUsreForm" class="demo-form-inline" label-width="80px" inline>
          <el-button type="primary" @click="handleadd">新增用户</el-button>
        </el-form>
      </div>
      <el-table ref="multipleTable" :data="tableData" border style="width: 100%" :header-cell-style="{color:'black',background:'#eef1f6'}" size="medium">
        <el-table-column prop="id" label="用户ID" width="120"></el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="auto"></el-table-column>
        <el-table-column prop="username" label="用户名" width="auto"></el-table-column>
        <el-table-column prop="nickname" label="姓名" width="auto"></el-table-column>
        <el-table-column prop="userStatus" label="状态" width="auto"></el-table-column>
        <el-table-column label="操作" width="auto">
          <template slot-scope="scope">
            <el-button size="small" type="text" @click="handleEdit(scope.$index, scope.row)">重置密码</el-button>
            <el-button size="small" type="text" @click="handleDelete(scope.$index, scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <!--分页-->
    <div class="pagination" style="margin-top: 20px">
      <el-pagination
        @current-change="handleCurrentChange"
        @size-change="handleSizeChange"
        layout="total, sizes, prev, pager, next, jumper"
        :total="totalCount"
        :current-page="currentPage"
        :page-sizes="[5, 10, 15, 20]"
        :page-size="pageSize"
      ></el-pagination>
    </div>
    <!--新增用户-->
    <el-dialog title="新增用户" :visible.sync="editUserVisible" width="20%" :close-on-click-modal="false" :close-on-press-escape="false" ref="editDialog">
      <el-form ref="editUsreForm" :model="editUsreForm" :label-position="labelPosition" label-width="80px">
        <el-form-item label="用户名" prop="username" :rules="[{required:true,message:'用户名必填',trigger:'blur'}]">
          <el-input v-model="editUsreForm.username" auto-complete="off" style="width: auto"></el-input>
        </el-form-item>
        <el-form-item label="昵称" prop="nickname" :rules="[{required: true,message:'昵称必填',trigger: 'blur'}]">
          <el-input v-model="editUsreForm.nickname" auto-complete="off" style="width: auto"></el-input>
        </el-form-item>
        <el-form-item label="权限" prop="role" :rules="[{required: true,message:'权限必填',trigger: 'change'}]">
          <el-radio-group v-model="editUsreForm.role">
            <el-radio :label="1">测试</el-radio>
            <el-radio :label="2">其他</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="editUserVisible = false">取 消</el-button>
        <el-button type="primary" @click="saveUserEdit('editUsreForm')">确 定</el-button>
      </div>
    </el-dialog>
    <!--//重置密码提示框-->
    <el-dialog title="提示" :visible.sync="resetVisible" width="30%" :before-close="handleClose">
      <span>确认将密码重置为:123456</span>
      <span slot="footer" class="dialog-footer">
        <el-button @click="resetVisible = false">取 消</el-button>
        <el-button type="primary" @click="resetpassword">确 定</el-button>
      </span>
    </el-dialog>

    <!-- 删除用户提示框 -->
    <el-dialog title="提示" :visible.sync="delUserVisible" width="300px" center>
      <div class="del-dialog-cnt">删除不可恢复，是否确定删除？</div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="delUserVisible = false">取 消</el-button>
        <el-button type="primary" @click="deleteRow">确 定</el-button>
      </span>
    </el-dialog>
  </d2-container>
</template>

<script>
import { fetchUsertList, addUser, deleteUser, resetUserPassword } from '@/api/sys/user'

export default {
  name: 'userManage',
  data() {
    return {
      labelPosition: 'right',
      totalCount: 100,
      currentPage: 1,
      pageSize: 10,
      idx: -1,
      resetVisible: false,
      editUserVisible: false,
      delUserVisible: false,
      editUsreForm: {
        username: '',
        nickname: '',
        user_id: '',
        role: 1
      },
      tableData: [],
      Token: '' // superuser token测试数据
    }
  },
  created() {
    this.gettabledata()
  },
  methods: {
    gettabledata() {
      fetchUsertList(
        {
          pageNo: this.currentPage,
          pageSize: this.pageSize
        },
        { Token: this.Token }
      ).then(res => {
        this.tableData = res.tableData
        this.totalCount = res.totalNum
      })
    },
    handleadd() {
      this.editUserVisible = true
      this.idx = -1
      this.editUsreForm.username = ''
      this.editUsreForm.nickname = ''
    },

    resetpassword() {
      resetUserPassword({ userId: this.editUsreForm.user_id }).then(res => {
        this.$message.success(res.desc)
      })
      this.resetVisible = false
    },

    handleEdit(index, row) {
      this.idx = index
      this.editUsreForm = {
        username: row.username,
        nickname: row.nickname,
        user_id: row.id
      }
      this.resetVisible = true
    },
    handleDelete(index, row) {
      this.idx = index
      this.editUsreForm = {
        user_id: row.id
      }
      this.delUserVisible = true
    },
    saveUserEdit(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          let role = this.editUsreForm.role === 1 ? 'tester' : 'developer'
          if (this.idx === -1) {
            addUser({
              username: this.editUsreForm.username,
              nickname: this.editUsreForm.nickname,
              role: role
            }).then(res => {
              this.editUserVisible = false
              this.$message.success(res.desc)
              this.gettabledata()
            })
          }
        }
      })
    },
    // 删除用户
    async deleteRow() {
      deleteUser({ userId: this.editUsreForm.user_id }).then(res => {
        this.$message.success(res.desc)
        this.gettabledata()
      })
      this.delUserVisible = false
    },
    handleClose(done) {
      this.$confirm('确认关闭？')
        .then(_ => {
          done()
        })
        .catch(_ => {})
    },
    handleSizeChange(val) {
      this.pageSize = val
      this.gettabledata()
    },
    handleCurrentChange(val) {
      this.currentPage = val
      this.gettabledata()
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
</style>
