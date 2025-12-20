<template>
  <div class="driver-page">
    <aside class="sidebar">
      <div class="brand">司机面板</div>
      <nav>
        <router-link to="/driver/profile" class="nav-item">个人资料</router-link>
        <router-link to="/driver/schedules" class="nav-item">我的班次</router-link>
        <router-link to="/driver/leaves" class="nav-item">请假申请</router-link>
      </nav>
    </aside>

    <main class="content">
      <header class="topbar">
          <h1>司机控制台</h1>
          <div class="top-actions">
            <button class="change-pw-btn" @click="openChangePassword">修改密码</button>
            <button class="logout-btn" @click="logout">登出</button>
          </div>
        </header>
        <!-- Change Password Modal -->
        <div v-if="showChangePw" class="modal-backdrop">
          <div class="modal">
            <h3>修改密码</h3>
            <label>当前密码</label> 
            <label><input type="password" v-model="cpw.current" /></label>
            <label>新密码 </label>
            <label><input type="password" v-model="cpw.new" /></label>
            <label>确认新密码 </label>
            <label><input type="password" v-model="cpw.confirm" /></label>
            <div class="modal-actions">
              <button @click="submitChangePassword" :disabled="submitting || !valid">保存</button>
              <button class="secondary" @click="closeChangePassword" :disabled="submitting">取消</button>
            </div>
          </div>
        </div>
      <section class="view">
        <router-view />
      </section>
    </main>
  </div>
</template>

<script>
import service from '../../plugins/messageService'
import { clearUserFromLocal, getUserFromLocal } from '@/plugins/storage';
import api from '../../api/api.js'
export default {
  name: 'DriverPage',
  data() {
    return {
      showChangePw: false,
      cpw: { current: '', new: '', confirm: '' },
      submitting: false
    }
  },
  computed: {
    valid() {
      return this.cpw.new && this.cpw.new === this.cpw.confirm
    }
  },
  methods: {
    async logout() {
      const confirmed = await service.showConfirm('确定要登出吗？', { type: 'warning', confirmText: '登出', cancelText: '取消' })
      if (!confirmed) return
      clearUserFromLocal();
      service.show('已登出', { type: 'info', duration: 1200 })
      this.$router.push('/')
    },
    openChangePassword() {
      this.cpw = { current: '', new: '', confirm: '' }
      this.showChangePw = true
    },
    closeChangePassword() {
      this.showChangePw = false
    },
    async submitChangePassword() {
      if (!this.valid) return
      this.submitting = true
      try {
        const user = getUserFromLocal() || {}
        const uid = user.uid
        if (!uid) {
          service.show('未检测到登录用户，请重新登录', { type: 'error' })
          return
        }
        await api.post('api/user/changePassword/', { uid, password: this.cpw.new, current_password: this.cpw.current })
        service.show('密码修改成功', { type: 'success' })
        this.showChangePw = false
      } catch (err) {
        const msg = err?.response?.data?.message || err.message || '修改失败，请重试'
        service.show(msg, { type: 'error' })
      } finally {
        this.submitting = false
      }
    }
  }
}
</script>

<style scoped>
.driver-page { display: flex; height: 100vh; background: #f9fafb }
.sidebar { width: 220px; background: #0f172a; color: #fff; padding: 18px; min-height: 100vh; display: flex; flex-direction: column; box-sizing: border-box }
.brand { font-size: 16px; font-weight: 600; margin-bottom: 12px }
.nav-item { display: block; color: #cbd5e1; padding: 8px 10px; border-radius: 6px; margin-bottom: 6px; text-decoration: none }
.nav-item.router-link-active { background: #1f2937; color: #fff }
.content { flex: 1; display: flex; flex-direction: column }
.topbar { padding: 14px 18px; border-bottom: 1px solid #e6edf3; background: #fff; display: flex; justify-content: space-between; align-items: center }
.top-actions { display: flex; gap: 12px; align-items: center }
.back-link { color: #111827; text-decoration: none }
.topbar .logout-btn { background: #ef4444; color: #fff; border: none; padding: 6px 10px; border-radius: 6px; cursor: pointer }
.topbar .logout-btn:disabled { opacity: 0.6; cursor: not-allowed }
.view { padding: 18px; overflow: auto }
@media (max-width: 800px) { .sidebar { display: none } }

.modal-backdrop { position:fixed; inset:0; background:rgba(0,0,0,0.4); display:flex; align-items:center; justify-content:center; z-index:50 }
.modal { background:#fff; padding:16px; border-radius:6px; width:360px; box-shadow:0 6px 18px rgba(0,0,0,0.2) }
.modal label { display:block; margin:8px 0 }
.modal-actions { display:flex; gap:8px; justify-content:flex-end; margin-top:12px }
.change-pw-btn { background:#3b82f6; color:#fff; border:none; padding:6px 10px; border-radius:6px; cursor:pointer }
.change-pw-btn:disabled { opacity:0.6 }
</style>
