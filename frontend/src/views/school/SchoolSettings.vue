<template>
  <div class="page-container">
    <el-row :gutter="20">
      <!-- 左侧：个人简版卡片 -->
      <el-col :span="6">
        <el-card shadow="hover" class="profile-card">
          <div class="profile-header">
            <el-avatar :size="100" :src="user.avatar" class="avatar-hover" />
            <h3>{{ user.name }}</h3>
            <p class="role-tag">管理员</p>
          </div>
          <div class="profile-stats">
            <div class="stat-item">
              <div class="num">12</div>
              <div class="label">登录次数</div>
            </div>
            <div class="stat-item">
              <div class="num">56</div>
              <div class="label">操作日志</div>
            </div>
          </div>
          <el-divider />
          <div class="contact-info">
            <p><el-icon><Message /></el-icon> {{ user.email }}</p>
            <p><el-icon><Phone /></el-icon> {{ user.phone }}</p>
            <p><el-icon><Location /></el-icon> 甘肃·庆阳</p>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：详细配置 -->
      <el-col :span="18">
        <el-card shadow="never" class="setting-card">
          <el-tabs v-model="activeTab" class="custom-tabs">
            
            <!-- Tab 1: 基础信息 -->
            <el-tab-pane label="基础设置" name="base">
              <div class="tab-content">
                <h4 class="section-title">学校基本信息</h4>
                <el-form :model="schoolInfo" label-position="top">
                  <el-row :gutter="20">
                    <el-col :span="12">
                      <el-form-item label="学校名称">
                        <el-input v-model="schoolInfo.name" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="统一社会信用代码">
                        <el-input v-model="schoolInfo.code" disabled />
                      </el-form-item>
                    </el-col>
                  </el-row>
                  <el-form-item label="学校简介">
                    <el-input type="textarea" v-model="schoolInfo.desc" :rows="4" />
                  </el-form-item>
                  <el-form-item label="联系地址">
                    <el-input v-model="schoolInfo.addr" />
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" @click="saveBaseInfo" :loading="loading">更新基本信息</el-button>
                  </el-form-item>
                </el-form>
              </div>
            </el-tab-pane>

            <!-- Tab 2: 安全中心 -->
            <el-tab-pane label="安全中心" name="security">
              <div class="tab-content">
                <h4 class="section-title">账号安全</h4>
                <div class="security-item">
                  <div class="sec-left">
                    <span class="sec-label">账户密码</span>
                    <span class="sec-desc">当前密码强度：<span style="color:#67C23A">强</span></span>
                  </div>
                  <el-button link type="primary" @click="pwdVisible = true">修改</el-button>
                </div>
                <el-divider />
                <div class="security-item">
                  <div class="sec-left">
                    <span class="sec-label">密保手机</span>
                    <span class="sec-desc">已绑定：138****8888</span>
                  </div>
                  <el-button link type="primary">更换</el-button>
                </div>
                <el-divider />
                <div class="security-item">
                  <div class="sec-left">
                    <span class="sec-label">备用邮箱</span>
                    <span class="sec-desc">已绑定：admin@qyvtc.edu.cn</span>
                  </div>
                  <el-button link type="primary">更换</el-button>
                </div>

                <h4 class="section-title mt-30">最近登录记录</h4>
                <el-table :data="loginLogs" style="width: 100%">
                  <el-table-column prop="time" label="时间" />
                  <el-table-column prop="ip" label="IP地址" />
                  <el-table-column prop="location" label="地点" />
                  <el-table-column prop="device" label="设备" />
                </el-table>
              </div>
            </el-tab-pane>

            <!-- Tab 3: 通知设置 -->
            <el-tab-pane label="通知偏好" name="notify">
              <div class="tab-content">
                <el-table :data="notifySettings" :show-header="false">
                  <el-table-column prop="title" width="200">
                    <template #default="{row}"><b>{{row.title}}</b></template>
                  </el-table-column>
                  <el-table-column prop="desc" />
                  <el-table-column width="100">
                    <template #default="{row}">
                      <el-switch v-model="row.open" @change="handleNotifyChange(row)" />
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </el-tab-pane>

            <!-- Tab 4: 操作日志 -->
            <el-tab-pane label="系统审计日志" name="logs">
              <div class="tab-content">
                <div class="log-filter">
                  <el-date-picker v-model="logDate" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" size="small" />
                  <el-button type="primary" size="small" icon="Search" @click="filterLogs">查询</el-button>
                  <el-button type="default" size="small" icon="Download" @click="exportLogs">导出</el-button>
                </div>
                <el-timeline class="mt-20">
                  <el-timeline-item
                    v-for="(activity, index) in activities"
                    :key="index"
                    :type="activity.type"
                    :color="activity.color"
                    :timestamp="activity.timestamp"
                    placement="top"
                  >
                    <el-card class="log-card">
                      <h4>{{ activity.title }}</h4>
                      <p>{{ activity.content }}</p>
                      <p class="log-user">操作人：{{ activity.user }}</p>
                    </el-card>
                  </el-timeline-item>
                </el-timeline>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>

    <!-- 修改密码弹窗 -->
    <el-dialog v-model="pwdVisible" title="修改登录密码" width="400px">
      <el-form :model="pwdForm" label-position="top">
        <el-form-item label="旧密码">
          <el-input v-model="pwdForm.old" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="pwdForm.new" type="password" show-password />
          <el-progress :percentage="pwdStrength" :status="pwdStrength > 80 ? 'success' : 'warning'" :show-text="false" style="margin-top:5px" />
          <span style="font-size:12px; color:#999">密码强度</span>
        </el-form-item>
        <el-form-item label="确认新密码">
          <el-input v-model="pwdForm.confirm" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pwdVisible = false">取消</el-button>
        <el-button type="primary" @click="savePwd">确认修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref, computed, watch } from 'vue'
