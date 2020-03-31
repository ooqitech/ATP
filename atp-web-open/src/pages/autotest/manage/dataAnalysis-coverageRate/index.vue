<template>
  <d2-container>
    <div class="table_container">
      <div class="handle-box">
        <el-tabs type="border-card">
          <el-tab-pane label="回归测试覆盖率">
            <el-form ref="regressTestBaseForm" :model="regressTestBaseForm" label-width="80px" inline>
              <el-form-item label="公司" prop="companyId" :rules="[{required:true,message:'请选择公司',trigger:'change'}]">
                <el-select v-model="companyId" filterable placeholder="请选择公司">
                  <el-option v-for="item in companyList" :key="item.id" :label="item.name" :value="item.id"></el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="项目" prop="projectId" :rules="[{required:true,message:'请选择项目',trigger:'change'}]">
                <el-select v-model="projectId" filterable placeholder="请选择项目">
                  <el-option v-for="item in projectList" :key="item.id" :label="item.name" :value="item.id"></el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="测试任务" prop="taskId">
                <el-select v-model="regressTestBaseForm.taskId" filterable placeholder="请选择测试任务">
                  <el-option v-for="item in regressTestBaseForm.taskList" :key="item.id" :label="item.name" :value="item.id"></el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="统计周期" prop="statPeriod">
                <el-select v-model="regressTestBaseForm.statPeriod" filterable placeholder="请选择测试任务">
                  <el-option v-for="item in regressTestBaseForm.statPeriodList" :key="item" :label="item" :value="item"></el-option>
                </el-select>
              </el-form-item>
              <el-button type="primary" icon="search" @click="getData">搜 索</el-button>
              <el-button type="primary" icon="search" @click="viewDetail">显示详细数据</el-button>
            </el-form>
            <el-row :gutter="20">
              <el-col :span="10">
                <!--柱形统计图和折线统计图测试-->
                <div class="echarts">
                  <div class="chart" style="height:600px;width:600px;" ref="myEchartPillar"></div>
                </div>
              </el-col>
              <el-col :span="14">
                <div>
                  <span style="font-size: 18px;font-weight: bold">详细数据</span>
                </div>
                <el-table :data="regressTestBaseForm.detailData" style="width: 100%" max-height="250">
                  <el-table-column prop="taskId" label="测试任务ID"></el-table-column>
                  <el-table-column prop="taskName" label="测试任务名称"></el-table-column>
                  <el-table-column prop="coverageRate" label="接口覆盖率"></el-table-column>
                  <el-table-column prop="runStartTime" label="运行时间"></el-table-column>
                </el-table>
              </el-col>
            </el-row>
          </el-tab-pane>
          <el-tab-pane label="当前整体覆盖率">
            <el-form ref="totalBaseForm" :model="totalBaseForm" label-width="80px" inline>
              <el-form-item label="公司" prop="companyId" :rules="[{required:true,message:'请选择公司',trigger:'change'}]">
                <el-select v-model="companyId" filterable placeholder="请选择公司">
                  <el-option v-for="item in companyList" :key="item.id" :label="item.name" :value="item.id"></el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="系统" prop="systemId">
                <el-select v-model="systemId" filterable placeholder="请选择系统">
                  <el-option v-for="item in systemList" :key="item.id" :label="item.name" :value="item.id"></el-option>
                </el-select>
              </el-form-item>
              <el-button type="primary" icon="search" @click="getData">搜 索</el-button>
              <el-button type="primary" icon="search" @click="viewDetail">显示详细数据</el-button>
            </el-form>
            <el-row :gutter="20">
              <el-col :span="10">
                <!--柱形统计图和折线统计图测试-->
                <div class="echarts">
                  <div class="chart" style="height:600px;width:600px;" ref="myEchartLine"></div>
                </div>
              </el-col>
              <el-col :span="14">
                <div>
                  <span style="font-size: 18px;font-weight: bold">详细数据</span>
                </div>
                <el-table :data="totalBaseForm.detailData" style="width: 100%" max-height="250">
                  <el-table-column prop="systemId" label="系统ID"></el-table-column>
                  <el-table-column prop="systemName" label="系统名称"></el-table-column>
                  <el-table-column prop="intfId" label="接口ID"></el-table-column>
                  <el-table-column prop="intfName" label="接口名称"></el-table-column>
                  <el-table-column prop="coverageRate" label="自动化覆盖率"></el-table-column>
                </el-table>
              </el-col>
            </el-row>
          </el-tab-pane>
          <el-tab-pane label="覆盖率变化趋势">
            <el-form ref="trendForm" :model="trendForm" label-width="80px" inline>
              <el-form-item label="公司" prop="companyId" :rules="[{required:true,message:'请选择公司',trigger:'change'}]">
                <el-select v-model="companyId" filterable placeholder="请选择公司">
                  <el-option v-for="item in companyList" :key="item.id" :label="item.name" :value="item.id"></el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="系统" prop="systemId">
                <el-select v-model="systemId" filterable placeholder="请选择系统">
                  <el-option v-for="item in systemList" :key="item.id" :label="item.name" :value="item.id"></el-option>
                </el-select>
              </el-form-item>
              <el-button type="primary" icon="search" @click="getData">搜 索</el-button>
              <el-button type="primary" icon="search" @click="viewDetail">显示详细数据</el-button>
            </el-form>
            <el-row :gutter="20">
              <el-col :span="10">
                <!--柱形统计图和折线统计图测试-->
                <div class="echarts">
                  <div class="chart" style="height:600px;width:600px;" ref="myEchartLine"></div>
                </div>
              </el-col>
              <el-col :span="14">
                <div>
                  <span style="font-size: 18px;font-weight: bold">详细数据</span>
                </div>
                <el-table :data="trendForm.detailData" style="width: 100%" max-height="250">
                  <el-table-column prop="systemId" label="系统ID"></el-table-column>
                  <el-table-column prop="systemName" label="系统名称"></el-table-column>
                  <el-table-column prop="intfId" label="接口ID"></el-table-column>
                  <el-table-column prop="intfName" label="接口名称"></el-table-column>
                  <el-table-column prop="coverageRate" label="自动化覆盖率"></el-table-column>
                  <el-table-column prop="statDate" label="统计日期"></el-table-column>
                </el-table>
              </el-col>
            </el-row>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </d2-container>
