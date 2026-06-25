<template>
  <div class="admin-hero animate-fade-in">
    <div class="hero-main">
      <p class="hero-eyebrow">管理员界面</p>
      <h1 class="hero-title">教务管理系统</h1>
      <div class="hero-status" :class="health?.db ? 'is-ok' : 'is-bad'">
        <span class="status-dot" :class="health?.db ? 'online' : 'offline'" />
        {{ health?.db ? '系统运行正常' : '等待后端连接' }}
      </div>
    </div>
    <div class="hero-stats" v-if="stats?.counts">
      <StatCard label="学生" :value="stats.counts.students" icon="👥" variant="accent" />
      <StatCard label="教师" :value="stats.counts.teachers" icon="👨‍🏫" variant="default" />
      <StatCard label="课程" :value="stats.counts.courses" icon="📚" variant="success" />
      <StatCard label="选课记录" :value="stats.counts.enrollments" icon="📝" variant="warning" />
    </div>
  </div>
</template>

<script setup>
import StatCard from '../../components/shared/StatCard.vue'

defineProps({
  stats: { type: Object, default: null },
  health: { type: Object, default: null }
})
</script>

<style scoped>
.admin-hero {
  background: var(--color-bg-glass);
  backdrop-filter: var(--blur-glass);
  -webkit-backdrop-filter: var(--blur-glass);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: var(--space-8);
  margin-bottom: var(--space-6);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--space-8);
  flex-wrap: wrap;
}
.hero-eyebrow {
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  color: var(--color-accent);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: var(--space-2);
}
.hero-title {
  font-size: var(--text-2xl);
  font-weight: var(--weight-extrabold);
  letter-spacing: var(--tracking-tight);
  margin-bottom: var(--space-3);
}
.hero-status {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--weight-medium);
}
.hero-status.is-ok { color: var(--color-success); background: var(--color-success-light); }
.hero-status.is-bad { color: var(--color-danger); background: var(--color-danger-light); }
.status-dot {
  width: 8px; height: 8px; border-radius: 50%;
}
.status-dot.online { background: var(--color-success); animation: pulse 2s ease-in-out infinite; }
.status-dot.offline { background: var(--color-danger); }

.hero-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: var(--space-4);
  flex: 1;
  min-width: 280px;
}
@media (max-width: 640px) {
  .admin-hero { flex-direction: column; }
  .hero-stats { width: 100%; }
}
</style>
