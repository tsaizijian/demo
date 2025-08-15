<template>
  <div
    class="message"
    :class="{
      own: isOwnMessage,
      other: !isOwnMessage,
    }"
  >
    <!-- 發送者名稱（僅對方消息顯示） -->
    <div v-if="!isOwnMessage && showSenderName" class="sender-name">
      {{ message.sender_name }}
    </div>

    <div
      class="message-bubble"
      :class="{
        own: isOwnMessage,
        other: !isOwnMessage,
      }"
      @contextmenu.prevent="(event) => showContextMenu(event, message.id)"
    >
      <!-- 消息內容 -->
      <div class="message-content">
        {{ message.content }}
      </div>
    </div>

    <!-- 右鍵選單 -->
    <Menu
      v-if="isMenuVisible(message.id)"
      ref="contextMenu"
      :model="contextMenuItems"
      :popup="true"
      class="message-context-menu"
      :style="contextMenuState.position"
      @click.stop
    />

    <!-- 時間戳 -->
    <div
      class="message-time"
      :class="{
        own: isOwnMessage,
        other: !isOwnMessage,
      }"
      :title="detailedTime"
      v-tooltip.top="detailedTime"
    >
      {{ formattedTime }}
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from "vue";
import { useChannelStore } from "~/stores/channel";
import { useUserStore } from "~/stores/user";
import { useSocket } from "~/composables/useSocket";
import { useContextMenu } from "~/composables/useContextMenu";
import { formatLocalTime, getDetailedTime } from "~/utils/timeUtils";
import { useTimeUpdate } from "~/composables/useTimeUpdate";

const props = defineProps({
  message: {
    type: Object,
    required: true,
  },
  showSenderName: {
    type: Boolean,
    default: true,
  },
});

const channelStore = useChannelStore();
const userStore = useUserStore();
const { deleteMessage: socketDeleteMessage, isConnected } = useSocket();
const { contextMenuState, showContextMenu, hideContextMenu, isMenuVisible } =
  useContextMenu();

// 右鍵選單項目
const contextMenuItems = computed(() => {
  const items = [
    {
      label: "回覆",
      icon: "pi pi-reply",
      command: handleReply,
    },
  ];

  if (canDeleteMessage.value) {
    items.push({
      label: "刪除",
      icon: "pi pi-trash",
      command: handleDelete,
      class: "text-red-600",
    });
  }

  return items;
});
const { updateTrigger } = useTimeUpdate(30000); // 每 30 秒更新一次

const isOwnMessage = computed(() => {
  return props.message.sender_id === userStore.userProfile?.user_id;
});

const canDeleteMessage = computed(() => {
  return isOwnMessage.value;
});

const formattedTime = computed(() => {
  // 使用 updateTrigger 來觸發重新計算
  updateTrigger.value;
  return formatLocalTime(props.message.created_on);
});

const detailedTime = computed(() => {
  updateTrigger.value;
  return getDetailedTime(props.message.created_on);
});

const handleDelete = async () => {
  hideContextMenu();
  if (confirm("確定要刪除這則訊息嗎？")) {
    if (isConnected()) {
      socketDeleteMessage(props.message.id);
    } else {
      await channelStore.deleteMessage(props.message.id);
    }
  }
};

const handleReply = () => {
  hideContextMenu();
  // TODO: 實現回覆功能
  alert("回覆功能開發中...");
};

// 監聽點擊事件關閉選單
const handleGlobalClick = (event) => {
  const contextMenu = event.target.closest(".message-context-menu");
  if (!contextMenu) {
    hideContextMenu();
  }
};

onMounted(() => {
  document.addEventListener("click", handleGlobalClick);
  document.addEventListener("scroll", hideContextMenu);
});

onUnmounted(() => {
  document.removeEventListener("click", handleGlobalClick);
  document.removeEventListener("scroll", hideContextMenu);
});
</script>

