<template>
  <div
    class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 relative overflow-hidden"
  >
    <!-- Background decoration -->
    <div
      class="absolute inset-0 bg-grid-slate-100 bg-[size:20px_20px] opacity-30"
    ></div>
    <div
      class="absolute top-0 -left-4 w-72 h-72 bg-blue-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"
    ></div>
    <div
      class="absolute top-0 -right-4 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"
    ></div>
    <div
      class="absolute -bottom-8 left-20 w-72 h-72 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"
    ></div>

    <div
      class="relative z-10 min-h-screen flex items-center justify-center px-4 sm:px-6 lg:px-8"
    >
      <div class="max-w-4xl w-full">
        <!-- Hero Section -->
        <div class="text-center mb-16 animate-fade-in">
          <div
            class="inline-flex items-center px-4 py-2 rounded-full bg-blue-100 text-blue-800 text-sm font-medium mb-6 animate-bounce-in"
          >
            <svg class="w-[16px] h-[16px] mr-[8px]" fill="currentColor" viewBox="0 0 20 20">
              <path
                d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"
              />
              <path
                d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"
              />
            </svg>
            全新聊天體驗
          </div>

          <h1
            class="text-5xl md:text-7xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent mb-6 leading-tight"
          >
            歡迎來到
            <br />聊天室應用
          </h1>

          <p
            class="text-xl md:text-2xl text-gray-600 mb-12 max-w-3xl mx-auto leading-relaxed"
          >
            體驗全新的即時通訊平台，<br class="hidden sm:block" />
            <span
              class="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent font-semibold"
            >
              連接你與世界的每一個瞬間
            </span>
          </p>

          <div class="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <NuxtLink
              to="/login"
              class="group relative inline-flex items-center justify-center px-8 py-4 text-lg font-semibold text-white bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-4 focus:ring-blue-300 transform hover:scale-105 transition-all duration-300 shadow-xl hover:shadow-2xl"
            >
              <svg
                class="w-[20px] h-[20px] mr-[8px] group-hover:animate-pulse"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"
                ></path>
              </svg>
              立即登入
              <div
                class="absolute inset-0 rounded-2xl bg-gradient-to-r from-blue-600 to-purple-600 opacity-0 group-hover:opacity-20 transition-opacity duration-300"
              ></div>
            </NuxtLink>

            <NuxtLink
              to="/register"
              class="group relative inline-flex items-center justify-center px-8 py-4 text-lg font-semibold text-gray-700 bg-white border-2 border-gray-200 rounded-2xl hover:border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-4 focus:ring-gray-200 transform hover:scale-105 transition-all duration-300 shadow-lg hover:shadow-xl"
            >
              <svg
                class="w-[20px] h-[20px] mr-[8px] group-hover:animate-pulse"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"
                ></path>
              </svg>
              註冊新帳號
            </NuxtLink>
          </div>
        </div>

        <!-- Features Grid -->
        <div
          class="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-5xl mx-auto animate-fade-in-up"
        >
          <div
            class="group bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2 border border-gray-100"
          >
            <div
              class="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300"
            >
              <svg
                class="w-[24px] h-[24px] text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                ></path>
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">即時聊天</h3>
            <p class="text-gray-600 text-sm">
              閃電般快速的訊息傳遞，零延遲溝通體驗
            </p>
          </div>

          <div
            class="group bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2 border border-gray-100"
          >
            <div
              class="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300"
            >
              <svg
                class="w-[24px] h-[24px] text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                ></path>
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">多人聊天室</h3>
            <p class="text-gray-600 text-sm">
              建立或加入群組，與朋友們一起暢聊無阻
            </p>
          </div>

          <div
            class="group bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2 border border-gray-100"
          >
            <div
              class="w-12 h-12 bg-gradient-to-br from-pink-500 to-pink-600 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300"
            >
              <svg
                class="w-[24px] h-[24px] text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                ></path>
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">私人訊息</h3>
            <p class="text-gray-600 text-sm">
              端到端加密的一對一聊天，保護隱私安全
            </p>
          </div>

          <div
            class="group bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2 border border-gray-100"
          >
            <div
              class="w-12 h-12 bg-gradient-to-br from-green-500 to-green-600 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300"
            >
              <svg
                class="w-[24px] h-[24px] text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"
                ></path>
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">檔案分享</h3>
            <p class="text-gray-600 text-sm">
              輕鬆分享圖片、文件和媒體檔案，支援多種格式
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
useSeoMeta({
  title: "聊天室應用 - 首頁",
  description: "高效能多功能聊天室應用，立即體驗即時通訊功能",
});
</script>
