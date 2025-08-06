<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          重設密碼
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          輸入您的電子郵件地址，我們將發送重設連結給您
        </p>
      </div>
      
      <form v-if="!emailSent" class="mt-8 space-y-6" @submit.prevent="handleForgotPassword">
        <div>
          <label for="email" class="block text-sm font-medium text-gray-700">電子郵件</label>
          <input
            id="email"
            v-model="email"
            name="email"
            type="email"
            required
            class="mt-1 relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            placeholder="請輸入您的電子郵件"
          />
        </div>

        <div>
          <button
            type="submit"
            :disabled="isLoading || !email"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="isLoading" class="absolute left-0 inset-y-0 flex items-center pl-3">
              <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </span>
            {{ isLoading ? '發送中...' : '發送重設連結' }}
          </button>
        </div>

        <div v-if="errorMessage" class="rounded-md bg-red-50 p-4">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-800">發送失敗</h3>
              <div class="mt-2 text-sm text-red-700">{{ errorMessage }}</div>
            </div>
          </div>
        </div>
      </form>

      <!-- 成功狀態 -->
      <div v-if="emailSent" class="text-center space-y-4">
        <div class="rounded-md bg-green-50 p-4">
          <div class="flex justify-center">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.236 4.53L7.53 10.23a.75.75 0 00-1.06 1.06l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-green-800">郵件已發送</h3>
              <div class="mt-2 text-sm text-green-700">
                重設密碼的連結已發送至 {{ email }}
              </div>
            </div>
          </div>
        </div>

        <div class="bg-blue-50 border border-blue-200 rounded-md p-4">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-blue-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a.75.75 0 000 1.5h.253a.25.25 0 01.244.304l-.459 2.066A1.75 1.75 0 0010.747 15H11a.75.75 0 000-1.5h-.253a.25.25 0 01-.244-.304l.459-2.066A1.75 1.75 0 009.253 9H9z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-blue-800">接下來該怎麼做？</h3>
              <div class="mt-2 text-sm text-blue-700">
                <ul class="list-disc list-inside space-y-1">
                  <li>檢查您的電子郵件收件匣</li>
                  <li>點擊郵件中的重設連結</li>
                  <li>設定新的密碼</li>
                  <li>使用新密碼登入</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <div class="flex justify-center space-x-4">
          <button
            @click="resendEmail"
            :disabled="resendCooldown > 0"
            class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ resendCooldown > 0 ? `重新發送 (${resendCooldown}s)` : '重新發送郵件' }}
          </button>
          <NuxtLink
            to="/login"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            返回登入
          </NuxtLink>
        </div>
      </div>

      <!-- 返回登入連結 -->
      <div v-if="!emailSent" class="text-center">
        <NuxtLink to="/login" class="font-medium text-blue-600 hover:text-blue-500">
          ← 返回登入頁面
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup>
const config = useRuntimeConfig()
const { $api } = useNuxtApp()

useSeoMeta({
  title: '忘記密碼 - 聊天室應用',
  description: '重設您的聊天室帳號密碼'
})

definePageMeta({
  layout: false
})

const email = ref('')
const isLoading = ref(false)
const errorMessage = ref('')
const emailSent = ref(false)
const resendCooldown = ref(0)

let cooldownTimer = null

const handleForgotPassword = async () => {
  if (!email.value) {
    errorMessage.value = '請輸入電子郵件地址'
    return
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email.value)) {
    errorMessage.value = '請輸入有效的電子郵件地址'
    return
  }

  isLoading.value = true
  errorMessage.value = ''

  try {
    // 這裡應該呼叫忘記密碼的 API
    // 目前暫時模擬成功回應
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    emailSent.value = true
    startResendCooldown()
  } catch (error) {
    console.error('忘記密碼錯誤:', error)
    errorMessage.value = '發送失敗，請稍後再試'
  } finally {
    isLoading.value = false
  }
}

const resendEmail = async () => {
  if (resendCooldown.value > 0) return
  
  isLoading.value = true
  
  try {
    // 重新發送郵件
    await new Promise(resolve => setTimeout(resolve, 1000))
    startResendCooldown()
  } catch (error) {
    console.error('重新發送郵件錯誤:', error)
  } finally {
    isLoading.value = false
  }
}

const startResendCooldown = () => {
  resendCooldown.value = 60
  cooldownTimer = setInterval(() => {
    resendCooldown.value--
    if (resendCooldown.value <= 0) {
      clearInterval(cooldownTimer)
    }
  }, 1000)
}

onUnmounted(() => {
  if (cooldownTimer) {
    clearInterval(cooldownTimer)
  }
})
</script>