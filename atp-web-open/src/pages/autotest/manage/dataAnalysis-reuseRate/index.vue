<template>
  <d2-container>
    <div class="table_container">
      <el-tabs type="border-card">
        <el-tab-pane label="当前整体复用率">
          <el-form ref="totalBaseForm" :model="totalBaseForm" label-width="80px" inline>
            <el-form-item label="公司" prop="companyId" :rules="[{required:true,message:'请选择公司',trigger:'change'}]">
              <el-select v-model="totalBaseForm.companyId" filterable placeholder="请选择公司" clearable @change="companyChangeForTotalBase">
                <el-option v-for="item in companyList" :key="item.companyId" :label="item.companyName" :value="item.companyId"></el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="系统" prop="systemId">
              <el-select v-model="totalBaseForm.systemId" filterable placeholder="请选择系统" clearable @change="systemChangeForTotalBase">
                <el-option v-for="item in totalBaseForm.systemList" :key="item.systemId" :label="item.label" :value="item.systemId"></el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="接口" prop="intfId">
              <el-select v-model="totalBaseForm.intfId" filterable clearable placeholder="请选择接口">
                <el-option v-for="item in totalBaseForm.intfList" :key="item.intfId" :label="item.label" :value="item.intfId"></el-option>
              </el-select>
            </el-form-item>
            <!--<el-form-item label="所属阶段" prop="stage">
              <el-select v-model="totalBaseForm.grained" filterable placeholder="请选择所属阶段">
                <el-option v-for="item in totalBaseForm.stageOptions" :key="item" :label="item"
                           :value="item">
                </el-option>
              </el-select>
            </el-form-item>-->
            <el-button type="primary" icon="el-icon-search" @click="getDataForTotalBase">搜 索</el-button>
          </el-form>
          <el-tabs>
            <el-tab-pane label="图表">
              <!--柱形统计图和折线统计图测试-->
              <el-scrollbar wrap-class="scroll-view" view-class="view-box" :native="false">
                <div id="myEchartPillar" ref="myEchartPillar"></div>
              </el-scrollbar>
            </el-tab-pane>
            <el-tab-pane label="详细数据">
              <el-table :data="totalBaseForm.detailData" style="width: 100%" max-height="650">
                <el-table-column prop="labelName" label="系统/接口/用例名称"></el-table-column>
                <el-table-column prop="totalReuseNum" label="复用总次数"></el-table-column>
                <el-table-column prop="succReuseNum" label="复用成功次数"></el-table-column>
                <el-table-column prop="failReuseNum" label="复用失败次数"></el-table-column>
                <el-table-column prop="succRate" label="复用成功率"></el-table-column>
              </el-table>
            </el-tab-pane>
          </el-tabs>
        </el-tab-pane>
        <el-tab-pane label="复用率变化趋势">
          <el-form ref="trendBaseForm" :model="trendBaseForm" label-width="80px" inline>
            <el-row>
              <el-form-item label="公司" prop="companyId" :rules="[{required:true,message:'请选择公司',trigger:'change'}]">
                <el-select v-model="trendBaseForm.companyId" filterable placeholder="请选择公司" clearable @change="companyChangeForTrendBase">
                  <el-option v-for="item in companyList" :key="item.companyId" :label="item.companyName" :value="item.companyId"></el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="系统" prop="systemId">
                <el-select v-model="trendBaseForm.systemId" filterable placeholder="请选择系统" clearable @change="systemChangeForTrendBase">
                  <el-option v-for="item in trendBaseForm.systemList" :key="item.systemId" :label="item.label" :value="item.systemId"></el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="接口" prop="intfId">
                <el-select v-model="trendBaseForm.intfId" filterable clearable placeholder="请选择接口">
                  <el-option v-for="item in trendBaseForm.intfList" :key="item.intfId" :label="item.label" :value="item.intfId"></el-option>
                </el-select>
              </el-form-item>
            </el-row>
            <el-row>
              <el-form-item label="统计周期" prop="statPeriod" :rules="[{required:true,message:'请选择统计周期',trigger:'change'}]">
                <el-select v-model="trendBaseForm.statPeriod" filterable placeholder="请选择测试任务">
                  <el-option v-for="item in trendBaseForm.statPeriodList" :key="item.value" :label="item.label" :value="item.value"></el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="时间范围" prop="timeRange">
                <el-date-picker
                  v-model="trendBaseForm.timeRange"
                  type="daterange"
                  :picker-options="pickerOptions"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  align="right"
                ></el-date-picker>
              </el-form-item>
              <el-button type="primary" icon="el-icon-search" @click="getDataForTrendBase">搜 索</el-button>
            </el-row>
          </el-form>
          <el-tabs>
            <el-tab-pane label="图表">
              <!--柱形统计图和折线统计图测试-->
              <el-scrollbar wrap-class="scroll-view" view-class="view-box" :native="false">
                <div id="myEchartLine" ref="myEchartLine"></div>
              </el-scrollbar>
            </el-tab-pane>
            <el-tab-pane label="详细数据">
              <el-table :data="trendBaseForm.detailData" style="width: 100%" max-height="250">
                <el-table-column prop="labelName" label="统计日期"></el-table-column>
                <el-table-column prop="totalReuseNum" label="复用总次数"></el-table-column>
                <el-table-column prop="succReuseNum" label="复用成功次数"></el-table-column>
                <el-table-column prop="failReuseNum" label="复用失败次数"></el-table-column>
                <el-table-column prop="succRate" label="复用成功率"></el-table-column>
              </el-table>
            </el-tab-pane>
          </el-tabs>
        </el-tab-pane>
      </el-tabs>
    </div>
  </d2-container>
