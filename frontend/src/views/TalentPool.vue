<template>
  <div class="talent-container">
    <!-- 顶部筛选栏 -->
    <el-card shadow="never" class="filter-card">
      <div class="toolbar">
        <!-- 左侧筛选 -->
        <el-form :inline="true" :model="filters" class="demo-form-inline">
          <el-form-item label="学生姓名">
            <el-input
              v-model="filters.name"
              placeholder="姓名/学号"
              prefix-icon="Search"
            />
          </el-form-item>
          <el-form-item label="专业方向">
            <el-select
              v-model="filters.major"
              placeholder="全部专业"
              style="width: 140px"
            >
              <el-option label="大数据技术" value="大数据技术" />
              <el-option label="云计算应用" value="云计算应用" />
              <el-option label="人工智能" value="人工智能" />
              <el-option label="软件工程" value="软件工程" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="resetFilter">重置</el-button>
          </el-form-item>
        </el-form>

        <!-- 右侧操作 -->
        <div class="right-actions">
          <el-button type="primary" icon="Plus" @click="openAddDialog"
            >新增学生</el-button
          >
          <el-button type="success" plain icon="Download">导出花名册</el-button>
        </div>
      </div>
    </el-card>

    <!-- 学生列表 -->
    <el-card shadow="never" class="table-card">
      <el-table :data="filteredList" style="width: 100%" size="large" stripe>
        <el-table-column label="学生信息" width="240">
          <template #default="scope">
            <div class="user-profile">
              <el-avatar :size="40" :src="scope.row.avatar" shape="square" />
              <div class="user-text">
                <div class="name">{{ scope.row.name }}</div>
                <div class="id">ID: {{ scope.row.id }}</div>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="major" label="专业" width="160" />

        <el-table-column label="核心技能 (Tags)" min-width="250">
          <template #default="scope">
            <el-tag
              v-for="tag in scope.row.skills"
              :key="tag"
              size="small"
              :type="getTagType(tag)"
              style="margin-right: 5px; margin-bottom: 5px"
            >
              {{ tag }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="gpa" label="综合绩点" width="120" sortable>
          <template #default="scope">
            <span style="font-weight: bold; color: #303133">{{
              scope.row.gpa
            }}</span>
          </template>
        </el-table-column>

        <el-table-column label="实习状态" width="120">
          <template #default="scope">
            <el-tag v-if="scope.row.isInterning" type="success" effect="dark"
              >实习中</el-tag
            >
            <el-tag v-else type="info" effect="plain">在校学习</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="240" fixed="right">
          <template #default="scope">
            <el-button
              link
              type="primary"
              size="small"
              @click="handleViewProfile(scope.row)"
              >查看档案</el-button
            >
            <el-button
              link
              type="warning"
              size="small"
              @click="handleRecommend(scope.row)"
              >推荐就业</el-button
            >
            <el-popconfirm
              title="确定删除该学生档案吗？"
              @confirm="handleDelete(scope.$index)"
            >
              <template #reference>
                <el-button link type="danger" size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          background
          layout="total, prev, pager, next"
          :total="filteredList.length"
          :page-size="10"
        />
      </div>
    </el-card>

    <!-- 弹窗：新增学生 -->
    <el-dialog v-model="addDialogVisible" title="录入新学生档案" width="500px">
      <el-form :model="addForm" label-width="80px">
        <el-form-item label="学生姓名">
          <el-input v-model="addForm.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="所属专业">
          <el-select
            v-model="addForm.major"
            placeholder="请选择专业"
            style="width: 100%"
          >
            <el-option label="大数据技术" value="大数据技术" />
            <el-option label="云计算应用" value="云计算应用" />
            <el-option label="人工智能" value="人工智能" />
            <el-option label="软件工程" value="软件工程" />
            <el-option label="网络安全" value="网络安全" />
          </el-select>
        </el-form-item>
        <el-form-item label="核心技能">
          <el-select
            v-model="addForm.skills"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="请输入技能标签 (如Python)"
            style="width: 100%"
          >
            <el-option label="Python" value="Python" />
            <el-option label="Java" value="Java" />
            <el-option label="Linux" value="Linux" />
            <el-option label="SQL" value="SQL" />
            <el-option label="Vue" value="Vue" />
          </el-select>
        </el-form-item>
        <el-form-item label="平均绩点">
          <el-input-number
            v-model="addForm.gpa"
            :min="0"
            :max="4.0"
            :step="0.1"
          />
        </el-form-item>
        <el-form-item label="当前状态">
          <el-radio-group v-model="addForm.isInterning">
            <el-radio :label="false">在校学习</el-radio>
            <el-radio :label="true">实习中</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAdd">确认录入</el-button>
      </template>
    </el-dialog>

    <!-- 抽屉：查看档案 (保持原有) -->
    <el-drawer v-model="drawerVisible" title="学生电子档案" size="40%">
      <div v-if="currentUser" class="profile-detail">
        <div class="profile-header">
          <el-avatar :size="80" :src="currentUser.avatar" />
          <h2>{{ currentUser.name }}</h2>
          <p>{{ currentUser.major }} | 2021级</p>
        </div>
        <el-descriptions title="基础信息" :column="2" border class="mt-20">
          <el-descriptions-item label="学号">{{
            currentUser.id
          }}</el-descriptions-item>
          <el-descriptions-item label="绩点"
            >{{ currentUser.gpa }} / 4.0</el-descriptions-item
          >
          <el-descriptions-item label="籍贯">甘肃庆阳</el-descriptions-item>
        </el-descriptions>
        <h3 class="mt-20">工学交替时间轴</h3>
        <el-timeline style="margin-top: 20px">
          <el-timeline-item timestamp="2023/09/01" placement="top"
            >入学报到</el-timeline-item
          >
        </el-timeline>
      </div>
    </el-drawer>

    <!-- 弹窗：推荐就业 (保持原有) -->
    <el-dialog v-model="recDialogVisible" title="推荐岗位匹配" width="500px">
      <p>
        正在为 <b>{{ currentUser?.name }}</b> 匹配岗位：
      </p>
      <el-select
        v-model="recJobId"
        placeholder="请选择岗位"
        style="width: 100%; margin-top: 10px"
      >
        <el-option label="Python数据清洗 (东数西算)" value="1" />
        <el-option label="IDC运维 (电信)" value="2" />
      </el-select>
      <template #footer>
        <el-button @click="recDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmRecommend">确认推荐</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from "vue";
import { Search, Plus, Download } from "@element-plus/icons-vue";
import { ElMessage, ElNotification } from "element-plus";

// --- 数据 ---
const filters = reactive({ name: "", major: "" });
const addDialogVisible = ref(false);
const drawerVisible = ref(false);
const recDialogVisible = ref(false);
const currentUser = ref(null);
const recJobId = ref("");

const addForm = reactive({
  name: "",
  major: "",
  skills: [],
  gpa: 3.0,
  isInterning: false,
});

const studentList = ref([
  {
    id: "202101",
    name: "张伟",
    avatar:
      "https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png",
    major: "大数据技术",
    skills: ["Python", "Hadoop", "MySQL"],
    gpa: "3.8",
    isInterning: false,
  },
  {
    id: "202102",
    name: "李娜",
    avatar:
      "https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png",
    major: "云计算应用",
    skills: ["Linux", "Docker", "K8s"],
    gpa: "3.6",
    isInterning: true,
  },
  {
    id: "202103",
    name: "王强",
    avatar:
      "https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png",
    major: "人工智能",
    skills: ["TensorFlow", "Python", "数学"],
    gpa: "3.9",
    isInterning: false,
  },
  {
    id: "202104",
    name: "赵敏",
    avatar:
      "https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png",
    major: "软件工程",
    skills: ["Java", "Spring", "Vue"],
    gpa: "3.5",
    isInterning: true,
  },
  {
    id: "202105",
    name: "孙悟空",
    avatar:
      "https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png",
    major: "网络安全",
    skills: ["渗透测试", "Web安全"],
    gpa: "4.0",
    isInterning: false,
  },
]);

// --- 逻辑 ---

// 筛选
const filteredList = computed(() => {
  return studentList.value.filter((item) => {
    const nameMatch = item.name.includes(filters.name);
    const majorMatch = filters.major ? item.major === filters.major : true;
    return nameMatch && majorMatch;
  });
});

// 重置筛选
const resetFilter = () => {
  filters.name = "";
  filters.major = "";
};

// 打开新增弹窗
const openAddDialog = () => {
  // 重置表单
  addForm.name = "";
  addForm.major = "";
  addForm.skills = [];
  addForm.gpa = 3.0;
  addForm.isInterning = false;
  addDialogVisible.value = true;
};

// 提交新增
const submitAdd = () => {
  if (!addForm.name || !addForm.major)
    return ElMessage.warning("请填写完整信息");

  studentList.value.unshift({
    id: `2021${Math.floor(Math.random() * 900) + 100}`,
    name: addForm.name,
    avatar:
      "https://cube.elemecdn.com/9/c2/f0ee8a3c7c9638a54940382568c9dpng.png", // 默认头像
    major: addForm.major,
    skills: addForm.skills,
    gpa: addForm.gpa,
    isInterning: addForm.isInterning,
  });

  ElMessage.success("录入成功");
  addDialogVisible.value = false;
};

// 删除
const handleDelete = (index) => {
  studentList.value.splice(index, 1);
  ElMessage.success("已删除该学生档案");
};

// 辅助方法
const getTagType = (tag) => {
  if (["Python", "Java"].includes(tag)) return "";
  if (["Linux", "Docker"].includes(tag)) return "warning";
  return "info";
};

const handleViewProfile = (row) => {
  currentUser.value = row;
  drawerVisible.value = true;
};

const handleRecommend = (row) => {
  currentUser.value = row;
  recDialogVisible.value = true;
};

const confirmRecommend = () => {
  recDialogVisible.value = false;
  ElNotification({
    title: "推荐成功",
    message: `已推送简历至企业HR`,
    type: "success",
  });
};
</script>

<style scoped>
.talent-container {
  padding: 20px;
}
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.filter-card {
  margin-bottom: 20px;
}
.demo-form-inline {
  margin-bottom: 0;
}
.user-profile {
  display: flex;
  align-items: center;
  gap: 12px;
}
.user-text .name {
  font-weight: bold;
  font-size: 14px;
}
.user-text .id {
  font-size: 12px;
  color: #909399;
}
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
.mt-20 {
  margin-top: 20px;
}
.profile-header {
  text-align: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}
.profile-header h2 {
  margin: 10px 0 5px;
}
.profile-header p {
  color: #666;
  font-size: 14px;
  margin: 0;
}
</style>