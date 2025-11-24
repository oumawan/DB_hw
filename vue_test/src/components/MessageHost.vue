<template>
  <!-- Non-modal stacked messages (top center) -->
  <div class="message-host">
    <Message
      v-for="msg in nonModal"
      :key="msg.id"
      :type="msg.type"
      :text="msg.text"
      :duration="msg.duration"
      :background="msg.background"
      :color="msg.color"
      @close="service.close(msg.id)"
    />
  </div>

  <!-- Modal overlay: if any message has modal=true, show the first one centered -->
  <div v-if="modalMessage" class="modal-overlay">
    <div class="modal-wrapper">
      <Message
        :type="modalMessage.type"
        :text="modalMessage.text"
        :duration="modalMessage.duration"
        :background="modalMessage.background"
        :color="modalMessage.color"
        :modal="true"
        :confirm="modalMessage.confirm"
        :confirm-text="modalMessage.confirmText"
        :cancel-text="modalMessage.cancelText"
        @confirm="onConfirm(modalMessage.id)"
        @cancel="onCancel(modalMessage.id)"
        @close="service.close(modalMessage.id)"
      />
    </div>
  </div>
</template>

<script>
import { computed, watch, onUnmounted } from 'vue'
import Message from './Message.vue'
import service from '../plugins/messageService'

export default {
  name: 'MessageHost',
  components: { Message },
  setup() {
    const nonModal = computed(() => service.state.messages.filter(m => !m.modal))
    const modalMessage = computed(() => service.state.messages.find(m => m.modal) || null)
    // when modalMessage exists, disable body scroll to block background interactions
    const originalOverflow = { value: '' }
    watch(modalMessage, (val) => {
      if (val) {
        originalOverflow.value = document.body.style.overflow
        document.body.style.overflow = 'hidden'
      } else {
        document.body.style.overflow = originalOverflow.value || ''
      }
    }, { immediate: true })

    onUnmounted(() => {
      document.body.style.overflow = originalOverflow.value || ''
    })

    function onConfirm(id) {
      const m = service.state.messages.find(x => x.id === id)
      if (m && typeof m._resolve === 'function') {
        m._resolve(true)
      }
      service.close(id)
    }

    function onCancel(id) {
      const m = service.state.messages.find(x => x.id === id)
      if (m && typeof m._resolve === 'function') {
        m._resolve(false)
      }
      service.close(id)
    }

    return { service, nonModal, modalMessage, onConfirm, onCancel }
  }
}
</script>

<style scoped>
.message-host {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: center;
  z-index: 1100;
  pointer-events: none; /* allow clicks through empty areas */
}
.message-host > * {
  pointer-events: auto; /* allow interacting with message buttons */
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0,0,0,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 99999;
}
.modal-wrapper {
  pointer-events: auto;
}
</style>
