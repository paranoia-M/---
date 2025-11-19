<template>
  <div class="dashboard-container">
    <!-- 1. 欢迎语 & 快捷统计 -->
    <div class="welcome-section">
      <div class="welcome-text">
        <h2>教学诊改驾驶舱</h2>
        <p>
          数字化赋能职业教育，今日共有
          <span class="highlight">5</span> 家企业发布了新需求
        </p>
      </div>
      <div class="quick-stats">
        <div class="stat-item">
          <div class="label">学生总数</div>
          <div class="value">1,203</div>
        </div>
        <div class="divider"></div>
        <div class="stat-item">
          <div class="label">合作企业</div>
          <div class="value">48</div>
        </div>
        <div class="divider"></div>
        <div class="stat-item">
          <div class="label">就业率</div>
          <div class="value green">98.2%</div>
        </div>
      </div>
    </div>

    <!-- 2. 核心指标卡片 (带微图表) -->
    <el-row :gutter="20" class="kpi-row">
      <el-col :span="6" v-for="(item, i) in kpis" :key="i">
        <el-card shadow="hover" class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-title">{{ item.title }}</span>
            <el-tag size="small" :type="item.type" effect="light">{{
              item.tag
            }}</el-tag>
          </div>
          <div class="kpi-body">
            <div class="num">{{ item.num }}</div>
            <div class="chart-placeholder" :class="'chart-' + i"></div>
            <!-- 模拟趋势图 -->
          </div>
          <div class="kpi-footer">
            <span>较上周</span>
            <span :class="item.trend > 0 ? 'up' : 'down'">
              {{ item.trend > 0 ? "+" : "" }}{{ item.trend }}%
            </span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="main-content">
      <!-- 左侧：需求大厅 (核心业务) -->
      <el-col :span="16">
        <el-card shadow="never" class="panel-card">
          <template #header>
            <div class="panel-header">
              <div class="header-left">
                <span class="icon-box"
                  ><el-icon><Monitor /></el-icon
                ></span>
                <span class="title">企业需求实时对接大厅</span>
              </div>
              <div class="header-right">
                <el-input
                  v-model="search"
                  placeholder="搜索岗位关键词..."
                  prefix-icon="Search"
                  size="small"
                  style="width: 200px; margin-right: 10px"
                />
                <el-button link type="primary" @click="fetchJobs">
                  <el-icon><Refresh /></el-icon> 刷新
                </el-button>
              </div>
            </div>
          </template>

          <!-- 现代化列表视图 -->
          <div class="job-list" v-loading="loading">
            <div v-for="job in jobList" :key="job.id" class="job-item">
              <div class="job-logo">
                <el-avatar
                  shape="square"
                  :size="48"
                  :style="{ background: getAvatarColor(job.enterprise_name) }"
                >
                  {{ job.enterprise_name.charAt(0) }}
                </el-avatar>
              </div>
              <div class="job-info">
                <div class="job-title-row">
                  <span class="job-title">{{ job.title }}</span>
                  <el-tag
                    v-if="job.count > 10"
                    type="danger"
                    size="small"
                    effect="dark"
                    >急聘</el-tag
                  >
                  <el-tag size="small" effect="plain"
                    >招 {{ job.count }} 人</el-tag
                  >
                </div>
                <div class="job-company">{{ job.enterprise_name }}</div>
                <div class="job-tags">
                  <span
                    v-for="tag in job.requirements.split(/[,，]/)"
                    :key="tag"
                    class="mini-tag"
                    >{{ tag }}</span
                  >
                </div>
              </div>
              <div class="job-action">
                <el-button type="primary" round @click="handleDocking(job)"
                  >立即对接</el-button
                >
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：辅助功能 -->
      <el-col :span="8">
        <!-- 雷达图 -->
        <el-card shadow="never" class="panel-card mb-20">
          <template #header>
            <div class="panel-header-small">
              <span
                ><el-icon><DataAnalysis /></el-icon> 技能匹配度分析</span
              >
            </div>
          </template>
          <div id="radarChart" style="height: 280px"></div>
        </el-card>

        <!-- 待办事项 -->
        <el-card shadow="never" class="panel-card">
          <template #header>
            <div class="panel-header-small">
              <span
                ><el-icon><Bell /></el-icon> 待办提醒</span
              >
              <el-tag type="danger" round size="small">3</el-tag>
            </div>
          </template>
          <ul class="todo-list">
            <li>
              <span class="dot red"></span>
              <span class="text">审核“庆阳云创”的入驻申请</span>
              <el-button link size="small">去处理</el-button>
            </li>
            <li>
              <span class="dot orange"></span>
              <span class="text">确认“IDC运维”项目实训名单</span>
              <el-button link size="small">去处理</el-button>
            </li>
            <li>
              <span class="dot blue"></span>
              <span class="text">发布下周招聘会通知</span>
              <el-button link size="small">去发布</el-button>
            </li>
          </ul>
        </el-card>
      </el-col>
    </el-row>

    <!-- 对接弹窗 (保持原有逻辑) -->
    <el-dialog v-model="dialogVisible" title="人才精准推送" width="600px">
      <div class="dialog-header-info">
        <p>
          正在对接：<b>{{ currentJob?.title }}</b>
        </p>
        <p style="font-size: 12px; color: #666; margin-top: 5px">
          企业方：{{ currentJob?.enterprise_name }}
        </p>
      </div>
      <el-table :data="mockStudents" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="major" label="专业" />
        <el-table-column label="匹配度">
          <template #default="scope">
            <el-progress
              :percentage="scope.row.match"
              :status="scope.row.match > 90 ? 'success' : ''"
            />
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmPush" :loading="pushing"
          >确认推送简历</el-button
        >
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from "vue";
import axios from "axios";
import * as echarts from "echarts";
import {
  Monitor,
  Search,
  Refresh,
  DataAnalysis,
  Bell,
} from "@element-plus/icons-vue";
import { ElMessage, ElNotification } from "element-plus";

