<template>
  <d2-container>
    <el-form :model="form" ref="smscodeQuery" label-width="100px" inline>
      <el-form-item label="测试环境" prop="env" :rules="[{ required: true, message: '请选择环境', trigger: 'change' }]">
        <el-select v-model="form.env" placeholder="请选择">
          <el-option v-for="item in envOptions" :key="item.value" :label="item.label" :value="item.value"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="realTimeStatusQuery('smscodeQuery')" :loading="queryLoading">实时状态查询</el-button>
        <el-button @click="failSystemReboot">远程重启故障中服务</el-button>
      </el-form-item>
    </el-form>
    <el-tabs type="border-card">
      <el-tab-pane label="最新状态">
        <el-row type="flex" justify="space-around">
          <el-col :span="6">
            <!--显示服务异常的系统-->
            <el-card class="monitor-box-card">
              <div slot="header" class="clearfix">
                <el-badge :value="failNum">
                  <el-button size="small" type="danger" disabled>故障中</el-button>
                </el-badge>
              </div>
              <el-scrollbar wrap-class="monitorCardScrollList" view-class="view-box" :native="false">
                <div v-for="o in failOptions" :key="o" class="text item">{{ o }}</div>
              </el-scrollbar>
            </el-card>
          </el-col>
          <el-col :span="6">
            <!--显示构建中的系统-->
            <el-card class="monitor-box-card">
              <div slot="header" class="clearfix">
                <el-badge :value="buildNum">
                  <el-button size="small" type="primary" disabled>构建中</el-button>
                </el-badge>
              </div>
              <el-scrollbar wrap-class="monitorCardScrollList" view-class="view-box" :native="false">
                <div v-for="o in buildOptions" :key="o" class="text item">{{ o }}</div>
              </el-scrollbar>
            </el-card>
          </el-col>
          <el-col :span="6">
            <!--显示运行中的系统-->
            <el-card class="monitor-box-card">
              <div slot="header" class="clearfix">
                <el-badge :value="succNum">
                  <el-button size="small" type="success" disabled>运行中</el-button>
                </el-badge>
              </div>
              <el-scrollbar wrap-class="monitorCardScrollList" view-class="view-box" :native="false">
                <div v-for="o in succOptions" :key="o" class="text item">{{ o }}</div>
              </el-scrollbar>
            </el-card>
          </el-col>
        </el-row>
        <!--<el-badge :value="failNum" class="content" v-show="failVisible">
          <el-button size="small" type="danger" disabled>故障中</el-button>
        </el-badge>
        <el-row :gutter="10" style="display: flex; margin-top: 10px;">
          <el-col :span="4" v-for="i in 6" :key="i">
            <el-tooltip v-for="item in failOptions[i-1]" :key="item.key" class="item" effect="dark" :content="item[0]"
                        placement="top">
              <div :class="'transition-box'+ item[1]">
                {{item[0]}}
              </div>
            </el-tooltip>
            &lt;!&ndash;<el-tag type="danger" v-for="item in failOptions[i-1]" :key="item.key">&ndash;&gt;
            &lt;!&ndash;{{item[0]}}&ndash;&gt;
            &lt;!&ndash;</el-tag>&ndash;&gt;
          </el-col>
        </el-row>
        &lt;!&ndash;显示正在构建的系统&ndash;&gt;
        <el-badge :value="buildNum" class="content" v-show="buildVisible">
          <el-button size="small" type="primary" disabled>构建中</el-button>
        </el-badge>
        <el-row :gutter="10" style="display: flex; margin-top: 10px;">
          <el-col :span="4" v-for="i in 6" :key="i">
            <el-tooltip v-for="item in buildOptions[i-1]" :key="item.key" class="item" effect="dark" :content="item[0]"
                        placement="top">
              <div :class="'transition-box'+ item[1]">
                {{item[0]}}
              </div>
            </el-tooltip>
            &lt;!&ndash;<el-tag type="danger" v-for="item in buildOptions[i-1]" :key="item.key">&ndash;&gt;
            &lt;!&ndash;{{item[0]}}&ndash;&gt;
            &lt;!&ndash;</el-tag>&ndash;&gt;
          </el-col>
        </el-row>
        &lt;!&ndash;显示正常运行的系统&ndash;&gt;
        <el-badge :value="succNum" class="content" v-show="succVisible">
          <el-button size="small" type="success" disabled>运行中</el-button>
        </el-badge>
        <el-row :gutter="10" style="display: flex; margin-top: 10px;">
          <el-col :span="4" v-for="i in 6" :key="i">
            <el-tooltip v-for="item in succOptions[i-1]" :key="item.key" class="item" effect="dark" :content="item[0]"
                        placement="top">
              <div :class="'transition-box'+ item[1]">
                {{item[0]}}
              </div>
            </el-tooltip>
            &lt;!&ndash;<el-tag type="success" size="medium" v-for="item in succOptions[i-1]" :key="item.key">&ndash;&gt;
            &lt;!&ndash;{{item[0]}}&ndash;&gt;
            &lt;!&ndash;</el-tag>&ndash;&gt;
          </el-col>
        </el-row>-->
      </el-tab-pane>
      <el-tab-pane label="当天历史记录" class="current-his">
        <el-table :data="monitorHisData" style="width: 100%" height="600" size="medium">
          <el-table-column prop="checkTime" label="检查时间"></el-table-column>
          <el-table-column prop="checkResult" label="检查状态"></el-table-column>
          <el-table-column prop="buildSystem" label="构建中应用"></el-table-column>
          <el-table-column prop="failSystem" label="故障中应用"></el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
    <el-dialog title="远程重启" :visible.sync="rebootVisible" width="35%" :close-on-click-modal="false" :close-on-press-escape="false" ref="rebootVisible">
      <el-form ref="rebootForm" :model="rebootForm" :rules="rules">
        <el-form-item label="请选择需要重启的系统" prop="checkAll" label-width="160px">
          <el-checkbox :indeterminate="rebootForm.isIndeterminate" v-model="rebootForm.checkAll" @change="handleCheckAllChange">全选</el-checkbox>
        </el-form-item>
        <el-form-item prop="checkedSystem">
          <el-checkbox-group v-model="rebootForm.checkedSystem" @change="handleCheckedSystemChange">
            <el-checkbox v-for="(item, index) in rebootForm.needRebootSystem" name="checkedSystem" :key="index" :label="item">{{item}}</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="rebootVisible = false">取 消</el-button>
        <el-button type="primary" @click="sendReboot('rebootForm')">确 定</el-button>
      </span>
    </el-dialog>
  </d2-container>
