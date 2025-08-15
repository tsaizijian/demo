<template>
  <div class="flex items-center justify-center py-12 px-4 bg-gray-50">
    <div class="mx-auto max-w-md w-full">
      <Card class="login-card shadow-lg border border-gray-200">
        <template #header>
          <div class="text-center">
            <h2 class="text-2xl font-semibold text-gray-900 mb-2">歡迎使用</h2>
            <p class="text-lg text-gray-600 mb-4">聊天室系統</p>
            <hr class="border-gray-200" />
          </div>
        </template>

        <template #content>
          <!-- 錯誤訊息 -->
          <Message
            v-if="userStore.error"
            severity="error"
            :closable="false"
            class="mb-4"
          >
            <template #messageicon>
              <i class="pi pi-exclamation-triangle"></i>
            </template>
            {{ userStore.error }}
          </Message>

          <div class="login-form-container">
            <form @submit.prevent="handleLogin">
              <!-- 使用者名稱 -->
              <div class="form-group">
                <label for="username" class="form-label"> 請輸入帳號 </label>
                <div class="input-container">
                  <InputText
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
                <label for="password" class="form-label"> 請輸入密碼 </label>
                <div class="input-container">
                  <Password
                    id="password"
                    v-model="form.password"
                    placeholder="請輸入密碼"
                    :disabled="userStore.loading"
                    autocomplete="current-password"
                    class="w-full"
                    required
                    :feedback="false"
                    toggleMask
                    @keyup.enter="handleLogin"
                  />
                </div>
              </div>

              <!-- 登入按鈕 -->
              <Button
                type="submit"
                :loading="userStore.loading"
                :disabled="userStore.loading"
                icon="pi pi-user"
                class="login-button w-full"
                size="large"
                :label="userStore.loading ? '登入中...' : '登入系統'"
              />

              <!-- 帳號選擇 -->
              <div class="account-choices">
                <NuxtLink to="/register" class="choice-link">
                  <Button text size="small" label="註冊帳號" />
                </NuxtLink>
                <Button text size="small" label="忘記密碼" disabled />
              </div>
            </form>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup>
import { useUserStore } from "~/stores/user";
import Card from "primevue/card";
import Button from "primevue/button";
import InputText from "primevue/inputtext";
import Password from "primevue/password";
import Message from "primevue/message";

// 設定頁面元資訊
definePageMeta({
  layout: "default",
  auth: false, // 不需要認證
});

// 響應式資料
const userStore = useUserStore();

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
    await navigateTo("/chatroom");
  }
};

// 檢查是否已登入
onMounted(async () => {
  if (userStore.isAuthenticated) {
    await navigateTo("/chatroom");
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
  color: var(--text-color);
  font-weight: 500;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.input-container {
  margin-bottom: 0.25rem;
}

/* PrimeVue Input 樣式 */
:deep(.p-inputtext) {
  width: 100%;
  border: 2px solid var(--border-color);
  border-radius: 12px;
  background: var(--input-bg);
  color: var(--text-color);
  padding: 12px 16px;
  font-size: 14px;
  transition: all 0.3s ease;
}

:deep(.p-inputtext:focus) {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

:deep(.p-password) {
  width: 100%;
}

:deep(.p-password .p-inputtext) {
  width: 100%;
}

/* PrimeVue Button 樣式 */
:deep(.p-button) {
  background: linear-gradient(
    135deg,
    var(--primary-color),
    var(--primary-light)
  );
  border: none;
  border-radius: 12px;
  color: white;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: var(--shadow-md);
}

:deep(.p-button:hover) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

:deep(.p-button.p-button-text) {
  background: transparent;
  color: var(--primary-color);
  box-shadow: none;
}

:deep(.p-button.p-button-text:hover) {
  background: var(--hover-bg);
  transform: none;
  box-shadow: none;
}

/* PrimeVue Message 樣式 */
:deep(.p-message) {
  border-radius: 12px;
  border: none;
  box-shadow: var(--shadow-sm);
}

:deep(.p-message.p-message-error) {
  background: #fef2f2;
  color: #dc2626;
}

/* PrimeVue Card 樣式 */
.login-card :deep(.p-card) {
  background: var(--card-bg) !important;
  border: 1px solid var(--border-color) !important;
  border-radius: 16px !important;
  box-shadow: var(--shadow-lg) !important;
}

.login-card :deep(.p-card .p-card-header) {
  border-bottom: 1px solid var(--border-color) !important;
  border-radius: 16px 16px 0 0 !important;
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
  color: var(--text-color);
}
</style>
