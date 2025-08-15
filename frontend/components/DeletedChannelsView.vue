<template>
  <Card class="deleted-channels-card">
    <!-- 已刪除頻道標題 -->
    <template #header>
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-semibold">已刪除的頻道</h2>
        <Button
          @click="$emit('close')"
          icon="pi pi-times"
          text
          size="small"
          class="close-button"
        />
      </div>
    </template>

    <!-- 已刪除頻道列表 -->
    <template #content>
      <div class="flex-1 overflow-y-auto px-0">
        <!-- 載入狀態 -->
        <div v-if="loading" class="flex items-center justify-center p-8">
          <ProgressSpinner style="width: 32px; height: 32px" strokeWidth="4" />
          <span class="ml-2 text-sm">載入中...</span>
        </div>

        <!-- 空狀態 -->
        <div v-else-if="deletedChannels.length === 0" class="empty-state">
          <div class="text-center py-12">
            <i class="pi pi-trash text-4xl text-gray-300 mb-4"></i>
            <h3 class="text-lg font-medium text-gray-600 mb-2">沒有已刪除的頻道</h3>
            <p class="text-sm text-gray-400">您目前沒有任何已刪除的頻道</p>
          </div>
        </div>

        <!-- 已刪除頻道列表 -->
        <div v-else class="px-3 py-2">
          <div class="space-y-2">
            <div
              v-for="channel in deletedChannels"
              :key="channel.id"
              class="deleted-channel-item group flex items-center px-3 py-3 border border-gray-200 rounded-lg"
            >
              <!-- 頻道頭像 -->
              <div
                class="w-12 h-12 rounded-full bg-gray-400 flex items-center justify-center text-white font-medium text-sm flex-shrink-0 mr-3"
              >
                {{ channel.name.charAt(0).toUpperCase() }}
              </div>

              <!-- 主要內容區域 -->
              <div class="flex-1 min-w-0">
                <!-- 頻道名稱和刪除時間 -->
                <div class="flex items-center justify-between mb-1">
                  <h3 class="font-semibold text-gray-900 truncate text-base">
                    {{ channel.name }}
                  </h3>
                  <span class="text-xs text-gray-500 flex-shrink-0 ml-2">
                    {{ formatDeletedTime(channel.changed_on) }}
                  </span>
                </div>

                <!-- 頻道描述 -->
                <div class="flex items-center justify-between">
                  <div class="text-sm text-gray-600 truncate flex-1">
                    <span v-if="channel.description" class="text-gray-500">
                      {{ channel.description }}
                    </span>
                    <span v-else class="text-gray-400 italic">無描述</span>
                  </div>

                  <!-- 恢復按鈕 -->
                  <Button
                    @click.stop="confirmRestoreChannel(channel)"
                    icon="pi pi-undo"
                    label="恢復"
                    text
                    size="small"
                    severity="success"
                    class="ml-2 opacity-0 group-hover:opacity-100 transition-opacity"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- 載入狀態 -->
    <template #footer v-if="loading">
      <div class="flex items-center justify-center p-4">
        <ProgressSpinner style="width: 24px; height: 24px" strokeWidth="4" />
        <span class="ml-2 text-sm">載入中...</span>
      </div>
    </template>

    <!-- 錯誤提示 -->
    <Message
      v-if="error"
      severity="error"
      :closable="true"
      @close="clearError"
      class="m-2"
    >
      {{ error }}
    </Message>
  </Card>

  <!-- 恢復確認對話框 -->
  <ConfirmPopup />
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useChannelStore } from "~/stores/channel";
import { useConfirm } from "primevue/useconfirm";
import { useToast } from "primevue/usetoast";

// 定義事件
const emit = defineEmits(["close"]);

// Store 和組合式函數
const channelStore = useChannelStore();
const confirm = useConfirm();
const toast = useToast();

// 狀態
const deletedChannels = ref([]);
const loading = ref(false);
const error = ref(null);

// 載入已刪除頻道
const loadDeletedChannels = async () => {
  loading.value = true;
  error.value = null;

  try {
    const result = await channelStore.fetchDeletedChannels();
    if (result.success) {
      deletedChannels.value = result.data || [];
    } else {
      error.value = result.error || "載入已刪除頻道失敗";
    }
  } catch (err) {
    console.error("載入已刪除頻道時發生錯誤:", err);
    error.value = "載入已刪除頻道時發生未知錯誤";
  } finally {
    loading.value = false;
  }
};

