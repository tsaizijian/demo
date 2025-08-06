<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 relative overflow-hidden flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <!-- Background decoration -->
    <div class="absolute inset-0 bg-grid-slate-100 bg-[size:20px_20px] opacity-20"></div>
    <div class="absolute top-0 right-0 w-72 h-72 bg-blue-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
    <div class="absolute bottom-0 left-0 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>

    <div class="relative z-10 max-w-md w-full">
      <!-- Header -->
      <div class="text-center mb-8 animate-fade-in">
        <div class="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl mb-6 shadow-lg">
          <svg class="w-[32px] h-[32px] text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"></path>
          </svg>
        </div>
        
        <h2 class="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent mb-2">
          歡迎回來
        </h2>
        <p class="text-gray-600">
          還沒有帳號？
          <NuxtLink to="/register" class="font-semibold text-blue-600 hover:text-blue-700 transition-colors">
            立即註冊
          </NuxtLink>
        </p>
      </div>

      <!-- Login Form Card -->
      <div class="bg-white/80 backdrop-blur-sm rounded-3xl shadow-2xl border border-gray-100 p-8 animate-slide-up">
      
        <form class="space-y-6" @submit.prevent="handleLogin">
          <!-- Username Field -->
          <div class="space-y-2">
            <label for="username" class="block text-sm font-semibold text-gray-700">使用者名稱</label>
            <div class="relative group">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="w-[20px] h-[20px] text-gray-400 group-focus-within:text-blue-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                </svg>
              </div>
              <input
                id="username"
                v-model="loginForm.username"
                name="username"
                type="text"
                required
                class="block w-full pl-10 pr-3 py-3 border border-gray-200 rounded-xl text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 bg-gray-50 focus:bg-white"
                placeholder="請輸入使用者名稱"
              />
            </div>
          </div>

          <!-- Password Field -->
          <div class="space-y-2">
            <label for="password" class="block text-sm font-semibold text-gray-700">密碼</label>
            <div class="relative group">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="w-[20px] h-[20px] text-gray-400 group-focus-within:text-blue-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
                </svg>
              </div>
              <input
                id="password"
                v-model="loginForm.password"
                name="password"
                type="password"
                required
                class="block w-full pl-10 pr-3 py-3 border border-gray-200 rounded-xl text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 bg-gray-50 focus:bg-white"
                placeholder="請輸入密碼"
              />
            </div>
          </div>

          <!-- Remember Me & Forgot Password -->
          <div class="flex items-center justify-between pt-2">
            <div class="flex items-center">
              <input
                id="remember-me"
                v-model="loginForm.rememberMe"
                name="remember-me"
                type="checkbox"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded transition-colors"
              />
              <label for="remember-me" class="ml-2 block text-sm font-medium text-gray-700">
                記住我
              </label>
            </div>

            <div class="text-sm">
              <NuxtLink to="/forgot-password" class="font-semibold text-blue-600 hover:text-blue-700 transition-colors">
                忘記密碼？
              </NuxtLink>
            </div>
          </div>

          <!-- Submit Button -->
          <div class="pt-4">
            <button
              type="submit"
              :disabled="isLoading"
              class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-base font-semibold rounded-xl text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-[1.02] transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              <span v-if="isLoading" class="absolute left-0 inset-y-0 flex items-center pl-3">
                <svg class="animate-spin w-[20px] h-[20px] text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </span>
              <span class="flex items-center">
                <svg v-if="!isLoading" class="w-[20px] h-[20px] mr-[8px] group-hover:animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"></path>
                </svg>
                {{ isLoading ? '登入中...' : '立即登入' }}
              </span>
            </button>
          </div>

          <!-- Error Message -->
          <div v-if="errorMessage" class="animate-shake bg-red-50 border border-red-200 rounded-xl p-4">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="w-[20px] h-[20px] text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3">
                <h3 class="text-sm font-semibold text-red-800">
                  登入失敗
                </h3>
                <div class="mt-1 text-sm text-red-700">
                  {{ errorMessage }}
                </div>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
const config = useRuntimeConfig()
const { $api } = useNuxtApp()

useSeoMeta({
  title: '登入 - 聊天室應用',
  description: '登入您的聊天室帳號，開始與朋友聊天'
})

definePageMeta({
  layout: false
})

const loginForm = reactive({
  username: '',
  password: '',
  rememberMe: false
})

const isLoading = ref(false)
const errorMessage = ref('')

const { login } = useAuth()

const handleLogin = async () => {
  if (!loginForm.username || !loginForm.password) {
    errorMessage.value = '請填寫使用者名稱和密碼'
    return
  }

  isLoading.value = true
  errorMessage.value = ''

  try {
    const result = await login({
      username: loginForm.username,
      password: loginForm.password,
      rememberMe: loginForm.rememberMe
    })

    if (result.success) {
      console.log('登入成功，用戶資訊:', result.user)
      
      // 檢查認證狀態是否正確設置
      const { user: currentUser, isAuthenticated } = useAuth()
      console.log('登入後狀態檢查:', {
        currentUser: currentUser.value,
        isAuthenticated: isAuthenticated.value
      })
      
      // 等待狀態更新完成
      await nextTick()
      
      console.log('nextTick 後狀態:', {
        currentUser: currentUser.value,
        isAuthenticated: isAuthenticated.value
      })
      
      // 導向聊天室頁面
      try {
        console.log('嘗試導向到 /chat')
        await navigateTo('/chat', { replace: true })
        console.log('導向成功')
      } catch (navError) {
        console.error('Nuxt 導向失敗，使用 window.location:', navError)
        // 如果 Nuxt 導向失敗，使用瀏覽器原生導向
        window.location.replace('/chat')
      }
    } else {
      errorMessage.value = result.message || '登入失敗，請檢查您的帳號密碼'
    }
  } catch (error) {
    console.error('登入錯誤:', error)
    errorMessage.value = '網路錯誤，請稍後再試'
  } finally {
    isLoading.value = false
  }
}
</script>