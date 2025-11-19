<template>
  <div class="page-container">
    <!-- 1. 顶部阅读量统计 -->
    <el-row :gutter="20" class="mb-20">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card bg-blue">
          <div class="stat-num">{{ totalViews.toLocaleString() }}</div>
          <div class="stat-label">累计阅读量</div>
          <el-icon class="stat-icon"><View /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card bg-purple">
          <div class="stat-num">{{ newsList.length }}</div>
          <div class="stat-label">已发布通知</div>
          <el-icon class="stat-icon"><Document /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never" class="chart-card">
          <div id="trendChart" style="height: 100px; width: 100%"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 2. 主体列表区 -->
    <el-card shadow="never">
      <template #header>
        <div class="toolbar">
          <div class="left-filters">
            <el-radio-group v-model="activeTab">
              <el-radio-button label="全部" />
              <el-radio-button label="政策文件" />
              <el-radio-button label="通知公告" />
              <el-radio-button label="新闻动态" />
            </el-radio-group>
            <el-input v-model="searchKey" placeholder="搜索标题..." prefix-icon="Search" style="width: 200px; margin-left: 15px" clearable />
          </div>
          <el-button type="primary" icon="Edit" @click="openEditor()">发布新通知</el-button>
        </div>
      </template>

      <el-table :data="filteredList" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="title" label="标题" min-width="300">
          <template #default="scope">
            <div class="title-cell">
              <el-tag v-if="scope.row.isTop" type="danger" size="small" effect="dark" class="mr-5">置顶</el-tag>
              <!-- ✅ 点击标题触发查看 -->
              <span class="news-title" @click="viewDetail(scope.row)">{{ scope.row.title }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="category" label="分类" width="120">
          <template #default="scope">
            <el-tag :type="getCategoryType(scope.row.category)" effect="plain">{{ scope.row.category }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="author" label="发布人" width="120" />
        
        <el-table-column prop="date" label="发布日期" width="150" sortable />
        
        <el-table-column prop="views" label="阅读" width="100" align="center">
          <template #default="scope">
            <span style="color: #909399">{{ scope.row.views }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="状态" width="150">
          <template #default="scope">
            <el-switch 
              v-model="scope.row.status" 
              active-text="已发" 
              inactive-text="撤回" 
              inline-prompt 
              @change="handleStatusChange(scope.row)"
            />
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button link type="primary" @click="openEditor(scope.row)">编辑</el-button>
            <el-button link type="warning" @click="toggleTop(scope.row)">{{ scope.row.isTop ? '取消置顶' : '置顶' }}</el-button>
            <el-popconfirm title="确定删除该通知吗？" @confirm="handleDelete(scope.$index)">
              <template #reference>
                <el-button link type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- ✅ 新增：查看详情抽屉 -->
    <el-drawer v-model="detailVisible" title="通知详情预览" size="50%">
      <div v-if="currentNews" class="article-container">
        <h1 class="article-title">{{ currentNews.title }}</h1>
        <div class="article-meta">
          <span><el-icon><User /></el-icon> {{ currentNews.author }}</span>
          <span><el-icon><Clock /></el-icon> {{ currentNews.date }}</span>
          <span><el-icon><View /></el-icon> {{ currentNews.views }} 次阅读</span>
          <el-tag size="small">{{ currentNews.category }}</el-tag>
        </div>
        <el-divider />
        <div class="article-content">
          <!-- 模拟正文内容 -->
          <p v-if="currentNews.content">{{ currentNews.content }}</p>
          <div v-else>
            <p><strong>各相关部门、全体师生：</strong></p>
            <p>为深入贯彻落实国家“东数西算”工程战略部署，加快我市数字经济人才培养...</p>
            <p>一、补贴对象：...</p>
            <p>二、申请流程：...</p>
            <p>特此通知。</p>
            <br>
            <p style="text-align: right;">{{ currentNews.author }}</p>
            <p style="text-align: right;">{{ currentNews.date }}</p>
          </div>
        </div>
      </div>
    </el-drawer>

    <!-- 编辑/发布抽屉 -->
    <el-drawer v-model="drawerVisible" :title="form.id ? '编辑通知' : '发布新通知'" size="60%">
      <el-form label-position="top" :model="form">
        <el-row :gutter="20">
          <el-col :span="16">
            <el-form-item label="通知标题">
              <el-input v-model="form.title" placeholder="请输入醒目的标题" size="large" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="所属分类">
              <el-select v-model="form.category" style="width: 100%" size="large">
                <el-option label="政策文件" value="政策文件" />
                <el-option label="通知公告" value="通知公告" />
                <el-option label="新闻动态" value="新闻动态" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="正文内容">
          <div class="editor-toolbar">
            <el-button-group>
              <el-button size="small"><b>B</b></el-button>
              <el-button size="small"><i>I</i></el-button>
              <el-button size="small"><u>U</u></el-button>
            </el-button-group>
            <el-button-group style="margin-left: 10px">
              <el-button size="small" icon="Picture" />
              <el-button size="small" icon="Link" />
            </el-button-group>
          </div>
          <el-input v-model="form.content" type="textarea" :rows="15" class="editor-area" />
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="form.isTop" label="发布后立即置顶" border />
          <el-checkbox v-model="form.status" label="直接发布 (不存草稿)" border />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="drawerVisible = false">取消</el-button>
        <el-button type="primary" @click="saveNews" size="large">
          <el-icon class="el-icon--left"><Position /></el-icon> 立即发布
        </el-button>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { View, Document, Edit, Search, Picture, Link, Position, User, Clock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

// --- 数据 ---
const activeTab = ref('全部')
const searchKey = ref('')
const loading = ref(false)
const drawerVisible = ref(false)
const detailVisible = ref(false)
const currentNews = ref(null)

const form = reactive({ id: null, title: '', category: '通知公告', isTop: false, status: true, content: '' })

const newsList = ref([
  { id: 1, title: '关于庆阳市“东数西算”人才补贴申请的通知', category: '政策文件', author: '教务处', date: '2023-11-01', views: 2340, isTop: true, status: true, content: '为鼓励高校毕业生在庆阳就业...' },
  { id: 2, title: '2024年春季学期工学交替实施方案', category: '通知公告', author: '实训中心', date: '2023-10-25', views: 1205, isTop: false, status: true },
  { id: 3, title: '教育部关于推进职业教育工学一体化改革的意见', category: '政策文件', author: '行政办', date: '2023-10-15', views: 890, isTop: false, status: true },
  { id: 4, title: '庆阳XXXX学院第十届技能大赛获奖名单公示', category: '新闻动态', author: '团委', date: '2023-10-10', views: 4500, isTop: false, status: true },
  { id: 5, title: '关于国庆节放假及安全注意事项的通知', category: '通知公告', author: '保卫处', date: '2023-09-28', views: 5600, isTop: false, status: false },
])

// --- 逻辑 ---

// 自动计算总阅读量
const totalViews = computed(() => newsList.value.reduce((sum, item) => sum + item.views, 0))

// 筛选
const filteredList = computed(() => {
  return newsList.value.filter(item => {
    const tabMatch = activeTab.value === '全部' ? true : item.category === activeTab.value
    const searchMatch = item.title.includes(searchKey.value)
    return tabMatch && searchMatch
  })
})

// 查看详情 (核心新增)
const viewDetail = (row) => {
  currentNews.value = row
  row.views++ // 阅读量+1
  detailVisible.value = true
}

// 编辑/发布
const openEditor = (row = null) => {
  if (row) {
    Object.assign(form, row)
  } else {
    Object.assign(form, { id: null, title: '', category: '通知公告', isTop: false, status: true, content: '' })
  }
  drawerVisible.value = true
}

const saveNews = () => {
  if (!form.title) return ElMessage.warning('标题不能为空')
  
  if (form.id) {
    const target = newsList.value.find(i => i.id === form.id)
    Object.assign(target, form)
    ElMessage.success('修改成功')
  } else {
    newsList.value.unshift({
      id: Date.now(),
      ...form,
      author: '管理员',
      date: new Date().toISOString().split('T')[0],
      views: 0
    })
    ElMessage.success('发布成功')
  }
  drawerVisible.value = false
}

// 置顶/状态/删除
const toggleTop = (row) => {
  row.isTop = !row.isTop
  newsList.value.sort((a, b) => b.isTop - a.isTop)
  ElMessage.success(row.isTop ? '已置顶' : '已取消置顶')
}
const handleStatusChange = (row) => ElMessage.info(row.status ? '已发布' : '已撤回')
const handleDelete = (index) => {
  newsList.value.splice(index, 1)
  ElMessage.success('删除成功')
}

// 图表
const getCategoryType = (cat) => {
  const map = { '政策文件': 'danger', '通知公告': 'warning', '新闻动态': 'success' }
  return map[cat] || 'info'
}

onMounted(() => {
  nextTick(() => {
    const chart = echarts.init(document.getElementById('trendChart'))
    chart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { top: 10, bottom: 20, left: 0, right: 0 },
      xAxis: { show: false, data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
      yAxis: { show: false },
      series: [{
        data: [820, 932, 901, 934, 1290, 1330, 1320],
        type: 'line',
        smooth: true,
        areaStyle: { color: 'rgba(64, 158, 255, 0.2)' },
        itemStyle: { color: '#409EFF' },
        showSymbol: false
      }]
    })
  })
})
</script>

<style scoped>
.page-container { padding: 20px; }
.mb-20 { margin-bottom: 20px; }
.mr-5 { margin-right: 5px; }

/* 统计卡片 */
.stat-card {
  position: relative;
  border: none;
  color: #fff;
  overflow: hidden;
}
.bg-blue { background: linear-gradient(135deg, #36d1dc 0%, #5b86e5 100%); }
.bg-purple { background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%); }
.stat-num { font-size: 32px; font-weight: bold; margin-bottom: 5px; }
.stat-label { font-size: 14px; opacity: 0.9; }
.stat-icon { position: absolute; right: 20px; bottom: 20px; font-size: 48px; opacity: 0.3; transform: rotate(-15deg); }

/* 列表区 */
.toolbar { display: flex; justify-content: space-between; align-items: center; }
.left-filters { display: flex; align-items: center; }
.news-title { font-weight: bold; color: #303133; cursor: pointer; transition: color 0.2s; }
.news-title:hover { color: #409EFF; text-decoration: underline; }
.pagination { margin-top: 20px; display: flex; justify-content: flex-end; }

/* 编辑器模拟 */
.editor-toolbar { border: 1px solid #dcdfe6; border-bottom: none; padding: 5px 10px; background: #f5f7fa; border-radius: 4px 4px 0 0; }
.editor-area :deep(.el-textarea__inner) { border-radius: 0 0 4px 4px; }

/* 文章详情样式 */
.article-container { padding: 0 20px; }
.article-title { font-size: 24px; color: #303133; margin-bottom: 15px; text-align: center; }
.article-meta { display: flex; justify-content: center; gap: 20px; color: #909399; font-size: 13px; margin-bottom: 20px; align-items: center; }
.article-meta span { display: flex; align-items: center; gap: 5px; }
.article-content { font-size: 16px; line-height: 1.8; color: #303133; }
</style>