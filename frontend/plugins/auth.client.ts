export default defineNuxtPlugin(() => {
  const userStore = useUserStore()
  
  // 在客戶端自動初始化認證狀態
  userStore.initAuth()
})