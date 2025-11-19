<template>
  <div class="page-container">
    <el-card shadow="never" class="main-card">
      <!-- 1. 顶部操作栏 -->
      <template #header>
        <div class="toolbar">
          <div class="title">
            <el-icon><Management /></el-icon> 工学一体化实训项目库
          </div>
          <div class="filters">
            <el-input v-model="searchKey" placeholder="搜索项目名称..." prefix-icon="Search" style="width: 240px" clearable />
            <el-select v-model="filterStatus" placeholder="项目状态" style="width: 120px; margin-left: 10px">
              <el-option label="全部" value="" />
              <el-option label="进行中" value="进行中" />
              <el-option label="已结项" value="已结项" />
              <el-option label="筹备中" value="筹备中" />
            </el-select>
            <el-button type="primary" icon="Plus" style="margin-left: 20px" @click="handleAdd">立项新项目</el-button>
          </div>
        </div>
      </template>

      <!-- 2. 数据表格 -->
      <el-table :data="filteredList" style="width: 100%" size="large" stripe v-loading="loading">
        <el-table-column prop="id" label="项目编号" width="120" />
        <el-table-column prop="name" label="项目名称" min-width="200">
          <template #default="scope">
            <span class="project-name">{{ scope.row.name }}</span>
            <el-tag v-if="scope.row.isHot" size="small" type="danger" effect="dark" style="margin-left: 5px">重点</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="company" label="合作企业" width="200">
          <template #default="scope">
             <el-tag type="info" effect="plain"><el-icon><OfficeBuilding /></el-icon> {{ scope.row.company }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="周期/进度" width="250">
          <template #default="scope">
            <div class="progress-box">
              <div class="time-range">{{ scope.row.startDate }} 至 {{ scope.row.endDate }}</div>
              <el-progress :percentage="scope.row.progress" :status="getProgressStatus(scope.row)" :stroke-width="8" />
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="students" label="参与人数" width="100" align="center" />
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="scope">
            <el-button link type="primary" icon="Edit" @click="handleEdit(scope.row)">编辑</el-button>
            <!-- ✅ 这里触发周报监控 -->
            <el-button link type="success" icon="DataAnalysis" @click="openReport(scope.row)">周报监控</el-button>
            <el-popconfirm title="确定要终止该项目吗？" @confirm="handleDelete(scope.row)">
              <template #reference>
                <el-button link type="danger" icon="Delete">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-box">
        <el-pagination background layout="total, prev, pager, next" :total="filteredList.length" :page-size="10" />
      </div>
    </el-card>

    <!-- 3. 新增/编辑 弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="项目名称">
          <el-input v-model="form.name" placeholder="请输入实训项目全称" />
        </el-form-item>
        <el-form-item label="合作企业">
          <el-select v-model="form.company" placeholder="请选择对接企业" style="width: 100%">
            <el-option label="东数西算云创科技" value="东数西算云创科技" />
            <el-option label="庆阳电信数据中心" value="庆阳电信数据中心" />
            <el-option label="字节跳动(庆阳基地)" value="字节跳动(庆阳基地)" />
          </el-select>
        </el-form-item>
        <el-form-item label="实训周期">
          <el-date-picker
            v-model="form.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="计划人数">
          <el-input-number v-model="form.students" :min="1" />
        </el-form-item>
        <el-form-item label="项目描述">
          <el-input v-model="form.desc" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveProject">确认保存</el-button>
      </template>
    </el-dialog>

    <!-- ✅ 4. 周报监控抽屉 (新增功能) -->
    <el-drawer v-model="drawerVisible" title="实习周报监控中心" size="50%">
      <div v-if="currentProject">
        <div class="drawer-header-info">
          <h3>{{ currentProject.name }}</h3>
          <p>当前周报提交率：<span style="color: #67C23A; font-weight: bold;">95%</span> ({{ currentProject.students }}人)</p>
        </div>

        <el-divider content-position="left">最新提交动态</el-divider>

        <el-timeline style="padding-left: 10px;">
          <el-timeline-item timestamp="2024-06-15" placement="top" type="primary">
            <el-card class="report-card">
              <div class="report-header">
                <span class="student-name">张伟 (大数据班)</span>
                <el-tag size="small">第12周</el-tag>
              </div>
              <p class="report-content">本周完成了Python爬虫脚本的编写，抓取了5000条电商数据并进行了清洗。遇到的问题是反爬机制...</p>
              <div class="report-meta">工时：40小时 | 心情：😄 开心</div>
            </el-card>
          </el-timeline-item>
          
          <el-timeline-item timestamp="2024-06-15" placement="top" type="success">
             <el-card class="report-card">
              <div class="report-header">
                <span class="student-name">李娜 (云计算班)</span>
                <el-tag size="small" type="success">第12周</el-tag>
              </div>
              <p class="report-content">协助企业导师完成了服务器的例行巡检，学习了Linux下的磁盘挂载命令。</p>
              <div class="report-meta">工时：38小时 | 心情：😐 平静</div>
            </el-card>
          </el-timeline-item>

          <el-timeline-item timestamp="2024-06-14" placement="top">
             <el-card class="report-card">
              <div class="report-header">
                <span class="student-name">王强 (人工智能班)</span>
                <el-tag size="small" type="warning">第11周(补交)</el-tag>
              </div>
              <p class="report-content">完成了图片标注任务，共标注200张。</p>
              <div class="report-meta">工时：35小时 | 心情：😫 疲惫</div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { Search, Plus, Management, OfficeBuilding, Edit, Delete, DataAnalysis } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 模拟数据
const rawData = [
  { id: 'P-2024001', name: '庆阳政务云数据清洗一期', isHot: true, company: '东数西算云创科技', startDate: '2024-01-10', endDate: '2024-06-30', progress: 65, students: 15, status: '进行中' },
  { id: 'P-2024002', name: 'IDC机房巡检实训', isHot: false, company: '庆阳电信数据中心', startDate: '2023-09-01', endDate: '2023-12-31', progress: 100, students: 8, status: '已结项' },
  { id: 'P-2024003', name: '抖音直播间数据标注', isHot: true, company: '字节跳动(庆阳基地)', startDate: '2024-03-01', endDate: '2024-05-01', progress: 25, students: 30, status: '进行中' },
  { id: 'P-2024004', name: '智慧校园网络升级', isHot: false, company: '华为云', startDate: '2024-06-01', endDate: '2024-09-01', progress: 0, students: 10, status: '筹备中' },
]

const list = ref([...rawData])
const loading = ref(false)
const searchKey = ref('')
const filterStatus = ref('')

// 弹窗 & 抽屉 控制
const dialogVisible = ref(false)
const drawerVisible = ref(false) // ✅ 控制周报抽屉
const currentProject = ref(null) // ✅ 当前选中的项目
const dialogTitle = ref('立项新项目')
const form = reactive({ name: '', company: '', dateRange: [], students: 10, desc: '' })

// 筛选逻辑
const filteredList = computed(() => {
  return list.value.filter(item => {
    const matchName = item.name.includes(searchKey.value)
    const matchStatus = filterStatus.value ? item.status === filterStatus.value : true
    return matchName && matchStatus
  })
})

const getStatusType = (status) => {
  if (status === '进行中') return 'primary'
  if (status === '已结项') return 'success'
  return 'info'
}

const getProgressStatus = (row) => {
  if (row.status === '已结项') return 'success'
  if (row.progress < 30) return 'warning'
  return ''
}

const handleAdd = () => {
  dialogTitle.value = '立项新项目'
  Object.assign(form, { name: '', company: '', dateRange: [], students: 10, desc: '' })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑项目信息'
  Object.assign(form, {
    name: row.name,
    company: row.company,
    dateRange: [row.startDate, row.endDate],
    students: row.students,
    desc: '这是从数据库获取的描述...'
  })
  dialogVisible.value = true
}

// ✅ 打开周报监控抽屉
const openReport = (row) => {
  currentProject.value = row
  drawerVisible.value = true
}

const saveProject = () => {
  if (!form.name || !form.company) return ElMessage.warning('请填写完整信息')
  dialogVisible.value = false
  loading.value = true
  setTimeout(() => {
    if (dialogTitle.value === '立项新项目') {
      list.value.unshift({
        id: `P-2024${Math.floor(Math.random() * 1000)}`,
        name: form.name,
        company: form.company,
        startDate: form.dateRange?.[0] || '2024-01-01',
        endDate: form.dateRange?.[1] || '2024-12-31',
        progress: 0,
        students: form.students,
        status: '筹备中'
      })
    }
    loading.value = false
    ElMessage.success('保存成功')
  }, 500)
}

const handleDelete = (row) => {
  list.value = list.value.filter(item => item.id !== row.id)
  ElMessage.success('项目已移除')
}
</script>

<style scoped>
.page-container { padding: 20px; height: 100%; box-sizing: border-box; }
.main-card { height: 100%; display: flex; flex-direction: column; }
.toolbar { display: flex; justify-content: space-between; align-items: center; }
.title { font-size: 18px; font-weight: bold; display: flex; align-items: center; gap: 10px; color: #303133; }
.filters { display: flex; align-items: center; }
.project-name { font-weight: bold; color: #303133; }
.progress-box { display: flex; flex-direction: column; justify-content: center; }
.time-range { font-size: 12px; color: #909399; margin-bottom: 4px; }
.pagination-box { margin-top: 20px; display: flex; justify-content: flex-end; }

/* 抽屉样式 */
.drawer-header-info { background: #f0f9eb; padding: 15px; border-radius: 6px; margin-bottom: 20px; }
.drawer-header-info h3 { margin: 0 0 10px 0; color: #303133; }
.drawer-header-info p { margin: 0; color: #606266; font-size: 14px; }
.report-card { cursor: pointer; transition: all 0.3s; }
.report-card:hover { transform: translateX(5px); }
.report-header { display: flex; justify-content: space-between; margin-bottom: 10px; }
.student-name { font-weight: bold; color: #303133; }
.report-content { color: #606266; font-size: 14px; line-height: 1.5; margin-bottom: 10px; }
.report-meta { color: #909399; font-size: 12px; border-top: 1px dashed #eee; padding-top: 8px; }
</style>