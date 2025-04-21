<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App',
  created() {
    // 从本地存储恢复用户登录状态
    const token = localStorage.getItem('token')
    const user = localStorage.getItem('user')
    
    if (token && user) {
      try {
        // 仅从本地存储恢复状态，不进行验证
        this.$store.commit('setToken', token)
        this.$store.commit('setUser', JSON.parse(user))
        this.$store.commit('setAuthenticated', true)
      } catch (error) {
        console.error('Failed to restore user session:', error)
        localStorage.removeItem('token')
        localStorage.removeItem('user')
      }
    }
  }
}
</script>

<style>
#app {
  height: 100%;
}
</style> 