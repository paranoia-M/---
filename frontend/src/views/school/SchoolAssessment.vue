<template>
  <div class="page-container">
    <el-card shadow="never" class="main-card">
      <template #header>
        <div class="toolbar">
          <div class="title">
            <el-icon><EditPen /></el-icon> 工学交替过程化考核
          </div>
          <el-button type="warning" plain icon="Bell">一键催办企业评分</el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab" type="card" class="custom-tabs">
        <!-- 待办列表 -->
        <el-tab-pane label="待学校复核 (3)" name="pending">
          <el-table :data="pendingList" border stripe size="large">
            <el-table-column type="index" width="50" />
            <el-table-column prop="student" label="实习学生" width="120">
              <template #default="scope">
                <b>{{ scope.row.student }}</b>
              </template>
            </el-table-column>
            <el-table-column prop="project" label="所属项目" min-width="180" />
            <el-table-column prop="week" label="考核周期" width="150" />
            <el-table-column label="企业导师评分" width="180">
              <template #default="scope">
                <div class="ent-score">
                  <span>{{ scope.row.entScore }}分</span>
                  <el-rate :model-value="scope.row.entScore / 20" disabled text-color="#ff9900" />
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="date" label="提交时间" width="120" />
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="scope">
                <el-button type="primary" size="small" @click="openGradeModal(scope.row)">开始复核</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 已办列表 -->
        <el-tab-pane label="已归档记录" name="history">
          <el-table :data="historyList" border stripe>
            <el-table-column prop="student" label="学生" width="120" />
            <el-table-column prop="project" label="项目" />
            <el-table-column prop="finalScore" label="最终得分" width="120">
              <template #default="scope">
                <span style="font-weight: bold; color: #67C23A">{{ scope.row.finalScore }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="comment" label="综合评语" show-overflow-tooltip />
            <el-table-column label="状态">
              <template #default><el-tag type="info">已归档</el-tag></template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 专业评分弹窗 -->
    <el-dialog v-model="gradeVisible" title="学校复核评分" width="500px" destroy-on-close>
      <div class="student-summary">
        <p>正在为 <b>{{ currentTask?.student }}</b> 的 <b>{{ currentTask?.week }}</b> 工作进行评分</p>
        <p class="sub-info">企业导师评分：{{ currentTask?.entScore }} (权重 60%)</p>
      </div>

      <el-form label-position="top" class="grade-form">
        <el-form-item label="职业技能掌握 (40分)">
          <el-slider v-model="scores.skill" :max="40" show-input />
        </el-form-item>
        <el-form-item label="团队协作与沟通 (30分)">
          <el-slider v-model="scores.team" :max="30" show-input />
        </el-form-item>
        <el-form-item label="出勤与纪律 (30分)">
          <el-slider v-model="scores.attendance" :max="30" show-input />
        </el-form-item>
        
        <el-divider />
        <div class="total-score">
          <span>学校总分：</span>
          <span class="score-num">{{ totalScore }}</span>
        </div>

        <el-form-item label="复核评语">
          <el-input v-model="comment" type="textarea" rows="3" placeholder="请输入针对学生的指导建议..." />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="gradeVisible = false">取消</el-button>
        <el-button type="primary" @click="submitGrade">提交最终成绩</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { EditPen, Bell } from '@element-plus/icons-vue'
import { ElMessage, ElNotification } from 'element-plus'

const activeTab = ref('pending')
const gradeVisible = ref(false)
const currentTask = ref(null)

// 待办数据
const pendingList = ref([
  { id: 1, student: '张伟', project: '政务云数据清洗一期', week: '第4周周报', date: '2023-11-18', entScore: 88 },
  { id: 2, student: '李娜', project: 'IDC机房巡检实训', week: '第4周周报', date: '2023-11-18', entScore: 92 },
  { id: 3, student: '王强', project: '抖音直播间数据标注', week: '第3周周报', date: '2023-11-19', entScore: 85 },
])

// 历史数据
const historyList = ref([
  { student: '赵云', project: 'Python开发实训', finalScore: 90, comment: '表现优秀，基础扎实' }
])

// 评分表单
const scores = reactive({ skill: 35, team: 25, attendance: 30 })
const comment = ref('')

// 自动计算总分
const totalScore = computed(() => scores.skill + scores.team + scores.attendance)

const openGradeModal = (row) => {
  currentTask.value = row
  // 重置表单
  scores.skill = 35
  scores.team = 25
  scores.attendance = 30
  comment.value = ''
  gradeVisible.value = true
}

const submitGrade = () => {
  // 1. 计算加权总分 (企业60% + 学校40%)
  // 这里简单演示，直接存入历史列表
  const final = Math.round(currentTask.value.entScore * 0.6 + totalScore.value * 0.4)
  
  // 2. 移出待办
  const taskIndex = pendingList.value.findIndex(i => i.id === currentTask.value.id)
  if (taskIndex > -1) pendingList.value.splice(taskIndex, 1)
  
  // 3. 加入历史
  historyList.value.unshift({
    student: currentTask.value.student,
    project: currentTask.value.project,
    finalScore: final,
    comment: comment.value || '无评语'
  })
  
  gradeVisible.value = false
  ElNotification({
    title: '评分完成',
    message: `${currentTask.value.student} 的最终成绩为 ${final} 分`,
    type: 'success'
  })
}
</script>

<style scoped>
.page-container { padding: 20px; height: 100%; box-sizing: border-box; }
.main-card { height: 100%; display: flex; flex-direction: column; }
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.title { font-size: 18px; font-weight: bold; display: flex; align-items: center; gap: 10px; color: #303133; }
.ent-score { display: flex; align-items: center; gap: 10px; font-weight: bold; color: #409EFF; }

.student-summary { background: #f0f9eb; padding: 10px; border-radius: 4px; margin-bottom: 20px; }
.student-summary p { margin: 5px 0; font-size: 14px; }
.sub-info { color: #666; font-size: 12px; }
.total-score { display: flex; justify-content: space-between; align-items: center; font-size: 16px; font-weight: bold; margin: 10px 0; }
.score-num { color: #F56C6C; font-size: 24px; }
</style>