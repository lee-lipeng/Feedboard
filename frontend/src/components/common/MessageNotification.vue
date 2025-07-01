<template>
  <transition name="notification-fade">
    <div 
      v-if="visible" 
      :class="['notification', `notification-${type}`]"
      @click="dismiss"
    >
      <div class="notification-icon">
        <svg v-if="type === 'success'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <svg v-else-if="type === 'error'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0z" />
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
        </svg>
        <svg v-else-if="type === 'warning'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
          <path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
        </svg>
      </div>
      <div class="notification-content">
        {{ message }}
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue';

const props = defineProps({
  message: { type: String, required: true },
  type: { 
    type: String, 
    default: 'info',
    validator: (value: string) => ['success', 'error', 'warning', 'info'].includes(value)
  },
  duration: { type: Number, default: 3000 },
  visible: { type: Boolean, default: true }
});

const emit = defineEmits(['close']);

let timer: number | null = null;

const dismiss = () => {
  emit('close');
  clearTimeout(timer as number);
};

const startTimer = () => {
  if (props.duration > 0) {
    timer = window.setTimeout(() => {
      dismiss();
    }, props.duration);
  }
};

watch(() => props.visible, (newVal) => {
  if (newVal) {
    startTimer();
  } else if (timer) {
    clearTimeout(timer);
  }
});

onMounted(() => {
  if (props.visible) {
    startTimer();
  }
});

onUnmounted(() => {
  if (timer) {
    clearTimeout(timer);
  }
});
</script>

<style scoped>
.notification {
  position: fixed;
  top: 20px;
  right: 20px;
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 9999;
  cursor: pointer;
  max-width: 400px;
}

.notification-success {
  background-color: #f0fdf4;
  border-left: 4px solid #10b981;
  color: #065f46;
}

.notification-error {
  background-color: #fef2f2;
  border-left: 4px solid #ef4444;
  color: #991b1b;
}

.notification-warning {
  background-color: #fffbeb;
  border-left: 4px solid #f59e0b;
  color: #92400e;
}

.notification-info {
  background-color: #eff6ff;
  border-left: 4px solid #3b82f6;
  color: #1e40af;
}

.notification-icon {
  margin-right: 12px;
  width: 24px;
  height: 24px;
  flex-shrink: 0;
}

.notification-content {
  flex-grow: 1;
  font-size: 14px;
}

/* 过渡动画 */
.notification-fade-enter-active,
.notification-fade-leave-active {
  transition: all 0.3s ease;
}

.notification-fade-enter-from,
.notification-fade-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style> 