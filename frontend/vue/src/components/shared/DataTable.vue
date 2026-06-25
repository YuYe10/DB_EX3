<template>
  <div class="data-table-wrapper">
    <table class="data-table" v-if="rows.length">
      <thead>
        <tr>
          <th v-for="col in columns" :key="col.key" :style="{ width: col.width }"
            :class="{ 'is-sortable': col.sortable, 'is-sorted': sortKey === col.key }"
            @click="col.sortable && toggleSort(col.key)">
            {{ col.label }}
            <span v-if="col.sortable && sortKey === col.key" class="sort-icon">
              {{ sortDir === 'asc' ? '↑' : '↓' }}
            </span>
          </th>
          <th v-if="$slots.actions" class="col-actions">操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, idx) in sortedRows" :key="row.id || idx">
          <td v-for="col in columns" :key="col.key">
            <slot :name="`cell-${col.key}`" :row="row" :value="row[col.key]">
              {{ row[col.key] }}
            </slot>
          </td>
          <td v-if="$slots.actions" class="col-actions">
            <slot name="actions" :row="row" />
          </td>
        </tr>
      </tbody>
    </table>
    <EmptyState v-else icon="📋" title="暂无数据" :description="emptyText" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import EmptyState from './EmptyState.vue'

const props = defineProps({
  columns: { type: Array, required: true },
  rows: { type: Array, default: () => [] },
  emptyText: { type: String, default: '' }
})

const sortKey = ref('')
const sortDir = ref('asc')

function toggleSort(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'asc'
  }
}

const sortedRows = computed(() => {
  if (!sortKey.value) return props.rows
  return [...props.rows].sort((a, b) => {
    const va = a[sortKey.value], vb = b[sortKey.value]
    if (va == null) return 1
    if (vb == null) return -1
    const cmp = typeof va === 'string' ? va.localeCompare(vb) : va - vb
    return sortDir.value === 'asc' ? cmp : -cmp
  })
})
</script>

<style scoped>
.data-table-wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}
.data-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}
.data-table thead {
  position: sticky;
  top: 0;
  z-index: 1;
}
.data-table th {
  padding: var(--space-3) var(--space-4);
  text-align: left;
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 2px solid var(--color-border);
  background: var(--color-bg-elevated);
  white-space: nowrap;
  user-select: none;
}
.data-table th.is-sortable {
  cursor: pointer;
}
.data-table th.is-sortable:hover {
  color: var(--color-accent);
}
.sort-icon {
  margin-left: var(--space-1);
  font-size: 10px;
}
.data-table td {
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-md);
  color: var(--color-text-primary);
  border-bottom: 1px solid var(--color-border);
  white-space: nowrap;
}
.data-table tbody tr {
  transition: background var(--duration-micro) var(--ease-default);
}
.data-table tbody tr:hover {
  background: var(--color-accent-light);
}
.col-actions {
  text-align: right;
  white-space: nowrap;
}
</style>
