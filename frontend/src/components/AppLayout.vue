<template>
  <el-container class="app-layout">
    <nav-header />
    <el-main class="main-container">
      <slot></slot>
    </el-main>
    <el-footer class="app-footer">
      <p>© 2024 日志态势感知系统 | 版权所有</p>
    </el-footer>
  </el-container>
</template>

<script>
import NavHeader from './NavHeader.vue'

export default {
  name: 'AppLayout',
  components: {
    NavHeader
  }
}
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  flex-direction: column;
}

.main-container {
  flex: 1;
  padding: 20px;
  background-color: #f5f7fa;
}

.app-footer {
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f2f6fc;
  color: #606266;
  font-size: 14px;
}
</style> 