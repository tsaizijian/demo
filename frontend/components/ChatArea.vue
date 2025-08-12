<template>
  <div class="chat-area flex flex-col h-full">
    <!-- 聊天室標題 -->
    <div class="chat-header border-b px-4 py-3">
      <div v-if="activeChannel" class="flex items-center justify-between">
        <div class="flex items-center">
          <div>
            <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
              {{ activeChannel?.name || "未命名" }}
            </h2>
            <p class="text-sm text-gray-500 dark:text-gray-400">
              {{ activeChannel?.description || "" }}
            </p>
          </div>
        </div>
        <div class="flex items-center space-x-2">
          <div
            :class="connectionStatusClass"
            class="w-2 h-2 rounded-full"
          ></div>
          <span class="text-xs text-gray-500">{{ connectionStatus }}</span>
        </div>
      </div>
      <div v-else class="text-center text-gray-500 dark:text-gray-400">
        選擇一個聊天室開始對話
      </div>
    </div>

    <!-- 訊息列表 -->
    <div
      ref="messagesContainer"
      class="chat-messages flex-1 overflow-y-auto px-4 py-3"
      @scroll="handleScroll"
    >
      <div
        v-if="(activeMessages?.length ?? 0) === 0"
        class="flex items-center justify-center h-full"
      >
        <div class="text-center text-gray-500 dark:text-gray-400">
          <div class="text-4xl mb-4">💬</div>
          <p class="text-lg font-medium mb-2">還沒有訊息</p>
          <p class="text-sm">成為第一個在這個聊天室發言的人吧！</p>
        </div>
      </div>

      <div v-else class="space-y-4">
        <MessageItem
          v-for="(message, index) in activeMessages ?? []"
          :key="message.id ?? `m-${index}`"
          :message="message"
          :show-sender-name="shouldShowSenderName(message, index)"
        />
      </div>

      <!-- 正在輸入指示器 -->
      <div
        v-if="chatStore.typingUsers.length > 0"
        class="typing-indicator mt-4"
      >
        <span>{{ chatStore.typingUsers.join(", ") }} 正在輸入</span>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    </div>

    <!-- 輸入區域 -->
    <ChatInput v-if="!!activeChannel" class="border-t" />
  </div>
</template>

<script setup>
import { ref, computed, nextTick, watch, onMounted } from "vue";
import { useChatStore } from "~/stores/chat";
import { useChannelStore } from "~/stores/channel";
import { useUserStore } from "~/stores/user";
import MessageItem from "~/components/MessageItem.vue";
import ChatInput from "~/components/ChatInput.vue";

defineOptions({ name: "ChatArea" });

const chatStore = useChatStore();
const channelStore = useChannelStore();
const userStore = useUserStore();
const messagesContainer = ref(null);

/** 連線狀態顯示 */
const connectionStatus = computed(() =>
  chatStore.isConnected ? "已連線" : "未連線"
);
const connectionStatusClass = computed(() =>
  chatStore.isConnected ? "bg-green-500" : "bg-red-500"
);

/** 安全取得活躍頻道／訊息 */
const activeChannel = computed(() => channelStore.currentChannel || null);
const activeMessages = computed(() => {
  const list = channelStore.currentChannelMessages;
  return Array.isArray(list) ? list : [];
});

/** 頭像首字（SSR 安全） */
const avatarInitial = computed(() => {
  const name = activeChannel.value?.name;
  if (typeof name === "string" && name.length > 0) {
    return name[0].toUpperCase();
  }
  return "?";
});

/** 是否顯示發送者名稱（避免 undefined 時間/欄位） */
const shouldShowSenderName = (message, index) => {
  if (!message || !userStore.userProfile) return false;
  if (message.sender_id === userStore.userProfile.user_id) return false;
  if (index === 0) return true;

  const prev = activeMessages.value?.[index - 1];
  if (!prev || prev.sender_id !== message.sender_id) return true;

  const curTs = message.created_on ? new Date(message.created_on).getTime() : 0;
  const prevTs = prev.created_on ? new Date(prev.created_on).getTime() : 0;
  return curTs - prevTs > 5 * 60 * 1000;
};

/** 滾至底部（SSR/CSR 安全） */
const scrollToBottom = () => {
  nextTick(() => {
    const el = messagesContainer.value;
    if (el) el.scrollTop = el.scrollHeight;
  });
};

const handleScroll = () => {
  // 之後可在此實作上拉載入歷史訊息
};

/** 切換頻道時載入訊息並滾到底 */
watch(
  activeChannel,
  async (newChannel) => {
    if (newChannel?.id) {
      // 如果有 loadMessages 方法則使用，否則使用 fetchMessages
      if (chatStore.loadMessages) {
        await chatStore.loadMessages(newChannel.id);
      } else if (chatStore.fetchMessages) {
        await chatStore.fetchMessages();
      }
      scrollToBottom();
    }
  },
  { immediate: false }
);

/** 新訊息到達自動滾動 */
watch(activeMessages, () => scrollToBottom(), { deep: true });

onMounted(() => {
  scrollToBottom();
});
</script>

<style scoped>
.chat-area {
  min-height: 0; /* 讓子元素 flex-1 正確滾動 */
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chat-header {
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
  background-color: white;
}

.bg-telegram-blue {
  /* 你可以換成 Tailwind config 自訂色 */
  background: linear-gradient(135deg, #41b4e6, #2696d9);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="2" fill="%23f0f0f0" opacity="0.3"/></svg>')
    repeat;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.typing-dot {
  width: 0.5rem;
  height: 0.5rem;
  background-color: currentColor;
  border-radius: 50%;
  animation: bounce 1s infinite;
}

.typing-dot:nth-child(2) {
  animation-delay: 0.1s;
}

.typing-dot:nth-child(3) {
  animation-delay: 0.2s;
}

@keyframes bounce {
  0%,
  80%,
  100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}
</style>
