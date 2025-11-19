<template>
  <div class="page-container">
    <!-- 顶部核心指标 -->
    <el-row :gutter="20" class="mb-20">
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card success">
          <div class="stat-icon"><el-icon><UserFilled /></el-icon></div>
          <div class="stat-info">
            <div class="num">12</div>
            <div class="label">今日实到人数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card warning">
          <div class="stat-icon"><el-icon><List /></el-icon></div>
          <div class="stat-info">
            <div class="num">92%</div>
            <div class="label">本周周报提交率</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card danger">
          <div class="stat-icon"><el-icon><WarningFilled /></el-icon></div>
          <div class="stat-info">
            <div class="num">1</div>
            <div class="label">异常缺勤预警</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 主列表区 -->
    <el-card shadow="never">
      <template #header>
        <div class="flex-between">
          <div class="left">
            <span class="title">实习生名册与考勤</span>
            <el-input v-model="search" placeholder="搜索姓名/岗位..." prefix-icon="Search" style="width: 250px; margin-left: 20px" />
          </div>
          <el-button type="primary" plain icon="Download" @click="exportData">导出本月考勤表</el-button>
        </div>
      </template>

      <el-table :data="filteredList" stripe style="width: 100%">
        <el-table-column label="实习生信息" width="250">
          <template #default="scope">
            <div class="user-info">
              <el-avatar :size="40" :style="{ background: getAvatarColor(scope.row.name) }">
                {{ scope.row.name.charAt(0) }}
              </el-avatar>
              <div class="text">
                <div class="name">{{ scope.row.name }}</div>
                <div class="school">{{ scope.row.school }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="post" label="实习岗位" width="180" />
        
        <el-table-column prop="mentor" label="带教导师" width="120" />
        
        <el-table-column label="今日考勤状态" width="180">
          <template #default="scope">
            <el-tag v-if="scope.row.isClockIn" type="success" effect="dark">
              <el-icon><Check /></el-icon> 已打卡 {{ scope.row.clockTime }}
            </el-tag>
            <el-tag v-else type="danger" effect="dark">
              <el-icon><Close /></el-icon> 未打卡
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="实习进度" min-width="200">
          <template #default="scope">
            <el-progress :percentage="scope.row.progress" :format="format" />
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button link type="primary" @click="openReportDrawer(scope.row)">查看周报</el-button>
            <el-button link type="warning" @click="openFixDialog(scope.row)">考勤修正</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 抽屉：查看周报详情 -->
    <el-drawer v-model="drawerVisible" title="实习成长档案" size="45%">
      <div v-if="currentStudent">
        <div class="drawer-header">
          <h3>{{ currentStudent.name }} - {{ currentStudent.post }}</h3>
          <p>累计实习时长：320小时 | 综合评分：A</p>
        </div>
        
        <el-divider content-position="left">近期工作日志</el-divider>
        
        <el-timeline>
          <el-timeline-item timestamp="2024-06-18" placement="top" type="primary" size="large">
            <el-card class="log-card">
              <h4>第12周：数据清洗脚本优化</h4>
              <p>本周重点优化了 Python 正则匹配规则，将数据处理效率提升了 30%。遇到的问题是部分脏数据格式不统一...</p>
              <div class="tags">
                <el-tag size="small">Python</el-tag>
                <el-tag size="small" type="warning">导师已阅</el-tag>
              </div>
            </el-card>
          </el-timeline-item>
          
          <el-timeline-item timestamp="2024-06-11" placement="top">
             <el-card class="log-card">
              <h4>第11周：服务器基础巡检</h4>
              <p>跟随刘工完成了 IDC 机房的例行巡检，学习了 Linux 磁盘挂载命令。</p>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </div>
    </el-drawer>

    <!-- 弹窗：考勤修正 -->
    <el-dialog v-model="fixDialogVisible" title="考勤状态修正" width="400px" append-to-body>
      <el-form label-position="top">
        <el-form-item label="修正对象">
          <el-input v-model="currentStudent.name" disabled />
        </el-form-item>
        <el-form-item label="考勤状态">
          <el-radio-group v-model="fixForm.status">
            <el-radio :label="true">正常出勤</el-radio>
            <el-radio :label="false">缺勤/请假</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="补卡时间" v-if="fixForm.status">
          <el-time-picker v-model="fixForm.time" format="HH:mm" value-format="HH:mm" />
        </el-form-item>
        <el-form-item label="修正理由">
          <el-input v-model="fixForm.reason" placeholder="例如：忘记打卡、外勤" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="fixDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmFix">确认修正</el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { UserFilled, List, WarningFilled, Search, Download, Check, Close } from '@element-plus/icons-vue'
import { ElMessage, ElNotification } from 'element-plus'

// --- 数据 ---
const search = ref('')
const drawerVisible = ref(false)
const fixDialogVisible = ref(false)
const currentStudent = ref({})
const fixForm = reactive({ status: true, time: '09:00', reason: '' })

const interns = ref([
  { id: 1, name: '张伟', school: '庆阳职院', post: 'Python开发', mentor: '刘工', isClockIn: true, clockTime: '08:55', progress: 80 },
  { id: 2, name: '李娜', school: '庆阳职院', post: '运维助理', mentor: '赵工', isClockIn: true, clockTime: '08:40', progress: 65 },
  { id: 3, name: '王强', school: 'XX学院', post: '数据标注', mentor: '孙主管', isClockIn: false, clockTime: '', progress: 30 },
  { id: 4, name: '赵云', school: '庆阳职院', post: '前端开发', mentor: '周经理', isClockIn: true, clockTime: '08:58', progress: 90 },
])

// --- 逻辑 ---

// 筛选
const filteredList = computed(() => {
  return interns.value.filter(item => 
    item.name.includes(search.value) || item.post.includes(search.value)
  )
})

const format = (percentage) => percentage === 100 ? '满' : `${percentage}%`

const getAvatarColor = (name) => {
  const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C']
  return colors[name.charCodeAt(0) % colors.length]
}

// 导出
const exportData = () => {
  ElMessage.success('考勤表 (Excel) 已生成并下载')
}

// 打开周报抽屉
const openReportDrawer = (row) => {
  currentStudent.value = row
  drawerVisible.value = true
}

// 打开修正弹窗
const openFixDialog = (row) => {
  currentStudent.value = row
  fixForm.status = true
  fixForm.time = '09:00'
  fixForm.reason = ''
  fixDialogVisible.value = true
}

// 确认修正
const confirmFix = () => {
  // 更新列表数据
  const target = interns.value.find(i => i.id === currentStudent.value.id)
  if (target) {
    target.isClockIn = fixForm.status
    target.clockTime = fixForm.status ? fixForm.time : ''
    
    ElNotification({
      title: '修正成功',
      message: `已更新 ${target.name} 的考勤记录`,
      type: 'success'
    })
  }
  fixDialogVisible.value = false
}
</script>

<style scoped>
.page-container { padding: 20px; }
.mb-20 { margin-bottom: 20px; }

/* 顶部统计卡片样式 */
.stat-card {
  border: none;
  display: flex;
  align-items: center;
  color: #fff;
}
.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 20px;
}
.stat-card.success { background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%); }
.stat-card.warning { background: linear-gradient(135deg, #fccb90 0%, #d57eeb 100%); }
.stat-card.danger { background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 99%, #fecfef 100%); }

.stat-icon {
  font-size: 40px;
  margin-right: 20px;
  opacity: 0.8;
}
.stat-info .num { font-size: 28px; font-weight: bold; }
.stat-info .label { font-size: 14px; opacity: 0.9; }

/* 表格区 */
.flex-between { display: flex; justify-content: space-between; align-items: center; }
.left { display: flex; align-items: center; }
.title { font-size: 16px; font-weight: bold; color: #303133; }

.user-info { display: flex; align-items: center; gap: 10px; }
.user-info .name { font-weight: bold; color: #303133; }
.user-info .school { font-size: 12px; color: #909399; }

/* 抽屉 */
.drawer-header { background: #f5f7fa; padding: 15px; border-radius: 6px; margin-bottom: 20px; }
.log-card { margin-bottom: 10px; }
.log-card h4 { margin: 0 0 10px 0; color: #303133; }
.log-card p { color: #606266; font-size: 14px; line-height: 1.5; }
.tags { margin-top: 10px; }
</style>