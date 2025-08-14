<template>
  <div class="bg-gradient-to-br from-emerald-50 to-green-100">
    <!-- 主要內容 -->
    <main>
      <!-- Hero 區塊 -->
      <section class="py-20 px-4">
        <div class="max-w-4xl mx-auto text-center">
          <div class="mb-8">
            <i class="pi pi-comments text-6xl text-emerald-600 mb-4 block"></i>
          </div>

          <h2 class="text-4xl md:text-6xl font-bold text-emerald-800 mb-6">
            現代化聊天室系統
          </h2>

          <p class="text-xl text-emerald-700 mb-8 max-w-2xl mx-auto">
            體驗流暢的即時通訊，連接你我他。簡潔優雅的介面設計，強大的功能支援。
          </p>

          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              @click="navigateTo('/register')"
              label="立即開始"
              icon="pi pi-arrow-right"
              size="large"
              class="p-button-lg"
            />
            <Button
              @click="scrollToFeatures"
              label="了解更多"
              icon="pi pi-info-circle"
              severity="secondary"
              size="large"
              outlined
            />
          </div>
        </div>
      </section>

      <!-- 功能特色 -->
      <section id="features" class="py-16 px-4 bg-white/50">
        <div class="max-w-6xl mx-auto">
          <h3 class="text-3xl font-bold text-center text-emerald-800 mb-12">
            功能特色
          </h3>

          <div class="grid md:grid-cols-3 gap-8">
            <Card class="feature-card text-center">
              <template #header>
                <div class="pt-6">
                  <i class="pi pi-bolt text-4xl text-emerald-600"></i>
                </div>
              </template>
              <template #content>
                <h4 class="text-xl font-bold text-emerald-800 mb-3">
                  即時通訊
                </h4>
                <p class="text-emerald-700">
                  使用 WebSocket 技術，實現真正的即時訊息傳遞，無延遲溝通體驗。
                </p>
              </template>
            </Card>

            <Card class="feature-card text-center">
              <template #header>
                <div class="pt-6">
                  <i class="pi pi-users text-4xl text-emerald-600"></i>
                </div>
              </template>
              <template #content>
                <h4 class="text-xl font-bold text-emerald-800 mb-3">
                  多人聊天
                </h4>
                <p class="text-emerald-700">
                  支援群組聊天，建立專屬頻道，與朋友們一起暢聊無阻。
                </p>
              </template>
            </Card>

            <Card class="feature-card text-center">
              <template #header>
                <div class="pt-6">
                  <i class="pi pi-shield text-4xl text-emerald-600"></i>
                </div>
              </template>
              <template #content>
                <h4 class="text-xl font-bold text-emerald-800 mb-3">
                  安全可靠
                </h4>
                <p class="text-emerald-700">
                  先進的加密技術保護你的隱私，安全的用戶認證系統。
                </p>
              </template>
            </Card>
          </div>
        </div>
      </section>

      <!-- 技術特點 -->
      <section class="py-16 px-4">
        <div class="max-w-4xl mx-auto">
          <h3 class="text-3xl font-bold text-center text-emerald-800 mb-12">
            技術架構
          </h3>

          <div class="grid md:grid-cols-2 gap-8">
            <Card>
              <template #header>
                <div class="p-4">
                  <h4 class="text-xl font-bold text-emerald-800">前端技術</h4>
                </div>
              </template>
              <template #content>
                <div class="space-y-3">
                  <div class="flex items-center">
                    <i class="pi pi-check-circle text-emerald-600 mr-2"></i>
                    <span>Vue.js 3 + Nuxt 3</span>
                  </div>
                  <div class="flex items-center">
                    <i class="pi pi-check-circle text-emerald-600 mr-2"></i>
                    <span>PrimeVue UI 組件庫</span>
                  </div>
                  <div class="flex items-center">
                    <i class="pi pi-check-circle text-emerald-600 mr-2"></i>
                    <span>Tailwind CSS</span>
                  </div>
                  <div class="flex items-center">
                    <i class="pi pi-check-circle text-emerald-600 mr-2"></i>
                    <span>TypeScript 支援</span>
                  </div>
                </div>
              </template>
            </Card>

            <Card>
              <template #header>
                <div class="p-4">
                  <h4 class="text-xl font-bold text-emerald-800">後端技術</h4>
                </div>
              </template>
              <template #content>
                <div class="space-y-3">
                  <div class="flex items-center">
                    <i class="pi pi-check-circle text-emerald-600 mr-2"></i>
                    <span>WebSocket 即時通訊</span>
                  </div>
                  <div class="flex items-center">
                    <i class="pi pi-check-circle text-emerald-600 mr-2"></i>
                    <span>用戶認證系統</span>
                  </div>
                  <div class="flex items-center">
                    <i class="pi pi-check-circle text-emerald-600 mr-2"></i>
                    <span>頻道管理</span>
                  </div>
                  <div class="flex items-center">
                    <i class="pi pi-check-circle text-emerald-600 mr-2"></i>
                    <span>訊息持久化</span>
                  </div>
                </div>
              </template>
            </Card>
          </div>
        </div>
      </section>

      <!-- CTA 區塊 -->
      <section class="py-16 px-4 bg-emerald-600">
        <div class="max-w-4xl mx-auto text-center text-white">
          <h3 class="text-3xl font-bold mb-4">準備開始聊天了嗎？</h3>
          <p class="text-xl mb-8 opacity-90">
            加入我們的聊天室社群，開始你的即時通訊體驗
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              @click="navigateTo('/register')"
              label="免費註冊"
              icon="pi pi-user-plus"
              size="large"
              severity="secondary"
              class="bg-white text-emerald-600 hover:bg-gray-100"
            />
            <Button
              @click="navigateTo('/login')"
              label="立即登入"
              icon="pi pi-sign-in"
              size="large"
              outlined
              class="border-white text-white hover:bg-white hover:text-emerald-600"
            />
          </div>
        </div>
      </section>
    </main>

    <!-- 頁腳 -->
    <footer class="bg-emerald-800 text-white py-8 px-4">
      <div class="max-w-4xl mx-auto text-center">
        <div class="flex items-center justify-center mb-4">
          <i class="pi pi-comments text-2xl mr-2"></i>
          <span class="text-lg font-semibold">聊天室系統</span>
        </div>
        <p class="text-emerald-200">
          © 2025 聊天室系統. 使用 Vue.js + PrimeVue 構建
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import Card from "primevue/card";
import Button from "primevue/button";
import { useUserStore } from "~/stores/user";

// 設定頁面元資訊
definePageMeta({
  layout: "default",
});

// Store
const userStore = useUserStore();

// SEO
useHead({
  title: "聊天室系統 - 現代化即時通訊平台",
  meta: [
    {
      name: "description",
      content:
        "體驗流暢的即時通訊，連接你我他。使用 Vue.js 3 + PrimeVue 構建的現代化聊天室系統。",
    },
  ],
});

// 檢查認證狀態，已登入用戶自動導向聊天室
onMounted(async () => {
  if (process.client) {
    userStore.initAuth();

    if (userStore.isAuthenticated) {
      await navigateTo("/chatroom");
    }
  }
});

// 平滑滾動到功能區塊
const scrollToFeatures = () => {
  document.getElementById("features")?.scrollIntoView({
    behavior: "smooth",
  });
};
</script>

<style scoped>
.feature-card {
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-4px);
}

/* PrimeVue Card 自定義樣式 */
:deep(.p-card) {
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border: 1px solid #d1fae5;
}

:deep(.p-card:hover) {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

/* PrimeVue Button 自定義樣式 */
:deep(.p-button) {
  border-radius: 8px;
  font-weight: 600;
}
</style>