</template>

<script>
import echarts from 'echarts'

export default {
  name: 'reuseRate',
  data() {
    return {
      companyId: 1,
      companyList: [
        {
          id: 1,
          name: '米么'
        }
      ],
      systemId: '',
      systemList: [],
      projectId: '',
      projectList: [],
      regressTestBaseForm: {
        taskId: '',
        taskList: [],
        statPeriod: '最近一月',
        statPeriodList: ['最近一周', '最近一月', '最近三月'],
        detailData: []
      },
      totalBaseForm: {
        detailData: []
      },
      trendForm: {
        detailData: []
      }
    }
  },
  mounted() {
    this.getPillar()
    this.getLine()
  },
  methods: {
    // 查询图表数据
    getData() {},
    // 查看详细数据
    viewDetail() {},
    // 柱形统计图
    getPillar() {
      {
        // 基于准备好的dom(myEchartPillar)，初始化echarts实例
        let myChart = echarts.init(this.$refs.myEchartPillar)
        // 指定图表的配置项和数据，绘制图表
        myChart.setOption({
          // 图表名称
          title: {
            text: '柱形统计图'
          },
          // 图表颜色
          color: ['#6284d3'],
          // 提示
          tooltip: {
            // 触发类型,axis:坐标轴触发，主要在柱状图，折线图等会使用类目轴的图表中使用。
            trigger: 'axis',
            axisPointer: {
              // 坐标轴指示器，坐标轴触发有效，默认为直线，可选为：'line' | 'shadow'
              type: 'shadow'
            }
          },
          grid: {
            show: true,
            // grid 组件离容器左侧的距离。
            left: '5%',
            // grid 组件离容器右侧的距离。
            right: '10%',
            // grid 组件离容器下侧的距离。
            bottom: '3%',
            // grid 区域是否包含坐标轴的刻度标签。true这常用于『防止标签溢出』的场景，标签溢出指的是，标签长度动态变化时，可能会溢出容器或者覆盖其他组件。
            containLabel: true,
            // 网格背景色，此配置项生效的前提是，设置了 show: true
            backgroundColor: '#E7F1F5'
          },
          // 直角坐标系 grid 中的 x 轴
          xAxis: [
            {
              // 'category' 类目轴
              type: 'category',
              // 坐标轴名称
              name: '测试任务',
              // 坐标轴名称显示位置
              nameLocation: 'end',
              // 坐标数据
              data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
              // 坐标轴刻度相关设置
              axisTick: {
                // 为 true 可以保证刻度线和标签对齐
                alignWithLabel: true
              },
              // 坐标轴名称与轴线之间的距离
              nameGap: 2
            }
          ],
          // 直角坐标系 grid 中的 y 轴
          yAxis: [
            {
              // 'value' 数值轴，适用于连续数据
              type: 'value',
              // 坐标轴名称
              name: '覆盖率（%）',
              // 坐标轴的标签是否响应和触发鼠标事件，默认不响应
              triggerEvent: true
            }
          ],
          // 系列列表。每个系列通过 type 决定自己的图表类型
          series: [
            {
              // 系列名称，用于tooltip的显示，legend 的图例筛选，在 setOption 更新数据和配置项时用于指定对应的系列
              name: '柜子使用量',
              // 类型为柱状/条形图
              type: 'bar',
              // 柱条的宽度，不设时自适应。支持设置成相对于类目宽度的百分比。
              barWidth: '60%',
              // 图形上的文本标签，可用于说明图形的一些数据信息
              label: {
                normal: {
                  // 是否显示标签
                  show: true,
                  // 通过相对的百分比或者绝对像素值表示标签相对于图形包围盒左上角的位置
                  position: 'top'
                }
              },
              // 系列中的数据内容数组
              data: [1, 3, 5, 7, 9, 11, 13]
            }
          ]
        })
        // 解决自适应
        setTimeout(function() {
          window.addEventListener('resize', () => {
            myChart.resize()
          })
        }, 500)
      }
    },
    // 折线统计图
    getLine() {
      let myChart = echarts.init(this.$refs.myEchartLine)
      myChart.setOption({
        title: {
          text: '折线统计图'
          //  text: that.$t("profitChart.Revenuechart")
        },
        color: ['#6284d3'],
        tooltip: {
          trigger: 'axis',
          formatter: '时间 : {b}<br/>收益 : {c}元',
          axisPointer: {
            type: 'line'
          }
        },
        grid: {
          left: '5%',
          right: '10%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: [
          {
            type: 'category',
            name: '系统/接口',
            data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun', 'Thu', 'Fri', 'Sat', 'Sun'],
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
            name: '覆盖率（%）'
          }
        ],
        series: [
          {
            name: '柜子使用量',
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
            data: [1, 3, 5, 7, 9, 11, 13, 11, 9, 7, 5]
          }
        ]
      })
      setTimeout(function() {
        window.addEventListener('resize', () => {
          myChart.resize()
        })
      }, 500)
    }
  }
}
</script>

<style lang="scss">
.table_container {
  padding: 10px;
}

.handle-box {
  margin-bottom: 20px;
}

/*.el-table .success-row {*/
/*background: #b3e19d;*/
/*}*/
.el-table .warning-row {
  background: oldlace;
}
</style>
