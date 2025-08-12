<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useUserStore } from "~/stores/user";
import { useChatStore } from "~/stores/chat";
import { useChannelStore } from "~/stores/channel";
import { useSocket } from "~/composables/useSocket";
import ChatSidebar from "~/components/ChatSidebar.vue";
import ChatArea from "~/components/ChatArea.vue";
import UserActionBar from "~/components/UserActionBar.vue";
import EditProfile from "~/components/EditProfile.vue";
import CreateChannelSidebar from "~/components/CreateChannelSidebar.vue";

// 設定頁面元資訊
definePageMeta({
  middleware: "auth",
});

// Store
const userStore = useUserStore();
const chatStore = useChatStore();
const channelStore = useChannelStore();
const router = useRouter();
const { connect, disconnect } = useSocket();

// 側邊欄狀態管理
const sidebarView = ref("chat"); // 'chat', 'settings', 'profile'
const rightSidebarView = ref("none"); // 'none', 'create-channel'

// 連線狀態顯示
const connectionStatus = computed(() =>
  chatStore.isConnected ? "已連線" : "未連線"
);
const connectionStatusClass = computed(() =>
  chatStore.isConnected ? "bg-green-500" : "bg-red-500"
);

const handleLogout = async () => {
  // 斷開WebSocket連接
  disconnect();

  // 清除聊天室狀態
  chatStore.clearMessages();
  chatStore.setOnlineUsers([]);

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

// 右側邊欄切換處理
const showCreateChannel = () => {
  rightSidebarView.value = "create-channel";
};

const hideRightSidebar = () => {
  rightSidebarView.value = "none";
};

// 初始化
onMounted(async () => {
  // 檢查登入狀態
  userStore.initAuth();

  if (!userStore.isAuthenticated) {
    await router.push("/login");
    return;
  }

  // 檢查是否有token
  if (!userStore.token) {
    console.warn("沒有找到認證token，重新導向到登入頁面");
    await router.push("/login");
    return;
  }

  // 載入初始資料
  await Promise.all([
    channelStore.fetchChannels(),
    chatStore.fetchMessages(),
    chatStore.fetchOnlineUsers(),
  ]);

  // 建立WebSocket連接
  console.log(
    "準備建立Socket連接，token:",
    userStore.token ? "已存在" : "不存在"
  );
  const socket = connect();

  if (socket) {
    console.log("WebSocket連接已建立");
  } else {
    console.warn("WebSocket連接失敗，將使用REST API模式");
    // 設定定時刷新線上使用者（僅在沒有WebSocket時）
    const refreshInterval = setInterval(() => {
      chatStore.fetchOnlineUsers();
    }, 30000); // 30秒更新一次

    // 清理定時器
    onUnmounted(() => {
      clearInterval(refreshInterval);
    });
  }
});

// 清理資源
onUnmounted(() => {
  disconnect();
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
        @create-channel="showCreateChannel"
      />

      <UserActionBar
        v-if="sidebarView === 'settings'"
        @back="backToChat"
        @edit-profile="showEditProfile"
        @logout="handleLogout"
      />

      <EditProfile
        v-if="sidebarView === 'profile'"
        @back="() => (sidebarView = 'settings')"
        @save="() => (sidebarView = 'settings')"
      />
    </div>

    <!-- 中間聊天區域 -->
    <ChatArea />

    <!-- 右側邊欄 -->
    <div v-if="rightSidebarView !== 'none'" class="sidebar-container">
      <CreateChannelSidebar
        v-if="rightSidebarView === 'create-channel'"
        @back="hideRightSidebar"
      />
    </div>
  </div>
</template>
