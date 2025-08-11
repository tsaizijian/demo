import { defineStore } from 'pinia'
import { useUserStore } from './user'

interface ChatMessage {
  id: number
  content: string
  sender_id: number
  sender_name: string
  sender_first_name: string
  sender_last_name: string
  message_type: string
  attachment_path?: string
  is_deleted: boolean
  reply_to_id?: number
  channel_id: number
  created_on: string
  changed_on?: string
}

interface OnlineUser {
  id: number
  user_id: number
  username: string
  display_name: string
  is_online: boolean
  last_seen?: string
}

export const useChatStore = defineStore('chat', {
  state: () => ({
    messages: [] as ChatMessage[],
    onlineUsers: [] as OnlineUser[],
    currentChannel: 1,
    loading: false,
    error: null as string | null,
    isTyping: false,
    typingUsers: [] as string[],
    isConnected: false,
    systemMessages: [] as string[]
  }),

  getters: {
    sortedMessages: (state) => {
      return [...state.messages].sort((a, b) => 
        new Date(a.created_on).getTime() - new Date(b.created_on).getTime()
      )
    },
    
    onlineUserCount: (state) => state.onlineUsers.length
  },

  actions: {
    async fetchMessages(limit = 50) {
      const userStore = useUserStore()
      if (!userStore.accessToken) return

      this.loading = true
      this.error = null

      try {
        const config = useRuntimeConfig()
        
        const response = await $fetch(`${config.public.apiBase}/api/v1/chatmessageapi/recent/${limit}`, {
          headers: {
            'Authorization': `Bearer ${userStore.accessToken}`,
            'Content-Type': 'application/json'
          }
        })

        this.messages = response.result || []
      } catch (error: any) {
        this.error = error.data?.message || '獲取訊息失敗'
        console.error('獲取訊息失敗:', error)
      } finally {
        this.loading = false
      }
    },

    async sendMessage(content: string, replyToId?: number) {
      const userStore = useUserStore()
      if (!userStore.accessToken) return

      try {
        const config = useRuntimeConfig()
        
        const response = await $fetch(`${config.public.apiBase}/api/v1/chatmessageapi/send`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${userStore.accessToken}`,
            'Content-Type': 'application/json'
          },
          body: {
            content,
            message_type: 'text',
            reply_to_id: replyToId,
            channel_id: this.currentChannel
          }
        })

        // 重新獲取訊息列表
        await this.fetchMessages()
        
        return { success: true }
      } catch (error: any) {
        this.error = error.data?.message || '發送訊息失敗'
        console.error('發送訊息失敗:', error)
        return { success: false, error: this.error }
      }
    },

    async deleteMessage(messageId: number) {
      const userStore = useUserStore()
      if (!userStore.accessToken) return

      try {
        const config = useRuntimeConfig()
        
        await $fetch(`${config.public.apiBase}/api/v1/chatmessageapi/delete/${messageId}`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${userStore.accessToken}`,
            'Content-Type': 'application/json'
          }
        })

        // 重新獲取訊息列表
        await this.fetchMessages()
        
        return { success: true }
      } catch (error: any) {
        this.error = error.data?.message || '刪除訊息失敗'
        console.error('刪除訊息失敗:', error)
        return { success: false, error: this.error }
      }
    },

    async fetchOnlineUsers() {
      const userStore = useUserStore()
      if (!userStore.accessToken) return

      try {
        const config = useRuntimeConfig()
        
        const response = await $fetch(`${config.public.apiBase}/api/v1/userprofileapi/online-users`, {
          headers: {
            'Authorization': `Bearer ${userStore.accessToken}`,
            'Content-Type': 'application/json'
          }
        })

        this.onlineUsers = response.result || []
      } catch (error: any) {
        console.error('獲取線上使用者失敗:', error)
      }
    },

    addMessage(message: ChatMessage) {
      // 避免重複訊息
      const exists = this.messages.find(m => m.id === message.id)
      if (!exists) {
        this.messages.push(message)
      }
    },

    updateMessage(messageId: number, updates: Partial<ChatMessage>) {
      const index = this.messages.findIndex(m => m.id === messageId)
      if (index !== -1) {
        this.messages[index] = { ...this.messages[index], ...updates }
      }
    },

    removeMessage(messageId: number) {
      const index = this.messages.findIndex(m => m.id === messageId)
      if (index !== -1) {
        this.messages.splice(index, 1)
      }
    },

    clearMessages() {
      this.messages = []
    },

    setTyping(isTyping: boolean) {
      this.isTyping = isTyping
    },

    addTypingUser(username: string) {
      if (!this.typingUsers.includes(username)) {
        this.typingUsers.push(username)
      }
    },

    removeTypingUser(username: string) {
      const index = this.typingUsers.indexOf(username)
      if (index !== -1) {
        this.typingUsers.splice(index, 1)
      }
    },

    setConnectionStatus(connected: boolean) {
      this.isConnected = connected
    },

    setOnlineUsers(users: OnlineUser[]) {
      this.onlineUsers = users
    },

    addSystemMessage(message: string) {
      this.systemMessages.push(message)
      // 限制系統訊息數量
      if (this.systemMessages.length > 50) {
        this.systemMessages = this.systemMessages.slice(-50)
      }
    },

    setError(error: string | null) {
      this.error = error
    }
  }
})