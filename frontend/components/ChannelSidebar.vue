<template>
  <aside class="w-64 bg-gray-50 border-r border-gray-200 flex flex-col h-full">
    <!-- 頻道側邊欄標題 -->
    <div class="p-4 border-b border-gray-200 bg-white">
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-semibold text-gray-900">頻道列表</h2>
        <UButton
          @click="channelStore.toggleChannelCreator()"
          variant="ghost"
          size="xs"
          icon="i-heroicons-plus"
          :title="channelStore.showChannelCreator ? '關閉' : '建立新頻道'"
        />
      </div>
    </div>

    <!-- 頻道列表 -->
    <div class="flex-1 overflow-y-auto">
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
              'hover:bg-gray-50': channel.id !== channelStore.currentChannelId,
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
                <h3 class="font-semibold text-gray-900 truncate text-base">
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
                <UButton
                  v-if="isChannelAdmin(channel.id)"
                  @click.stop="openChannelSettings(channel)"
                  size="xs"
                  variant="ghost"
                  icon="i-heroicons-cog-6-tooth"
                  class="ml-2 opacity-0 group-hover:opacity-100 transition-opacity"
                />
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
              'hover:bg-gray-50': channel.id !== channelStore.currentChannelId,
            }"
          >
            <!-- 頻道頭像 (私人頻道使用鎖定圖標) -->
            <div
              class="w-12 h-12 rounded-full bg-gray-500 flex items-center justify-center text-white font-medium text-sm flex-shrink-0 mr-3"
            >
              <UIcon name="i-heroicons-lock-closed" class="w-6 h-6" />
            </div>

            <!-- 主要內容區域 -->
            <div class="flex-1 min-w-0">
              <!-- 頻道名稱和時間戳 -->
              <div class="flex items-center justify-between mb-1">
                <h3 class="font-semibold text-gray-900 truncate text-base">
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
                <UButton
                  v-if="isChannelAdmin(channel.id)"
                  @click.stop="openChannelSettings(channel)"
                  size="xs"
                  variant="ghost"
                  icon="i-heroicons-cog-6-tooth"
                  class="ml-2 opacity-0 group-hover:opacity-100 transition-opacity"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 線上使用者 -->
      <div class="px-3 py-2 border-t border-gray-100">
        <div class="flex items-center justify-between mb-2">
          <h3
            class="text-xs font-medium text-gray-400 uppercase tracking-wider"
          >
            線上使用者
          </h3>
        </div>

        <div class="space-y-0.5 max-h-32 overflow-y-auto">
          <div
            v-for="member in channelStore.currentChannelMembers"
            :key="member.id"
            class="flex items-center px-2 py-1 text-sm text-gray-700 rounded hover:bg-gray-50"
          >
            <div
              class="w-2 h-2 bg-green-400 rounded-full mr-2 flex-shrink-0"
            ></div>
            <span class="truncate flex-1">{{ member.display_name }}</span>

            <!-- 角色標籤 -->
            <UBadge
              v-if="member.role !== 'member'"
              :label="member.role === 'owner' ? '擁有者' : '管理員'"
              color="blue"
              variant="soft"
              size="xs"
              class="ml-1"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 載入狀態 -->
    <div
      v-if="channelStore.loading"
      class="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center"
    >
      <div class="text-center">
        <div
          class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"
        ></div>
        <div class="mt-2 text-sm text-gray-600">載入中...</div>
      </div>
    </div>

    <!-- 錯誤提示 -->
    <UAlert
      v-if="channelStore.error"
      icon="i-heroicons-exclamation-triangle"
      color="red"
      variant="soft"
      :title="channelStore.error"
      class="m-2"
      :close-button="{
        icon: 'i-heroicons-x-mark-20-solid',
        color: 'red',
        variant: 'link',
      }"
      @close="channelStore.clearError()"
    />
  </aside>
</template>

<script setup>
import { useChannelStore } from "~/stores/channel";
import { useUserStore } from "~/stores/user";

// 不再需要 emit 事件，直接操作 store

const channelStore = useChannelStore();
const userStore = useUserStore();

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
/* 自訂滾動條樣式 */
.overflow-y-auto::-webkit-scrollbar {
  width: 4px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 2px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}

/* TG 風格頻道項目 - 覆蓋全域 theme.css 樣式 */
.channel-item-tg {
  /* 重置全域 sidebar-item 樣式 */
  margin: 0 !important;
  padding: 16px 16px !important;
  border-radius: 0 !important;
  transform: none !important;
  background: transparent !important;
  min-height: 72px; /* 確保足夠高度容納兩行內容 */
}

.channel-item-tg:hover {
  background: #f8fafc !important;
  transform: none !important;
}

.channel-item-tg.bg-blue-50 {
  background: #e1f0ff !important;
  border-left: 3px solid #3b82f6;
}

/* 頻道項目的懸停效果 */
.group:hover .opacity-0 {
  opacity: 1;
}

/* 訊息內容樣式 */
.channel-item-tg .text-sm {
  line-height: 1.4;
}

/* 時間戳樣式 */
.channel-item-tg .text-xs {
  font-weight: 500;
  letter-spacing: 0.025em;
}
</style>
