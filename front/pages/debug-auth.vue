<template>
  <div class="min-h-screen bg-gray-100 p-8">
    <div class="max-w-4xl mx-auto">
      <h1 class="text-3xl font-bold mb-8">認證狀態調試</h1>
      
      <div class="grid md:grid-cols-2 gap-6">
        <!-- 當前狀態 -->
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-xl font-semibold mb-4">當前狀態</h2>
          <div class="space-y-2 text-sm">
            <div>
              <strong>isAuthenticated:</strong> 
              <span :class="isAuthenticated ? 'text-green-600' : 'text-red-600'">
                {{ isAuthenticated }}
              </span>
            </div>
            <div>
              <strong>user:</strong> 
              <pre class="bg-gray-100 p-2 rounded text-xs overflow-auto">{{ JSON.stringify(user, null, 2) }}</pre>
            </div>
            <div>
              <strong>error:</strong> 
              <span class="text-red-600">{{ error }}</span>
            </div>
          </div>
        </div>

        <!-- 測試按鈕 -->
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-xl font-semibold mb-4">測試操作</h2>
          <div class="space-y-4">
            <button
              @click="testCheckAuth"
              :disabled="isLoading"
              class="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {{ isLoading ? '檢查中...' : '檢查認證狀態' }}
            </button>
            
            <button
              @click="testGetCurrentUser"
              :disabled="isLoading"
              class="w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
            >
              {{ isLoading ? '獲取中...' : '獲取當前用戶' }}
            </button>
            
            <button
              @click="testNavigateToChat"
              class="w-full px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
            >
              測試導向到聊天室
            </button>
            
            <button
              @click="testLogout"
              :disabled="isLoading"
              class="w-full px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
            >
              {{ isLoading ? '登出中...' : '測試登出' }}
            </button>
          </div>
        </div>
      </div>

      <!-- API 回應日誌 -->
      <div class="mt-8 bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4">API 回應日誌</h2>
        <div class="space-y-2 max-h-96 overflow-y-auto">
          <div 
            v-for="(log, index) in apiLogs" 
            :key="index"
            class="p-2 bg-gray-50 rounded text-xs border-l-4"
            :class="log.type === 'error' ? 'border-red-500' : log.type === 'success' ? 'border-green-500' : 'border-blue-500'"
          >
            <div class="font-semibold">{{ log.timestamp }} - {{ log.action }}</div>
            <pre class="mt-1 whitespace-pre-wrap">{{ JSON.stringify(log.data, null, 2) }}</pre>
          </div>
        </div>
        <button 
          @click="clearLogs" 
          class="mt-4 px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
        >
          清除日誌
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
const { 
  user, 
  isAuthenticated, 
  isLoading, 
  error, 
  checkAuth, 
  getCurrentUser,
  logout 
} = useAuth()

const apiLogs = ref([])

const addLog = (action, data, type = 'info') => {
  apiLogs.value.unshift({
    timestamp: new Date().toLocaleTimeString(),
    action,
    data,
    type
  })
  
  // 只保留最新的 20 條日誌
  if (apiLogs.value.length > 20) {
    apiLogs.value = apiLogs.value.slice(0, 20)
  }
}

const testCheckAuth = async () => {
  try {
    const result = await checkAuth()
    addLog('checkAuth', { result, user: user.value, isAuthenticated: isAuthenticated.value }, 'success')
  } catch (err) {
    addLog('checkAuth', { error: err.message }, 'error')
  }
}

const testGetCurrentUser = async () => {
  try {
    const result = await getCurrentUser()
    addLog('getCurrentUser', { result, user: user.value }, 'success')
  } catch (err) {
    addLog('getCurrentUser', { error: err.message }, 'error')
  }
}

const testNavigateToChat = async () => {
  try {
    addLog('navigateToChat', '嘗試導向到聊天室頁面', 'info')
    await navigateTo('/chat')
  } catch (err) {
    addLog('navigateToChat', { error: err.message }, 'error')
    // 如果失敗，嘗試使用 window.location
    window.location.href = '/chat'
  }
}

const testLogout = async () => {
  try {
    const result = await logout()
    addLog('logout', result, result.success ? 'success' : 'error')
  } catch (err) {
    addLog('logout', { error: err.message }, 'error')
  }
}

const clearLogs = () => {
  apiLogs.value = []
}

// 頁面載入時自動檢查狀態
onMounted(() => {
  addLog('pageLoad', '頁面載入，當前狀態', 'info')
  testCheckAuth()
})
</script>