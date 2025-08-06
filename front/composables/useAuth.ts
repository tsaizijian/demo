import { ref, computed } from 'vue'

export interface User {
  id: number
  username: string
  first_name: string
  last_name: string
  email: string
  roles?: string[]
}

export interface LoginData {
  username: string
  password: string
  rememberMe?: boolean
}

export interface RegisterData {
  username: string
  email: string
  first_name: string
  last_name: string
  password: string
  recaptcha_response: string
}

// 使用 globalThis 確保狀態在所有實例間共享
const globalState = globalThis as any
if (!globalState._authState) {
  globalState._authState = {
    user: ref<User | null>(null),
    isAuthenticated: ref(false),
    isLoading: ref(false),
    error: ref<string>('')
  }
}

export const useAuth = () => {
  const config = useRuntimeConfig()
  const { $api } = useNuxtApp()
  
  // 使用全局共享狀態
  const user = globalState._authState.user
  const isAuthenticated = globalState._authState.isAuthenticated
  const isLoading = globalState._authState.isLoading
  const error = globalState._authState.error
  
  /**
   * 檢查認證狀態
   */
  const checkAuth = async () => {
    try {
      // 如果本地已有用戶資訊，直接返回 true
      if (user.value && isAuthenticated.value) {
        return true
      }
      
      const response = await $api.get(config.public.apiUrls.auth.check)
      
      if (response && response.authenticated) {
        isAuthenticated.value = true
        // 如果已認證但沒有用戶資訊，獲取用戶資訊
        if (!user.value) {
          await getCurrentUser()
        }
      } else {
        isAuthenticated.value = false
        user.value = null
      }
      
      return isAuthenticated.value
      
    } catch (err: any) {
      console.error('檢查認證狀態失敗:', err)
      isAuthenticated.value = false
      user.value = null
      return false
    }
  }
  
  /**
   * 獲取當前用戶資訊
   */
  const getCurrentUser = async () => {
    try {
      const response = await $api.get(config.public.apiUrls.auth.me)
      
      if (response && response.success && response.user) {
        user.value = response.user
        isAuthenticated.value = true
        return response.user
      }
      
    } catch (err: any) {
      console.error('獲取用戶資訊失敗:', err)
      error.value = err.message || '獲取用戶資訊失敗'
      
      // 如果獲取用戶資訊失敗，可能是token過期
      isAuthenticated.value = false
      user.value = null
    }
  }
  
  /**
   * 用戶登入
   */
  const login = async (loginData: LoginData) => {
    isLoading.value = true
    error.value = ''
    
    try {
      const response = await $api.post(config.public.apiUrls.auth.login, {
        username: loginData.username,
        password: loginData.password
      })
      
      if (response && response.success) {
        user.value = response.user
        isAuthenticated.value = true
        
        console.log('用戶登入成功，設置狀態:', {
          user: response.user,
          isAuthenticated: isAuthenticated.value
        })
        
        return {
          success: true,
          user: response.user,
          message: response.message || '登入成功'
        }
      } else {
        error.value = response.message || '登入失敗'
        return {
          success: false,
          message: error.value
        }
      }
      
    } catch (err: any) {
      console.error('登入失敗:', err)
      error.value = err.message || '登入失敗，請稍後再試'
      
      return {
        success: false,
        message: error.value
      }
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * 用戶登出
   */
  const logout = async () => {
    isLoading.value = true
    error.value = ''
    
    try {
      await $api.post(config.public.apiUrls.auth.logout)
      
      // 清理本地狀態
      user.value = null
      isAuthenticated.value = false
      
      return {
        success: true,
        message: '登出成功'
      }
      
    } catch (err: any) {
      console.error('登出失敗:', err)
      error.value = err.message || '登出失敗'
      
      // 即使API調用失敗，也清理本地狀態
      user.value = null
      isAuthenticated.value = false
      
      return {
        success: false,
        message: error.value
      }
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * 用戶註冊
   */
  const register = async (registerData: RegisterData) => {
    isLoading.value = true
    error.value = ''
    
    try {
      const response = await $api.post(config.public.apiUrls.auth.register, registerData)
      
      if (response && response.success) {
        return {
          success: true,
          data: response.data,
          message: response.message || '註冊成功'
        }
      } else {
        error.value = response.message || '註冊失敗'
        return {
          success: false,
          message: error.value
        }
      }
      
    } catch (err: any) {
      console.error('註冊失敗:', err)
      error.value = err.message || '註冊失敗，請稍後再試'
      
      return {
        success: false,
        message: error.value
      }
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * 檢查用戶名是否可用
   */
  const checkUsername = async (username: string) => {
    try {
      const response = await $api.post(config.public.apiUrls.auth.checkUsername, {
        username
      })
      
      return {
        success: response.success || false,
        available: response.available || false,
        message: response.message || ''
      }
      
    } catch (err: any) {
      console.error('檢查用戶名失敗:', err)
      return {
        success: false,
        available: false,
        message: err.message || '檢查失敗'
      }
    }
  }
  
  /**
   * 檢查郵箱是否可用
   */
  const checkEmail = async (email: string) => {
    try {
      const response = await $api.post(config.public.apiUrls.auth.checkEmail, {
        email
      })
      
      return {
        success: response.success || false,
        available: response.available || false,
        message: response.message || ''
      }
      
    } catch (err: any) {
      console.error('檢查郵箱失敗:', err)
      return {
        success: false,
        available: false,
        message: err.message || '檢查失敗'
      }
    }
  }
  
  /**
   * 清理狀態
   */
  const cleanup = () => {
    user.value = null
    isAuthenticated.value = false
    error.value = ''
  }
  
  // Computed properties
  const userName = computed(() => {
    if (!user.value) return ''
    return user.value.first_name && user.value.last_name 
      ? `${user.value.first_name} ${user.value.last_name}`
      : user.value.username
  })
  
  const userRoles = computed(() => {
    return user.value?.roles || []
  })
  
  const isAdmin = computed(() => {
    return userRoles.value.includes('Admin')
  })
  
  return {
    // 狀態
    user: readonly(user),
    isAuthenticated: readonly(isAuthenticated),
    isLoading: readonly(isLoading),
    error: readonly(error),
    
    // Computed
    userName,
    userRoles,
    isAdmin,
    
    // 方法
    checkAuth,
    getCurrentUser,
    login,
    logout,
    register,
    checkUsername,
    checkEmail,
    cleanup
  }
}

export default useAuth