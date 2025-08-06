<template>
  <div class="flex flex-col h-full bg-white">
    <!-- Chat Header -->
    <div class="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
          <svg class="w-[20px] h-[20px] text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
          </svg>
        </div>
        <div>
          <h3 class="font-semibold text-gray-900">{{ room?.name || '載入中...' }}</h3>
          <p class="text-sm text-gray-500">{{ onlineCount }} 人在線</p>
        </div>
      </div>
      
      <div class="flex items-center space-x-2">
        <button
          @click="$emit('toggleMemberList')"
          class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-all duration-200"
        >
          <svg class="w-[20px] h-[20px]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"></path>
          </svg>
        </button>
        
        <button
          @click="$emit('showSettings')"
          class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-all duration-200"
        >
          <svg class="w-[20px] h-[20px]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
          </svg>
        </button>
      </div>
    </div>

    <!-- Messages Area -->
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
          @click="$emit('loadMoreMessages')"
          :disabled="isLoadingMessages"
          class="px-4 py-2 text-sm text-blue-600 hover:text-blue-700 disabled:opacity-50 hover:bg-blue-50 rounded-lg transition-all duration-200"
        >
          {{ isLoadingMessages ? '載入中...' : '載入更多訊息' }}
        </button>
      </div>

      <!-- Date Separator -->
      <div
        v-for="(messagesGroup, date) in groupedMessages"
        :key="date"
        class="space-y-4"
      >
        <div class="flex items-center justify-center">
          <div class="px-3 py-1 bg-gray-200 text-gray-600 text-xs rounded-full">
            {{ formatDate(date) }}
          </div>
        </div>
        
        <!-- Messages -->
        <div
          v-for="message in messagesGroup"
          :key="message.id"
          class="flex"
          :class="message.isOwn ? 'justify-end' : 'justify-start'"
        >
          <!-- Avatar for other users -->
          <div
            v-if="!message.isOwn"
            class="flex-shrink-0 mr-3"
          >
            <div class="w-8 h-8 bg-gradient-to-r from-gray-400 to-gray-600 rounded-full flex items-center justify-center">
              <span class="text-white text-xs font-medium">
                {{ message.sender.name.charAt(0).toUpperCase() }}
              </span>
            </div>
          </div>
          
          <!-- Message Bubble -->
          <div
            class="max-w-xs lg:max-w-md px-4 py-2 rounded-2xl shadow-sm"
            :class="message.isOwn 
              ? 'bg-blue-600 text-white' 
              : 'bg-gray-100 text-gray-900'"
          >
            <!-- Sender Name (for group messages) -->
            <div
              v-if="!message.isOwn && showSenderNames"
              class="text-xs font-medium mb-1 opacity-75"
            >
              {{ message.sender.name }}
            </div>
            
            <!-- Message Content -->
            <p class="text-sm whitespace-pre-wrap">{{ message.content }}</p>
            
            <!-- Message Meta -->
            <div
              class="text-xs mt-1 flex items-center justify-end space-x-1"
              :class="message.isOwn ? 'text-blue-100' : 'text-gray-500'"
            >
              <span>{{ formatMessageTime(message.timestamp) }}</span>
              
              <!-- Message Status (for own messages) -->
              <div
                v-if="message.isOwn && message.status"
                class="flex items-center"
              >
                <!-- Sending -->
                <svg
                  v-if="message.status === 'sending'"
                  class="w-[14px] h-[14px] animate-spin"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                
                <!-- Sent -->
                <svg
                  v-else-if="message.status === 'sent'"
                  class="w-[14px] h-[14px]"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
                </svg>
                
                <!-- Delivered -->
                <svg
                  v-else-if="message.status === 'delivered'"
                  class="w-[14px] h-[14px]"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path fill-rule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                </svg>
                
                <!-- Failed -->
                <svg
                  v-else-if="message.status === 'failed'"
                  class="w-[14px] h-[14px] text-red-400"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z" clip-rule="evenodd"></path>
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Typing Indicator -->
      <div
        v-if="typingUsers.length > 0"
        class="flex justify-start"
      >
        <div class="flex items-center space-x-3">
          <div class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
            <div class="flex space-x-1">
              <div class="w-1 h-1 bg-gray-500 rounded-full animate-bounce"></div>
              <div class="w-1 h-1 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
              <div class="w-1 h-1 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
            </div>
          </div>
          <div class="bg-gray-100 rounded-2xl px-4 py-2">
            <span class="text-xs text-gray-600">{{ typingUsers.join(', ') }} 正在輸入...</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Message Input -->
    <div class="border-t border-gray-200 p-4 bg-gray-50">
      <div class="flex items-end space-x-3">
        <!-- Attachment Button -->
        <button
          @click="$emit('showAttachmentOptions')"
          class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-all duration-200"
        >
          <svg class="w-[20px] h-[20px]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path>
          </svg>
        </button>
        
        <!-- Message Input -->
        <div class="flex-1">
          <textarea
            ref="messageInput"
            v-model="newMessage"
            @keydown="handleKeyDown"
            @input="handleInput"
            placeholder="輸入訊息..."
            class="w-full px-4 py-2 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none bg-white"
            rows="1"
            style="max-height: 120px;"
          ></textarea>
        </div>
        
        <!-- Send Button -->
        <button
          @click="sendMessage"
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
const props = defineProps({
  room: {
    type: Object,
    default: null
  },
  messages: {
    type: Array,
    default: () => []
  },
  typingUsers: {
    type: Array,
    default: () => []
  },
  hasMoreMessages: {
    type: Boolean,
    default: false
  },
  isLoadingMessages: {
    type: Boolean,
    default: false
  },
  isSending: {
    type: Boolean,
    default: false
  },
  showSenderNames: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits([
  'sendMessage',
  'loadMoreMessages',
  'toggleMemberList',
  'showSettings',
  'showAttachmentOptions',
  'typing'
])

const newMessage = ref('')
const messagesContainer = ref(null)
const messageInput = ref(null)

// 計算在線人數
const onlineCount = computed(() => {
  return props.room?.members?.filter(member => member.online).length || 0
})

// 按日期分組訊息
const groupedMessages = computed(() => {
  const groups = {}
  
  props.messages.forEach(message => {
    const date = new Date(message.timestamp).toDateString()
    if (!groups[date]) {
      groups[date] = []
    }
    groups[date].push(message)
  })
  
  return groups
})

// 發送訊息
const sendMessage = () => {
  if (!newMessage.value.trim()) return
  
  emit('sendMessage', newMessage.value.trim())
  newMessage.value = ''
  
  // 重置輸入框高度
  nextTick(() => {
    if (messageInput.value) {
      messageInput.value.style.height = 'auto'
    }
  })
}

// 處理鍵盤事件
const handleKeyDown = (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

// 處理輸入事件
const handleInput = () => {
  // 自動調整高度
  if (messageInput.value) {
    messageInput.value.style.height = 'auto'
    messageInput.value.style.height = Math.min(messageInput.value.scrollHeight, 120) + 'px'
  }
  
  // 觸發打字事件
  emit('typing')
}

// 處理滾動事件
const handleScroll = () => {
  if (!messagesContainer.value) return
  
  const { scrollTop } = messagesContainer.value
  if (scrollTop === 0 && props.hasMoreMessages) {
    emit('loadMoreMessages')
  }
}

// 滾動到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)
  
  if (date.toDateString() === today.toDateString()) {
    return '今天'
  } else if (date.toDateString() === yesterday.toDateString()) {
    return '昨天'
  } else {
    return date.toLocaleDateString('zh-TW', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }
}

// 格式化訊息時間
const formatMessageTime = (date) => {
  return new Date(date).toLocaleTimeString('zh-TW', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  })
}

// 監聽訊息變化，自動滾動到底部
watch(() => props.messages, () => {
  scrollToBottom()
}, { deep: true })

// 組件掛載時滾動到底部
onMounted(() => {
  scrollToBottom()
})

// 暴露方法給父組件
defineExpose({
  scrollToBottom
})
</script>