</template>

<script>
import echarts from 'echarts'
import { fetchCompanyList } from '@/api/autotest/manage/resource-apiManage/company'
import { queryByCompanyId } from '@/api/autotest/manage/resource-apiManage/system'
import { queryByProjectId } from '@/api/autotest/manage/resource-apiManage/api'
import { getReuseSummary, getReuseTrend } from '@/api/autotest/manage/dataAnalysis-reuseRate'

export default {
  name: 'reuseRate',
  data() {
    return {
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
      companyList: [],
      totalBaseForm: {
        companyId: '',
        systemId: '',
        intfId: '',
        systemList: [],
        intfList: [],
        //                    stage: '',
        //                    stageOptions: ['接口测试阶段', '回归测试阶段'],
        detailData: []
      },
      trendBaseForm: {
        companyId: '',
        systemId: '',
        intfId: '',
        systemList: [],
        intfList: [],
        statPeriod: 'day',
        statPeriodList: [
          {
            label: '按天',
            value: 'day'
          },
          {
            label: '按周',
            value: 'week'
          },
          {
            label: '按月',
            value: 'month'
          }
        ],
        timeRange: [new Date(new Date() - 30 * 24 * 3600 * 1000), new Date()],
        detailData: []
      }
    }
  },
  mounted() {
    this.getCompanyList()
  },
  methods: {
    // 获取公司列表
    getCompanyList() {
      fetchCompanyList({}).then(res => {
        this.companyList = res.companyList
        if (res.code === '000') {
          this.totalBaseForm.companyId = res.companyList[0].companyId
          this.trendBaseForm.companyId = res.companyList[0].companyId
          this.getSystemForTotalBase(this.totalBaseForm.companyId)
          this.getSystemForTrendBase(this.trendBaseForm.companyId)
        } else {
          this.$message.error(res.desc)
        }
      })
    },
    // 获取公司下系统列表
    getSystemForTotalBase(id) {
      queryByCompanyId({ companyId: id }).then(res => {
        this.totalBaseForm.systemList = res.allSystemList
      })
    },
    // 获取系统下引用/未引用接口
    getInterfaceForTotalBase(id) {
      queryByProjectId({ systemId: id }).then(res => {
        this.totalBaseForm.intfList = res.intfList
      })
    },
    // 获取公司下系统列表
    getSystemForTrendBase(id) {
      queryByCompanyId({ companyId: id }).then(res => {
        this.trendBaseForm.systemList = res.allSystemList
      })
    },
    // 获取系统下引用/未引用接口
    getInterfaceForTrendBase(id) {
      queryByProjectId({ systemId: id }).then(res => {
        this.trendBaseForm.intfList = res.intfList
      })
    },
    // 切换公司--整体复用率页面
    companyChangeForTotalBase() {
      this.totalBaseForm.systemId = ''
      this.getSystemForTotalBase(this.totalBaseForm.companyId)
    },
    // 切换系统--整体复用率页面
    systemChangeForTotalBase() {
      this.totalBaseForm.intfId = ''
      this.getInterfaceForTotalBase(this.totalBaseForm.systemId)
    },
    // 切换公司--复用率趋势页面
    companyChangeForTrendBase() {
      this.trendBaseForm.systemId = ''
      this.getSystemForTrendBase(this.trendBaseForm.companyId)
    },
    // 切换系统--复用率趋势页面
    systemChangeForTrendBase() {
      this.trendBaseForm.intfId = ''
      this.getInterfaceForTrendBase(this.trendBaseForm.systemId)
    },
    // 查询图表数据
    getDataForTotalBase() {
      getReuseSummary({
        companyId: this.totalBaseForm.companyId,
        systemId: this.totalBaseForm.systemId,
        intfId: this.totalBaseForm.intfId
      }).then(res => {
        this.totalBaseForm.detailData = JSON.parse(JSON.stringify(res.valueList))
        this.totalBaseForm.detailData.reverse()
        const data = res.valueList
        const yData = []
        const seriesSuccData = []
        const seriesFailData = []
        data.forEach(item => {
          yData.push(item.labelName)
          seriesSuccData.push(item.succReuseNum)
          seriesFailData.push(item.failReuseNum)
        })
        this.getPillar(yData, seriesSuccData, seriesFailData)
      })
    },
    // 查询图表数据
    getDataForTrendBase() {
      //                var dates = Math.floor(this.trendBaseForm.timeRange[1] - this.trendBaseForm.timeRange[0]) / (1000 * 60 * 60 * 24)
      //                console.log(dates)
      let startTimestamp = null
      let endTimestamp = null
      if (this.trendBaseForm.timeRange) {
        startTimestamp = this.trendBaseForm.timeRange[0].getTime() / 1000
        endTimestamp = this.trendBaseForm.timeRange[1].getTime() / 1000
      }
      getReuseTrend({
        companyId: this.trendBaseForm.companyId,
        systemId: this.trendBaseForm.systemId,
        intfId: this.trendBaseForm.intfId,
        period: this.trendBaseForm.statPeriod,
        startTimestamp: startTimestamp,
        endTimestamp: endTimestamp
      }).then(res => {
        this.trendBaseForm.detailData = JSON.parse(JSON.stringify(res.valueList))
        this.trendBaseForm.detailData.reverse()
        const data = res.valueList
        const xData = []
        const seriesTotalData = []
        data.forEach(item => {
          xData.push(item.labelName)
          seriesTotalData.push(item.totalReuseNum)
        })
        this.getLine(xData, seriesTotalData)
      })
    },
    // 柱形统计图
    getPillar(ydata, seriesSuccData, seriesFailData) {
      {
        let myEchartPillar = document.getElementById('myEchartPillar')
        // 自适应宽高
        let myChartContainer = function() {
          myEchartPillar.style.width = window.innerWidth - 400 + 'px'
          myEchartPillar.style.height = window.innerHeight - 400 + 'px'
        }
        myChartContainer()
        // 基于准备好的dom(myEchartPillar)，初始化echarts实例
        let myChart = echarts.init(myEchartPillar)
        myChart.clear()
        // 指定图表的配置项和数据，绘制图表
        myChart.setOption({
          // 图表名称
          title: {
            text: '复用率统计图'
          },
          // 图表颜色
          color: ['#91c7ae', '#c23531'],
          // 提示
          tooltip: {
            // 触发类型,axis:坐标轴触发，主要在柱状图，折线图等会使用类目轴的图表中使用。
            trigger: 'axis',
            axisPointer: {
              // 坐标轴指示器，坐标轴触发有效，默认为直线，可选为：'line' | 'shadow'
              type: 'shadow'
            }
          },
          legend: {
            data: ['复用成功次数', '复用失败次数']
          },
          grid: {
            show: true,
            // grid 组件离容器左侧的距离。
            left: '5%',
            // grid 组件离容器右侧的距离。
            right: '15%',
            // grid 组件离容器下侧的距离。
            bottom: '10%',
            // grid 区域是否包含坐标轴的刻度标签。true这常用于『防止标签溢出』的场景，标签溢出指的是，标签长度动态变化时，可能会溢出容器或者覆盖其他组件。
            containLabel: true,
            // 网格背景色，此配置项生效的前提是，设置了 show: true
            backgroundColor: '#E7F1F5'
          },
          // 直角坐标系 grid 中的 x 轴
          yAxis: [
            {
              // 'category' 类目轴
              type: 'category',
              // 坐标轴名称
              name: '系统/接口/用例',
              // 坐标轴名称显示位置
              nameLocation: 'end',
              // 坐标数据
              data: ydata,
              // 坐标轴刻度相关设置
              axisTick: {
                // 为 true 可以保证刻度线和标签对齐
                alignWithLabel: true
              },
              // 调整坐标名称展示方式
              axisLabel: {
                interval: 0,
                rotate: 30
              },
              // 坐标轴名称与轴线之间的距离
              nameGap: 2
            }
          ],
          // 直角坐标系 grid 中的 y 轴
          xAxis: [
            {
              // 'value' 数值轴，适用于连续数据
              type: 'value',
              // 坐标轴名称
              name: '复用次数',
              // 坐标轴的标签是否响应和触发鼠标事件，默认不响应
              triggerEvent: true
            }
          ],
          // 系列列表。每个系列通过 type 决定自己的图表类型
          series: [
            {
              // 系列名称，用于tooltip的显示，legend 的图例筛选，在 setOption 更新数据和配置项时用于指定对应的系列
              name: '复用成功次数',
              // 类型为柱状/条形图
              type: 'bar',
              stack: '总量',
              // 柱条的宽度，不设时自适应。支持设置成相对于类目宽度的百分比。
              barWidth: '60%',
              // 图形上的文本标签，可用于说明图形的一些数据信息
              label: {
                normal: {
                  // 是否显示标签
                  show: true,
                  // 通过相对的百分比或者绝对像素值表示标签相对于图形包围盒左上角的位置
                  position: 'insideRight'
                }
              },
              // 系列中的数据内容数组
              data: seriesSuccData
            },
            {
              // 系列名称，用于tooltip的显示，legend 的图例筛选，在 setOption 更新数据和配置项时用于指定对应的系列
              name: '复用失败次数',
              // 类型为柱状/条形图
              type: 'bar',
              stack: '总量',
              // 柱条的宽度，不设时自适应。支持设置成相对于类目宽度的百分比。
              barWidth: '60%',
              // 图形上的文本标签，可用于说明图形的一些数据信息
              label: {
                normal: {
                  // 是否显示标签
                  show: true,
                  // 通过相对的百分比或者绝对像素值表示标签相对于图形包围盒左上角的位置
                  position: 'insideRight'
                }
              },
              // 系列中的数据内容数组
              data: seriesFailData
            }
          ]
        })
        // 解决自适应
        let _mayChart = myChart
        setTimeout(function() {
          window.addEventListener('resize', () => {
            _mayChart.resize()
          })
        }, 500)
      }
    },
    // 折线统计图
    getLine(xData, seriesData) {
      let myEchartLine = document.getElementById('myEchartLine')
      // 自适应宽高
      let myChartContainer = function() {
        myEchartLine.style.width = window.innerWidth - 400 + 'px'
        myEchartLine.style.height = window.innerHeight - 400 + 'px'
      }
      myChartContainer()
      let myChart = echarts.init(myEchartLine)
      myChart.clear()
      myChart.setOption({
        title: {
          text: '折线统计图'
          //  text: that.$t("profitChart.Revenuechart")
        },
        legend: {
          data: ['复用次数']
        },
        color: ['#6284d3'],
        tooltip: {
          trigger: 'axis',
          formatter: '统计周期 : {b}<br/>复用次数 : {c}',
          axisPointer: {
            type: 'line'
          }
        },
        grid: {
          left: '5%',
          right: '5%',
          bottom: '10%',
          containLabel: true
        },
        xAxis: [
          {
            type: 'category',
            name: '统计周期',
            //                            data: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun", "Thu", "Fri", "Sat", "Sun"],
            data: xData,
            boundaryGap: false,
            axisTick: {
              alignWithLabel: true
            },
            nameGap: 2
          }
        ],
        yAxis: [
          {
            type: 'value',
            name: '复用次数'
          }
        ],
        series: [
          {
            name: '复用次数',
            // 类型为折线图
            type: 'line',
            // 折线样式
            lineStyle: {
              normal: {
                // 宽度
                width: 3,
                // 阴影颜色
                shadowColor: 'rgba(0,0,0,0.1)',
                // 阴影的模糊范围
                shadowBlur: 10,
                // 阴影的纵向位移量
                shadowOffsetY: 10
              }
            },
            areaStyle: {
              normal: {
                // 折线范围内的背景色
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  {
                    offset: 0,
                    color: '#E7F1F5'
                  },
                  {
                    offset: 1,
                    color: '#E7F1F5'
                  }
                ])
              }
            },
            //                            data: [1, 3, 5, 7, 9, 11, 13, 11, 9, 7, 5]
            data: seriesData
          }
        ]
      })
      let _mayChart = myChart
      setTimeout(function() {
        window.addEventListener('resize', () => {
          _mayChart.resize()
        })
      }, 500)
    }
  }
}
</script>

<style lang="scss">
.scroll-view {
  max-height: 650px;
}
</style>
