<template>
  <div class="page">
    <header class="hero">
      <div class="hero-content">
        <p class="eyebrow">✨ 管理员界面</p>
        <h1 class="hero-title">学生选课与成绩管理系统</h1>
        <p class="subtitle">欢迎，<strong>管理员</strong> · 完整权限</p>
        <div class="status" :class="health.db ? 'ok' : 'bad'">
          <span class="status-dot" :class="health.db ? 'online' : 'offline'"></span>
          {{ health.db ? '✓ 后端连接正常' : '✗ 等待后端连接' }}
        </div>
      </div>
      <div class="stat-panel" v-if="stats.counts">
        <div class="stat-card">
          <div class="stat-value">{{ stats.counts.students }}</div>
          <div class="stat-label">学生</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.counts.teachers }}</div>
          <div class="stat-label">教师</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.counts.courses }}</div>
          <div class="stat-label">课程</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.counts.enrollments }}</div>
          <div class="stat-label">选课</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ enrollmentRate }}</div>
          <div class="stat-label">选课率</div>
        </div>
        <button @click="handleLogout" class="btn-logout-hero">退出登录</button>
      </div>
    </header>

    <section class="grid">
      <article class="card" style="--accent: #3b82f6;">
        <header class="card-header">
          <h2>👥 新增学生</h2>
          <p class="card-desc">创建学生账户，输入学号和姓名</p>
        </header>
        <form @submit.prevent="createStudent" class="form-grid">
          <label class="form-group">
            <span class="label-text">学号</span>
            <input v-model="studentForm.student_no" required placeholder="例: S001" />
          </label>
          <label class="form-group">
            <span class="label-text">姓名</span>
            <input v-model="studentForm.name" required placeholder="例: 张三" />
          </label>
          <label class="form-group">
            <span class="label-text">专业</span>
            <input v-model="studentForm.major" placeholder="例: 计算机科学" />
          </label>
          <button type="submit" class="btn-primary">+ 添加学生</button>
        </form>
        <div class="list" v-if="students.length">
          <div class="list-header">
            <h3 class="list-title">📋 学生列表 ({{ filteredStudents.length }}/{{ students.length }})</h3>
            <button class="btn-collapse" @click="studentsCollapsed = !studentsCollapsed">
              {{ studentsCollapsed ? '展开 ▼' : '折叠 ▲' }}
            </button>
          </div>
          <div class="search-box" v-show="!studentsCollapsed">
            <input 
              v-model="studentSearch" 
              placeholder="🔍 搜索学号、姓名或专业..." 
              class="search-input"
            />
          </div>
          <transition name="collapse">
            <div v-show="!studentsCollapsed">
              <div class="item-card" v-for="s in filteredStudents" :key="s.id">
                <div class="item-content">
                  <div class="item-badge">{{ s.student_no }}</div>
                  <div class="item-details">
                    <div class="item-name">{{ s.name }}</div>
                    <div class="item-meta">{{ s.major || '未填专业' }}</div>
                  </div>
                </div>
                <button class="btn-danger-sm" @click="deleteStudent(s.id)">删除</button>
              </div>
              <div class="empty-state" v-if="filteredStudents.length === 0 && studentSearch">
                <p>未找到匹配的学生</p>
              </div>
            </div>
          </transition>
        </div>
        <div class="empty-state" v-else>
          <p>暂无学生记录</p>
        </div>
      </article>

      <article class="card" style="--accent: #8b5cf6;">
        <header class="card-header">
          <h2>🎓 新增教师</h2>
          <p class="card-desc">创建教师账户，输入工号和姓名</p>
        </header>
        <form @submit.prevent="createTeacher" class="form-grid">
          <label class="form-group">
            <span class="label-text">工号</span>
            <input v-model="teacherForm.teacher_no" required placeholder="例: T001" />
          </label>
          <label class="form-group">
            <span class="label-text">姓名</span>
            <input v-model="teacherForm.name" required placeholder="例: 王老师" />
          </label>
          <label class="form-group">
            <span class="label-text">院系</span>
            <input v-model="teacherForm.department" placeholder="例: 计算机学院" />
          </label>
          <button type="submit" class="btn-primary">+ 添加教师</button>
        </form>
        <div class="list" v-if="teachers.length">
          <div class="list-header">
            <h3 class="list-title">📋 教师列表 ({{ filteredTeachers.length }}/{{ teachers.length }})</h3>
            <button class="btn-collapse" @click="teachersCollapsed = !teachersCollapsed">
              {{ teachersCollapsed ? '展开 ▼' : '折叠 ▲' }}
            </button>
          </div>
          <div class="search-box" v-show="!teachersCollapsed">
            <input 
              v-model="teacherSearch" 
              placeholder="🔍 搜索工号、姓名或院系..." 
              class="search-input"
            />
          </div>
          <transition name="collapse">
            <div v-show="!teachersCollapsed">
              <div class="item-card" v-for="t in filteredTeachers" :key="t.id">
                <div class="item-content">
                  <div class="item-badge" style="background: #f3e8ff; color: #6d28d9;">{{ t.teacher_no }}</div>
                  <div class="item-details">
                    <div class="item-name">{{ t.name }}</div>
                    <div class="item-meta">{{ t.department || '未填院系' }}</div>
                  </div>
                </div>
                <button class="btn-danger-sm" @click="deleteTeacher(t.id)">删除</button>
              </div>
              <div class="empty-state" v-if="filteredTeachers.length === 0 && teacherSearch">
                <p>未找到匹配的教师</p>
              </div>
            </div>
          </transition>
        </div>
        <div class="empty-state" v-else>
          <p>暂无教师记录</p>
        </div>
      </article>

      <article class="card" style="--accent: #ec4899;">
        <header class="card-header">
          <h2>📚 新增课程</h2>
          <p class="card-desc">创建课程，可关联授课教师</p>
        </header>
        <form @submit.prevent="createCourse" class="form-grid">
          <label class="form-group">
            <span class="label-text">课程号</span>
            <input v-model="courseForm.course_code" required placeholder="例: C001" />
          </label>
          <label class="form-group">
            <span class="label-text">课程名</span>
            <input v-model="courseForm.name" required placeholder="例: 数据库原理" />
          </label>
          <label class="form-group">
            <span class="label-text">学分</span>
            <input type="number" step="0.5" v-model.number="courseForm.credit" placeholder="例: 3" />
          </label>
          <label class="form-group">
            <span class="label-text">容量</span>
            <input type="number" v-model.number="courseForm.capacity" placeholder="例: 50" />
          </label>
          <label class="form-group">
            <span class="label-text">授课教师</span>
            <select v-model.number="courseForm.teacher_id">
              <option :value="null">── 未指定教师</option>
              <option v-for="t in teachers" :value="t.id" :key="t.id">{{ t.name }}</option>
            </select>
          </label>
          <button type="submit" class="btn-primary">+ 添加课程</button>
        </form>
        <div class="list" v-if="courses.length">
          <div class="list-header">
            <h3 class="list-title">📋 课程列表 ({{ filteredCourses.length }}/{{ courses.length }})</h3>
            <button class="btn-collapse" @click="coursesCollapsed = !coursesCollapsed">
              {{ coursesCollapsed ? '展开 ▼' : '折叠 ▲' }}
            </button>
          </div>
          <div class="search-box" v-show="!coursesCollapsed">
            <input 
              v-model="courseSearch" 
              placeholder="🔍 搜索课程号、课程名或教师..." 
              class="search-input"
            />
          </div>
          <transition name="collapse">
            <div v-show="!coursesCollapsed">
              <div class="item-card" v-for="c in filteredCourses" :key="c.id">
                <div class="item-content">
                  <div class="item-badge" style="background: #fce7f3; color: #be185d;">{{ c.course_code }}</div>
                  <div class="item-details">
                    <div class="item-name">{{ c.name }}</div>
                    <div class="item-meta">{{ c.teacher_name || '暂无教师' }} · {{ c.credit }}学分</div>
                  </div>
                </div>
                <button class="btn-danger-sm" @click="deleteCourse(c.id)">删除</button>
              </div>
              <div class="empty-state" v-if="filteredCourses.length === 0 && courseSearch">
                <p>未找到匹配的课程</p>
              </div>
            </div>
          </transition>
        </div>
        <div class="empty-state" v-else>
          <p>暂无课程记录</p>
        </div>
      </article>

      <article class="card" style="--accent: #14b8a6;">
        <header class="card-header">
          <h2>⭐ 选课/退课与成绩</h2>
          <p class="card-desc">管理选课关系和成绩信息</p>
        </header>
        <form class="enroll-form" @submit.prevent="enroll">
          <div class="form-row">
            <label class="form-group">
              <span class="label-text">学生</span>
              <select v-model.number="enrollForm.student_id" required>
                <option disabled value="">请选择学生</option>
                <option v-for="s in students" :value="s.id" :key="s.id">{{ s.name }}</option>
              </select>
            </label>
            <label class="form-group">
              <span class="label-text">课程</span>
              <select v-model.number="enrollForm.course_id" required>
                <option disabled value="">请选择课程</option>
                <option v-for="c in courses" :value="c.id" :key="c.id">{{ c.name }}</option>
              </select>
            </label>
          </div>
          <button type="submit" class="btn-primary">✓ 选课</button>
        </form>

        <div class="list" v-if="enrollments.length">
          <div class="list-header">
            <h3 class="list-title">📋 选课记录 ({{ filteredEnrollments.length }}/{{ enrollments.length }})</h3>
            <button class="btn-collapse" @click="toggleEnrollmentsCollapsed">
              {{ enrollmentsCollapsed ? '展开 ▼' : '折叠 ▲' }}
            </button>
          </div>
          <div class="search-box" v-show="!enrollmentsCollapsed">
            <input 
              v-model="enrollmentSearch" 
              placeholder="🔍 搜索学生、学号、课程或教师..." 
              class="search-input"
            />
          </div>
          <transition name="collapse">
            <div v-show="!enrollmentsCollapsed">
              <div class="enrollment-item" v-for="e in filteredEnrollments" :key="e.id">
                <div class="enrollment-info">
                  <div class="enrollment-header">
                    <strong>{{ e.student_name }} ({{ e.student_no }})</strong>
                    <span class="divider">→</span>
                    <strong>{{ e.course_name }}</strong>
                  </div>
                  <div class="enrollment-meta">
                    <span>教师: {{ e.teacher_name || '未分配' }}</span>
                    <div class="grade-display">
                      <span class="grade-tag" v-if="e.ordinary_score !== null">平时: <strong>{{ e.ordinary_score }}</strong></span>
                      <span class="grade-tag" v-if="e.final_score !== null">期末: <strong>{{ e.final_score }}</strong></span>
                      <span class="grade-tag final" v-if="e.final_grade !== null">最终: <strong>{{ e.final_grade }}</strong></span>
                      <span class="grade-tag" v-else-if="e.grade !== null">成绩: <strong>{{ e.grade }}</strong></span>
                    </div>
                  </div>
                </div>
                <div class="enrollment-actions">
                  <button class="btn-info-sm" @click="toggleGradeEditor(e.id)" type="button">
                    {{ expandedGradeEditors[e.id] ? '收起 ▲' : '编辑成绩 ▼' }}
                  </button>
                  <button class="btn-danger-sm" @click="dropCourse(e.id)">退课</button>
                </div>
                <!-- Grade Editor Panel -->
                <transition name="expand">
                  <div v-show="expandedGradeEditors[e.id]" class="grade-editor-panel">
                    <div class="editor-form">
                      <div class="form-row">
                        <label class="form-group">
                          <span class="label-text">平时成绩 (0-100)</span>
                          <input 
                            type="number" 
                            step="0.5" 
                            min="0" 
                            max="100" 
                            placeholder="输入平时成绩"
                            :value="(gradeEditForm[e.id]?.ordinary_score) ?? ''"
                            @input="(event) => {
                              if (!gradeEditForm[e.id]) gradeEditForm[e.id] = {};
                              gradeEditForm[e.id].ordinary_score = event.target.value ? parseFloat(event.target.value) : null;
                            }"
                          />
                        </label>
                        <label class="form-group">
                          <span class="label-text">期末成绩 (0-100)</span>
                          <input 
                            type="number" 
                            step="0.5" 
                            min="0" 
                            max="100" 
                            placeholder="输入期末成绩"
                            :value="(gradeEditForm[e.id]?.final_score) ?? ''"
                            @input="(event) => {
                              if (!gradeEditForm[e.id]) gradeEditForm[e.id] = {};
                              gradeEditForm[e.id].final_score = event.target.value ? parseFloat(event.target.value) : null;
                            }"
                          />
                        </label>
                      </div>
                      <div class="form-row">
                        <label class="form-group">
                          <span class="label-text">平时占比</span>
                          <div class="weight-input">
                            <input 
                              type="number" 
                              step="0.01" 
                              min="0" 
                              max="1" 
                              placeholder="0.5"
                              :value="(gradeEditForm[e.id]?.ordinary_weight) ?? 0.5"
                              @input="(event) => {
                                if (!gradeEditForm[e.id]) gradeEditForm[e.id] = {};
                                gradeEditForm[e.id].ordinary_weight = event.target.value ? parseFloat(event.target.value) : 0.5;
                              }"
                              @change="() => autoCalcWeight(e.id, 'ordinary')"
                            />
                            <span class="weight-percent">{{ (Number(gradeEditForm[e.id]?.ordinary_weight ?? 0.5) * 100).toFixed(0) }}%</span>
                          </div>
                        </label>
                        <label class="form-group">
                          <span class="label-text">期末占比</span>
                          <div class="weight-input">
                            <input 
                              type="number" 
                              step="0.01" 
                              min="0" 
                              max="1" 
                              placeholder="0.5"
                              :value="(gradeEditForm[e.id]?.final_weight) ?? 0.5"
                              @input="(event) => {
                                if (!gradeEditForm[e.id]) gradeEditForm[e.id] = {};
                                gradeEditForm[e.id].final_weight = event.target.value ? parseFloat(event.target.value) : 0.5;
                              }"
                              @change="() => autoCalcWeight(e.id, 'final')"
                            />
                            <span class="weight-percent">{{ (Number(gradeEditForm[e.id]?.final_weight ?? 0.5) * 100).toFixed(0) }}%</span>
                          </div>
                        </label>
                      </div>
                      <div class="weight-info">
                        占比和: <strong :class="{ valid: Math.abs(Number(gradeEditForm[e.id]?.ordinary_weight ?? 0.5) + Number(gradeEditForm[e.id]?.final_weight ?? 0.5) - 1) < 0.01 }">
                          {{ (Number(gradeEditForm[e.id]?.ordinary_weight ?? 0.5) + Number(gradeEditForm[e.id]?.final_weight ?? 0.5)).toFixed(2) }}
                        </strong>
                      </div>
                      <div class="preview-info">
                        <strong>预计最终成绩:</strong>
                        {{ calcPreviewGrade(e.id) }}
                      </div>
                      <div class="editor-buttons">
                        <button class="btn-success-sm" @click="updateStudentGrades(e.id)" type="button">✓ 保存</button>
                        <button class="btn-secondary-sm" @click="toggleGradeEditor(e.id)" type="button">取消</button>
                      </div>
                    </div>
                  </div>
                </transition>
              </div>
              <div class="empty-state" v-if="filteredEnrollments.length === 0 && enrollmentSearch">
                <p>未找到匹配的选课记录</p>
              </div>
            </div>
          </transition>
        </div>
        <div class="empty-state" v-else>
          <p>暂无选课记录</p>
        </div>
      </article>

      <article class="card" style="--accent: #f59e0b;">
        <header class="card-header">
          <h2>📥 Excel导入/导出</h2>
          <p class="card-desc">批量导入课程与学生名单，导出课程成绩</p>
        </header>

        <div class="import-box">
          <label class="upload-btn">
            <input type="file" accept=".xlsx,.xls" @change="importExcel" />
            <span>{{ importLoading ? '正在导入...' : '上传Excel导入' }}</span>
          </label>
          <p class="help-text">工作表要求：courses(必填)，可选 students、enrollments</p>
          <p class="error-text" v-if="importError">{{ importError }}</p>
          <div class="summary" v-if="importSummary">
            <div>课程新增 {{ importSummary.courses_created }}，跳过 {{ importSummary.courses_skipped }}</div>
            <div>学生新增 {{ importSummary.students_created }}，跳过 {{ importSummary.students_skipped }}</div>
            <div>教师新增 {{ importSummary.teachers_created }}</div>
            <div>选课新增 {{ importSummary.enrollments_created }}，跳过 {{ importSummary.enrollments_skipped }}</div>
            <div v-if="importSummary.errors?.length" class="error-list">
              <strong>提醒:</strong>
              <ul>
                <li v-for="(e, idx) in importSummary.errors" :key="idx">{{ e }}</li>
              </ul>
            </div>
          </div>
        </div>

        <div class="export-box">
          <div class="form-row">
            <label class="form-group">
              <span class="label-text">选择课程</span>
              <select v-model.number="exportCourseId">
                <option :value="''">请选择课程</option>
                <option v-for="c in courses" :value="c.id" :key="c.id">{{ c.name }}</option>
              </select>
            </label>
          </div>
          <button class="btn-primary" @click="exportGrades" :disabled="!exportCourseId || exportLoading">
            {{ exportLoading ? '生成中...' : '导出成绩Excel' }}
          </button>
          <p class="error-text" v-if="exportError">{{ exportError }}</p>
        </div>
      </article>
    </section>

    <section class="card stats-card" v-if="stats.course_avg?.length">
      <header class="card-header">
        <h2>📊 课程平均成绩统计</h2>
        <p class="card-desc">实时显示各课程的平均成绩、及格率、优秀率，可按课程号/课程名查询</p>
      </header>
      <div class="stat-filters">
        <input
          v-model="courseStatFilters.code"
          placeholder="按课程号查询..."
          class="search-input compact"
        />
        <input
          v-model="courseStatFilters.name"
          placeholder="按课程名查询..."
          class="search-input compact"
        />
        <div class="filter-actions">
          <button class="btn-secondary-sm" type="button" @click="loadStatistics">查询</button>
          <button class="btn-cancel-sm" type="button" @click="resetStatFilters">重置</button>
        </div>
      </div>
      <div class="stats-grid">
        <div class="stat-item" v-for="c in stats.course_avg" :key="c.id">
          <div class="stat-item-header">
            <span class="stat-code">{{ c.course_code }}</span>
            <span class="stat-name">{{ c.name }}</span>
          </div>
          <div class="stat-value-large">{{ c.avg_grade ?? '无' }}</div>
          <div class="stat-meta">
            <span class="stat-chip">📈 及格率 {{ formatRate(c.pass_rate) }}</span>
            <span class="stat-chip">🌟 优秀率 {{ formatRate(c.excellent_rate) }}</span>
            <span class="stat-chip">👥 选课人数 {{ c.enrolled_count ?? 0 }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Major Professional Development Plans Management Section -->
    <section class="grid">
      <article class="card" style="--accent: #10b981;">
        <header class="card-header">
          <h2>🎯 新增专业培养计划</h2>
          <p class="card-desc">为不同专业创建课程修习计划</p>
        </header>
        <form @submit.prevent="createMajorPlan" class="form-grid">
          <label class="form-group">
            <span class="label-text">专业名称</span>
            <input v-model="majorPlanForm.major_name" required placeholder="例: 计算机科学" />
          </label>
          <label class="form-group">
            <span class="label-text">描述</span>
            <input v-model="majorPlanForm.description" placeholder="例: 计算机科学专业培养计划" />
          </label>
          <button type="submit" class="btn-primary">+ 创建培养计划</button>
        </form>
        <div class="list" v-if="majorPlans.length">
          <div class="list-header">
            <h3 class="list-title">📋 培养计划列表 ({{ filteredMajorPlans.length }}/{{ majorPlans.length }})</h3>
            <button class="btn-collapse" @click="majorPlansCollapsed = !majorPlansCollapsed">
              {{ majorPlansCollapsed ? '展开 ▼' : '折叠 ▲' }}
            </button>
          </div>
          <div class="search-box" v-show="!majorPlansCollapsed">
            <input 
              v-model="majorPlanSearch" 
              placeholder="🔍 搜索专业名称..." 
              class="search-input"
            />
          </div>
          <transition name="collapse">
            <div v-show="!majorPlansCollapsed">
              <div class="item-card" v-for="plan in filteredMajorPlans" :key="plan.id">
                <div class="item-content">
                  <div class="item-badge">📚</div>
                  <div class="item-details">
                    <div class="item-name">{{ plan.major_name }}</div>
                    <div class="item-meta">{{ plan.description || '无描述' }} · {{ plan.course_count || 0 }}门课程</div>
                  </div>
                </div>
                <div class="item-actions">
                  <button class="btn-secondary-sm" @click="editingPlanId = plan.id">编辑</button>
                  <button class="btn-danger-sm" @click="deleteMajorPlan(plan.id)">删除</button>
                </div>
              </div>
              <div class="empty-state" v-if="filteredMajorPlans.length === 0 && majorPlanSearch">
                <p>未找到匹配的专业培养计划</p>
              </div>
            </div>
          </transition>
        </div>
        <div class="empty-state" v-else>
          <p>暂无专业培养计划</p>
        </div>
      </article>

      <article class="card" style="--accent: #f59e0b;">
        <header class="card-header">
          <h2>📖 为培养计划添加课程</h2>
          <p class="card-desc">指定课程在计划中的学期与是否必修</p>
        </header>
        <form @submit.prevent="addCourseToPlan" class="form-grid" v-if="majorPlans.length">
          <label class="form-group">
            <span class="label-text">选择培养计划</span>
            <select v-model.number="planCourseForm.plan_id" required>
              <option :value="''">请选择培养计划</option>
              <option v-for="plan in majorPlans" :key="plan.id" :value="plan.id">
                {{ plan.major_name }}
              </option>
            </select>
          </label>
          <label class="form-group">
            <span class="label-text">选择课程</span>
            <select v-model.number="planCourseForm.course_id" required>
              <option :value="''">请选择课程</option>
              <option v-for="c in courses" :key="c.id" :value="c.id">
                {{ c.name }}
              </option>
            </select>
          </label>
          <label class="form-group">
            <span class="label-text">学期</span>
            <select v-model.number="planCourseForm.semester" required>
              <option :value="''">请选择学期</option>
              <option v-for="s in semesterOptions" :key="s" :value="s">
                第{{ s }}学期
              </option>
            </select>
          </label>
          <label class="form-group checkbox-group">
            <input v-model="planCourseForm.is_required" type="checkbox" />
            <span class="label-text">是否为必修课</span>
          </label>
          <button type="submit" class="btn-primary">+ 添加课程到计划</button>
        </form>
        <div v-else class="empty-state">
          <p>请先创建培养计划</p>
        </div>

        <div class="plan-courses-view" v-if="selectedPlanCourses.length">
          <h4>📚 当前计划的课程</h4>
          <div class="semester-courses">
            <div v-for="semester in uniqueSemesters" :key="semester" class="semester-section">
              <div class="semester-title">第{{ semester }}学期</div>
              <div class="course-item" v-for="pc in selectedPlanCourses.filter(c => c.semester === semester)" :key="pc.id">
                <div class="course-info">
                  <span class="course-name">{{ pc.course_name }}</span>
                  <span class="course-type">{{ pc.is_required ? '必修' : '选修' }}</span>
                </div>
                <button class="btn-danger-sm" @click="removeCoursePlan(pc.id)">移除</button>
              </div>
            </div>
          </div>
        </div>
      </article>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted, computed, watch } from 'vue'

