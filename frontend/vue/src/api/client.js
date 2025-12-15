// api/client.js
// 统一的 API 客户端，隔离网络层与业务逻辑层

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api';

class ApiClient {
  /**
   * 统一的 HTTP 请求方法
   * @param {string} method - HTTP 方法 (GET, POST, PUT, DELETE)
   * @param {string} endpoint - API 端点路径 (不含 /api 前缀)
   * @param {Object} options - 请求选项
   * @returns {Promise<{data, status, error}>}
   */
  async request(method, endpoint, options = {}) {
    const {
      body = null,
      headers = {},
      query = {},
      timeout = 10000,
      onProgress = null
    } = options;

    try {
      // 构建完整 URL
      const url = new URL(`${API_BASE}${endpoint}`);
      
      // 添加查询参数
      Object.entries(query).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          url.searchParams.append(key, value);
        }
      });

      // 构建请求配置
      const fetchOptions = {
        method,
        headers: {
          'Accept': 'application/json',
          ...headers
        },
        credentials: 'include' // 发送 cookie
      };

      // 设置请求体
      if (body) {
        if (body instanceof FormData) {
          fetchOptions.body = body;
          // FormData 自动设置 Content-Type: multipart/form-data
          delete fetchOptions.headers['Content-Type'];
        } else if (typeof body === 'object') {
          fetchOptions.headers['Content-Type'] = 'application/json';
          fetchOptions.body = JSON.stringify(body);
        } else {
          fetchOptions.body = body;
        }
      }

      // 超时处理
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);
      fetchOptions.signal = controller.signal;

      // 发起请求
      const response = await fetch(url.toString(), fetchOptions);
      clearTimeout(timeoutId);

      // 处理响应
      const contentType = response.headers.get('content-type');
      let data = null;

      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else if (contentType && contentType.includes('application/')) {
        // 二进制文件 (Excel, PDF 等)
        data = await response.blob();
      } else {
        data = await response.text();
      }

      // 调用进度回调 (用于上传/下载进度)
      if (onProgress) {
        onProgress({ loaded: 100, total: 100 });
      }

      return {
        data,
        status: response.status,
        headers: response.headers,
        error: !response.ok ? (data?.error || data?.message || '请求失败') : null
      };

    } catch (error) {
      if (error.name === 'AbortError') {
        return {
          data: null,
          status: 0,
          error: '请求超时，请检查网络连接'
        };
      }

      return {
        data: null,
        status: 0,
        error: error.message || '网络错误，请检查后端服务'
      };
    }
  }

  // 便捷方法

  get(endpoint, options = {}) {
    return this.request('GET', endpoint, options);
  }

  post(endpoint, body = null, options = {}) {
    return this.request('POST', endpoint, { ...options, body });
  }

  put(endpoint, body = null, options = {}) {
    return this.request('PUT', endpoint, { ...options, body });
  }

  delete(endpoint, options = {}) {
    return this.request('DELETE', endpoint, options);
  }

  /**
   * 上传文件
   * @param {string} endpoint - 上传端点
   * @param {File} file - 文件对象
   * @param {Object} additionalData - 额外的表单数据
   */
  async uploadFile(endpoint, file, additionalData = {}) {
    const formData = new FormData();
    formData.append('file', file);

    Object.entries(additionalData).forEach(([key, value]) => {
      formData.append(key, value);
    });

    return this.post(endpoint, formData);
  }

  /**
   * 下载文件
   * @param {string} endpoint - 下载端点
   * @param {string} filename - 保存的文件名
   */
  async downloadFile(endpoint, filename) {
    const response = await this.get(endpoint);

    if (response.error) {
      throw new Error(response.error);
    }

    // 创建下载链接
    const blob = response.data;
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }
}

// 导出单例
export const apiClient = new ApiClient();

/**
 * 便捷 hook：处理 API 调用的通用逻辑
 * 自动处理加载状态、错误处理、响应转换
 */
export function useApi() {
  const loading = ref(false);
  const error = ref(null);
  const data = ref(null);

  const execute = async (apiCall) => {
    loading.value = true;
    error.value = null;
    data.value = null;

    try {
      const response = await apiCall();
      
      if (response.error) {
        error.value = response.error;
        return null;
      }

      data.value = response.data?.data || response.data;
      return data.value;
    } catch (err) {
      error.value = err.message || '未知错误';
      return null;
    } finally {
      loading.value = false;
    }
  };

  return {
    loading,
    error,
    data,
    execute
  };
}

export default apiClient;
