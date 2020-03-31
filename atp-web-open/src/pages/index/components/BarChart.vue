<template>
  <div :class="className" :style="{height:height,width:width}" />
</template>

<script>
import echarts from 'echarts'
require('echarts/theme/macarons') // echarts theme
import { debounce } from '@/libs/common'
import { testcaseSummary } from '@/api/home'
const animationDuration = 6000
export default {
  props: {
    className: {
      type: String,
      default: 'chart'
    },
    width: {
      type: String,
      default: '100%'
    },
    height: {
      type: String,
      default: '300px'
    }
  },
  data() {
    return {
      chart: null,
      projects: [],
      tags: [],
      series: [],
      legend: []
    }
  },
  mounted() {
    this.queryData()
    this.__resizeHandler = debounce(() => {
      if (this.chart) {
        this.chart.resize()
      }
    }, 100)
    window.addEventListener('resize', this.__resizeHandler)
  },
  beforeDestroy() {
    if (!this.chart) {
      return
    }
    window.removeEventListener('resize', this.__resizeHandler)
    this.chart.dispose()
    this.chart = null
  },
  methods: {
    queryData() {
      testcaseSummary({}).then(resp => {
        this.projects = resp.values.projects
        this.tags = resp.values.tags
        this.initChart()
      })
    },
    initChart() {
      this.chart = echarts.init(this.$el, 'macarons')
      this.tags.forEach(item => {
        this.legend.push(item.showName)
        this.series.push({
          name: item.showName,
          type: 'bar',
          stack: 'vistors',
          barWidth: '60%',
          data: item.dataList,
          itemStyle: {
            normal: {
              label: {
                show: true, // 开启显示
                position: 'inside', // 在内部显示
                textStyle: {
                  // 数值样式
                  color: 'black',
                  fontSize: 12
                }
              }
            }
          },
          animationDuration
        })
      })
      this.chart.setOption({
        title: {
          show: true,
          text: '按项目统计自动化用例数',
          textStyle: {
            fontWeight: 'normal',
            color: 'black',
            fontSize: 14
          },
          left: 'left'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            // 坐标轴指示器，坐标轴触发有效
            type: 'shadow' // 默认为直线，可选为：'line' | 'shadow'
          }
        },
        legend: {
          data: this.legend
        },
        grid: {
          top: 10,
          left: '2%',
          right: '2%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: [
          {
            type: 'category',
            data: this.projects,
            axisTick: {
              alignWithLabel: true
            },
            axisLabel: {
              interval: 0,
              rotate: 40
            }
          }
        ],
        yAxis: [
          {
            type: 'value',
            axisTick: {
              show: false
            }
          }
        ],
        series: this.series
      })
    }
  }
}
</script>
