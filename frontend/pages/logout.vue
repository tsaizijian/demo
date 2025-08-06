<script setup>
// 設定頁面元資訊
definePageMeta({
  layout: false
});

const userStore = useUserStore();
const router = useRouter();

// 自動執行登出
onMounted(async () => {
  // 執行登出邏輯
  await userStore.logout();
  
  // 3秒後自動跳轉到登入頁面
  setTimeout(() => {
    router.push('/login');
  }, 3000);
});
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
    <div class="max-w-md w-full">
      <!-- 登出成功卡片 -->
      <UCard class="shadow-xl">
        <div class="text-center py-8">
          <!-- 成功圖標 -->
          <div class="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
            <UIcon name="i-heroicons-check-circle" class="w-8 h-8 text-green-600" />
          </div>
          
          <!-- 標題 -->
          <h1 class="text-2xl font-bold text-gray-900 mb-2">
            登出成功
          </h1>
          
          <!-- 描述 -->
          <p class="text-gray-600 mb-6">
            感謝您使用聊天室！您已安全登出。
          </p>
          
          <!-- 登出詳情 -->
          <div class="space-y-3 text-left bg-gray-50 rounded-lg p-4 mb-6">
            <div class="flex items-center gap-3 text-sm text-gray-600">
              <UIcon name="i-heroicons-wifi-slash" class="w-4 h-4 text-gray-400" />
              <span>即時連線已斷開</span>
              <UIcon name="i-heroicons-check" class="w-4 h-4 text-green-500 ml-auto" />
            </div>
            
            <div class="flex items-center gap-3 text-sm text-gray-600">
              <UIcon name="i-heroicons-shield-check" class="w-4 h-4 text-gray-400" />
              <span>登入資訊已清除</span>
              <UIcon name="i-heroicons-check" class="w-4 h-4 text-green-500 ml-auto" />
            </div>
            
            <div class="flex items-center gap-3 text-sm text-gray-600">
              <UIcon name="i-heroicons-lock-closed" class="w-4 h-4 text-gray-400" />
              <span>會話已安全結束</span>
              <UIcon name="i-heroicons-check" class="w-4 h-4 text-green-500 ml-auto" />
            </div>
          </div>
          
          <!-- 倒數計時 -->
          <div class="text-sm text-gray-500 mb-4">
            <UIcon name="i-heroicons-clock" class="w-4 h-4 inline mr-1" />
            3秒後自動跳轉到登入頁面
          </div>
          
          <!-- 立即跳轉按鈕 -->
          <div class="flex gap-3">
            <UButton
              @click="$router.push('/login')"
              color="blue"
              size="sm"
              class="flex-1"
              icon="i-heroicons-arrow-right-on-rectangle"
            >
              立即重新登入
            </UButton>
            
            <UButton
              @click="$router.push('/')"
              color="gray"
              variant="soft"
              size="sm"
              class="flex-1"
              icon="i-heroicons-home"
            >
              回到首頁
            </UButton>
          </div>
        </div>
      </UCard>
      
      <!-- 底部信息 -->
      <div class="text-center mt-6">
        <p class="text-sm text-gray-500">
          希望您下次再來使用聊天室！
        </p>
      </div>
    </div>
  </div>
</template>