const props = defineProps({
  user: { type: Object, required: true }
})

const emit = defineEmits(['logout'])

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api'

const health = reactive({ db: false })
const students = ref([])
const teachers = ref([])
const courses = ref([])
const enrollments = ref([])
const stats = reactive({ counts: null, course_avg: [] })
const importSummary = ref(null)
const importError = ref('')
const importLoading = ref(false)
const exportCourseId = ref('')
const exportLoading = ref(false)
const exportError = ref('')
const majorPlans = ref([])
const planCourses = ref([])
const selectedPlanId = ref('')
const editingPlanId = ref('')

const studentForm = reactive({ student_no: '', name: '', major: '' })
const teacherForm = reactive({ teacher_no: '', name: '', department: '' })
const courseForm = reactive({ course_code: '', name: '', credit: 0, capacity: 50, teacher_id: null })
const enrollForm = reactive({ student_id: '', course_id: '' })
const gradeInput = reactive({})
const majorPlanForm = reactive({ major_name: '', description: '' })
const planCourseForm = reactive({ plan_id: '', course_id: '', semester: '', is_required: true })
const courseStatFilters = reactive({ code: '', name: '' })

// 折叠状态
const studentsCollapsed = ref(false)
const teachersCollapsed = ref(false)
const coursesCollapsed = ref(false)
const enrollmentsCollapsed = ref(false)
const majorPlansCollapsed = ref(false)
const expandedGradeEditors = ref({})
const gradeEditForm = ref({})

