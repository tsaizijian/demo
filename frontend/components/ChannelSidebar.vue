<template>
  <aside class="w-64 bg-gray-50 border-r border-gray-200 flex flex-col h-full">
    <!-- 頻道側邊欄標題 -->
    <div class="p-4 border-b border-gray-200 bg-white">
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-semibold text-gray-900">頻道列表</h2>
        <button
          @click="showCreateForm = !showCreateForm"
          class="p-1.5 rounded-md hover:bg-gray-100 transition-colors"
          title="建立新頻道"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" />
          </svg>
        </button>
      </div>
    </div>

    <!-- 建立頻道表單 -->
    <div v-if="showCreateForm" class="p-4 bg-blue-50 border-b border-gray-200">
      <h3 class="text-sm font-medium text-gray-900 mb-3">建立新頻道</h3>
      <div class="space-y-3">
        <div>
          <input
            v-model="newChannel.name"
            type="text"
            placeholder="頻道名稱"
            class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            @keydown.enter="createChannel"
          />
        </div>
        <div>
          <textarea
            v-model="newChannel.description"
            placeholder="頻道描述（選填）"
            rows="2"
            class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
          ></textarea>
        </div>
        <div class="flex items-center">
          <input
            v-model="newChannel.isPrivate"
            type="checkbox"
            id="private-channel"
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label for="private-channel" class="ml-2 text-sm text-gray-700">私人頻道</label>
        </div>
        <div class="flex justify-end space-x-2">
          <button
            @click="cancelCreate"
            class="px-3 py-1.5 text-sm text-gray-600 hover:text-gray-800 transition-colors"
          >
            取消
          </button>
          <button
            @click="createChannel"
            :disabled="!newChannel.name.trim() || creating"
            class="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {{ creating ? '建立中...' : '建立' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 頻道列表 -->
    <div class="flex-1 overflow-y-auto">
      <!-- 公開頻道 -->
      <div class="p-2">
        <div class="px-2 py-1 text-xs font-medium text-gray-500 uppercase tracking-wide">
          公開頻道
        </div>
        
        <div class="mt-1 space-y-1">
          <div
            v-for="channel in channelStore.publicChannels"
            :key="channel.id"
            @click="switchChannel(channel)"
            class="group flex items-center px-2 py-2 text-sm rounded-md cursor-pointer transition-colors duration-200"
            :class="{
              'bg-blue-50 text-blue-700 border-r-2 border-blue-600': channel.id === channelStore.currentChannelId,
              'text-gray-700 hover:bg-gray-100': channel.id !== channelStore.currentChannelId
            }"
          >
            <UIcon 
              name="i-heroicons-hashtag" 
              class="w-4 h-4 mr-2 flex-shrink-0"
              :class="{
                'text-blue-600': channel.id === channelStore.currentChannelId,
                'text-gray-400': channel.id !== channelStore.currentChannelId
              }"
            />
            
            <div class="flex-1 min-w-0">
              <div class="font-medium truncate">{{ channel.name }}</div>
              <div v-if="channel.description" class="text-xs text-gray-500 truncate">
                {{ channel.description }}
              </div>
            </div>
            
            <!-- 頻道成員數量 -->
            <div v-if="getChannelMemberCount(channel.id)" class="ml-2">
              <span class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                {{ getChannelMemberCount(channel.id) }}
              </span>
            </div>
            
            <!-- 頻道設定按鈕 -->
            <UButton
              v-if="isChannelAdmin(channel.id)"
              @click.stop="openChannelSettings(channel)"
              size="xs"
              variant="ghost"
              icon="i-heroicons-cog-6-tooth"
              class="ml-1 opacity-0 group-hover:opacity-100 transition-opacity"
            />
          </div>
        </div>
      </div>

      <!-- 私人頻道 -->
      <div v-if="channelStore.privateChannels.length > 0" class="p-2 border-t border-gray-200">
        <div class="px-2 py-1 text-xs font-medium text-gray-500 uppercase tracking-wide">
          私人頻道
        </div>
        
        <div class="mt-1 space-y-1">
          <div
            v-for="channel in channelStore.privateChannels"
            :key="channel.id"
            @click="switchChannel(channel)"
            class="group flex items-center px-2 py-2 text-sm rounded-md cursor-pointer transition-colors duration-200"
            :class="{
              'bg-blue-50 text-blue-700 border-r-2 border-blue-600': channel.id === channelStore.currentChannelId,
              'text-gray-700 hover:bg-gray-100': channel.id !== channelStore.currentChannelId
            }"
          >
            <UIcon 
              name="i-heroicons-lock-closed" 
              class="w-4 h-4 mr-2 flex-shrink-0"
              :class="{
                'text-blue-600': channel.id === channelStore.currentChannelId,
                'text-gray-400': channel.id !== channelStore.currentChannelId
              }"
            />
            
            <div class="flex-1 min-w-0">
              <div class="font-medium truncate">{{ channel.name }}</div>
              <div v-if="channel.description" class="text-xs text-gray-500 truncate">
                {{ channel.description }}
              </div>
            </div>
            
            <!-- 頻道設定按鈕 -->
            <UButton
              v-if="isChannelAdmin(channel.id)"
              @click.stop="openChannelSettings(channel)"
              size="xs"
              variant="ghost"
              icon="i-heroicons-cog-6-tooth"
              class="ml-1 opacity-0 group-hover:opacity-100 transition-opacity"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 線上使用者區域 -->
    <div class="border-t border-gray-200 bg-white">
      <div class="p-4">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-sm font-medium text-gray-900">線上使用者</h3>
          <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
            {{ channelStore.currentChannelMembers.length }}
          </span>
        </div>
        
        <div class="space-y-1 max-h-32 overflow-y-auto">
          <div
            v-for="member in channelStore.currentChannelMembers"
            :key="member.id"
            class="flex items-center text-sm text-gray-700"
          >
            <div class="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
            <span class="truncate">{{ member.display_name }}</span>
            
            <!-- 角色標籤 -->
            <UBadge
              v-if="member.role !== 'member'"
              :label="member.role === 'owner' ? '擁有者' : '管理員'"
              color="blue"
              variant="soft"
              size="xs"
              class="ml-auto"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 載入狀態 -->
    <div v-if="channelStore.loading" class="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center">
      <div class="text-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        <div class="mt-2 text-sm text-gray-600">載入中...</div>
      </div>
    </div>

    <!-- 錯誤提示 -->
    <UAlert
      v-if="channelStore.error"
      icon="i-heroicons-exclamation-triangle"
      color="red"
      variant="soft"
      :title="channelStore.error"
      class="m-2"
      :close-button="{
        icon: 'i-heroicons-x-mark-20-solid',
        color: 'red',
        variant: 'link'
      }"
      @close="channelStore.clearError()"
    />
  </aside>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useChannelStore } from '~/stores/channel'
