<template>
  <div class="min-h-screen flex items-center justify-center py-12 px-4 bg-gray-50">
    <div class="mx-auto max-w-md w-full">
      <UCard class="shadow-lg border border-gray-200">
        <template #header>
          <div class="text-center">
            <h2 class="text-2xl font-semibold text-gray-900 mb-2">歡迎使用</h2>
            <p class="text-lg text-gray-600 mb-4">聊天室系統</p>
            <hr class="border-gray-200" />
          </div>
        </template>

        <!-- 錯誤訊息 -->
        <UAlert
          v-if="userStore.error"
          icon="i-heroicons-exclamation-triangle"
          color="red"
          variant="soft"
          :title="userStore.error"
          class="mb-4"
        />

        <div class="login-form-container">
          <form @submit.prevent="handleLogin">
            <!-- 使用者名稱 -->
            <div class="form-group">
              <label for="username" class="form-label">
                請輸入帳號
              </label>
              <div class="input-container">
                <UInput
                  id="username"
                  v-model="form.username"
                  type="text"
                  placeholder="請輸入使用者帳號"
                  :disabled="userStore.loading"
                  class="w-full"
                  required
                  @keyup.enter="handleLogin"
                />
              </div>
            </div>

            <!-- 密碼 -->
            <div class="form-group">
              <label for="password" class="form-label">
                請輸入密碼
              </label>
              <div class="input-container">
                <UInput
                  id="password"
                  v-model="form.password"
                  type="password"
                  placeholder="請輸入密碼"
                  :disabled="userStore.loading"
                  autocomplete="current-password"
                  class="w-full"
                  required
                  @keyup.enter="handleLogin"
                />
              </div>
            </div>

            <!-- 登入按鈕 -->
            <UButton
              type="submit"
              color="primary"
              :loading="userStore.loading"
              :disabled="userStore.loading"
              icon="i-heroicons-user"
              class="login-button"
              block
              size="lg"
            >
              {{ userStore.loading ? '登入中...' : '登入系統' }}
            </UButton>

            <!-- 帳號選擇 -->
            <div class="account-choices">
              <NuxtLink to="/register" class="choice-link">
                <UButton
                  variant="ghost"
                  color="primary"
                  size="sm"
                >
                  註冊帳號
                </UButton>
              </NuxtLink>
              <UButton
                variant="ghost"
                color="primary"
                size="sm"
                disabled
              >
                忘記密碼
              </UButton>
            </div>
          </form>
        </div>
      </UCard>
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
.login-form-container {
  max-width: 505px;
  margin: 1.5rem auto 0;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  color: #374151;
  font-weight: 500;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.input-container {
  margin-bottom: 0.25rem;
}

.login-button {
  margin-top: 1.5rem;
}

.account-choices {
  display: flex;
  align-items: center;
  justify-content: space-around;
  margin-top: 1.5rem;
  margin-bottom: 1.5rem;
  gap: 1rem;
}

.choice-link {
  text-decoration: none;
}

h2 {
  text-align: center;
  color: #1f2937;
}
</style>
