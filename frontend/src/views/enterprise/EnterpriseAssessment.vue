<template>
  <div class="page-container">
    <el-row :gutter="20">
      <!-- 左侧：评分任务列表 -->
      <el-col :span="16">
        <el-card shadow="never" class="task-card">
          <template #header>
            <div class="flex-between">
              <div class="title">
                <el-icon><Edit /></el-icon> 技能考核评价中心
              </div>
              <el-radio-group v-model="activeTab" size="small">
                <el-radio-button label="pending">待评分任务</el-radio-button>
                <el-radio-button label="completed">历史评价记录</el-radio-button>
              </el-radio-group>
            </div>
          </template>

          <!-- 待评分列表 -->
          <div v-if="activeTab === 'pending'">
            <el-table :data="taskList" border stripe size="large">
              <el-table-column prop="student" label="实习生" width="120">
                <template #default="scope">
                  <div class="user-cell">
                    <el-avatar :size="30" style="background:#409EFF">{{ scope.row.student[0] }}</el-avatar>
                    <b>{{ scope.row.student }}</b>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="post" label="岗位" width="120" />
              <el-table-column prop="cycle" label="考核周期" />
              <el-table-column prop="deadline" label="截止日期" width="120">
                <template #default="scope">
                  <span style="color: #F56C6C">{{ scope.row.deadline }}</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120" align="center">
                <template #default="scope">
                  <el-button type="primary" size="small" @click="openRateDialog(scope.row)">立即评分</el-button>
                </template>
              </el-table-column>
            </el-table>
            <div class="empty-tip" v-if="taskList.length === 0">
              <el-empty description="暂无待评分任务，您太棒了！" />
            </div>
          </div>

          <!-- 历史记录列表 -->
          <div v-else>
            <el-table :data="historyList" border stripe>
              <el-table-column prop="student" label="实习生" width="100" />
              <el-table-column prop="cycle" label="周期" width="150" />
              <el-table-column prop="totalScore" label="总分" width="80">
                <template #default="scope">
                  <span style="font-weight: bold; color: #67C23A">{{ scope.row.totalScore }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="comment" label="导师评语" show-overflow-tooltip />
              <el-table-column label="评级" width="100">
                <template #default="scope">
                  <el-tag v-if="scope.row.totalScore >= 90" type="success">优秀</el-tag>
                  <el-tag v-else type="primary">良好</el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：评分指南 & 进度 -->
      <el-col :span="8">
        <el-card shadow="hover" class="guide-card">
          <h3>📅 本月评分进度</h3>
          <div class="progress-circle">
            <el-progress type="dashboard" :percentage="completionRate" :color="colors">
              <template #default="{ percentage }">
                <span class="percentage-value">{{ percentage }}%</span>
                <span class="percentage-label">完成率</span>
              </template>
            </el-progress>
          </div>
          <el-divider />
          <div class="guide-text">
            <h4>评分标准指南：</h4>
            <p>1. <strong>职业素养 (30%)</strong>：出勤率、团队协作、沟通能力。</p>
            <p>2. <strong>专业技能 (40%)</strong>：任务完成质量、技术难点突破。</p>
            <p>3. <strong>创新实践 (30%)</strong>：提出优化建议、解决新问题。</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 评分弹窗 (核心交互) -->
    <el-dialog v-model="dialogVisible" title="企业导师综合评价" width="600px" destroy-on-close>
      <div class="dialog-header">
        <span>正在评价：<b>{{ currentTask?.student }}</b> ({{ currentTask?.post }})</span>
        <span class="cycle-tag">{{ currentTask?.cycle }}</span>
      </div>

      <el-row :gutter="20">
        <!-- 左侧表单 -->
        <el-col :span="14">
          <el-form label-position="top" size="small">
            <el-form-item label="职业素养 (态度/考勤)">
              <el-rate v-model="form.attitude" show-text :texts="['差', '一般', '合格', '良好', '优秀']" />
            </el-form-item>
            <el-form-item label="专业技能 (代码/交付)">
              <el-slider v-model="form.skill" :step="5" show-input />
            </el-form-item>
            <el-form-item label="团队协作">
              <el-slider v-model="form.team" :step="5" show-input />
            </el-form-item>
            <el-form-item label="创新能力">
              <el-slider v-model="form.innovation" :step="5" show-input />
            </el-form-item>
          </el-form>
        </el-col>
        
        <!-- 右侧雷达图预览 -->
        <el-col :span="10">
          <div id="miniRadar" style="width: 100%; height: 250px;"></div>
        </el-col>
      </el-row>

      <el-form-item label="导师寄语/改进建议">
        <el-input type="textarea" v-model="form.comment" :rows="3" placeholder="请输入具体的指导意见..." />
      </el-form-item>

      <template #footer>
        <div class="dialog-footer">
          <div class="total-score">预估总分：<span>{{ calculateTotal }}</span></div>
          <div>
            <el-button @click="dialogVisible = false">取消</el-button>
            <el-button type="primary" @click="submitRating">提交评价</el-button>
          </div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { Edit } from '@element-plus/icons-vue'
import { ElMessage, ElNotification } from 'element-plus'
import * as echarts from 'echarts'

// --- 数据 ---
const activeTab = ref('pending')
const dialogVisible = ref(false)
const currentTask = ref(null)
let radarChart = null

const taskList = ref([
  { id: 1, student: '张伟', post: 'Python开发', cycle: '2024年6月第2周', deadline: '2024-06-20' },
  { id: 2, student: '李娜', post: '运维助理', cycle: '2024年6月第2周', deadline: '2024-06-20' },
  { id: 3, student: '王强', post: '数据标注', cycle: '2024年6月第2周', deadline: '2024-06-20' },
])

const historyList = ref([
  { student: '赵云', cycle: '2024年6月第1周', totalScore: 92, comment: '表现优异，提前完成任务' }
])

const form = reactive({ attitude: 4, skill: 80, team: 80, innovation: 70, comment: '' })

const colors = [
  { color: '#f56c6c', percentage: 20 },
  { color: '#e6a23c', percentage: 40 },
  { color: '#5cb87a', percentage: 60 },
  { color: '#1989fa', percentage: 80 },
  { color: '#6f7ad3', percentage: 100 },
]

// --- 计算属性 ---
const completionRate = computed(() => {
  const total = taskList.value.length + historyList.value.length
  return Math.round((historyList.value.length / total) * 100) || 0
})

const calculateTotal = computed(() => {
  // 简单加权算法：态度(20) + 技能(30) + 团队(25) + 创新(25)
  const score = (form.attitude * 20) * 0.2 + form.skill * 0.3 + form.team * 0.25 + form.innovation * 0.25
  return Math.round(score)
})

// --- 方法 ---

const openRateDialog = (row) => {
  currentTask.value = row
  // 重置表单
  form.attitude = 4
  form.skill = 80
  form.team = 80
  form.innovation = 70
  form.comment = ''
  dialogVisible.value = true
  
  // 弹窗打开后渲染图表
  nextTick(() => initRadar())
}

const initRadar = () => {
  const dom = document.getElementById('miniRadar')
  if (!dom) return
  if (radarChart) radarChart.dispose()
  
  radarChart = echarts.init(dom)
  updateChart()
}

const updateChart = () => {
  if (!radarChart) return
  const option = {
    radar: {
      indicator: [
        { name: '态度', max: 5 },
        { name: '技能', max: 100 },
        { name: '协作', max: 100 },
        { name: '创新', max: 100 }
      ],
      radius: '60%'
    },
    series: [{
      type: 'radar',
      data: [
        {
          value: [form.attitude, form.skill, form.team, form.innovation],
          name: '能力模型',
          areaStyle: { color: 'rgba(64, 158, 255, 0.5)' }
        }
      ]
    }]
  }
  radarChart.setOption(option)
}

// 监听表单变化，实时更新图表
watch(form, () => {
  updateChart()
}, { deep: true })

const submitRating = () => {
  // 1. 移除待办
  const index = taskList.value.findIndex(i => i.id === currentTask.value.id)
  if (index > -1) taskList.value.splice(index, 1)
  
  // 2. 加入历史
  historyList.value.unshift({
    student: currentTask.value.student,
    cycle: currentTask.value.cycle,
    totalScore: calculateTotal.value,
    comment: form.comment || '表现良好'
  })
  
  // 3. 关闭弹窗
  dialogVisible.value = false
  
  ElNotification({
    title: '评分提交成功',
    message: `${currentTask.value.student} 的成绩已同步至学校端，本月绩效 +1`,
    type: 'success'
  })
}
</script>

<style scoped>
.page-container { padding: 20px; }
.task-card { min-height: 500px; }
.flex-between { display: flex; justify-content: space-between; align-items: center; }
.title { font-size: 16px; font-weight: bold; display: flex; align-items: center; gap: 8px; }
.user-cell { display: flex; align-items: center; gap: 8px; }

.guide-card { height: 100%; text-align: center; }
.progress-circle { margin: 20px 0; }
.percentage-value { display: block; margin-top: 10px; font-size: 28px; }
.percentage-label { display: block; margin-top: 10px; font-size: 12px; }
.guide-text { text-align: left; margin-top: 20px; color: #606266; font-size: 13px; line-height: 1.8; }
.guide-text h4 { color: #303133; margin-bottom: 10px; }

/* 弹窗样式 */
.dialog-header { background: #f5f7fa; padding: 10px 15px; border-radius: 4px; margin-bottom: 20px; display: flex; justify-content: space-between; }
.cycle-tag { background: #ecf5ff; color: #409EFF; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
.dialog-footer { display: flex; justify-content: space-between; align-items: center; width: 100%; }
.total-score { font-size: 16px; font-weight: bold; }
.total-score span { color: #F56C6C; font-size: 20px; }
</style>