// 搜索/筛选条件
const studentSearch = ref('')
const teacherSearch = ref('')
const courseSearch = ref('')
const enrollmentSearch = ref('')
const majorPlanSearch = ref('')

// 其他常量
const semesterOptions = [1, 2, 3, 4, 5, 6, 7, 8]

const healthText = computed(() => (health.db ? '连接正常' : '等待连接'))

// 计算选课率
const enrollmentRate = computed(() => {
  if (!stats.counts || stats.counts.students === 0) return '0%'
  const rate = (stats.counts.enrollments / (stats.counts.students * stats.counts.courses || 1)) * 100
  return rate > 100 ? '100%+' : `${Math.round(rate)}%`
})

// 筛选后的列表
const filteredStudents = computed(() => {
  if (!studentSearch.value) return students.value
  const search = studentSearch.value.toLowerCase()
  return students.value.filter(s => 
    s.name.toLowerCase().includes(search) ||
    s.student_no.toLowerCase().includes(search) ||
    (s.major && s.major.toLowerCase().includes(search))
  )
})

const filteredTeachers = computed(() => {
  if (!teacherSearch.value) return teachers.value
  const search = teacherSearch.value.toLowerCase()
  return teachers.value.filter(t => 
    t.name.toLowerCase().includes(search) ||
    t.teacher_no.toLowerCase().includes(search) ||
    (t.department && t.department.toLowerCase().includes(search))
  )
})

