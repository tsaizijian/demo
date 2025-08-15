<template>
  <div class="chat-input-area w-full max-w-none">
    <!-- 輸入框和傳送按鈕在同一行 -->
    <div class="flex items-end w-full max-w-none">
      <!-- 輸入框 -->
      <div class="input-container">
        <textarea
          ref="textareaRef"
          v-model="messageText"
          class="chat-input"
          placeholder="輸入訊息..."
          @keydown="handleKeydown"
          @input="handleInput"
          @focus="handleFocus"
          @blur="handleBlur"
          rows="1.5"
          :disabled="sending"
        ></textarea>
      </div>

      <!-- 傳送按鈕 -->
      <button
        class="send-button"
        :disabled="!canSend || sending"
        @click="handleSend"
      >
        <i
          v-if="sending"
          class="pi pi-spin pi-spinner"
          style="font-size: 1rem"
        ></i>
        <i v-else class="pi pi-send" style="font-size: 1rem"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from "vue";
import { useChannelStore } from "~/stores/channel";
import { useSocket } from "~/composables/useSocket";

const channelStore = useChannelStore();
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
      const success = socketSendMessage(text, channelStore.currentChannelId);
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
      // 降級為REST API，傳遞當前頻道ID
      const result = await channelStore.sendMessage(
        text,
        undefined,
        channelStore.currentChannelId
      );
      if (result.success) {
        messageText.value = "";
        // 停止輸入狀態
        isTyping.value = false;
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
      }
      isTyping.value = true;
    }

    // 重置計時器
    clearTimeout(typingTimer);
    typingTimer = setTimeout(() => {
      if (isTyping.value) {
        if (isConnected()) {
          setTyping(false);
        }
        isTyping.value = false;
      }
    }, 3000); // 3秒後停止輸入狀態
  } else {
    if (isTyping.value) {
      if (isConnected()) {
        setTyping(false);
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
  background: var(--surface-0);
  width: 100%;
  max-width: none !important;
  box-sizing: border-box;
  border-top: 1px solid var(--surface-border);
}

.input-container {
  padding: 0 0.5rem 0 0;
  width: 85%;
}

.chat-input {
  width: 100%;
  padding: 0.75rem 1rem;
  max-width: none;
  border: 1px solid gray;
  border-radius: 1rem;
  min-height: 48px;
  max-height: 120px;
  resize: none;
  outline: none;
  font-family: inherit;
  font-size: 0.875rem;
  line-height: 1.5;
  overflow-y: auto;
  box-sizing: border-box;
  background: var(--surface-0);
  color: var(--text-color);
  transition: border-color 0.2s ease;
}

.chat-input:focus {
  border-color: var(--primary-color) !important;
  box-shadow: 0 0 0 1px var(--primary-color);
}

.chat-input::placeholder {
  color: var(--text-color-secondary);
  opacity: 0.7;
}

.send-button {
  width: 2.75rem;
  padding: 0;
  margin: 0 0 0.5rem 0;
  height: 2.75rem;
  border-radius: 0.75rem;
  background: aliceblue;
  color: var(--primary-color-text);
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  align-self: flex-end;
  box-shadow: var(--shadow-1);
}

.send-button:hover:not(:disabled) {
  background: var(--primary-600);
  transform: translateY(-1px);
  box-shadow: var(--shadow-2);
}

.send-button:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: var(--shadow-1);
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 暗色主題支援 */
@media (prefers-color-scheme: dark) {
  .chat-input {
    background: var(--surface-800);
    border-color: var(--surface-600);
  }

  .chat-input:focus {
    border-color: var(--primary-400);
    box-shadow: 0 0 0 1px var(--primary-400);
  }
}
</style>
