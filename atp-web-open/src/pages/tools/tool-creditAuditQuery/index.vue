<template>
  <d2-container>
    <el-form :model="creditAuditQuery" ref="creditAuditQuery" label-width="100px" size="small" style="margin-bottom: 30px" inline>
      <el-form-item label="测试环境" prop="env" :rules="[{ required: true, message: '测试环境必填', trigger: 'change' }]">
        <el-select v-model="creditAuditQuery.env" placeholder="请选择">
          <el-option v-for="item in creditAuditQuery.options" :key="item.value" :label="item.label" :value="item.value"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="手机号" prop="mobile" :rules="[{ required: true, message: '手机号必填', trigger: 'blur' }]">
        <el-input v-model="creditAuditQuery.mobile" placeholder="请输入手机号码" auto-complete="off" style="width: 300px"></el-input>
      </el-form-item>
      <el-form-item label="设备号" prop="deviceId">
        <el-input v-model="creditAuditQuery.deviceId" placeholder="请输入设备编号" auto-complete="off" style="width: 300px"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submitForm('creditAuditQuery')">查询</el-button>
        <el-button @click="resetForm('creditAuditQuery')">重置</el-button>
      </el-form-item>
    </el-form>
    <h4>用户信息</h4>
    <el-table :data="userInfoData" size="mini" border style="width: 80%; margin-top: 20px; margin-bottom: 20px" ref="userInfoTable">
      <el-table-column type="index"></el-table-column>
      <el-table-column prop="phoneNo" label="用户手机号"></el-table-column>
      <el-table-column prop="userName" label="用户姓名"></el-table-column>
      <el-table-column prop="memberId" label="会员编号"></el-table-column>
    </el-table>
    <h4>最近一次申请信息</h4>
    <el-table :data="applyInfoData" size="mini" border style="width: 80%; margin-top: 20px; margin-bottom: 20px" ref="applyInfoTable">
      <el-table-column type="index"></el-table-column>
      <el-table-column prop="applyNo" label="申请编号"></el-table-column>
      <el-table-column prop="channelType" label="申请渠道"></el-table-column>
      <el-table-column prop="applyMerchant" label="申请商户"></el-table-column>
      <!--<el-table-column prop="deviceId" label="使用的设备编号">
      </el-table-column>
      <el-table-column prop="phoneBrand" label="使用的设备型号">
      </el-table-column>-->
      <el-table-column prop="applyDate" label="申请时间"></el-table-column>
    </el-table>
    <h4>最近一次征信拒件记录</h4>
    <el-table :data="creditAuditResult" size="mini" border style="width: 80%; margin-top: 20px; margin-bottom: 20px" ref="creditAuditResultTable">
      <el-table-column type="index"></el-table-column>
      <el-table-column prop="caStage" label="审核阶段" width="150px"></el-table-column>
      <el-table-column prop="isPass" label="审核结果"></el-table-column>
      <el-table-column prop="auditTime" label="审核时间"></el-table-column>
    </el-table>
    <h4>征信白名单配置情况</h4>
    <el-table :data="whiteListData" size="mini" border style="width: 80%; margin-top: 20px" ref="whiteListTable">
      <el-table-column type="index"></el-table-column>
      <el-table-column prop="type" label="类型" width="150px"></el-table-column>
      <el-table-column prop="ca" label="ca预授信"></el-table-column>
      <el-table-column prop="activate" label="激活"></el-table-column>
      <el-table-column prop="auth" label="授权"></el-table-column>
      <el-table-column prop="cta" label="cta交易审核"></el-table-column>
      <el-table-column label="操作" fixed="right" width="100">
        <template slot-scope="scope">
          <el-button type="text" @click="handleConfig(scope.$index, scope.row)">配置</el-button>
        </template>
      </el-table-column>
    </el-table>
  </d2-container>
</template>
<script>
import { crediAuditQuery } from '@/api/tools/tool-creditAuditQuery'

export default {
  data() {
    return {
      creditAuditQuery: {
        options: [
          {
            value: 'SIT',
            label: 'SIT'
          },
          {
            value: 'ALIUAT',
            label: 'ALIUAT'
          },
          {
            value: 'BaoSheng',
            label: 'BaoSheng'
          }
        ],
        env: '',
        mobile: '',
        deviceId: ''
      },
      creditAuditResult: [],
      whiteListData: [],
      userInfoData: [],
      applyInfoData: []
    }
  },
  methods: {
    // 提交查询
    submitForm() {
      this.$refs.creditAuditQuery.validate(valid => {
        if (valid) {
          this.$message.info('正在查询,请稍等')
          this.userInfoData = []
          this.applyInfoData = []
          this.creditAuditResult = []
          this.whiteListData = []
          crediAuditQuery({
            phone: this.creditAuditQuery.mobile,
            env: this.creditAuditQuery.env,
            deviceId: this.creditAuditQuery.deviceId
          }).then(resp => {
            if (!resp.data) {
              this.$message.success('根据手机号获取不到会员信息')
            } else if (resp.data === 'more than one member') {
              this.$message.success('根据手机号获取到多条会员信息')
            } else {
              this.userInfoData = resp.data.user_info
              this.applyInfoData = resp.data.apply_info
              this.creditAuditResult = resp.data.last_credit_audit_result
              this.whiteListData = resp.data.user_white_list_info
              this.$message.success(resp.desc)
            }
          })
        } else {
          return false
        }
      })
    },
    handleConfig() {},
    // 重置表单
    resetForm(formName) {
      if (this.$refs[formName] !== undefined) {
        this.$refs[formName].resetFields()
      }
    }
  }
}
</script>
<style scoped lang="scss">
.text {
  font-size: 14px;
}

.item {
  padding: 18px 0;
}

.box-card {
  width: 480px;
}
</style>
