<template>
  <div class="page-container">
    <!-- 顶部通栏卡片：展示合作概况 -->
    <el-row :gutter="20" class="mb-20">
      <el-col :span="24">
        <el-card shadow="hover" class="header-card">
          <div class="header-content">
            <div class="icon-box">
              <el-icon :size="40"><Connection /></el-icon>
            </div>
            <div class="text-box">
              <h3>“东数西算”产业对接项目库</h3>
              <p>当前签约院校：庆阳XXXX学院 | XX学院 &nbsp;&nbsp; 累计交付项目：15 个</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 主内容区 -->
    <el-card shadow="never">
      <!-- 工具栏 -->
      <div class="toolbar">
        <div class="left">
          <el-radio-group v-model="filterStatus" size="large" @change="handleFilter">
            <el-radio-button label="全部" />
            <el-radio-button label="进行中" />
            <el-radio-button label="已结项" />
          </el-radio-group>
        </div>
        <div class="right">
          <el-button type="primary" size="large" icon="Plus" @click="openAddDialog">发起新合作项目</el-button>
        </div>
      </div>

      <!-- 项目列表 -->
      <el-table :data="filteredList" size="large" stripe style="width: 100%; margin-top: 20px">
        <el-table-column prop="id" label="项目编号" width="120" />
        
        <el-table-column prop="name" label="项目名称" min-width="200">
          <template #default="scope">
            <span style="font-weight: bold; color: #303133">{{ scope.row.name }}</span>
            <el-tag v-if="scope.row.isNew" type="danger" size="small" effect="dark" style="margin-left: 5px">New</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="承接院校" width="180">
          <template #default="scope">
            <el-tag effect="plain" round>{{ scope.row.school }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="项目进度" min-width="250">
          <template #default="scope">
            <div class="progress-wrapper">
              <el-progress 
                :percentage="scope.row.progress" 
                :status="scope.row.progress === 100 ? 'success' : ''"
                :stroke-width="10"
                striped
                striped-flow
              />
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="当前状态" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.status === '进行中' ? 'primary' : 'success'">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="scope">
            <template v-if="scope.row.status === '进行中'">
              <el-button type="primary" link icon="Edit" @click="openUpdateDialog(scope.row)">更新进度</el-button>
              <el-button type="success" link icon="CircleCheck" @click="openFinishDialog(scope.row)">验收结项</el-button>
            </template>
            <template v-else>
              <el-button type="info" link icon="Document" @click="viewReport">查看报告</el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 弹窗1：发起新项目 -->
    <el-dialog v-model="addVisible" title="发起校企合作项目" width="500px" append-to-body>
      <el-form :model="addForm" label-position="top">
        <el-form-item label="项目名称">
          <el-input v-model="addForm.name" placeholder="例如：2024智慧城市数据采集" />
        </el-form-item>
        <el-form-item label="指定承接院校">
          <el-select v-model="addForm.school" placeholder="请选择院校" style="width: 100%">
            <el-option label="庆阳XXXX学院" value="庆阳XXXX学院" />
            <el-option label="XX学院" value="XX学院" />
          </el-select>
        </el-form-item>
        <el-form-item label="项目预算/经费">
          <el-input v-model="addForm.budget" placeholder="例如：50,000元" />
        </el-form-item>
        <el-form-item label="项目需求描述">
          <el-input v-model="addForm.desc" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmAdd">立即发布</el-button>
      </template>
    </el-dialog>

    <!-- 弹窗2：更新进度 -->
    <el-dialog v-model="updateVisible" title="更新项目交付进度" width="400px" append-to-body>
      <div style="padding: 20px 0; text-align: center;">
        <h4 style="margin-bottom: 20px;">{{ currentProject?.name }}</h4>
        <el-slider v-model="tempProgress" show-input />
        <p style="font-size: 12px; color: #999; margin-top: 10px;">请根据学校实际交付情况调整</p>
      </div>
      <template #footer>
        <el-button @click="updateVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmUpdate">确认更新</el-button>
      </template>
    </el-dialog>

    <!-- 弹窗3：验收结项 -->
    <el-dialog v-model="finishVisible" title="项目验收与归档" width="500px" append-to-body>
      <el-form label-position="top">
        <el-form-item label="验收评语">
          <el-input type="textarea" v-model="finishComment" :rows="3" placeholder="对学校交付质量、响应速度的评价..." />
        </el-form-item>
        <el-form-item label="上传验收报告">
          <el-upload class="upload-demo" drag action="#" multiple>
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">拖拽文件到此处或 <em>点击上传</em></div>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="finishVisible = false">取消</el-button>
        <el-button type="success" @click="confirmFinish">确认结项</el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { Connection, Plus, Edit, CircleCheck, Document, UploadFilled } from '@element-plus/icons-vue'
import { ElMessage, ElNotification } from 'element-plus'

// --- 数据 ---
const filterStatus = ref('全部')
const addVisible = ref(false)
const updateVisible = ref(false)
const finishVisible = ref(false)

const currentProject = ref(null)
const tempProgress = ref(0)
const finishComment = ref('')

const addForm = reactive({ name: '', school: '', budget: '', desc: '' })

const projects = ref([
  { id: 'XM202401', name: '政务云平台历史数据迁移清洗', school: '庆阳XXXX学院', progress: 65, status: '进行中', isNew: false },
  { id: 'XM202402', name: '数据中心服务器资产盘点', school: '庆阳XXXX学院', progress: 100, status: '已结项', isNew: false },
  { id: 'XM202403', name: '智慧农业物联网数据采集', school: 'XX学院', progress: 30, status: '进行中', isNew: false },
])

// --- 逻辑 ---

// 筛选
const filteredList = computed(() => {
  if (filterStatus.value === '全部') return projects.value
  return projects.value.filter(p => p.status === filterStatus.value)
})

// 1. 发起新项目
const openAddDialog = () => {
  addForm.name = ''
  addForm.school = ''
  addForm.budget = ''
  addForm.desc = ''
  addVisible.value = true
}

const confirmAdd = () => {
  if (!addForm.name || !addForm.school) return ElMessage.warning('请填写完整信息')
  
  projects.value.unshift({
    id: `XM${Date.now().toString().slice(-6)}`,
    name: addForm.name,
    school: addForm.school,
    progress: 0,
    status: '进行中',
    isNew: true
  })
  
  addVisible.value = false
  ElMessage.success('项目发布成功，已通知院校负责人')
}

// 2. 更新进度
const openUpdateDialog = (row) => {
  currentProject.value = row
  tempProgress.value = row.progress
  updateVisible.value = true
}

const confirmUpdate = () => {
  currentProject.value.progress = tempProgress.value
  if (tempProgress.value === 100) {
    ElMessage.success('进度已更新至 100%，建议进行验收结项')
  } else {
    ElMessage.success('进度更新成功')
  }
  updateVisible.value = false
}

// 3. 验收结项
const openFinishDialog = (row) => {
  currentProject.value = row
  finishComment.value = ''
  finishVisible.value = true
}

const confirmFinish = () => {
  currentProject.value.progress = 100
  currentProject.value.status = '已结项'
  finishVisible.value = false
  
  ElNotification({
    title: '结项成功',
    message: `项目【${currentProject.value.name}】已归档，感谢您的评价！`,
    type: 'success'
  })
}

const viewReport = () => {
  ElMessage.info('正在下载验收报告 PDF...')
}
</script>

<style scoped>
.page-container { padding: 20px; }
.mb-20 { margin-bottom: 20px; }

/* 头部卡片样式 */
.header-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border: none;
}
.header-content {
  display: flex;
  align-items: center;
  gap: 20px;
}
.icon-box {
  background: rgba(255,255,255,0.2);
  padding: 15px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.text-box h3 { margin: 0 0 5px 0; font-size: 20px; }
.text-box p { margin: 0; opacity: 0.9; font-size: 14px; }

/* 工具栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>