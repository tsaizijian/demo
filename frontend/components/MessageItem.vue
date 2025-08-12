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

      <!-- 刪除按鈕 (僅自己的消息) -->
      <button
        v-if="canDeleteMessage"
        @click="handleDelete"
        class="absolute -top-2 -right-2 w-5 h-5 bg-red-500 text-white rounded-full text-xs opacity-0 hover:opacity-100 transition-opacity flex items-center justify-center"
        title="刪除訊息"
      >
        ×
      </button>
    </div>

    <!-- 時間戳 -->
    <div
      class="message-time"
      :class="{
        own: isOwnMessage,
        other: !isOwnMessage,
      }"
    >
      {{ formattedTime }}
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useChatStore } from "~/stores/chat";
import { useUserStore } from "~/stores/user";
import { useSocket } from "~/composables/useSocket";

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

const chatStore = useChatStore();
const userStore = useUserStore();
const { deleteMessage: socketDeleteMessage, isConnected } = useSocket();

const isOwnMessage = computed(() => {
  return props.message.sender_id === userStore.userProfile?.user_id;
});

const canDeleteMessage = computed(() => {
  return isOwnMessage.value;
});

const formattedTime = computed(() => {
  return formatTime(props.message.created_on);
});

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

const handleDelete = async () => {
  if (confirm("確定要刪除這則訊息嗎？")) {
    // 優先使用WebSocket刪除訊息
    if (isConnected()) {
      socketDeleteMessage(props.message.id);
    } else {
      // 降級為REST API
      await chatStore.deleteMessage(props.message.id);
    }
  }
};
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
</style>