const filteredCourses = computed(() => {
  if (!courseSearch.value) return courses.value
  const search = courseSearch.value.toLowerCase()
  return courses.value.filter(c => 
    c.name.toLowerCase().includes(search) ||
    c.course_code.toLowerCase().includes(search) ||
    (c.teacher_name && c.teacher_name.toLowerCase().includes(search))
  )
})

const filteredEnrollments = computed(() => {
  if (!enrollmentSearch.value) return enrollments.value
  const search = enrollmentSearch.value.toLowerCase()
  return enrollments.value.filter(e => 
    e.student_name.toLowerCase().includes(search) ||
    e.student_no.toLowerCase().includes(search) ||
    e.course_name.toLowerCase().includes(search) ||
    (e.teacher_name && e.teacher_name.toLowerCase().includes(search))
  )
})

const filteredMajorPlans = computed(() => {
  if (!majorPlanSearch.value) return majorPlans.value
  const search = majorPlanSearch.value.toLowerCase()
  return majorPlans.value.filter(p => 
    p.major_name.toLowerCase().includes(search) ||
    (p.description && p.description.toLowerCase().includes(search))
  )
})

const selectedPlanCourses = computed(() => {
  if (!selectedPlanId.value) return []
  return planCourses.value.filter(pc => pc.plan_id === selectedPlanId.value)
})

