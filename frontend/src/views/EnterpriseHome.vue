<template>
  <div class="dashboard-container">
    <!-- 1. 顶部欢迎横幅 (视觉重心) -->
    <div class="welcome-banner">
      <div class="banner-content">
        <h2>早安，{{ currentEntName }} 👋</h2>
        <p>
          今天是 {{ today }}，您有
          <span class="highlight">{{ pendingCount }}</span>
          份简历待筛选，祝您招聘顺利！
        </p>
      </div>
      <div class="banner-bg"></div>
    </div>

    <!-- 2. 核心指标区 (悬浮在 Banner 之上) -->
    <el-row :gutter="20" class="kpi-row">
      <el-col :span="6" v-for="(kpi, i) in kpis" :key="i">
        <el-card shadow="hover" class="kpi-card">
          <div class="kpi-inner">
            <div class="icon-wrapper" :class="kpi.color">
              <el-icon><component :is="kpi.icon" /></el-icon>
            </div>
            <div class="text-wrapper">
              <div class="label">{{ kpi.title }}</div>
              <div class="value">{{ kpi.num }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 3. 主体内容区 (左宽右窄布局) -->
    <el-row :gutter="20" class="main-content">
      <!-- 左侧：业务核心 (简历处理) -->
      <el-col :span="17">
        <el-card shadow="never" class="main-card">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <span class="title-icon"></span>
                <span class="title-text">最新简历投递</span>
              </div>
              <el-button link type="primary" @click="fetchApplications">
                刷新数据 <el-icon class="el-icon--right"><Refresh /></el-icon>
              </el-button>
            </div>
          </template>

          <el-table
            :data="applicationList"
            style="width: 100%"
            v-loading="loading"
            size="large"
          >
            <el-table-column label="候选人信息" width="220">
              <template #default="scope">
                <div class="student-info">
                  <el-avatar
                    :size="44"
                    :src="getAvatar(scope.row.student_name)"
                    shape="square"
                    class="avatar-shadow"
                  />
                  <div class="info-text">
                    <div class="name">{{ scope.row.student_name }}</div>
                    <div class="major">{{ scope.row.major }}</div>
                  </div>
                </div>
              </template>
            </el-table-column>

            <el-table-column prop="job_title" label="投递岗位" />

            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <span
                  class="status-badge"
                  :class="getStatusClass(scope.row.status)"
                ></span>
                <span class="status-text">{{ scope.row.status }}</span>
              </template>
            </el-table-column>

            <el-table-column label="快捷操作" width="150" align="right">
              <template #default="scope">
                <el-button
                  v-if="scope.row.status === '待初筛'"
                  type="primary"
                  size="small"
                  class="action-btn"
                  @click="handleInterview(scope.row)"
                >
                  安排面试
                </el-button>
                <el-button v-else type="info" bg size="small" disabled
                  >已处理</el-button
                >
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 右侧：快捷工具 (发布岗位) -->
      <el-col :span="7">
        <el-card shadow="never" class="side-card">
          <template #header>
            <div class="card-header">
              <span class="title-text">⚡ 快速发布岗位</span>
            </div>
          </template>
          <div class="quick-form">
            <el-input
              v-model="jobForm.title"
              placeholder="岗位名称 (如: Java工程师)"
              class="mb-15"
              size="large"
            >
              <template #prefix
                ><el-icon><Suitcase /></el-icon
              ></template>
            </el-input>

            <el-input
              v-model="jobForm.requirements"
              type="textarea"
              :rows="4"
              placeholder="核心技能要求 (如: 熟悉Spring Boot, Vue3...)"
              class="mb-15"
            />

            <div class="form-row mb-20">
              <span class="label">招聘人数</span>
              <el-input-number
                v-model="jobForm.count"
                :min="1"
                style="width: 120px"
              />
            </div>

            <el-button
              type="primary"
              size="large"
              class="submit-btn"
              @click="submitJob"
            >
              立即发布并同步
            </el-button>
          </div>
        </el-card>

        <!-- 底部装饰卡片 (增加页面饱满度) -->
        <el-card shadow="hover" class="promo-card mt-20">
          <div class="promo-content">
            <h4>校企双选会即将开始</h4>
            <p>6月20日 庆阳体育馆专场</p>
            <el-button type="primary" link>查看详情 ></el-button>
          </div>
          <el-icon class="promo-icon"><Calendar /></el-icon>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from "vue";
import axios from "axios";
import { ElMessage, ElNotification } from "element-plus";
import {
  Message,
  Edit,
  Refresh,
  Suitcase,
  Calendar,
  User,
  Timer,
  Trophy,
  Document,
} from "@element-plus/icons-vue";

// --- 数据 ---
const loading = ref(false);
const applicationList = ref([]);
const currentEntName = localStorage.getItem("name") || "企业用户";
const jobForm = reactive({ title: "", requirements: "", count: 5 });
const today = new Date().toLocaleDateString();

// 动态 KPI
const pendingCount = computed(
  () => applicationList.value.filter((i) => i.status === "待初筛").length
);
const kpis = computed(() => [
  {
    title: "待处理简历",
    num: pendingCount.value,
    icon: "Document",
    color: "blue",
  },
  { title: "今日面试", num: 3, icon: "Timer", color: "cyan" },
  { title: "在岗实习生", num: 12, icon: "User", color: "purple" },
  { title: "发布岗位", num: 8, icon: "Trophy", color: "green" },
]);

// --- 逻辑方法 ---

// 1. 获取数据
const fetchApplications = async () => {
  loading.value = true;
  try {
    const res = await axios.get("http://127.0.0.1:8000/api/applications");
    // 取前 5 条展示，避免首页过长
    applicationList.value = res.data.slice(0, 5);
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

// 2. 操作面试
const handleInterview = async (row) => {
  try {
    await axios.put(`http://127.0.0.1:8000/api/applications/${row.id}`, {
      status: "待面试",
    });
    ElMessage.success("邀请已发送");
    fetchApplications();
  } catch (e) {
    ElMessage.error("操作失败");
  }
};

// 3. 发布岗位
const submitJob = async () => {
  if (!jobForm.title) return ElMessage.warning("请填写岗位名称");
  await axios.post("http://127.0.0.1:8000/api/jobs", {
    ...jobForm,
    enterprise_name: currentEntName,
  });
  ElNotification({ title: "发布成功", message: "岗位已上线", type: "success" });
  jobForm.title = "";
  jobForm.requirements = "";
};

// --- 辅助样式方法 ---
const getStatusClass = (status) => {
  if (status === "待初筛") return "status-warning";
  if (status === "待面试") return "status-success";
  return "status-info";
};

const getAvatar = (name) => {
  // 使用 UI Avatars 生成首字母头像
  return `https://ui-avatars.com/api/?name=${name}&background=random&color=fff&size=128`;
};

onMounted(() => fetchApplications());
</script>

<style scoped>
/* 全局布局 */
.dashboard-container {
  background-color: #f5f7fa; /* 高级灰底色 */
  min-height: 100vh;
  padding-bottom: 40px;
}

/* 1. 欢迎横幅 (科技感蓝紫渐变) */
.welcome-banner {
  background: linear-gradient(135deg, #3a7bd5 0%, #3a6073 100%);
  height: 180px;
  padding: 30px 40px;
  color: #fff;
  position: relative;
  overflow: hidden;
  border-radius: 0 0 20px 20px; /* 底部圆角 */
  margin: -20px -20px 0 -20px; /* 抵消 MainLayout 的 padding */
}
.welcome-banner h2 {
  margin: 0 0 10px 0;
  font-size: 26px;
  font-weight: 500;
}
.welcome-banner p {
  opacity: 0.9;
  font-size: 14px;
}
.highlight {
  font-weight: bold;
  font-size: 18px;
  color: #ffd04b;
}
/* 装饰背景圆圈 */
.banner-bg {
  position: absolute;
  top: -50%;
  right: -5%;
  width: 300px;
  height: 300px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
}

/* 2. KPI 卡片 (悬浮样式) */
.kpi-row {
  padding: 0 20px;
  margin-top: -50px; /* 向上重叠 Banner */
  position: relative;
  z-index: 10;
}
.kpi-card {
  border: none;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s;
}
.kpi-card:hover {
  transform: translateY(-5px);
}
.kpi-inner {
  display: flex;
  align-items: center;
  padding: 10px 0;
}
.icon-wrapper {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-right: 15px;
}
/* 图标颜色定义 */
.blue {
  background: #e6f7ff;
  color: #1890ff;
}
.cyan {
  background: #e6fffb;
  color: #13c2c2;
}
.purple {
  background: #f9f0ff;
  color: #722ed1;
}
.green {
  background: #f6ffed;
  color: #52c41a;
}

.text-wrapper .label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}
.text-wrapper .value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

/* 3. 主内容区 */
.main-content {
  padding: 0 20px;
  margin-top: 25px;
}

.main-card,
.side-card,
.promo-card {
  border: none;
  border-radius: 12px; /* 圆角更圆润 */
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);
}

/* 卡片头部通用 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 0;
}
.header-left {
  display: flex;
  align-items: center;
}
.title-icon {
  width: 4px;
  height: 18px;
  background: #409eff;
  border-radius: 2px;
  margin-right: 10px;
}
.title-text {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

/* 列表样式 */
.student-info {
  display: flex;
  align-items: center;
  gap: 12px;
}
.avatar-shadow {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
.info-text .name {
  font-weight: bold;
  color: #303133;
  font-size: 14px;
}
.info-text .major {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.status-badge {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 6px;
}
.status-warning {
  background: #e6a23c;
  box-shadow: 0 0 4px #e6a23c;
}
.status-success {
  background: #67c23a;
  box-shadow: 0 0 4px #67c23a;
}
.status-info {
  background: #909399;
}
.status-text {
  font-size: 13px;
}

/* 侧边栏样式 */
.quick-form {
  padding: 10px 0;
}
.mb-15 {
  margin-bottom: 15px;
}
.mb-20 {
  margin-bottom: 20px;
}
.mt-20 {
  margin-top: 20px;
}

.form-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.form-row .label {
  font-size: 14px;
  color: #606266;
}
.submit-btn {
  width: 100%;
  border-radius: 8px;
  font-weight: bold;
  letter-spacing: 1px;
}

/* 推广卡片 */
.promo-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  position: relative;
  overflow: hidden;
}
.promo-content {
  position: relative;
  z-index: 2;
}
.promo-content h4 {
  margin: 0 0 5px 0;
  font-size: 16px;
}
.promo-content p {
  margin: 0 0 10px 0;
  font-size: 12px;
  opacity: 0.8;
}
.promo-content :deep(.el-button) {
  color: #fff;
  padding: 0;
}
.promo-icon {
  position: absolute;
  right: -10px;
  bottom: -10px;
  font-size: 80px;
  color: rgba(255, 255, 255, 0.15);
  transform: rotate(-15deg);
}
</style>