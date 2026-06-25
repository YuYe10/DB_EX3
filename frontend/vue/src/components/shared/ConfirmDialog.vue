<template>
  <Teleport to="body">
    <Transition name="overlay">
      <div v-if="visible" class="confirm-overlay" @click.self="$emit('cancel')">
        <Transition name="modal">
          <div v-if="visible" class="confirm-dialog modal-content">
            <div class="confirm-dialog__icon">{{ icon }}</div>
            <h3 class="confirm-dialog__title">{{ title }}</h3>
            <p class="confirm-dialog__message">{{ message }}</p>
            <div class="confirm-dialog__actions">
              <button class="btn btn--secondary" @click="$emit('cancel')" :disabled="loading">
                {{ cancelText }}
              </button>
              <button class="btn" :class="[`btn--${variant}`]" @click="$emit('confirm')" :disabled="loading">
                <LoadingSpinner v-if="loading" size="sm" />
                <span v-else>{{ confirmText }}</span>
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import LoadingSpinner from './LoadingSpinner.vue'

defineProps({
  visible: { type: Boolean, default: false },
  title: { type: String, default: '确认操作' },
  message: { type: String, default: '确定要执行此操作吗？' },
  icon: { type: String, default: '⚠️' },
  confirmText: { type: String, default: '确定' },
  cancelText: { type: String, default: '取消' },
  variant: { type: String, default: 'danger', validator: v => ['primary', 'danger'].includes(v) },
  loading: { type: Boolean, default: false }
})

defineEmits(['confirm', 'cancel'])
</script>

<style scoped>
.confirm-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: var(--blur-subtle);
  padding: var(--space-6);
}
.confirm-dialog {
  background: var(--color-bg-elevated);
  border-radius: var(--radius-xl);
  padding: var(--space-8);
  max-width: 400px;
  width: 100%;
  text-align: center;
  box-shadow: var(--shadow-2xl);
  border: 1px solid var(--color-border);
}
.confirm-dialog__icon {
  font-size: 2.5rem;
  margin-bottom: var(--space-4);
}
.confirm-dialog__title {
  font-size: var(--text-lg);
  font-weight: var(--weight-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}
.confirm-dialog__message {
  font-size: var(--text-md);
  color: var(--color-text-secondary);
  line-height: var(--leading-relaxed);
  margin-bottom: var(--space-6);
}
.confirm-dialog__actions {
  display: flex;
  gap: var(--space-3);
  justify-content: center;
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-5);
  border-radius: var(--radius-md);
  font-size: var(--text-md);
  font-weight: var(--weight-semibold);
  transition: all var(--duration-fast) var(--ease-default);
  min-height: 36px;
}
.btn--primary {
  background: var(--color-accent);
  color: var(--color-text-inverse);
}
.btn--primary:hover { background: var(--color-accent-hover); }
.btn--danger {
  background: var(--color-danger);
  color: var(--color-text-inverse);
}
.btn--danger:hover { background: var(--color-danger-hover); }
.btn--secondary {
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}
.btn--secondary:hover {
  background: var(--color-bg-primary);
  border-color: var(--color-border-strong);
}
.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
