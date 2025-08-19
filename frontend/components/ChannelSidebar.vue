<template>
  <Card class="channel-sidebar-card">
    <!-- 頻道側邊欄標題 -->
    <template #header>
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-semibold">頻道列表</h2>
        <div class="flex items-center gap-2">
          <Button
            @click="showJoinDialog = true"
            icon="pi pi-sign-in"
            text
            size="small"
            severity="secondary"
            v-tooltip="'加入頻道'"
          />
          <Button
            @click="showCreateDialog = true"
            icon="pi pi-plus"
            text
            size="small"
            v-tooltip="'建立新頻道'"
          />
        </div>
      </div>
    </template>

    <!-- 頻道列表 -->
    <template #content>
      <div class="flex-1 overflow-y-auto px-0">
        <!-- 公開頻道 -->
        <div class="px-3 py-2">
          <h3
            class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-2"
          >
            公開頻道
          </h3>

          <div class="space-y-0">
            <div
              v-for="channel in channelStore.publicChannels"
              :key="channel.id"
              @click="switchChannel(channel)"
              class="channel-item-tg group flex items-center px-3 py-3 cursor-pointer transition-colors duration-200 border-b border-gray-100"
              :class="{
                'bg-blue-50': channel.id === channelStore.currentChannelId,
                'hover:bg-gray-50':
                  channel.id !== channelStore.currentChannelId,
              }"
            >
              <!-- 頻道頭像 -->
              <div
                class="w-12 h-12 rounded-full bg-blue-500 flex items-center justify-center text-white font-medium text-sm flex-shrink-0 mr-3"
              >
                {{ channel.name.charAt(0).toUpperCase() }}
              </div>

              <!-- 主要內容區域 -->
              <div class="flex-1 min-w-0">
                <!-- 頻道名稱和時間戳 -->
                <div class="flex items-center justify-between mb-1">
                  <h3
                    class="font-semibold text-gray-900 truncate text-base"
                    style="margin-right: 0.25rem"
                  >
                    {{ channel.name }}
                  </h3>
                  <span
                    v-if="channel.lastMessage?.created_on"
                    class="text-xs text-gray-500 flex-shrink-0 ml-2"
                  >
                    {{ formatTime(channel.lastMessage.created_on) }}
                  </span>
                </div>

                <!-- 最新訊息 -->
                <div class="flex items-center justify-between">
                  <div class="text-sm text-gray-600 truncate flex-1">
                    <template v-if="channel.lastMessage">
                      <span class="font-medium text-gray-700">
                        {{ channel.lastMessage.sender_name }}:
                      </span>
                      <span class="ml-1">
                        {{ channel.lastMessage.content }}
                      </span>
                    </template>
                    <span v-else class="text-gray-400 italic">
                      {{ channel.description || "尚無訊息" }}
                    </span>
                  </div>

                  <!-- 頻道設定按鈕 -->
                  <div
                    v-if="canDeleteChannel(channel)"
                    class="ml-2 opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <Button
                      @click.stop="toggleChannelMenu(channel, $event)"
                      icon="pi pi-cog"
                      text
                      size="small"
                      class="channel-menu-button"
                      :data-channel-id="channel.id"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 私人頻道 -->
        <div
          v-if="channelStore.privateChannels.length > 0"
          class="px-3 py-2 border-t border-gray-100"
        >
          <h3
            class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-2"
          >
            私人頻道
          </h3>

          <div class="space-y-0">
            <div
              v-for="channel in channelStore.privateChannels"
              :key="channel.id"
              @click="switchChannel(channel)"
              class="channel-item-tg group flex items-center px-3 py-3 cursor-pointer transition-colors duration-200 border-b border-gray-100"
              :class="{
                'bg-blue-50': channel.id === channelStore.currentChannelId,
                'hover:bg-gray-50':
                  channel.id !== channelStore.currentChannelId,
              }"
            >
              <!-- 頻道頭像 (私人頻道使用鎖定圖標) -->
              <div
                class="w-12 h-12 rounded-full bg-gray-500 flex items-center justify-center text-white font-medium text-sm flex-shrink-0 mr-3"
              >
                <i class="pi pi-lock text-xl"></i>
              </div>

              <!-- 主要內容區域 -->
              <div class="flex-1 min-w-0">
                <!-- 頻道名稱和時間戳 -->
                <div class="flex items-center justify-between mb-1">
                  <h3
                    class="font-semibold text-gray-900 truncate text-base"
                    style="margin-right: 0.25rem"
                  >
                    {{ channel.name }}
                  </h3>
                  <span
                    v-if="channel.lastMessage?.created_on"
                    class="text-xs text-gray-500 flex-shrink-0 ml-2"
                  >
                    {{ formatTime(channel.lastMessage.created_on) }}
                  </span>
                </div>

                <!-- 最新訊息 -->
                <div class="flex items-center justify-between">
                  <div class="text-sm text-gray-600 truncate flex-1">
                    <template v-if="channel.lastMessage">
                      <span class="font-medium text-gray-700">
                        {{ channel.lastMessage.sender_name }}:
                      </span>
                      <span class="ml-1">
                        {{ channel.lastMessage.content }}
                      </span>
                    </template>
                    <span v-else class="text-gray-400 italic">
                      {{ channel.description || "尚無訊息" }}
                    </span>
                  </div>

                  <!-- 頻道設定按鈕 -->
                  <div
                    v-if="canDeleteChannel(channel)"
                    class="ml-2 opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <Button
                      @click.stop="toggleChannelMenu(channel, $event)"
                      icon="pi pi-cog"
                      text
                      size="small"
                      class="channel-menu-button"
                      :data-channel-id="channel.id"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- 載入狀態 -->
    <template #footer v-if="channelStore.loading">
      <div class="flex items-center justify-center p-4">
        <ProgressSpinner style="width: 32px; height: 32px" strokeWidth="4" />
        <span class="ml-2 text-sm">載入中...</span>
      </div>
    </template>

    <!-- 錯誤提示 -->
    <Message
      v-if="channelStore.error"
      severity="error"
      :closable="true"
      @close="channelStore.clearError()"
      class="m-2"
    >
      {{ channelStore.error }}
    </Message>
  </Card>

  <!-- 頻道設定選單 -->
  <Popover ref="channelMenuPanel" class="channel-menu-panel">
    <div class="channel-menu-content">
      <div class="menu-header">
        <h4 class="text-sm font-semibold text-gray-700 mb-2">頻道設定</h4>
      </div>
      <Button
        @click="editChannel"
        icon="pi pi-pencil"
        label="編輯頻道"
        text
        size="small"
        class="w-full justify-start"
      />
      <Button
        @click="confirmDeleteChannel"
        icon="pi pi-trash"
        label="刪除頻道"
        text
        size="small"
        severity="danger"
        class="w-full justify-start"
      />
    </div>
  </Popover>

  <!-- 刪除確認對話框 -->
  <ConfirmPopup />

  <!-- 加入頻道對話框 -->
  <JoinChannelDialog
    v-model:visible="showJoinDialog"
    @joined="handleChannelJoined"
  />

  <!-- 頻道設定對話框 -->
  <ChannelSettingsDialog
    v-model:visible="showSettingsDialog"
    :channel="selectedChannelForSettings"
    @updated="handleChannelUpdated"
  />

  <!-- 建立頻道對話框 -->
  <CreateChannelDialog
    v-model:visible="showCreateDialog"
    @created="handleChannelCreated"
  />
