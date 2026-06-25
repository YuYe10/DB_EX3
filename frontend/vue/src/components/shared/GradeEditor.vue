<template>
  <div class="grade-editor">
    <div class="grade-editor__fields">
      <label class="grade-field">
        <span class="grade-field__label">平时成绩</span>
        <input type="number" v-model.number="local.ordinary_score" min="0" max="100" step="0.5"
          placeholder="0-100" class="grade-field__input"
          @input="recalc" />
      </label>
      <span class="grade-editor__times">× {{ ordinaryWeight }}</span>
      <span class="grade-editor__plus">+</span>
      <label class="grade-field">
        <span class="grade-field__label">期末成绩</span>
        <input type="number" v-model.number="local.final_score" min="0" max="100" step="0.5"
          placeholder="0-100" class="grade-field__input"
          @input="recalc" />
      </label>
      <span class="grade-editor__times">× {{ finalWeight }}</span>
      <span class="grade-editor__equals">=</span>
      <div class="grade-field grade-field--result">
        <span class="grade-field__label">最终成绩</span>
        <span class="grade-result" :class="gradeClass">{{ previewGrade }}</span>
      </div>
    </div>
    <div class="grade-editor__actions">
      <button class="btn-save" @click="save" :disabled="!isValid || saving">
        {{ saving ? '保存中...' : '保存成绩' }}
      </button>
      <button class="btn-cancel" @click="$emit('cancel')" v-if="showCancel">取消</button>
    </div>
  </div>
</template>

<script setup>
import { reactive, computed, watch, ref } from 'vue'

const props = defineProps({
  ordinaryScore: { type: Number, default: null },
  finalScore: { type: Number, default: null },
  ordinaryWeight: { type: Number, default: 0.5 },
  finalWeight: { type: Number, default: 0.5 },
  showCancel: { type: Boolean, default: true }
})

const emit = defineEmits(['save', 'cancel'])

const saving = ref(false)
const local = reactive({
  ordinary_score: props.ordinaryScore,
  final_score: props.finalScore
})

watch(() => [props.ordinaryScore, props.finalScore], ([o, f]) => {
  local.ordinary_score = o
  local.final_score = f
})

const previewGrade = computed(() => {
  if (local.ordinary_score == null || local.final_score == null) return '--'
  return (local.ordinary_score * props.ordinaryWeight + local.final_score * props.finalWeight).toFixed(1)
})

const isValid = computed(() => {
  return local.ordinary_score != null && local.final_score != null &&
    local.ordinary_score >= 0 && local.ordinary_score <= 100 &&
    local.final_score >= 0 && local.final_score <= 100
})

const gradeClass = computed(() => {
  const g = parseFloat(previewGrade.value)
  if (isNaN(g)) return ''
  if (g >= 90) return 'is-excellent'
  if (g >= 60) return 'is-pass'
  return 'is-fail'
})

function recalc() { /* reactive, computed handles it */ }

function save() {
  if (!isValid.value) return
  saving.value = true
  emit('save', {
    ordinary_score: local.ordinary_score,
    final_score: local.final_score
  })
  setTimeout(() => { saving.value = false }, 500)
}
</script>

<style scoped>
.grade-editor {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-4) var(--space-5);
}
.grade-editor__fields {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-wrap: wrap;
}
.grade-field {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}
.grade-field__label {
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.grade-field__input {
  width: 80px;
  padding: var(--space-1) var(--space-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: var(--text-md);
  font-weight: var(--weight-semibold);
  text-align: center;
  background: var(--color-bg-elevated);
  transition: border-color var(--duration-fast) var(--ease-default);
}
.grade-field__input:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px var(--color-accent-light);
}
.grade-editor__times, .grade-editor__plus, .grade-editor__equals {
  font-size: var(--text-lg);
  color: var(--color-text-tertiary);
  font-weight: var(--weight-medium);
  margin-top: var(--space-4);
}
.grade-result {
  font-size: var(--text-xl);
  font-weight: var(--weight-extrabold);
  margin-top: 2px;
  min-width: 60px;
}
.grade-result.is-excellent { color: var(--color-success); }
.grade-result.is-pass { color: var(--color-accent); }
.grade-result.is-fail { color: var(--color-danger); }

.grade-editor__actions {
  display: flex;
  gap: var(--space-3);
  margin-top: var(--space-4);
  padding-top: var(--space-4);
  border-top: 1px solid var(--color-border);
}
.btn-save {
  padding: var(--space-2) var(--space-5);
  background: var(--color-accent);
  color: var(--color-text-inverse);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  transition: all var(--duration-fast) var(--ease-default);
}
.btn-save:hover:not(:disabled) { background: var(--color-accent-hover); }
.btn-save:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-cancel {
  padding: var(--space-2) var(--space-5);
  background: var(--color-bg-elevated);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  transition: all var(--duration-fast) var(--ease-default);
}
.btn-cancel:hover { border-color: var(--color-border-strong); }
</style>