const uniqueSemesters = computed(() => {
  const semesters = new Set(selectedPlanCourses.value.map(c => c.semester))
  return Array.from(semesters).sort((a, b) => a - b)
})

function handleLogout() {
  emit('logout')
}

function toggleEnrollmentsCollapsed() {
  enrollmentsCollapsed.value = !enrollmentsCollapsed.value
  if (enrollmentsCollapsed.value) {
    expandedGradeEditors.value = {}
    gradeEditForm.value = {}
  }
}

async function api(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    ...options,
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

async function loadHealth() {
  try {
    const data = await api('/health')
    health.db = data.db
  } catch (err) {
    health.db = false
    console.error(err)
  }
}

async function loadAll() {
  const [s, t, c, e, mp] = await Promise.all([
    api('/students'),
    api('/teachers'),
    api('/courses'),
    api('/enrollments'),
    api('/major-plans'),
  ])
  students.value = s
  teachers.value = t
  courses.value = c
  enrollments.value = e
  majorPlans.value = mp || []
  await loadStatistics()
  await loadPlanCourseCounts()
}

async function loadStatistics() {
  const params = new URLSearchParams()
  if (courseStatFilters.code) params.append('course_code', courseStatFilters.code)
  if (courseStatFilters.name) params.append('course_name', courseStatFilters.name)

  const st = await api(`/statistics/overview${params.toString() ? `?${params.toString()}` : ''}`)
  stats.counts = st.counts
  stats.course_avg = st.course_avg || []
}

function resetStatFilters() {
  courseStatFilters.code = ''
  courseStatFilters.name = ''
  loadStatistics()
}

function formatRate(val) {
  if (val === null || val === undefined) return '—'
  const num = Number(val)
  if (Number.isNaN(num)) return '—'
  return `${num.toFixed(2)}%`
}

async function createStudent() {
  await api('/students', { method: 'POST', body: JSON.stringify(studentForm) })
  Object.assign(studentForm, { student_no: '', name: '', major: '' })
  await loadAll()
}

async function deleteStudent(id) {
  const student = students.value.find(s => s.id === id)
  if (!confirm(`确定要删除学生 "${student?.name}" 吗？`)) return
  try {
    await api(`/students/${id}`, { method: 'DELETE' })
    await loadAll()
  } catch (err) {
    alert(`删除失败: ${err.message}`)
  }
}

async function createTeacher() {
  await api('/teachers', { method: 'POST', body: JSON.stringify(teacherForm) })
  Object.assign(teacherForm, { teacher_no: '', name: '', department: '' })
  await loadAll()
}

async function deleteTeacher(id) {
  const teacher = teachers.value.find(t => t.id === id)
  if (!confirm(`确定要删除教师 "${teacher?.name}" 吗？`)) return
  try {
    await api(`/teachers/${id}`, { method: 'DELETE' })
    await loadAll()
  } catch (err) {
    alert(`删除失败: ${err.message}`)
  }
}

async function createCourse() {
  await api('/courses', { method: 'POST', body: JSON.stringify(courseForm) })
  Object.assign(courseForm, { course_code: '', name: '', credit: 0, capacity: 50, teacher_id: null })
  await loadAll()
}

async function deleteCourse(id) {
  const course = courses.value.find(c => c.id === id)
  if (!confirm(`确定要删除课程 "${course?.name}" 吗？`)) return
  try {
    await api(`/courses/${id}`, { method: 'DELETE' })
    await loadAll()
  } catch (err) {
    alert(`删除失败: ${err.message}`)
  }
}

async function enroll() {
  await api('/enrollments', { method: 'POST', body: JSON.stringify(enrollForm) })
  enrollForm.student_id = ''
  enrollForm.course_id = ''
  await loadAll()
}

async function setGrade(id) {
  const grade = gradeInput[id]
  if (grade === undefined || grade === '') return
  try {
    await api(`/enrollments/${id}/grade`, { method: 'PUT', body: JSON.stringify({ grade }) })
    await loadAll()
  } catch (err) {
    alert(`成绩更新失败: ${err.message}`)
  }
}

function toggleGradeEditor(enrollmentId) {
  const current = expandedGradeEditors.value[enrollmentId] || false
  expandedGradeEditors.value = { ...expandedGradeEditors.value, [enrollmentId]: !current }

  if (!current) {
    const enrollment = enrollments.value.find(e => e.id === enrollmentId)
    if (enrollment) {
      gradeEditForm.value = {
        ...gradeEditForm.value,
        [enrollmentId]: {
          ordinary_score: enrollment.ordinary_score ?? null,
          final_score: enrollment.final_score ?? null,
          ordinary_weight: enrollment.ordinary_weight ?? 0.5,
          final_weight: enrollment.final_weight ?? 0.5,
        },
      }
    }
  }
}

function autoCalcWeight(enrollmentId, changedField) {
  const form = gradeEditForm.value[enrollmentId]
  if (!form) return
  
  if (changedField === 'ordinary') {
    const ow = form.ordinary_weight
    if (ow !== undefined && ow !== null) {
      form.final_weight = Math.round((1 - ow) * 100) / 100
    }
  } else if (changedField === 'final') {
    const fw = form.final_weight
    if (fw !== undefined && fw !== null) {
      form.ordinary_weight = Math.round((1 - fw) * 100) / 100
    }
  }
}

function calcPreviewGrade(enrollmentId) {
  const form = gradeEditForm.value[enrollmentId]
  if (!form) return '—'
  
  const os = form.ordinary_score
  const fs = form.final_score
  const ow = form.ordinary_weight || 0.5
  const fw = form.final_weight || 0.5
  
  if (os === null || os === undefined || fs === null || fs === undefined) {
    return '—'
  }
  
  const final = Number(os) * Number(ow) + Number(fs) * Number(fw)
  return final.toFixed(1)
}

async function updateStudentGrades(enrollmentId) {
  const form = gradeEditForm.value[enrollmentId]
  if (!form) return
  
  // Validate weights sum to 1
  const totalWeight = (form.ordinary_weight || 0.5) + (form.final_weight || 0.5)
  if (Math.abs(totalWeight - 1) > 0.01) {
    alert('占比和必须等于 1，当前为: ' + totalWeight.toFixed(2))
    return
  }
  
  try {
    const payload = {
      ordinary_score: form.ordinary_score,
      final_score: form.final_score,
      ordinary_weight: form.ordinary_weight,
      final_weight: form.final_weight,
    }
    
    await api(`/enrollments/${enrollmentId}/grades`, { 
      method: 'PUT', 
      body: JSON.stringify(payload) 
    })
    
    alert('成绩更新成功')
    toggleGradeEditor(enrollmentId)
    await loadAll()
  } catch (err) {
    alert(`成绩更新失败: ${err.message}`)
  }
}

async function dropCourse(id) {
  const enrollment = enrollments.value.find(e => e.id === id)
  if (!confirm(`确定要删除 "${enrollment?.student_name}" 选的 "${enrollment?.course_name}" 吗？`)) return
  try {
    await api(`/enrollments/${id}`, { method: 'DELETE' })
    await loadAll()
  } catch (err) {
    alert(`删除选课失败: ${err.message}`)
  }
}

async function importExcel(event) {
  const file = event.target.files?.[0]
  if (!file) return
  importError.value = ''
  importSummary.value = null
  importLoading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    const res = await fetch(`${API_BASE}/import/courses`, {
      method: 'POST',
      body: formData,
      credentials: 'include',
    })
    const data = await res.json()
    if (!res.ok || data.success === false) throw new Error(data.message || '导入失败')
    importSummary.value = data.summary || null
    await loadAll()
  } catch (err) {
    importError.value = err.message
  } finally {
    importLoading.value = false
    event.target.value = ''
  }
}

