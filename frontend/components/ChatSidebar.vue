<template>
  <div class="chat-sidebar">
    <!-- 用戶資訊卡片 -->
    <Card class="user-info-card">
      <template #content>
        <div class="user-info-content">
          <!-- 用戶頭像和資訊 -->
          <div class="flex items-center gap-3">
            <Avatar 
              :label="userInitials" 
              class="user-avatar"
              shape="circle" 
              size="large"
            />
            <div class="user-details">
              <ClientOnly>
                <div class="user-name">{{ userStore.displayName }}</div>
                <template #fallback>
                  <div class="user-name">訪客</div>
                </template>
              </ClientOnly>
              
              <!-- 連線狀態 -->
              <ClientOnly>
                <div class="connection-status">
                  <Badge 
                    :value="connectionStatus" 
                    :severity="connectionBadgeSeverity"
                    class="status-badge"
                  />
                </div>
                <template #fallback>
                  <div class="connection-status">
                    <Badge value="連線中..." severity="secondary" class="status-badge" />
                  </div>
                </template>
              </ClientOnly>
            </div>
          </div>

          <!-- 操作按鈕 -->
          <div class="user-actions">
            <Button
              @click="$emit('show-user-settings')"
              icon="pi pi-cog"
              severity="secondary"
              text
              rounded
              class="settings-button"
              v-tooltip.bottom="'用戶設定'"
            />
            <Button
              icon="pi pi-sign-out"
              severity="secondary"
              text
              rounded
              class="logout-button"
              v-tooltip.bottom="'登出'"
              @click="$emit('logout')"
            />
          </div>
        </div>
      </template>
    </Card>

    <!-- 聊天室標題 -->
    <div class="section-header">
      <h3 class="section-title">
        <i class="pi pi-comments"></i>
        聊天頻道
      </h3>
      <Button
        icon="pi pi-plus"
        severity="success"
        text
        rounded
        size="small"
        v-tooltip.bottom="'新增頻道'"
        @click="$emit('create-channel')"
      />
    </div>

    <!-- 聊天室清單 -->
    <div class="channel-list">
      <ChannelSidebar />
    </div>

    <!-- 底部資訊 -->
    <div class="sidebar-footer">
      <Divider />
      <div class="footer-content">
        <div class="online-count">
          <i class="pi pi-users text-emerald-500"></i>
          <span class="count-text">聊天室系統</span>
        </div>
        <div class="app-version">
          <small class="version-text">v2.0</small>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useUserStore } from "~/stores/user";
import ChannelSidebar from "~/components/ChannelSidebar.vue";
import Avatar from "primevue/avatar";
import Button from "primevue/button";
import Card from "primevue/card";
import Badge from "primevue/badge";
import Divider from "primevue/divider";

// 定義 props
const props = defineProps({
  connectionStatus: {
    type: String,
    default: "未連線",
  },
  connectionStatusClass: {
    type: String,
    default: "bg-red-500",
  },
});

// 定義事件
const emit = defineEmits(["show-user-settings", "logout", "create-channel"]);

const userStore = useUserStore();

// 計算用戶姓名縮寫
const userInitials = computed(() => {
  const name = userStore.displayName || '訪客';
  return name.split(' ')
    .map(word => word.charAt(0))
    .join('')
    .substring(0, 2)
    .toUpperCase();
});

// 連線狀態徽章樣式
const connectionBadgeSeverity = computed(() => {
  switch (props.connectionStatus) {
    case '已連線':
      return 'success';
    case '連線中...':
      return 'info';
    case '重新連線中...':
      return 'warn';
    default:
      return 'danger';
  }
});
</script>

<style scoped>
.chat-sidebar {
  width: 20rem;
  max-width: 320px;
  height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-right: 1px solid var(--surface-border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 用戶資訊卡片 */
.user-info-card {
  margin: 1rem;
  margin-bottom: 0.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.user-info-card :deep(.p-card-content) {
  padding: 1rem;
}

.user-info-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.user-avatar {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  font-weight: 600;
}

.user-details {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-weight: 600;
  color: var(--text-color);
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.connection-status {
  display: flex;
  align-items: center;
}

.status-badge :deep(.p-badge) {
  font-size: 0.7rem;
  padding: 0.25rem 0.5rem;
}

.user-actions {
  display: flex;
  gap: 0.25rem;
}

.settings-button, .logout-button {
  width: 2rem;
  height: 2rem;
}

.settings-button:hover {
  background: var(--primary-color) !important;
  color: white !important;
}

.logout-button:hover {
  background: var(--red-500) !important;
  color: white !important;
}

/* 區段標題 */
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  padding-bottom: 0.5rem;
}

.section-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.section-title i {
  color: var(--primary-color);
}

/* 頻道清單 */
.channel-list {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 0 0.5rem;
}

/* 自定義滾動條 */
.channel-list::-webkit-scrollbar {
  width: 4px;
}

.channel-list::-webkit-scrollbar-track {
  background: transparent;
}

.channel-list::-webkit-scrollbar-thumb {
  background: var(--surface-300);
  border-radius: 4px;
}

.channel-list::-webkit-scrollbar-thumb:hover {
  background: var(--surface-400);
}

/* 底部資訊 */
.sidebar-footer {
  margin-top: auto;
  padding: 0.5rem 1rem 1rem;
}

.footer-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 0.5rem;
}

.online-count {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.count-text {
  font-size: 0.8rem;
  color: var(--text-color-secondary);
  font-weight: 500;
}

.version-text {
  color: var(--text-color-secondary);
  font-size: 0.7rem;
}

/* 動畫效果 */
.user-info-card, .section-header {
  animation: fadeInDown 0.3s ease-out;
}

.channel-list {
  animation: fadeInUp 0.4s ease-out;
}

.sidebar-footer {
  animation: fadeInUp 0.5s ease-out;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 響應式設計 */
@media (max-width: 768px) {
  .chat-sidebar {
    width: 100%;
    max-width: none;
  }
  
  .user-info-card {
    margin: 0.5rem;
    margin-bottom: 0.25rem;
  }
  
  .section-header {
    padding: 0.75rem;
    padding-bottom: 0.25rem;
  }
}

/* 暗色主題支援 */
@media (prefers-color-scheme: dark) {
  .chat-sidebar {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  }
}
</style>