<style scoped>
.message {
  max-width: 20rem;
  position: relative;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .message {
    max-width: 100%;
    margin: 0 0.5rem;
  }

  .message-bubble {
    padding: 0.625rem 0.875rem;
    font-size: 0.875rem;
  }

  .message-time {
    font-size: 0.6875rem;
  }

  .sender-name {
    font-size: 0.6875rem;
  }

  .message-context-menu :deep(.p-menu) {
    min-width: 120px;
  }

  .message-context-menu :deep(.p-menuitem-link) {
    padding: 0.5rem 0.75rem;
    font-size: 0.8125rem;
  }
}

@media (min-width: 768px) {
  .message {
    max-width: 28rem;
  }
}

@media (min-width: 1024px) {
  .message {
    max-width: 32rem;
  }
}

.message.own {
  margin-left: auto;
}

.message.other {
  margin-right: auto;
}

.message-bubble {
  padding: 0.75rem 1rem;
  border-radius: 1rem;
  box-shadow: var(--shadow-1);
  position: relative;
  transition: all 0.2s ease;
  backdrop-filter: blur(10px);
}

.message-bubble:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-2);
}

.message-bubble.own {
  color: var(--primary-color-text);
  border-bottom-right-radius: 0.375rem;
  background-color: white;
}

.message-bubble.other {
  background: white;
  color: var(--text-color);
  border: 1px solid;
  border-bottom-left-radius: 0.375rem;
}

.message-time {
  font-size: 0.75rem;
  opacity: 0.7;
  margin-top: 0.25rem;
}

.message-time.own {
  text-align: right;
  color: var(--text-color-secondary);
}

.message-time.other {
  text-align: left;
  color: var(--text-color-secondary);
}

/* PrimeVue Menu 自定義樣式 */
.message-context-menu {
  position: fixed !important;
  z-index: 1000;
  animation: contextMenuFadeIn 0.15s ease-out;
}

.message-context-menu :deep(.p-menu) {
  background: var(--surface-0);
  border: 1px solid var(--surface-border);
  border-radius: 0.5rem;
  box-shadow: var(--shadow-2);
  padding: 0.5rem;
  min-width: 140px;
}

.message-context-menu :deep(.p-menuitem-link) {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: all 0.15s ease;
  font-size: 0.875rem;
  border-radius: 0.375rem;
  color: var(--text-color);
}

.message-context-menu :deep(.p-menuitem-link:hover) {
  background-color: var(--surface-100);
}

.message-context-menu :deep(.p-menuitem-link.text-red-600) {
  color: var(--red-500);
}

.message-context-menu :deep(.p-menuitem-link.text-red-600:hover) {
  background-color: var(--red-50);
  color: var(--red-600);
}

.message-context-menu :deep(.p-menuitem-icon) {
  width: 1rem;
  height: 1rem;
}
.context-menu-icon {
  width: 1rem;
  height: 1rem;
  color: var(--text-color);
}

.context-menu-item {
  color: var(--text-color);
  transition: all 0.15s ease;
}

.context-menu-item.text-red-600 {
  color: var(--red-500);
}

.context-menu-item.text-red-600:hover {
  background-color: var(--red-50);
  color: var(--red-600);
}

.sender-name {
  font-size: 0.75rem;
  font-weight: 600;
  margin-bottom: 0.375rem;
  margin-left: 0.5rem;
  color: var(--text-color-secondary);
  opacity: 0.8;
}

@keyframes contextMenuFadeIn {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(-5px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* 訊息動畫 */
.message {
  animation: messageSlideIn 0.3s ease-out;
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 暗色主題支援 */
@media (prefers-color-scheme: dark) {
  .message-bubble.other {
    background: var(--surface-700);
    border-color: var(--surface-600);
  }

  .message-context-menu :deep(.p-menu) {
    background: var(--surface-800);
    border-color: var(--surface-600);
  }

  .message-context-menu :deep(.p-menuitem-link:hover) {
    background-color: var(--surface-700);
  }

  .message-context-menu :deep(.p-menuitem-link.text-red-600:hover) {
    background-color: var(--red-900);
    color: var(--red-400);
  }
}
</style>
