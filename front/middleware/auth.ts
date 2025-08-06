export default defineNuxtRouteMiddleware(async (to, from) => {
  const { isAuthenticated, checkAuth, user } = useAuth()
  
  console.log('認證中介軟體執行，當前狀態:', {
    hasUser: !!user.value,
    isAuthenticated: isAuthenticated.value,
    user: user.value
  })
  
  // 如果已經有用戶資訊並且已認證，表示已登入
  if (user.value && isAuthenticated.value) {
    console.log('用戶已登入，允許訪問')
    return
  }
  
  // 如果是從登入頁面導向過來的，先等待一下再檢查
  if (from?.path === '/login') {
    console.log('從登入頁面導向，等待狀態更新...')
    await new Promise(resolve => setTimeout(resolve, 100))
    
    // 再次檢查本地狀態
    if (user.value && isAuthenticated.value) {
      console.log('延遲檢查通過，允許訪問')
      return
    }
  }
  
  // 檢查認證狀態
  console.log('執行 API 認證檢查...')
  const isLoggedIn = await checkAuth()
  
  if (!isLoggedIn) {
    console.log('用戶未登入，重定向到登入頁面')
    // 如果用戶未登入，重定向到登入頁面
    return navigateTo('/login')
  }
  
  console.log('認證檢查通過，允許訪問')
})