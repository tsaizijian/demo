export default defineNuxtPlugin((nuxtApp) => {
  const config = useRuntimeConfig();

  const handleApiError = (error: any) => {
    console.error("API 錯誤:", error);

    if (error.status === 401) {
      navigateTo("/login");
    } else if (error.status === 403) {
      // 處理權限錯誤
    } else {
      // 處理其他錯誤
    }

    throw error;
  };

  const createApi = (baseURL: string) => {
    return {
      get: async (endpoint: string, options = {}) => {
        try {
          const data = await $fetch(endpoint, {
            baseURL,
            method: "GET",
            credentials: 'include', // 包含 cookies/session
            ...options,
          });
          return data;
        } catch (err) {
          handleApiError(err);
        }
      },

      post: async (endpoint: string, body: any, options = {}) => {
        try {
          console.log('API POST 請求:', {
            endpoint,
            baseURL,
            body: typeof body === 'object' && body.password ? 
              { ...body, password: '***隱藏***' } : body,
            options
          });
          
          const data = await $fetch(endpoint, {
            method: "POST",
            body,
            baseURL,
            credentials: 'include', // 包含 cookies/session
            ...options,
          });
          
          console.log('API POST 回應:', data);
          return data;
        } catch (err) {
          console.error('API POST 錯誤詳情:', {
            endpoint,
            status: err.status,
            statusCode: err.statusCode,
            statusText: err.statusText,
            data: err.data,
            response: err.response
          });
          handleApiError(err);
        }
      },

      put: async (endpoint: string, body: any, options = {}) => {
        try {
          const data = await $fetch(endpoint, {
            method: "PUT",
            body,
            baseURL,
            credentials: 'include', // 包含 cookies/session
            ...options,
          });
          return data;
        } catch (err) {
          handleApiError(err);
        }
      },

      delete: async (endpoint: string, options = {}) => {
        try {
          const data = await $fetch(endpoint, {
            method: "DELETE",
            baseURL,
            credentials: 'include', // 包含 cookies/session
            ...options,
          });
          return data;
        } catch (err) {
          handleApiError(err);
        }
      },
    };
  };

  const api = createApi(config.public.apiBase);

  return {
    provide: {
      api,
    },
  };
});