<template>
  <div class="search-filter">
    <div class="search-filter__input-wrap">
      <svg class="search-filter__icon" viewBox="0 0 24 24" fill="none" width="16" height="16">
        <circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="2"/>
        <path d="M20 20l-3.5-3.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>
      <input type="text" :value="modelValue" @input="$emit('update:modelValue', $event.target.value)"
        :placeholder="placeholder" class="search-filter__input" />
      <button v-if="modelValue" class="search-filter__clear" @click="$emit('update:modelValue', '')" aria-label="Clear">
        <svg viewBox="0 0 24 24" width="14" height="14" fill="none">
          <circle cx="12" cy="12" r="10" fill="currentColor" opacity="0.15"/>
          <path d="M8 8l8 8M16 8l-8 8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
      </button>
    </div>
    <slot name="filters" />
  </div>
</template>

<script setup>
defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: '搜索...' }
})
defineEmits(['update:modelValue'])
</script>

<style scoped>
.search-filter {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-wrap: wrap;
}
.search-filter__input-wrap {
  position: relative;
  flex: 1;
  min-width: 180px;
}
.search-filter__icon {
  position: absolute;
  left: var(--space-3);
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-tertiary);
  pointer-events: none;
}
.search-filter__input {
  width: 100%;
  padding: var(--space-2) var(--space-4) var(--space-2) var(--space-8);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--text-md);
  background: var(--color-bg-elevated);
  color: var(--color-text-primary);
  transition: all var(--duration-fast) var(--ease-default);
  outline: none;
}
.search-filter__input::placeholder { color: var(--color-text-tertiary); }
.search-filter__input:focus {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px var(--color-accent-light);
}
.search-filter__clear {
  position: absolute;
  right: var(--space-2);
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  padding: 2px;
  color: var(--color-text-tertiary);
  transition: color var(--duration-micro);
}
.search-filter__clear:hover { color: var(--color-text-secondary); }
</style>
