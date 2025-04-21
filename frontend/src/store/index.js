import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    authenticated: false,
    token: null,
    user: null,
    logFiles: [],
    currentFile: null,
    analysisResults: null,
    loadingStatus: false
  },
  getters: {
    isAuthenticated: state => state.authenticated,
    currentUser: state => state.user,
    getToken: state => state.token,
    getLogFiles: state => state.logFiles,
    getCurrentFile: state => state.currentFile,
    getAnalysisResults: state => state.analysisResults,
    isLoading: state => state.loadingStatus
  },
  mutations: {
    setAuthenticated(state, authenticated) {
      state.authenticated = authenticated
    },
    setToken(state, token) {
      state.token = token
      localStorage.setItem('token', token)
    },
    setUser(state, user) {
      state.user = user
      localStorage.setItem('user', JSON.stringify(user))
    },
    setLogFiles(state, files) {
      state.logFiles = files
    },
    setCurrentFile(state, file) {
      state.currentFile = file
    },
    setAnalysisResults(state, results) {
      state.analysisResults = results
    },
    setLoadingStatus(state, status) {
      state.loadingStatus = status
    },
    clearUserData(state) {
      state.authenticated = false
      state.token = null
      state.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  },
  actions: {
    // 用户登录
    async login({ commit }, credentials) {
      commit('setLoadingStatus', true)
      try {
        const response = await Vue.prototype.$http.post('/auth/login', credentials)
        commit('setToken', response.access_token)
        commit('setUser', response.user)
        commit('setAuthenticated', true)
        commit('setLoadingStatus', false)
        return response
      } catch (error) {
        commit('setLoadingStatus', false)
        throw error
      }
    },
    
    // 用户注册
    async register({ commit }, userData) {
      commit('setLoadingStatus', true)
      try {
        const response = await Vue.prototype.$http.post('/auth/register', userData)
        commit('setToken', response.access_token)
        commit('setUser', response.user)
        commit('setAuthenticated', true)
        commit('setLoadingStatus', false)
        return response
      } catch (error) {
        commit('setLoadingStatus', false)
        throw error
      }
    },
    
    // 用户退出
    logout({ commit }) {
      commit('clearUserData')
    },
    
    // 获取日志文件列表
    async fetchLogFiles({ commit }) {
      commit('setLoadingStatus', true)
      try {
        const response = await Vue.prototype.$http.get('/logs/list')
        commit('setLogFiles', response.files)
        commit('setLoadingStatus', false)
        return response
      } catch (error) {
        commit('setLoadingStatus', false)
        throw error
      }
    },
    
    // 获取单个日志文件
    async fetchLogFile({ commit }, fileId) {
      commit('setLoadingStatus', true)
      try {
        const response = await Vue.prototype.$http.get(`/logs/${fileId}`)
        commit('setCurrentFile', response)
        commit('setLoadingStatus', false)
        return response
      } catch (error) {
        commit('setLoadingStatus', false)
        throw error
      }
    },
    
    // 上传日志文件
    async uploadLogFile({ commit }, formData) {
      commit('setLoadingStatus', true)
      try {
        const response = await Vue.prototype.$http.post('/logs/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        commit('setLoadingStatus', false)
        return response
      } catch (error) {
        commit('setLoadingStatus', false)
        throw error
      }
    },
    
    // 开始分析日志文件
    async analyzeLogFile({ commit }, fileId) {
      commit('setLoadingStatus', true)
      try {
        const response = await Vue.prototype.$http.post(`/analysis/analyze/${fileId}`)
        commit('setLoadingStatus', false)
        return response
      } catch (error) {
        commit('setLoadingStatus', false)
        throw error
      }
    },
    
    // 获取分析结果
    async fetchAnalysisResults({ commit }, fileId) {
      commit('setLoadingStatus', true)
      try {
        const response = await Vue.prototype.$http.get(`/analysis/results/${fileId}`)
        commit('setAnalysisResults', response.results)
        commit('setLoadingStatus', false)
        return response
      } catch (error) {
        commit('setLoadingStatus', false)
        throw error
      }
    }
  },
  modules: {
  }
}) 