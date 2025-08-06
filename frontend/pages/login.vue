<template>
  <div
    class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8"
  >
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          登入聊天室
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          歡迎回來！請輸入您的登入資訊
        </p>
      </div>

      <UCard class="p-8">
        <form @submit.prevent="handleLogin" class="space-y-6">
          <!-- 錯誤訊息 -->
          <UAlert
            v-if="userStore.error"
            icon="i-heroicons-exclamation-triangle"
            color="red"
            variant="solid"
            :title="userStore.error"
            class="mb-4"
          />

          <!-- 使用者名稱 -->
          <div>
            <UFormGroup label="使用者名稱" name="username" required>
              <UInput
                v-model="form.username"
                type="text"
                placeholder="請輸入使用者名稱"
                :disabled="userStore.loading"
                required
              />
            </UFormGroup>
          </div>

          <!-- 密碼 -->
          <div>
            <UFormGroup label="密碼" name="password" required>
              <UInput
                v-model="form.password"
                type="password"
                placeholder="請輸入密碼"
                :disabled="userStore.loading"
                required
              />
            </UFormGroup>
          </div>

          <!-- 記住我 -->
          <div class="flex items-center gap-2">
            <input
              id="remember"
              type="checkbox"
              v-model="form.rememberMe"
              :disabled="userStore.loading"
              class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label for="remember" class="text-sm text-gray-700 select-none">
              記住我
            </label>
          </div>

          <!-- 登入按鈕 -->
          <div>
            <UButton
              type="submit"
              block
              :loading="userStore.loading"
              :disabled="userStore.loading"
            >
              {{ userStore.loading ? "登入中..." : "登入" }}
            </UButton>
          </div>
        </form>
      </UCard>

      <!-- 註冊連結 -->
      <div class="text-center">
        <p class="text-gray-600">
          還沒有帳號？
          <NuxtLink
            to="/register"
            class="font-medium text-blue-600 hover:text-blue-500 transition-colors"
          >
            立即註冊
          </NuxtLink>
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
