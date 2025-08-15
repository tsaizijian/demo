export default defineNuxtRouteMiddleware((to, from) => {
  const userStore = useUserStore();

  // 在客戶端檢查認證狀態
  if (import.meta.client) {
    if (!userStore.isAuthenticated) {
      return navigateTo("/login");
    }
  }
});
