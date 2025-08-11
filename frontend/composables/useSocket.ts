import { io, Socket } from 'socket.io-client'
import { useUserStore } from '~/stores/user'
import { useChatStore } from '~/stores/chat'

// 創建全局響應式socket引用
const socket = ref<Socket | null>(null)

export const useSocket = () => {
  const config = useRuntimeConfig()
  const userStore = useUserStore()
  const chatStore = useChatStore()

  const connect = () => {
    if (socket.value?.connected) {
      return socket.value
    }

    // 確保有認證token
    if (!userStore.token) {
      console.warn('無認證token，無法建立Socket連接')
      return null
    }

    console.log('正在建立Socket連接...')
    
    socket.value = io(config.public.apiBase, {
      transports: ['websocket', 'polling'],
      autoConnect: true,
      withCredentials: true,
      auth: {
        token: userStore.token
      }
    })

    // 連接事件
    socket.value.on('connect', () => {
      console.log('Socket已連接:', socket.value?.id)
      chatStore.setConnectionStatus(true)
    })

    socket.value.on('disconnect', (reason) => {
      console.log('Socket已斷線:', reason)
      chatStore.setConnectionStatus(false)
    })

    socket.value.on('connect_error', (error) => {
      console.error('Socket連接錯誤:', error)
      chatStore.setConnectionStatus(false)
      
      // 如果是認證錯誤，可能是token過期，嘗試重新登入
      if (error.message && error.message.includes('rejected')) {
        console.warn('連接被拒絕，可能是token過期，請重新登入')
        // 清除過期token
        userStore.logout()
      }
    })

    // 訊息事件
    socket.value.on('new_message', (messageData) => {
      console.log('收到新訊息:', messageData)
      chatStore.addMessage(messageData)
    })

    socket.value.on('message_deleted', (data) => {
      console.log('訊息已刪除:', data.message_id)
      chatStore.removeMessage(data.message_id)
    })

    // 使用者事件
    socket.value.on('user_joined', (data) => {
      console.log('使用者加入:', data.display_name)
      chatStore.addSystemMessage(`${data.display_name} 加入聊天室`)
    })

    socket.value.on('user_left', (data) => {
      console.log('使用者離開:', data.display_name)
      chatStore.addSystemMessage(`${data.display_name} 離開聊天室`)
    })

    socket.value.on('online_users', (users) => {
      console.log('更新線上使用者:', users.length, '人')
      chatStore.setOnlineUsers(users)
    })

    socket.value.on('user_typing', (data) => {
      if (data.is_typing) {
        chatStore.addTypingUser(data.display_name)
      } else {
        chatStore.removeTypingUser(data.display_name)
      }
    })

    // 錯誤處理
    socket.value.on('error', (error) => {
      console.error('Socket錯誤:', error)
      chatStore.setError(error.message || '連接發生錯誤')
    })

    return socket.value
  }

  const disconnect = () => {
    if (socket.value) {
      console.log('正在斷開Socket連接...')
      socket.value.disconnect()
      socket.value = null
      chatStore.setConnectionStatus(false)
    }
  }

  const sendMessage = (content: string) => {
    if (!socket.value?.connected) {
      console.warn('Socket未連接，無法發送訊息')
      return false
    }

    socket.value.emit('send_message', { content })
    return true
  }

  const deleteMessage = (messageId: number) => {
    if (!socket.value?.connected) {
      console.warn('Socket未連接，無法刪除訊息')
      return false
    }

    socket.value.emit('delete_message', { message_id: messageId })
    return true
  }

  const setTyping = (isTyping: boolean) => {
    if (!socket.value?.connected) {
      return
    }

    socket.value.emit('typing', { is_typing: isTyping })
  }

  const joinRoom = (room: string = 'general') => {
    if (!socket.value?.connected) {
      return
    }

    socket.value.emit('join_room', { room })
  }

  const leaveRoom = (room: string = 'general') => {
    if (!socket.value?.connected) {
      return
    }

    socket.value.emit('leave_room', { room })
  }

  const getOnlineUsers = () => {
    if (!socket.value?.connected) {
      return
    }

    socket.value.emit('get_online_users')
  }

  const isConnected = () => {
    return socket.value?.connected || false
  }

  return {
    connect,
    disconnect,
    sendMessage,
    deleteMessage,
    setTyping,
    joinRoom,
    leaveRoom,
    getOnlineUsers,
    isConnected,
    socket
  }
}