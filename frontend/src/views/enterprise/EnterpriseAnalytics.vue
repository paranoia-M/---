<template>
  <div class="page-container">
    <!-- 1. 顶部控制栏 -->
    <div class="dashboard-header">
      <div class="left">
        <h2 class="title">📊 数字经济人才招聘效能驾驶舱</h2>
        <span class="subtitle">数据更新时间：{{ currentDate }}</span>
      </div>
      <div class="right">
        <el-radio-group v-model="timeRange" size="small" @change="refreshData">
          <el-radio-button label="本周" />
          <el-radio-button label="本月" />
          <el-radio-button label="本季度" />
        </el-radio-group>
        <el-button type="primary" icon="Download" style="margin-left: 15px" @click="exportReport">导出分析报告</el-button>
      </div>
    </div>

    <!-- 2. 核心指标 KPI -->
    <el-row :gutter="20" class="mb-20">
      <el-col :span="6" v-for="(item, index) in kpiData" :key="index">
        <el-card shadow="hover" class="kpi-card">
          <div class="kpi-icon" :class="item.colorClass">
            <el-icon><component :is="item.icon" /></el-icon>
          </div>
          <div class="kpi-content">
            <div class="label">{{ item.label }}</div>
            <div class="value">{{ item.value }}</div>
            <div class="trend">
              同比 {{ item.rate }}% 
              <el-icon :color="item.trend === 'up' ? '#F56C6C' : '#67C23A'">
                <component :is="item.trend === 'up' ? 'Top' : 'Bottom'" />
              </el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 3. 核心图表区 -->
    <el-row :gutter="20" class="chart-row">
      <!-- 左侧：招聘漏斗 + 趋势图 -->
      <el-col :span="16">
        <el-card shadow="never" class="chart-card mb-20">
          <template #header>
            <div class="card-header">
              <span>📉 招聘转化漏斗分析</span>
              <el-tag type="info" size="small">全流程转化率 15%</el-tag>
            </div>
          </template>
          <div id="funnelChart" class="chart-box"></div>
        </el-card>

        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>📈 简历投递量趋势 (近6个月)</span>
            </div>
          </template>
          <div id="lineChart" class="chart-box"></div>
        </el-card>
      </el-col>

      <!-- 右侧：画像 + 分布 -->
      <el-col :span="8">
        <el-card shadow="never" class="chart-card mb-20">
          <template #header>
            <span>🎯 人岗匹配度 (需求vs能力)</span>
          </template>
          <div id="radarChart" class="chart-box"></div>
          <div class="chart-footer">
            <small>注：蓝色为学生能力，绿色为岗位标准</small>
          </div>
        </el-card>

        <el-card shadow="never" class="chart-card">
          <template #header>
            <span>🍰 生源专业分布</span>
          </template>
          <div id="pieChart" class="chart-box"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, nextTick } from 'vue'
import * as echarts from 'echarts'
import { User, DataLine, Timer, Trophy, Top, Bottom, Download } from '@element-plus/icons-vue'
import { ElMessage, ElLoading } from 'element-plus'

const currentDate = new Date().toLocaleDateString()
const timeRange = ref('本月')

// KPI 数据
const kpiData = reactive([
  { label: '累计简历投递', value: '1,285', rate: 12.5, trend: 'up', icon: 'User', colorClass: 'icon-blue' },
  { label: '面试通过率', value: '32.4%', rate: 2.1, trend: 'down', icon: 'DataLine', colorClass: 'icon-purple' },
  { label: '平均招聘周期', value: '15天', rate: 5.0, trend: 'down', icon: 'Timer', colorClass: 'icon-orange' }, // 周期缩短是好事
  { label: '成功入职人数', value: '45人', rate: 8.8, trend: 'up', icon: 'Trophy', colorClass: 'icon-green' },
])

// 图表实例
let charts = []

