<template>
  <div class="user-login">
    <div class="user-login-bg" :style="{'background-image':`url(${backgroundImage})`}"></div>
    <div class="content-wrapper">
      <h2 class="slogan">
        欢迎使用
        <br />ATP测试综合管理平台
      </h2>
      <div class="form-container">
        <h4 class="form-title">登录</h4>
        <el-form ref="form" :model="user" label-width="0">
          <div class="form-items">
            <el-row class="form-item">
              <el-col>
                <el-form-item prop="username" :rules="[ { required: true, message: '会员名/邮箱/手机号不能为空'}]">
                  <div class="form-line">
                    <i class="el-icon-edit-outline input-icon"></i>
                    <el-input placeholder="邮箱/昵称" v-model="user.username" @keyup.enter.native="submitBtn"></el-input>
                  </div>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row class="form-item">
              <el-col>
                <el-form-item prop="password" :rules="[ { required: true, message: '密码不能为空'}]">
                  <div class="form-line">
                    <i class="el-icon-service input-icon"></i>
                    <el-input type="password" placeholder="密码" v-model="user.password" @keyup.enter.native="submitBtn"></el-input>
                  </div>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row class="form-item">
              <el-col>
                <el-form-item>
                  <el-checkbox class="checkbox">记住账号</el-checkbox>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row class="form-item">
              <el-button type="primary" class="submit-btn" size="small" @click="submitBtn">登 录</el-button>
            </el-row>
          </div>
          <!--<el-row class="tips">
            <a href="/" class="link">
              立即注册
            </a>
            <span class="line">|</span>
            <a href="/" class="link">
              忘记密码
            </a>
          </el-row>-->
        </el-form>
      </div>
    </div>
  </div>
</template>

<script>
/* eslint-disable */
import BasicContainer from '@vue-materials/basic-container'
import { mapActions } from 'vuex'
const baseUrl = process.env.BASE_URL
const backgroundImage = baseUrl + 'image/theme/atp/login/background.png'
export default {
  components: { BasicContainer },
  name: 'UserLogin',
  data() {
    return {
      backgroundImage: backgroundImage,
      // 表单
      user: {
        username: '',
        password: ''
      },
      // 校验
      rules: {
        username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
        password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
      }
    }
  },
  methods: {
    ...mapActions('d2admin/account', ['login']),
    /**
     * @description 提交表单
     */
    // 提交登录信息
    submitBtn() {
      this.$refs['form'].validate(valid => {
        if (valid) {
          // 登录
          this.login({
            vm: this,
            username: this.user.username,
            password: this.user.password
          })
        } else {
          // 登录表单校验失败
          this.$message.error('表单校验失败')
        }
      })
    }
  }
}
</script>

<style lang="scss">
@import './UserLogin.scss';
</style>