import { useUserStore } from '~/stores/user'

const channelStore = useChannelStore()
const userStore = useUserStore()

// 建立頻道相關狀態
const showCreateForm = ref(false)
const creating = ref(false)
const newChannel = reactive({
  name: '',
  description: '',
  isPrivate: false
})

// 建立頻道方法
const createChannel = async () => {
  if (!newChannel.name.trim() || creating.value) return
  
  creating.value = true
  
  try {
    const result = await channelStore.createChannel({
      name: newChannel.name.trim(),
      description: newChannel.description.trim(),
      is_private: newChannel.isPrivate
    })
    
    if (result.success) {
      // 重置表單
      newChannel.name = ''
      newChannel.description = ''
      newChannel.isPrivate = false
      showCreateForm.value = false
      
      console.log('頻道建立成功')
    } else {
      console.error('頻道建立失敗:', result.error)
    }
  } catch (error) {
    console.error('頻道建立失敗:', error)
  } finally {
    creating.value = false
  }
}

const cancelCreate = () => {
  newChannel.name = ''
  newChannel.description = ''
  newChannel.isPrivate = false
  showCreateForm.value = false
}

// 組件方法
const switchChannel = async (channel) => {
  if (channel.id === channelStore.currentChannelId) return
  
  console.log(`切換到頻道: ${channel.name}`)
  const result = await channelStore.switchChannel(channel.id)
  
  if (!result.success) {
    console.error('切換頻道失敗:', result.error)
  }
}

const openChannelSettings = (channel) => {
  channelStore.openChannelSettings(channel)
}

const getChannelMemberCount = (channelId) => {
  const members = channelStore.channelMembers[channelId]
  return members ? members.length : 0
}

const isChannelAdmin = (channelId) => {
  if (!userStore.currentUser) return false
  
  const members = channelStore.channelMembers[channelId] || []
  const member = members.find(m => m.user_id === userStore.currentUser?.id)
  
  return member?.role === 'admin' || member?.role === 'owner'
}

// 載入頻道資料
onMounted(async () => {
  console.log('ChannelSidebar mounted, 載入頻道資料...')
  await channelStore.fetchChannels()
  
  // 載入當前頻道的成員
  if (channelStore.currentChannelId) {
    await channelStore.fetchChannelMembers(channelStore.currentChannelId)
  }
})
</script>

<style scoped>
/* 自訂滾動條樣式 */
.overflow-y-auto::-webkit-scrollbar {
  width: 4px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 2px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}

/* 頻道項目的懸停效果 */
.group:hover .opacity-0 {
  opacity: 1;
}
</style>