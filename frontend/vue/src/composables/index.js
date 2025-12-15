// composables/useAuth.js
// 认证相关的可重用逻辑

import { ref, computed, onMounted } from 'vue';
import { AuthService } from '@/api/services';

export function useAuth() {
  const user = ref(null);
  const isLoading = ref(false);
  const error = ref(null);
  const isAuthenticated = computed(() => user.value !== null);

  const login = async (username, password) => {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await AuthService.login(username, password);
      
      if (response.error) {
        error.value = response.error;
        return false;
      }

      user.value = response.data?.data?.user || response.data?.user;
      localStorage.setItem('login_username', username);
      return true;
    } catch (err) {
      error.value = '登录失败，请重试';
      return false;
    } finally {
      isLoading.value = false;
    }
  };

  const logout = async () => {
    try {
      await AuthService.logout();
      user.value = null;
      localStorage.removeItem('login_username');
    } catch (err) {
      console.error('登出失败', err);
    }
  };

  const changePassword = async (oldPassword, newPassword) => {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await AuthService.changePassword(oldPassword, newPassword);
      
      if (response.error) {
        error.value = response.error;
        return false;
      }

      return true;
    } catch (err) {
      error.value = '修改密码失败，请重试';
      return false;
    } finally {
      isLoading.value = false;
    }
  };

  const getCurrentUser = async () => {
    try {
      const response = await AuthService.getCurrentUser();
      
      if (!response.error) {
        user.value = response.data?.data?.user || response.data?.user;
      }
    } catch (err) {
      user.value = null;
    }
  };

  // 组件挂载时检查当前用户
  onMounted(() => {
    getCurrentUser();
  });

  return {
    user,
    isLoading,
    error,
    isAuthenticated,
    login,
    logout,
    changePassword,
    getCurrentUser
  };
}

// composables/useAsync.js
// 异步操作的可重用逻辑

import { ref } from 'vue';

export function useAsync(asyncFn) {
  const data = ref(null);
  const loading = ref(false);
  const error = ref(null);

  const execute = async (...args) => {
    loading.value = true;
    error.value = null;

    try {
      const result = await asyncFn(...args);
      
      if (result.error) {
        error.value = result.error;
        return null;
      }

      data.value = result.data?.data || result.data;
      return data.value;
    } catch (err) {
      error.value = err.message || '操作失败';
      return null;
    } finally {
      loading.value = false;
    }
  };

  const reset = () => {
    data.value = null;
    error.value = null;
    loading.value = false;
  };

  return {
    data,
    loading,
    error,
    execute,
    reset
  };
}

// composables/useList.js
// 列表数据的通用操作（CRUD）

import { ref, computed } from 'vue';
import { useAsync } from './useAsync';

export function useList(fetchFn, initialData = []) {
  const items = ref(initialData);
  const { loading, error, execute } = useAsync(fetchFn);
  const selectedItem = ref(null);
  const searchQuery = ref('');

  const filteredItems = computed(() => {
    if (!searchQuery.value) return items.value;

    const query = searchQuery.value.toLowerCase();
    return items.value.filter(item =>
      Object.values(item).some(value =>
        String(value).toLowerCase().includes(query)
      )
    );
  });

  const fetch = async () => {
    const result = await execute();
    if (result) {
      items.value = result;
    }
  };

  const select = (item) => {
    selectedItem.value = item;
  };

  const deselect = () => {
    selectedItem.value = null;
  };

  const search = (query) => {
    searchQuery.value = query;
  };

  return {
    items,
    filteredItems,
    loading,
    error,
    selectedItem,
    searchQuery,
    fetch,
    select,
    deselect,
    search
  };
}

// composables/useConfirm.js
// 确认对话框的可重用逻辑

import { ref } from 'vue';

export function useConfirm() {
  const isVisible = ref(false);
  const message = ref('');
  const title = ref('确认');
  const confirmCallback = ref(null);

  const confirm = (msg, titleText = '确认', callback = null) => {
    message.value = msg;
    title.value = titleText;
    confirmCallback.value = callback;
    isVisible.value = true;
  };

  const onConfirm = async () => {
    isVisible.value = false;
    if (confirmCallback.value) {
      await confirmCallback.value();
    }
  };

  const onCancel = () => {
    isVisible.value = false;
  };

  return {
    isVisible,
    message,
    title,
    confirm,
    onConfirm,
    onCancel
  };
}

// composables/useForm.js
// 表单的通用验证和提交逻辑

import { reactive, ref, watch } from 'vue';

export function useForm(initialValues, onSubmit, validateFn = null) {
  const form = reactive({ ...initialValues });
  const errors = reactive({});
  const touched = reactive({});
  const isSubmitting = ref(false);

  const validate = () => {
    // 清空之前的错误
    Object.keys(errors).forEach(key => delete errors[key]);

    if (!validateFn) return true;

    const newErrors = validateFn(form);
    Object.assign(errors, newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const submit = async () => {
    if (!validate()) return false;

    isSubmitting.value = true;
    try {
      const result = await onSubmit(form);
      return result;
    } finally {
      isSubmitting.value = false;
    }
  };

  const reset = () => {
    Object.assign(form, initialValues);
    Object.keys(errors).forEach(key => delete errors[key]);
    Object.keys(touched).forEach(key => delete touched[key]);
  };

  const touch = (field) => {
    touched[field] = true;
  };

  const blur = (field) => {
    touch(field);
    validate();
  };

  return {
    form,
    errors,
    touched,
    isSubmitting,
    validate,
    submit,
    reset,
    touch,
    blur
  };
}

export default {
  useAuth,
  useAsync,
  useList,
  useConfirm,
  useForm
};
