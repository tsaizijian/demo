<script setup>
import { useUserStore } from "~/stores/user"

const userStore = useUserStore()

// 初始化認證狀態
onMounted(() => {
  userStore.initAuth()
})

// 主題切換功能
const isDark = ref(false)

const toggleDarkMode = () => {
  isDark.value = !isDark.value
  if (process.client) {
    document.documentElement.classList.toggle('dark', isDark.value)
    localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
  }
}

// 初始化主題
onMounted(() => {
  if (process.client) {
    const savedTheme = localStorage.getItem('theme')
    isDark.value = savedTheme === 'dark'
    document.documentElement.classList.toggle('dark', isDark.value)
  }
})

async function logout() {
  await userStore.logout()
}

// 導航項目
const navItems = computed(() => {
  if (!userStore.isAuthenticated) {
    return [
      { label: "登入", route: "/login" },
      { label: "註冊", route: "/register" }
    ]
  } else {
    return [
      { label: "聊天室", route: "/chatroom" },
      { label: "個人資料", route: "/profile" },
      { label: "登出", action: logout }
    ]
  }
})
</script>

<template>
  <div class="layout-container">
    <!-- 導航欄 -->
    <header class="header">
      <div class="header-content">
        <div class="header-inner">
          <!-- Logo -->
          <NuxtLink to="/" class="logo">
            <div class="logo-icon">
              <span class="logo-symbol">💬</span>
            </div>
            <span class="logo-text">
              聊天室
            </span>
          </NuxtLink>

          <!-- 桌面導航 -->
          <nav class="desktop-nav">
            <template v-for="item in navItems" :key="item.label">
              <NuxtLink 
                v-if="item.route" 
                :to="item.route"
                class="nav-item"
              >
                {{ item.label }}
              </NuxtLink>
              <button 
                v-else 
                @click="item.action"
                class="nav-button"
              >
                {{ item.label }}
              </button>
            </template>

            <!-- 主題切換 -->
            <button 
              @click="toggleDarkMode"
              class="theme-toggle"
              :title="isDark ? '切換到淺色模式' : '切換到深色模式'"
            >
              {{ isDark ? '☀️' : '🌙' }}
            </button>

            <!-- 用戶頭像 -->
            <div v-if="userStore.isAuthenticated" class="user-info">
              <div class="user-avatar">
                {{ userStore.displayName?.charAt(0).toUpperCase() || 'U' }}
              </div>
              <span class="user-name">
                {{ userStore.displayName || '使用者' }}
              </span>
            </div>
          </nav>

          <!-- 移動端菜單按鈕 -->
          <button class="mobile-menu-btn">
            ☰
          </button>
        </div>
      </div>
    </header>

    <!-- 主要內容 -->
    <main class="main-content">
      <NuxtPage />
    </main>

    <!-- 頁腳 -->
    <footer class="footer">
      <div class="footer-content">
        <div class="footer-inner">
          <div class="copyright">
            © 2025 聊天室系統 版權所有
          </div>
          <div class="footer-links">
            <a href="#" class="footer-link">隱私政策</a>
            <a href="#" class="footer-link">服務條款</a>
            <a href="#" class="footer-link">聯絡我們</a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.layout-container {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--gradient-from), var(--gradient-to));
  display: flex;
  flex-direction: column;
}

.header {
  backdrop-filter: blur(10px);
  background: var(--menubar-bg);
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: 50;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 4rem;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
  transition: opacity 0.3s ease;
}

.logo:hover {
  opacity: 0.8;
}

.logo-icon {
  width: 2.5rem;
  height: 2.5rem;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-lg);
}

.logo-symbol {
  color: white;
  font-size: 1.25rem;
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--logo-text);
}

.desktop-nav {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.nav-item, .nav-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 0.75rem;
  font-weight: 500;
  color: var(--text-color);
  text-decoration: none;
  transition: all 0.2s ease;
  background: none;
  border: none;
  cursor: pointer;
  font-family: inherit;
  font-size: inherit;
}

.nav-item:hover, .nav-button:hover {
  background: var(--hover-bg);
  transform: translateY(-1px);
}

.nav-button:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #DC2626;
}

.nav-item.router-link-active {
  background: var(--hover-bg);
  color: var(--primary-color);
}

.theme-toggle {
  padding: 0.5rem;
  border-radius: 0.75rem;
  background: none;
  border: none;
  cursor: pointer;
  transition: background-color 0.3s ease;
  font-size: 1.25rem;
}

.theme-toggle:hover {
  background: var(--hover-bg);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 2rem;
  height: 2rem;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  box-shadow: var(--shadow-md);
  font-size: 0.875rem;
}

.user-name {
  font-weight: 500;
  color: var(--text-color);
}

.mobile-menu-btn {
  display: none;
  padding: 0.5rem;
  border-radius: 0.75rem;
  background: none;
  border: none;
  cursor: pointer;
  transition: background-color 0.3s ease;
  color: var(--text-color);
  font-size: 1.25rem;
}

.mobile-menu-btn:hover {
  background: var(--hover-bg);
}

.main-content {
  flex: 1;
}

.footer {
  backdrop-filter: blur(10px);
  background: var(--footer-bg);
  border-top: 1px solid var(--border-color);
  padding: 1.5rem 0;
  margin-top: auto;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.footer-inner {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.copyright {
  color: #6B7280;
  font-size: 0.875rem;
}

.footer-links {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.footer-link {
  color: #6B7280;
  text-decoration: none;
  transition: color 0.3s ease;
  font-size: 0.875rem;
}

.footer-link:hover {
  color: var(--primary-color);
}

/* 響應式設計 */
@media (min-width: 768px) {
  .desktop-nav {
    display: flex;
  }
  
  .footer-inner {
    flex-direction: row;
  }
  
  .user-name {
    display: block;
  }
}

@media (max-width: 767px) {
  .desktop-nav {
    display: none;
  }
  
  .mobile-menu-btn {
    display: block;
  }
  
  .user-name {
    display: none;
  }
  
  .logo-text {
    font-size: 1rem;
  }
}
</style>