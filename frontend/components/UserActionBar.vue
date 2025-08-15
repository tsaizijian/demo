<template>
  <Card class="user-action-sidebar">
    <!-- 用戶操作標題 -->
    <template #header>
      <div class="flex items-center justify-between">
        <h1 class="text-lg font-semibold">設定</h1>
        <Button
          @click="$emit('back')"
          icon="pi pi-arrow-left"
          text
          rounded
          size="small"
          class="back-button"
          v-tooltip.bottom="'返回'"
        />
      </div>
    </template>

    <template #content>
      <!-- 用戶資訊 -->
      <div class="user-info-section">
        <div class="flex items-center p-4">
          <Avatar
            :label="userInitials"
            class="user-avatar"
            shape="circle"
            size="large"
          />
          <div class="flex-1 ml-3">
            <h3 class="text-lg font-semibold">
              {{ userStore.displayName }}
            </h3>
            <div class="flex items-center">
              <Badge value="線上" severity="success" class="status-badge" />
            </div>
          </div>
        </div>
      </div>

      <!-- 操作選單 -->
      <div class="action-list">
        <!-- 個人資料 -->
        <div class="action-item" @click="$emit('edit-profile')">
          <div class="action-icon bg-blue-100">
            <i class="pi pi-user text-blue-600"></i>
          </div>
          <div class="action-content">
            <div class="action-title">我的帳號</div>
            <div class="action-subtitle">設定個人資料</div>
          </div>
          <div class="action-arrow">
            <i class="pi pi-chevron-right text-gray-400"></i>
          </div>
        </div>

        <!-- 通知設定 -->
        <div class="action-item">
          <div class="action-icon bg-green-100">
            <i class="pi pi-bell text-green-600"></i>
          </div>
          <div class="action-content">
            <div class="action-title">通知</div>
            <div class="action-subtitle">訊息通知設定</div>
          </div>
          <div class="action-arrow">
            <i class="pi pi-chevron-right text-gray-400"></i>
          </div>
        </div>

        <!-- 隱私設定 -->
        <div class="action-item">
          <div class="action-icon bg-purple-100">
            <i class="pi pi-shield text-purple-600"></i>
          </div>
          <div class="action-content">
            <div class="action-title">隱私與安全</div>
            <div class="action-subtitle">隱私設定</div>
          </div>
          <div class="action-arrow">
            <i class="pi pi-chevron-right text-gray-400"></i>
          </div>
        </div>

        <!-- 已刪除頻道 -->
        <div class="action-item" @click="$emit('view-deleted-channels')">
          <div class="action-icon bg-orange-100">
            <i class="pi pi-trash text-orange-600"></i>
          </div>
          <div class="action-content">
            <div class="action-title">已刪除的頻道</div>
            <div class="action-subtitle">查看並恢復已刪除的頻道</div>
          </div>
          <div class="action-arrow">
            <i class="pi pi-chevron-right text-gray-400"></i>
          </div>
        </div>

        <!-- 分隔線 -->
        <Divider />

        <!-- 登出 -->
        <div class="action-item logout-item" @click="$emit('logout')">
          <div class="action-icon bg-red-100">
            <i class="pi pi-sign-out text-red-600"></i>
          </div>
          <div class="action-content">
            <div class="action-title text-red-600">登出</div>
            <div class="action-subtitle">登出聊天室</div>
          </div>
        </div>
      </div>
    </template>
  </Card>
</template>

<script setup>
import { computed } from "vue";
import { useUserStore } from "~/stores/user";

// 定義事件
const emit = defineEmits(["back", "edit-profile", "logout", "view-deleted-channels"]);

const userStore = useUserStore();

// 用戶名稱縮寫
const userInitials = computed(() => {
  const name = userStore.displayName || "User";
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
});
</script>

<style scoped>
/* 用戶操作側邊欄卡片樣式 */
.user-action-sidebar {
  width: 20rem;
  max-width: 320px;
  height: 100vh;
  border: 0;
  border-radius: 0;
  border-right: 1px solid var(--surface-border);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  background: linear-gradient(
    135deg,
    var(--surface-50) 0%,
    var(--surface-100) 100%
  );
}

.user-action-sidebar :deep(.p-card-header) {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border-bottom: 1px solid var(--surface-border);
  padding: 1rem;
}

.user-action-sidebar :deep(.p-card-content) {
  padding: 0;
  height: calc(100% - 80px);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 用戶資訊區域 */
.user-info-section {
  border-bottom: 1px solid var(--surface-border);
  background: var(--surface-0);
  flex-shrink: 0;
}

.user-avatar {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  font-weight: 600;
}

.status-badge :deep(.p-badge) {
  font-size: 0.7rem;
  padding: 0.25rem 0.5rem;
}

/* 操作選單 */
.action-list {
  flex: 1;
  overflow-y: auto;
  background: var(--surface-0);
}

.action-item {
  display: flex;
  align-items: center;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border-bottom: 1px solid var(--surface-100);
}

.action-item:hover:not(.logout-item) {
  background-color: var(--surface-50);
}

.logout-item:hover {
  background-color: var(--red-50);
}

.action-icon {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
  flex-shrink: 0;
  font-size: 1.25rem;
}

.action-content {
  flex: 1;
}

.action-title {
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 0.125rem;
  font-size: 0.95rem;
}

.action-subtitle {
  font-size: 0.8rem;
  color: var(--text-color-secondary);
}

.action-arrow {
  margin-left: 1rem;
  color: var(--text-color-secondary);
  font-size: 0.9rem;
}

/* 返回按鈕樣式 */
.back-button {
  background: rgba(255, 255, 255, 0.1) !important;
  border: none !important;
  backdrop-filter: blur(10px);
}

.back-button:hover {
  background: rgba(255, 255, 255, 0.2) !important;
  transform: scale(1.05);
}

/* 自訂滾動條樣式 */
.action-list::-webkit-scrollbar {
  width: 4px;
}

.action-list::-webkit-scrollbar-track {
  background: transparent;
}

.action-list::-webkit-scrollbar-thumb {
  background: var(--surface-300);
  border-radius: 4px;
}

.action-list::-webkit-scrollbar-thumb:hover {
  background: var(--surface-400);
}

/* 動畫效果 */
.user-action-sidebar {
  animation: slideInRight 0.3s ease-out;
}

.user-info-section {
  animation: fadeInDown 0.4s ease-out;
}

.action-list {
  animation: fadeInUp 0.5s ease-out;
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
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
  .user-action-sidebar {
    width: 100%;
    max-width: none;
  }
}

/* 暗色主題支援 */
@media (prefers-color-scheme: dark) {
  .user-action-sidebar {
    background: linear-gradient(
      135deg,
      var(--surface-800) 0%,
      var(--surface-900) 100%
    );
  }

  .action-item:hover:not(.logout-item) {
    background-color: var(--surface-700);
  }

  .logout-item:hover {
    background-color: var(--red-900);
  }
}
</style>