const initCharts = () => {
  // 1. 漏斗图 (更美观的配置)
  const funnelChart = echarts.init(document.getElementById('funnelChart'))
  funnelChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b} : {c} ({d}%)' },
    color: ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399'],
    series: [{
      name: '招聘流程',
      type: 'funnel',
      left: '10%', top: 10, bottom: 10, width: '70%',
      min: 0, max: 100,
      minSize: '0%', maxSize: '100%',
      sort: 'descending',
      gap: 2,
      label: { show: true, position: 'right' },
      data: [
        { value: 100, name: '简历投递 (1285)' },
        { value: 60, name: '简历初筛 (771)' },
        { value: 40, name: '安排面试 (514)' },
        { value: 20, name: '发送Offer (257)' },
        { value: 15, name: '成功入职 (192)' }
      ]
    }]
  })

  // 2. 雷达图 (对比分析)
  const radarChart = echarts.init(document.getElementById('radarChart'))
  radarChart.setOption({
    tooltip: {},
    legend: { data: ['学生平均能力', '岗位标准要求'], bottom: 0 },
    radar: {
      indicator: [
        { name: 'Python编程', max: 100 },
        { name: '数据清洗', max: 100 },
        { name: '团队协作', max: 100 },
        { name: '文档编写', max: 100 },
        { name: '抗压能力', max: 100 }
      ],
      radius: '65%'
    },
    series: [{
      type: 'radar',
      data: [
        {
          value: [85, 90, 70, 60, 75],
          name: '学生平均能力',
          areaStyle: { color: 'rgba(64, 158, 255, 0.3)' },
          itemStyle: { color: '#409EFF' }
        },
        {
          value: [95, 95, 85, 85, 80],
          name: '岗位标准要求',
          itemStyle: { color: '#67C23A' }
        }
      ]
    }]
  })

  // 3. 折线图 (趋势)
  const lineChart = echarts.init(document.getElementById('lineChart'))
  lineChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: ['1月', '2月', '3月', '4月', '5月', '6月'] },
    yAxis: { type: 'value' },
    series: [{
      name: '投递量',
      type: 'line',
      smooth: true,
      areaStyle: { 
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{offset: 0, color: '#8ec5fc'}, {offset: 1, color: '#e0c3fc'}]) 
      },
      data: [120, 132, 101, 134, 290, 230]
    }]
  })

  // 4. 饼图 (南丁格尔玫瑰图)
  const pieChart = echarts.init(document.getElementById('pieChart'))
  pieChart.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      name: '专业来源',
      type: 'pie',
      radius: [20, 80],
      center: ['50%', '50%'],
      roseType: 'area',
      itemStyle: { borderRadius: 5 },
      data: [
        { value: 40, name: '大数据技术' },
        { value: 32, name: '云计算应用' },
        { value: 28, name: '人工智能' },
        { value: 22, name: '软件工程' },
        { value: 18, name: '网络安全' }
      ]
    }]
  })

  charts = [funnelChart, radarChart, lineChart, pieChart]
}

// --- 交互逻辑 ---

const refreshData = () => {
  const loading = ElLoading.service({
    lock: true,
    text: '正在重新计算数据模型...',
    background: 'rgba(255, 255, 255, 0.7)',
  })
  setTimeout(() => {
    loading.close()
    ElMessage.success(`已切换至【${timeRange.value}】数据视图`)
    // 这里可以添加重新随机生成数据的逻辑，让图表动起来
  }, 800)
}

const exportReport = () => {
  ElMessage.success('《2024年度人才招聘效能分析报告.pdf》下载中...')
}

// 响应式缩放
const handleResize = () => charts.forEach(c => c.resize())

onMounted(() => {
  nextTick(() => {
    initCharts()
    window.addEventListener('resize', handleResize)
  })
})
</script>

<style scoped>
.page-container { padding: 20px; background-color: #f5f7fa; min-height: 100%; }
.mb-20 { margin-bottom: 20px; }

/* 头部 */
.dashboard-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.title { margin: 0; font-size: 22px; color: #303133; }
.subtitle { font-size: 12px; color: #909399; margin-left: 10px; }

/* KPI 卡片 */
.kpi-card { border: none; transition: transform 0.3s; }
.kpi-card:hover { transform: translateY(-5px); }
.kpi-card :deep(.el-card__body) { display: flex; align-items: center; padding: 20px; }
.kpi-icon { width: 60px; height: 60px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-right: 20px; font-size: 28px; }
.icon-blue { background: #ecf5ff; color: #409EFF; }
.icon-purple { background: #f4f4f5; color: #909399; }
.icon-orange { background: #fdf6ec; color: #E6A23C; }
.icon-green { background: #f0f9eb; color: #67C23A; }

.kpi-content .label { font-size: 14px; color: #909399; }
.kpi-content .value { font-size: 26px; font-weight: bold; color: #303133; margin: 5px 0; }
.kpi-content .trend { font-size: 12px; color: #606266; display: flex; align-items: center; gap: 4px; }

/* 图表区 */
.chart-card { border-radius: 8px; }
.chart-box { height: 300px; width: 100%; }
.chart-header { display: flex; justify-content: space-between; align-items: center; }
.chart-footer { text-align: center; color: #999; font-size: 12px; margin-top: 10px; }
</style>