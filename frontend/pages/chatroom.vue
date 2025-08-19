<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useUserStore } from "~/stores/user";
import { useChannelStore } from "~/stores/channel";
import { useSocket } from "~/composables/useSocket";
import ChatSidebar from "~/components/ChatSidebar.vue";
import ChatArea from "~/components/ChatArea.vue";
import UserActionBar from "~/components/UserActionBar.vue";
import EditProfile from "~/components/EditProfile.vue";
import DeletedChannelsView from "~/components/DeletedChannelsView.vue";

// 設定頁面元資訊
definePageMeta({
  middleware: "auth",
});

// Store
const userStore = useUserStore();
const channelStore = useChannelStore();
const router = useRouter();
const { connect, disconnect } = useSocket();

// 側邊欄狀態管理
const sidebarView = ref("chat"); // 'chat', 'settings', 'profile', 'deleted-channels'

// Socket connection
const { isConnected, isSocketConnected } = useSocket();

// 連線狀態顯示
const connectionStatus = computed(() =>
  isSocketConnected.value ? "已連線" : "未連線"
);
const connectionStatusClass = computed(() =>
  isSocketConnected.value ? "bg-green-500" : "bg-red-500"
);

const handleLogout = async () => {
  // 斷開WebSocket連接
  disconnect();

  // 清除頻道狀態
  channelStore.reset();

  // 執行登出（會自動導向登出頁面）
  await userStore.logout();
};

// 側邊欄切換處理
const showUserSettings = () => {
  sidebarView.value = "settings";
};

const showEditProfile = () => {
  sidebarView.value = "profile";
};

const backToChat = () => {
  sidebarView.value = "chat";
};

const showDeletedChannels = () => {
  sidebarView.value = "deleted-channels";
};

// 移除了右側邊欄處理，現在直接使用 channelStore.showChannelCreator

// 初始化
onMounted(async () => {
  // 檢查登入狀態
  userStore.initAuth();

  if (!userStore.isAuthenticated) {
    await navigateTo("/login");
    return;
  }

  // 檢查是否有token
  if (!userStore.accessToken) {
    console.warn("沒有找到認證token，重新導向到登入頁面");
    await router.push("/login");
    return;
  }

  // 載入初始資料
  await channelStore.fetchChannels();

  // 建立WebSocket連接
  console.log(
    "準備建立Socket連接，token:",
    userStore.accessToken ? "已存在" : "不存在"
  );
  const socket = connect();

  // 監聽瀏覽器關閉事件
  if (import.meta.client) {
    window.addEventListener("beforeunload", handleBeforeUnload);
  }

  if (socket) {
    console.log("WebSocket連接已建立");
  } else {
    console.warn("WebSocket連接失敗，將使用REST API模式");
    // 設定定時刷新（僅在沒有WebSocket時）
    const refreshInterval = setInterval(() => {
      // 可以在這裡定期更新頻道列表等
      channelStore.fetchChannels();
    }, 60000); // 60秒更新一次

    // 清理定時器
    onUnmounted(() => {
      clearInterval(refreshInterval);
    });
  }
});

// 處理瀏覽器關閉
const handleBeforeUnload = () => {
  disconnect();
};

// 清理資源
onUnmounted(() => {
  disconnect();

  // 移除事件監聽器
  if (import.meta.client) {
    window.removeEventListener("beforeunload", handleBeforeUnload);
  }
});
</script>

<style scoped>
.telegram-container {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.sidebar-container {
  width: 320px;
  flex-shrink: 0;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .sidebar-container {
    width: 100%;
  }
}
</style>

<template>
  <div class="telegram-container">
    <!-- 左側邊欄 -->
    <div class="sidebar-container">
      <!-- 動態切換左側邊欄內容 -->
      <ChatSidebar
        v-if="sidebarView === 'chat'"
        :connectionStatus="connectionStatus"
        :connectionStatusClass="connectionStatusClass"
        @show-user-settings="showUserSettings"
        @logout="handleLogout"
      />

      <UserActionBar
        v-if="sidebarView === 'settings'"
        @back="backToChat"
        @edit-profile="showEditProfile"
        @logout="handleLogout"
        @view-deleted-channels="showDeletedChannels"
      />

      <EditProfile
        v-if="sidebarView === 'profile'"
        @back="() => (sidebarView = 'settings')"
        @save="() => (sidebarView = 'settings')"
      />

      <DeletedChannelsView
        v-if="sidebarView === 'deleted-channels'"
        @close="() => (sidebarView = 'settings')"
      />
    </div>

    <!-- 中間聊天區域 -->
    <ChatArea />
  </div>
</template>
