<script setup>
import { useUserStore } from "~/stores/user";

const userStore = useUserStore();

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
</script>

<template>
  <div class="layout-container">
    <!-- 主要內容 -->
    <main class="main-content">
      <NuxtPage />
    </main>
  </div>
</template>

<style scoped>
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