async function exportGrades() {
  if (!exportCourseId.value) return
  exportError.value = ''
  exportLoading.value = true
  try {
    const res = await fetch(`${API_BASE}/courses/${exportCourseId.value}/grades/export`, {
      credentials: 'include',
    })
    if (!res.ok) throw new Error(await res.text())
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    
    // 构造文件名：<课程名称>-<老师名称>-<导出时间>.xlsx
    const course = courses.value.find(c => c.id === exportCourseId.value)
    const courseName = (course?.name || '未知课程').replace(/\//g, '-')
    const teacherName = (course?.teacher_name || '未指定教师').replace(/\//g, '-')
    const timestamp = new Date().toISOString().slice(0, 19).replace(/T/, '-').replace(/:/g, '')
    const filename = `${courseName}-${teacherName}-${timestamp}.xlsx`
    
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  } catch (err) {
    exportError.value = err.message
  } finally {
    exportLoading.value = false
  }
}

// Major Plan Functions
async function createMajorPlan() {
  try {
    await api('/major-plans', { method: 'POST', body: JSON.stringify(majorPlanForm) })
    majorPlanForm.major_name = ''
    majorPlanForm.description = ''
    await loadAll()
  } catch (err) {
    alert(`创建培养计划失败: ${err.message}`)
  }
}

async function deleteMajorPlan(id) {
  const plan = majorPlans.value.find(p => p.id === id)
  if (!confirm(`确定要删除培养计划 "${plan?.major_name}" 吗？`)) return
  try {
    await api(`/major-plans/${id}`, { method: 'DELETE' })
    await loadAll()
  } catch (err) {
    alert(`删除失败: ${err.message}`)
  }
}

async function addCourseToPlan() {
  try {
    await api(`/major-plans/${planCourseForm.plan_id}/courses`, {
      method: 'POST',
      body: JSON.stringify({
        course_id: planCourseForm.course_id,
        semester: planCourseForm.semester,
        is_required: planCourseForm.is_required,
      }),
    })
    selectedPlanId.value = planCourseForm.plan_id
    planCourseForm.course_id = ''
    planCourseForm.semester = ''
    planCourseForm.is_required = true
    await loadMajorPlanCourses()
    await loadAll()
  } catch (err) {
    alert(`添加课程失败: ${err.message}`)
  }
}

async function removeCoursePlan(courseId) {
  try {
    await api(`/major-plans/courses/${courseId}`, { method: 'DELETE' })
    await loadMajorPlanCourses()
    await loadAll()
  } catch (err) {
    alert(`移除课程失败: ${err.message}`)
  }
}

async function loadMajorPlanCourses() {
  if (!selectedPlanId.value) {
    planCourses.value = []
    return
  }
  try {
    const data = await api(`/major-plans/${selectedPlanId.value}/courses`)
    planCourses.value = data
  } catch (err) {
    console.error('加载计划课程失败:', err)
    planCourses.value = []
  }
}

// 加载所有培养计划的课程数量并更新列表展示
async function loadPlanCourseCounts() {
  if (!majorPlans.value.length) return
  try {
    const results = await Promise.all(
      majorPlans.value.map(async (p) => {
        try {
          const data = await api(`/major-plans/${p.id}/courses`)
          return { id: p.id, count: Array.isArray(data) ? data.length : 0 }
        } catch (_) {
          return { id: p.id, count: p.course_count ?? 0 }
        }
      })
    )
    const countMap = Object.fromEntries(results.map(r => [r.id, r.count]))
    majorPlans.value = majorPlans.value.map(p => ({
      ...p,
      course_count: countMap[p.id] ?? (p.course_count ?? 0),
    }))
  } catch (err) {
    console.error('加载培养计划课程数量失败:', err)
  }
}

onMounted(async () => {
  await loadHealth()
  await loadAll()
})

// 当选择的培养计划变化时，自动加载该计划的课程
watch(
  () => planCourseForm.plan_id,
  async (newPlanId) => {
    selectedPlanId.value = newPlanId || ''
    await loadMajorPlanCourses()
  }
)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+SC:wght@400;500;600;700&display=swap');

:global(body) {
  margin: 0;
  font-family: 'Inter', 'Noto Sans SC', system-ui, -apple-system, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%);
  background-size: 400% 400%;
  animation: gradient-shift 15s ease infinite;
  color: #0f172a;
  min-height: 100vh;
}

@keyframes gradient-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.page {
  max-width: 1280px;
  margin: 0 auto;
  padding: 40px 24px 60px;
}

/* ===== HERO SECTION ===== */
.hero {
  display: flex;
  justify-content: space-between;
  gap: 40px;
  align-items: flex-start;
  padding: 48px 48px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 24px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15), 0 0 1px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.5);
  animation: fade-in 0.6s ease-out;
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.hero-content {
  flex: 1;
}

