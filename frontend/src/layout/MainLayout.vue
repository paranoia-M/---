<template>
  <el-container class="layout-container">
    <!-- 侧边栏 (Sidebar) -->
    <el-aside width="240px" class="aside-container">
      <!-- 1. 品牌 Logo 区 -->
      <div class="brand-box">
        <img
          src="https://element-plus.org/images/element-plus-logo.svg"
          alt="logo"
          class="brand-logo"
        />
        <span class="brand-text">庆阳工学平台</span>
      </div>

      <!-- 2. 菜单区 -->
      <el-scrollbar>
        <el-menu
          :default-active="activeMenu"
          class="el-menu-vertical"
          :background-color="variables.menuBg"
          :text-color="variables.menuText"
          :active-text-color="variables.menuActiveText"
          :unique-opened="true"
          router
        >
          <!-- 学校端菜单 -->
          <template v-if="role === 'school'">
            <div class="menu-category">教学管理中心</div>
            <el-menu-item index="/school">
              <el-icon><DataLine /></el-icon> <span>教学诊改驾驶舱</span>
            </el-menu-item>

            <el-sub-menu index="1">
              <template #title
                ><el-icon><User /></el-icon><span>人才与企业</span></template
              >
              <el-menu-item index="/school/students">人才库管理</el-menu-item>
              <el-menu-item index="/school/enterprises"
                >合作企业库</el-menu-item
              >
            </el-sub-menu>

            <el-menu-item index="/school/projects">
              <el-icon><Management /></el-icon> <span>实训项目管理</span>
            </el-menu-item>
            <el-menu-item index="/school/assessment">
              <el-icon><EditPen /></el-icon> <span>过程考核评价</span>
            </el-menu-item>

            <div class="menu-category">资源与服务</div>
            <el-menu-item index="/school/resources">
              <el-icon><VideoPlay /></el-icon> <span>数字课程资源</span>
            </el-menu-item>
            <el-menu-item index="/school/jobs-service">
              <el-icon><Suitcase /></el-icon> <span>就业服务中心</span>
            </el-menu-item>
            <el-menu-item index="/school/analytics">
              <el-icon><PieChart /></el-icon> <span>大数据分析</span>
            </el-menu-item>
            <el-menu-item index="/school/news">
              <el-icon><Bell /></el-icon> <span>政策资讯</span>
            </el-menu-item>
            <el-menu-item index="/school/settings">
              <el-icon><Setting /></el-icon> <span>系统设置</span>
            </el-menu-item>
          </template>

          <!-- 企业端菜单 -->
          <template v-if="role === 'enterprise'">
            <div class="menu-category">工作台</div>
            <el-menu-item index="/enterprise">
              <el-icon><Odometer /></el-icon> <span>企业驾驶舱</span>
            </el-menu-item>
            <el-menu-item index="/enterprise/resume">
              <el-icon><DocumentCopy /></el-icon> <span>简历收件箱</span>
            </el-menu-item>

            <div class="menu-category">人才招聘与培养</div>
            <el-menu-item index="/enterprise/jobs">
              <el-icon><Suitcase /></el-icon> <span>岗位需求管理</span>
            </el-menu-item>
            <el-menu-item index="/enterprise/projects">
              <el-icon><Connection /></el-icon> <span>校企合作项目</span>
            </el-menu-item>
            <el-menu-item index="/enterprise/interns">
              <el-icon><UserFilled /></el-icon> <span>在岗实习管理</span>
            </el-menu-item>
            <el-menu-item index="/enterprise/assessment">
              <el-icon><Edit /></el-icon> <span>技能考核评价</span>
            </el-menu-item>

            <div class="menu-category">数据与配置</div>
            <el-menu-item index="/enterprise/analytics">
              <el-icon><DataAnalysis /></el-icon> <span>人才数据看板</span>
            </el-menu-item>
            <el-menu-item index="/enterprise/profile">
              <el-icon><OfficeBuilding /></el-icon> <span>企业信息维护</span>
            </el-menu-item>
          </template>
        </el-menu>
      </el-scrollbar>
    </el-aside>

    <!-- 主内容区 -->
    <el-container>
      <!-- 3. 顶部 Header -->
      <el-header class="header-container">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ roleName }}</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentPathName }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-tooltip content="全屏模式" effect="dark" placement="bottom">
            <div class="icon-btn">
              <el-icon><FullScreen /></el-icon>
            </div>
          </el-tooltip>
          <el-tooltip content="消息通知" effect="dark" placement="bottom">
            <div class="icon-btn">
              <el-badge is-dot class="item"
                ><el-icon><Bell /></el-icon
              ></el-badge>
            </div>
          </el-tooltip>

          <!-- 用户下拉菜单 -->
          <el-dropdown trigger="click">
            <div class="user-box">
              <el-avatar :size="32" :src="avatarUrl" />
              <span class="username">{{ name }}</span>
              <el-icon><CaretBottom /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>个人中心</el-dropdown-item>
                <el-dropdown-item
                  divided
                  @click="handleLogout"
                  style="color: #f56c6c"
                  >退出登录</el-dropdown-item
                >
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 4. 内容渲染区 (带动画) -->
      <el-main class="main-box">
        <router-view v-slot="{ Component }">
          <transition name="fade-transform" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import {
  DataLine,
  User,
  OfficeBuilding,
  DocumentCopy,
  Management,
  EditPen,
  VideoPlay,
  Suitcase,
  PieChart,
  Bell,
  Setting,
  Odometer,
  Connection,
  UserFilled,
  Edit,
  DataAnalysis,
  FullScreen,
  CaretBottom,
} from "@element-plus/icons-vue";

