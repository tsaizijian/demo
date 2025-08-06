<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="text-center">
      <UIcon name="i-heroicons-arrow-path" class="animate-spin h-8 w-8 mx-auto mb-4" />
      <p class="text-gray-600">載入中...</p>
    </div>
  </div>
</template>

<script setup>
import { useUserStore } from '~/stores/user'

const userStore = useUserStore()
const router = useRouter()

onMounted(async () => {
  // 初始化認證狀態
  userStore.initAuth()
  
  // 根據登入狀態導向對應頁面
  if (userStore.isAuthenticated) {
    await router.push('/chatroom')
  } else {
    await router.push('/login')
  }
})
</script>