</template>

<script setup>
import { useChannelStore } from "~/stores/channel";
import { useUserStore } from "~/stores/user";
import { useConfirm } from "primevue/useconfirm";
import { useToast } from "primevue/usetoast";
import JoinChannelDialog from "./JoinChannelDialog.vue";
import ChannelSettingsDialog from "./ChannelSettingsDialog.vue";
import CreateChannelDialog from "./CreateChannelDialog.vue";

// 不再需要 emit 事件，直接操作 store

const channelStore = useChannelStore();
const userStore = useUserStore();
const confirm = useConfirm();
const toast = useToast();

// refs
const channelMenuPanel = ref(null);
let selectedChannelForMenu = ref(null);

// 對話框狀態
const showJoinDialog = ref(false);
const showSettingsDialog = ref(false);
const showCreateDialog = ref(false);
const selectedChannelForSettings = ref(null);

// 組件方法
const switchChannel = async (channel) => {
  if (channel.id === channelStore.currentChannelId) return;

  console.log(`切換到頻道: ${channel.name}`);
  const result = await channelStore.switchChannel(channel.id);

  if (!result.success) {
    console.error("切換頻道失敗:", result.error);
  }
};

const openChannelSettings = (channel) => {
  channelStore.openChannelSettings(channel);
};

const getChannelMemberCount = (channelId) => {
  const members = channelStore.channelMembers[channelId];
  return members ? members.length : 0;
};