import { Message, Phone, Location, Search, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('base')
const loading = ref(false)
const pwdVisible = ref(false)
const logDate = ref([])

// 用户信息
const user = reactive({
  name: '教务管理员',
  avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
  email: 'admin@qyvtc.edu.cn',
  phone: '13800138000'
})

// 学校信息
const schoolInfo = reactive({
  name: '庆阳XXXX学院',
  code: '12620000438002938A',
  desc: '庆阳XXXX学院是经甘肃省人民政府批准、教育部备案的公办全日制普通高等职业院校。',
  addr: '甘肃省庆阳市西峰区长庆大道'
})

// 登录日志
const loginLogs = [
  { time: '2024-06-18 09:00:21', ip: '192.168.1.10', location: '甘肃·庆阳', device: 'Chrome / Windows 10' },
  { time: '2024-06-17 14:23:05', ip: '192.168.1.10', location: '甘肃·庆阳', device: 'Chrome / Windows 10' },
  { time: '2024-06-16 08:55:12', ip: '114.255.x.x', location: '甘肃·兰州', device: 'Safari / iPhone 13' },
]

// 通知设置
const notifySettings = reactive([
  { title: '待办任务通知', desc: '当有新的企业入驻申请或待办事项时通知我', open: true },
  { title: '系统消息', desc: '系统升级维护、功能更新通知', open: true },
  { title: '异常告警', desc: '学生实习考勤异常、周报逾期提醒', open: false },
])

// 操作日志
const activities = ref([
  { content: '审核通过了“东数西算云创科技”的入驻申请', timestamp: '2024-06-18', type: 'primary', user: 'admin', title: '企业审核' },
  { content: '发布了《2024年春季学期工学交替实施方案》', timestamp: '2024-06-15', color: '#0bbd87', user: 'admin', title: '内容发布' },
  { content: '导出了“大数据技术”专业 2021 级学生花名册', timestamp: '2024-06-10', user: 'teacher_li', title: '数据导出' },
])

// 密码表单
const pwdForm = reactive({ old: '', new: '', confirm: '' })

// 密码强度计算
const pwdStrength = computed(() => {
  const val = pwdForm.new
  let score = 0
  if (val.length > 6) score += 30
  if (/[A-Z]/.test(val)) score += 30
  if (/[0-9]/.test(val)) score += 40
  return score
})

// --- 逻辑方法 ---

const saveBaseInfo = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success('学校信息已更新')
  }, 800)
}

const handleNotifyChange = (row) => {
  ElMessage.info(`${row.title} 已${row.open ? '开启' : '关闭'}`)
}

const savePwd = () => {
  if (pwdForm.new !== pwdForm.confirm) return ElMessage.error('两次密码不一致')
  if (pwdStrength.value < 60) return ElMessage.warning('密码强度太低')
  
  pwdVisible.value = false
  ElMessage.success('密码修改成功，请重新登录')
}

const filterLogs = () => {
  ElMessage.success('日志筛选完成')
}

const exportLogs = () => {
  ElMessage.success('系统审计日志导出中...')
}
</script>

<style scoped>
.page-container { padding: 20px; }

/* 左侧个人卡片 */
.profile-card { text-align: center; height: 100%; }
.avatar-hover { transition: transform 0.3s; cursor: pointer; border: 4px solid #fff; box-shadow: 0 2px 12px rgba(0,0,0,0.1); }
.avatar-hover:hover { transform: rotate(360deg); }
.profile-header h3 { margin: 10px 0 5px; }
.role-tag { background: #ecf5ff; color: #409EFF; padding: 2px 10px; border-radius: 10px; font-size: 12px; display: inline-block; }
.profile-stats { display: flex; justify-content: space-around; margin: 20px 0; }
.stat-item .num { font-size: 20px; font-weight: bold; color: #303133; }
.stat-item .label { font-size: 12px; color: #909399; }
.contact-info p { display: flex; align-items: center; gap: 10px; justify-content: center; color: #606266; font-size: 13px; margin: 10px 0; }

/* 右侧设置区 */
.setting-card { min-height: 600px; }
.tab-content { padding: 0 20px; }
.section-title { font-size: 16px; font-weight: bold; margin-bottom: 20px; border-left: 4px solid #409EFF; padding-left: 10px; }

/* 安全中心 */
.security-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; }
.sec-label { display: block; font-weight: bold; color: #303133; }
.sec-desc { font-size: 13px; color: #909399; margin-top: 5px; }
.mt-30 { margin-top: 30px; }

/* 日志 */
.log-filter { display: flex; gap: 10px; align-items: center; margin-bottom: 20px; }
.mt-20 { margin-top: 20px; }
.log-card { padding: 10px; }
.log-card h4 { margin: 0 0 5px 0; font-size: 15px; }
.log-card p { margin: 0; color: #666; font-size: 13px; }
.log-user { font-size: 12px; color: #909399; margin-top: 5px; text-align: right; }
</style>