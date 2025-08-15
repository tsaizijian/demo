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
        <!-- 歷史訊息載入指示器 -->
        <div
          v-if="isLoadingHistory && hasMoreHistory"
          class="history-loading-indicator"
        >
          <div class="loading-content">
            <i class="pi pi-spin pi-spinner loading-icon"></i>
            <span class="loading-text">載入歷史訊息...</span>
          </div>
        </div>

        <!-- 沒有更多歷史訊息提示 -->
        <div
          v-else-if="!hasMoreHistory && (activeMessages?.length ?? 0) > 0"
          class="no-more-history"
        >
          <span class="no-more-text">已顯示所有訊息</span>
        </div>

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

        <div v-else class="messages-list">
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

        <!-- 跳到底部按鈕 -->
        <Transition name="scroll-to-bottom">
          <div v-if="showScrollToBottom" class="scroll-to-bottom-container">
            <Button
              @click="scrollToBottom(true)"
              icon="pi pi-chevron-down"
              rounded
              class="scroll-to-bottom-btn"
              v-tooltip.top="'跳到最新訊息'"
              severity="secondary"
            />
          </div>
        </Transition>
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

// 歷史訊息載入狀態
const isLoadingHistory = ref(false);
const hasMoreHistory = ref(true);
const lastScrollTop = ref(0);

// 顯示跳到底部按鈕
const showScrollToBottom = ref(false);

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
const scrollToBottom = (smooth = false) => {
  nextTick(() => {
    const el = messagesContainer.value;
    if (el) {
      if (smooth) {
        // 用於新訊息的平滑滾動
        el.scrollTo({
          top: el.scrollHeight,
          behavior: "smooth",
        });
      } else {
        // 用於初始載入的立即跳轉
        el.scrollTop = el.scrollHeight;
      }
    }
  });
};

const handleScroll = async () => {
  const container = messagesContainer.value;
  if (!container) return;

  // 檢查是否接近底部 - 與自動滾動邏輯保持一致
  const scrollFromBottom = container.scrollHeight - (container.scrollTop + container.clientHeight);
  const isNearBottom = scrollFromBottom <= 100;
  showScrollToBottom.value = !isNearBottom;

  // 歷史訊息載入邏輯
  if (
    !isLoadingHistory.value &&
    hasMoreHistory.value &&
    container.scrollTop <= 50
  ) {
    // 記錄當前滾動位置和容器高度
    const previousScrollHeight = container.scrollHeight;
    const previousScrollTop = container.scrollTop;

    isLoadingHistory.value = true;

    try {
      // 取得當前頻道的最舊訊息時間作為參考點
      const oldestMessage = activeMessages.value?.[0];
      const beforeTimestamp = oldestMessage?.created_on;

      // 載入歷史訊息
      const result = await channelStore.loadHistoryMessages(
        activeChannel.value?.id,
        beforeTimestamp,
        20 // 每次載入 20 條
      );

      if (result.success && result.messages?.length > 0) {
        // 等待 DOM 更新
        await nextTick();

        // 計算新的滾動位置，保持用戶當前查看的訊息位置
        const newScrollHeight = container.scrollHeight;
        const scrollDiff = newScrollHeight - previousScrollHeight;
        container.scrollTop = previousScrollTop + scrollDiff;

        // 如果返回的訊息少於請求數量，表示沒有更多歷史訊息
        if (result.messages.length < 20) {
          hasMoreHistory.value = false;
        }
      } else {
        hasMoreHistory.value = false;
      }
    } catch (error) {
      console.error("載入歷史訊息失敗:", error);
    } finally {
      isLoadingHistory.value = false;
    }
  }

  // 記錄當前滾動位置
  lastScrollTop.value = container.scrollTop;
};

/** 切換頻道時載入訊息並滾到底 */
watch(
  activeChannel,
  async (newChannel) => {
    if (newChannel?.id) {
      // 重置歷史訊息載入狀態
      isLoadingHistory.value = false;
      hasMoreHistory.value = true;
      lastScrollTop.value = 0;
      showScrollToBottom.value = false; // 重置跳到底部按鈕

      await channelStore.fetchChannelMessages(newChannel.id);
      scrollToBottom(false); // 切換頻道時立即跳到底部
    }
  },
  { immediate: false }
);

