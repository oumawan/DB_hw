<template>
  <div class="admin-page">
    <aside class="sidebar">
      <div class="brand">后台管理</div>
      <nav>
        <router-link to="/admin/drivers" class="nav-item">司机管理</router-link>
        <router-link to="/admin/vehicles" class="nav-item">车辆管理</router-link>
        <router-link to="/admin/schedules" class="nav-item">班次管理</router-link>
        <router-link to="/admin/transfers" class="nav-item">调动记录</router-link>
        <router-link to="/admin/leaves" class="nav-item">请假管理</router-link>
      </nav>
    </aside>

    <main class="content">
      <header class="topbar">
        <h1>管理员控制台</h1>
        <div class="top-actions">
          <button class="logout-btn" @click="logout">登出</button>
        </div>
      </header>
      <section class="view">
        <!-- 子路由内容将渲染在这里 -->
        <router-view />
      </section>
    </main>
  </div>
</template>

<script>
import service from '../plugins/messageService'
import { clearUserFromLocal } from '@/plugins/storage';
export default {
  name: 'AdminPage',
  methods: {
    async logout() {
      const confirmed = await service.showConfirm('确定要登出吗？', { type: 'warning', confirmText: '登出', cancelText: '取消' })
      if (!confirmed) return
      // clear local login flags (frontend-only)
      clearUserFromLocal();
      service.show('已登出', { type: 'info', duration: 1200 })
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.admin-page {
  display: flex;
  height: 100vh;
  background: #f9fafb;
}
.sidebar {
  width: 220px;
  background: #0f172a;
  color: #fff;
  display: flex;
  flex-direction: column;
  padding: 18px;
  box-sizing: border-box;
}
.brand {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
}
.nav-item {
  display: block;
  color: #cbd5e1;
  padding: 8px 10px;
  border-radius: 6px;
  margin-bottom: 6px;
  text-decoration: none;
}
.nav-item.router-link-active {
  background: #1f2937;
  color: #fff;
}
.content {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.topbar {
  padding: 14px 18px;
  border-bottom: 1px solid #e6edf3;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.top-actions { display: flex; gap: 12px; align-items: center }
.back-link { color: #111827; text-decoration: none }
.topbar .logout-btn {
  background: #ef4444;
  color: #fff;
  border: none;
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
}
.topbar .logout-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.view {
  padding: 18px;
  overflow: auto;
}

@media (max-width: 800px) {
  .sidebar { display: none; }
  .admin-page { flex-direction: column; }
}
</style>
