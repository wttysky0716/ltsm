import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import './assets/styles/main.css'

Vue.use(ElementUI, { size: 'medium' })

Vue.config.productionTip = false

// 添加请求拦截器，为每个请求添加token
import axios from 'axios'

// 创建axios实例
const http = axios.create({
  baseURL: '/api',
  timeout: 60000
})

// 请求拦截器
http.interceptors.request.use(
  config => {
    const token = store.state.token
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
http.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API Error:', error);
    
    // 只在有明确的401状态码时才登出
    if (error.response && error.response.status === 401) {
      console.log('认证失败，退出登录');
      store.dispatch('logout')
      
      // 只有在用户不在登录页时，才跳转到登录页
      if (router.currentRoute.path !== '/login') {
        router.push('/login')
      }
    }
    
    return Promise.reject(error)
  }
)

Vue.prototype.$http = http

// 设置默认语言为中文
Vue.prototype.$ELEMENT = { size: 'medium', zIndex: 3000 }

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app') 