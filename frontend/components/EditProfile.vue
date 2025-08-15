<template>
  <Card class="edit-profile-sidebar">
    <!-- 編輯個人資料標題 -->
    <template #header>
      <div class="flex items-center justify-between">
        <h1 class="text-lg font-semibold">編輯個人資料</h1>
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

    <!-- 編輯表單 -->
    <template #content>
      <div class="edit-form">
        <!-- 大頭貼區域 -->
        <div class="avatar-section">
          <div class="flex flex-col items-center py-6">
            <div class="relative">
              <Avatar
                :label="userInitials"
                class="edit-avatar"
                shape="circle"
                size="xlarge"
              />
            </div>
            <p class="text-sm text-gray-500 mt-2">點擊更換大頭貼</p>
          </div>
        </div>

        <!-- 表單欄位 -->
        <div class="form-fields">
          <!-- 顯示名稱 -->
          <div class="form-group">
            <label class="form-label">顯示名稱</label>
            <div class="form-input-container">
              <InputText
                v-model="profileForm.displayName"
                placeholder="請輸入顯示名稱"
                :disabled="saving"
                class="w-full"
                maxlength="50"
              />
              <small class="input-counter">
                {{ profileForm.displayName.length }}/50
              </small>
            </div>
          </div>

          <!-- 個人簡介 -->
          <div class="form-group">
            <label class="form-label">個人簡介</label>
            <div class="form-input-container">
              <Textarea
                v-model="profileForm.bio"
                placeholder="介紹一下自己..."
                :rows="3"
                :disabled="saving"
                class="w-full"
                maxlength="200"
              />
              <small class="input-counter">
                {{ profileForm.bio.length }}/200
              </small>
            </div>
          </div>

          <!-- 用戶名稱 -->
          <div class="form-group">
            <label class="form-label">用戶名稱</label>
            <div class="form-input-container">
              <InputText
                v-model="profileForm.username"
                readonly
                disabled
                class="w-full"
              />
              <small class="form-help">用戶名稱無法修改</small>
            </div>
          </div>

          <!-- 電子郵件 -->
          <div class="form-group">
            <label class="form-label">電子郵件</label>
            <div class="form-input-container">
              <InputText
                v-model="profileForm.email"
                type="email"
                readonly
                disabled
                class="w-full"
              />
              <small class="form-help">電子郵件無法修改</small>
            </div>
          </div>

          <!-- 語言設定 -->
          <div class="form-group">
            <label class="form-label">語言</label>
            <div class="form-input-container">
              <Dropdown
                v-model="profileForm.language"
                :options="languageOptions"
                optionLabel="label"
                optionValue="value"
                :disabled="saving"
                class="w-full"
              />
            </div>
          </div>

          <!-- 時區設定 -->
          <div class="form-group">
            <label class="form-label">時區</label>
            <div class="form-input-container">
              <Dropdown
                v-model="profileForm.timezone"
                :options="timezoneOptions"
                optionLabel="label"
                optionValue="value"
                :disabled="saving"
                class="w-full"
              />
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- 保存按鈕 -->
    <template #footer>
      <div class="form-actions">
        <Button
          @click="handleSave"
          :disabled="saving || !hasChanges"
          :loading="saving"
          :label="saving ? '保存中...' : '保存變更'"
          class="w-full"
          severity="success"
        />
      </div>
    </template>
  </Card>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from "vue";
import { useUserStore } from "~/stores/user";

// 定義事件
const emit = defineEmits(["back", "save"]);

const userStore = useUserStore();
const saving = ref(false);

// 表單資料
const profileForm = reactive({
  displayName: "",
  bio: "",
  username: "",
  email: "",
  language: "zh-TW",
  timezone: "Asia/Taipei",
});

// 語言選項
const languageOptions = [
  { label: "繁體中文", value: "zh-TW" },
  { label: "简体中文", value: "zh-CN" },
  { label: "English", value: "en" },
  { label: "日本語", value: "ja" },
];

// 時區選項
const timezoneOptions = [
  { label: "台北 (GMT+8)", value: "Asia/Taipei" },
  { label: "上海 (GMT+8)", value: "Asia/Shanghai" },
  { label: "東京 (GMT+9)", value: "Asia/Tokyo" },
  { label: "協調世界時 (GMT+0)", value: "UTC" },
];