/** 新訊息到達自動滾動 */
watch(
  activeMessages,
  (newMessages, oldMessages) => {
    console.log('activeMessages changed:', {
      newCount: newMessages?.length,
      oldCount: oldMessages?.length,
      hasIncrease: newMessages && oldMessages && newMessages.length > oldMessages.length
    });

    // 只有當訊息數量增加時才滾動到底部（新訊息）
    if (newMessages && oldMessages && newMessages.length > oldMessages.length) {
      // 取得最新訊息
      const latestMessage = newMessages[newMessages.length - 1];
      const isOwnMessage = latestMessage?.sender_id === userStore.userProfile?.user_id;
      
      console.log('New message detected:', {
        latestMessage: latestMessage,
        userProfileId: userStore.userProfile?.user_id,
        isOwnMessage: isOwnMessage
      });
      
      // 如果是自己的訊息，總是滾動到底部
      if (isOwnMessage) {
        console.log('Own message - scrolling to bottom');
        scrollToBottom(true);
      } else {
        // 其他人的訊息，只有在接近底部時才自動滾動
        const container = messagesContainer.value;
        if (container) {
          const scrollFromBottom = container.scrollHeight - (container.scrollTop + container.clientHeight);
          const isNearBottom = scrollFromBottom <= 100;
          
          console.log('Other message - scroll check:', {
            scrollFromBottom,
            isNearBottom,
            willScroll: isNearBottom
          });
          
          if (isNearBottom) {
            scrollToBottom(true);
          }
        }
      }
    } else if (newMessages && !oldMessages) {
      // 初始載入時立即跳到底部
      console.log('Initial load - scrolling to bottom');
      scrollToBottom(false);
    }
  },
  { deep: true }
);

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
  scrollToBottom(false); // 頁面載入時立即跳到底部
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
  flex: 1;
  height: 100vh;
  border-radius: 0;
  flex-direction: column;
}

/* 關鍵修復：確保 PrimeVue Card 的完整 flex 鏈 */
.chat-area-card :deep(.p-card) {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
}

.chat-area-card :deep(.p-card-body) {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  padding: 0;
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
  min-height: 0; /* 關鍵修復：確保 flex 子元素可以收縮 */
  background: aliceblue;
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
  overflow-x: hidden;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-height: 0; /* 關鍵修復：確保可以滾動 */
  max-height: 100%; /* 確保不會超出容器 */
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

/* 訊息列表容器 */
.messages-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  flex-shrink: 0; /* 防止壓縮，讓內容可以滾動 */
  background-color: aliceblue;
}

/* 歷史訊息載入指示器 */
.history-loading-indicator {
  display: flex;
  justify-content: center;
  padding: 1rem;
  margin-bottom: 0.5rem;
}

.loading-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: var(--surface-100);
  border-radius: 1rem;
  border: 1px solid var(--surface-border);
}

.loading-icon {
  font-size: 0.875rem;
  color: var(--primary-color);
}

.loading-text {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
  font-style: italic;
}

/* 沒有更多歷史訊息提示 */
.no-more-history {
  display: flex;
  justify-content: center;
  padding: 0.75rem 1rem;
  margin-bottom: 0.5rem;
}

.no-more-text {
  font-size: 0.75rem;
  color: var(--text-color-secondary);
  opacity: 0.7;
  font-style: italic;
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

/* 跳到底部按鈕 */
.scroll-to-bottom-container {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  z-index: 10;
}

.scroll-to-bottom-btn {
  background: var(--surface-0) !important;
  border: 1px solid var(--surface-border) !important;
  box-shadow: var(--shadow-3) !important;
  color: var(--text-color) !important;
  transition: all 0.2s ease !important;
}

.scroll-to-bottom-btn:hover {
  background: var(--surface-100) !important;
  transform: translateY(-2px) !important;
  box-shadow: var(--shadow-4) !important;
}

.scroll-to-bottom-btn:active {
  transform: translateY(0) !important;
  box-shadow: var(--shadow-2) !important;
}

/* 跳到底部按鈕動畫 */
.scroll-to-bottom-enter-active,
.scroll-to-bottom-leave-active {
  transition: all 0.3s ease;
}

.scroll-to-bottom-enter-from {
  opacity: 0;
  transform: translateY(20px) scale(0.8);
}

.scroll-to-bottom-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.8);
}

.scroll-to-bottom-enter-to,
.scroll-to-bottom-leave-from {
  opacity: 1;
  transform: translateY(0) scale(1);
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

  .loading-content {
    background: var(--surface-700);
    border-color: var(--surface-600);
  }

  .scroll-to-bottom-btn {
    background: var(--surface-800) !important;
    border-color: var(--surface-600) !important;
  }

  .scroll-to-bottom-btn:hover {
    background: var(--surface-700) !important;
  }
}
</style>
