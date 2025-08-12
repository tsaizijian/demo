<template>
  <div class="chat-input-area">
    <!-- 輸入框和傳送按鈕在同一行 -->
    <div class="flex">
      <!-- 輸入框 -->
      <div class="flex-1">
        <textarea
          ref="textareaRef"
          v-model="messageText"
          class="chat-input w-full"
          placeholder="輸入訊息..."
          @keydown="handleKeydown"
          @input="handleInput"
          @focus="handleFocus"
          @blur="handleBlur"
          rows="1"
          :disabled="sending"
        ></textarea>
      </div>

      <!-- 傳送按鈕 -->
      <button
        class="send-button"
        :disabled="!canSend || sending"
        @click="handleSend"
      >
        <svg
          v-if="sending"
          class="w-4 h-4 animate-spin"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path
            d="M4 2a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V4a2 2 0 00-2-2H4z"
          />
        </svg>
        <svg v-else class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path
            d="M2.94 6.412A2 2 0 015.368 4.32L16.06 9.652a1 1 0 010 1.696L5.368 16.68a2 2 0 01-2.428-2.092l.4-3.734a1 1 0 01.985-.878h4.15a.5.5 0 000-1h-4.15a1 1 0 01-.985-.878l-.4-3.734z"
          />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from "vue";
import { useChatStore } from "~/stores/chat";
import { useSocket } from "~/composables/useSocket";

const chatStore = useChatStore();
const { sendMessage: socketSendMessage, setTyping, isConnected } = useSocket();

const messageText = ref("");
const textareaRef = ref(null);
const isTyping = ref(false);
const sending = ref(false);
let typingTimer = null;

const canSend = computed(() => {
  return messageText.value.trim().length > 0;
});

const handleSend = async () => {
  if (!canSend.value || sending.value) return;

  const text = messageText.value.trim();
  sending.value = true;

  try {
    // 優先使用WebSocket發送訊息
    if (isConnected()) {
      const success = socketSendMessage(text);
      if (success) {
        messageText.value = "";
        // 停止輸入狀態
        if (isTyping.value) {
          setTyping(false);
          isTyping.value = false;
        }
        nextTick(() => adjustTextareaHeight());
      }
    } else {
      // 降級為REST API
      const result = await chatStore.sendMessage(text);
      if (result.success) {
        messageText.value = "";
        // 停止輸入狀態
        if (isTyping.value) {
          chatStore.setTyping(false);
          isTyping.value = false;
        }
        nextTick(() => adjustTextareaHeight());
      }
    }
  } finally {
    sending.value = false;
  }
};

const handleKeydown = (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    handleSend();
  }
};

const handleInput = () => {
  adjustTextareaHeight();

  // 處理輸入狀態
  if (messageText.value.trim().length > 0) {
    if (!isTyping.value) {
      if (isConnected()) {
        setTyping(true);
      } else {
        chatStore.setTyping(true);
      }
      isTyping.value = true;
    }

    // 重置計時器
    clearTimeout(typingTimer);
    typingTimer = setTimeout(() => {
      if (isTyping.value) {
        if (isConnected()) {
          setTyping(false);
        } else {
          chatStore.setTyping(false);
        }
        isTyping.value = false;
      }
    }, 3000); // 3秒後停止輸入狀態
  } else {
    if (isTyping.value) {
      if (isConnected()) {
        setTyping(false);
      } else {
        chatStore.setTyping(false);
      }
      isTyping.value = false;
    }
  }
};

const handleFocus = () => {
  // 聚焦時的處理
};

const handleBlur = () => {
  // 失焦時停止輸入狀態
  if (isTyping.value) {
    if (isConnected()) {
      setTyping(false);
    } else {
      chatStore.setTyping(false);
    }
    isTyping.value = false;
  }
};

const adjustTextareaHeight = () => {
  if (textareaRef.value) {
    textareaRef.value.style.height = "auto";
    textareaRef.value.style.height = `${textareaRef.value.scrollHeight}px`;
  }
};

onMounted(() => {
  adjustTextareaHeight();
});
</script>

<style scoped>
.chat-input-area {
  padding: 1rem;
  border-top: 1px solid #e5e7eb;
  background-color: white;
}

.chat-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 9999px;
  min-height: 44px;
  max-height: 120px;
  resize: none;
  outline: none;
  font-family: inherit;
}

.chat-input:focus {
  box-shadow: 0 0 0 2px #3b82f6;
}

.send-button {
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 9999px;
  background: #0088cc;
  color: white;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.send-button:hover:not(:disabled) {
  background: #40a7e3;
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