// --- 数据 ---
const loading = ref(false);
const search = ref("");
const jobList = ref([]);

const kpis = [
  {
    title: "本月新增岗位",
    num: "156",
    tag: "月度",
    type: "primary",
    trend: 12.5,
  },
  { title: "简历投递量", num: "892", tag: "周", type: "success", trend: 5.2 },
  { title: "面试邀约数", num: "340", tag: "周", type: "warning", trend: -2.1 },
  { title: "成功入职", num: "45", tag: "日", type: "danger", trend: 8.4 },
];

// 弹窗相关
const dialogVisible = ref(false);
const pushing = ref(false);
const currentJob = ref(null);
const selectedStudents = ref([]);
const mockStudents = [
  { name: "张伟", major: "大数据技术", match: 95 },
  { name: "李娜", major: "云计算应用", match: 92 },
  { name: "王强", major: "人工智能", match: 88 },
  { name: "赵敏", major: "软件工程", match: 85 },
  { name: "孙悟空", major: "网络安全", match: 80 },
];

// --- 逻辑 ---

const fetchJobs = async () => {
  loading.value = true;
  try {
    const res = await axios.get("http://127.0.0.1:8000/api/jobs");
    jobList.value = res.data;
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const handleDocking = (row) => {
  currentJob.value = row;
  dialogVisible.value = true;
};

const handleSelectionChange = (val) => (selectedStudents.value = val);

const confirmPush = async () => {
  if (selectedStudents.value.length === 0)
    return ElMessage.warning("请选择学生");
  pushing.value = true;
  try {
    for (const s of selectedStudents.value) {
      await axios.post("http://127.0.0.1:8000/api/applications", {
        student_name: s.name,
        major: s.major,
        job_title: currentJob.value.title,
        enterprise_name: currentJob.value.enterprise_name,
      });
    }
    ElNotification({
      title: "推送成功",
      message: `已将 ${selectedStudents.value.length} 份简历发送给企业`,
      type: "success",
    });
    dialogVisible.value = false;
  } catch (e) {
    ElMessage.error("操作失败");
  } finally {
    pushing.value = false;
  }
};

const getAvatarColor = (name) => {
  const colors = ["#409EFF", "#67C23A", "#E6A23C", "#F56C6C", "#909399"];
  return colors[name.charCodeAt(0) % colors.length];
};

const initChart = () => {
  const chart = echarts.init(document.getElementById("radarChart"));
  chart.setOption({
    radar: {
      indicator: [
        { name: "Python", max: 100 },
        { name: "大数据", max: 100 },
        { name: "云计算", max: 100 },
        { name: "沟通", max: 100 },
        { name: "英语", max: 100 },
      ],
      radius: "65%",
    },
    series: [
      {
        type: "radar",
        data: [
          {
            value: [90, 85, 95, 70, 60],
            name: "企业需求",
            itemStyle: { color: "#67C23A" },
          },
          {
            value: [80, 75, 70, 85, 70],
            name: "学生能力",
            itemStyle: { color: "#409EFF" },
            areaStyle: { opacity: 0.3 },
          },
        ],
      },
    ],
  });
  window.addEventListener("resize", () => chart.resize());
};

onMounted(() => {
  fetchJobs();
  initChart();
});
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100%;
}

/* 1. 欢迎区 */
.welcome-section {
  background: #fff;
  padding: 20px 30px;
  border-radius: 12px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);
}
.welcome-text h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 22px;
}
.welcome-text p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}
.highlight {
  color: #409eff;
  font-weight: bold;
  font-size: 16px;
}

