<template>
  <div class="page-container">
    <!-- 1. 顶部精选推荐轮播 -->
    <div class="featured-section mb-20">
      <el-carousel :interval="4000" type="card" height="200px">
        <el-carousel-item v-for="item in featuredList" :key="item.id">
          <div class="carousel-card" :style="{ backgroundImage: `url(${item.cover})` }">
            <div class="carousel-content">
              <el-tag type="danger" effect="dark">热门推荐</el-tag>
              <h3>{{ item.title }}</h3>
              <p>{{ item.desc }}</p>
              <el-button type="primary" size="small" icon="VideoPlay" @click="openPreview(item)">立即学习</el-button>
            </div>
          </div>
        </el-carousel-item>
      </el-carousel>
    </div>

    <el-row :gutter="20">
      <!-- 左侧：主要资源列表 -->
      <el-col :span="18">
        <el-card shadow="never" class="main-card">
          <template #header>
            <div class="toolbar">
              <el-tabs v-model="activeTab" @tab-click="handleFilter">
                <el-tab-pane label="全部资源" name="all" />
                <el-tab-pane label="企业内训视频" name="video" />
                <el-tab-pane label="实训指导手册" name="doc" />
                <el-tab-pane label="行业标准规范" name="standard" />
              </el-tabs>
              <div class="actions">
                <el-input v-model="searchKey" placeholder="搜索资源..." prefix-icon="Search" style="width: 200px" />
                <el-button type="primary" icon="Upload" class="ml-10" @click="uploadVisible = true">上传资源</el-button>
              </div>
            </div>
          </template>

          <!-- 资源列表 -->
          <div class="resource-grid" v-loading="loading">
            <el-card 
              v-for="item in filteredList" 
              :key="item.id" 
              class="resource-item" 
              :body-style="{ padding: '0px' }"
              shadow="hover"
            >
              <!-- 封面区 -->
              <div class="cover-wrapper" @click="openPreview(item)">
                <el-image :src="item.cover" fit="cover" class="cover-img" />
                <div class="duration-badge">{{ item.duration }}</div>
                <div class="hover-overlay">
                  <el-icon size="40"><VideoPlay v-if="item.type==='video'" /><Document v-else /></el-icon>
                </div>
              </div>
              
              <!-- 内容区 -->
              <div class="info-wrapper">
                <div class="res-title" :title="item.title">{{ item.title }}</div>
                <div class="res-meta">
                  <span class="author">
                    <el-avatar :size="20" :src="item.avatar" style="vertical-align: middle; margin-right: 5px;" />
                    {{ item.author }}
                  </span>
                  <el-rate v-model="item.rating" disabled size="small" text-color="#ff9900" />
                </div>
                <div class="res-footer">
                  <span class="views"><el-icon><View /></el-icon> {{ item.views }}</span>
                  <div class="footer-actions">
                    <el-button link type="primary" icon="Download"></el-button>
                    <el-button link type="warning" icon="Star"></el-button>
                  </div>
                </div>
              </div>
            </el-card>
          </div>
          
          <el-pagination background layout="prev, pager, next" :total="50" class="mt-20" style="justify-content: center" />
        </el-card>
      </el-col>

      <!-- 右侧：排行榜与标签 -->
      <el-col :span="6">
        <!-- 热门下载榜 -->
        <el-card shadow="hover" class="side-card mb-20">
          <template #header>
            <span class="side-title"><el-icon><Trophy /></el-icon> 本周下载热榜</span>
          </template>
          <ul class="rank-list">
            <li v-for="(item, index) in hotDownloads" :key="index">
              <span class="rank-num" :class="'top-'+(index+1)">{{ index + 1 }}</span>
              <div class="rank-info">
                <div class="rank-title">{{ item.title }}</div>
                <div class="rank-count">{{ item.count }}次下载</div>
              </div>
            </li>
          </ul>
        </el-card>

        <!-- 热门标签云 -->
        <el-card shadow="hover" class="side-card">
          <template #header>
            <span class="side-title"><el-icon><CollectionTag /></el-icon> 热门技术栈</span>
          </template>
          <div class="tag-cloud">
            <el-tag v-for="tag in tags" :key="tag" class="cloud-tag" :type="getRandomType()" effect="plain" round>
              {{ tag }}
            </el-tag>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 预览弹窗 -->
    <el-dialog v-model="previewVisible" :title="currentItem?.title" width="800px" destroy-on-close top="5vh">
      <div class="preview-player">
        <div v-if="currentItem?.type === 'video'" class="video-box">
          <div class="play-btn"><el-icon size="60"><VideoPlay /></el-icon></div>
          <p>模拟视频播放器加载中...</p>
        </div>
        <div v-else class="doc-box">
          <el-icon size="80" color="#909399"><Document /></el-icon>
          <p>文档预览组件加载中...</p>
          <el-button type="primary" plain>下载源文件</el-button>
        </div>
      </div>
      <div class="preview-info">
        <h4>课程简介</h4>
        <p>本课程由 {{ currentItem?.author }} 精心录制，涵盖了核心知识点。适合初学者入门及进阶学习。</p>
      </div>
    </el-dialog>

    <!-- 上传弹窗 -->
    <el-dialog v-model="uploadVisible" title="上传新资源" width="500px">
      <el-form label-position="top">
        <el-form-item label="资源标题">
          <el-input placeholder="请输入资源名称" />
        </el-form-item>
        <el-form-item label="资源类型">
          <el-radio-group>
            <el-radio label="视频">视频 MP4</el-radio>
            <el-radio label="文档">文档 PDF/Word</el-radio>
            <el-radio label="代码">代码包 ZIP</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="文件上传">
          <el-upload drag action="#" multiple>
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">拖拽文件到此处或 <em>点击上传</em></div>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadVisible = false">取消</el-button>
        <el-button type="primary" @click="uploadVisible = false; ElMessage.success('上传成功，等待审核')">开始上传</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { 
  VideoPlay, Document, Search, Upload, UploadFilled, View, 
  Star, Trophy, CollectionTag, Download 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// --- 数据 ---
const activeTab = ref('all')
const searchKey = ref('')
const loading = ref(false)
const previewVisible = ref(false)
const uploadVisible = ref(false)
const currentItem = ref(null)

// 轮播图数据
const featuredList = [
  { id: 101, title: '2024数字经济产业全景解析', desc: '深度解读东数西算核心战略与人才需求', cover: 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=1000&auto=format&fit=crop', type: 'video' },
  { id: 102, title: 'Python数据分析实战训练营', desc: '从零开始掌握 Pandas 与 NumPy', cover: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?q=80&w=1000&auto=format&fit=crop', type: 'video' },
  { id: 103, title: '企业级Linux运维手册', desc: '庆阳数据中心内部运维SOP', cover: 'https://images.unsplash.com/photo-1629654297299-c8506221ca97?q=80&w=1000&auto=format&fit=crop', type: 'doc' }
]

// 资源列表数据
const resources = ref([
  { id: 1, title: '华为云原生架构师实战课', type: 'video', category: '企业内训', author: '华为云大学', avatar: 'https://ui-avatars.com/api/?name=H&bg=c0392b&color=fff', views: 1203, rating: 5.0, date: '2023-11-01', duration: '45:20', cover: 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?q=80&w=500&auto=format&fit=crop' },
  { id: 2, title: 'Python大数据清洗手册(V2.0)', type: 'doc', category: '实训手册', author: '东数西算云创', avatar: 'https://ui-avatars.com/api/?name=D&bg=2980b9&color=fff', views: 856, rating: 4.5, date: '2023-10-20', duration: 'PDF', cover: 'https://images.unsplash.com/photo-1587620962725-abab7fe55159?q=80&w=500&auto=format&fit=crop' },
  { id: 3, title: 'Linux集群运维规范', type: 'doc', category: '行业标准', author: '电信数据中心', avatar: 'https://ui-avatars.com/api/?name=T&bg=27ae60&color=fff', views: 542, rating: 4.0, date: '2023-10-15', duration: 'DOCX', cover: 'https://images.unsplash.com/photo-1607799275518-d58665d67243?q=80&w=500&auto=format&fit=crop' },
  { id: 4, title: 'AI数据标注操作演示', type: 'video', category: '实训视频', author: '字节跳动', avatar: 'https://ui-avatars.com/api/?name=B&bg=8e44ad&color=fff', views: 2300, rating: 4.8, date: '2023-11-15', duration: '12:05', cover: 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=500&auto=format&fit=crop' },
  { id: 5, title: 'MySQL数据库优化指南', type: 'video', category: '技能提升', author: '数据库教研组', avatar: 'https://ui-avatars.com/api/?name=S&bg=e67e22&color=fff', views: 1560, rating: 4.7, date: '2023-12-01', duration: '30:00', cover: 'https://images.unsplash.com/photo-1504639725590-34d0984388bd?q=80&w=500&auto=format&fit=crop' },
  { id: 6, title: 'Web前端开发入门', type: 'video', category: '基础课程', author: '前端组', avatar: 'https://ui-avatars.com/api/?name=W&bg=16a085&color=fff', views: 3100, rating: 4.2, date: '2023-09-10', duration: '18:20', cover: 'https://images.unsplash.com/photo-1593720213428-28a5b9e94613?q=80&w=500&auto=format&fit=crop' }
])

const hotDownloads = [
  { title: '2024毕业生就业白皮书.pdf', count: 3420 },
  { title: 'Python环境搭建安装包.zip', count: 2890 },
  { title: 'Linux常用命令速查表.png', count: 2100 },
  { title: '数据结构与算法笔记.docx', count: 1850 },
  { title: 'Java面试题库大全.pdf', count: 1540 }
]

const tags = ['Python', 'Vue3', 'SpringBoot', 'Linux', 'Docker', 'Hadoop', 'MySQL', '数据清洗', '云计算', 'Redis']

// --- 逻辑 ---
const filteredList = computed(() => {
  return resources.value.filter(item => {
    const typeMatch = activeTab.value === 'all' 
      ? true 
      : activeTab.value === 'video' ? item.type === 'video' 
      : activeTab.value === 'doc' ? item.category === '实训手册'
      : item.category === '行业标准'
    const nameMatch = item.title.includes(searchKey.value)
    return typeMatch && nameMatch
  })
})

const handleFilter = () => {
  loading.value = true
  setTimeout(() => loading.value = false, 300)
}

const openPreview = (item) => {
  currentItem.value = item
  previewVisible.value = true
}

const getRandomType = () => {
  const types = ['', 'success', 'info', 'warning', 'danger']
  return types[Math.floor(Math.random() * types.length)]
}
</script>

<style scoped>
.page-container { padding: 20px; }
.mb-20 { margin-bottom: 20px; }
.mt-20 { margin-top: 20px; }
.ml-10 { margin-left: 10px; }

/* 轮播卡片 */
.carousel-card {
  height: 100%;
  background-size: cover;
  background-position: center;
  border-radius: 8px;
  position: relative;
  display: flex;
  align-items: center;
  padding-left: 50px;
}
.carousel-card::before {
  content: ''; position: absolute; top:0; left:0; width:100%; height:100%;
  background: linear-gradient(90deg, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0) 100%);
  border-radius: 8px;
}
.carousel-content { position: relative; z-index: 2; color: #fff; max-width: 500px; }
.carousel-content h3 { font-size: 24px; margin: 10px 0; }
.carousel-content p { opacity: 0.8; margin-bottom: 20px; }

/* 资源网格 */
.resource-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
}
.resource-item { border: none; border-radius: 8px; transition: all 0.3s; }
.resource-item:hover { transform: translateY(-4px); box-shadow: 0 12px 32px rgba(0,0,0,0.08); }

/* 封面样式 */
.cover-wrapper { position: relative; height: 140px; cursor: pointer; overflow: hidden; border-radius: 8px 8px 0 0; }
.cover-img { width: 100%; height: 100%; transition: transform 0.5s; }
.cover-wrapper:hover .cover-img { transform: scale(1.1); }
.duration-badge {
  position: absolute; bottom: 8px; right: 8px;
  background: rgba(0,0,0,0.7); color: #fff;
  padding: 2px 6px; border-radius: 4px; font-size: 11px;
}
.hover-overlay {
  position: absolute; top:0; left:0; width:100%; height:100%;
  background: rgba(0,0,0,0.3);
  display: flex; align-items: center; justify-content: center;
  opacity: 0; transition: opacity 0.3s; color: #fff;
}
.cover-wrapper:hover .hover-overlay { opacity: 1; }

/* 信息样式 */
.info-wrapper { padding: 12px; }
.res-title { font-weight: bold; font-size: 14px; margin-bottom: 8px; color: #303133; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.res-meta { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; font-size: 12px; color: #909399; }
.res-footer { display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #f5f5f5; padding-top: 10px; font-size: 12px; color: #909399; }
.footer-actions .el-button { padding: 0; margin-left: 10px; }

/* 侧边栏样式 */
.side-title { font-weight: bold; display: flex; align-items: center; gap: 8px; }
.rank-list { list-style: none; padding: 0; margin: 0; }
.rank-list li { display: flex; align-items: center; padding: 12px 0; border-bottom: 1px dashed #eee; }
.rank-num { width: 24px; height: 24px; background: #eee; color: #909399; border-radius: 4px; text-align: center; line-height: 24px; font-weight: bold; margin-right: 10px; font-size: 12px; }
.rank-num.top-1 { background: #f56c6c; color: #fff; }
.rank-num.top-2 { background: #e6a23c; color: #fff; }
.rank-num.top-3 { background: #409EFF; color: #fff; }
.rank-info { flex: 1; overflow: hidden; }
.rank-title { font-size: 13px; color: #303133; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.rank-count { font-size: 12px; color: #909399; margin-top: 2px; }

.tag-cloud { display: flex; flex-wrap: wrap; gap: 8px; }
.cloud-tag { cursor: pointer; transition: transform 0.2s; }
.cloud-tag:hover { transform: scale(1.1); }

/* 预览播放器 */
.preview-player { background: #000; height: 400px; display: flex; align-items: center; justify-content: center; color: #fff; margin-bottom: 20px; border-radius: 8px; }
.doc-box { background: #f2f2f2; width: 100%; height: 100%; color: #606266; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 20px; }
.preview-info { padding: 10px; background: #f9f9f9; border-radius: 4px; }
.preview-info h4 { margin: 0 0 10px 0; }
.preview-info p { font-size: 14px; color: #666; line-height: 1.6; }
</style>