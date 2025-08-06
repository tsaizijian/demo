<template>
  <div class="min-h-screen bg-gray-100 p-8">
    <div class="max-w-4xl mx-auto">
      <h1 class="text-3xl font-bold mb-8">API 連接測試</h1>
      
      <div class="grid md:grid-cols-2 gap-6">
        <!-- CORS 測試 -->
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-xl font-semibold mb-4">CORS 測試</h2>
          <div class="space-y-4">
            <button
              @click="testPublicApi"
              :disabled="isLoading"
              class="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {{ isLoading ? '測試中...' : '測試公開 API' }}
            </button>
            
            <button
              @click="testAuthApi"
              :disabled="isLoading"
              class="w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
            >
              {{ isLoading ? '測試中...' : '測試認證 API' }}
            </button>
            
            <button
              @click="testChatRoomApi"
              :disabled="isLoading"
              class="w-full px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50"
            >
              {{ isLoading ? '測試中...' : '測試聊天室 API' }}
            </button>
          </div>
        </div>

        <!-- 認證狀態 -->
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-xl font-semibold mb-4">認證狀態</h2>
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
          </div>
        </div>
      </div>

      <!-- 測試結果 -->
      <div class="mt-8 bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4">測試結果</h2>
        <div class="space-y-2 max-h-96 overflow-y-auto">
          <div 
            v-for="(result, index) in testResults" 
            :key="index"
            class="p-3 rounded border-l-4"
            :class="result.success ? 'border-green-500 bg-green-50' : 'border-red-500 bg-red-50'"
          >
            <div class="font-semibold">{{ result.timestamp }} - {{ result.test }}</div>
            <div class="text-sm mt-1">
              <strong>狀態:</strong> {{ result.success ? '成功' : '失敗' }}
            </div>
            <pre class="mt-2 text-xs bg-white p-2 rounded overflow-auto">{{ JSON.stringify(result.data, null, 2) }}</pre>
          </div>
        </div>
        <button 
          @click="clearResults" 
          class="mt-4 px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
        >
          清除結果
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
const { user, isAuthenticated } = useAuth()
const { $api } = useNuxtApp()

const isLoading = ref(false)
const testResults = ref([])

const addResult = (test, data, success = true) => {
  testResults.value.unshift({
    timestamp: new Date().toLocaleTimeString(),
    test,
    data,
    success
  })
  
  // 只保留最新的 10 條結果
  if (testResults.value.length > 10) {
    testResults.value = testResults.value.slice(0, 10)
  }
}

const testPublicApi = async () => {
  isLoading.value = true
  try {
    const result = await $api.get('/api/test/public')
    addResult('公開 API 測試', result, true)
  } catch (error) {
    addResult('公開 API 測試', { error: error.message, details: error }, false)
  } finally {
    isLoading.value = false
  }
}

const testAuthApi = async () => {
  isLoading.value = true
  try {
    const result = await $api.get('/api/test/auth')
    addResult('認證 API 測試', result, true)
  } catch (error) {
    addResult('認證 API 測試', { error: error.message, details: error }, false)
  } finally {
    isLoading.value = false
  }
}

const testChatRoomApi = async () => {
  isLoading.value = true
  try {
    const result = await $api.get('/chatroom/list')
    addResult('聊天室 API 測試', result, true)
  } catch (error) {
    addResult('聊天室 API 測試', { error: error.message, details: error }, false)
  } finally {
    isLoading.value = false
  }
}

const clearResults = () => {
  testResults.value = []
}
</script>