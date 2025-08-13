<template>
  <div
    class="message"
    :class="{
      own: isOwnMessage,
      other: !isOwnMessage,
    }"
  >
    <div
      class="message-bubble"
      :class="{
        own: isOwnMessage,
        other: !isOwnMessage,
      }"
      @contextmenu.prevent="(event) => showContextMenu(event, message.id)"
    >
      <!-- 發送者名稱（僅對方消息顯示） -->
      <div
        v-if="!isOwnMessage && showSenderName"
        class="text-xs font-semibold mb-1 opacity-70"
      >
        {{ message.sender_name }}
      </div>

      <!-- 消息內容 -->
      <div class="message-content">
        {{ message.content }}
      </div>
    </div>

    <!-- 右鍵選單 -->
    <div
      v-if="isMenuVisible(message.id)"
      class="context-menu"
      :style="contextMenuState.position"
      @click.stop
    >
      <div class="context-menu-item" @click="handleReply">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"
          />
        </svg>
        <span>回覆</span>
      </div>
      <div
        v-if="canDeleteMessage"
        class="context-menu-item text-red-600"
        @click="handleDelete"
      >
        <svg class="" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
          />
        </svg>
        <span>刪除</span>
      </div>
    </div>

    <!-- 時間戳 -->
    <div
      class="message-time"
      :class="{
        own: isOwnMessage,
        other: !isOwnMessage,
      }"
      :title="detailedTime"
    >
      {{ formattedTime }}
    </div>

    <!-- 點擊遮罩層關閉選單 -->
    <div
      v-if="isMenuVisible(message.id)"
      class="fixed inset-0 z-10"
      @click="hideContextMenu"
    ></div>
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

onMounted(() => {
  document.addEventListener("click", hideContextMenu);
  document.addEventListener("scroll", hideContextMenu);
});

onUnmounted(() => {
  document.removeEventListener("click", hideContextMenu);
  document.removeEventListener("scroll", hideContextMenu);
});
</script>

<style scoped>
.message {
  max-width: 20rem;
  position: relative;
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
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  position: relative;
}

.message-bubble.own {
  background: #0088cc;
  color: white;
  border-bottom-right-radius: 0.375rem;
}

.message-bubble.other {
  background-color: white;
  color: #111827;
  border-bottom-left-radius: 0.375rem;
}

.message-time {
  font-size: 0.75rem;
  opacity: 0.7;
  margin-top: 0.25rem;
}

.message-time.own {
  text-align: right;
  color: #757575;
}

.message-time.other {
  text-align: left;
  color: #757575;
}

.context-menu {
  position: fixed;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
    0 4px 6px -2px rgba(0, 0, 0, 0.05);
  padding: 0.5rem 0;
  min-width: 120px;
  z-index: 50;
  animation: contextMenuFadeIn 0.15s ease-out;
}

.context-menu-item {
  width: 7rem;
  height: 4rem;
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.25rem;
  cursor: pointer;
  transition: background-color 0.15s;
  font-size: 0.875rem;
  white-space: nowrap;
}

.context-menu-item:hover {
  background-color: #f3f4f6;
}

.context-menu-item:active {
  background-color: #e5e7eb;
}
svg {
  width: 3rem;
  height: 3rem;
}

@keyframes contextMenuFadeIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
