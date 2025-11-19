<template>
  <div class="page-container">
    <el-card shadow="never" class="main-card">
      <template #header>
        <div class="card-header-row">
          <span class="main-title"><el-icon><OfficeBuilding /></el-icon> 企业主页信息维护</span>
          <el-tag type="success" effect="dark" round>当前状态：已认证</el-tag>
        </div>
      </template>

      <el-tabs v-model="activeTab" class="custom-tabs">
        
        <!-- Tab 1: 基础信息维护 -->
        <el-tab-pane label="企业基础档案" name="base">
          <div class="content-wrapper">
            <!-- 左侧：编辑表单 -->
            <div class="form-section">
              <div class="section-title">编辑信息</div>
              <el-form label-position="top" :model="info" :rules="rules" ref="infoForm" size="large">
                
                <!-- Logo 上传优化 -->
                <el-form-item label="企业Logo" class="logo-item">
                  <div class="logo-upload-container">
                    <div class="logo-preview">
                      <el-image :src="info.logo" fit="cover" class="logo-img" />
                    </div>
                    <div class="upload-actions">
                      <el-button type="primary" plain icon="Upload">上传新Logo</el-button>
                      <p class="tips">支持 JPG/PNG，建议尺寸 200x200px，最大 2MB</p>
                    </div>
                  </div>
                </el-form-item>

                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="企业全称" prop="name">
                      <el-input v-model="info.name" placeholder="需与营业执照一致" prefix-icon="OfficeBuilding" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="所属行业" prop="industry">
                      <el-select v-model="info.industry" style="width: 100%">
                        <el-option label="云计算/大数据" value="云计算/大数据" />
                        <el-option label="人工智能" value="人工智能" />
                        <el-option label="物联网" value="物联网" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                </el-row>

                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="企业规模">
                      <el-select v-model="info.scale" style="width: 100%">
                        <el-option label="0-20人" value="0-20人" />
                        <el-option label="20-99人" value="20-99人" />
                        <el-option label="100-499人" value="100-499人" />
                        <el-option label="500人以上" value="500人以上" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="联系地址">
                      <el-input v-model="info.addr" prefix-icon="Location" placeholder="企业办公所在地" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <el-form-item label="企业简介" prop="desc">
                  <el-input 
                    v-model="info.desc" 
                    type="textarea" 
                    :rows="6" 
                    maxlength="500"
                    show-word-limit
                    placeholder="请详细介绍企业主营业务、发展历程及人才培养计划..." 
                  />
                </el-form-item>

                <el-form-item style="margin-top: 30px;">
                  <el-button type="primary" @click="saveInfo" :loading="saving" class="save-btn">保存并同步</el-button>
                  <el-button @click="resetInfo" plain>重置修改</el-button>
                </el-form-item>
              </el-form>
            </div>

            <!-- 右侧：实时预览 -->
            <div class="preview-section">
              <div class="section-title">🏫 学校端展示效果预览</div>
              <div class="mobile-mockup">
                <div class="mockup-header">
                  <div class="camera"></div>
                </div>
                <div class="mockup-screen">
                  <!-- 模拟学校端看到的卡片 -->
                  <div class="profile-banner"></div>
                  <div class="profile-header">
                    <el-avatar :size="70" :src="info.logo" class="profile-avatar" />
                    <div class="profile-name">{{ info.name || '企业名称' }}</div>
                    <div class="profile-tags">
                      <span class="tag blue">{{ info.industry }}</span>
                      <span class="tag gray">{{ info.scale }}</span>
                    </div>
                  </div>
                  <div class="profile-body">
                    <div class="info-row">
                      <el-icon><Location /></el-icon> {{ info.addr || '暂无地址' }}
                    </div>
                    <div class="info-desc">
                      {{ info.desc || '暂无简介...' }}
                    </div>
                    <div class="mock-stats">
                      <div class="stat-item">
                        <b>12</b><span>在岗</span>
                      </div>
                      <div class="stat-item">
                        <b>5</b><span>岗位</span>
                      </div>
                      <div class="stat-item">
                        <b>4.9</b><span>评分</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- Tab 2: 资质与认证 -->
        <el-tab-pane label="资质与认证" name="cert">
          <div class="cert-container">
            <el-alert title="请上传最新的营业执照与校企合作协议，审核通过后将获得“认证企业”标识" type="info" show-icon :closable="false" class="mb-20" />
            <el-row :gutter="40">
              <el-col :span="12">
                <div class="upload-box">
                  <div class="upload-title">营业执照 (副本)</div>
                  <el-upload drag action="#" multiple>
                    <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                    <div class="el-upload__text">拖拽上传或 <em>点击上传</em></div>
                  </el-upload>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="upload-box">
                  <div class="upload-title">校企合作协议书</div>
                  <el-upload drag action="#" multiple>
                    <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                    <div class="el-upload__text">支持 PDF / Word 格式</div>
                  </el-upload>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>

        <!-- Tab 3: 账号安全 -->
        <el-tab-pane label="账号安全设置" name="security">
          <div class="security-box">
             <el-form label-position="top">
                <el-form-item label="修改密码">
                  <el-input type="password" placeholder="新密码" show-password />
                </el-form-item>
                <el-button type="danger">更新密码</el-button>
             </el-form>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Location, UploadFilled, OfficeBuilding, Upload } from '@element-plus/icons-vue'

