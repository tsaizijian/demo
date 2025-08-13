import { ref, readonly, onMounted, onUnmounted } from 'vue'

/**
 * 用於實時更新時間顯示的 composable
 * @param updateInterval 更新間隔（毫秒），默認 30 秒
 */
export const useTimeUpdate = (updateInterval: number = 30000) => {
  const updateTrigger = ref(0)
  let intervalId: NodeJS.Timeout | null = null
  
  const startUpdating = () => {
    if (intervalId) return
    
    intervalId = setInterval(() => {
      updateTrigger.value++
    }, updateInterval)
  }
  
  const stopUpdating = () => {
    if (intervalId) {
      clearInterval(intervalId)
      intervalId = null
    }
  }
  
  onMounted(() => {
    startUpdating()
  })
  
  onUnmounted(() => {
    stopUpdating()
  })
  
  return {
    updateTrigger: readonly(updateTrigger),
    startUpdating,
    stopUpdating
  }
}