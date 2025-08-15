<template>
  <Card class="chat-area-card">
    <!-- 聊天室標題 -->
    <template #header>
      <div v-if="activeChannel" class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="channel-info">
            <h2 class="channel-title">
              {{ activeChannel?.name || "未命名" }}
            </h2>
            <p v-if="activeChannel?.description" class="channel-description">
              {{ activeChannel.description }}
            </p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <Badge
            :value="connectionStatus"
            :severity="connectionBadgeSeverity"
            class="connection-badge"
          />
        </div>
      </div>
      <div v-else class="empty-channel-header">選擇一個聊天室開始對話</div>
    </template>

    <!-- 訊息列表 -->
    <template #content>
      <div ref="messagesContainer" class="chat-messages" @scroll="handleScroll">
        <div
          v-if="(activeMessages?.length ?? 0) === 0"
          class="empty-messages-state"
        >
          <div class="empty-content">
            <i class="pi pi-comments empty-icon"></i>
            <h3 class="empty-title">還沒有訊息</h3>
            <p class="empty-description">成為第一個在這個聊天室發言的人吧！</p>
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
          v-if="typingUsers.length > 0"
          class="typing-indicator"
          :class="{ 'many-users': typingUsers.length > 2 }"
          v-tooltip.top="
            typingUsers.length > 2 ? `正在輸入：${typingUsers.join(', ')}` : ''
          "
        >
          <span class="typing-text">{{ typingDisplayText }} 正在輸入</span>
          <div class="typing-dots">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
          </div>
        </div>
      </div>
    </template>

    <!-- 輸入區域 -->
    <template #footer v-if="activeChannel">
      <ChatInput />
    </template>
  </Card>
</template>

<script setup>
import { ref, computed, nextTick, watch, onMounted, onUnmounted } from "vue";
import { useChannelStore } from "~/stores/channel";
import { useUserStore } from "~/stores/user";
import { useSocket } from "~/composables/useSocket";
import MessageItem from "~/components/MessageItem.vue";
import ChatInput from "~/components/ChatInput.vue";

defineOptions({ name: "ChatArea" });

const channelStore = useChannelStore();
const userStore = useUserStore();
const { isConnected, socket } = useSocket();
const messagesContainer = ref(null);

// 正在輸入的用戶列表
const typingUsers = ref([]);
const typingTimers = ref(new Map());

/** 智能顯示正在輸入的文字 */
const typingDisplayText = computed(() => {
  const count = typingUsers.value.length;

  if (count === 0) return "";

  if (count === 1) {
    // 1人：直接顯示名字
    return typingUsers.value[0];
  } else if (count === 2) {
    // 2人：顯示兩個名字
    return typingUsers.value.join(", ");
  } else if (count <= 5) {
    // 3-5人：顯示前2個 + 其他人數
    const first = typingUsers.value[0];
    const second = typingUsers.value[1];
    const others = count - 2;
    return `${first}, ${second} 和其他 ${others} 人`;
  } else {
    // 6+人：只顯示總人數
    return `${count} 人`;
  }
});

/** 連線狀態顯示 */
const connectionStatus = computed(() => (isConnected() ? "已連線" : "未連線"));
const connectionBadgeSeverity = computed(() =>
  isConnected() ? "success" : "danger"
);

/** 安全取得活躍頻道／訊息 */
const activeChannel = computed(() => channelStore.currentChannel || null);
const activeMessages = computed(() => {
  const list = channelStore.currentChannelMessages;
  return Array.isArray(list) ? list : [];
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
      await channelStore.fetchChannelMessages(newChannel.id);
      scrollToBottom();
    }
  },
  { immediate: false }
);

/** 新訊息到達自動滾動 */
watch(activeMessages, () => scrollToBottom(), { deep: true });

/** 處理正在輸入事件 */
const handleUserTyping = (data) => {
  const { display_name, is_typing } = data;

  // 過濾掉自己的輸入狀態
  if (display_name === userStore.displayName) {
    return;
  }

  if (is_typing) {
    // 添加正在輸入的用戶
    if (!typingUsers.value.includes(display_name)) {
      typingUsers.value.push(display_name);

      // 限制最大顯示數量（防止性能問題）
      if (typingUsers.value.length > 10) {
        typingUsers.value = typingUsers.value.slice(-10);
      }
    }

    // 設置超時清除器（5秒後自動移除）
    if (typingTimers.value.has(display_name)) {
      clearTimeout(typingTimers.value.get(display_name));
    }

    const timer = setTimeout(() => {
      const index = typingUsers.value.indexOf(display_name);
      if (index > -1) {
        typingUsers.value.splice(index, 1);
      }
      typingTimers.value.delete(display_name);
    }, 5000);

    typingTimers.value.set(display_name, timer);
  } else {
    // 移除正在輸入的用戶
    const index = typingUsers.value.indexOf(display_name);
    if (index > -1) {
      typingUsers.value.splice(index, 1);
    }

    if (typingTimers.value.has(display_name)) {
      clearTimeout(typingTimers.value.get(display_name));
      typingTimers.value.delete(display_name);
    }
  }
};

