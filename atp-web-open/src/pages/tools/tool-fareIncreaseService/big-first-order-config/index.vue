<template>
  <div>
    <el-form :model="fareIncreaseServiceConfig.searchForm" inline labelWidth="80px" size="mini" ref="fareIncreaseServiceConfigSearchFrom">
      <el-form-item label="场景" prop="sceneSearch">
        <el-select v-model="fareIncreaseServiceConfig.searchForm.sceneSearch" filterable placeholder="请选择" clearable>
          <el-option v-for="(val, key, index) in mappingList.sceneMap" :key="index" :label="val" :value="val"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="资方" prop="fundSearch">
        <el-input v-model="fareIncreaseServiceConfig.searchForm.fundSearch" size="mini" placeholder="输入关键字搜索"></el-input>
      </el-form-item>
      <el-form-item label="加价类型" prop="typeSearch">
        <el-select v-model="fareIncreaseServiceConfig.searchForm.typeSearch" placeholder="请选择" clearable>
          <el-option v-for="(val, key, index) in mappingList.fareIncreaseTypeMap" :key="index" :label="val" :value="val"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="getConfigData">刷新</el-button>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handAdd">新增</el-button>
      </el-form-item>
    </el-form>
    <el-table class="table-layout" :data="tables" :span-method="objectSpanMethod" size="mini" border highlight-current-row ref="tables">
      <el-table-column prop="scene" label="场景" width="120"></el-table-column>
      <el-table-column v-for="(v, i) in fareIncreaseServiceConfig.columns" :prop="v.field" :label="v.title" :width="v.width" :key="i">
        <template slot-scope="scope">
          <span v-if="scope.row.isSet">
            <el-select v-if="v.field === 'fareIncreaseType'" size="mini" v-model="fareIncreaseServiceConfig.sel[v.field]" placeholder="请选择">
              <el-option v-for="(val, key, index) in mappingList.fareIncreaseTypeMap" :key="index" :label="val" :value="val"></el-option>
            </el-select>
            <el-input v-else size="mini" placeholder="请输入内容" v-model="fareIncreaseServiceConfig.sel[v.field]"></el-input>
          </span>
          <span v-else>{{ scope.row[v.field] }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" fixed="right" width="100">
        <template slot-scope="scope">
          <span class="el-tag el-tag--info el-tag--mini" style="cursor: pointer;" @click="handEdit(scope.row, scope.$index)">{{ scope.row.isSet ? '保存' : '修改' }}</span>
          <span v-if="!scope.row.isSet" class="el-tag el-tag--danger el-tag--mini" style="cursor: pointer;" @click="handDelete(scope.row, scope.$index)">删除</span>
          <span v-else class="el-tag el-tag--mini" style="cursor: pointer;" @click="handCancel(scope.row, scope.$index)">取消</span>
        </template>
      </el-table-column>
    </el-table>

    <!--现金贷加价策略新增配置表单-->
    <el-dialog
      title="配置"
      :visible.sync="fareIncreaseServiceConfig.editVisible"
      width="40%"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      ref="fareIncreaseServiceConfigDialog"
    >
      <el-form :model="fareIncreaseServiceConfig.addForm" labelWidth="110px" labelPosition="right" size="mini" ref="fareIncreaseServiceConfigAddFrom">
        <el-row :gutter="5">
          <el-col :span="12">
            <el-form-item label="场景" prop="scene" :rules="[
                { required: true, message: '场景必填', trigger: 'change' }
              ]">
              <el-select v-model="fareIncreaseServiceConfig.addForm.scene" filterable placeholder="请选择" clearable>
                <el-option v-for="(val, key, index) in mappingList.sceneMap" :key="index" :label="val" :value="val"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="资方" prop="fundId" :rules="[
                { required: true, message: '资方必填', trigger: 'blur' }
              ]">
              <el-input v-model="fareIncreaseServiceConfig.addForm.fundId" size="mini" placeholder="请输入"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="5">
          <el-col :span="12">
            <el-form-item label="用户评级" prop="userLevel" :rules="[
                { required: true, message: '用户评级必填', trigger: 'blur' }
              ]">
              <el-input v-model="fareIncreaseServiceConfig.addForm.userLevel" size="mini" placeholder="请输入"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="适用期数" prop="period" :rules="[
                { required: true, message: '适用期数必填', trigger: 'blur' }
              ]">
              <el-input v-model.number="fareIncreaseServiceConfig.addForm.period" type="number" size="mini" placeholder="请输入"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="5">
          <el-col :span="12">
            <el-form-item
              label="加价类型"
              prop="fareIncreaseType"
              :rules="[
                { required: true, message: '加价类型必填', trigger: 'change' }
              ]"
            >
              <el-select v-model="fareIncreaseServiceConfig.addForm.fareIncreaseType" placeholder="请选择" clearable>
                <el-option v-for="(val, key, index) in mappingList.fareIncreaseTypeMap" :key="index" :label="val" :value="val"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="总保费费率" prop="totalFeeRate" :rules="[
                { required: true, message: '总保费费率必填', trigger: 'blur' }
              ]">
              <el-input v-model.number="fareIncreaseServiceConfig.addForm.totalFeeRate" type="number" size="mini" placeholder="请输入"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="5">
          <el-form-item label="趸缴费率" prop="onetimeFeeRate">
            <el-input v-model.number="fareIncreaseServiceConfig.addForm.onetimeFeeRate" type="number" size="mini" placeholder="请输入"></el-input>
          </el-form-item>
        </el-row>
        <el-row :gutter="5">
          <el-form-item label="期缴费率" prop="periodFeeRateList">
            <el-input
              v-model="fareIncreaseServiceConfig.addForm.periodFeeRateList"
              type="textarea"
              size="mini"
              :autosize="{ minRows: 4, maxRows: 6 }"
              placeholder="请输入"
            ></el-input>
          </el-form-item>
        </el-row>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="fareIncreaseServiceConfig.editVisible = false">取 消</el-button>
        <el-button type="primary" @click="saveEdit('fareIncreaseServiceConfigAddFrom')">确 定</el-button>
      </span>
    </el-dialog>
  </div>
