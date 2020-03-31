<style scoped lang="scss">
.context {
  font-size: 16px;
  font-weight: bold;
}
</style>
<template>
  <d2-container>
    <el-form class="context" :inline="true" :model="form" :rules="rules" ref="autotestDataQuery" size="small">
      <el-form-item label="业务中心" prop="businesscenter" label-width="80px">
        <el-select v-model="form.businesscenter" placeholder="请选择" @change="isselected">
          <el-option v-for="item in bcoptions" :key="item" :label="item" :value="item"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="项目名称" prop="projectname" label-width="70px">
        <el-select v-model="form.projectname" placeholder="请选择">
          <el-option v-for="item in pnoptions" :key="item" :label="item" :value="item"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="时间段" prop="datetimerange" label-width="70px">
        <el-date-picker
          v-model="form.datetimerange"
          type="datetimerange"
          align="right"
          unlink-panels
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          :picker-options="pickerOptions"
        ></el-date-picker>
      </el-form-item>
      <el-form-item>
        <div style="margin-left:100px">
          <el-button type="primary" @click="search('autotestDataQuery')">生成</el-button>
          <el-button @click="resetForm('autotestDataQuery')">重置</el-button>
        </div>
      </el-form-item>
    </el-form>
    <div class="charts" style="margin-top:30px">
      <div id="myChart" style="width:1500px;height:600px"></div>
    </div>
  </d2-container>
</template>
<script>
import { queryAutotestProject, queryAutotestResultByMonth } from '@/api/qadata/chart-successRateCount'

// 引入基本模板
let echarts = require('echarts/lib/echarts')
// 引入柱状图组件
require('echarts/lib/chart/line')
require('echarts/lib/component/tooltip')
require('echarts/lib/component/toolbox')
require('echarts/lib/component/legend')

export default {
  data() {
    return {
      form: {
        businesscenter: '全部',
        projectname: '全部',
        datetimerange: ''
      },
      bcoptions: ['全部'],
      pnoptions: ['全部'],
      alloptions: [],
      pickerOptions: {
        shortcuts: [
          {
            text: '最近一周',
            onClick(picker) {
              const end = new Date()
              const start = new Date()
              start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
              picker.$emit('pick', [start, end])
            }
          },
          {
            text: '最近一个月',
            onClick(picker) {
              const end = new Date()
              const start = new Date()
              start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
              picker.$emit('pick', [start, end])
            }
          },
          {
            text: '最近三个月',
            onClick(picker) {
              const end = new Date()
              const start = new Date()
              start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
              picker.$emit('pick', [start, end])
            }
          }
        ]
      },
      rules: {
        businesscenter: [
          {
            validator: (rule, value, callback) => {
              if (this.form.businesscenter === '') {
                callback(new Error('请选择业务中心'))
              } else {
                callback()
              }
            },
            trigger: 'blur,change'
          }
        ],
        projectname: [
          {
            validator: (rule, value, callback) => {
              if (this.form.projectname === '' || this.form.projectname === '全部') {
                callback(new Error('请选择具体的项目'))
              } else {
                callback()
              }
            },
            trigger: 'blur,change'
          }
        ],
        datetimerange: [
          {
            validator: (rule, value, callback) => {
              if (this.form.datetimerange === '') {
                callback(new Error('请选择开始和结束时间'))
              } else {
                callback()
              }
            },
            trigger: 'blur,change'
          }
        ]
      }
    }
  },
  mounted() {
    queryAutotestProject({}).then(resp => {
      this.alloptions = resp.desc
      for (let i in this.alloptions) {
        this.bcoptions.push(i)
        this.pnoptions = this.pnoptions.concat(this.alloptions[i])
      }
    })
  },
  methods: {
    drawLine(projectname, starttime, endtime) {
      let chartBox = document.getElementsByClassName('charts')[0]
      let myChart = document.getElementById('myChart')

      // 用于使chart自适应高度和宽度,通过窗体高宽计算容器高宽
      function resizeCharts() {
        myChart.style.width = chartBox.style.width + 'px'
        myChart.style.height = chartBox.style.height + 'px'
      }

      // 设置容器高宽
      resizeCharts()
      // 基于准备好的dom，初始化echarts实例
      let mainChart = echarts.init(myChart)
      // 绘制图表
      var option = null
      var seriesLabel = {
        normal: {
          show: true,
          textBorderWidth: 2
        }
      }
      // 指定图表的配置项和数据
      option = {
        title: {
          text: '按时间段统计冒烟测试执行成功率' + '(' + projectname + ')'
        },
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['成功率']
        },
        grid: {
          left: '5%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        toolbox: {
          right: '6%',
          feature: {
            saveAsImage: {}
          }
        },
        xAxis: {
          type: 'category',
          axisLabel: {
            interval: 0,
            rotate: 45,
            margin: 10
          },
          boundaryGap: false,
          data: []
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: '成功率',
            type: 'line',
            stack: '总量',
            label: seriesLabel,
            data: []
          }
        ]
      }
      mainChart.setOption(option)
      mainChart.showLoading()
      queryAutotestResultByMonth({
        projectName: projectname,
        starttime: starttime,
        endtime: endtime
      })
        .then(resp => {
          if (resp.resultList.length === 0) {
            mainChart.hideLoading()
            this.$message.warning('所选时间段内无数据!')
          } else {
            let xdata = []
            let ydata = []
            var len = resp.resultList.length
            for (var i = 0; i < len; i++) {
              xdata.push(resp.resultList[i].time)
              ydata.push(resp.resultList[i].testApr)
            }
            mainChart.hideLoading()
            mainChart.setOption({
              xAxis: {
                data: xdata
              },
              series: [
                {
                  data: ydata
                }
              ]
            })
          }
        })
        .catch(e => {
          mainChart.hideLoading()
        })
    },
    isselected(value) {
      this.form.projectname = ''
      this.pnoptions = ['全部']
      if (value === '全部') {
        for (let i in this.alloptions) {
          this.pnoptions = this.pnoptions.concat(this.alloptions[i])
        }
        this.form.projectname = '全部'
      } else {
        this.pnoptions = this.pnoptions.concat(this.alloptions[value])
        this.form.projectname = '全部'
      }
    },
    search(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          var starttime = this.form.datetimerange[0].getTime()
          var endtime = this.form.datetimerange[1].getTime()
          this.drawLine(this.form.projectname, starttime, endtime)
        } else {
          return false
        }
      })
    },
    resetForm(formName) {
      this.$refs[formName].resetFields()
      this.form.datetimerange = ''
    }
  }
}
</script>
