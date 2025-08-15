import { ref } from 'vue'

// 記錄當前被右鍵的訊息ID
const currentMessageId = ref<string | null>(null)

export const useContextMenu = () => {
  const setCurrentMessageId = (messageId: string) => {
    currentMessageId.value = messageId
  }

  const clearCurrentMessageId = () => {
    currentMessageId.value = null
  }

  const getCurrentMessageId = () => {
    return currentMessageId.value
  }

  return {
    currentMessageId,
    setCurrentMessageId,
    clearCurrentMessageId,
    getCurrentMessageId
  }
}