const activeTab = ref('base')
const saving = ref(false)
const infoForm = ref(null)

// 初始数据
const info = reactive({
  name: '东数西算云创科技',
  industry: '云计算/大数据',
  scale: '100-499人',
  logo: 'https://element-plus.org/images/element-plus-logo.svg',
  desc: '庆阳本地核心算力服务提供商，专注于IDC运维与数据清洗业务。已与庆阳职院建立深度合作关系，累计接纳实习生 200+ 人次。',
  addr: '甘肃省庆阳市国家数据中心产业园A座'
})

const rules = {
  name: [{ required: true, message: '请输入企业全称', trigger: 'blur' }],
  industry: [{ required: true, message: '请选择行业', trigger: 'change' }],
  desc: [{ required: true, message: '简介不能为空', trigger: 'blur' }]
}

const saveInfo = () => {
  infoForm.value.validate((valid) => {
    if (valid) {
      saving.value = true
      setTimeout(() => {
        saving.value = false
        ElMessage.success('保存成功！信息已同步至学校端')
      }, 800)
    }
  })
}

const resetInfo = () => {
  info.name = ''
  info.desc = ''
  info.addr = ''
}
</script>

<style scoped>
.page-container { padding: 20px; height: 100%; box-sizing: border-box; }
.main-card { min-height: 600px; }
.card-header-row { display: flex; justify-content: space-between; align-items: center; }
.main-title { font-size: 18px; font-weight: bold; display: flex; align-items: center; gap: 10px; }

/* 布局结构 */
.content-wrapper { display: flex; gap: 40px; padding-top: 20px; }
.form-section { flex: 3; padding-right: 20px; border-right: 1px dashed #e0e0e0; }
.preview-section { flex: 2; display: flex; flex-direction: column; align-items: center; }

.section-title { font-size: 16px; font-weight: bold; color: #303133; margin-bottom: 20px; border-left: 4px solid #409EFF; padding-left: 10px; }

/* Logo 上传美化 */
.logo-upload-container { display: flex; align-items: center; gap: 20px; background: #f5f7fa; padding: 15px; border-radius: 8px; }
.logo-preview { border: 1px solid #dcdfe6; border-radius: 6px; padding: 2px; background: #fff; }
.logo-img { width: 70px; height: 70px; display: block; border-radius: 4px; }
.upload-actions .tips { font-size: 12px; color: #909399; margin-top: 5px; }

/* 按钮样式 */
.save-btn { width: 150px; font-weight: bold; }

/* ---------------- 预览手机样式 (核心美化) ---------------- */
.mobile-mockup {
  width: 320px;
  height: 500px;
  background: #fff;
  border-radius: 30px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
  border: 8px solid #303133;
  position: relative;
  overflow: hidden;
  /* position: sticky; top: 20px; (如果内容长可开启) */
}
.mockup-header {
  height: 25px;
  background: #303133;
  display: flex;
  justify-content: center;
  align-items: center;
}
.camera { width: 60px; height: 10px; background: #1a1a1a; border-radius: 10px; }

.mockup-screen { height: 100%; background: #f5f7fa; overflow-y: auto; position: relative; }

/* 预览内容 */
.profile-banner { height: 100px; background: linear-gradient(135deg, #3a7bd5 0%, #3a6073 100%); }
.profile-header {
  margin-top: -35px;
  padding: 0 20px;
  text-align: center;
}
.profile-avatar { border: 3px solid #fff; box-shadow: 0 2px 10px rgba(0,0,0,0.1); background: #fff; }
.profile-name { font-size: 18px; font-weight: bold; margin-top: 10px; color: #303133; }
.profile-tags { margin-top: 8px; display: flex; justify-content: center; gap: 5px; }
.tag { padding: 2px 8px; border-radius: 10px; font-size: 10px; }
.tag.blue { background: #ecf5ff; color: #409EFF; }
.tag.gray { background: #f4f4f5; color: #909399; }

.profile-body { padding: 20px; }
.info-row { display: flex; align-items: center; gap: 5px; font-size: 12px; color: #606266; margin-bottom: 15px; justify-content: center; }
.info-desc { font-size: 13px; color: #666; line-height: 1.6; background: #fff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); text-align: left; min-height: 100px; }

.mock-stats { display: flex; justify-content: space-around; margin-top: 20px; background: #fff; padding: 15px; border-radius: 8px; }
.stat-item { display: flex; flex-direction: column; align-items: center; }
.stat-item b { font-size: 16px; color: #303133; }
.stat-item span { font-size: 10px; color: #909399; }

/* 资质上传美化 */
.cert-container { padding: 20px 40px; }
.upload-box { background: #f9fafc; border: 1px dashed #dcdfe6; border-radius: 8px; padding: 20px; text-align: center; transition: all 0.3s; }
.upload-box:hover { border-color: #409EFF; background: #fff; }
.upload-title { font-weight: bold; margin-bottom: 15px; color: #303133; }

.security-box { padding: 20px 40px; max-width: 400px; }
</style>