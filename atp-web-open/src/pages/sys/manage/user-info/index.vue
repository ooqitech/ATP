<template>
  <d2-container>
    <span style="margin: 20px">
      <strong>基础信息</strong>
    </span>
    <div class="userform" style="margin: 20px">
      <el-form :label-position="labelPosition" label-width="80px" :model="userInfo">
        <el-form-item label="用户名：">
          <span>{{userInfo.username}}</span>
        </el-form-item>
        <el-form-item label="昵称：">
          <span>{{userInfo.nickname}}</span>
        </el-form-item>
        <el-form-item label="状态：">
          <span>{{userInfo.statusDesc}}</span>
        </el-form-item>
        <el-form-item style="float: left">
          <el-button type="primary" @click="handlechange">修改密码</el-button>
        </el-form-item>
      </el-form>
    </div>
    <!--重置密码框-->
    <el-dialog title="重置密码" :visible.sync="changeVisible" width="20%" :close-on-click-modal="false" :close-on-press-escape="false" ref="resetDialog">
      <el-form :model="ruleForm2" status-icon :rules="rules2" ref="ruleForm2" label-width="100px" :label-position="labelPosition" class="demo-ruleForm">
        <el-form-item label="原密码" prop="oldpassword">
          <el-input v-model="ruleForm2.oldpassword"></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="newpassword">
          <el-input type="password" v-model="ruleForm2.newpassword"></el-input>
        </el-form-item>
        <el-form-item label="确认密码" prop="checkpassword">
          <el-input type="password" v-model="ruleForm2.checkpassword"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitResetPWD('ruleForm2')">提交</el-button>
          <el-button @click="resetForm('ruleForm2')">重置</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>
  </d2-container>
</template>

<script>
import { changeUserPassword, getUserInfo } from '@/api/sys/user'
import { mapActions } from 'vuex'

export default {
  name: 'personalInfo',
  data() {
    var validatePass = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请输入密码'))
      } else {
        if (this.ruleForm2.checkpassword !== '') {
          this.$refs.ruleForm2.validateField('checkpassword')
        }
        callback()
      }
    }
    var validatePass2 = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请再次输入密码'))
      } else if (value !== this.ruleForm2.newpassword) {
        callback(new Error('两次输入密码不一致!'))
      } else {
        callback()
      }
    }
    return {
      ruleForm2: {
        oldpassword: '',
        newpassword: '',
        checkpassword: ''
      },
      labelPosition: 'left',
      userInfo: {
        nickname: '',
        statusDesc: '',
        username: ''
      },
      rules2: {
        newPassword: [{ validator: validatePass, trigger: 'blur' }],
        checkpassword: [{ validator: validatePass2, trigger: 'blur' }]
      },
      changeVisible: false,
      Token: '' // superuser token测试数据
    }
  },
  created() {
    this.getUserdata()
  },
  methods: {
    ...mapActions('d2admin/account', ['logout']),
    getUserdata() {
      getUserInfo({}).then(res => {
        this.userInfo.nickname = res.nickname
        this.userInfo.username = res.username
        this.userInfo.statusDesc = res.statusDesc
      })
    },
    handlechange() {
      this.changeVisible = true
    },
    // 提交重置密码
    submitResetPWD(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          changeUserPassword({
            oldPassword: this.ruleForm2.oldpassword,
            newPassword: this.ruleForm2.newpassword
          }).then(res => {
            this.changeVisible = false
            this.$message.success(res.desc)
            this.logout({
              vm: this,
              confirm: false
            })
          })
        } else {
          console.log('error submit!!')
          return false
        }
      })
    },
    // 重置
    resetForm(formName) {
      this.$refs[formName].resetFields()
    }
  }
}
</script>

<style lang="scss" scoped>
</style>
