import { defineStore } from 'pinia'
import { useSocket } from '~/composables/useSocket'
import { useUserStore } from './user'

interface Channel {
  id: number
  name: string
  description?: string
  is_private: boolean
  is_active: boolean
  creator_id: number
  creator_name?: string
  max_members: number
  member_count?: number
  created_on: string
}

interface ChannelMessage {
  id: number
  content: string
  sender_id: number
  sender_name: string
  message_type: string
  channel_id: number
  created_on: string
}

interface ChannelMember {
  id: number
  channel_id: number
  user_id: number
  username: string
  display_name: string
  role: 'owner' | 'admin' | 'member'
  joined_at: string
}

export const useChannelStore = defineStore('channel', {
  state: () => ({
    // 頻道相關
    channels: [] as Channel[],
    currentChannel: null as Channel | null,
    currentChannelId: 1, // 預設頻道
    
    // 頻道訊息
    channelMessages: {} as Record<number, ChannelMessage[]>,
    
    // 頻道成員
    channelMembers: {} as Record<number, ChannelMember[]>,
    
    // UI 狀態
    loading: false,
    error: null as string | null,
    
    // 頻道管理 UI
    showChannelCreator: false,
    showChannelSettings: false,
    selectedChannelForSettings: null as Channel | null,
  }),

  getters: {
    // 當前頻道訊息
    currentChannelMessages: (state): ChannelMessage[] => {
      return state.channelMessages[state.currentChannelId] || []
    },
    
    // 當前頻道成員
    currentChannelMembers: (state): ChannelMember[] => {
      return state.channelMembers[state.currentChannelId] || []
    },
    
    // 公開頻道
    publicChannels: (state): Channel[] => {
      return state.channels.filter(channel => !channel.is_private && channel.is_active)
    },
    
    // 私人頻道
    privateChannels: (state): Channel[] => {
      return state.channels.filter(channel => channel.is_private && channel.is_active)
    },
    
    // 是否為頻道管理員
    isChannelAdmin: (state) => {
      const userStore = useUserStore()
      if (!userStore.currentUser) return false
      
      const member = state.currentChannelMembers.find(
        m => m.user_id === userStore.currentUser?.id
      )
      return member?.role === 'admin' || member?.role === 'owner'
    }
  },

  actions: {
    // 獲取所有頻道
    async fetchChannels() {
      this.loading = true
      this.error = null
      
      try {
        const config = useRuntimeConfig()
        const userStore = useUserStore()
        
        // 同時獲取公開和私人頻道
        const [publicResponse, privateResponse] = await Promise.all([
          $fetch(`${config.public.apiBase}/api/v1/chatchannelapi/public-channels`, {
            headers: {
              'Authorization': `Bearer ${userStore.token}`,
              'Content-Type': 'application/json'
            }
          }),
          $fetch(`${config.public.apiBase}/api/v1/chatchannelapi/my-channels`, {
            headers: {
              'Authorization': `Bearer ${userStore.token}`,
              'Content-Type': 'application/json'
            }
          })
        ])
        
        if (publicResponse && publicResponse.result) {
          let allChannels = [...publicResponse.result]
          
          // 合併私人頻道（避免重複）
          if (privateResponse && privateResponse.result) {
            const publicChannelIds = new Set(publicResponse.result.map(c => c.id))
            const privateChannels = privateResponse.result.filter(c => !publicChannelIds.has(c.id))
            allChannels = [...allChannels, ...privateChannels]
          }
          
          this.channels = allChannels
          
          // 如果沒有當前頻道，設定為第一個頻道
          if (!this.currentChannel && this.channels.length > 0) {
            this.currentChannel = this.channels[0]
            this.currentChannelId = this.channels[0].id
          }
          
          return { success: true, data: response.result }
        }
        
        return { success: false, error: 'No channels found' }
      } catch (error: any) {
        console.error('獲取頻道失敗:', error)
        this.error = error.message || '獲取頻道失敗'
        return { success: false, error: error.message }
      } finally {
        this.loading = false
      }
    },

    // 切換頻道
    async switchChannel(channelId: number) {
      const channel = this.channels.find(c => c.id === channelId)
      if (!channel) {
        this.error = '頻道不存在'
        return { success: false, error: '頻道不存在' }
      }
      
      this.currentChannel = channel
      this.currentChannelId = channelId
      
      // 載入該頻道的訊息
      await this.fetchChannelMessages(channelId)
      
      // 載入該頻道的成員
      await this.fetchChannelMembers(channelId)
      
      // 通知 Socket.IO 切換房間
      const socketStore = useSocket()
      if (socketStore.socket.value) {
        socketStore.socket.value.emit('join_channel', { channel_id: channelId })
      }
      
      return { success: true }
    },

    // 獲取頻道訊息
    async fetchChannelMessages(channelId: number) {
      try {
        const config = useRuntimeConfig()
        const userStore = useUserStore()
        
        const response = await $fetch(`${config.public.apiBase}/api/v1/chatmessageapi/recent/50?channel_id=${channelId}`, {
          headers: {
            'Authorization': `Bearer ${userStore.token}`,
            'Content-Type': 'application/json'
          }
        })
        
        if (response && response.result) {
          this.channelMessages[channelId] = response.result
          return { success: true, data: response.result }
        }
        
        return { success: false, error: 'No messages found' }
      } catch (error: any) {
        console.error('獲取頻道訊息失敗:', error)
        return { success: false, error: error.message }
      }
    },

    // 獲取頻道成員
    async fetchChannelMembers(channelId: number) {
      try {
        const config = useRuntimeConfig()
        const userStore = useUserStore()
        
        // 暫時使用線上使用者 API，之後可以改為頻道專用 API
        const response = await $fetch(`${config.public.apiBase}/api/v1/userprofileapi/online-users`, {
          headers: {
            'Authorization': `Bearer ${userStore.token}`,
            'Content-Type': 'application/json'
          }
        })
        
        if (response && response.result) {
          // 模擬頻道成員結構
          const members = response.result.map((user: any) => ({
            id: user.id,
            channel_id: channelId,
            user_id: user.user_id,
            username: user.username,
            display_name: user.display_name || user.username,
            role: user.user_id === 1 ? 'owner' : 'member', // 暫時邏輯
            joined_at: new Date().toISOString()
          }))
          
          this.channelMembers[channelId] = members
          return { success: true, data: members }
        }
        
        return { success: false, error: 'No members found' }
      } catch (error: any) {
        console.error('獲取頻道成員失敗:', error)
        return { success: false, error: error.message }
      }
    },

    // 建立新頻道
    async createChannel(channelData: {
      name: string
      description?: string
      is_private?: boolean
      max_members?: number
    }) {
      this.loading = true
      this.error = null
      
      try {
        const config = useRuntimeConfig()
        const userStore = useUserStore()
        
        // 調試：印出 token 
        console.log('Creating channel with token:', userStore.token)
        
        const response = await $fetch(`${config.public.apiBase}/api/v1/chatchannelapi/create-channel`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${userStore.token}`,
            'Content-Type': 'application/json'
          },
          body: {
            name: channelData.name,
            description: channelData.description || '',
            is_private: channelData.is_private || false,
            max_members: channelData.max_members || 100
          }
        })
        
        if (response) {
          // 重新獲取頻道列表
          await this.fetchChannels()
          
          // 關閉建立頻道對話框
          this.showChannelCreator = false
          
          return { success: true, data: response }
        }
        
        return { success: false, error: 'Failed to create channel' }
      } catch (error: any) {
        console.error('建立頻道失敗:', error)
        this.error = error.message || '建立頻道失敗'
        return { success: false, error: error.message }
      } finally {
        this.loading = false
      }
    },

    // 更新頻道設定
    async updateChannel(channelId: number, updates: Partial<Channel>) {
      this.loading = true
      this.error = null
      
      try {
        const config = useRuntimeConfig()
        const userStore = useUserStore()
        
        const response = await $fetch(`${config.public.apiBase}/api/v1/chatchannelapi/${channelId}`, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${userStore.token}`,
            'Content-Type': 'application/json'
          },
          body: updates
        })
        
        if (response) {
          // 更新本地頻道資料
          const channelIndex = this.channels.findIndex(c => c.id === channelId)
          if (channelIndex !== -1) {
            this.channels[channelIndex] = { ...this.channels[channelIndex], ...updates }
          }
          
          // 如果是當前頻道，也更新當前頻道
          if (this.currentChannelId === channelId) {
            this.currentChannel = this.channels[channelIndex]
          }
          
          return { success: true, data: response }
        }
        
        return { success: false, error: 'Failed to update channel' }
      } catch (error: any) {
        console.error('更新頻道失敗:', error)
        this.error = error.message || '更新頻道失敗'
        return { success: false, error: error.message }
      } finally {
        this.loading = false
      }
    },

    // 添加訊息到頻道
    addMessageToChannel(channelId: number, message: ChannelMessage) {
      if (!this.channelMessages[channelId]) {
        this.channelMessages[channelId] = []
      }
      this.channelMessages[channelId].push(message)
    },

    // 從頻道移除訊息
    removeMessageFromChannel(channelId: number, messageId: number) {
      if (this.channelMessages[channelId]) {
        this.channelMessages[channelId] = this.channelMessages[channelId].filter(
          m => m.id !== messageId
        )
      }
    },

    // UI 控制方法
    openChannelCreator() {
      this.showChannelCreator = true
    },

    closeChannelCreator() {
      this.showChannelCreator = false
    },

    openChannelSettings(channel: Channel) {
      this.selectedChannelForSettings = channel
      this.showChannelSettings = true
    },

    closeChannelSettings() {
      this.showChannelSettings = false
      this.selectedChannelForSettings = null
    },

    // 清除錯誤
    clearError() {
      this.error = null
    },

    // 重置狀態
    reset() {
      this.channels = []
      this.currentChannel = null
      this.currentChannelId = 1
      this.channelMessages = {}
      this.channelMembers = {}
      this.loading = false
      this.error = null
      this.showChannelCreator = false
      this.showChannelSettings = false
      this.selectedChannelForSettings = null
    }
  }
})