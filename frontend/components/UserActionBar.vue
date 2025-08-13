<template>
  <div class="sidebar">
    <!-- 用戶操作標題 -->
    <div class="sidebar-header">
      <div class="flex items-center justify-between">
        <h1 class="text-lg font-semibold">設定</h1>
        <button @click="$emit('back')" class="back-btn" title="返回">
          <svg
            width="18"
            height="18"
            viewBox="0 0 20 20"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M12.5 15L7.5 10L12.5 5"
              stroke="rgba(255, 255, 255, 0.8)"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </button>
      </div>
    </div>

    <!-- 用戶資訊 -->
    <div class="user-info-section">
      <div class="flex items-center p-4">
        <div class="flex-1">
          <h3 class="text-lg font-semibold text-gray-900">
            {{ userStore.displayName }}
          </h3>
          <p class="text-sm text-gray-500">線上</p>
        </div>
      </div>
    </div>

    <!-- 操作選單 -->
    <div class="action-list">
      <!-- 個人資料 -->
      <div class="action-item" @click="$emit('edit-profile')">
        <div class="action-icon bg-blue-100">
          <svg
            class="w-5 h-5 text-blue-600"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fill-rule="evenodd"
              d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"
              clip-rule="evenodd"
            />
          </svg>
        </div>
        <div class="action-content">
          <div class="action-title">我的帳號</div>
          <div class="action-subtitle">設定個人資料</div>
        </div>
        <div class="action-arrow">
          <svg
            class="w-4 h-4 text-gray-400"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fill-rule="evenodd"
              d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
              clip-rule="evenodd"
            />
          </svg>
        </div>
      </div>

      <!-- 通知設定 -->
      <div class="action-item">
        <div class="action-icon bg-green-100">
          <svg
            class="w-5 h-5 text-green-600"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z"
            />
          </svg>
        </div>
        <div class="action-content">
          <div class="action-title">通知</div>
          <div class="action-subtitle">訊息通知設定</div>
        </div>
        <div class="action-arrow">
          <svg
            class="w-4 h-4 text-gray-400"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fill-rule="evenodd"
              d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
              clip-rule="evenodd"
            />
          </svg>
        </div>
      </div>

      <!-- 隱私設定 -->
      <div class="action-item">
        <div class="action-icon bg-purple-100">
          <svg
            class="w-5 h-5 text-purple-600"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fill-rule="evenodd"
              d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z"
              clip-rule="evenodd"
            />
          </svg>
        </div>
        <div class="action-content">
          <div class="action-title">隱私與安全</div>
          <div class="action-subtitle">隱私設定</div>
        </div>
        <div class="action-arrow">
          <svg
            class="w-4 h-4 text-gray-400"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fill-rule="evenodd"
              d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
              clip-rule="evenodd"
            />
          </svg>
        </div>
      </div>

      <!-- 分隔線 -->
      <div class="divider"></div>

      <!-- 登出 -->
      <div class="action-item logout-item" @click="$emit('logout')">
        <div class="action-icon bg-red-100">
          <svg
            class="w-5 h-5 text-red-600"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fill-rule="evenodd"
              d="M3 3a1 1 0 00-1 1v12a1 1 0 102 0V4a1 1 0 00-1-1zm10.293 9.293a1 1 0 001.414 1.414l3-3a1 1 0 000-1.414l-3-3a1 1 0 10-1.414 1.414L14.586 9H7a1 1 0 100 2h7.586l-1.293 1.293z"
              clip-rule="evenodd"
            />
          </svg>
        </div>
        <div class="action-content">
          <div class="action-title text-red-600">登出</div>
          <div class="action-subtitle">登出聊天室</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useUserStore } from "~/stores/user";

// 定義事件
const emit = defineEmits(["back", "edit-profile", "logout"]);

const userStore = useUserStore();

// 用戶名稱縮寫
const userInitials = computed(() => {
  const name = userStore.displayName || "User";
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
});
</script>

<style scoped>
.sidebar {
  width: 20rem;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
  overflow-x: hidden;
  max-width: 320px;
  height: 100vh;
}

.sidebar-header {
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
  background: #10b981;
  color: white;
}

.user-info-section {
  border-bottom: 1px solid #e5e7eb;
  background: white;
}

.bg-telegram-blue {
  background: linear-gradient(135deg, #41b4e6, #2696d9);
}

.action-list {
  flex: 1;
  overflow-y: auto;
  background: white;
}

.action-item {
  display: flex;
  align-items: center;
  padding: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
  border-bottom: 1px solid #f3f4f6;
}

.action-item:hover:not(.logout-item) {
  background-color: #f9fafb;
}

.logout-item:hover {
  background-color: #fef2f2;
}

.action-icon {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
  flex-shrink: 0;
}

.action-content {
  flex: 1;
}

.action-title {
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 0.125rem;
}

.action-subtitle {
  font-size: 0.875rem;
  color: #6b7280;
}

.action-arrow {
  margin-left: 1rem;
}

.divider {
  height: 0.5rem;
  background-color: #f3f4f6;
}

/* 返回按鈕樣式 */
.back-btn {
  padding: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.05);
}

.back-btn:hover svg path {
  stroke: rgba(255, 255, 255, 1);
}

.back-btn svg {
  display: block;
  transition: all 0.2s ease;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .sidebar {
    width: 100%;
  }
}
</style>
