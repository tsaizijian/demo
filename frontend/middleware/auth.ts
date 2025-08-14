export default defineNuxtRouteMiddleware((to, from) => {
  const userStore = useUserStore();

  // 在客戶端檢查認證狀態
  if (process.client) {
    userStore.initAuth();

    if (!userStore.isAuthenticated) {
      return navigateTo("/login");
    }
  }
});