</template>
<script>
import { getSystemStatus, rebootSystem, getLastStatus, getCurrentDayHis } from '@/api/monitor/businessStatus'

export default {
  name: 'monitor',
  data() {
    return {
      form: {
        env: 'ALIUAT'
      },
      envOptions: [
        {
          value: 'ALIUAT',
          label: 'ALIUAT'
        },
        {
          value: 'SIT',
          label: 'SIT'
        }
      ],
      succOptions: [],
      failOptions: [],
      buildOptions: [],
      //                failVisible: false,
      //                buildVisible: false,
      //                succVisible: false,
      failNum: 0,
      buildNum: 0,
      succNum: 0,
      rebootVisible: false,
      rebootForm: {
        isIndeterminate: false,
        checkAll: false,
        checkedSystem: [],
        needRebootSystem: []
      },
      monitorHisData: [],
      queryLoading: false,
      rules: {
        checkedSystem: [{ type: 'array', required: true, message: '请至少选择一项', trigger: 'change' }]
      }
    }
  },
  watch: {
    $route: {
      handler(newName, oldName) {
        if (newName.name === 'monitor-businessStatus') {
          this.getLastStatus('aliuat')
          this.getCurrentDayHis('aliuat')
        }
      },
      deep: true
    }
  },
  methods: {
    // 获取最近一次监控记录
    getLastStatus(envName) {
      this.succOptions = []
      this.failOptions = []
      this.buildOptions = []
      this.failNum = 0
      this.buildNum = 0
      this.succNum = 0
      getLastStatus({ envName: envName }).then(res => {
        res.data.forEach(item => {
          if (item[1] === 0) {
            this.succOptions.push(item[0])
          } else if (item[1] === 1) {
            this.failOptions.push(item[0])
          } else {
            this.buildOptions.push(item[0])
          }
        })
        this.failOptions.sort()
        this.buildOptions.sort()
        this.succOptions.sort()
        this.failNum = this.failOptions.length
        this.buildNum = this.buildOptions.length
        this.succNum = this.succOptions.length
        this.rebootForm.needRebootSystem = this.failOptions
      })
    },
    // 获取当天所有监控记录
    getCurrentDayHis(envName) {
      this.monitorHisData = []
      getCurrentDayHis({ envName: envName }).then(res => {
        res.data.forEach(item => {
          item.buildSystem = item.buildSystem.length === 0 ? '无' : item.buildSystem.sort().join('\n')
          item.failSystem = item.failSystem.length === 0 ? '无' : item.failSystem.sort().join('\n')
        })
        this.monitorHisData = res.data
      })
    },
    // 查询操作
    realTimeStatusQuery(formName) {
      this.succOptions = []
      this.failOptions = []
      this.buildOptions = []
      this.failNum = 0
      this.buildNum = 0
      this.succNum = 0
      this.queryLoading = true
      this.rebootForm.needRebootSystem = []
      //                this.failVisible = false
      //                this.buildVisible = false
      //                this.succVisible = false
      this.$refs[formName].validate(valid => {
        if (valid) {
          getSystemStatus({
            envName: this.form.env
          }).then(resp => {
            this.queryLoading = false
            resp.data.forEach(item => {
              if (item[1] === 0) {
                this.succOptions.push(item[0])
              } else if (item[1] === 1) {
                this.failOptions.push(item[0])
              } else {
                this.buildOptions.push(item[0])
              }
            })
            this.failOptions.sort()
            this.buildOptions.sort()
            this.succOptions.sort()
            //                            this.grouping(resp.data, 0, this.succOptions)
            //                            this.grouping(resp.data, 1, this.failOptions)
            //                            this.grouping(resp.data, 2, this.buildOptions)
            //                            let failRes = this.counting(this.failOptions)
            //                            this.failVisible = failRes[0]
            this.failNum = this.failOptions.length
            //                            let buildRes = this.counting(this.buildOptions)
            //                            this.buildVisible = buildRes[0]
            this.buildNum = this.buildOptions.length
            //                            let succRes = this.counting(this.succOptions)
            //                            this.succVisible = succRes[0]
            this.succNum = this.succOptions.length
            /* this.failOptions.forEach((item) => {
                                if (item.length !== 0) {
                                    item.forEach((param) => {
                                        this.rebootForm.needRebootSystem.push(param[0])
                                    })
                                }
                            })*/
            this.rebootForm.needRebootSystem = this.failOptions
            this.$message.success(resp.desc)
            this.getCurrentDayHis(this.form.env)
          })
        } else {
          return false
        }
      })
    },
    // 计算失败，构建中，成功的系统数量
    /* counting (options) {
                var count = 0
                options.forEach((item) => {
                    item.forEach((opts) => {
                        if (opts.length !== 0) {
                            count += 1
                        }
                    })
                })
                const visible = count !== 0
                const num = count.toString()
                return [visible, num]
            },*/
    // 分类排版，每行6个系统
    /* grouping (data, state, options) {
                const temData = []
                data.forEach((item) => {
                    if (item[1] === state) {
                        temData.push(item)
                    }
                })
                const temData0 = []
                for (let i = 0; i < temData.length; i += 6) {
                    temData0.push(temData[i])
                }
                options.push(temData0)
                const temData1 = []
                for (let i = 1; i < temData.length; i += 6) {
                    temData1.push(temData[i])
                }
                options.push(temData1)
                const temData2 = []
                for (let i = 2; i < temData.length; i += 6) {
                    temData2.push(temData[i])
                }
                options.push(temData2)
                const temData3 = []
                for (let i = 3; i < temData.length; i += 6) {
                    temData3.push(temData[i])
                }
                options.push(temData3)
                const temData4 = []
                for (let i = 4; i < temData.length; i += 6) {
                    temData4.push(temData[i])
                }
                options.push(temData4)
                const temData5 = []
                for (let i = 5; i < temData.length; i += 6) {
                    temData5.push(temData[i])
                }
                options.push(temData5)
            },*/
    // 打开重启系统弹窗
    failSystemReboot() {
      this.rebootVisible = true
      this.resetForm('rebootForm')
    },
    // 下发重启命令
    sendReboot(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          this.rebootVisible = false
          rebootSystem({
            envName: this.form.env,
            systemList: this.rebootForm.checkedSystem
          }).then(resp => {
            const failMessage = this.analysis(resp.data)
            this.$message({
              duration: 0,
              showClose: true,
              dangerouslyUseHTMLString: true,
              message: failMessage
            })
          })
        } else {
          return false
        }
      })
    },
    // 分析重启接口返回数据，对错误原因进行分类展示
    analysis(data) {
      const fail = data.fail
      const notRun = data.notRun
      const success = data.success
      var htmlFail = ''
      fail.forEach(item => {
        htmlFail += '<li>' + item + '</li>'
      })
      var htmlNotRun = ''
      notRun.forEach(item => {
        htmlNotRun += '<li>' + item + '</li>'
      })
      var htmlSucc = ''
      success.forEach(item => {
        htmlSucc += '<li>' + item + '</li>'
      })
      return '<h4>失败的系统:</h4>' + htmlFail + '<h4>未重启的系统:</h4>' + htmlNotRun + '<h4>成功的系统:</h4>' + htmlSucc
    },
    // 选择全部或取消选择全部
    handleCheckAllChange(val) {
      this.rebootForm.checkedSystem = this.rebootForm.checkAll ? this.rebootForm.needRebootSystem : []
      this.rebootForm.isIndeterminate = false
    },
    // 选择指定条件
    handleCheckedSystemChange(value) {
      let checkedCount = this.rebootForm.checkedSystem.length
      this.rebootForm.checkAll = checkedCount === this.rebootForm.needRebootSystem.length
      this.rebootForm.isIndeterminate = checkedCount > 0 && checkedCount < this.rebootForm.needRebootSystem.length
    },
    // 重置表单
    resetForm(formName) {
      if (this.$refs[formName] !== undefined) {
        this.$refs[formName].resetFields()
      }
    }
  }
}
</script>
<style lang="scss">
/*.transition-box0 {
    margin-bottom: 10px;
    border-radius: 4px;
    background-color: #67c23a;
    text-align: center;
    color: #fff;
    padding: 20px 20px;
    box-sizing: border-box;
    margin-right: 10px;
    max-height: 60px;
    font-size: 14px;
    font-weight: bold;
    !*超出部分省略号显示*!
    !*overflow: hidden;*!
    !*text-overflow: ellipsis;*!
    !*white-space: nowrap;*!
    height: auto;
    word-wrap: break-word;
    word-break: break-all;
    overflow: hidden;
  }

  .transition-box1 {
    margin-bottom: 10px;
    border-radius: 4px;
    background-color: #f76664;
    text-align: center;
    color: #fff;
    padding: 20px 20px;
    box-sizing: border-box;
    margin-right: 10px;
    max-height: 60px;
    font-size: 14px;
    font-weight: bold;
    !*超出部分省略号显示*!
    !*overflow: hidden;*!
    !*text-overflow: ellipsis;*!
    !*white-space: nowrap;*!
    height: auto;
    word-wrap: break-word;
    word-break: break-all;
    overflow: hidden;
  }

  .transition-box2 {
    margin-bottom: 10px;
    border-radius: 4px;
    background-color: #66b1ff;
    text-align: center;
    color: #fff;
    padding: 20px 20px;
    box-sizing: border-box;
    margin-right: 10px;
    max-height: 60px;
    font-size: 14px;
    font-weight: bold;
    !*超出部分省略号显示*!
    !*overflow: hidden;*!
    !*text-overflow: ellipsis;*!
    !*white-space: nowrap;*!
    height: auto;
    word-wrap: break-word;
    word-break: break-all;
    overflow: hidden;
  }*/

.monitor-box-card .text {
  font-size: 16px;
  color: #606266;
}

.monitor-box-card .item {
  margin-bottom: 18px;
}

.clearfix:before,
.clearfix:after {
  display: table;
  content: '';
}
.clearfix:after {
  clear: both;
}

.monitor-box-card {
  width: 480px;
}

.monitor-box-card .el-card__header {
  padding: 10px 20px;
}

.monitorCardScrollList {
  min-height: 550px;
  max-height: 550px;
}

.current-his .el-table .cell {
  white-space: pre-line;
}
</style>
