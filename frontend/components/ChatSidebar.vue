<template>
  <div class="sidebar">
    <!-- 側邊欄標題 -->
    <div class="sidebar-header">
      <div class="flex items-center justify-between">
        <h1 class="text-lg font-semibold">聊天室</h1>
        <ClientOnly>
          <div class="flex items-center space-x-2">
            <div
              :class="connectionStatusClass"
              class="w-2 h-2 rounded-full"
            ></div>
            <span class="text-xs opacity-75">{{ connectionStatus }}</span>
          </div>
          <template #fallback>
            <div class="flex items-center space-x-2">
              <div class="w-2 h-2 rounded-full bg-gray-400"></div>
              <span class="text-xs opacity-75">連線中...</span>
            </div>
          </template>
        </ClientOnly>
      </div>
      <div class="mt-2 flex items-center justify-between">
        <ClientOnly>
          <span class="text-sm opacity-90">
            {{ userStore.displayName }}
          </span>
          <template #fallback>
            <span class="text-sm opacity-90">
              訪客
            </span>
          </template>
        </ClientOnly>
        <button
          @click="$emit('show-user-settings')"
          class="settings-btn"
          title="用戶設定"
        >
          <!-- 選項1: 簡單的三個點 -->
          <svg
            width="18"
            height="18"
            viewBox="0 0 20 20"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <circle cx="10" cy="4" r="2" fill="rgba(255, 255, 255, 0.8)" />
            <circle cx="10" cy="10" r="2" fill="rgba(255, 255, 255, 0.8)" />
            <circle cx="10" cy="16" r="2" fill="rgba(255, 255, 255, 0.8)" />
          </svg>
        </button>
      </div>
    </div>

    <!-- 聊天室清單 -->
    <div class="channel-list">
      <ChannelSidebar />
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useUserStore } from "~/stores/user";
import ChannelSidebar from "~/components/ChannelSidebar.vue";

// 定義 props
const props = defineProps({
  connectionStatus: {
    type: String,
    default: "未連線",
  },
  connectionStatusClass: {
    type: String,
    default: "bg-red-500",
  },
});

// 定義事件
const emit = defineEmits(["show-user-settings"]);

const userStore = useUserStore();
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

.channel-list {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

/* 滾動條樣式 */
.channel-list::-webkit-scrollbar {
  width: 6px;
}

.channel-list::-webkit-scrollbar-track {
  background: transparent;
}

.channel-list::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.channel-list::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.3);
}

/* 設定按鈕樣式 */
.settings-btn {
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

.settings-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.05);
}

.settings-btn:hover svg path {
  fill: rgba(255, 255, 255, 1);
}

.settings-btn svg {
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
