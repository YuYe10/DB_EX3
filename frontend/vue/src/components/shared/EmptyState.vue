<template>
  <div class="empty-state">
    <div class="empty-state__icon">{{ icon }}</div>
    <h3 class="empty-state__title">{{ title }}</h3>
    <p class="empty-state__desc" v-if="description">{{ description }}</p>
    <slot name="action" />
  </div>
</template>

<script setup>
defineProps({
  icon: { type: String, default: '📋' },
  title: { type: String, default: '暂无数据' },
  description: { type: String, default: '' }
})
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-12) var(--space-6);
  text-align: center;
}
.empty-state__icon {
  font-size: 2.5rem;
  margin-bottom: var(--space-4);
  opacity: 0.6;
}
.empty-state__title {
  font-size: var(--text-lg);
  font-weight: var(--weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}
.empty-state__desc {
  font-size: var(--text-md);
  color: var(--color-text-secondary);
  max-width: 280px;
  line-height: var(--leading-relaxed);
}
</style>
