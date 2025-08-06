<script setup>
import { useUserStore } from "~/stores/user";
import { useChatStore } from "~/stores/chat";
import { useSocket } from "~/composables/useSocket";

// 設定頁面元資訊
definePageMeta({
  middleware: "auth",
});

// Store
const userStore = useUserStore();
const chatStore = useChatStore();
const router = useRouter();
const { connect, disconnect, sendMessage: socketSendMessage, deleteMessage: socketDeleteMessage, setTyping, isConnected } = useSocket();

// 響應式資料
const newMessage = ref("");
const sending = ref(false);
const messagesContainer = ref();

// 登出確認
const showLogoutModal = ref(false);

const confirmLogout = () => {
  showLogoutModal.value = true;
};

const handleLogout = async () => {
  showLogoutModal.value = false;
  
  // 斷開WebSocket連接
  disconnect();
  
  // 清除聊天室狀態
  chatStore.clearMessages();
  chatStore.setOnlineUsers([]);
  
  // 執行登出（會自動導向登出頁面）
  await userStore.logout();
};

// 使用者選單
const userMenuItems = [
  [
    {
      label: "個人設定",
      icon: "i-heroicons-user-circle",
      click: () => {
        // TODO: 開啟個人設定modal
      },
    },
  ],
  [
    {
      label: "登出",
      icon: "i-heroicons-arrow-right-on-rectangle",
      click: confirmLogout,
    },
  ],
];

// 發送訊息
const sendMessage = async () => {
  if (!newMessage.value.trim() || sending.value) return;

  sending.value = true;

  try {
    // 優先使用WebSocket發送訊息
    if (isConnected()) {
      const success = socketSendMessage(newMessage.value.trim());
      if (success) {
        newMessage.value = "";
        nextTick(() => scrollToBottom());
      }
    } else {
      // 降級為REST API
      const result = await chatStore.sendMessage(newMessage.value.trim());
      if (result.success) {
        newMessage.value = "";
        nextTick(() => scrollToBottom());
      }
    }
  } finally {
    sending.value = false;
  }
};

// 刪除訊息
const deleteMessage = async (messageId) => {
  if (confirm("確定要刪除這則訊息嗎？")) {
    // 優先使用WebSocket刪除訊息
    if (isConnected()) {
      socketDeleteMessage(messageId);
    } else {
      // 降級為REST API
      await chatStore.deleteMessage(messageId);
    }
  }
};

// 檢查是否可以刪除訊息
const canDeleteMessage = (message) => {
  return message.sender_id === userStore.userProfile?.user_id;
};

