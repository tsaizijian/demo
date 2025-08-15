<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
    <div class="max-w-md w-full">
      <!-- 登出成功卡片 -->
      <Card class="logout-card shadow-xl">
        <template #content>
          <div class="text-center py-8">
            <!-- 成功圖標 -->
            <div class="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
              <i class="pi pi-check-circle text-4xl text-green-600"></i>
            </div>

            <!-- 標題 -->
            <h1 class="text-2xl font-bold text-gray-900 mb-2">登出成功</h1>

            <!-- 描述 -->
            <p class="text-gray-600 mb-6">感謝您使用聊天室！您已安全登出。</p>

            <!-- 登出詳情 -->
            <div class="space-y-3 text-left bg-gray-50 rounded-lg p-4 mb-6">
              <div class="flex items-center gap-3 text-sm text-gray-600">
                <i class="pi pi-wifi-slash text-gray-400"></i>
                <span>即時連線已斷開</span>
                <i class="pi pi-check text-green-500 ml-auto"></i>
              </div>

              <div class="flex items-center gap-3 text-sm text-gray-600">
                <i class="pi pi-shield text-gray-400"></i>
                <span>登入資訊已清除</span>
                <i class="pi pi-check text-green-500 ml-auto"></i>
              </div>

              <div class="flex items-center gap-3 text-sm text-gray-600">
                <i class="pi pi-lock text-gray-400"></i>
                <span>會話已安全結束</span>
                <i class="pi pi-check text-green-500 ml-auto"></i>
              </div>
            </div>

            <!-- 倒數計時 -->
            <div class="text-sm text-gray-500 mb-4">
              <i class="pi pi-clock mr-1"></i>
              {{ countdown }}秒後自動跳轉到登入頁面
            </div>

            <!-- 立即跳轉按鈕 -->
            <div class="flex gap-3">
              <Button
                @click="navigateTo('/login')"
                severity="info"
                size="small"
                class="flex-1"
                icon="pi pi-sign-in"
                label="立即重新登入"
              />

              <Button
                @click="navigateTo('/')"
                severity="secondary"
                size="small"
                class="flex-1"
                icon="pi pi-home"
                label="回到首頁"
                outlined
              />
            </div>
          </div>
        </template>
      </Card>

      <!-- 底部信息 -->
      <div class="text-center mt-6">
        <p class="text-sm text-gray-500">希望您下次再來使用聊天室！</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import Card from "primevue/card";
import Button from "primevue/button";
import { useSocket } from "~/composables/useSocket";

// 設定頁面元資訊
definePageMeta({
  layout: "default",
});

// 倒數計時
const countdown = ref(3);

// 自動執行登出
onMounted(async () => {
  // 確保 Socket 已斷開（如果還沒斷開的話）
  const { disconnect } = useSocket();
  disconnect();

  // 倒數計時
  const timer = setInterval(() => {
    countdown.value--;
    if (countdown.value <= 0) {
      clearInterval(timer);
      navigateTo("/login");
    }
  }, 1000);
});
</script>

<style scoped>
/* PrimeVue Card 自定義樣式 */
.logout-card :deep(.p-card) {
  background: white;
  border-radius: 16px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  border: 1px solid #e5e7eb;
}

.logout-card :deep(.p-card .p-card-content) {
  padding: 0;
}

/* PrimeVue Button 自定義樣式 */
:deep(.p-button) {
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.3s ease;
}

:deep(.p-button:hover) {
  transform: translateY(-1px);
}

/* 成功動畫 */
@keyframes checkmark {
  0% {
    transform: scale(0) rotate(45deg);
    opacity: 0;
  }
  50% {
    transform: scale(1.2) rotate(45deg);
    opacity: 1;
  }
  100% {
    transform: scale(1) rotate(45deg);
    opacity: 1;
  }
}

.pi-check-circle {
  animation: checkmark 0.6s ease-in-out;
}
</style>