<template>
  <div class="resume-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span><el-icon><Document /></el-icon> 简历收件箱 (全量管理)</span>
          <div class="actions">
            <el-button type="primary" link @click="fetchApplications">刷新数据</el-button>
            <el-button type="success" plain @click="exportExcel">导出Excel</el-button>
          </div>
        </div>
      </template>

      <!-- 筛选栏 -->
      <el-form :inline="true" class="filter-form">
        <el-form-item label="状态筛选">
          <el-select v-model="filterStatus" placeholder="全部状态" style="width: 120px" clearable>
            <el-option label="待初筛" value="待初筛" />
            <el-option label="待面试" value="待面试" />
            <el-option label="已淘汰" value="已淘汰" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <!-- 查询按钮实际上触发的是前端筛选逻辑，我们加个loading效果模拟一下 -->
          <el-button type="primary" @click="handleSearch" :loading="searching">查询</el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="filteredList" style="width: 100%" v-loading="loading" stripe size="large">
        <el-table-column type="index" width="50" />
        
        <el-table-column label="学生姓名" width="150">
          <template #default="scope">
            <div style="display: flex; align-items: center; gap: 10px;">
              <el-avatar :size="36" :style="{ background: getAvatarColor(scope.row.student_name) }">
                {{ scope.row.student_name.charAt(0) }}
              </el-avatar>
              <span style="font-weight: bold;">{{ scope.row.student_name }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="major" label="专业" width="160" />
        <el-table-column prop="job_title" label="投递岗位" show-overflow-tooltip />
        
        <el-table-column prop="created_at" label="投递时间" width="160">
          <template #default="scope">
            {{ new Date(scope.row.created_at).toLocaleDateString() }}
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="当前状态" width="110">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)" effect="dark">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="scope">
            
            <!-- 场景1: 待初筛 -> 显示通过/淘汰 -->
            <template v-if="scope.row.status === '待初筛'">
              <el-button type="primary" size="small" @click="handleStatusChange(scope.row, '待面试')">
                通过筛选
              </el-button>
              
              <el-popconfirm title="确定要淘汰该简历吗？" @confirm="handleStatusChange(scope.row, '已淘汰')">
                <template #reference>
                  <el-button type="danger" link size="small">淘汰</el-button>
                </template>
              </el-popconfirm>
            </template>

            <!-- 场景2: 待面试 -> 显示已处理 -->
            <template v-else-if="scope.row.status === '待面试'">
              <el-button type="success" size="small" plain disabled>面试安排中</el-button>
              <el-button type="info" link size="small" disabled>淘汰</el-button>
            </template>

             <!-- 场景3: 已淘汰 -> 显示状态 -->
            <template v-else>
              <el-button type="info" size="small" disabled>已结束</el-button>
            </template>

          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { Document } from '@element-plus/icons-vue'
import { ElMessage, ElNotification } from 'element-plus'

const loading = ref(false)
const searching = ref(false)
const list = ref([])
const filterStatus = ref('')

// 计算属性：前端筛选
const filteredList = computed(() => {
  if (!filterStatus.value) return list.value
  return list.value.filter(item => item.status === filterStatus.value)
})

// 1. 获取数据
const fetchApplications = async () => {
  loading.value = true
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/applications')
    list.value = res.data
  } catch (error) {
    console.error(error)
    ElMessage.error('数据获取失败')
  } finally {
    loading.value = false
  }
}

// 2. 模拟查询按钮点击
const handleSearch = () => {
  searching.value = true
  setTimeout(() => {
    searching.value = false
    ElMessage.success('查询完成')
  }, 500)
}

// 3. 状态样式映射
const getStatusType = (status) => {
  if (status === '待初筛') return 'warning'
  if (status === '待面试') return 'success'
  if (status === '已淘汰') return 'danger' // 红色
  return 'info'
}

// 4. 生成随机头像背景色
const getAvatarColor = (name) => {
  const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399']
  const index = name.charCodeAt(0) % colors.length
  return colors[index]
}

// 5. 核心功能：状态变更 (通过/淘汰)
// 替换原有的 handleStatusChange 函数
const handleStatusChange = async (row, newStatus) => {
  console.log("正在请求更新 ID:", row.id, "新状态:", newStatus); // 调试日志
  
  try {
    // 确保 URL 拼写正确，且 row.id 有值
    await axios.put(`http://127.0.0.1:8000/api/applications/${row.id}`, { 
      status: newStatus 
    })
    
    const msg = newStatus === '待面试' 
      ? `已发送面试邀请给 ${row.student_name}` 
      : `已淘汰 ${row.student_name} 的投递`
      
    ElNotification({
      title: '操作成功',
      message: msg,
      type: newStatus === '待面试' ? 'success' : 'info'
    })
    
    fetchApplications() // 刷新列表
  } catch (e) {
    console.error("更新失败:", e);
    // 弹出更详细的错误提示
    if (e.response && e.response.status === 404) {
      ElMessage.error('操作失败：找不到该条记录 (404)')
    } else if (e.response && e.response.status === 405) {
      ElMessage.error('操作失败：后端接口未定义 (405) - 请检查 main.py')
    } else if (e.response && e.response.status === 422) {
      ElMessage.error('操作失败：数据格式错误 (422)')
    } else {
      ElMessage.error('操作失败：服务器未响应或报错')
    }
  }
}

// 6. 核心功能：导出 Excel (前端生成 CSV)
const exportExcel = () => {
  if (filteredList.value.length === 0) {
    return ElMessage.warning('暂无数据可导出')
  }

  // 定义表头
  let csvContent = "\uFEFF姓名,专业,投递岗位,投递时间,当前状态\n";

  // 填充数据
  filteredList.value.forEach(row => {
    const date = new Date(row.created_at).toLocaleDateString()
    // 拼接 CSV 字符串
    csvContent += `${row.student_name},${row.major},${row.job_title},${date},${row.status}\n`;
  });

  // 创建下载链接
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement("a");
  const url = URL.createObjectURL(blob);
  
  link.setAttribute("href", url);
  link.setAttribute("download", `简历列表导出_${new Date().getTime()}.csv`);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  ElMessage.success('导出成功！')
}

onMounted(() => fetchApplications())
</script>

<style scoped>
.resume-container { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; font-size: 16px; font-weight: bold; }
.filter-form { margin-bottom: 10px; margin-top: 10px; }
.actions { display: flex; gap: 10px; }
</style>