// 格式化時間
const formatTime = (timestamp) => {
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now.getTime() - date.getTime();

  // 小於一分鐘
  if (diff < 60000) {
    return "剛剛";
  }

  // 小於一小時
  if (diff < 3600000) {
    const minutes = Math.floor(diff / 60000);
    return `${minutes} 分鐘前`;
  }

  // 今天
  if (date.toDateString() === now.toDateString()) {
    return date.toLocaleTimeString("zh-TW", {
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  // 其他日期
  return date.toLocaleDateString("zh-TW", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

// 取得姓名縮寫
const getInitials = (name) => {
  if (!name) return "?";
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
};

// 滾動到底部
const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

// 處理滾動
const handleScroll = () => {
  // TODO: 實現無限滾動載入更多歷史訊息
};

// 處理輸入狀態
let typingTimeout;
const handleTyping = () => {
  if (isConnected()) {
    setTyping(true);
    
    clearTimeout(typingTimeout);
    typingTimeout = setTimeout(() => {
      setTyping(false);
    }, 1000);
  } else {
    chatStore.setTyping(true);

    clearTimeout(typingTimeout);
    typingTimeout = setTimeout(() => {
      chatStore.setTyping(false);
    }, 1000);
  }
};

// 初始化
onMounted(async () => {
  // 檢查登入狀態
  userStore.initAuth();

  if (!userStore.isAuthenticated) {
    await router.push("/login");
    return;
  }

  // 載入初始資料
  await Promise.all([chatStore.fetchMessages(), chatStore.fetchOnlineUsers()]);

  // 滾動到底部
  nextTick(() => scrollToBottom());

  // 建立WebSocket連接
  const socket = connect();
  
  if (socket) {
    console.log('WebSocket連接已建立');
  } else {
    console.warn('WebSocket連接失敗，將使用REST API模式');
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
  clearTimeout(typingTimeout);
});

// 監聽訊息變化，自動滾動到底部
watch(
  () => chatStore.messages.length,
  () => {
    nextTick(() => scrollToBottom());
  }
);
</script>

<template>
  <div class="h-screen flex flex-col bg-gray-100">
    <!-- 頭部 -->
    <header class="bg-white shadow-sm border-b border-gray-200 px-4 py-3">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <h1 class="text-xl font-semibold text-gray-900">聊天室</h1>
          <UBadge
            :label="`${chatStore.onlineUserCount} 人線上`"
            variant="soft"
            color="green"
          />
          <UBadge
            v-if="chatStore.isConnected"
            label="即時連線"
            variant="soft"
            color="blue"
          />
          <UBadge
            v-else
            label="REST模式"
            variant="soft"
            color="yellow"
          />
        </div>

        <div class="flex items-center space-x-4">
          <div class="text-sm text-gray-600">
            歡迎, {{ userStore.displayName }}
          </div>
          <UDropdown :items="userMenuItems">
            <UButton
              variant="ghost"
              :label="userStore.displayName"
              trailing-icon="i-heroicons-chevron-down-20-solid"
            />
          </UDropdown>
        </div>
      </div>
    </header>

    <!-- 主要內容區域 -->
    <div class="flex-1 flex overflow-hidden">
      <!-- 側邊欄 - 線上使用者 -->
      <aside class="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div class="p-4 border-b border-gray-200">
          <h2
            class="text-sm font-medium text-gray-900 uppercase tracking-wider"
          >
            線上使用者
          </h2>
        </div>

        <div class="flex-1 overflow-y-auto p-4">
          <div
            v-if="chatStore.onlineUsers.length === 0"
            class="text-sm text-gray-500 text-center"
          >
            正在載入...
          </div>

          <div v-else class="space-y-2">
            <div
              v-for="user in chatStore.onlineUsers"
              :key="user.id"
              class="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-50"
            >
              <div class="w-2 h-2 bg-green-500 rounded-full"></div>
              <div class="flex-1 min-w-0">
                <div class="text-sm font-medium text-gray-900 truncate">
                  {{ user.display_name || user.username }}
                </div>
                <div class="text-xs text-gray-500" v-if="user.last_seen">
                  {{ formatTime(user.last_seen) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <!-- 聊天區域 -->
      <main class="flex-1 flex flex-col">
        <!-- 訊息列表 -->
        <div
          ref="messagesContainer"
          class="flex-1 overflow-y-auto p-4 space-y-4"
          @scroll="handleScroll"
        >
          <!-- 載入指示器 -->
          <div v-if="chatStore.loading" class="text-center py-4">
            <UIcon name="i-heroicons-arrow-path" class="animate-spin h-6 w-6" />
            <div class="text-sm text-gray-500 mt-2">載入中...</div>
          </div>

          <!-- 錯誤訊息 -->
          <UAlert
            v-if="chatStore.error"
            icon="i-heroicons-exclamation-triangle"
            color="red"
            variant="soft"
            :title="chatStore.error"
            class="mb-4"
          />

          <!-- 沒有訊息 -->
          <div
            v-if="!chatStore.loading && chatStore.messages.length === 0"
            class="text-center py-12"
          >
            <UIcon
              name="i-heroicons-chat-bubble-left"
              class="h-12 w-12 text-gray-400 mx-auto mb-4"
            />
            <div class="text-gray-500">還沒有訊息，開始聊天吧！</div>
          </div>

          <!-- 訊息列表 -->
          <div
            v-for="message in chatStore.sortedMessages"
            :key="message.id"
            class="flex space-x-3"
            :class="{
              'justify-end':
                message.sender_id === userStore.userProfile?.user_id,
            }"
          >
            <!-- 其他人的訊息 -->
            <div
              v-if="message.sender_id !== userStore.userProfile?.user_id"
              class="flex space-x-3 max-w-xs lg:max-w-md"
            >
              <!-- 使用者頭像 -->
              <div
                class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center flex-shrink-0"
              >
                <span class="text-xs font-medium text-gray-700">
                  {{ getInitials(message.sender_name) }}
                </span>
              </div>

              <!-- 訊息內容 -->
              <div class="flex flex-col space-y-1">
                <div class="flex items-center space-x-2">
                  <span class="text-sm font-medium text-gray-900">
                    {{ message.sender_name }}
                  </span>
                  <span class="text-xs text-gray-500">
                    {{ formatTime(message.created_on) }}
                  </span>
                </div>

                <div
                  class="bg-white rounded-lg px-3 py-2 shadow-sm border border-gray-200"
                >
                  <p class="text-sm text-gray-900">{{ message.content }}</p>
                </div>
              </div>
            </div>

            <!-- 自己的訊息 -->
            <div v-else class="flex space-x-3 max-w-xs lg:max-w-md">
              <!-- 訊息內容 -->
              <div class="flex flex-col space-y-1">
                <div class="flex items-center justify-end space-x-2">
                  <span class="text-xs text-gray-500">
                    {{ formatTime(message.created_on) }}
                  </span>
                  <span class="text-sm font-medium text-gray-900">你</span>
                </div>

                <div
                  class="bg-blue-500 rounded-lg px-3 py-2 shadow-sm relative"
                >
                  <p class="text-sm text-white">{{ message.content }}</p>

                  <!-- 刪除按鈕 -->
                  <UButton
                    v-if="canDeleteMessage(message)"
                    @click="deleteMessage(message.id)"
                    size="xs"
                    color="red"
                    variant="ghost"
                    icon="i-heroicons-trash"
                    class="absolute -top-2 -right-2 opacity-0 hover:opacity-100 transition-opacity"
                  />
                </div>
              </div>

              <!-- 使用者頭像 -->
              <div
                class="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0"
              >
                <span class="text-xs font-medium text-white">
                  {{ getInitials(userStore.displayName) }}
                </span>
              </div>
            </div>
          </div>

          <!-- 正在輸入指示器 -->
          <div
            v-if="chatStore.typingUsers.length > 0"
            class="flex items-center space-x-2 text-sm text-gray-500"
          >
            <UIcon
              name="i-heroicons-ellipsis-horizontal"
              class="animate-pulse"
            />
            <span>{{ chatStore.typingUsers.join(", ") }} 正在輸入...</span>
          </div>
        </div>

        <!-- 訊息輸入區域 -->
        <div class="border-t border-gray-200 p-4 bg-white">
          <form @submit.prevent="sendMessage" class="flex space-x-2">
            <UInput
              v-model="newMessage"
              placeholder="輸入訊息..."
              class="flex-1"
              :disabled="sending"
              @keydown="handleTyping"
            />
            <UButton
              type="submit"
              :loading="sending"
              :disabled="!newMessage.trim() || sending"
              icon="i-heroicons-paper-airplane"
            >
              發送
            </UButton>
          </form>
        </div>
      </main>
    </div>

    <!-- 登出確認對話框 -->
    <UModal v-model="showLogoutModal">
      <UCard :ui="{ ring: '', divide: 'divide-y divide-gray-100 dark:divide-gray-800' }">
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-5 h-5 text-amber-500" />
            <h3 class="text-lg font-semibold text-gray-900">確認登出</h3>
          </div>
        </template>

        <div class="py-4">
          <p class="text-sm text-gray-600">
            您確定要登出聊天室嗎？這將會：
          </p>
          <ul class="mt-3 space-y-1 text-sm text-gray-500">
            <li class="flex items-center gap-2">
              <UIcon name="i-heroicons-wifi-slash" class="w-4 h-4" />
              斷開即時連線
            </li>
            <li class="flex items-center gap-2">
              <UIcon name="i-heroicons-arrow-right-on-rectangle" class="w-4 h-4" />
              清除登入狀態
            </li>
            <li class="flex items-center gap-2">
              <UIcon name="i-heroicons-arrow-path" class="w-4 h-4" />
              返回登入頁面
            </li>
          </ul>
        </div>

        <template #footer>
          <div class="flex justify-end gap-2">
            <UButton 
              color="gray" 
              variant="soft" 
              @click="showLogoutModal = false"
            >
              取消
            </UButton>
            <UButton 
              color="red" 
              @click="handleLogout"
              icon="i-heroicons-arrow-right-on-rectangle"
            >
              確認登出
            </UButton>
          </div>
        </template>
      </UCard>
    </UModal>
  </div>
</template>
