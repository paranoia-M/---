<template>
  <div class="page-container">
    <div class="chart-header">
      <h2>📊 庆阳数字经济人才培养数据驾驶舱</h2>
      <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="2023" end-placeholder="2024" size="small" />
    </div>

    <el-row :gutter="20" class="row-box">
      <!-- 图表1：技能需求 -->
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header><span>💡 企业技能需求热度 (Top 5)</span></template>
          <div id="chart1" class="chart-dom"></div>
        </el-card>
      </el-col>
      <!-- 图表2：薪资趋势 -->
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header><span>📈 历年毕业生平均薪资趋势</span></template>
          <div id="chart2" class="chart-dom"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="row-box mt-20">
      <!-- 图表3：就业去向 -->
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header><span>🍰 2024届毕业生就业去向分布</span></template>
          <div id="chart3" class="chart-dom"></div>
        </el-card>
      </el-col>
      <!-- 图表4：专业匹配度 -->
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header><span>🎯 专业与岗位匹配度分析</span></template>
          <div id="chart4" class="chart-dom"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

const dateRange = ref([])

onMounted(() => {
  // 1. 技能热度 (柱状图)
  const c1 = echarts.init(document.getElementById('chart1'))
  c1.setOption({
    tooltip: {},
    grid: { bottom: 30, top: 20, right: 20 },
    xAxis: { type: 'category', data: ['Python', 'Java', 'Linux', 'SQL', 'AI标注'] },
    yAxis: { type: 'value' },
    series: [{ 
      data: [120, 200, 150, 80, 180], 
      type: 'bar', 
      itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{offset: 0, color: '#83bff6'}, {offset: 1, color: '#188df0'}]) } 
    }]
  })

  // 2. 薪资趋势 (折线图)
  const c2 = echarts.init(document.getElementById('chart2'))
  c2.setOption({
    tooltip: { trigger: 'axis' },
    grid: { bottom: 30, top: 20, right: 20 },
    xAxis: { type: 'category', data: ['2020', '2021', '2022', '2023', '2024'] },
    yAxis: { type: 'value', name: '元/月' },
    series: [{ 
      data: [3500, 3800, 4200, 4800, 5200], 
      type: 'line', 
      smooth: true, 
      areaStyle: { color: 'rgba(64, 158, 255, 0.2)' },
      itemStyle: { color: '#409EFF' }
    }]
  })

  // 3. 就业分布 (饼图)
  const c3 = echarts.init(document.getElementById('chart3'))
  c3.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: [
        { value: 850, name: '企业就业' },
        { value: 120, name: '升学' },
        { value: 50, name: '自主创业' },
        { value: 80, name: '待就业' }
      ],
      emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.5)' } }
    }]
  })

  // 4. 专业匹配度 (雷达图)
  const c4 = echarts.init(document.getElementById('chart4'))
  c4.setOption({
    radar: {
      indicator: [
        { name: '大数据', max: 100 },
        { name: '云计算', max: 100 },
        { name: '软件工程', max: 100 },
        { name: '网络安全', max: 100 },
        { name: '人工智能', max: 100 }
      ]
    },
    series: [{
      type: 'radar',
      data: [
        { value: [90, 85, 95, 70, 60], name: '岗位匹配度', areaStyle: { color: 'rgba(103, 194, 58, 0.4)' }, itemStyle: { color: '#67C23A' } }
      ]
    }]
  })

  // 自动缩放
  window.addEventListener('resize', () => {
    c1.resize(); c2.resize(); c3.resize(); c4.resize();
  })
})
</script>

<style scoped>
.page-container { padding: 20px; background-color: #f0f2f5; height: 100%; box-sizing: border-box; display: flex; flex-direction: column; }
.chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.chart-header h2 { margin: 0; font-size: 20px; color: #303133; }
.row-box { flex: 1; }
.mt-20 { margin-top: 20px; }
.chart-card { height: 100%; display: flex; flex-direction: column; }
.chart-dom { width: 100%; height: 250px; }
</style>