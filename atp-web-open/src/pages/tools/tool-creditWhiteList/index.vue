<style lang="scss" scoped>
.del-dialog-cnt {
  font-size: 14px;
  text-align: center;
  margin-bottom: 20px;
}
</style>
<template>
  <d2-container>
    <el-alert title="请根据测试环境、手机号和设备号/商户号查询当前白名单配置情况，再根据需要选择设置。" type="success" show-icon></el-alert>
    <!--查询条件-->
    <el-form :model="filterForm" ref="filterForm" label-width="120px">
      <el-row :gutter="50">
        <el-col :span="6">
          <el-form-item label="测试环境" prop="env" :rules="{required: true, message: '不能为空', trigger: 'change'}">
            <el-select v-model="filterForm.env" placeholder="请选择环境">
              <el-option v-for="item in options" :key="item.value" :label="item.label" :value="item.value"></el-option>
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="手机号" prop="mobile" :rules="{required: true, message: '不能为空', trigger: 'blur'}">
            <el-input v-model="filterForm.mobile" placeholder="请输入手机号码" auto-complete="off"></el-input>
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="50">
        <el-col :span="6">
          <el-form-item label="授权白名单类型" prop="authWhiteListType">
            <el-radio v-model="authWhiteListType" label="merchantId">商户号</el-radio>
            <el-radio v-model="authWhiteListType" label="equipmentId">设备号</el-radio>
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item :label="whiteListId" prop="whitelist">
            <el-input v-model="filterForm.whitelist" :placeholder="'请输入'+whiteListId" auto-complete="off"></el-input>
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label>
            <el-button type="primary" @click="fetchWhiteList('filterForm')">获取白名单配置</el-button>
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
    <!--展示查询结果-->
    <el-row style="margin-top: 30px;margin-left: 20px">
      <el-button size="mini" type="success" icon="el-icon-check" circle></el-button>
      <span style="margin-right: 20px;font-size: 14px;color: #909399">-已配置</span>
      <el-button size="mini" type="danger" icon="el-icon-close" circle></el-button>
      <span style="margin-right: 20px;font-size: 14px;color: #909399">-未配置</span>
      <el-button size="mini" type="info" icon="el-icon-minus" circle></el-button>
      <span style="margin-right: 20px;font-size: 14px;color: #909399">-未知状态</span>
    </el-row>
    <el-table
      :data="creditConfData"
      border
      style="width: 100%"
      ref="creditConfData"
      tooltip-effect="light"
      :header-cell-style="{color:'black',background:'#eef1f6'}"
    >
      <el-table-column prop="creditNode" label="征信审核节点">
        <template slot-scope="scope">
          <span>{{ scope.row.creditNode }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="isWhiteList" label="白名单(过件)">
        <template slot-scope="scope">
          <el-button size="mini" type="success" icon="el-icon-check" circle v-if="scope.row.isWhiteList === 1"></el-button>
          <el-button size="mini" type="danger" icon="el-icon-close" circle v-else-if="scope.row.isWhiteList === 2"></el-button>
          <el-button size="mini" type="info" icon="el-icon-minus" circle v-else></el-button>
        </template>
      </el-table-column>
      <el-table-column prop="isBlackList" label="黑名单(拒件)">
        <template slot-scope="scope">
          <el-button size="mini" type="success" icon="el-icon-check" circle v-if="scope.row.isBlackList === 1"></el-button>
          <el-button size="mini" type="danger" icon="el-icon-close" circle v-else-if="scope.row.isBlackList === 2"></el-button>
          <el-button size="mini" type="info" icon="el-icon-minus" circle v-else-if="scope.row.isBlackList === 0"></el-button>
          <span v-else>CTA无黑名单</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" fixed="right">
        <template slot-scope="scope">
          <el-button type="text" @click="setWhiteList(scope.$index, scope.row)">设置白名单</el-button>
          <el-button type="text" @click="setBlackList(scope.$index, scope.row)" v-if="scope.row.creditNode !=='CTA'">设置黑名单</el-button>
          <el-button type="text" @click="clearWhiteList(scope.$index, scope.row)">清除白名单</el-button>
        </template>
      </el-table-column>
    </el-table>
    <!--设置白名单弹框-->
    <!--配置前置不可申请-->
    <el-dialog title="配置" :visible.sync="preApplyWhiteListVisible" width="30%">
      <div class="del-dialog-cnt">即将为手机号:({{filterForm.mobile}})配置前置不可申请白名单，是否确认？</div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="preApplyWhiteListVisible = false">取 消</el-button>
        <el-button type="primary" @click="setPreApplyWhiteList">确 定</el-button>
      </span>
    </el-dialog>
    <!--预授信&激活-->
    <el-dialog title="配置" :visible.sync="caWhiteListVisible" width="30%">
      <div class="del-dialog-cnt">即将为手机号:({{filterForm.mobile}})配置预授信&激活白名单，是否确认？</div>
      <el-form ref="CAForm" :model="CAForm" label-width="180px">
        <el-form-item label="线下大额额度(单位:元)" prop="generalAmount" :rules="[{ type: 'number', message: '必须为数字值'}]">
          <el-input v-model.number="CAForm.generalAmount" placeholder="请输入线下大额额度" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item label="现金贷/商城额度(单位:元)" prop="cashLoanAmount" :rules="[{ type: 'number', message: '必须为数字值'}]">
          <el-input v-model.number="CAForm.cashLoanAmount" placeholder="请输入现金贷额度" auto-complete="off"></el-input>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="caWhiteListVisible = false">取 消</el-button>
        <el-button type="primary" @click="setCaWhiteList('CAForm')">确 定</el-button>
      </span>
    </el-dialog>
    <!--配置再审（现金贷）-->
    <el-dialog title="配置" :visible.sync="caRetrialWhiteListVisible" width="30%">
      <div class="del-dialog-cnt">即将为手机号:({{filterForm.mobile}})配置再审(现金贷)白名单，是否确认？</div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="caRetrialWhiteListVisible = false">取 消</el-button>
        <el-button type="primary" @click="setCaRetrialWhiteList">确 定</el-button>
      </span>
    </el-dialog>
    <!--授权-->
    <el-dialog title="配置" :visible.sync="authWhiteListVisible" width="30%">
      <div class="del-dialog-cnt">即将为设备号/商户号:({{authForm.whitelist}})配置授权白名单，是否确认？</div>
      <el-form ref="authForm" :model="authForm" label-width="120px">
        <el-form-item class="test" label="白名单类型" prop="type">
          <el-radio v-model="authWhiteListType" label="merchantId">商户号</el-radio>
          <el-radio v-model="authWhiteListType" label="equipmentId">设备号</el-radio>
        </el-form-item>
        <el-form-item :label="whiteListId" prop="whitelist" :rules="{required: true, message: whiteListId + '不能为空', trigger: 'blur'}">
          <el-input v-model="authForm.whitelist" :placeholder="'请输入'+whiteListId" auto-complete="off" style="width: 300px"></el-input>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="authWhiteListVisible = false">取 消</el-button>
        <el-button type="primary" @click="setAuthWhiteList('authForm')">确 定</el-button>
      </span>
    </el-dialog>
    <!--CTA-->
    <el-dialog title="配置" :visible.sync="ctaWhiteListVisible" width="30%">
      <div class="del-dialog-cnt">即将为手机号:({{filterForm.mobile}})配置CTA白名单，是否确认？</div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="ctaWhiteListVisible = false">取 消</el-button>
        <el-button type="primary" @click="setCtaWhiteList">确 定</el-button>
      </span>
    </el-dialog>
    <!--设置黑名单弹框-->
    <el-dialog title="配置" :visible.sync="setblackListVisible" width="30%">
      <div class="del-dialog-cnt">即将为手机号:({{filterForm.mobile}})配置黑名单，会自动清除白名单，是否确认？</div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="setblackListVisible = false">取 消</el-button>
        <el-button type="primary" @click="handleSetBlackList">确 定</el-button>
      </span>
    </el-dialog>
    <!--清除白名单弹框-->
    <el-dialog title="配置" :visible.sync="clearWhiteListVisible" width="30%">
      <div class="del-dialog-cnt">即将为手机号:({{filterForm.mobile}})清除白名单，是否确认？</div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="clearWhiteListVisible = false">取 消</el-button>
        <el-button type="primary" @click="handleClearWhiteList">确 定</el-button>
      </span>
    </el-dialog>
    <!--清除授权白名单弹框-->
    <el-dialog title="配置" :visible.sync="clearAuthWhiteListVisible" width="30%">
      <div class="del-dialog-cnt">即将为设备号/商户号:({{authClearForm.whitelist}})清除白名单，是否确认？</div>
      <el-form ref="authForm" :model="authClearForm" label-width="120px">
        <el-form-item class="test" label="白名单类型" prop="type">
          <el-radio v-model="authWhiteListType" label="merchantId">商户号</el-radio>
          <el-radio v-model="authWhiteListType" label="equipmentId">设备号</el-radio>
        </el-form-item>
        <el-form-item :label="whiteListId" prop="whitelist" :rules="{required: true, message: whiteListId + '不能为空', trigger: 'blur'}">
          <el-input v-model="authClearForm.whitelist" :placeholder="'请输入'+whiteListId" auto-complete="off" style="width: 300px"></el-input>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="authWhiteListVisible = false">取 消</el-button>
        <el-button type="primary" @click="handleClearAuthWhiteList('authForm')">确 定</el-button>
      </span>
    </el-dialog>
  </d2-container>
</template>
<script>
import { configCredit, queryCredit } from '@/api/tools/tool-creditWhiteList'

export default {
  data() {
    return {
      filterForm: {
        // 查询条件表单
        env: '',
        mobile: '',
        whitelist: ''
      },
      authWhiteListType: 'equipmentId', // 授权白名单类型
      preApplyWhiteListVisible: false, // 前置不可申请
      caWhiteListVisible: false, // 预授信&激活
      caRetrialWhiteListVisible: false, // 现金贷再审
      authWhiteListVisible: false, // 授权
      ctaWhiteListVisible: false, // CTA
      setblackListVisible: false, // 设置黑名单弹框
      clearWhiteListVisible: false, // 清理白名单弹框
      clearAuthWhiteListVisible: false, // 清理授权白名单弹框
      creditNode: '', // 标识是哪个审核节点
      CAForm: {
        // 设置CA白名单表单
        generalAmount: 50000,
        greenSmallAmount: 10000,
        cashLoanAmount: 5000
      },
      authForm: {
        // 设置授权白名单表单
        whitelist: ''
      },
      authClearForm: {
        // 清理授权白名单表单
        whitelist: ''
      },
      creditConfData: [],
      // 测试环境备选值
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
      ]
    }
  },
  computed: {
    // 计算属性
    whiteListId() {
      if (this.authWhiteListType === 'merchantId') {
        return '商户号'
      } else {
        return '设备号'
      }
    }
  },
  methods: {
    // 查询白名单数据
    fetchWhiteList() {
      this.creditConfData = []
      let params = {
        env: this.filterForm.env,
        phone: this.filterForm.mobile
      }
      if (this.authWhiteListType === 'merchantId') {
        params['merchantId'] = this.filterForm.whitelist
      } else {
        params['deviceId'] = this.filterForm.whitelist
      }
      queryCredit(params).then(res => {
        this.creditConfData.push({
          creditNode: '前置不可申请',
          isWhiteList: res.data['preApply'][0],
          isBlackList: res.data['preApply'][1]
        })
        this.creditConfData.push({
          creditNode: '预授信&激活',
          isWhiteList: res.data['ca'][0],
          isBlackList: res.data['ca'][1]
        })
        this.creditConfData.push({
          creditNode: '再审(现金贷)',
          isWhiteList: res.data['caRetrial'][0],
          isBlackList: res.data['caRetrial'][1]
        })
        this.creditConfData.push({
          creditNode: '授权',
          isWhiteList: res.data['auth'][0],
          isBlackList: res.data['auth'][1]
        })
        this.creditConfData.push({
          creditNode: 'CTA',
          isWhiteList: res.data['cta'][0],
          isBlackList: res.data['cta'][1]
        })
      })
    },
    // 设置白名单
    setWhiteList(index, row) {
      if (row.creditNode === '前置不可申请') {
        this.preApplyWhiteListVisible = true
        this.creditNode = 'preApply'
      }
      if (row.creditNode === '预授信&激活') {
        this.caWhiteListVisible = true
        this.creditNode = 'ca'
      }
      if (row.creditNode === '再审(现金贷)') {
        this.caRetrialWhiteListVisible = true
        this.creditNode = 'caRetrial'
      }
      if (row.creditNode === '授权') {
        this.authWhiteListVisible = true
        this.creditNode = 'auth'
        this.authForm.whitelist = ''
      }
      if (row.creditNode === 'CTA') {
        this.ctaWhiteListVisible = true
        this.creditNode = 'cta'
      }
    },
    // 设置黑名单
    setBlackList(index, row) {
      this.setblackListVisible = true
      if (row.creditNode === '前置不可申请') {
        this.creditNode = 'preApply'
      }
      if (row.creditNode === '预授信&激活') {
        this.creditNode = 'ca'
      }
      if (row.creditNode === '再审(现金贷)') {
        this.creditNode = 'caRetrial'
      }
      if (row.creditNode === '授权') {
        this.creditNode = 'auth'
      }
      if (row.creditNode === 'CTA') {
        this.creditNode = 'cta'
      }
    },
    // 清除白名单
    clearWhiteList(index, row) {
      if (row.creditNode === '前置不可申请') {
        this.creditNode = 'preApply'
        this.clearWhiteListVisible = true
      }
      if (row.creditNode === '预授信&激活') {
        this.creditNode = 'ca'
        this.clearWhiteListVisible = true
      }
      if (row.creditNode === '再审(现金贷)') {
        this.creditNode = 'caRetrial'
        this.clearWhiteListVisible = true
      }
      if (row.creditNode === '授权') {
        this.creditNode = 'auth'
        this.clearAuthWhiteListVisible = true
      }
      if (row.creditNode === 'CTA') {
        this.creditNode = 'cta'
        this.clearWhiteListVisible = true
      }
    },
    // 设置前置不可申请白名单
    setPreApplyWhiteList() {
      let params = {
        env: this.filterForm.env,
        phone: this.filterForm.mobile,
        node: this.creditNode,
        action: 'addWhite'
      }
      configCredit(params).then(res => {
        this.$message.success(res.desc)
        this.preApplyWhiteListVisible = false
        this.fetchWhiteList()
      })
    },
    // 设置预授信&激活白名单
    setCaWhiteList() {
      let params = {
        env: this.filterForm.env,
        phone: this.filterForm.mobile,
        node: this.creditNode,
        action: 'addWhite'
      }
      configCredit(params).then(res => {
        this.$message.success(res.desc)
        this.caWhiteListVisible = false
        this.fetchWhiteList()
      })
    },
    // 设置现金贷再审
    setCaRetrialWhiteList() {
      let params = {
        env: this.filterForm.env,
        phone: this.filterForm.mobile,
        node: this.creditNode,
        action: 'addWhite'
      }
      configCredit(params).then(res => {
        this.$message.success(res.desc)
        this.caRetrialWhiteListVisible = false
        this.fetchWhiteList()
      })
    },
    // 设置授权白名单
    setAuthWhiteList() {
      let params = {
        env: this.filterForm.env,
        phone: this.filterForm.mobile,
        node: this.creditNode,
        action: 'addWhite'
      }
      if (this.authWhiteListType === 'merchantId') {
        params['merchantId'] = this.authForm.whitelist
      } else {
        params['deviceId'] = this.authForm.whitelist
      }
      configCredit(params).then(res => {
        this.$message.success(res.desc)
        this.authWhiteListVisible = false
        this.filterForm.whitelist = this.authForm.whitelist
        this.fetchWhiteList()
      })
    },
    // 设置CTA白名单
    setCtaWhiteList() {
      let params = {
        env: this.filterForm.env,
        phone: this.filterForm.mobile,
        node: this.creditNode,
        action: 'addWhite'
      }
      configCredit(params).then(res => {
        this.$message.success(res.desc)
        this.ctaWhiteListVisible = false
        this.fetchWhiteList()
      })
    },
    // 设置黑名单
    handleSetBlackList() {
      let params = {
        env: this.filterForm.env,
        phone: this.filterForm.mobile,
        node: this.creditNode,
        action: 'addBlack'
      }
      configCredit(params).then(res => {
        this.$message.success(res.desc)
        this.setblackListVisible = false
        this.fetchWhiteList()
      })
    },
    // 清除白名单
    handleClearWhiteList() {
      let params = {
        env: this.filterForm.env,
        phone: this.filterForm.mobile,
        node: this.creditNode,
        action: 'removeWhite'
      }
      configCredit(params).then(res => {
        this.$message.success(res.desc)
        this.clearWhiteListVisible = false
        this.fetchWhiteList()
      })
    },
    handleClearAuthWhiteList() {
      let params = {
        env: this.filterForm.env,
        phone: this.filterForm.mobile,
        node: this.creditNode,
        action: 'removeWhite'
      }
      if (this.creditNode === 'auth') {
        if (this.authWhiteListType === 'merchantId') {
          params['merchantId'] = this.authClearForm.whitelist
        } else {
          params['deviceId'] = this.authClearForm.whitelist
        }
      }
      configCredit(params).then(res => {
        this.$message.success(res.desc)
        this.clearAuthWhiteListVisible = false
        this.fetchWhiteList()
      })
    },
    // 重置表单
    resetForm(formName) {
      if (this.$refs[formName] !== 'undefined') {
        this.$refs[formName].resetFields()
      }
    }
  }
}
</script>
