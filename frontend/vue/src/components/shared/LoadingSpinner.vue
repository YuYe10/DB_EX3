<template>
  <div class="spinner" :class="[`spinner--${size}`]" role="status" aria-label="Loading">
    <svg class="spinner__svg" viewBox="0 0 24 24" fill="none">
      <circle class="spinner__track" cx="12" cy="12" r="10" stroke-width="3" />
      <circle class="spinner__indicator" cx="12" cy="12" r="10" stroke-width="3"
        stroke-linecap="round" stroke="currentColor" />
    </svg>
    <span v-if="text" class="spinner__text">{{ text }}</span>
  </div>
</template>

<script setup>
defineProps({
  size: { type: String, default: 'md', validator: v => ['sm', 'md', 'lg'].includes(v) },
  text: { type: String, default: '' }
})
</script>

<style scoped>
.spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
}
.spinner__svg {
  width: 28px;
  height: 28px;
  animation: spin 0.8s linear infinite;
}
.spinner--sm .spinner__svg { width: 18px; height: 18px; }
.spinner--lg .spinner__svg { width: 40px; height: 40px; }
.spinner__track {
  stroke: var(--color-border);
}
.spinner__indicator {
  stroke-dasharray: 64;
  stroke-dashoffset: 48;
  color: var(--color-accent);
}
.spinner__text {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}
</style>
