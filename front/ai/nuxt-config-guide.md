# Nuxt 配置指南

本文檔提供了聊天室應用的 Nuxt.js 配置方案，專注於 API URL 管理和代碼可維護性。

## nuxt.config.ts 配置示例

```typescript
// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  // 基本配置
  compatibilityDate: "2025-07-15",
  devtools: { enabled: true },

  // 模組
  modules: ["@nuxt/eslint", "@nuxt/ui"],

  // 運行時配置
  runtimeConfig: {
    // 僅在服務器端可用的私有配置
    apiSecret: process.env.API_SECRET || "default_secret",

    // 公共配置 (也會暴露給客戶端)
    public: {
      apiBase: process.env.API_BASE || "http://localhost:8080",
      apiUrls: {
        auth: {
          login: "/api/login",
          register: "/api/register/user",
          checkUsername: "/api/register/check-username",
          checkEmail: "/api/register/check-email",
          recaptchaConfig: "/api/register/recaptcha-config",
        },
        chatroom: {
          list: "/api/chatroom/list",
          create: "/api/chatroom/create",
          join: "/api/chatroom/join",
          leave: "/api/chatroom/leave",
          details: "/api/chatroom/", // + room_id
        },
        messages: {
          send: "/api/messages/send",
          list: "/api/messages/list",
          delete: "/api/messages/delete",
          upload: "/api/messages/upload",
        },
        users: {
          profile: "/api/users/profile",
          update: "/api/users/update",
          online: "/api/users/online",
        },
        privateMessages: {
          list: "/api/private-messages/list",
          send: "/api/private-messages/send",
          conversation: "/api/private-messages/conversation", // + user_id
        },
      },
    },
  },

  // 應用程式設定
  app: {
    // 全局頁面轉場效果
    pageTransition: { name: "page", mode: "out-in" },
    // 頭部配置
    head: {
      title: "聊天室應用",
      meta: [
        { charset: "utf-8" },
        { name: "viewport", content: "width=device-width, initial-scale=1" },
        { name: "description", content: "高效能多功能聊天室應用" },
      ],
      link: [{ rel: "icon", type: "image/x-icon", href: "/favicon.ico" }],
    },
  },

  // TypeScript 配置
  typescript: {
    strict: true,
    typeCheck: true,
  },

  // 構建配置
  build: {
    transpile: [],
  },

  // 掛載插件
  plugins: ["~/plugins/api.ts"],

  // CSS 全局樣式
  css: ["~/assets/css/main.css"],

  // Vite 配置
  vite: {
    optimizeDeps: {
      include: [],
    },
    // CSS 預處理器配置
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: '@import "~/assets/scss/variables.scss";',
        },
      },
    },
  },
});
```

## API 調用示例

使用配置中的 API URL:

```typescript
// composables/useAuthApi.ts
export function useAuthApi() {
  const config = useRuntimeConfig();

  // 登入方法
  const login = async (username: string, password: string) => {
    try {
      const { data, error } = await useFetch(config.public.apiUrls.auth.login, {
        method: "POST",
        body: { username, password },
      });

      if (error.value) throw error.value;
      return data.value;
    } catch (err) {
      console.error("登入錯誤:", err);
      throw err;
    }
  };

  // 註冊方法
  const register = async (userData: RegisterData) => {
    try {
      const { data, error } = await useFetch(
        config.public.apiUrls.auth.register,
        {
          method: "POST",
          body: userData,
        }
      );

      if (error.value) throw error.value;
      return data.value;
    } catch (err) {
      console.error("註冊錯誤:", err);
      throw err;
    }
  };

  // 驗證用戶名可用性
  const checkUsername = async (username: string) => {
    try {
      const { data } = await useFetch(
        config.public.apiUrls.auth.checkUsername,
        {
          method: "POST",
          body: { username },
        }
      );

      return data.value;
    } catch (err) {
      console.error("用戶名檢查錯誤:", err);
      throw err;
    }
  };

  // 獲取 reCAPTCHA 配置
  const getRecaptchaConfig = async () => {
    try {
      const { data } = await useFetch(
        config.public.apiUrls.auth.recaptchaConfig
      );
      return data.value;
    } catch (err) {
      console.error("reCAPTCHA 配置獲取錯誤:", err);
      throw err;
    }
  };

  return {
    login,
    register,
    checkUsername,
    getRecaptchaConfig,
  };
}
```

