<template>
  <div class="admin-page">
    <aside class="sidebar">
      <div class="brand">后台管理</div>
      <nav>
        <router-link to="/admin/drivers" class="nav-item">司机管理</router-link>
        <router-link to="/admin/vehicles" class="nav-item">车辆管理</router-link>
        <router-link to="/admin/schedules" class="nav-item">班次管理</router-link>
        <router-link to="/admin/lines" class="nav-item">线路管理</router-link>
        <router-link to="/admin/leaves" class="nav-item">请假管理</router-link>
      </nav>
    </aside>

    <main class="content">
      <header class="topbar">
        <h1>管理员控制台</h1>
        <div class="top-actions">
          <div class="user-info">
            <div class="u-row"><span class="label">UID:</span> <span class="val">{{ currentUser ? currentUser.uid : '-' }}</span></div>
            <div class="u-row"><span class="label">姓名:</span> <span class="val">{{ currentUser ? currentUser.name : '-' }}</span></div>
            <div class="u-row"><span class="label">邮箱:</span> <span class="val">{{ currentUser ? currentUser.email : '-' }}</span></div>
            <div class="u-row"><span class="label">管理车场:</span> <span class="val">{{ currentUser ? currentUser.depotID : '-' }}</span></div>
          </div>
          <div class="action-buttons">
            <button class="change-pw-btn" @click="openChangePassword">修改密码</button>
            <button class="logout-btn" @click="logout">登出</button>
          </div>
        </div>
      </header>
      <!-- Change Password Modal -->
      <div v-if="showChangePw" class="modal-backdrop">
        <div class="modal">
          <h3>修改密码</h3>
          <label>当前密码（当前无效，仅展示）</label>
          <label> <input type="password" v-model="cpw.current" /></label>
          <label>新密码</label>
          <label> <input type="password" v-model="cpw.new" /></label>
          <label>确认新密码</label>
          <label> <input type="password" v-model="cpw.confirm" /></label>
          <div class="modal-actions">
            <button @click="submitChangePassword" :disabled="submitting || !valid">保存</button>
            <button class="secondary" @click="closeChangePassword" :disabled="submitting">取消</button>
          </div>
        </div>
      </div>
      <section class="view">
        <!-- 子路由内容将渲染在这里 -->
        <router-view />
      </section>
    </main>
  </div>
</template>

<script>
import service from '../plugins/messageService'
import { clearUserFromLocal, getUserFromLocal } from '@/plugins/storage';
import { apiService } from '../api/api.js'

export default {
  name: 'AdminPage',
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
    },
    currentUser() {
      // read user info from storage; supports sessionStorage or localStorage implementation
      try {
        return getUserFromLocal()
      } catch (e) {
        return null
      }
    }
  },
  methods: {
    async logout() {
      const confirmed = await service.showConfirm('确定要登出吗？', { type: 'warning', confirmText: '登出', cancelText: '取消' })
      if (!confirmed) return
      // clear local login flags (frontend-only)
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
        // 当前密码字段在后端目前无效——仍随请求发送以备后端将来校验
        await apiService.modifyPassword({ uid: uid, old_password: this.cpw.current, password: this.cpw.new })
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
.user-info { display:flex; flex-direction:column; align-items:flex-end; gap:2px; margin-right:12px; font-size:13px; color:#374151 }
.user-info .u-row { line-height:1 }
.user-info .label { font-weight:600; margin-right:6px; color:#111827 }
.action-buttons { display:flex; gap:12px; align-items:center }
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

.modal-backdrop { position:fixed; inset:0; background:rgba(0,0,0,0.4); display:flex; align-items:center; justify-content:center; z-index:50 }
.modal { background:#fff; padding:16px; border-radius:6px; width:360px; box-shadow:0 6px 18px rgba(0,0,0,0.2) }
.modal label { display:block; margin:8px 0 }
.modal-actions { display:flex; gap:8px; justify-content:flex-end; margin-top:12px }
.change-pw-btn { background:#3b82f6; color:#fff; border:none; padding:6px 10px; border-radius:6px; cursor:pointer }
.change-pw-btn:disabled { opacity:0.6 }

@media (max-width: 800px) {
  .sidebar { display: none; }
  .admin-page { flex-direction: column; }
}
</style>
