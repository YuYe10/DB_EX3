<template>
  <header class="app-header">
    <div class="app-header__inner">
      <div class="app-header__left">
        <div class="app-header__logo">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none">
            <rect x="3" y="3" width="18" height="18" rx="4" stroke="currentColor" stroke-width="1.5"/>
            <path d="M7 8h10M7 12h10M7 16h7" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          <span class="app-header__title">教务管理系统</span>
        </div>
      </div>
      <div class="app-header__right">
        <div class="app-header__user">
          <div class="app-header__avatar">
            {{ avatarChar }}
          </div>
          <div class="app-header__user-info">
            <span class="app-header__name">{{ user?.name || user?.username }}</span>
            <span class="app-header__role">{{ roleLabel }}</span>
          </div>
        </div>
        <button class="app-header__logout" @click="$emit('logout')" title="退出登录">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none">
            <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9"
              stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  user: { type: Object, default: null }
})

defineEmits(['logout'])

const avatarChar = computed(() => {
  const name = props.user?.name || props.user?.username || '?'
  return name.charAt(0).toUpperCase()
})

const roleLabel = computed(() => {
  const map = { admin: '管理员', teacher: '教师', student: '学生' }
  return map[props.user?.role] || props.user?.role || ''
})
</script>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--color-bg-glass);
  backdrop-filter: var(--blur-glass);
  -webkit-backdrop-filter: var(--blur-glass);
  border-bottom: 1px solid var(--color-border);
}
/* Fallback for browsers without backdrop-filter */
@supports not (backdrop-filter: blur(1px)) {
  .app-header { background: rgba(245, 245, 247, 0.95); }
}
.app-header__inner {
  max-width: var(--content-max-width);
  margin: 0 auto;
  padding: 0 var(--space-6);
  height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.app-header__left {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}
.app-header__logo {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--color-text-primary);
}
.app-header__title {
  font-size: var(--text-md);
  font-weight: var(--weight-bold);
  letter-spacing: var(--tracking-tight);
}
.app-header__right {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}
.app-header__user {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}
.app-header__avatar {
  width: 30px;
  height: 30px;
  border-radius: var(--radius-full);
  background: var(--color-accent);
  color: var(--color-text-inverse);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-sm);
  font-weight: var(--weight-bold);
}
.app-header__user-info {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}
.app-header__name {
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  color: var(--color-text-primary);
}
.app-header__role {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
}
.app-header__logout {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  color: var(--color-text-tertiary);
  transition: all var(--duration-fast) var(--ease-default);
}
.app-header__logout:hover {
  background: var(--color-danger-light);
  color: var(--color-danger);
}
</style>