// 原始資料（用於檢查是否有變更）
const originalForm = reactive({});

// 用戶名稱縮寫
const userInitials = computed(() => {
  const name = profileForm.displayName || userStore.displayName || "User";
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
});

// 檢查是否有變更
const hasChanges = computed(() => {
  return (
    profileForm.displayName !== originalForm.displayName ||
    profileForm.bio !== originalForm.bio ||
    profileForm.language !== originalForm.language ||
    profileForm.timezone !== originalForm.timezone
  );
});

// 初始化表單資料
const initForm = () => {
  const profile = userStore.userProfile || {};
  const user = userStore.user || {};

  profileForm.displayName = profile.display_name || userStore.displayName || "";
  profileForm.bio = profile.bio || "";
  profileForm.username = user.username || "";
  profileForm.email = user.email || "";
  profileForm.language = profile.language || "zh-TW";
  profileForm.timezone = profile.timezone || "Asia/Taipei";

  // 保存原始資料
  Object.assign(originalForm, { ...profileForm });
};

// 保存變更
const handleSave = async () => {
  saving.value = true;

  try {
    // 這裡應該調用 API 保存用戶資料
    // await userStore.updateProfile({
    //   display_name: profileForm.displayName,
    //   bio: profileForm.bio,
    //   language: profileForm.language,
    //   timezone: profileForm.timezone
    // });

    // 模擬保存延遲
    await new Promise((resolve) => setTimeout(resolve, 1000));

    // 更新原始資料
    Object.assign(originalForm, { ...profileForm });

    console.log("個人資料已保存");
    emit("save");
  } catch (error) {
    console.error("保存失敗:", error);
  } finally {
    saving.value = false;
  }
};

onMounted(() => {
  initForm();
});
</script>

<style scoped>
/* 編輯個人資料側邊欄卡片樣式 */
.edit-profile-sidebar {
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

.edit-profile-sidebar :deep(.p-card-header) {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border-bottom: 1px solid var(--surface-border);
  padding: 1rem;
}

.edit-profile-sidebar :deep(.p-card-content) {
  padding: 0;
  height: calc(100% - 140px);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.edit-profile-sidebar :deep(.p-card-footer) {
  background: var(--surface-50);
  border-top: 1px solid var(--surface-border);
  padding: 1rem;
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

/* 編輯表單 */
.edit-form {
  flex: 1;
  overflow-y: auto;
  background: var(--surface-0);
}

/* 大頭貼區域 */
.avatar-section {
  border-bottom: 1px solid var(--surface-border);
  background: var(--surface-0);
  flex-shrink: 0;
}

.edit-avatar {
  background: linear-gradient(135deg, #10b981, #059669) !important;
  color: white !important;
  font-weight: 600;
  width: 6rem !important;
  height: 6rem !important;
  font-size: 1.5rem !important;
}

/* 表單欄位 */
.form-fields {
  padding: 1rem;
  flex: 1;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.form-input-container {
  position: relative;
}

.input-counter {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: var(--text-color-secondary);
  text-align: right;
}

.form-help {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: var(--text-color-secondary);
}

/* 保存按鈕區域 */
.form-actions {
  padding: 0;
}

/* 自訂滾動條樣式 */
.edit-form::-webkit-scrollbar {
  width: 4px;
}

.edit-form::-webkit-scrollbar-track {
  background: transparent;
}

.edit-form::-webkit-scrollbar-thumb {
  background: var(--surface-300);
  border-radius: 4px;
}

.edit-form::-webkit-scrollbar-thumb:hover {
  background: var(--surface-400);
}

/* 動畫效果 */
.edit-profile-sidebar {
  animation: slideInRight 0.3s ease-out;
}

.avatar-section {
  animation: fadeInDown 0.4s ease-out;
}

.form-fields {
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
  .edit-profile-sidebar {
    width: 100%;
    max-width: none;
  }
}

/* 暗色主題支援 */
@media (prefers-color-scheme: dark) {
  .edit-profile-sidebar {
    background: linear-gradient(
      135deg,
      var(--surface-800) 0%,
      var(--surface-900) 100%
    );
  }

  .edit-form {
    background: var(--surface-800);
  }

  .avatar-section {
    background: var(--surface-800);
  }
}
</style>