const router = useRouter();
const route = useRoute();

// 样式变量
const variables = {
  menuBg: "#001529",
  menuText: "#bfcbd9",
  menuActiveText: "#ffffff",
};

const role = localStorage.getItem("role");
const name = localStorage.getItem("name");
const avatarUrl =
  "https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png";

const roleName = computed(() => (role === "school" ? "院校端" : "企业端"));
const currentPathName = computed(
  () => route.matched[route.matched.length - 1]?.name || "当前页面"
);
const activeMenu = computed(() => route.path);

const handleLogout = () => {
  localStorage.clear();
  router.push("/login");
};
</script>

<style scoped>
/* 布局容器 */
.layout-container {
  height: 100vh;
  display: flex;
}

/* 侧边栏样式优化 */
.aside-container {
  background-color: #001529;
  box-shadow: 2px 0 6px rgba(0, 21, 41, 0.35);
  z-index: 10;
  transition: width 0.3s;
  overflow-x: hidden; /* 隐藏横向滚动条 */
}

.brand-box {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #002140;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  gap: 10px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.12);
}
.brand-logo {
  width: 28px;
  height: 28px;
}

/* 菜单样式重写 */
.el-menu-vertical {
  border-right: none;
}

.menu-category {
  padding: 12px 20px 8px;
  font-size: 12px;
  color: #6a7885;
  font-weight: bold;
  letter-spacing: 1px;
}

:deep(.el-menu-item) {
  height: 50px;
  line-height: 50px;
  margin: 4px 10px; /* 增加间距 */
  border-radius: 4px; /* 圆角 */
}

:deep(.el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.08) !important;
}

/* 选中状态的高级感 */
:deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, #1890ff 0%, #096dd9 100%) !important;
  box-shadow: 0 2px 6px rgba(24, 144, 255, 0.4);
  font-weight: bold;
}

/* Header 样式 */
.header-container {
  background: #fff;
  height: 60px;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  z-index: 9;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.icon-btn {
  cursor: pointer;
  font-size: 20px;
  color: #5a5e66;
  transition: transform 0.2s;
}
.icon-btn:hover {
  transform: scale(1.1);
  color: #409eff;
}

.user-box {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 20px;
  transition: background 0.3s;
}
.user-box:hover {
  background: #f5f5f5;
}
.username {
  margin: 0 8px;
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

/* 内容区背景 */
.main-box {
  background-color: #f0f2f5;
  padding: 0; /* 由子页面自己控制 padding */
  overflow-x: hidden;
}

/* 页面切换动画 (淡入淡出 + 缩放) */
.fade-transform-leave-active,
.fade-transform-enter-active {
  transition: all 0.4s cubic-bezier(0.55, 0, 0.1, 1);
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
</style>