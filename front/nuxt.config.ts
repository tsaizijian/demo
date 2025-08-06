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
    recaptchaSecret: process.env.APP_RECAPTCHA_SECRET,
    // 公共配置 (也會暴露給客戶端)
    public: {
      recaptchaSiteKey: process.env.APP_RECAPTCHA_SITE,
      apiBase: process.env.API_BASE || "http://localhost:8080",
      apiUrls: {
        auth: {
          login: "/api/auth/login",
          logout: "/api/auth/logout",
          me: "/api/auth/me",
          check: "/api/auth/check",
          register: "/api/register/user",
          checkUsername: "/api/register/check-username",
          checkEmail: "/api/register/check-email",
        },
        chatroom: {
          list: "/chatroom/list",
          create: "/chatroom/create",
          join: "/chatroom/join/", // + room_id
          leave: "/chatroom/leave/", // + room_id
          members: "/chatroom/members/", // + room_id
        },
        messages: {
          send: "/message/send",
          list: "/message/room/", // + room_id
          delete: "/message/delete/", // + message_id
          upload: "/message/upload",
          download: "/message/download/", // + attachment_id
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

  // Nitro 開發代理配置 (Nuxt 4)
  nitro: {
    devProxy: {},
  },

  // Vite 配置
  vite: {
    server: {
      proxy: {
        "/api": {
          target: "http://localhost:8080",
          changeOrigin: true,
        },
      },
    },
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