// 確認恢復頻道
const confirmRestoreChannel = (channel) => {
  confirm.require({
    target: event.currentTarget,
    message: `確定要恢復頻道「${channel.name}」嗎？`,
    header: "恢復頻道",
    icon: "pi pi-question-circle",
    acceptLabel: "恢復",
    rejectLabel: "取消",
    acceptClass: "p-button-success",
    accept: async () => {
      await restoreChannel(channel.id);
    }
  });
};

// 恢復頻道
const restoreChannel = async (channelId) => {
  try {
    const result = await channelStore.restoreChannel(channelId);

    if (result.success) {
      toast.add({
        severity: "success",
        summary: "成功",
        detail: "頻道已成功恢復",
        life: 3000
      });
      
      // 重新載入已刪除頻道列表
      await loadDeletedChannels();
    } else {
      toast.add({
        severity: "error",
        summary: "錯誤",
        detail: result.error || "恢復頻道失敗",
        life: 5000
      });
    }
  } catch (err) {
    console.error("恢復頻道時發生錯誤:", err);
    toast.add({
      severity: "error",
      summary: "錯誤",
      detail: "恢復頻道時發生未知錯誤",
      life: 5000
    });
  }
};

// 清除錯誤
const clearError = () => {
  error.value = null;
};

// 格式化刪除時間
const formatDeletedTime = (dateString) => {
  if (!dateString) return "";

  const date = new Date(dateString);
  const now = new Date();
  const diff = now - date;

  // 小於1小時
  if (diff < 60 * 60 * 1000) {
    const minutes = Math.floor(diff / (60 * 1000));
    return `${minutes}分鐘前刪除`;
  }

  // 小於24小時
  if (diff < 24 * 60 * 60 * 1000) {
    const hours = Math.floor(diff / (60 * 60 * 1000));
    return `${hours}小時前刪除`;
  }

  // 其他情況顯示日期
  return `${date.toLocaleDateString("zh-TW")}刪除`;
};

// 組件掛載時載入資料
onMounted(() => {
  loadDeletedChannels();
});
</script>

<style scoped>
/* 已刪除頻道卡片樣式 */
.deleted-channels-card {
  height: auto;
  border: 0;
  border-radius: 0;
  border-right: 1px solid var(--surface-border);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.deleted-channels-card :deep(.p-card-header) {
  background: var(--red-50);
  border-bottom: 1px solid var(--surface-border);
  padding: 1rem;
  color: var(--red-700);
}

.deleted-channels-card :deep(.p-card-content) {
  padding: 0;
  height: calc(100% - 80px);
  overflow: hidden;
}

.deleted-channels-card :deep(.p-card-footer) {
  background: var(--surface-50);
  border-top: 1px solid var(--surface-border);
  padding: 0.75rem 1rem;
}

/* 關閉按鈕樣式 */
.close-button {
  background: rgba(239, 68, 68, 0.1) !important;
  color: var(--red-600) !important;
  border: none !important;
}

.close-button:hover {
  background: rgba(239, 68, 68, 0.2) !important;
  transform: scale(1.05);
}

/* 已刪除頻道項目樣式 */
.deleted-channel-item {
  background: var(--surface-0);
  border-color: var(--red-200);
  transition: all 0.2s ease;
}

.deleted-channel-item:hover {
  background: var(--red-25);
  border-color: var(--red-300);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.1);
}

/* 空狀態樣式 */
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

/* 頻道項目的懸停效果 */
.group:hover .opacity-0 {
  opacity: 1;
}

/* 自訂滾動條樣式 */
.overflow-y-auto::-webkit-scrollbar {
  width: 4px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: var(--surface-300);
  border-radius: 4px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: var(--surface-400);
}

/* 動畫效果 */
.deleted-channels-card {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* 響應式設計 */
@media (max-width: 768px) {
  .deleted-channels-card {
    width: 100%;
    max-width: none;
  }
}

/* 暗色主題支援 */
@media (prefers-color-scheme: dark) {
  .deleted-channel-item:hover {
    background: var(--red-900);
    border-color: var(--red-700);
  }

  .deleted-channels-card :deep(.p-card-header) {
    background: var(--red-900);
    color: var(--red-200);
  }
}
</style>