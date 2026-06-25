<template>
  <div class="stat-card" :class="[`stat-card--${variant}`, { 'stat-card--clickable': clickable }]"
    @click="clickable && $emit('click')">
    <div class="stat-card__header">
      <span class="stat-card__icon" v-if="icon">{{ icon }}</span>
      <span class="stat-card__label">{{ label }}</span>
    </div>
    <div class="stat-card__value" :style="{ color: valueColor }">
      <span v-if="prefix" class="stat-card__prefix">{{ prefix }}</span>
      {{ formattedValue }}
      <span v-if="suffix" class="stat-card__suffix">{{ suffix }}</span>
    </div>
    <div class="stat-card__trend" v-if="trend !== undefined" :class="trend >= 0 ? 'is-up' : 'is-down'">
      {{ trend >= 0 ? '↑' : '↓' }} {{ Math.abs(trend) }}%
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: { type: String, required: true },
  value: { type: [Number, String], default: 0 },
  icon: { type: String, default: '' },
  variant: { type: String, default: 'default', validator: v => ['default', 'accent', 'success', 'warning', 'danger'].includes(v) },
  clickable: { type: Boolean, default: false },
  trend: { type: Number, default: undefined },
  prefix: { type: String, default: '' },
  suffix: { type: String, default: '' },
  valueColor: { type: String, default: '' },
  format: { type: String, default: 'number' } // number | percent | decimal
})

defineEmits(['click'])

const formattedValue = computed(() => {
  const v = typeof props.value === 'string' ? parseFloat(props.value) : props.value
  if (isNaN(v)) return props.value
  if (props.format === 'percent') return `${v}%`
  if (props.format === 'decimal') return v.toFixed(1)
  return Number.isInteger(v) ? v.toString() : v.toFixed(2)
})
</script>

<style scoped>
.stat-card {
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-5) var(--space-6);
  transition: all var(--duration-fast) var(--ease-default);
}
.stat-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}
.stat-card--clickable { cursor: pointer; }
.stat-card--clickable:hover { border-color: var(--color-border-strong); }
.stat-card--accent { border-left: 3px solid var(--color-accent); }
.stat-card--success { border-left: 3px solid var(--color-success); }
.stat-card--warning { border-left: 3px solid var(--color-warning); }
.stat-card--danger { border-left: 3px solid var(--color-danger); }

.stat-card__header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-2);
}
.stat-card__icon { font-size: var(--text-lg); }
.stat-card__label {
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.stat-card__value {
  font-size: var(--text-3xl);
  font-weight: var(--weight-bold);
  letter-spacing: var(--tracking-tight);
  color: var(--color-text-primary);
  line-height: 1.2;
}
.stat-card__prefix, .stat-card__suffix {
  font-size: var(--text-lg);
  font-weight: var(--weight-medium);
  color: var(--color-text-tertiary);
}
.stat-card__trend {
  margin-top: var(--space-2);
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
}
.stat-card__trend.is-up { color: var(--color-success); }
.stat-card__trend.is-down { color: var(--color-danger); }
</style>
