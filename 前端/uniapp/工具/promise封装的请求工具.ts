/**
 * request.ts
 * uni-app 请求工具类封装（TypeScript版本）
 */

// 定义接口
interface RequestOptions {
    url: string;
    method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
    data?: any;
    header?: Record<string, any>;
    accessKey?: string;
    timeout?: number;
    showError?: boolean;
    [key: string]: any;
  }
  
  interface ResponseError {
    statusCode: number;
    errMsg: string;
    data: any;
  }
  
  // uni-app 请求成功结果类型
  interface RequestSuccessCallbackResult {
    data: any;
    statusCode: number;
    header: any;
    cookies: string[];
    errMsg: string;
  }
  
  // 基础配置
  const BASE_URL = 'https://tea.qingnian8.com/api';
  const DEFAULT_ACCESS_KEY = '108745';
  const DEFAULT_TIMEOUT = 10000; // 默认超时时间 10s
  
  // 请求拦截器
  const beforeRequest = (config: RequestOptions): RequestOptions => {
    // 这里可以做一些请求前的操作，比如显示加载框
    // uni.showLoading({ title: '加载中...' });
    
    // 添加全局参数
    const accessKey = config.accessKey || DEFAULT_ACCESS_KEY;
    
    if (!config.header) {
      config.header = {};
    }
    
    // 设置访问密钥
    config.header['access-key'] = accessKey;
    
    // 这里可以添加其他全局请求头，如token等
    // const token = uni.getStorageSync('token');
    // if (token) {
    //   config.header['Authorization'] = `Bearer ${token}`;
    // }
    
    return config;
  };
  
  // 响应拦截器
  const handleResponse = (response: RequestSuccessCallbackResult, resolve: Function, reject: Function): void => {
    // 这里可以做一些响应后的操作，比如关闭加载框
    // uni.hideLoading();
    
    // 这里处理的是 uni.request 的响应格式
    if (response.statusCode >= 200 && response.statusCode < 300) {
      // 请求成功
      resolve(response.data);
    } else {
      // 请求失败
      const error: ResponseError = {
        statusCode: response.statusCode,
        errMsg: response.errMsg || '请求失败',
        data: response.data
      };
      
      // 处理特定错误码
      switch (response.statusCode) {
        case 401:
          // 未授权处理
          uni.showToast({
            title: '请先登录',
            icon: 'none'
          });
          // 可以在这里清除本地token并跳转到登录页
          // uni.removeStorageSync('token');
          // uni.navigateTo({ url: '/pages/login/index' });
          break;
        case 403:
          uni.showToast({
            title: '没有权限访问该资源',
            icon: 'none'
          });
          break;
        case 404:
          uni.showToast({
            title: '请求的资源不存在',
            icon: 'none'
          });
          break;
        case 500:
          uni.showToast({
            title: '服务器内部错误',
            icon: 'none'
          });
          break;
        default:
          uni.showToast({
            title: error.errMsg,
            icon: 'none'
          });
      }
      
      reject(error);
    }
  };
  
  /**
   * 封装的请求方法
   * @param options - 请求配置
   * @returns 返回一个Promise对象
   */
  const request = <T = any>(options: RequestOptions): Promise<T> => {
    // 合并请求配置
    const config: RequestOptions = {
      url: options.url.startsWith('http') ? options.url : BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data || {},
      header: options.header || {},
      timeout: options.timeout || DEFAULT_TIMEOUT,
      accessKey: options.accessKey || DEFAULT_ACCESS_KEY,
      showError: options.showError !== false // 默认为true
    };
    
    // 应用请求拦截器
    const processedConfig = beforeRequest(config);
    
    // 返回Promise
    return new Promise<T>((resolve, reject) => {
      uni.request({
        url: processedConfig.url,
        method: processedConfig.method,
        data: processedConfig.data,
        header: processedConfig.header,
        // 注意：uniapp 类型定义中可能没有 timeout 属性，此处移除类型检查警告
        // @ts-ignore
        timeout: processedConfig.timeout,
        success: (res) => {
          handleResponse(res as RequestSuccessCallbackResult, resolve, reject);
        },
        fail: (err) => {
          // uni.hideLoading();
          
          if (processedConfig.showError) {
            let errMsg = err.errMsg || '请求失败';
            
            // 处理一些特殊错误
            if (errMsg.includes('timeout')) {
              errMsg = '请求超时，请检查网络';
            } else if (errMsg.includes('fail')) {
              errMsg = '网络异常，请检查网络连接';
            }
            
            uni.showToast({
              title: errMsg,
              icon: 'none'
            });
          }
          
          reject(err);
        }
      });
    });
  };
  
  // 封装常用请求方法
  const http = {
    /**
     * GET请求
     * @param url - 请求地址
     * @param data - 请求参数
     * @param options - 其他配置选项
     */
    get: <T = any>(url: string, data: Record<string, any> = {}, options: Partial<RequestOptions> = {}): Promise<T> => {
      return request<T>({
        url,
        method: 'GET',
        data,
        ...options
      });
    },
    
    /**
     * POST请求
     * @param url - 请求地址
     * @param data - 请求参数
     * @param options - 其他配置选项
     */
    post: <T = any>(url: string, data: Record<string, any> = {}, options: Partial<RequestOptions> = {}): Promise<T> => {
      return request<T>({
        url,
        method: 'POST',
        data,
        ...options
      });
    },
    
    /**
     * PUT请求
     * @param url - 请求地址
     * @param data - 请求参数
     * @param options - 其他配置选项
     */
    put: <T = any>(url: string, data: Record<string, any> = {}, options: Partial<RequestOptions> = {}): Promise<T> => {
      return request<T>({
        url,
        method: 'PUT',
        data,
        ...options
      });
    },
    
    /**
     * DELETE请求
     * @param url - 请求地址
     * @param data - 请求参数
     * @param options - 其他配置选项
     */
    delete: <T = any>(url: string, data: Record<string, any> = {}, options: Partial<RequestOptions> = {}): Promise<T> => {
      return request<T>({
        url,
        method: 'DELETE',
        data,
        ...options
      });
    },
    
    /**
     * 自定义请求
     * @param options - 请求配置
     */
    request
  };
  
  export default http; 