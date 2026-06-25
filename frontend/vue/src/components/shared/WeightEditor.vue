<template>
  <div class="weight-editor">
    <div class="weight-editor__header">
      <h4 class="weight-editor__title">成绩占比设置</h4>
      <span class="weight-editor__sum" :class="sumClass">合计: {{ totalWeight }}</span>
    </div>
    <div class="weight-editor__sliders">
      <label class="weight-field">
        <div class="weight-field__header">
          <span>平时成绩占比</span>
          <span class="weight-field__value">{{ ordinaryPercent }}%</span>
        </div>
        <input type="range" v-model.number="ordinaryPercent" min="0" max="100" step="5"
          class="weight-slider" @input="syncFromOrdinary" />
      </label>
      <label class="weight-field">
        <div class="weight-field__header">
          <span>期末成绩占比</span>
          <span class="weight-field__value">{{ finalPercent }}%</span>
        </div>
        <input type="range" v-model.number="finalPercent" min="0" max="100" step="5"
          class="weight-slider" @input="syncFromFinal" />
      </label>
    </div>
    <div class="weight-editor__actions">
      <button class="btn-save-weights" @click="save" :disabled="!isValid || saving">
        {{ saving ? '保存中...' : '保存成绩占比' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'

const props = defineProps({
  ordinaryWeight: { type: Number, default: 0.5 },
  finalWeight: { type: Number, default: 0.5 }
})

const emit = defineEmits(['save'])

const saving = ref(false)
const ordinaryPercent = ref(Math.round(props.ordinaryWeight * 100))
const finalPercent = ref(Math.round(props.finalWeight * 100))

watch(() => props.ordinaryWeight, v => { ordinaryPercent.value = Math.round(v * 100) })
watch(() => props.finalWeight, v => { finalPercent.value = Math.round(v * 100) })

const totalWeight = computed(() => ordinaryPercent.value + finalPercent.value)

const isValid = computed(() => totalWeight.value === 100)

const sumClass = computed(() => {
  if (totalWeight.value === 100) return 'is-valid'
  if (totalWeight.value > 100) return 'is-over'
  return 'is-under'
})

function syncFromOrdinary() {
  finalPercent.value = 100 - ordinaryPercent.value
}
function syncFromFinal() {
  ordinaryPercent.value = 100 - finalPercent.value
}

function save() {
  if (!isValid.value) return
  saving.value = true
  emit('save', {
    ordinary_weight: ordinaryPercent.value / 100,
    final_weight: finalPercent.value / 100
  })
  setTimeout(() => { saving.value = false }, 500)
}
</script>

<style scoped>
.weight-editor {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
}
.weight-editor__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-4);
}
.weight-editor__title {
  font-size: var(--text-md);
  font-weight: var(--weight-bold);
  color: var(--color-text-primary);
}
.weight-editor__sum {
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
}
.weight-editor__sum.is-valid { color: var(--color-success); background: var(--color-success-light); }
.weight-editor__sum.is-over { color: var(--color-danger); background: var(--color-danger-light); }
.weight-editor__sum.is-under { color: var(--color-warning); background: var(--color-warning-light); }

.weight-editor__sliders {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}
.weight-field__header {
  display: flex;
  justify-content: space-between;
  margin-bottom: var(--space-2);
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  color: var(--color-text-secondary);
}
.weight-field__value {
  font-weight: var(--weight-bold);
  color: var(--color-text-primary);
  min-width: 36px;
  text-align: right;
}
.weight-slider {
  width: 100%;
  height: 6px;
  -webkit-appearance: none;
  appearance: none;
  background: var(--color-border);
  border-radius: var(--radius-full);
  outline: none;
  cursor: pointer;
}
.weight-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--color-accent);
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  transition: transform var(--duration-micro) var(--ease-default);
}
.weight-slider::-webkit-slider-thumb:hover { transform: scale(1.15); }
.weight-slider::-webkit-slider-thumb:active { transform: scale(0.95); }

.weight-editor__actions { margin-top: var(--space-4); }
.btn-save-weights {
  width: 100%;
  padding: var(--space-2) var(--space-4);
  background: var(--color-accent);
  color: var(--color-text-inverse);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  transition: all var(--duration-fast) var(--ease-default);
}
.btn-save-weights:hover:not(:disabled) { background: var(--color-accent-hover); }
.btn-save-weights:disabled { opacity: 0.4; cursor: not-allowed; }
</style>
