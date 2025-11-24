<template>
  <div class="driver-profile">
    <h2>司机资料</h2>

    <div class="card">
      <div v-if="!editing">
        <p><strong>姓名：</strong> {{ profile.name || '未设置' }}</p>
        <p><strong>邮箱：</strong> {{ profile.email || '未设置' }}</p>
        <p><strong>司机编号：</strong> {{ profile.uid || '未设置' }}</p>
        <p><strong>准驾车型：</strong> {{ profile.license || '未设置' }}</p>
        <p><strong>所属车场：</strong> {{ profile.depotID || '未设置' }}</p>

        <div class="actions">
          <button @click="editing = true">编辑资料</button>
        </div>
      </div>

      <div v-else>
        <label>姓名 <input v-model="draft.name" disabled class="disabled" /></label>
        <label>邮箱 <input v-model="draft.email" /></label>
        <div v-if="emailError" class="error">{{ emailError }}</div>
        <label>司机编号 <input v-model="draft.uid" disabled class="disabled" /></label>
        <label>准驾车型 <input v-model="draft.license" disabled class="disabled" /></label>
        <label>所属车场 <input v-model="draft.depotID" disabled class="disabled" /></label>

        <div class="actions">
          <button @click="save" :disabled="saving">{{ saving ? '保存中...' : '保存' }}</button>
          <button class="secondary" @click="cancel" :disabled="saving">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import service from '../plugins/messageService'
import { getUserFromLocal, saveUserToLocal } from '../plugins/storage'
import { apiService } from '../api/api.js'
export default {
  name: 'DriverProfile',
  data() {
    return {
      editing: false,
      profile: {},
      draft: {},
      saving: false,
      emailError: ''
    }
  },
  created() {
    // load from centralized storage plugin if available, otherwise fallback to legacy key
    try {
      const user = getUserFromLocal()
      if (user) {
        this.profile = {
          name: user.name || '',
          email: user.email || '',
          uid: user.uid || '',
          license: user.license || '',
          depotID: user.depotID || ''
        }
      } else {
        const raw = localStorage.getItem('driverProfile')
        this.profile = raw ? JSON.parse(raw) : { name: '', email: '', uid: '', license: '', depotID: '' }
      }
    } catch (e) {
      this.profile = { name: '', email: '', uid: '', license: '', depotID: '' }
    }
    
  },
  methods: {
    save() {
      // 只允许修改邮箱，其他字段保持不变
      const email = (this.draft.email || '').trim()
      // 简单邮箱校验
      const emailRe = /^[^@\s]+@[^@\s]+\.[^@\s]+$/
      if (!emailRe.test(email)) {
        this.emailError = '请输入有效的邮箱地址'
        return
      }
      this.emailError = ''
      this.saving = true

      // 如果需要同步到后端，在这里调用 API（示例为注释）
      // apiService.updateProfile(this.profile.uid, { email })
      //   .then(() => { ... })
      //   .catch(err => { ... })

      // 本地持久化（开发阶段）
      this.profile.email = email
      // update centralized user storage if present
      try {
        const existing = getUserFromLocal() || {}
        const updatedUser = Object.assign({}, existing, {
          uid: this.profile.uid || existing.uid,
          email: this.profile.email,
          name: this.profile.name || existing.name,
          depotID: this.profile.depotID || existing.depotID,
          license: this.profile.license || existing.license,
          is_admin: existing.is_admin || false
        })
        apiService.driver_change_profile({
          uid: updatedUser.uid,
          email: updatedUser.email,
          name: updatedUser.name,
          depotID: updatedUser.depotID,
          license: updatedUser.license
        })
        saveUserToLocal(updatedUser)
      } catch (e) {
        // ignore storage plugin errors, fall back to legacy storage
      }

      try {
        localStorage.setItem('driverProfile', JSON.stringify(this.profile))
        service.show('个人资料已保存', { type: 'success' })
      } catch (e) {
        service.show('保存失败，请重试', { type: 'error' })
      } finally {
        this.saving = false
        this.editing = false
      }
    },
    cancel() {
      this.editing = false
    },
    
  },
  watch: {
    editing(val) {
      if (val) {
        // start editing: clone profile to draft
        this.draft = Object.assign({}, this.profile)
        this.emailError = ''
      }
    }
  }
}
</script>

<style scoped>
.driver-profile { padding: 20px }
.card { background: #fff; padding: 16px; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.06); max-width: 640px }
.card p { margin: 8px 0 }
.card label { display: block; margin: 8px 0 }
.card input { width: 100%; padding: 6px 8px; box-sizing: border-box }
.actions { margin-top: 12px; display: flex; gap: 10px }
.actions .secondary { background: #f3f4f6 }
.disabled { background-color: #f5f7fa; color: #6b7280; }
.disabled input[disabled] { pointer-events: none }
.error { color: #dc2626; margin: 6px 0; font-size: 13px }
.schedules { margin-top: 18px }
.schedules ul { list-style: none; padding: 0 }
.sched-item { display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid #eee }
.sched-item .meta { font-size: 14px }
.sched-item .ops button { background: #10b981; color: #fff; border: none; padding: 6px 10px; border-radius: 6px; cursor: pointer }
.sched-item .ops .done { color: #6b7280 }
</style>