const isChannelAdmin = (channelId) => {
  if (!userStore.currentUser) return false;

  const members = channelStore.channelMembers[channelId] || [];
  const member = members.find((m) => m.user_id === userStore.currentUser?.id);

  return member?.role === "admin" || member?.role === "owner";
};

// 檢查是否可以刪除頻道
const canDeleteChannel = (channel) => {
  console.log("檢查頻道刪除權限:", {
    channel: channel,
    userProfile: userStore.userProfile,
    creator_id: channel.creator_id,
    user_id: userStore.userProfile?.user_id,
    canDelete: channelStore.canDeleteChannel(channel),
  });
  return channelStore.canDeleteChannel(channel);
};

// 切換頻道選單
const toggleChannelMenu = (channel, event) => {
  selectedChannelForMenu.value = channel;
  channelMenuPanel.value.toggle(event);
};

// 編輯頻道
const editChannel = () => {
  if (selectedChannelForMenu.value) {
    selectedChannelForSettings.value = selectedChannelForMenu.value;
    showSettingsDialog.value = true;
    channelMenuPanel.value.hide();
  }
};

// 確認刪除頻道
const confirmDeleteChannel = () => {
  if (!selectedChannelForMenu.value) return;

  const channel = selectedChannelForMenu.value;

  confirm.require({
    target: event.currentTarget,
    message: `確定要刪除頻道「${channel.name}」嗎？`,
    header: "刪除頻道",
    icon: "pi pi-exclamation-triangle",
    acceptLabel: "刪除",
    rejectLabel: "取消",
    acceptClass: "p-button-danger",
    accept: async () => {
      await deleteChannel(channel.id);
    },
    reject: () => {
      channelMenuPanel.value.hide();
    },
  });
};

// 刪除頻道
const deleteChannel = async (channelId) => {
  try {
    const result = await channelStore.deleteChannel(channelId);

    if (result.success) {
      toast.add({
        severity: "success",
        summary: "成功",
        detail: "頻道已成功刪除",
        life: 3000,
      });
    } else {
      toast.add({
        severity: "error",
        summary: "錯誤",
        detail: result.error || "刪除頻道失敗",
        life: 5000,
      });
    }
  } catch (error) {
    console.error("刪除頻道時發生錯誤:", error);
    toast.add({
      severity: "error",
      summary: "錯誤",
      detail: "刪除頻道時發生未知錯誤",
      life: 5000,
    });
  } finally {
    channelMenuPanel.value.hide();
  }
};

// 時間格式化方法 - 針對聊天頻道列表優化
const formatTime = (dateString) => {
  if (!dateString) return "";

  const date = new Date(dateString);
  const now = new Date();
  const diff = now - date;

  // 小於1分鐘
  if (diff < 60 * 1000) {
    return "剛剛";
  }

  // 小於1小時，顯示分鐘
  if (diff < 60 * 60 * 1000) {
    const minutes = Math.floor(diff / (60 * 1000));
    return `${minutes}分鐘前`;
  }

  // 如果是今天，顯示時間
  if (diff < 24 * 60 * 60 * 1000 && date.getDate() === now.getDate()) {
    return date.toLocaleTimeString("zh-TW", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    });
  }

  // 如果是昨天
  const yesterday = new Date(now);
  yesterday.setDate(yesterday.getDate() - 1);
  if (
    date.getDate() === yesterday.getDate() &&
    date.getMonth() === yesterday.getMonth() &&
    date.getFullYear() === yesterday.getFullYear()
  ) {
    return "昨天";
  }

  // 如果是一週內
  if (diff < 7 * 24 * 60 * 60 * 1000) {
    const days = ["週日", "週一", "週二", "週三", "週四", "週五", "週六"];
    return days[date.getDay()];
  }

  // 其他情況顯示日期
  return date.toLocaleDateString("zh-TW", {
    month: "numeric",
    day: "numeric",
  });
};

