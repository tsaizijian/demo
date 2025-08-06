<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <!-- Chat Header -->
    <div class="bg-white border-b border-gray-200 px-4 py-4 flex items-center justify-between">
      <div class="flex items-center space-x-4">
        <button
          @click="$router.back()"
          class="p-2 text-gray-400 hover:text-gray-600 transition-colors duration-200"
        >
          <svg class="w-[24px] h-[24px]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
          </svg>
        </button>
        
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
            <svg class="w-[20px] h-[20px] text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
            </svg>
          </div>
          <div>
            <h1 class="text-lg font-semibold text-gray-900">{{ chatRoom?.name || '載入中...' }}</h1>
            <p class="text-sm text-gray-500">{{ onlineMembers }} 人在線</p>
          </div>
        </div>
      </div>
      
      <div class="flex items-center space-x-2">
        <button
          @click="showMemberList = true"
          class="p-2 text-gray-400 hover:text-gray-600 transition-colors duration-200"
        >
          <svg class="w-[20px] h-[20px]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"></path>
          </svg>
        </button>
        
        <button
          @click="showSettings = true"
          class="p-2 text-gray-400 hover:text-gray-600 transition-colors duration-200"
        >
          <svg class="w-[20px] h-[20px]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
          </svg>
        </button>
      </div>
    </div>

    <!-- Messages Container -->
    <div
      ref="messagesContainer"
      class="flex-1 overflow-y-auto p-4 space-y-4"
      @scroll="handleScroll"
    >
      <!-- Load More Button -->
      <div
        v-if="hasMoreMessages"
        class="text-center"
      >
        <button
          @click="loadMoreMessages"
          :disabled="isLoadingMessages"
          class="px-4 py-2 text-sm text-blue-600 hover:text-blue-700 disabled:opacity-50"
        >
          {{ isLoadingMessages ? '載入中...' : '載入更多訊息' }}
        </button>
      </div>

      <!-- Messages List -->
      <div
        v-for="message in messages"
        :key="message.id"
        class="flex"
        :class="message.isOwn ? 'justify-end' : 'justify-start'"
      >
        <div
          class="max-w-xs lg:max-w-md px-4 py-2 rounded-2xl"
          :class="message.isOwn 
            ? 'bg-blue-600 text-white' 
            : 'bg-white border border-gray-200 text-gray-900'"
        >
          <div
            v-if="!message.isOwn"
            class="text-xs font-medium mb-1"
            :class="message.isOwn ? 'text-blue-100' : 'text-gray-500'"
          >
            {{ message.sender.name }}
          </div>
          
          <p class="text-sm">{{ message.content }}</p>
          
          <div
            class="text-xs mt-1 flex items-center justify-end space-x-1"
            :class="message.isOwn ? 'text-blue-100' : 'text-gray-400'"
          >
            <span>{{ formatMessageTime(message.timestamp) }}</span>
            <div
              v-if="message.isOwn && message.status"
              class="flex items-center"
            >
              <svg
                v-if="message.status === 'sent'"
                class="w-[16px] h-[16px]"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
              </svg>
              <svg
                v-else-if="message.status === 'delivered'"
                class="w-[16px] h-[16px]"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path fill-rule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- Typing Indicator -->
      <div
        v-if="typingUsers.length > 0"
        class="flex justify-start"
      >
        <div class="bg-gray-200 rounded-2xl px-4 py-2">
          <div class="flex items-center space-x-2">
            <div class="flex space-x-1">
              <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
              <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
              <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
            </div>
            <span class="text-xs text-gray-600">{{ typingUsers.join(', ') }} 正在輸入...</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Message Input -->
    <div class="bg-white border-t border-gray-200 p-4">
      <div class="flex items-end space-x-3">
        <button
          class="p-2 text-gray-400 hover:text-gray-600 transition-colors duration-200"
        >
          <svg class="w-[20px] h-[20px]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path>
          </svg>
        </button>
        
        <div class="flex-1">
          <textarea
            ref="messageInput"
            v-model="newMessage"
            @keydown="handleKeyDown"
            @input="handleTyping"
            placeholder="輸入訊息..."
            class="w-full px-4 py-2 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            rows="1"
            style="max-height: 120px;"
          ></textarea>
        </div>
        
        <button
          @click="handleSendMessage"
          :disabled="!newMessage.trim() || isSending"
          class="p-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
        >
          <svg
            v-if="isSending"
            class="w-[20px] h-[20px] animate-spin"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <svg
            v-else
            class="w-[20px] h-[20px]"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
const route = useRoute()
const config = useRuntimeConfig()
const { $api } = useNuxtApp()

definePageMeta({
  middleware: 'auth'
})

useSeoMeta({
  title: '聊天室 - 聊天室應用',
  description: '與朋友們即時聊天'
})

const chatRoomId = route.params.id

// 使用聊天室composable
const { 
  currentRoom: chatRoom,
  messages,
  typingUsers,
  isLoadingMessages,
  isSendingMessage: isSending,
  hasMoreMessages,
  error,
  loadChatRoom,
  loadMessages,
  sendMessage
} = useChat()

// 狀態管理
const newMessage = ref('')
const showMemberList = ref(false)
const showSettings = ref(false)
const onlineMembers = ref(0)

// DOM 引用
const messagesContainer = ref(null)
const messageInput = ref(null)

// 計算在線成員數
watch(chatRoom, (newRoom) => {
  if (newRoom && newRoom.members) {
    onlineMembers.value = newRoom.members.filter(m => m.online).length
  }
}, { immediate: true })

// 載入更多訊息
const loadMoreMessages = async () => {
  // TODO: 實現分頁載入
  console.log('載入更多訊息')
}

// 發送訊息處理
const handleSendMessage = async () => {
  if (!newMessage.value.trim() || isSending.value) return
  
  const messageContent = newMessage.value.trim()
  newMessage.value = ''
  
  try {
    await sendMessage({
      roomId: chatRoomId,
      content: messageContent,
      type: 'text'
    })
    
    nextTick(() => {
      scrollToBottom()
    })
  } catch (error) {
    console.error('發送訊息失敗:', error)
  }
}

// 處理鍵盤事件
const handleKeyDown = (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    handleSendMessage()
  }
}

// 處理輸入事件（打字指示器）
const handleTyping = () => {
  // TODO: 實現打字指示器邏輯
}

// 處理滾動事件
const handleScroll = () => {
  // TODO: 實現滾動到頂部載入更多訊息
}

// 滾動到底部
const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 格式化訊息時間
const formatMessageTime = (date) => {
  return date.toLocaleTimeString('zh-TW', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  })
}

// 頁面載入時初始化
onMounted(async () => {
  // 手動認證檢查
  const { user, checkAuth } = useAuth()
  if (!user.value) {
    console.log('聊天室詳情頁面：沒有用戶資訊，檢查認證狀態')
    const isLoggedIn = await checkAuth()
    if (!isLoggedIn) {
      console.log('聊天室詳情頁面：用戶未登入，重定向到登入頁面')
      await navigateTo('/login')
      return
    }
  }
  
  await loadChatRoom(chatRoomId)
  await loadMessages(chatRoomId)
  
  // 自動調整輸入框高度
  if (messageInput.value) {
    messageInput.value.addEventListener('input', function() {
      this.style.height = 'auto'
      this.style.height = Math.min(this.scrollHeight, 120) + 'px'
    })
  }
})
</script>