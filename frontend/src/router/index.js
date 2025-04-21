import Vue from 'vue'
import VueRouter from 'vue-router'
import store from '../store'

Vue.use(VueRouter)

// 路由配置
const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: {
      title: '首页',
      requiresAuth: true
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: {
      title: '登录',
      requiresAuth: false
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: {
      title: '注册',
      requiresAuth: false
    }
  },
  {
    path: '/upload',
    name: 'Upload',
    component: () => import('../views/Upload.vue'),
    meta: {
      title: '上传日志',
      requiresAuth: true
    }
  },
  {
    path: '/files',
    name: 'FileList',
    component: () => import('../views/FileList.vue'),
    meta: {
      title: '文件列表',
      requiresAuth: true
    }
  },
  {
    path: '/analysis/:id',
    name: 'Analysis',
    component: () => import('../views/Analysis.vue'),
    meta: {
      title: '日志分析',
      requiresAuth: true
    }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: {
      title: '态势感知',
      requiresAuth: true
    }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/Profile.vue'),
    meta: {
      title: '个人资料',
      requiresAuth: true
    }
  },
  {
    path: '*',
    redirect: '/'
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

// 全局导航守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 日志态势感知系统` : '日志态势感知系统'
  
  // 已登录用户尝试访问登录/注册页时重定向到首页
  const isLoginPage = to.path === '/login' || to.path === '/register'
  if (isLoginPage && store.state.authenticated) {
    return next({ path: '/' })
  }
  
  // 检查是否需要身份验证
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // 该路由需要身份验证，检查是否已登录
    if (!store.state.authenticated) {
      // 未登录，重定向到登录页
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    } else {
      // 已登录，继续导航
      next()
    }
  } else {
    // 不需要身份验证，继续
    next()
  }
})

export default router 