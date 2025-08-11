<template>
  <aside class="w-64 bg-gray-50 border-r border-gray-200 flex flex-col h-full">
    <!-- 頻道側邊欄標題 -->
    <div class="p-4 border-b border-gray-200 bg-white">
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-semibold text-gray-900">頻道列表</h2>
        <UButton
          @click="channelStore.openChannelCreator()"
          size="xs"
          variant="ghost"
          icon="i-heroicons-plus"
          title="建立新頻道"
        />
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
import { useChannelStore } from '~/stores/channel'
import { useUserStore } from '~/stores/user'

const channelStore = useChannelStore()
const userStore = useUserStore()

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