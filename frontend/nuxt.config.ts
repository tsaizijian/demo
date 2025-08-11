// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  modules: ['@nuxt/image', '@nuxt/eslint', '@nuxt/ui', '@pinia/nuxt'],
  
  // CSS 配置
  css: [
    '~/assets/css/global.css',
    '~/assets/css/theme.css'
  ],

  // Tailwind CSS 配置
  tailwindcss: {
    configPath: '~/tailwind.config.js'
  },

  // UI 配置
  ui: {
    icons: ['heroicons']
  },
  
  // 開發環境設定
  runtimeConfig: {
    public: {
      apiBase: process.env.API_BASE || 'http://localhost:8080'
    }
  }
})