// 對話框事件處理
const handleChannelJoined = () => {
  // 重新載入頻道列表
  channelStore.fetchChannels();
};

const handleChannelUpdated = () => {
  // 重新載入頻道列表
  channelStore.fetchChannels();
};

const handleChannelCreated = () => {
  // 重新載入頻道列表
  channelStore.fetchChannels();
};

// 載入頻道資料
onMounted(async () => {
  console.log("ChannelSidebar mounted, 載入頻道資料...");
  await channelStore.fetchChannels();

  // 載入當前頻道的成員
  if (channelStore.currentChannelId) {
    await channelStore.fetchChannelMembers(channelStore.currentChannelId);
  }
});
</script>

<style scoped>
/* 頻道側邊欄卡片樣式 */
.channel-sidebar-card {
  height: auto;
  border: 0;
  border-radius: 0;
  border-right: 1px solid var(--surface-border);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.channel-sidebar-card :deep(.p-card-header) {
  background: var(--surface-50);
  border-bottom: 1px solid var(--surface-border);
  padding: 1rem;
}

.channel-sidebar-card :deep(.p-card-content) {
  padding: 0;
  height: calc(100% - 80px);
  overflow: hidden;
}

.channel-sidebar-card :deep(.p-card-footer) {
  background: var(--surface-50);
  border-top: 1px solid var(--surface-border);
  padding: 0.75rem 1rem;
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

/* TG 風格頻道項目 */
.channel-item-tg {
  margin: 0 !important;
  padding: 16px 16px !important;
  border-radius: 0 !important;
  transform: none !important;
  background: transparent !important;
  min-height: 72px;
  transition: all 0.2s ease;
}

.channel-item-tg:hover {
  background: var(--surface-100) !important;
  transform: none !important;
}

.channel-item-tg.bg-blue-50 {
  background: var(--primary-50) !important;
  border-left: 3px solid var(--primary-color);
}

/* 頻道項目的懸停效果 */
.group:hover .opacity-0 {
  opacity: 1;
}

/* 訊息內容樣式 */
.channel-item-tg .text-sm {
  line-height: 1.4;
  color: var(--text-color-secondary);
}

/* 時間戳樣式 */
.channel-item-tg .text-xs {
  font-weight: 500;
  letter-spacing: 0.025em;
  color: var(--text-color-secondary);
}

/* 頻道名稱樣式 */
.channel-item-tg h3 {
  color: var(--text-color);
  font-weight: 600;
}

/* 區段標題樣式 */
.text-gray-400 {
  color: var(--text-color-secondary) !important;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* 線上使用者區域 */
.max-h-32 {
  scrollbar-width: thin;
  scrollbar-color: var(--surface-300) transparent;
}

/* 動畫效果 */
.channel-sidebar-card {
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
  .channel-sidebar-card {
    width: 100%;
    max-width: none;
  }
}

/* 暗色主題支援 */
@media (prefers-color-scheme: dark) {
  .channel-item-tg:hover {
    background: var(--surface-700) !important;
  }

  .channel-item-tg.bg-blue-50 {
    background: var(--primary-900) !important;
  }
}

/* 頻道設定選單樣式 */
.channel-menu-panel {
  min-width: 180px;
}

.channel-menu-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 1rem;
}

.menu-header {
  border-bottom: 1px solid var(--surface-200);
  padding-bottom: 0.5rem;
  margin-bottom: 0.5rem;
}

.channel-menu-content .p-button {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  transition: all 0.15s ease;
}

.channel-menu-content .p-button:hover {
  background-color: var(--surface-100);
}

.channel-menu-content .p-button.p-button-danger:hover {
  background-color: var(--red-50);
  color: var(--red-600);
}

.channel-menu-button {
  opacity: 0.7;
  transition: opacity 0.15s ease;
}

.channel-menu-button:hover {
  opacity: 1;
}
</style>
