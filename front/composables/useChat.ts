import { ref, computed, reactive } from 'vue'

export interface ChatRoom {
  id: string | number
  name: string
  description?: string
  members: ChatMember[]
  onlineMembers?: number
  unreadCount?: number
  lastActivity?: Date
  lastMessage?: string
  createdAt?: Date
  updatedAt?: Date
}

export interface ChatMember {
  id: string | number
  name: string
  email?: string
  online?: boolean
  lastSeen?: Date
  role?: 'admin' | 'member'
}

export interface ChatMessage {
  id: string | number
  content: string
  sender: ChatMember
  timestamp: Date
  isOwn: boolean
  status?: 'sending' | 'sent' | 'delivered' | 'failed'
  type?: 'text' | 'image' | 'file'
  metadata?: any
}

export interface CreateRoomData {
  name: string
  description?: string
}

export interface SendMessageData {
  roomId: string | number
  content: string
  type?: 'text' | 'image' | 'file'
  metadata?: any
}

export const useChat = () => {
  const config = useRuntimeConfig()
  const { $api } = useNuxtApp()
  
  // 狀態管理
  const chatRooms = ref<ChatRoom[]>([])
  const currentRoom = ref<ChatRoom | null>(null)
  const messages = ref<ChatMessage[]>([])
  const typingUsers = ref<string[]>([])
  const onlineUsers = ref<ChatMember[]>([])
  
  // 載入狀態
  const isLoadingRooms = ref(false)
  const isLoadingMessages = ref(false)
  const isSendingMessage = ref(false)
  const hasMoreMessages = ref(true)
  
  // 錯誤狀態
  const error = ref<string>('')
  
  /**
   * 載入聊天室列表
   */
  const loadChatRooms = async () => {
    isLoadingRooms.value = true
    error.value = ''
    
    try {
      const response = await $api.get(config.public.apiUrls.chatroom.list)
      
      if (response && response.rooms) {
        // 轉換後端資料格式到前端格式
        const transformedRooms: ChatRoom[] = response.rooms.map((room: any) => ({
          id: room.id,
          name: room.name,
          description: room.description || '',
          members: [], // 成員資訊需要額外API調用
          onlineMembers: 0, // 需要額外計算
          unreadCount: 0, // 需要額外API提供
          lastActivity: new Date(room.created_at),
          lastMessage: '', // 需要額外API提供
          createdAt: new Date(room.created_at)
        }))
        
        chatRooms.value = transformedRooms
      }
      
    } catch (err: any) {
      console.error('載入聊天室列表失敗:', err)
      error.value = err.message || '載入聊天室列表失敗'
      
      // 如果API調用失敗，使用模擬數據作為後備
      const mockRooms: ChatRoom[] = [
        {
          id: 1,
          name: '技術討論',
          description: '分享技術知識、討論程式設計問題',
          members: [
            { id: 1, name: 'Alice', online: true },
            { id: 2, name: 'Bob', online: true },
            { id: 3, name: 'Charlie', online: false },
            { id: 4, name: 'David', online: true }
          ],
          onlineMembers: 3,
          unreadCount: 2,
          lastActivity: new Date('2025-01-15T10:30:00'),
          lastMessage: '有什麼Vue.js的問題可以隨時提出來討論'
        }
      ]
      chatRooms.value = mockRooms
      
    } finally {
      isLoadingRooms.value = false
    }
  }
  
  /**
   * 載入指定聊天室資訊
   */
  const loadChatRoom = async (roomId: string | number) => {
    try {
      // 先從本地列表中查找
      const room = chatRooms.value.find(r => r.id == roomId)
      if (room) {
        currentRoom.value = room
        
        // 載入成員資訊
        try {
          const membersResponse = await $api.get(`${config.public.apiUrls.chatroom.members}${roomId}`)
          if (membersResponse && membersResponse.members) {
            const members: ChatMember[] = membersResponse.members.map((member: any) => ({
              id: member.user_id,
              name: member.username,
              email: member.email,
              online: false, // 需要額外的在線狀態API
              role: member.is_admin ? 'admin' : 'member'
            }))
            
            currentRoom.value.members = members
            currentRoom.value.onlineMembers = members.filter(m => m.online).length
          }
        } catch (membersErr) {
          console.warn('載入成員資訊失敗:', membersErr)
        }
      } else {
        // 如果本地沒有，使用模擬數據
        currentRoom.value = {
          id: roomId,
          name: '技術討論',
          description: '分享技術知識、討論程式設計問題',
          members: [
            { id: 1, name: 'Alice', online: true },
            { id: 2, name: 'Bob', online: true },
            { id: 3, name: 'Charlie', online: false },
            { id: 4, name: 'David', online: true }
          ],
          onlineMembers: 3
        }
      }
      
    } catch (err: any) {
      console.error('載入聊天室資訊失敗:', err)
      error.value = err.message || '載入聊天室資訊失敗'
    }
  }
  
  /**
   * 載入聊天室訊息
   */
  const loadMessages = async (roomId: string | number, page = 1, perPage = 50) => {
    isLoadingMessages.value = true
    error.value = ''
    
    try {
      const response = await $api.get(`${config.public.apiUrls.messages.list}${roomId}`, {
        params: { page, per_page: perPage }
      })
      
      if (response && response.messages) {
        // 轉換後端資料格式到前端格式
        const transformedMessages: ChatMessage[] = response.messages.map((msg: any) => ({
          id: msg.id,
          content: msg.content,
          sender: {
            id: msg.sender.id,
            name: msg.sender.username,
            email: msg.sender.email
          },
          timestamp: new Date(msg.created_at),
          isOwn: false, // 需要比較當前用戶ID
          status: 'delivered',
          type: msg.message_type || 'text'
        }))
        
        if (page === 1) {
          messages.value = transformedMessages.reverse() // 後端是倒序，前端需要正序
        } else {
          messages.value.unshift(...transformedMessages.reverse())
        }
        
        hasMoreMessages.value = response.pagination?.has_next || false
      }
      
    } catch (err: any) {
      console.error('載入訊息失敗:', err)
      error.value = err.message || '載入訊息失敗'
      
      // 如果API調用失敗，使用模擬數據作為後備
      const mockMessages: ChatMessage[] = [
        {
          id: 1,
          content: '大家好！歡迎來到技術討論群組',
          sender: { id: 2, name: 'Bob' },
          timestamp: new Date('2025-01-15T09:00:00'),
          isOwn: false,
          status: 'delivered'
        },
        {
          id: 2,
          content: '謝謝邀請！很高興能在這裡學習',
          sender: { id: 1, name: 'You' },
          timestamp: new Date('2025-01-15T09:05:00'),
          isOwn: true,
          status: 'sent'
        },
        {
          id: 3,
          content: '有什麼Vue.js的問題可以隨時提出來討論',
          sender: { id: 3, name: 'Charlie' },
          timestamp: new Date('2025-01-15T09:10:00'),
          isOwn: false,
          status: 'delivered'
        }
      ]
      
      if (page === 1) {
        messages.value = mockMessages
      } else {
        messages.value.unshift(...mockMessages)
      }
      
      hasMoreMessages.value = false
      
    } finally {
      isLoadingMessages.value = false
    }
  }
  
  /**
   * 發送訊息
   */
  const sendMessage = async (data: SendMessageData) => {
    if (!data.content.trim()) return
    
    isSendingMessage.value = true
    error.value = ''
    
    // 立即添加到本地訊息列表
    const tempMessage: ChatMessage = {
      id: Date.now(),
      content: data.content,
      sender: { id: 1, name: 'You' },
      timestamp: new Date(),
      isOwn: true,
      status: 'sending'
    }
    
    messages.value.push(tempMessage)
    
    try {
      const response = await $api.post(config.public.apiUrls.messages.send, {
        room_id: data.roomId,
        content: data.content,
        message_type: data.type || 'text'
      })
      
      if (response && response.data) {
        // 更新本地訊息為伺服器返回的資料
        const messageIndex = messages.value.findIndex(m => m.id === tempMessage.id)
        if (messageIndex !== -1) {
          messages.value[messageIndex] = {
            id: response.data.id,
            content: response.data.content,
            sender: { id: response.data.sender_id, name: response.data.sender },
            timestamp: new Date(response.data.created_at),
            isOwn: true,
            status: 'sent'
          }
        }
      }
      
    } catch (err: any) {
      console.error('發送訊息失敗:', err)
      error.value = err.message || '發送訊息失敗'
      
      // 標記訊息為失敗
      const messageIndex = messages.value.findIndex(m => m.id === tempMessage.id)
      if (messageIndex !== -1) {
        messages.value[messageIndex].status = 'failed'
      }
    } finally {
      isSendingMessage.value = false
    }
  }
  
  /**
   * 創建聊天室
   */
  const createChatRoom = async (data: CreateRoomData) => {
    isLoadingRooms.value = true
    error.value = ''
    
    try {
      const response = await $api.post(config.public.apiUrls.chatroom.create, {
        name: data.name,
        description: data.description || '',
        is_private: false // 預設為公開聊天室
      })
      
      if (response && response.room) {
        // 轉換後端資料格式到前端格式
        const newRoom: ChatRoom = {
          id: response.room.id,
          name: response.room.name,
          description: response.room.description || '',
          members: [{ id: 1, name: 'You', online: true }],
          onlineMembers: 1,
          unreadCount: 0,
          lastActivity: new Date(response.room.created_at),
          createdAt: new Date(response.room.created_at)
        }
        
        chatRooms.value.unshift(newRoom)
        return newRoom
      }
      
    } catch (err: any) {
      console.error('創建聊天室失敗:', err)
      error.value = err.message || '創建聊天室失敗'
      throw err
    } finally {
      isLoadingRooms.value = false
    }
  }
  
  /**
   * 加入聊天室
   */
  const joinChatRoom = async (roomId: string | number) => {
    try {
      const response = await $api.post(`${config.public.apiUrls.chatroom.join}${roomId}`)
      
      if (response && response.message) {
        console.log(`成功加入聊天室: ${response.message}`)
        
        // 重新載入聊天室列表以更新成員狀態
        await loadChatRooms()
      }
      
    } catch (err: any) {
      console.error('加入聊天室失敗:', err)
      error.value = err.message || '加入聊天室失敗'
      throw err
    }
  }
  
  /**
   * 離開聊天室
   */
  const leaveChatRoom = async (roomId: string | number) => {
    try {
      const response = await $api.post(`${config.public.apiUrls.chatroom.leave}${roomId}`)
      
      if (response && response.message) {
        console.log(`成功離開聊天室: ${response.message}`)
        
        // 從本地列表中移除或更新狀態
        chatRooms.value = chatRooms.value.filter(room => room.id !== roomId)
        
        if (currentRoom.value?.id === roomId) {
          currentRoom.value = null
          messages.value = []
        }
      }
      
    } catch (err: any) {
      console.error('離開聊天室失敗:', err)
      error.value = err.message || '離開聊天室失敗'
      throw err
    }
  }
  
  /**
   * 開始打字
   */
  const startTyping = (roomId: string | number) => {
    // TODO: 發送打字狀態到伺服器
    // $api.post(`${config.public.apiUrls.chatrooms.typing}/${roomId}`, { typing: true })
    console.log(`開始打字: ${roomId}`)
  }
  
  /**
   * 停止打字
   */
  const stopTyping = (roomId: string | number) => {
    // TODO: 發送停止打字狀態到伺服器
    // $api.post(`${config.public.apiUrls.chatrooms.typing}/${roomId}`, { typing: false })
    console.log(`停止打字: ${roomId}`)
  }
  
  /**
   * 標記訊息為已讀
   */
  const markAsRead = async (roomId: string | number) => {
    try {
      // TODO: 替換為實際API調用
      // await $api.post(`${config.public.apiUrls.messages.markRead}/${roomId}`)
      
      // 更新本地未讀計數
      const room = chatRooms.value.find(r => r.id === roomId)
      if (room) {
        room.unreadCount = 0
      }
      
    } catch (err: any) {
      console.error('標記已讀失敗:', err)
    }
  }
  
  /**
   * 清理狀態
   */
  const cleanup = () => {
    chatRooms.value = []
    currentRoom.value = null
    messages.value = []
    typingUsers.value = []
    onlineUsers.value = []
    error.value = ''
  }
  
  // Computed properties  
  const sortedChatRooms = computed(() => {
    return [...chatRooms.value].sort((a, b) => {
      const aTime = a.lastActivity ? new Date(a.lastActivity).getTime() : 0
      const bTime = b.lastActivity ? new Date(b.lastActivity).getTime() : 0
      return bTime - aTime
    })
  })
  
  const totalUnreadCount = computed(() => {
    return chatRooms.value.reduce((total, room) => total + (room.unreadCount || 0), 0)
  })
  
  return {
    // 狀態
    chatRooms: readonly(chatRooms),
    currentRoom: readonly(currentRoom),
    messages: readonly(messages),
    typingUsers: readonly(typingUsers),
    onlineUsers: readonly(onlineUsers),
    
    // 載入狀態
    isLoadingRooms: readonly(isLoadingRooms),
    isLoadingMessages: readonly(isLoadingMessages),
    isSendingMessage: readonly(isSendingMessage),
    hasMoreMessages: readonly(hasMoreMessages),
    
    // 錯誤狀態
    error: readonly(error),
    
    // Computed
    sortedChatRooms,
    totalUnreadCount,
    
    // 方法
    loadChatRooms,
    loadChatRoom,
    loadMessages,
    sendMessage,
    createChatRoom,
    joinChatRoom,
    leaveChatRoom,
    startTyping,
    stopTyping,
    markAsRead,
    cleanup
  }
}

export default useChat