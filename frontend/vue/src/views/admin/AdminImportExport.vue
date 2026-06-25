<template>
  <section class="card--glass animate-slide-up">
    <div class="card__header">
      <h2 class="card__title">Excel 导入导出</h2>
    </div>
    <div class="card__body">
      <div class="ie-grid">
        <!-- Import -->
        <div class="ie-panel">
          <div class="ie-panel__icon">📥</div>
          <h3 class="ie-panel__title">批量导入</h3>
          <p class="ie-panel__desc">上传包含 courses / students / enrollments 工作表的 Excel 文件</p>
          <label class="ie-upload-btn">
            选择文件上传
            <input type="file" accept=".xlsx,.xls" hidden @change="handleImport" :disabled="importing" />
          </label>
          <LoadingSpinner v-if="importing" size="sm" text="导入中..." class="ie-spinner" />
          <div v-if="importSummary" class="import-result">
            <h4>导入结果</h4>
            <div class="import-grid">
              <div class="import-item"><span>课程创建</span><strong>{{ importSummary.courses_created || 0 }}</strong></div>
              <div class="import-item"><span>课程跳过</span><strong>{{ importSummary.courses_skipped || 0 }}</strong></div>
              <div class="import-item"><span>学生创建</span><strong>{{ importSummary.students_created || 0 }}</strong></div>
              <div class="import-item"><span>教师创建</span><strong>{{ importSummary.teachers_created || 0 }}</strong></div>
              <div class="import-item"><span>选课创建</span><strong>{{ importSummary.enrollments_created || 0 }}</strong></div>
            </div>
            <div v-if="importSummary.errors?.length" class="import-errors">
              <p v-for="(err, i) in importSummary.errors" :key="i" class="import-err">{{ err }}</p>
            </div>
          </div>
        </div>
        <!-- Export -->
        <div class="ie-panel">
          <div class="ie-panel__icon">📤</div>
          <h3 class="ie-panel__title">成绩导出</h3>
          <p class="ie-panel__desc">选择课程导出 Excel 格式的成绩单</p>
          <select v-model="exportCourseId" class="ie-select">
            <option :value="null">选择课程</option>
            <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.course_code }} {{ c.name }}</option>
          </select>
          <button class="ie-export-btn" @click="exportGrades" :disabled="!exportCourseId || exporting">
            {{ exporting ? '导出中...' : '导出 Excel' }}
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import LoadingSpinner from '../../components/shared/LoadingSpinner.vue'

const props = defineProps({ courses: { type: Array, default: () => [] } })
const emit = defineEmits(['changed'])
const API = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api'
const importing = ref(false); const exporting = ref(false)
const importSummary = ref(null); const exportCourseId = ref(null)

async function handleImport(e) {
  const file = e.target.files[0]; if (!file) return
  importing.value = true; importSummary.value = null
  const fd = new FormData(); fd.append('file', file)
  try {
    const r = await fetch(`${API}/import/courses`, { method: 'POST', credentials: 'include', body: fd })
    importSummary.value = await r.json()
    emit('changed')
  } catch (e) { alert(e.message) } finally { importing.value = false; e.target.value = '' }
}

async function exportGrades() {
  exporting.value = true
  try {
    const r = await fetch(`${API}/courses/${exportCourseId.value}/grades/export`, { credentials: 'include' })
    const blob = await r.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url; a.download = `grades_${exportCourseId.value}.xlsx`
    a.click(); URL.revokeObjectURL(url)
  } catch (e) { alert('导出失败') } finally { exporting.value = false }
}
</script>

<style scoped>
.card--glass { background: var(--color-bg-glass); backdrop-filter: var(--blur-glass); -webkit-backdrop-filter: var(--blur-glass); border: 1px solid var(--color-border); border-radius: var(--radius-xl); overflow: hidden; box-shadow: var(--shadow-sm); }
.card__header { padding: var(--space-5) var(--space-6) var(--space-3); }
.card__title { font-size: var(--text-lg); font-weight: var(--weight-bold); }
.card__body { padding: 0 var(--space-6) var(--space-6); }
.ie-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-6); }
@media (max-width: 640px) { .ie-grid { grid-template-columns: 1fr; } }
.ie-panel {
  text-align: center; padding: var(--space-6);
  background: var(--color-bg-secondary); border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
}
.ie-panel__icon { font-size: 2.5rem; margin-bottom: var(--space-4); }
.ie-panel__title { font-size: var(--text-lg); font-weight: var(--weight-bold); margin-bottom: var(--space-2); }
.ie-panel__desc { font-size: var(--text-sm); color: var(--color-text-secondary); margin-bottom: var(--space-5); }
.ie-upload-btn, .ie-export-btn {
  display: inline-block; padding: var(--space-2) var(--space-5);
  background: var(--color-accent); color: white;
  border-radius: var(--radius-md); font-size: var(--text-sm); font-weight: var(--weight-semibold);
  transition: all var(--duration-fast); cursor: pointer;
}
.ie-upload-btn:hover, .ie-export-btn:hover:not(:disabled) { background: var(--color-accent-hover); }
.ie-export-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.ie-select {
  display: block; width: 100%; padding: var(--space-2) var(--space-3);
  border: 1px solid var(--color-border); border-radius: var(--radius-md);
  font-size: var(--text-sm); margin-bottom: var(--space-3);
  background: var(--color-bg-elevated); outline: none;
}
.ie-spinner { margin-top: var(--space-4); }
.import-result { margin-top: var(--space-4); text-align: left; background: var(--color-bg-elevated); padding: var(--space-4); border-radius: var(--radius-md); border: 1px solid var(--color-border); }
.import-result h4 { font-size: var(--text-sm); font-weight: var(--weight-semibold); margin-bottom: var(--space-3); }
.import-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-2); }
.import-item { display: flex; justify-content: space-between; font-size: var(--text-xs); padding: var(--space-1) 0; }
.import-item strong { font-weight: var(--weight-bold); color: var(--color-accent); }
.import-errors { margin-top: var(--space-3); }
.import-err { font-size: var(--text-xs); color: var(--color-danger); }
</style>
