import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import MainLayout from '../layout/MainLayout.vue'
import SchoolHome from '../views/SchoolHome.vue'
import EnterpriseHome from '../views/EnterpriseHome.vue'
import TalentPool from '../views/TalentPool.vue'
import SchoolEnterprises from '../views/SchoolEnterprises.vue'
import EnterpriseResume from '../views/EnterpriseResume.vue'
import SchoolProjects from '../views/school/SchoolProjects.vue'
import SchoolAssessment from '../views/school/SchoolAssessment.vue'
import SchoolResources from '../views/school/SchoolResources.vue'
import SchoolJobs from '../views/school/SchoolJobs.vue'
import SchoolAnalytics from '../views/school/SchoolAnalytics.vue'
import SchoolNews from '../views/school/SchoolNews.vue'
import SchoolSettings from '../views/school/SchoolSettings.vue'
import EnterpriseJobs from '../views/enterprise/EnterpriseJobs.vue'
import EnterpriseProjects from '../views/enterprise/EnterpriseProjects.vue'
import EnterpriseInterns from '../views/enterprise/EnterpriseInterns.vue'
import EnterpriseAssessment from '../views/enterprise/EnterpriseAssessment.vue'
import EnterpriseAnalytics from '../views/enterprise/EnterpriseAnalytics.vue'
import EnterpriseProfile from '../views/enterprise/EnterpriseProfile.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    
    // --- 学校端路由组 ---
    {
      path: '/school',
      component: MainLayout,
      meta: { role: 'school' },
       children: [
        { path: '', component: SchoolHome },
        { path: 'students', component: TalentPool },
        { path: 'enterprises', component: SchoolEnterprises },
        // 新增的7个路由
        { path: 'projects', component: SchoolProjects },
        { path: 'assessment', component: SchoolAssessment },
        { path: 'resources', component: SchoolResources },
        { path: 'jobs-service', component: SchoolJobs },
        { path: 'analytics', component: SchoolAnalytics },
        { path: 'news', component: SchoolNews },
        { path: 'settings', component: SchoolSettings },
      ]
    },
    
    // --- 企业端路由组 ---
    {
      path: '/enterprise',
      component: MainLayout,
      meta: { role: 'enterprise' },
       children: [
        { path: '', component: EnterpriseHome },
        { path: 'resume', component: EnterpriseResume },
        // 新增的6个路由
        { path: 'jobs', component: EnterpriseJobs },
        { path: 'projects', component: EnterpriseProjects },
        { path: 'interns', component: EnterpriseInterns },
        { path: 'assessment', component: EnterpriseAssessment },
        { path: 'analytics', component: EnterpriseAnalytics },
        { path: 'profile', component: EnterpriseProfile },
      ]
    }
  ]
})

// 全局路由守卫 (权限控制)
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const userRole = localStorage.getItem('role')

  if (to.path === '/login') {
    next()
  } else {
    if (!token) {
      // 没登录，去登录页
      next('/login')
    } else {
      // 登录了，检查权限
      if (to.meta.role && to.meta.role !== userRole) {
        // 权限不符
        if (userRole === 'school') next('/school')
        else if (userRole === 'enterprise') next('/enterprise')
        else next('/login')
      } else {
        next()
      }
    }
  }
})

export default router