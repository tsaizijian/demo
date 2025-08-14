<script setup>
import { useUserStore } from "~/stores/user";
import Button from "primevue/button";
import Toast from "primevue/toast";

const userStore = useUserStore();
const route = useRoute();

// 初始化認證狀態
onMounted(() => {
  userStore.initAuth();
});

// 主題切換功能
const isDark = ref(false);

const toggleDarkMode = () => {
  isDark.value = !isDark.value;
  if (process.client) {
    document.documentElement.classList.toggle("dark", isDark.value);
    localStorage.setItem("theme", isDark.value ? "dark" : "light");
  }
};

// 初始化主題
onMounted(() => {
  if (process.client) {
    const savedTheme = localStorage.getItem("theme");
    isDark.value = savedTheme === "dark";
    document.documentElement.classList.toggle("dark", isDark.value);
  }
});

async function logout() {
  await userStore.logout();
}

// 計算是否顯示導覽列
const showNavbar = computed(() => {
  // 聊天室頁面不顯示導覽列
  return route.path !== "/chatroom";
});
</script>

<template>
  <div class="layout-container">
    <!-- 導覽列 -->
    <nav
      v-if="showNavbar"
      class="bg-white/80 backdrop-blur-sm border-b border-emerald-200 sticky top-0 z-10"
    >
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-4">
          <!-- Logo -->
          <div
            class="flex items-center cursor-pointer"
            @click="navigateTo('/')"
          >
            <i class="pi pi-comments text-emerald-600 text-2xl mr-2"></i>
            <h1 class="text-xl font-bold text-emerald-800">聊天室系統</h1>
          </div>

          <!-- 右側按鈕 -->
          <div class="flex items-center gap-2">
            <!-- 主題切換 -->
            <ClientOnly>
              <Button
                @click="toggleDarkMode"
                :icon="isDark ? 'pi pi-sun' : 'pi pi-moon'"
                text
                rounded
                :aria-label="isDark ? '切換到亮色主題' : '切換到暗色主題'"
              />
            </ClientOnly>

            <!-- 未登入狀態 -->
            <ClientOnly>
              <template v-if="!userStore.isAuthenticated">
                <!-- 首頁：顯示登入/註冊 -->
                <template v-if="route.path === '/'">
                  <Button
                    @click="navigateTo('/login')"
                    label="登入"
                    icon="pi pi-sign-in"
                    outlined
                  />
                  <Button
                    @click="navigateTo('/register')"
                    label="註冊"
                    icon="pi pi-user-plus"
                  />
                </template>

                <!-- 登入頁面：顯示返回首頁 -->
                <template v-else-if="route.path === '/login'">
                  <Button
                    @click="navigateTo('/')"
                    label="返回首頁"
                    icon="pi pi-home"
                    text
                  />
                  <Button
                    @click="navigateTo('/register')"
                    label="註冊"
                    icon="pi pi-user-plus"
                    outlined
                  />
                </template>

                <!-- 註冊頁面：顯示返回首頁和登入 -->
                <template v-else-if="route.path === '/register'">
                  <Button
                    @click="navigateTo('/')"
                    label="返回首頁"
                    icon="pi pi-home"
                    text
                  />
                  <Button
                    @click="navigateTo('/login')"
                    label="登入"
                    icon="pi pi-sign-in"
                    outlined
                  />
                </template>
              </template>

              <!-- 已登入狀態 -->
              <template v-else>
                <span class="text-sm text-emerald-700 mr-2">
                  歡迎，{{ userStore.displayName }}
                </span>
                <Button
                  @click="navigateTo('/chatroom')"
                  label="聊天室"
                  icon="pi pi-comments"
                  outlined
                />
                <Button
                  @click="logout"
                  label="登出"
                  icon="pi pi-sign-out"
                  severity="secondary"
                />
              </template>
            </ClientOnly>
          </div>
        </div>
      </div>
    </nav>
    <!-- 主要內容 -->
    <main class="main-content">
      <slot></slot>
    </main>
    <Toast />
  </div>
</template>

<style scoped>
.layout-container {
  background: var(--background-color, #f9fafb);
  min-height: 100vh;
}

.main-content {
  flex: 1;
}

/* 響應式設計 */
@media (max-width: 768px) {
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

@media (min-width: 768px) {
  .desktop-nav {
    display: flex;
  }

  .user-name {
    display: block;
  }
}
</style>
