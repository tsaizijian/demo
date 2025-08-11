<template>
  <div class="min-h-screen flex items-center justify-center py-12 px-4">
    <div class="w-full max-w-md">
      <!-- 主卡片 -->
      <div class="glass-card p-8 fade-in">
        <!-- 頭部 -->
        <div class="header">
          <div class="header-icon">
            <span class="icon-symbol">💬</span>
          </div>
          <h2 class="title">
            歡迎回來
          </h2>
          <p class="subtitle">
            登入您的聊天室帳號
          </p>
        </div>

        <!-- 錯誤訊息 -->
        <div 
          v-if="userStore.error" 
          class="error-message"
        >
          <div class="error-content">
            <span class="error-icon">⚠️</span>
            <span class="error-text">{{ userStore.error }}</span>
          </div>
        </div>

        <!-- 登入表單 -->
        <form @submit.prevent="handleLogin" class="space-y-6">
          <!-- 使用者名稱 -->
          <div>
            <label for="username" class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              使用者名稱
            </label>
            <input
              id="username"
              v-model="form.username"
              type="text"
              placeholder="請輸入使用者名稱"
              :disabled="userStore.loading"
              class="floating-input w-full text-gray-900 dark:text-white"
              required
            />
          </div>

          <!-- 密碼 -->
          <div>
            <label for="password" class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              密碼
            </label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              placeholder="請輸入密碼"
              :disabled="userStore.loading"
              class="floating-input w-full text-gray-900 dark:text-white"
              required
            />
          </div>

          <!-- 記住我 -->
          <div class="flex items-center justify-between">
            <label class="flex items-center cursor-pointer">
              <input
                v-model="form.rememberMe"
                type="checkbox"
                :disabled="userStore.loading"
                class="w-4 h-4 text-emerald-600 bg-gray-100 border-gray-300 rounded focus:ring-emerald-500 dark:focus:ring-emerald-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
              />
              <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">記住我</span>
            </label>
            <a href="#" class="text-sm text-emerald-600 hover:text-emerald-500 dark:text-emerald-400 dark:hover:text-emerald-300 font-medium">
              忘記密碼？
            </a>
          </div>

          <!-- 登入按鈕 -->
          <button
            type="submit"
            :disabled="userStore.loading"
            class="login-button"
          >
            <span v-if="userStore.loading" class="loading-icon">🔄</span>
            <span v-else class="login-icon">🚀</span>
            {{ userStore.loading ? "登入中..." : "登入" }}
          </button>
        </form>

        <!-- 分隔線 -->
        <div class="divider">
          <div class="divider-line"></div>
          <span class="divider-text">或者</span>
          <div class="divider-line"></div>
        </div>

        <!-- 註冊連結 -->
        <div class="register-section">
          <p class="register-text">
            還沒有帳號？
            <NuxtLink
              to="/register"
              class="register-link"
            >
              立即註冊
            </NuxtLink>
          </p>
        </div>
      </div>

      <!-- 底部資訊 -->
      <div class="bottom-info">
        <p class="terms-text">
          登入即表示您同意我們的
          <a href="#" class="terms-link">服務條款</a>
          和
          <a href="#" class="terms-link">隱私政策</a>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useUserStore } from "~/stores/user";

// 設定頁面元資訊
definePageMeta({
  layout: false, // 不使用預設layout
  auth: false, // 不需要認證
});

// 響應式資料
const userStore = useUserStore();
const router = useRouter();

const form = reactive({
  username: "",
  password: "",
  rememberMe: false,
});

// 處理登入
const handleLogin = async () => {
  const result = await userStore.login({
    username: form.username,
    password: form.password,
    provider: "db",
  });

  if (result.success) {
    // 設定線上狀態
    await userStore.setOnlineStatus(true);

    // 導向聊天室
    await router.push("/chatroom");
  }
};

// 檢查是否已登入
onMounted(() => {
  if (userStore.isAuthenticated) {
    router.push("/chatroom");
  }
});
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
}

.login-card {
  width: 100%;
  max-width: 28rem;
}

.glass-card {
  background: var(--card-bg);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-color);
  border-radius: 1rem;
  box-shadow: var(--shadow-lg);
  padding: 2rem;
}

.fade-in {
  animation: fadeIn 0.5s ease forwards;
}

.header {
  text-align: center;
  margin-bottom: 2rem;
}

.header-icon {
  width: 4rem;
  height: 4rem;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
  border-radius: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-lg);
  margin: 0 auto 1rem;
}

.icon-symbol {
  color: white;
  font-size: 1.5rem;
}

.title {
  font-size: 1.875rem;
  font-weight: 700;
  color: var(--text-color);
  margin: 0 0 0.5rem 0;
}

.subtitle {
  color: #6B7280;
  margin: 0;
}

.error-message {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 0.75rem;
}

.error-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.error-icon {
  font-size: 1rem;
}

.error-text {
  color: #DC2626;
  font-size: 0.875rem;
  font-weight: 500;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-field {
  display: flex;
  flex-direction: column;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 0.5rem;
}

.floating-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid var(--border-color);
  border-radius: 0.75rem;
  background: var(--input-bg);
  color: var(--text-color);
  font-size: 0.875rem;
  transition: all 0.3s ease;
}

.floating-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.floating-input::placeholder {
  color: #9CA3AF;
}

.remember-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.remember-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  gap: 0.5rem;
}

.remember-checkbox {
  width: 1rem;
  height: 1rem;
  accent-color: var(--primary-color);
}

.remember-text {
  font-size: 0.875rem;
  color: var(--text-color);
}

.forgot-link {
  font-size: 0.875rem;
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s ease;
}

.forgot-link:hover {
  color: var(--primary-light);
}

.login-button {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
  color: white;
  border: none;
  border-radius: 0.75rem;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: var(--shadow-md);
}

.login-button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: var(--shadow-lg);
}

.login-button:active {
  transform: translateY(0);
}

.login-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-icon {
  animation: spin 1s linear infinite;
}

.login-icon {
  font-size: 1rem;
}

.divider {
  margin: 2rem 0 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.divider-line {
  flex: 1;
  height: 1px;
  background: var(--border-color);
}

.divider-text {
  color: #6B7280;
  font-size: 0.875rem;
}

.register-section {
  text-align: center;
}

.register-text {
  color: var(--text-color);
  margin: 0;
}

.register-link {
  font-weight: 600;
  color: var(--primary-color);
  text-decoration: none;
  transition: color 0.3s ease;
}

.register-link:hover {
  color: var(--primary-light);
}

.bottom-info {
  margin-top: 2rem;
  text-align: center;
}

.terms-text {
  font-size: 0.75rem;
  color: #6B7280;
  margin: 0;
}

.terms-link {
  color: var(--primary-color);
  text-decoration: none;
  transition: color 0.3s ease;
}

.terms-link:hover {
  color: var(--primary-light);
}

/* 動畫 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 響應式設計 */
@media (max-width: 640px) {
  .glass-card {
    padding: 1.5rem;
    margin: 1rem;
  }
  
  .header-icon {
    width: 3rem;
    height: 3rem;
  }
  
  .icon-symbol {
    font-size: 1.25rem;
  }
  
  .title {
    font-size: 1.5rem;
  }
}
</style>