/** 監聽 Socket 事件 */
watch(
  socket,
  (newSocket) => {
    if (newSocket) {
      // 監聽正在輸入事件
      newSocket.on("user_typing", handleUserTyping);

      // 清理之前的監聽器
      return () => {
        newSocket.off("user_typing", handleUserTyping);
      };
    }
  },
  { immediate: true }
);

onMounted(() => {
  scrollToBottom();
});

onUnmounted(() => {
  // 清理所有定時器
  typingTimers.value.forEach((timer) => clearTimeout(timer));
  typingTimers.value.clear();
});
</script>

<style scoped>
/* 聊天區域卡片樣式 */
.chat-area-card {
  height: 100vh;
  flex: 1;
  border: 0;
  border-radius: 0;
  background: var(--surface-0);
  display: flex;
  flex-direction: column;
}

.chat-area-card :deep(.p-card-header) {
  background: var(--surface-50);
  border-bottom: 1px solid var(--surface-border);
  padding: 1rem;
  flex-shrink: 0;
}

.chat-area-card :deep(.p-card-content) {
  padding: 0;
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.chat-area-card :deep(.p-card-footer) {
  background: var(--surface-50);
  border-top: 1px solid var(--surface-border);
  padding: 0;
  flex-shrink: 0;
}

/* 頻道標題區域 */
.channel-info {
  flex: 1;
}

.channel-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.channel-description {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
  margin: 0.25rem 0 0 0;
}

.empty-channel-header {
  text-align: center;
  color: var(--text-color-secondary);
  font-size: 0.875rem;
}

/* 連線狀態徽章 */
.connection-badge :deep(.p-badge) {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
}

/* 訊息區域 */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: radial-gradient(
      circle at 20px 20px,
      var(--surface-100) 1px,
      transparent 1px
    ),
    radial-gradient(
      circle at 60px 60px,
      var(--surface-100) 1px,
      transparent 1px
    );
  background-size: 80px 80px;
  background-position: 0 0, 40px 40px;
}

/* 空狀態設計 */
.empty-messages-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.empty-content {
  text-align: center;
  max-width: 300px;
}

.empty-icon {
  font-size: 3rem;
  color: var(--text-color-secondary);
  margin-bottom: 1rem;
  opacity: 0.6;
}

.empty-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 0.5rem;
}

.empty-description {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
  line-height: 1.5;
}

/* 正在輸入指示器 */
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: var(--surface-100);
  border-radius: 1rem;
  margin-top: 1rem;
  width: fit-content;
  max-width: 280px;
  animation: fadeIn 0.3s ease-in-out;
  transition: all 0.2s ease;
}

.typing-indicator.many-users {
  background: var(--primary-50);
  border: 1px solid var(--primary-200);
  cursor: help;
}

.typing-indicator.many-users:hover {
  background: var(--primary-100);
}

.typing-text {
  color: var(--text-color-secondary);
  font-size: 0.875rem;
  font-style: italic;
}

.typing-dots {
  display: flex;
  gap: 0.25rem;
}

.typing-dot {
  width: 0.5rem;
  height: 0.5rem;
  background-color: var(--primary-color);
  border-radius: 50%;
  animation: typingBounce 1.4s infinite ease-in-out;
}

.typing-dot:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-dot:nth-child(2) {
  animation-delay: -0.16s;
}

.typing-dot:nth-child(3) {
  animation-delay: 0s;
}

/* 自訂滾動條樣式 */
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: transparent;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: var(--surface-300);
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: var(--surface-400);
}

/* 動畫效果 */
@keyframes typingBounce {
  0%,
  80%,
  100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 聊天區域動畫 */
.chat-area-card {
  animation: slideInUp 0.3s ease-out;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 響應式設計 */
@media (max-width: 768px) {
  .chat-area-card :deep(.p-card-header) {
    padding: 0.75rem;
  }

  .chat-messages {
    padding: 0.75rem;
    gap: 0.75rem;
  }

  .channel-title {
    font-size: 1rem;
  }

  .channel-description {
    font-size: 0.8rem;
  }

  .typing-indicator {
    max-width: 200px;
    padding: 0.5rem 0.75rem;
    font-size: 0.8rem;
  }

  .typing-text {
    font-size: 0.8rem;
  }
}

/* 暗色主題支援 */
@media (prefers-color-scheme: dark) {
  .chat-messages {
    background: radial-gradient(
        circle at 20px 20px,
        var(--surface-700) 1px,
        transparent 1px
      ),
      radial-gradient(
        circle at 60px 60px,
        var(--surface-700) 1px,
        transparent 1px
      );
    background-size: 80px 80px;
    background-position: 0 0, 40px 40px;
  }

  .typing-indicator {
    background: var(--surface-700);
  }
}
</style>
