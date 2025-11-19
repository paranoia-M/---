<template>
  <div class="page-container">
    <el-card shadow="never">
      <template #header>
        <div class="flex-between">
          <span><el-icon><Suitcase /></el-icon> 岗位需求全生命周期管理</span>
          <el-button type="primary" icon="Plus" @click="openDialog()">发布新岗位</el-button>
        </div>
      </template>

      <!-- 列表数据 -->
      <!-- 修复：移除了 v-loading，防止页面卡死无法点击 -->
      <el-table :data="jobList" stripe style="width: 100%">
        <el-table-column prop="title" label="岗位名称" min-width="200">
          <template #default="scope">
            <b>{{ scope.row.title }}</b>
            <el-tag v-if="scope.row.urgent" type="danger" size="small" effect="dark" style="margin-left: 5px">急聘</el-tag>
            <el-tag v-if="scope.row.isNew" type="success" size="small" effect="light" style="margin-left: 5px">New</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="salary" label="薪资范围" width="150" />
        
        <el-table-column label="招聘/缺口" width="140">
          <template #default="scope">
            <span>{{ scope.row.hired }} / {{ scope.row.count }}</span>
            <el-progress :percentage="Math.round((scope.row.hired/scope.row.count)*100)" :show-text="false" size="small" />
          </template>
        </el-table-column>
        
        <el-table-column prop="views" label="浏览量" width="100">
          <template #default="scope">
            {{ scope.row.views }} <span style="font-size:12px; color:#999">次</span>
          </template>
        </el-table-column>
        
        <el-table-column label="状态" width="120">
          <template #default="scope">
            <el-switch 
              v-model="scope.row.status" 
              active-text="招聘" 
              inactive-text="停用" 
              inline-prompt 
              @change="handleStatusChange(scope.row)"
            />
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="scope">
            <el-button link type="primary" icon="Edit" @click="openDialog(scope.row)">编辑</el-button>
            <el-button link type="warning" icon="Top" @click="handleTop(scope.$index)">刷新置顶</el-button>
            <el-button link type="danger" icon="Delete" @click="handleDelete(scope.$index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 发布/编辑 弹窗 -->
    <!-- 修复：增加 append-to-body 确保弹窗在最上层 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="isEdit ? '编辑岗位信息' : '发布新岗位'" 
      width="500px"
      append-to-body
    >
      <el-form :model="form" label-width="100px">
        <el-form-item label="岗位名称">
          <el-input v-model="form.title" placeholder="如：Python开发工程师" />
        </el-form-item>
        <el-form-item label="薪资范围">
          <el-select v-model="form.salary" style="width: 100%">
            <el-option label="2k-4k (实习)" value="2k-4k" />
            <el-option label="4k-6k" value="4k-6k" />
            <el-option label="6k-8k" value="6k-8k" />
            <el-option label="8k-10k" value="8k-10k" />
          </el-select>
        </el-form-item>
        <el-form-item label="需求人数">
          <el-input-number v-model="form.count" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="岗位标签">
          <el-checkbox v-model="form.urgent" label="急聘岗位" border />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveData" :loading="submitting">
          {{ isEdit ? '保存修改' : '立即发布' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
// 显式引入所需图标
import { Suitcase, Plus, Edit, Top, Delete } from '@element-plus/icons-vue'
// 显式引入反馈组件 (解决点击无反应的核心)
import { ElMessage, ElMessageBox } from 'element-plus'

// --- 状态定义 ---
const dialogVisible = ref(false)
const submitting = ref(false)
const isEdit = ref(false)
const editIndex = ref(-1)

// 初始数据
const jobList = ref([
  { title: 'Python数据清洗专员', salary: '3k-5k', count: 10, hired: 3, views: 1205, status: true, urgent: true, isNew: true },
  { title: 'IDC机房运维工程师', salary: '4k-6k', count: 5, hired: 1, views: 890, status: true, urgent: false, isNew: false },
  { title: 'AI数据标注实习生', salary: '2.5k-4k', count: 20, hired: 12, views: 3400, status: true, urgent: true, isNew: false },
  { title: '云计算售前支持', salary: '3k-6k', count: 2, hired: 2, views: 450, status: false, urgent: false, isNew: false },
])

const form = reactive({
  title: '',
  salary: '',
  count: 1,
  urgent: false
})

// --- 交互方法 ---

// 1. 打开弹窗
const openDialog = (row = null) => {
  console.log('点击打开弹窗', row)
  if (row) {
    isEdit.value = true
    editIndex.value = jobList.value.indexOf(row)
    // 填充数据
    form.title = row.title
    form.salary = row.salary
    form.count = row.count
    form.urgent = row.urgent
  } else {
    isEdit.value = false
    // 重置表单
    form.title = ''
    form.salary = '3k-5k'
    form.count = 1
    form.urgent = false
  }
  dialogVisible.value = true
}

// 2. 保存数据
const saveData = () => {
  console.log('点击保存')
  if (!form.title) return ElMessage.warning('请输入岗位名称')
  
  submitting.value = true
  
  setTimeout(() => {
    if (isEdit.value) {
      // 编辑
      if (editIndex.value > -1) {
        const target = jobList.value[editIndex.value]
        target.title = form.title
        target.salary = form.salary
        target.count = form.count
        target.urgent = form.urgent
        ElMessage.success('修改成功')
      }
    } else {
      // 新增
      jobList.value.unshift({
        title: form.title,
        salary: form.salary,
        count: form.count,
        hired: 0,
        views: 0,
        status: true,
        urgent: form.urgent,
        isNew: true // 标记为新
      })
      ElMessage.success('发布成功')
    }
    submitting.value = false
    dialogVisible.value = false
  }, 400)
}

// 3. 置顶
const handleTop = (index) => {
  if (index === 0) return ElMessage.info('已经是第一条了')
  const item = jobList.value.splice(index, 1)[0]
  item.isNew = true // 置顶后显示 New 标签
  jobList.value.unshift(item)
  ElMessage.success('置顶成功')
}

// 4. 删除 (关键修复：确保引用了 ElMessageBox)
const handleDelete = (index) => {
  ElMessageBox.confirm(
    '确定要下架并删除该岗位吗？',
    '警告',
    { confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning' }
  ).then(() => {
    jobList.value.splice(index, 1)
    ElMessage.success('岗位已删除')
  }).catch(() => {})
}

// 5. 状态切换
const handleStatusChange = (row) => {
  ElMessage({
    message: row.status ? '招聘已开启' : '招聘已暂停',
    type: row.status ? 'success' : 'info'
  })
}
</script>

<style scoped>
.page-container { padding: 20px; }
.flex-between { display: flex; justify-content: space-between; align-items: center; font-weight: bold; }
</style>