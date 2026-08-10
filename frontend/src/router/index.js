import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '../components/AppLayout.vue'
import {
  FolderOpened, WarningFilled, DataAnalysis, Collection, Document,
} from '@element-plus/icons-vue'

const routes = [
  {
    path: '/',
    name: 'Welcome',
    component: () => import('../views/Welcome.vue'),
  },
  {
    path: '/',
    component: AppLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
      },
      {
        path: 'detection',
        name: 'Detection',
        component: () => import('../views/Detection.vue'),
      },
      {
        path: 'tasks', name: 'Tasks', component: () => import('../views/Tasks.vue'),
      },
      {
        path: 'tasks/:id', name: 'TaskDetail', component: () => import('../views/TaskDetail.vue'),
      },
      {
        path: 'cases', name: 'Cases', component: () => import('../views/Cases.vue'),
      },
      {
        path: 'cases/:id', name: 'CaseDetail', component: () => import('../views/CaseDetail.vue'),
      },
      {
        path: 'risk-cases', redirect: '/cases',
      },
      {
        path: 'analytics', name: 'Analytics', component: () => import('../views/Analytics.vue'),
      },
      {
        path: 'case-center', name: 'CaseCenter', component: () => import('../views/PlaceholderPage.vue'),
        props: { title: '案例中心', description: '典型案例沉淀与检索功能将在后续阶段提供。', icon: Collection },
      },
      {
        path: 'reports', name: 'Reports', component: () => import('../views/PlaceholderPage.vue'),
        props: { title: '检测报告', description: '检测报告生成与管理功能将在后续阶段提供。', icon: Document },
      },
      {
        path: 'settings', name: 'Settings', component: () => import('../views/Settings.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫 — 不做严格校验，任何用户都可以访问
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    const user = localStorage.getItem('user')
    if (!user) {
      // 如果未登录，使用默认用户
      localStorage.setItem('user', JSON.stringify({ username: 'anonymous' }))
    }
  }
  next()
})

export default router