.quick-stats {
  display: flex;
  align-items: center;
  gap: 30px;
}
.stat-item {
  text-align: center;
}
.stat-item .label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}
.stat-item .value {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}
.stat-item .value.green {
  color: #67c23a;
}
.divider {
  width: 1px;
  height: 30px;
  background: #eee;
}

/* 2. KPI 卡片 */
.kpi-row {
  margin-bottom: 20px;
}
.kpi-card {
  border: none;
  border-radius: 12px;
  transition: transform 0.3s;
}
.kpi-card:hover {
  transform: translateY(-5px);
}
.kpi-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.kpi-title {
  color: #606266;
  font-size: 14px;
}
.kpi-body {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 15px;
}
.kpi-body .num {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
}
.chart-placeholder {
  width: 60px;
  height: 30px;
  background: #f5f7fa;
  border-radius: 4px;
}
/* 模拟图表颜色 */
.chart-0 {
  background: linear-gradient(to right, #fff, #ecf5ff);
  border-bottom: 2px solid #409eff;
}
.chart-1 {
  background: linear-gradient(to right, #fff, #f0f9eb);
  border-bottom: 2px solid #67c23a;
}
.chart-2 {
  background: linear-gradient(to right, #fff, #fdf6ec);
  border-bottom: 2px solid #e6a23c;
}
.chart-3 {
  background: linear-gradient(to right, #fff, #fef0f0);
  border-bottom: 2px solid #f56c6c;
}

.kpi-footer {
  border-top: 1px solid #f5f7fa;
  padding-top: 10px;
  font-size: 12px;
  color: #909399;
  display: flex;
  justify-content: space-between;
}
.up {
  color: #f56c6c;
}
.down {
  color: #67c23a;
}

/* 3. 面板卡片通用 */
.panel-card {
  border: none;
  border-radius: 12px;
}
.panel-header,
.panel-header-small {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}
.icon-box {
  background: #ecf5ff;
  color: #409eff;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.title {
  font-weight: bold;
  font-size: 16px;
  color: #303133;
}
.mb-20 {
  margin-bottom: 20px;
}

/* 4. 任务列表样式 (Job List) */
.job-item {
  display: flex;
  align-items: center;
  padding: 20px 0;
  border-bottom: 1px solid #f5f7fa;
  transition: background 0.3s;
}
.job-item:hover {
  background: #fafafa;
}
.job-item:last-child {
  border-bottom: none;
}
.job-logo {
  margin-right: 15px;
}
.job-info {
  flex: 1;
}
.job-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 5px;
}
.job-title {
  font-weight: bold;
  color: #303133;
  font-size: 15px;
}
.job-company {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}
.job-tags {
  display: flex;
  gap: 5px;
}
.mini-tag {
  background: #f4f4f5;
  color: #909399;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

/* 5. 待办列表 */
.todo-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.todo-list li {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px dashed #eee;
}
.todo-list li:last-child {
  border-bottom: none;
}
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 10px;
}
.dot.red {
  background: #f56c6c;
}
.dot.orange {
  background: #e6a23c;
}
.dot.blue {
  background: #409eff;
}
.text {
  flex: 1;
  font-size: 13px;
  color: #606266;
}

.dialog-header-info {
  background: #f0f9eb;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}
</style>