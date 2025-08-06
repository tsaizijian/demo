<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">聊天室</h1>
            <p class="text-gray-600 mt-1">選擇或創建聊天室開始對話</p>
          </div>
          <button
            @click="showCreateModal = true"
            class="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200"
          >
            <svg class="w-[20px] h-[20px] mr-[8px]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
            </svg>
            創建聊天室
          </button>
        </div>
      </div>

      <!-- Chat Room List -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="room in sortedChatRooms"
          :key="room.id"
          class="bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-all duration-200 cursor-pointer"
          @click="enterChatRoom(room.id)"
        >
          <div class="p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900">{{ room.name }}</h3>
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                {{ room.members.length }} 成員
              </span>
            </div>
            
            <p class="text-gray-600 text-sm mb-4 line-clamp-2">{{ room.description }}</p>
            
            <div class="flex items-center justify-between">
              <div class="flex -space-x-2">
                <div
                  v-for="member in room.members.slice(0, 3)"
                  :key="member.id"
                  class="w-8 h-8 bg-gradient-to-r from-blue-400 to-purple-500 rounded-full flex items-center justify-center text-white text-xs font-medium border-2 border-white"
                >
                  {{ member.name.charAt(0) }}
                </div>
                <div
                  v-if="room.members.length > 3"
                  class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center text-gray-600 text-xs font-medium border-2 border-white"
                >
                  +{{ room.members.length - 3 }}
                </div>
              </div>
              
              <div class="text-xs text-gray-500">
                {{ formatTime(room.lastActivity) }}
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div
          v-if="sortedChatRooms.length === 0 && !isLoadingRooms"
          class="col-span-full bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center"
        >
          <svg class="w-[48px] h-[48px] mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
          </svg>
          <h3 class="text-lg font-medium text-gray-900 mb-2">還沒有聊天室</h3>
          <p class="text-gray-600 mb-4">創建第一個聊天室開始對話吧！</p>
          <button
            @click="showCreateModal = true"
            class="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200"
          >
            創建聊天室
          </button>
        </div>
      </div>

      <!-- Create Chat Room Modal -->
      <div
        v-if="showCreateModal"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
        @click="showCreateModal = false"
      >
        <div
          class="bg-white rounded-xl shadow-xl max-w-md w-full mx-4"
          @click.stop
        >
          <div class="p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">創建新聊天室</h3>
            
            <form @submit.prevent="handleCreateChatRoom">
              <div class="mb-4">
                <label for="roomName" class="block text-sm font-medium text-gray-700 mb-2">
                  聊天室名稱
                </label>
                <input
                  id="roomName"
                  v-model="newRoom.name"
                  type="text"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="輸入聊天室名稱"
                >
              </div>
              
              <div class="mb-6">
                <label for="roomDescription" class="block text-sm font-medium text-gray-700 mb-2">
                  聊天室描述
                </label>
                <textarea
                  id="roomDescription"
                  v-model="newRoom.description"
                  rows="3"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  placeholder="輸入聊天室描述（選填）"
                ></textarea>
              </div>
              
              <div class="flex justify-end space-x-3">
                <button
                  type="button"
                  @click="showCreateModal = false"
                  class="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-all duration-200"
                >
                  取消
                </button>
                <button
                  type="submit"
                  :disabled="isCreating"
                  class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 transition-all duration-200"
                >
                  {{ isCreating ? '創建中...' : '創建' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const config = useRuntimeConfig()
const { $api } = useNuxtApp()

definePageMeta({
  middleware: 'auth'
})

// 手動認證檢查作為後備
const authStore = useAuth()
const { user, isAuthenticated, checkAuth } = authStore

useSeoMeta({  
  title: '聊天室列表 - 聊天室應用',
  description: '選擇或創建聊天室開始與朋友對話'
})

// 使用聊天室composable
const { 
  chatRooms: sortedChatRooms, 
  isLoadingRooms, 
  error,
  loadChatRooms, 
  createChatRoom 
} = useChat()

// 狀態管理
const showCreateModal = ref(false)
const isCreating = ref(false)
const newRoom = reactive({
  name: '',
  description: ''
})

// 創建聊天室
const handleCreateChatRoom = async () => {
  if (!newRoom.name.trim()) return
  
  isCreating.value = true
  
  try {
    await createChatRoom({
      name: newRoom.name,
      description: newRoom.description
    })
    
    // 重置表單
    newRoom.name = ''
    newRoom.description = ''
    showCreateModal.value = false
    
  } catch (error) {
    console.error('創建聊天室失敗:', error)
  } finally {
    isCreating.value = false
  }
}

// 進入聊天室
const enterChatRoom = (roomId) => {
  navigateTo(`/chat/${roomId}`)
}

// 格式化時間
const formatTime = (date) => {
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (minutes < 1) return '剛剛'
  if (minutes < 60) return `${minutes}分鐘前`
  if (hours < 24) return `${hours}小時前`
  if (days < 7) return `${days}天前`
  
  return date.toLocaleDateString()
}

// 頁面載入時獲取聊天室列表
onMounted(async () => {
  // 手動認證檢查作為後備
  if (!user.value) {
    console.log('聊天室頁面：沒有用戶資訊，檢查認證狀態')
    const isLoggedIn = await checkAuth()
    if (!isLoggedIn) {
      console.log('聊天室頁面：用戶未登入，重定向到登入頁面')
      await navigateTo('/login')
      return
    }
  }
  
  await loadChatRooms()
})
</script>