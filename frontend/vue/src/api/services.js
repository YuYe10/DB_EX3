// api/services.js
// 各个业务域的 API 服务封装
// 减少组件直接依赖 API，便于服务端迁移

import { apiClient } from './client';

/**
 * 认证服务
 */
export const AuthService = {
  login(username, password) {
    return apiClient.post('/auth/login', { username, password });
  },

  logout() {
    return apiClient.post('/auth/logout');
  },

  getCurrentUser() {
    return apiClient.get('/auth/me');
  },

  changePassword(oldPassword, newPassword) {
    return apiClient.post('/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword
    });
  }
};

/**
 * 学生服务
 */
export const StudentService = {
  getAvailableCourses() {
    return apiClient.get('/student/courses');
  },

  getEnrollments() {
    return apiClient.get('/student/enrollments');
  },

  enrollCourse(courseId) {
    return apiClient.post('/enrollments', { course_id: courseId });
  },

  dropCourse(enrollmentId) {
    return apiClient.delete(`/student/enrollments/${enrollmentId}`);
  }
};

/**
 * 教师服务
 */
export const TeacherService = {
  getCourses() {
    return apiClient.get('/teacher/courses');
  },

  getCourseStudents(courseId) {
    return apiClient.get(`/teacher/courses/${courseId}/students`);
  },

  setGrade(enrollmentId, grade) {
    return apiClient.put(`/teacher/enrollments/${enrollmentId}/grade`, { grade });
  },

  exportGrades(courseId) {
    const timestamp = new Date().toISOString().replace(/[:\-T.]/g, '').slice(0, 14);
    return apiClient.downloadFile(
      `/teacher/courses/${courseId}/grades/export`,
      `grades-${courseId}-${timestamp}.xlsx`
    );
  },

  importRoster(file) {
    return apiClient.uploadFile('/teacher/courses/import', file);
  },

  downloadSampleRoster() {
    return apiClient.downloadFile(
      '/teacher/courses/import/sample',
      'roster_sample.xlsx'
    );
  }
};

/**
 * 管理员服务
 */
export const AdminService = {
  // 学生管理
  getStudents(major = null, keyword = null) {
    return apiClient.get('/students', {
      query: { major, keyword }
    });
  },

  createStudent(data) {
    return apiClient.post('/students', data);
  },

  updateStudent(studentId, data) {
    return apiClient.put(`/students/${studentId}`, data);
  },

  deleteStudent(studentId) {
    return apiClient.delete(`/students/${studentId}`);
  },

  // 教师管理
  getTeachers() {
    return apiClient.get('/teachers');
  },

  createTeacher(data) {
    return apiClient.post('/teachers', data);
  },

  updateTeacher(teacherId, data) {
    return apiClient.put(`/teachers/${teacherId}`, data);
  },

  deleteTeacher(teacherId) {
    return apiClient.delete(`/teachers/${teacherId}`);
  },

  // 课程管理
  getCourses() {
    return apiClient.get('/courses');
  },

  createCourse(data) {
    return apiClient.post('/courses', data);
  },

  updateCourse(courseId, data) {
    return apiClient.put(`/courses/${courseId}`, data);
  },

  deleteCourse(courseId) {
    return apiClient.delete(`/courses/${courseId}`);
  },

  // 选课管理
  getEnrollments() {
    return apiClient.get('/enrollments');
  },

  createEnrollment(data) {
    return apiClient.post('/enrollments', data);
  },

  setEnrollmentGrade(enrollmentId, grade) {
    return apiClient.put(`/enrollments/${enrollmentId}/grade`, { grade });
  },

  deleteEnrollment(enrollmentId) {
    return apiClient.delete(`/enrollments/${enrollmentId}`);
  },

  // 导入导出
  importCourses(file) {
    return apiClient.uploadFile('/import/courses', file);
  },

  exportCourseGrades(courseId, courseName, teacherName) {
    const timestamp = new Date().toISOString().replace(/[:\-T.]/g, '').slice(0, 14);
    const filename = `${courseName}-${teacherName}-${timestamp}.xlsx`;
    return apiClient.downloadFile(
      `/courses/${courseId}/grades/export`,
      filename
    );
  },

  // 统计信息
  getStatistics() {
    return apiClient.get('/statistics/overview');
  },

  // 健康检查
  healthCheck() {
    return apiClient.get('/admin/health');
  }
};

export default {
  AuthService,
  StudentService,
  TeacherService,
  AdminService
};
