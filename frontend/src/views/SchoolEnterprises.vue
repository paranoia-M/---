<template>
  <div class="enterprise-container">
    <!-- 顶部统计 Banner -->
    <el-row :gutter="20" class="mb-20">
      <el-col :span="24">
        <div class="header-banner">
          <div class="icon-wrapper">
            <el-icon><OfficeBuilding /></el-icon>
          </div>
          <div class="banner-text">
            <h3>已入驻合作企业库</h3>
            <p>庆阳数字经济产业集群 · 校企深度融合</p>
          </div>
          <div class="banner-num">
            <span>{{ entList.length }}</span> 家
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 企业列表 -->
    <el-card shadow="never">
      <template #header>
        <div class="flex-between">
          <span>企业名录管理</span>
          <div class="right-tools">
            <el-input v-model="search" placeholder="搜索企业..." prefix-icon="Search" style="width: 200px; margin-right: 10px" size="small" />
            <el-button type="primary" link @click="fetchEnterprises">刷新列表</el-button>
          </div>
        </div>
      </template>

      <el-table :data="filteredList" style="width: 100%" size="large" stripe>
        <el-table-column label="企业名称" min-width="250">
          <template #default="scope">
            <div class="ent-info" @click="openDetail(scope.row)">
              <el-avatar shape="square" :size="40" :style="{background: getAvatarColor(scope.row.full_name)}">
                {{ scope.row.full_name.charAt(0) }}
              </el-avatar>
              <span class="ent-name">{{ scope.row.full_name }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="登录账号" prop="username" width="150" />
        
        <el-table-column label="认证状态" width="120">
          <template #default>
            <el-tag type="success" effect="dark"><el-icon><Check /></el-icon> 已认证</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="合作等级" width="180">
          <template #default>
             <el-rate v-model="rate" disabled text-color="#ff9900" />
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button link type="primary" @click="openDetail(scope.row)">查看详情</el-button>
            <el-popconfirm title="确定要移除该合作企业吗？" @confirm="handleDelete(scope.row)">
              <template #reference>
                <el-button link type="danger">移除合作</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- ✅ 新增：企业详情抽屉 -->
    <el-drawer v-model="drawerVisible" title="企业详细档案" size="40%">
      <div v-if="currentEnt" class="detail-container">
        <!-- 头部信息 -->
        <div class="detail-header">
          <el-avatar :size="80" shape="square" :src="currentEnt.logo || 'https://element-plus.org/images/element-plus-logo.svg'" />
          <div class="dh-text">
            <h2>{{ currentEnt.full_name }}</h2>
            <div class="tags">
              <el-tag size="small">云计算/大数据</el-tag>
              <el-tag size="small" type="warning">100-499人</el-tag>
            </div>
          </div>
        </div>

        <!-- 简介 -->
        <div class="section">
          <div class="sec-title">🏢 企业简介</div>
          <p class="desc-text">
            {{ currentEnt.desc || '该企业暂未填写详细简介。作为庆阳数字经济产业的核心成员，该企业在云算力、数据清洗领域拥有丰富经验，已接纳我校多批次实习生。' }}
          </p>
          <div class="addr-row">
            <el-icon><Location /></el-icon> 甘肃省庆阳市国家数据中心产业园
          </div>
        </div>

        <!-- 招聘岗位 -->
        <div class="section">
          <div class="sec-title">🔥 正在招聘的岗位</div>
          <div class="job-card" v-for="i in 2" :key="i">
            <div class="job-row">
              <span class="j-title">{{ i===1 ? 'Python数据分析师' : 'IDC运维工程师' }}</span>
              <span class="j-salary">4k-6k</span>
            </div>
            <div class="job-req">本科及以上 | 计算机相关专业 | 招5人</div>
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { OfficeBuilding, Search, Check, Location } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const entList = ref([])
const search = ref('')
const rate = ref(4.5)
const drawerVisible = ref(false)
const currentEnt = ref(null)

// 筛选
const filteredList = computed(() => {
  return entList.value.filter(item => item.full_name.includes(search.value))
})

const fetchEnterprises = async () => {
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/enterprises')
    entList.value = res.data
  } catch (error) {
    console.error(error)
  }
}

const handleDelete = async (row) => {
  try {
    await axios.delete(`http://127.0.0.1:8000/api/enterprises/${row.id}`)
    ElMessage.success('已移除该企业')
    fetchEnterprises()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

// 打开详情
const openDetail = (row) => {
  currentEnt.value = row
  drawerVisible.value = true
}

const getAvatarColor = (name) => {
  const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C']
  return colors[name.charCodeAt(0) % colors.length]
}

onMounted(() => fetchEnterprises())
</script>

<style scoped>
.enterprise-container { padding: 20px; }
.mb-20 { margin-bottom: 20px; }
.flex-between { display: flex; justify-content: space-between; align-items: center; }

/* 顶部 Banner 美化 */
.header-banner {
  background: linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%);
  border-radius: 8px;
  padding: 30px 40px;
  color: #fff;
  display: flex;
  align-items: center;
  position: relative;
  overflow: hidden;
}
.icon-wrapper {
  background: rgba(255,255,255,0.2);
  width: 60px; height: 60px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 32px;
  margin-right: 20px;
}
.banner-text h3 { margin: 0 0 5px 0; font-size: 24px; }
.banner-text p { margin: 0; opacity: 0.9; font-size: 14px; }
.banner-num { margin-left: auto; font-size: 48px; font-weight: bold; }
.banner-num span { font-size: 48px; }

/* 列表项 */
.ent-info { display: flex; align-items: center; gap: 12px; cursor: pointer; }
.ent-name { font-weight: bold; color: #303133; transition: color 0.3s; }
.ent-info:hover .ent-name { color: #409EFF; text-decoration: underline; }

/* 抽屉详情样式 */
.detail-header { display: flex; gap: 20px; margin-bottom: 30px; }
.dh-text h2 { margin: 0 0 10px 0; color: #303133; }
.tags { display: flex; gap: 8px; }

.section { margin-bottom: 30px; }
.sec-title { font-weight: bold; font-size: 16px; margin-bottom: 10px; border-left: 4px solid #409EFF; padding-left: 10px; }
.desc-text { font-size: 14px; color: #606266; line-height: 1.6; background: #f9fafc; padding: 15px; border-radius: 8px; }
.addr-row { margin-top: 10px; font-size: 13px; color: #909399; display: flex; align-items: center; gap: 5px; }

.job-card { border: 1px solid #ebeef5; border-radius: 6px; padding: 15px; margin-bottom: 10px; transition: all 0.3s; }
.job-card:hover { border-color: #409EFF; box-shadow: 0 2px 12px rgba(0,0,0,0.05); }
.job-row { display: flex; justify-content: space-between; margin-bottom: 5px; }
.j-title { font-weight: bold; color: #303133; }
.j-salary { color: #F56C6C; font-weight: bold; }
.job-req { font-size: 12px; color: #909399; }
</style>