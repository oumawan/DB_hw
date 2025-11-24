<template>
  <div class="message" :class="[typeClass, { modal: modal, confirm: confirm }]" :style="customStyle" v-show="visible" role="status" aria-live="polite">
    <template v-if="confirm">
      <div class="content">
        <span class="text">{{ text }}</span>
        <div class="actions">
          <button class="btn-confirm" @click="confirmAction">{{ confirmText }}</button>
          <button class="btn-cancel" @click="cancelAction">{{ cancelText }}</button>
        </div>
      </div>
    </template>
    <template v-else>
      <span class="text">{{ text }}</span>
      <button class="close" @click="close" aria-label="Close message">×</button>
    </template>
  </div>
</template>

<script>
export default {
  name: 'AppMessage',
  props: {
    modal: { type: Boolean, default: false },
    confirm: { type: Boolean, default: false },
    confirmText: { type: String, default: '确认' },
    cancelText: { type: String, default: '取消' },
    type: { type: String, default: 'info' },
    text: { type: String, default: '' },
    duration: { type: Number, default: 3000 },
    /** 可选自定义背景色（优先） */
    background: { type: String, default: '' },
    /** 可选自定义文本颜色 */
    color: { type: String, default: '' }
  },
  data() {
    return { visible: true }
  },
  computed: {
    typeClass() {
      return `message-${this.type}`
    },
    customStyle() {
      const s = {}
      if (this.background) s.background = this.background
      if (this.color) s.color = this.color
      return s
    }
  },
  mounted() {
    if (this.duration > 0) {
      this.timer = setTimeout(this.close, this.duration)
    }
    // when modal and not a confirm dialog, focus the close button for accessibility
    if (this.modal && !this.confirm) {
      this.$nextTick(() => {
        const btn = this.$el.querySelector('.close')
        if (btn) btn.focus()
      })
    }
  },
  beforeUnmount() {
    clearTimeout(this.timer)
  },
  methods: {
    close() {
      this.visible = false
      this.$emit('close')
    }
    ,
    confirmAction() {
      this.visible = false
      this.$emit('confirm')
    },
    cancelAction() {
      this.visible = false
      this.$emit('cancel')
    }
  }
}
</script>

<style scoped>
.message {
  /* let the host position the container; here we size the message box */
  min-width: 240px;
  max-width: 90vw;
  padding: 10px 14px;
  border-radius: 6px;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
.message .text {
  flex: 1;
  margin-right: 8px;
}
.message .close {
  background: transparent;
  border: none;
  color: inherit;
  font-size: 16px;
  cursor: pointer;
}
.message-info { background: #2196F3; }
.message-success { background: #4CAF50; }
.message-error { background: #F44336; }
.message-warning { background: #FF9800; }

/* stack animation (optional simple fade-slide) */
.message {
  opacity: 0;
  transform: translateY(-6px);
  transition: opacity 0.18s ease, transform 0.18s ease;
}
.message[role="status"] {
  opacity: 1;
  transform: translateY(0);
}

/* modal specific styling */
.message.modal {
  min-width: 320px;
  max-width: 80vw;
  padding: 18px 22px;
  border-radius: 10px;
  font-size: 16px;
  box-shadow: 0 8px 28px rgba(0,0,0,0.45);
}
.message.modal .text {
  text-align: center;
}
.message.modal .close {
  font-size: 20px;
}
.message .actions {
  display: flex;
  gap: 10px;
  margin-left: 8px;
}
.message .actions .btn-confirm {
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.18);
  color: inherit;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
}
.message .actions .btn-cancel {
  background: transparent;
  border: 1px solid rgba(255,255,255,0.12);
  color: inherit;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
}
.message.confirm .text { margin-bottom: 8px }
</style>