</template>
<script>
import { queryFareIncreaseServiceConfig, setBigFirstOrderConfig } from '@/api/tools/tool-fareIncreaseService'
import { isJsonString } from '@/libs/common'
var env = 'ALIUAT'

export default {
  name: 'big-first-order-config',
  props: {
    mappingList: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      // 现金贷按期加价策略配置
      fareIncreaseServiceConfig: {
        spanArr: [], // 记录每行是否需要合并
        pos: null, // 记录当前行索引
        searchForm: {
          // 查询表单
          sceneSearch: '', // 场景条件
          fundSearch: '', // 资方条件
          typeSearch: '' // 加价类型条件
        },
        addForm: {
          // 新增表单
          scene: '',
          fundId: '',
          userLevel: '',
          period: '',
          fareIncreaseType: '',
          totalFeeRate: '',
          onetimeFeeRate: '',
          periodFeeRateList: ''
        },
        editVisible: false, // 新增弹框是否显示
        sel: null, // 选中行
        columns: [
          // 表格列
          /* { field: "scene", title: "场景", width: 120 },*/
          { field: 'fundId', title: '资方', width: 100 },
          { field: 'fareIncreaseType', title: '加价类型', width: 120 },
          { field: 'userLevel', title: '用户评级', width: 80 },
          { field: 'period', title: '适用期数', width: 80 },
          { field: 'totalFeeRate', title: '总保费费率', width: 120 },
          { field: 'onetimeFeeRate', title: '趸缴费率', width: 120 },
          { field: 'periodFeeRateList', title: '期缴费率' }
        ],
        data: [] // 表格数据
      }
    }
  },
  computed: {
    // 现金贷按期加价策略配置页面查询过滤
    tables: function() {
      let fundSearch = this.fareIncreaseServiceConfig.searchForm.fundSearch
      let sceneSearch = this.fareIncreaseServiceConfig.searchForm.sceneSearch
      let typeSearch = this.fareIncreaseServiceConfig.searchForm.typeSearch
      if (fundSearch || sceneSearch || typeSearch) {
        return this.fareIncreaseServiceConfig.data.filter(function(dataNews) {
          return (
            String(dataNews['fundId'])
              .toLowerCase()
              .includes(fundSearch.toLowerCase())
            && String(dataNews['scene'])
              .toLowerCase()
              .includes(sceneSearch.toLowerCase())
            && String(dataNews['fareIncreaseType'])
              .toLowerCase()
              .includes(typeSearch.toLowerCase())
          )
        })
      }
      return this.fareIncreaseServiceConfig.data
    }
  },
  watch: {
    // 监听现金贷按期加价配置页面列表数据变化，重新进行合并行
    tables(newName, oldName) {
      this.fareIncreaseServiceConfig.spanArr = []
      this.fareIncreaseServiceConfig.pos = 0
      this.getSpanArr(newName, this.fareIncreaseServiceConfig.spanArr, this.fareIncreaseServiceConfig.pos, 'scene')
    }
  },
  mounted() {
    this.refreshData()
  },
  methods: {
    refreshData() {
      this.fareIncreaseServiceConfig.data = []
      // 从后台获取当前disconf配置
      queryFareIncreaseServiceConfig({ env: env }).then(res => {
        let incorrectObj = res.data.incorrectConfig
        let correctObj = res.data.correctConfig
        if (JSON.stringify(incorrectObj) !== '{}') {
          let errMsg = Object.keys(incorrectObj).join('\n')
          this.$message.warning(errMsg + '上述配置项数据异常，无法解析')
        }
        if (JSON.stringify(correctObj) !== '{}') {
          for (let n in correctObj) {
            if (n === 'feeRateStrategyOfBigFirstOrder') {
              // 现金贷按期配置加价策略
              let id = 1
              correctObj.feeRateStrategyOfBigFirstOrder.forEach(item => {
                if (item.hasOwnProperty('periodFeeRateList')) {
                  item.periodFeeRateList = JSON.stringify(item.periodFeeRateList)
                }
                item['id'] = id++
                item['isSet'] = false
              })
              this.fareIncreaseServiceConfig.data = correctObj.feeRateStrategyOfBigFirstOrder
              this.getSpanArr(this.fareIncreaseServiceConfig.data, this.fareIncreaseServiceConfig.spanArr, this.fareIncreaseServiceConfig.pos, 'scene')
            }
          }
        }
      })
    },
    // 处理需要合并的行
    getSpanArr(data, spanArr, pos, filter) {
      for (var i = 0; i < data.length; i++) {
        if (i === 0) {
          spanArr.push(1)
          pos = 0
        } else {
          // 判断当前元素与上一个元素是否相同
          if (data[i][filter] === data[i - 1][filter]) {
            spanArr[pos] += 1
            spanArr.push(0)
          } else {
            spanArr.push(1)
            pos = i
          }
        }
      }
    },
    objectSpanMethod({ row, column, rowIndex, columnIndex }) {
      if (columnIndex === 0) {
        const _row = this.fareIncreaseServiceConfig.spanArr[rowIndex]
        const _col = _row > 0 ? 1 : 0
        return {
          rowspan: _row,
          colspan: _col
        }
      }
    },
    // 刷新数据
    getConfigData() {
      this.resetForm('fareIncreaseServiceConfigSearchFrom')
      this.refreshData()
    },
    // 重置表单
    resetForm(formName) {
      if (this.$refs[formName] !== undefined) {
        this.$refs[formName].resetFields()
      }
    },
    // 新增现金贷加价策略配置
    handAdd() {
      this.fareIncreaseServiceConfig.editVisible = true
      this.fareIncreaseServiceConfig.addForm.scene = '大额首单现金贷'
      this.resetForm('fareIncreaseServiceConfigAddFrom')
    },
    // 保存现金贷加价策略配置
    saveEdit(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          if (this.fareIncreaseServiceConfig.addForm.scene !== '大额首单现金贷') {
            this.$message.warning('场景不正确,只能配置大额首单现金贷')
            return false
          }
          if (!this.fareIncreaseServiceConfig.addForm.onetimeFeeRate && !this.fareIncreaseServiceConfig.addForm.periodFeeRateList) {
            this.$message.warning('趸缴费率和期缴费率不能同时为空')
            return false
          }
          if (this.fareIncreaseServiceConfig.addForm.periodFeeRateList && !isJsonString(this.fareIncreaseServiceConfig.addForm.periodFeeRateList)) {
            this.$message.warning('期缴费率格式不正确')
            return false
          }
          let reqData = { env: env, action: 'add' }
          Object.assign(reqData, this.fareIncreaseServiceConfig.addForm)
          this.submitData(reqData).then(() => {
            this.fareIncreaseServiceConfig.editVisible = false
            this.refreshData()
          })
        }
      })
    },
    // 提交数据到后台
    submitData(data) {
      return new Promise((resolve, reject) => {
        setBigFirstOrderConfig(data).then(res => {
          this.$message.success(res.desc)
          resolve(1)
        })
      })
    },
    handCancel(row, index) {
      row.isSet = false
    },
    // 修改现金贷加价策略配置
    handEdit(row, index) {
      // 点击修改 判断是否已经保存所有操作
      for (let i of this.fareIncreaseServiceConfig.data) {
        if (i.isSet && i.id !== row.id) {
          this.$message.warning('请先保存当前编辑项')
          return false
        }
      }
      // 提交数据
      if (row.isSet) {
        let data = JSON.parse(JSON.stringify(this.fareIncreaseServiceConfig.sel))

        if (data['fundId'] === '') {
          this.$message.warning('资方不能为空')
          return false
        }
        if (data['userLevel'] === '') {
          this.$message.warning('用户评级不能为空')
          return false
        }
        if (data['period'] === '') {
          this.$message.warning('适用期数不能为空')
          return false
        }

        if (!data['onetimeFeeRate'] && !data['periodFeeRateList']) {
          this.$message.warning('趸缴费率和期缴费率不能同时为空')
          return false
        }
        if (data['periodFeeRateList'] && !isJsonString(data['periodFeeRateList'])) {
          this.$message.warning('期缴费率格式不正确')
          return false
        }

        data['period'] = parseInt(data['period'])
        data['totalFeeRate'] = data['totalFeeRate'] ? parseFloat(data['totalFeeRate']) : 0
        data['onetimeFeeRate'] = data['onetimeFeeRate'] ? parseFloat(data['onetimeFeeRate']) : 0

        let reqData = { env: env, action: 'edit' }
        Object.assign(reqData, data)
        this.submitData(reqData).then(() => {
          row.isSet = false
          this.refreshData()
        })
      } else {
        this.fareIncreaseServiceConfig.sel = JSON.parse(JSON.stringify(row))
        row.isSet = true
      }
    },
    // 删除配置
    handDelete(row, index) {
      this.$confirm('此操作将永久删除配置, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
        .then(() => {
          let reqData = { env: env, action: 'del' }
          Object.assign(reqData, row)
          this.submitData(reqData).then(() => {
            this.refreshData()
          })
        })
        .catch(() => {
          this.$message({
            type: 'info',
            message: '已取消删除'
          })
        })
    }
  }
}
</script>
<style lang="scss">
.table-layout {
  margin-bottom: 20px;
}
</style>
