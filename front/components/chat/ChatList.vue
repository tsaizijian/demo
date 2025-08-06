<template>
  <div class="flex flex-col h-full bg-white border-r border-gray-200">
    <!-- Header -->
    <div class="p-4 border-b border-gray-200">
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-semibold text-gray-900">聊天室</h2>
        <button
          @click="$emit('showCreateModal')"
          class="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all duration-200"
        >
          <svg class="w-[20px] h-[20px]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
          </svg>
        </button>
      </div>
      
      <!-- Search -->
      <div class="mt-3 relative">
        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <svg class="w-[16px] h-[16px] text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
          </svg>
        </div>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="搜尋聊天室..."
          class="w-full pl-9 pr-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>
    </div>

    <!-- Chat Room List -->
    <div class="flex-1 overflow-y-auto">
      <div class="p-2 space-y-1">
        <div
          v-for="room in filteredRooms"
          :key="room.id"
          @click="$emit('selectRoom', room)"
          class="p-3 rounded-lg cursor-pointer transition-all duration-200 hover:bg-gray-50"
          :class="{
            'bg-blue-50 border-l-4 border-blue-500': selectedRoomId === room.id,
            'hover:bg-gray-50': selectedRoomId !== room.id
          }"
        >
          <div class="flex items-center space-x-3">
            <!-- Room Avatar -->
            <div class="flex-shrink-0">
              <div class="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <svg class="w-[20px] h-[20px] text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                </svg>
              </div>
            </div>
            
            <!-- Room Info -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between">
                <h3 class="text-sm font-medium text-gray-900 truncate">{{ room.name }}</h3>
                <span class="text-xs text-gray-500">{{ formatTime(room.lastActivity) }}</span>
              </div>
              
              <div class="flex items-center justify-between mt-1">
                <p class="text-sm text-gray-600 truncate">{{ room.lastMessage || room.description }}</p>
                <div class="flex items-center space-x-2">
                  <!-- Unread Count -->
                  <span
                    v-if="room.unreadCount > 0"
                    class="inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-red-500 rounded-full"
                  >
                    {{ room.unreadCount > 99 ? '99+' : room.unreadCount }}
                  </span>
                  
                  <!-- Online Members Count -->
                  <div class="flex items-center text-xs text-gray-500">
                    <div class="w-2 h-2 bg-green-500 rounded-full mr-1"></div>
                    {{ room.onlineMembers || 0 }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Empty State -->
      <div
        v-if="filteredRooms.length === 0"
        class="flex flex-col items-center justify-center h-64 text-center p-4"
      >
        <svg class="w-[48px] h-[48px] text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
        </svg>
        <h3 class="text-lg font-medium text-gray-900 mb-2">沒有找到聊天室</h3>
        <p class="text-gray-600 mb-4">試試其他搜尋詞或創建新的聊天室</p>
        <button
          @click="$emit('showCreateModal')"
          class="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200"
        >
          <svg class="w-[16px] h-[16px] mr-[8px]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
          </svg>
          創建聊天室
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  rooms: {
    type: Array,
    default: () => []
  },
  selectedRoomId: {
    type: [String, Number],
    default: null
  }
})

const emit = defineEmits(['selectRoom', 'showCreateModal'])

const searchQuery = ref('')

// 過濾聊天室
const filteredRooms = computed(() => {
  if (!searchQuery.value) return props.rooms
  
  const query = searchQuery.value.toLowerCase()
  return props.rooms.filter(room => 
    room.name.toLowerCase().includes(query) ||
    room.description?.toLowerCase().includes(query)
  )
})

// 格式化時間
const formatTime = (date) => {
  if (!date) return ''
  
  const now = new Date()
  const messageDate = new Date(date)
  const diff = now - messageDate
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (minutes < 1) return '剛剛'
  if (minutes < 60) return `${minutes}分鐘前`
  if (hours < 24) return `${hours}小時前`
  if (days < 7) return `${days}天前`
  
  return messageDate.toLocaleDateString('zh-TW', {
    month: 'short',
    day: 'numeric'
  })
}
</script>