.eyebrow {
  letter-spacing: 0.15em;
  text-transform: uppercase;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 800;
  margin: 0 0 8px 0;
  font-size: 12px;
}

.hero-title {
  margin: 0 0 12px 0;
  font-size: 42px;
  font-weight: 800;
  background: linear-gradient(135deg, #0f172a 0%, #334155 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.02em;
}

.subtitle {
  color: #64748b;
  margin: 0 0 16px 0;
  font-size: 16px;
  line-height: 1.6;
  max-width: 500px;
}

.status {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding: 12px 16px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 14px;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.status.ok {
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
  color: #166534;
  border-color: #86efac;
}

.status.bad {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #991b1b;
  border-color: #fca5a5;
}

.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

.status-dot.online {
  background: #22c55e;
}

.status-dot.offline {
  background: #ef4444;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* ===== STAT PANEL ===== */
.stat-panel {
  display: flex;
  align-items: stretch;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.stat-card {
  padding: 14px 16px;
  min-width: 110px;
  border-radius: 14px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 1px solid #7dd3fc;
  text-align: center;
  transition: all 0.25s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 18px rgba(56, 189, 248, 0.25);
}

.stat-value {
  font-size: 26px;
  font-weight: 800;
  background: linear-gradient(135deg, #0284c7 0%, #06b6d4 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  font-size: 11px;
  font-weight: 700;
  color: #0c4a6e;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-top: 2px;
}

/* ===== GRID LAYOUT ===== */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
  margin-top: 32px;
}

/* ===== CARD STYLES ===== */
.card {
  background: white;
  border-radius: 20px;
  padding: 28px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.08);
  border: 1px solid #f0f1f3;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  animation: slide-up 0.6s ease-out;
}

@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 48px rgba(0, 0, 0, 0.12);
  border-color: var(--accent, #3b82f6);
}

.card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--accent, #3b82f6), transparent);
  border-radius: 20px 20px 0 0;
}

.card-header {
  margin-bottom: 20px;
  border-bottom: 2px solid #f0f1f3;
  padding-bottom: 16px;
}

.card-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #0f172a;
}

.card-desc {
  margin: 8px 0 0 0;
  color: #64748b;
  font-size: 13px;
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: 32px 16px;
  color: #94a3b8;
  font-size: 14px;
}

/* ===== FORM STYLES ===== */
.form-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.label-text {
  font-weight: 700;
  color: #0f172a;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

input, select {
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  padding: 12px 14px;
  font-size: 14px;
  font-family: inherit;
  outline: none;
  transition: all 0.3s ease;
  background: #f8fafc;
}

input::placeholder, select::placeholder {
  color: #cbd5e1;
}

input:focus, select:focus {
  border-color: var(--accent, #3b82f6);
  background: white;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  transform: translateY(-1px);
}

/* ===== BUTTON STYLES ===== */
.btn-primary {
  border: none;
  border-radius: 12px;
  padding: 12px 24px;
  font-weight: 700;
  font-size: 14px;
  background: linear-gradient(135deg, var(--accent, #3b82f6) 0%, rgba(59, 130, 246, 0.8) 100%);
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 28px rgba(59, 130, 246, 0.4);
}

.btn-primary:active {
  transform: translateY(0);
}

.btn-danger-sm {
  border: 1px solid #fee2e2;
  border-radius: 8px;
  padding: 6px 12px;
  font-weight: 600;
  font-size: 12px;
  background: #fef2f2;
  color: #b91c1c;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-danger-sm:hover {
  background: #fee2e2;
  border-color: #fecaca;
}

.btn-success-sm {
  border: 1px solid #dcfce7;
  border-radius: 8px;
  padding: 6px 12px;
  font-weight: 600;
  font-size: 12px;
  background: #f0fdf4;
  color: #166534;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-success-sm:hover {
  background: #dcfce7;
  border-color: #86efac;
}

.btn-logout-hero {
  padding: 10px 16px;
  border: none;
  border-radius: 10px;
  background: #ef4444;
  color: white;
  font-weight: 700;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.btn-logout-hero:hover {
  background: #dc2626;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(239, 68, 68, 0.4);
}

/* ===== LIST STYLES ===== */
.list {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.list-title {
  margin: 0 0 16px 0;
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.item-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  transition: all 0.2s ease;
}

.item-card:hover {
  border-color: var(--accent, #3b82f6);
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.item-content {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.item-badge {
  padding: 6px 12px;
  border-radius: 8px;
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #1e40af;
  font-weight: 700;
  font-size: 12px;
  text-transform: uppercase;
  white-space: nowrap;
}

.item-details {
  flex: 1;
  min-width: 0;
}

.item-name {
  font-weight: 700;
  color: #0f172a;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-meta {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ===== ENROLLMENT STYLES ===== */
.enroll-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 12px;
}

.enrollment-item {
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  transition: all 0.2s ease;
}

.enrollment-item:hover {
  border-color: var(--accent, #14b8a6);
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.enrollment-header {
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 8px;
}

.divider {
  color: #cbd5e1;
  margin: 0 8px;
}

.enrollment-info {
  margin-bottom: 12px;
}

.enrollment-meta {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  font-size: 12px;
  color: #64748b;
}

.grade-tag {
  background: #fef3c7;
  color: #92400e;
  padding: 4px 8px;
  border-radius: 6px;
  font-weight: 600;
}

.grade-tag.final {
  background: #e0e7ff;
  color: #3730a3;
}

.grade-display {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 8px;
}

.enrollment-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.grade-input-group {
  display: flex;
  gap: 6px;
  flex: 1;
  min-width: 200px;
}

.grade-input-group input {
  flex: 1;
  padding: 8px 10px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 13px;
}

.btn-info-sm {
  border: 1px solid #dbeafe;
  border-radius: 8px;
  padding: 6px 12px;
  font-weight: 600;
  font-size: 12px;
  background: #f0f9ff;
  color: #0c4a6e;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-info-sm:hover {
  background: #e0f2fe;
  border-color: #7dd3fc;
}

.btn-secondary-sm {
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 6px 12px;
  font-weight: 600;
  font-size: 12px;
  background: #f3f4f6;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary-sm:hover {
  background: #e5e7eb;
  border-color: #9ca3af;
}

/* Grade Editor Panel */
.grade-editor-panel {
  margin-top: 12px;
  padding: 16px;
  border: 2px solid #3b82f6;
  border-radius: 10px;
  background: #f0f9ff;
  display: block;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.editor-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.weight-input {
  display: flex;
  align-items: center;
  gap: 8px;
}

.weight-input input {
  flex: 1;
  padding: 8px 10px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 13px;
}

.weight-percent {
  min-width: 45px;
  text-align: right;
  font-weight: 600;
  color: #1e40af;
  font-size: 12px;
}

.weight-info {
  padding: 10px;
  border-radius: 8px;
  background: white;
  border: 1px solid #bfdbfe;
  font-size: 13px;
  color: #0c4a6e;
}

.weight-info strong {
  margin-left: 4px;
  font-weight: 700;
}

.weight-info strong.valid {
  color: #16a34a;
}

.weight-info strong:not(.valid) {
  color: #dc2626;
}

.preview-info {
  padding: 10px;
  border-radius: 8px;
  background: white;
  border: 1px solid #dbeafe;
  font-size: 13px;
  color: #0c4a6e;
  font-weight: 600;
}

.editor-buttons {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  margin-top: 8px;
}

/* ===== IMPORT / EXPORT ===== */
.import-box, .export-box {
  margin-top: 12px;
  padding: 16px;
  border: 1px dashed #f59e0b;
  border-radius: 12px;
  background: #fff7ed;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.upload-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 10px;
  background: #f59e0b;
  color: #fff;
  cursor: pointer;
  font-weight: 700;
  border: none;
  box-shadow: 0 10px 25px rgba(245, 158, 11, 0.25);
  position: relative;
  overflow: hidden;
}

.upload-btn input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.help-text {
  margin: 0;
  color: #b45309;
  font-size: 13px;
}

.summary {
  font-size: 13px;
  color: #92400e;
  display: grid;
  gap: 4px;
}

.error-text {
  color: #b91c1c;
  font-size: 13px;
  margin: 0;
}

.error-list {
  margin-top: 6px;
  background: #fef2f2;
  border: 1px solid #fecdd3;
  border-radius: 8px;
  padding: 8px 10px;
  color: #991b1b;
}

.error-list ul {
  padding-left: 18px;
  margin: 6px 0 0 0;
}

/* ===== STATS SECTION ===== */
.stats-card {
  margin-top: 32px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-top: 20px;
}

.stat-item {
  padding: 20px;
  border-radius: 16px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 2px solid #7dd3fc;
  transition: all 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(56, 189, 248, 0.25);
}

.stat-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.stat-code {
  font-weight: 800;
  color: #0284c7;
  font-size: 13px;
  text-transform: uppercase;
  background: white;
  padding: 4px 8px;
  border-radius: 6px;
}

.stat-name {
  color: #0c4a6e;
  font-weight: 600;
  font-size: 12px;
}

.stat-value-large {
  font-size: 36px;
  font-weight: 800;
  background: linear-gradient(135deg, #0284c7 0%, #06b6d4 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 10px;
  margin-top: 12px;
}

.search-input.compact {
  padding: 8px 10px;
  font-size: 12px;
}

.filter-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.stat-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 6px;
  margin-top: 12px;
}

.stat-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 10px;
  border-radius: 10px;
  background: #e0f2fe;
  color: #0c4a6e;
  font-weight: 600;
  font-size: 12px;
  border: 1px solid #bae6fd;
}

/* ===== 折叠与搜索功能样式 ===== */
.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.list-header .list-title {
  margin: 0;
}

.btn-collapse {
  padding: 6px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background: white;
  color: #475569;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-collapse:hover {
  border-color: var(--accent, #3b82f6);
  color: var(--accent, #3b82f6);
  background: #f8fafc;
}

.search-box {
  margin-bottom: 12px;
}

.search-input {
  width: 100%;
  padding: 10px 14px;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  font-size: 13px;
  background: white;
  transition: all 0.3s ease;
  outline: none;
}

.search-input::placeholder {
  color: #94a3b8;
}

.search-input:focus {
  border-color: var(--accent, #3b82f6);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  transform: translateY(-1px);
}

/* 折叠动画 */
.collapse-enter-active,
.collapse-leave-active {
  transition: all 0.3s ease;
  max-height: 2000px;
  overflow: hidden;
}

.collapse-enter-from,
.collapse-leave-to {
  max-height: 0;
  opacity: 0;
  transform: translateY(-10px);
}

/* 独立的展开动画，避免与外层 collapse 冲突 */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.2s ease;
  max-height: 800px;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
  transform: translateY(-6px);
}

.expand-enter-to,
.expand-leave-from {
  max-height: 800px;
  opacity: 1;
  transform: translateY(0);
}

/* ===== RESPONSIVE DESIGN ===== */
@media (max-width: 768px) {
  .page {
    padding: 24px 16px 40px;
  }

  .hero {
    flex-direction: column;
    gap: 24px;
    padding: 32px 20px;
  }

  .hero-title {
    font-size: 28px;
  }

  .stat-panel {
    justify-content: flex-start;
  }

  .card {
    padding: 20px;
  }

  .grid {
    grid-template-columns: 1fr;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .enrollment-actions {
    flex-direction: column;
  }

  .grade-input-group {
    min-width: auto;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }
}

/* Major Plan Styles */
.plan-courses-view {
  margin-top: 20px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 10px;
}

.plan-courses-view h4 {
  margin: 0 0 16px 0;
  font-size: 14px;
  color: #0f172a;
  font-weight: 600;
}

.semester-courses {
  display: grid;
  gap: 16px;
}

.semester-section {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
}

.semester-title {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 12px 16px;
  font-weight: 600;
  font-size: 14px;
}

.course-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #e2e8f0;
  transition: background 0.2s ease;
}

.course-item:last-child {
  border-bottom: none;
}

.course-item:hover {
  background: #f1f5f9;
}

.course-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.course-name {
  color: #0f172a;
  font-size: 14px;
  font-weight: 500;
}

.course-type {
  display: inline-block;
  background: #dbeafe;
  color: #1e40af;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.course-item .course-type {
  background: #fef3c7;
  color: #92400e;
}

.item-actions {
  display: flex;
  gap: 8px;
}

.btn-secondary-sm {
  padding: 6px 12px;
  background: #e0e7ff;
  color: #4f46e5;
  border: 1px solid #c7d2fe;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
}

.btn-secondary-sm:hover {
  background: #c7d2fe;
  color: #4338ca;
  transform: translateY(-1px);
}

.checkbox-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.checkbox-group input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

@media (max-width: 480px) {
  .page {
    padding: 16px 12px 32px;
  }

  .hero {
    padding: 20px 16px;
  }

  .hero-title {
    font-size: 24px;
  }

  .stat-panel {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }

  .stat-card {
    padding: 12px;
  }

  .stat-value {
    font-size: 24px;
  }

  .card {
    padding: 16px;
  }

  .card-header {
    margin-bottom: 16px;
  }

  .card-header h2 {
    font-size: 16px;
  }

  .item-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .enrollment-item {
    padding: 12px;
  }
}
</style>