## API 插件設置

創建一個統一的 API 處理插件:

```typescript
// plugins/api.ts
export default defineNuxtPlugin((nuxtApp) => {
  const config = useRuntimeConfig();

  // 統一錯誤處理方法
  const handleApiError = (error: any) => {
    console.error("API 錯誤:", error);

    // 處理不同類型的錯誤
    if (error.status === 401) {
      // 處理未授權錯誤
      navigateTo("/login");
    } else if (error.status === 403) {
      // 處理權限錯誤
    } else {
      // 處理其他錯誤
    }

    return error;
  };

  // 創建 API 實例
  const createApi = (baseURL: string) => {
    return {
      get: async (endpoint: string, options = {}) => {
        try {
          const { data, error } = await useFetch(endpoint, {
            baseURL,
            ...options,
          });

          if (error.value) return handleApiError(error.value);
          return data.value;
        } catch (err) {
          return handleApiError(err);
        }
      },

      post: async (endpoint: string, body: any, options = {}) => {
        try {
          const { data, error } = await useFetch(endpoint, {
            method: "POST",
            body,
            baseURL,
            ...options,
          });

          if (error.value) return handleApiError(error.value);
          return data.value;
        } catch (err) {
          return handleApiError(err);
        }
      },

      put: async (endpoint: string, body: any, options = {}) => {
        try {
          const { data, error } = await useFetch(endpoint, {
            method: "PUT",
            body,
            baseURL,
            ...options,
          });

          if (error.value) return handleApiError(error.value);
          return data.value;
        } catch (err) {
          return handleApiError(err);
        }
      },

      delete: async (endpoint: string, options = {}) => {
        try {
          const { data, error } = await useFetch(endpoint, {
            method: "DELETE",
            baseURL,
            ...options,
          });

          if (error.value) return handleApiError(error.value);
          return data.value;
        } catch (err) {
          return handleApiError(err);
        }
      },
    };
  };

  // 提供 API 實例給應用
  const api = createApi(config.public.apiBase);

  return {
    provide: {
      api,
    },
  };
});
```

## 使用示例

在組件中使用 API:

```typescript
<script setup>
// 在 Vue 組件中使用 API 插件
const { $api } = useNuxtApp()

// 獲取聊天室列表
const fetchChatRooms = async () => {
  try {
    const endpoint = useRuntimeConfig().public.apiUrls.chatroom.list
    const response = await $api.get(endpoint)
    return response
  } catch (error) {
    // 處理錯誤
    console.error('獲取聊天室列表錯誤:', error)
    return []
  }
}

// 使用聊天室 API
const { data: chatRooms } = await useAsyncData('chatRooms', fetchChatRooms)
</script>

<template>
  <div>
    <h1>聊天室列表</h1>
    <div v-if="chatRooms && chatRooms.length > 0">
      <div v-for="room in chatRooms" :key="room.id" class="chat-room-item">
        {{ room.name }}
      </div>
    </div>
    <div v-else>
      暫無聊天室
    </div>
  </div>
</template>
```

## 環境變數設置

建立 `.env` 文件來管理環境設置:

```bash
# .env.development
API_BASE=http://localhost:8080
API_SECRET=development_secret

# .env.production
API_BASE=https://api.chatroom-app.com
API_SECRET=production_secret
```

透過這種方式，您可以輕鬆管理不同環境的 API URL，並確保代碼結構清晰、易於維護。
