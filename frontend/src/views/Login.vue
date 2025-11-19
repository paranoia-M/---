<template>
  <div class="login-wrapper">
    <div class="login-box">
      <!-- 左侧：宣传图区 -->
      <div class="login-left">
        <div class="left-content">
          <!-- ✅ 修改点：使用图标代替图片Logo，通用且美观 -->
          <div class="logo-box">
            <el-icon :size="48"><DataAnalysis /></el-icon>
          </div>

          <h2 class="app-title">庆阳职业教育<br />工学一体化平台</h2>
          <p class="app-desc">助力“东数西算”数字经济人才培养</p>
          <div class="glass-decoration"></div>
        </div>
      </div>

      <!-- 右侧：表单交互区 -->
      <div class="login-right">
        <!-- 场景 A: 登录界面 -->
        <div v-if="!isRegister" class="form-container fade-in">
          <h3 class="welcome-text">欢迎登录</h3>

          <el-tabs
            v-model="activeRole"
            class="role-tabs"
            @tab-click="handleTabClick"
          >
            <el-tab-pane label="院校入口" name="school"></el-tab-pane>
            <el-tab-pane label="企业入口" name="enterprise"></el-tab-pane>
          </el-tabs>

          <el-form size="large" class="login-form" @keyup.enter="handleLogin">
            <el-form-item>
              <el-input
                v-model="form.username"
                :prefix-icon="User"
                placeholder="请输入账号"
              />
            </el-form-item>
            <el-form-item>
              <el-input
                v-model="form.password"
                type="password"
                :prefix-icon="Lock"
                placeholder="请输入密码"
                show-password
              />
            </el-form-item>

            <el-button
              type="primary"
              :loading="loading"
              class="login-btn"
              @click="handleLogin"
              >立即登录</el-button
            >

            <div class="tips-container">
              <div v-if="activeRole === 'enterprise'" class="register-link">
                <span
                  >还没有账号？
                  <el-button link type="primary" @click="isRegister = true"
                    >企业入驻注册</el-button
                  ></span
                >
              </div>
              <div class="test-account">
                <span>测试账号：school / 123 &nbsp;|&nbsp; company / 123</span>
              </div>
            </div>
          </el-form>
        </div>

        <!-- 场景 B: 注册界面 -->
        <div v-else class="form-container fade-in">
          <h3 class="welcome-text">企业入驻申请</h3>
          <p class="sub-title">请填写真实企业信息以便院校审核对接</p>

          <el-form
            size="large"
            class="login-form"
            @keyup.enter="handleRegister"
          >
            <el-form-item>
              <el-input
                v-model="regForm.full_name"
                :prefix-icon="OfficeBuilding"
                placeholder="企业全称 (如: 陇东云算力科技)"
              />
            </el-form-item>
            <el-form-item>
              <el-input
                v-model="regForm.username"
                :prefix-icon="User"
                placeholder="设置登录账号"
              />
            </el-form-item>
            <el-form-item>
              <el-input
                v-model="regForm.password"
                type="password"
                :prefix-icon="Lock"
                placeholder="设置登录密码"
                show-password
              />
            </el-form-item>

            <el-button
              type="success"
              :loading="loading"
              class="login-btn"
              @click="handleRegister"
              >提交注册</el-button
            >

            <div class="tips-container">
              <span
                >已有账号？
                <el-button link type="primary" @click="isRegister = false"
                  >返回登录</el-button
                ></span
              >
            </div>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
// 引入 DataAnalysis 图标作为 Logo
import {
  User,
  Lock,
  OfficeBuilding,
  DataAnalysis,
} from "@element-plus/icons-vue";
import axios from "axios";
import { ElMessage } from "element-plus";

const router = useRouter();
const loading = ref(false);
const activeRole = ref("school");
const isRegister = ref(false);

const form = reactive({ username: "", password: "" });
const regForm = reactive({ username: "", password: "", full_name: "" });

const handleTabClick = () => {
  form.username = "";
  form.password = "";
};

const handleLogin = async () => {
  if (!form.username || !form.password)
    return ElMessage.warning("请输入完整的账号和密码");
  loading.value = true;
  try {
    const res = await axios.post("http://127.0.0.1:8000/api/login", form);
    const realRole = res.data.role;
    if (activeRole.value !== realRole) {
      ElMessage.error(
        `身份不匹配！该账号属于${
          realRole === "school" ? "【院校端】" : "【企业端】"
        }`
      );
      loading.value = false;
      return;
    }
    localStorage.setItem("token", res.data.access_token);
    localStorage.setItem("role", realRole);
    localStorage.setItem("name", res.data.name);
    ElMessage.success(`欢迎回来，${res.data.name}`);
    setTimeout(() => {
      if (realRole === "school") router.push("/school");
      else router.push("/enterprise");
    }, 800);
  } catch (error) {
    if (error.response && error.response.status === 401)
      ElMessage.error("账号或密码错误");
    else ElMessage.error("连接服务器失败，请确认后端已启动");
  } finally {
    loading.value = false;
  }
};

const handleRegister = async () => {
  if (!regForm.username || !regForm.password || !regForm.full_name)
    return ElMessage.warning("请填写完整信息");
  loading.value = true;
  try {
    await axios.post("http://127.0.0.1:8000/api/register", regForm);
    ElMessage.success("注册成功！请使用新账号登录");
    activeRole.value = "enterprise";
    form.username = regForm.username;
    form.password = regForm.password;
    isRegister.value = false;
  } catch (error) {
    const msg = error.response?.data?.detail || "注册失败";
    ElMessage.error(msg);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-wrapper {
  height: 100vh;
  width: 100vw;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
  background-size: cover;
}
.login-box {
  width: 900px;
  height: 520px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
  display: flex;
  overflow: hidden;
}
.login-left {
  width: 50%;
  background: linear-gradient(135deg, #3a7bd5 0%, #3a6073 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  position: relative;
}
.left-content {
  text-align: center;
  z-index: 2;
}

/* Logo 样式替换 */
.logo-box {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(5px);
}

.app-title {
  font-size: 28px;
  font-weight: bold;
  margin: 0;
  line-height: 1.4;
  letter-spacing: 2px;
}
.app-desc {
  margin-top: 15px;
  font-size: 14px;
  opacity: 0.8;
  letter-spacing: 1px;
}
.glass-decoration {
  position: absolute;
  bottom: -50px;
  left: -50px;
  width: 200px;
  height: 200px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
}
.login-right {
  width: 50%;
  padding: 40px 50px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background-color: #fff;
}
.welcome-text {
  font-size: 24px;
  color: #333;
  margin-bottom: 20px;
  font-weight: 600;
}
.sub-title {
  color: #999;
  margin-bottom: 25px;
  font-size: 14px;
  margin-top: -10px;
}
.role-tabs {
  margin-bottom: 20px;
}
:deep(.el-tabs__item) {
  font-size: 16px;
  color: #666;
}
:deep(.el-tabs__item.is-active) {
  color: #3a7bd5;
  font-weight: bold;
}
:deep(.el-tabs__active-bar) {
  background-color: #3a7bd5;
}
.login-btn {
  width: 100%;
  margin-top: 10px;
  font-weight: bold;
  letter-spacing: 2px;
  height: 40px;
  font-size: 16px;
  transition: all 0.3s;
}
.login-btn:hover {
  opacity: 0.9;
  transform: translateY(-2px);
}
.tips-container {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
}
.test-account {
  font-size: 12px;
  color: #ccc;
}
.fade-in {
  animation: fadeIn 0.4s ease-in-out;
}
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>