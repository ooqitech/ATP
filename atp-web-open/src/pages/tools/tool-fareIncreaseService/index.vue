<template>
  <d2-container>
    <el-tabs type="border-card">
      <el-tab-pane label="现金贷加价策略配置">
        <cash-loan-config :mapping-list="mappingList"></cash-loan-config>
      </el-tab-pane>
      <el-tab-pane label="大额首单现金贷加价策略配置">
        <big-first-order-config :mapping-list="mappingList"></big-first-order-config>
      </el-tab-pane>
      <el-tab-pane label="不等贷加价策略配置">
        <no-wait-loan-config :mapping-list="mappingList"></no-wait-loan-config>
      </el-tab-pane>
      <el-tab-pane label="医美加价策略配置">
        <medical-config :mapping-list="mappingList"></medical-config>
      </el-tab-pane>
      <el-tab-pane label="加价服务代扣信息配置">
        <withhold-info-config :mapping-list="mappingList"></withhold-info-config>
      </el-tab-pane>
    </el-tabs>
  </d2-container>
</template>
<script>
import { getFareIncreaseServiceMappingList } from '@/api/tools/tool-fareIncreaseService'

export default {
  name: 'tool-fareIncreaseService',
  components: {
    'cash-loan-config': () => import('./cash-loan-config'),
    'big-first-order-config': () => import('./big-first-order-config'),
    'no-wait-loan-config': () => import('./no-wait-loan-config'),
    'medical-config': () => import('./medical-config'),
    'withhold-info-config': () => import('./withhold-info-config')
  },
  data() {
    return {
      mappingList: null
    }
  },
  mounted() {
    this.refreshData()
  },
  methods: {
    refreshData() {
      // 从后台获取配置项映射表
      getFareIncreaseServiceMappingList().then(res => {
        this.mappingList = res.data
      })
    }
  }
}
</script>
<style lang="scss"></style>
