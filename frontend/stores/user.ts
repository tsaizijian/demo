import { defineStore } from 'pinia'
import { useSocket } from '~/composables/useSocket'

interface User {
  id: number
  username: string
  first_name: string
  last_name: string
  email: string
}

interface UserProfile {
  id?: number
  user_id?: number
  username: string
  display_name?: string
  avatar_url?: string
  bio?: string
  is_online: boolean
  last_seen?: string
  message_count: number
  join_date?: string
  timezone: string
  language: string
}

interface LoginCredentials {
  username: string
  password: string
  provider: string
}

export const useUserStore = defineStore('user', {
  state: () => ({
    currentUser: null as User | null,
    userProfile: null as UserProfile | null,
    accessToken: null as string | null,
    isAuthenticated: false,
    loading: false,
    error: null as string | null
  }),

  getters: {
    displayName: (state): string => {
      if (state.userProfile?.display_name) {
        return state.userProfile.display_name
      }
      if (state.currentUser) {
        return `${state.currentUser.first_name} ${state.currentUser.last_name}`.trim()
      }
      return state.userProfile?.username || '訪客'
    },
    
    token: (state): string | null => {
      return state.accessToken
    }
  },

  actions: {
    async login(credentials: LoginCredentials) {
      this.loading = true
      this.error = null
      
      try {
        const config = useRuntimeConfig()
        
        const response = await $fetch(`${config.public.apiBase}/api/v1/auth/login`, {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json'
          },
          body: credentials
        })

        if (response.access_token) {
          this.accessToken = response.access_token
          this.isAuthenticated = true
          
          // 儲存到localStorage
          if (process.client) {
            localStorage.setItem('access_token', response.access_token)
          }
          
          // 獲取使用者資料
          await this.fetchUserProfile()
          
          return { success: true }
        } else {
          throw new Error('登入失敗')
        }
      } catch (error: any) {
        this.error = error.data?.message || error.message || '登入失敗'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    async register(userData: {
      username: string
      first_name: string
      last_name: string
      email: string
      password: string
    }) {
      this.loading = true
      this.error = null

      try {
        const config = useRuntimeConfig()
        
        const response = await $fetch(`${config.public.apiBase}/api/v1/register/signup`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: userData
        })

        if (response && response.success) {
          return { success: true, user: response.user }
        } else {
          throw new Error(response?.message || '註冊失敗')
        }
      } catch (error: any) {
        this.error = error.data?.message || error.message || '註冊失敗'
        console.error('註冊錯誤:', error)
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    async checkUsername(username: string) {
      try {
        const config = useRuntimeConfig()
        
        const response = await $fetch(`${config.public.apiBase}/api/v1/register/check-username`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: { username }
        })

        return { available: response.available }
      } catch (error: any) {
        console.error('檢查使用者名稱失敗:', error)
        return { available: true }
      }
    },

    async logout() {
      // 斷開 Socket 連接
      const { disconnect } = useSocket()
      disconnect()
      
      this.currentUser = null
      this.userProfile = null
      this.accessToken = null
      this.isAuthenticated = false
      this.error = null
      
      // 清除localStorage
      if (process.client) {
        localStorage.removeItem('access_token')
      }
      
      // 導向登出頁面
      await navigateTo('/logout')
    },

    async fetchUserProfile() {
      if (!this.accessToken) return
      
      try {
        const config = useRuntimeConfig()
        
        const profile = await $fetch(`${config.public.apiBase}/api/v1/userprofileapi/me`, {
          credentials: 'include',
          headers: {
            'Authorization': `Bearer ${this.accessToken}`,
            'Content-Type': 'application/json'
          }
        })
        
        this.userProfile = profile.result
      } catch (error) {
        console.error('獲取使用者資料失敗:', error)
      }
    },

    async updateProfile(profileData: Partial<UserProfile>) {
      if (!this.accessToken) return
      
      this.loading = true
      this.error = null
      
      try {
        const config = useRuntimeConfig()
        
        const response = await $fetch(`${config.public.apiBase}/api/v1/userprofileapi/update-profile`, {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Authorization': `Bearer ${this.accessToken}`,
            'Content-Type': 'application/json'
          },
          body: profileData
        })
        
        if (response.data) {
          this.userProfile = response.data
        }
        
        return { success: true }
      } catch (error: any) {
        this.error = error.data?.message || '更新失敗'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    async setOnlineStatus(isOnline: boolean) {
      if (!this.accessToken) return
      
      try {
        const config = useRuntimeConfig()
        
        await $fetch(`${config.public.apiBase}/api/v1/userprofileapi/set-online-status`, {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Authorization': `Bearer ${this.accessToken}`,
            'Content-Type': 'application/json'
          },
          body: { is_online: isOnline }
        })
        
        if (this.userProfile) {
          this.userProfile.is_online = isOnline
        }
      } catch (error) {
        console.error('設定線上狀態失敗:', error)
      }
    },

    // 檢查登入狀態
    initAuth() {
      if (process.client) {
        const token = localStorage.getItem('access_token')
        if (token) {
          // 檢查token是否過期
          try {
            const payload = JSON.parse(atob(token.split('.')[1]))
            const currentTime = Math.floor(Date.now() / 1000)
            
            if (payload.exp && payload.exp > currentTime) {
              // Token未過期
              this.accessToken = token
              this.isAuthenticated = true
              this.fetchUserProfile()
            } else {
              // Token已過期，清除並導向登入
              console.warn('Token已過期，請重新登入')
              this.logout()
            }
          } catch (error) {
            // Token格式錯誤，清除
            console.error('Token格式錯誤:', error)
            this.logout()
          }
        }
      }
    }
  }
})