<template>
  <div class="page-container">
    <!-- 1. 顶部核心指标 (KPI 驾驶舱) -->
    <el-row :gutter="20" class="mb-20">
      <el-col :span="6" v-for="(item, index) in kpis" :key="index">
        <el-card shadow="hover" class="kpi-card">
          <div class="kpi-icon" :class="item.color">
            <el-icon><component :is="item.icon" /></el-icon>
          </div>
          <div class="kpi-data">
            <div class="label">{{ item.label }}</div>
            <div class="num">{{ item.value }}</div>
            <div class="trend">
              较上届 <span :class="item.trend > 0 ? 'up' : 'down'">
                {{ item.trend > 0 ? '+' : ''}}{{ item.trend }}%
                <el-icon><component :is="item.trend > 0 ? 'Top' : 'Bottom'" /></el-icon>
              </span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="main-layout">
      <!-- 2. 左侧：就业台账 (核心管理区) -->
      <el-col :span="17">
        <el-card shadow="never" class="table-card">
          <template #header>
            <div class="card-header">
              <span class="title"><el-icon><Collection /></el-icon> 毕业生就业电子台账</span>
              <div class="actions">
                <el-button type="success" plain icon="Download" @click="exportData">批量导出</el-button>
              </div>
            </div>
            <!-- 筛选栏 -->
            <div class="filter-bar">
              <el-input v-model="filters.name" placeholder="搜姓名..." prefix-icon="Search" style="width: 150px" />
              <el-select v-model="filters.major" placeholder="所有专业" style="width: 150px" clearable>
                <el-option label="大数据技术" value="大数据技术" />
                <el-option label="云计算应用" value="云计算应用" />
                <el-option label="人工智能" value="人工智能" />
              </el-select>
              <el-select v-model="filters.status" placeholder="就业状态" style="width: 150px" clearable>
                <el-option label="已签约" value="已签约" />
                <el-option label="待就业" value="待就业" />
                <el-option label="升学" value="升学" />
              </el-select>
              <el-button type="primary" @click="handleFilter">查询</el-button>
            </div>
          </template>

          <el-table :data="filteredList" stripe style="width: 100%" v-loading="loading" size="large">
            <el-table-column prop="name" label="学生姓名" width="120">
              <template #default="scope">
                <div class="user-cell">
                  <el-avatar :size="28" :src="scope.row.avatar" />
                  <span>{{ scope.row.name }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="major" label="专业" width="140" />
            <el-table-column label="就业状态" width="110">
              <template #default="scope">
                <el-tag :type="getStatusColor(scope.row.status)" effect="dark">{{ scope.row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="company" label="去向单位/院校" min-width="180" show-overflow-tooltip />
            <el-table-column prop="salary" label="薪资" width="100">
              <template #default="scope">{{ scope.row.salary ? '¥'+scope.row.salary : '-' }}</template>
            </el-table-column>
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="scope">
                <el-button link type="primary" @click="openUpdateDialog(scope.row)">更新去向</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination">
            <el-pagination background layout="total, prev, pager, next" :total="filteredList.length" :page-size="10" />
          </div>
        </el-card>
      </el-col>

      <!-- 3. 右侧：图表 + 通知 -->
      <el-col :span="7">
        <!-- 图表卡片 -->
        <el-card shadow="hover" class="mb-20">
          <template #header><span class="sub-title">📊 就业结构分析</span></template>
          <div id="pieChart" style="height: 220px;"></div>
        </el-card>

        <!-- 招聘会时间轴 -->
        <el-card shadow="hover" class="timeline-card">
          <template #header>
            <div class="card-header">
              <span class="sub-title">🗓 近期双选会安排</span>
              <el-button link type="primary" size="small" @click="openFairDialog">发布通知</el-button>
            </div>
          </template>
          <el-scrollbar height="350px">
            <el-timeline>
              <el-timeline-item 
                v-for="(fair, index) in fairs" 
                :key="index" 
                :timestamp="fair.date" 
                :type="fair.type"
                placement="top"
              >
                <el-card class="event-card" :body-style="{ padding: '10px' }">
                  <h4>{{ fair.title }}</h4>
                  <p><el-icon><Location /></el-icon> {{ fair.loc }}</p>
                  <div class="tags">
                    <el-tag size="small" type="info">{{ fair.count }}家企业</el-tag>
                  </div>
                </el-card>
              </el-timeline-item>
            </el-timeline>
          </el-scrollbar>
        </el-card>
      </el-col>
    </el-row>

    <!-- 弹窗1：更新学生去向 -->
    <el-dialog v-model="updateVisible" title="更新就业信息" width="500px">
      <el-form label-width="100px" label-position="left">
        <el-form-item label="学生姓名">
          <el-input v-model="updateForm.name" disabled />
        </el-form-item>
        <el-form-item label="就业状态">
          <el-radio-group v-model="updateForm.status">
            <el-radio-button label="已签约" />
            <el-radio-button label="在岗实习" />
            <el-radio-button label="升学" />
            <el-radio-button label="待就业" />
          </el-radio-group>
        </el-form-item>
        <el-form-item label="单位/院校">
          <el-input v-model="updateForm.company" placeholder="请输入具体名称" />
        </el-form-item>
        <el-form-item label="薪资待遇" v-if="updateForm.status === '已签约'">
          <el-input-number v-model="updateForm.salary" :step="100" />
        </el-form-item>
        <el-form-item label="就业证明">
          <el-upload drag action="#" :limit="1">
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">拖拽上传三方协议/录取通知书</div>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="updateVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmUpdate">保存提交</el-button>
      </template>
    </el-dialog>

    <!-- 弹窗2：发布招聘会 -->
    <el-dialog v-model="fairVisible" title="发布双选会通知" width="450px">
      <el-form label-position="top">
        <el-form-item label="双选会标题">
          <el-input v-model="fairForm.title" />
        </el-form-item>
        <el-form-item label="举办日期">
          <el-date-picker v-model="fairForm.date" type="date" value-format="YYYY/MM/DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="举办地点">
          <el-input v-model="fairForm.loc" prefix-icon="Location" />
        </el-form-item>
        <el-form-item label="参会企业数">
          <el-input-number v-model="fairForm.count" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button type="primary" @click="publishFair">立即发布</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import * as echarts from 'echarts'
import { 
  Collection, Search, Location, UploadFilled, 
  User, Trophy, Money, School, Top, Bottom 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// --- KPI 数据 ---
const kpis = [
  { label: '2024届毕业生', value: '1,203', icon: 'User', color: 'blue', trend: 1.5 },
  { label: '已落实去向', value: '1,108', icon: 'Trophy', color: 'green', trend: 5.2 },
  { label: '平均实习薪资', value: '¥3,850', icon: 'Money', color: 'orange', trend: 8.4 },
  { label: '专升本录取', value: '120', icon: 'School', color: 'purple', trend: -2.1 },
]

// --- 列表数据 ---
const loading = ref(false)
const filters = reactive({ name: '', major: '', status: '' })
const jobList = ref([
  { id: 1, name: '张伟', avatar: 'https://ui-avatars.com/api/?name=ZW&bg=409eff&color=fff', major: '大数据技术', status: '已签约', company: '东数西算云创科技', salary: 4500 },
  { id: 2, name: '李娜', avatar: 'https://ui-avatars.com/api/?name=LN&bg=67c23a&color=fff', major: '云计算应用', status: '在岗实习', company: '庆阳电信数据中心', salary: 3200 },
  { id: 3, name: '王强', avatar: 'https://ui-avatars.com/api/?name=WQ&bg=e6a23c&color=fff', major: '人工智能', status: '待就业', company: '-', salary: 0 },
  { id: 4, name: '赵云', avatar: 'https://ui-avatars.com/api/?name=ZY&bg=909399&color=fff', major: '软件工程', status: '升学', company: '兰州大学', salary: 0 },
  { id: 5, name: '孙悟空', avatar: 'https://ui-avatars.com/api/?name=SW&bg=f56c6c&color=fff', major: '网络安全', status: '已签约', company: '奇安信', salary: 5000 },
])

// --- 双选会数据 ---
const fairs = ref([
  { date: '2024/06/20', title: '庆阳市数字经济专场招聘会', loc: '学院体育馆', count: 50, type: 'primary' },
  { date: '2024/06/15', title: '华为生态伙伴专场宣讲', loc: '报告厅A', count: 12, type: 'success' },
  { date: '2024/06/01', title: '东数西算产业园线上双选', loc: '腾讯会议', count: 80, type: 'warning' },
])

// --- 弹窗状态 ---
const updateVisible = ref(false)
const fairVisible = ref(false)
const updateForm = reactive({ id: null, name: '', status: '', company: '', salary: 0 })
const fairForm = reactive({ title: '', date: '', loc: '', count: 10 })

// --- 逻辑方法 ---

const filteredList = computed(() => {
  return jobList.value.filter(item => {
    const nameMatch = item.name.includes(filters.name)
    const majorMatch = filters.major ? item.major === filters.major : true
    const statusMatch = filters.status ? item.status === filters.status : true
    return nameMatch && majorMatch && statusMatch
  })
})

const handleFilter = () => {
  loading.value = true
  setTimeout(() => loading.value = false, 300)
}

const exportData = () => ElMessage.success('就业花名册导出成功')

const getStatusColor = (status) => {
  if (status === '已签约') return 'success'
  if (status === '在岗实习') return 'primary'
  if (status === '升学') return 'warning'
  return 'danger'
}

// 打开更新弹窗
const openUpdateDialog = (row) => {
  Object.assign(updateForm, row)
  updateVisible.value = true
}

// 确认更新
const confirmUpdate = () => {
  const target = jobList.value.find(i => i.id === updateForm.id)
  if (target) Object.assign(target, updateForm)
  updateVisible.value = false
  ElMessage.success('就业信息已更新')
}

// 发布招聘会
const openFairDialog = () => {
  fairForm.title = ''
  fairForm.date = ''
  fairForm.loc = ''
  fairVisible.value = true
}

const publishFair = () => {
  if (!fairForm.title) return ElMessage.warning('请填写完整')
  fairs.value.unshift({ ...fairForm, type: 'primary' })
  fairVisible.value = false
  ElMessage.success('通知发布成功')
}

// 初始化图表
onMounted(() => {
  nextTick(() => {
    const chart = echarts.init(document.getElementById('pieChart'))
    chart.setOption({
      color: ['#67C23A', '#409EFF', '#E6A23C', '#F56C6C'],
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        data: [
          { value: 800, name: '已签约' },
          { value: 308, name: '在岗实习' },
          { value: 120, name: '升学' },
          { value: 45, name: '待就业' }
        ]
      }]
    })
    window.addEventListener('resize', () => chart.resize())
  })
})
</script>

<style scoped>
.page-container { padding: 20px; }
.mb-20 { margin-bottom: 20px; }

/* KPI 卡片 */
.kpi-card { border: none; }
.kpi-card :deep(.el-card__body) { display: flex; align-items: center; padding: 20px; }
.kpi-icon { width: 60px; height: 60px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 28px; margin-right: 15px; }
.blue { background: #ecf5ff; color: #409EFF; }
.green { background: #f0f9eb; color: #67C23A; }
.orange { background: #fdf6ec; color: #E6A23C; }
.purple { background: #f4f4f5; color: #909399; }

.kpi-data .label { font-size: 12px; color: #909399; }
.kpi-data .num { font-size: 24px; font-weight: bold; color: #303133; margin: 5px 0; }
.trend { font-size: 12px; color: #909399; }
.up { color: #F56C6C; } .down { color: #67C23A; }

/* 表格区 */
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.title { font-size: 16px; font-weight: bold; display: flex; align-items: center; gap: 8px; }
.filter-bar { display: flex; gap: 10px; background: #f8f9fa; padding: 10px; border-radius: 6px; }
.user-cell { display: flex; align-items: center; gap: 8px; }
.pagination { margin-top: 20px; display: flex; justify-content: flex-end; }

/* 右侧 */
.sub-title { font-weight: bold; color: #303133; }
.timeline-card { height: 400px; }
.event-card h4 { margin: 0 0 5px 0; font-size: 14px; }
.event-card p { margin: 0; font-size: 12px; color: #909399; display: flex; align-items: center; gap: 4px; }
.tags { margin-top: 5px; }
</style>