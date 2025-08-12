<template>
  <div class="sidebar">
    <!-- 編輯個人資料標題 -->
    <div class="sidebar-header">
      <div class="flex items-center justify-between">
        <h1 class="text-lg font-semibold">編輯個人資料</h1>
        <button @click="$emit('back')" class="back-btn" title="返回">
          <svg
            width="18"
            height="18"
            viewBox="0 0 20 20"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M12.5 15L7.5 10L12.5 5"
              stroke="rgba(255, 255, 255, 0.8)"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </button>
      </div>
    </div>

    <!-- 編輯表單 -->
    <div class="edit-form">
      <!-- 大頭貼區域 -->
      <div class="avatar-section">
        <div class="flex flex-col items-center py-6">
          <div
            class="w-24 h-24 rounded-full bg-telegram-blue flex items-center justify-center text-white font-bold text-2xl mb-4 relative"
          >
            {{ userInitials }}
            <button
              class="absolute -bottom-1 -right-1 w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white hover:bg-blue-600 transition-colors"
            >
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path
                  d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z"
                />
              </svg>
            </button>
          </div>
          <p class="text-sm text-gray-500">點擊更換大頭貼</p>
        </div>
      </div>

      <!-- 表單欄位 -->
      <div class="form-fields">
        <!-- 顯示名稱 -->
        <div class="form-group">
          <label class="form-label">顯示名稱</label>
          <div class="form-input-container">
            <input
              v-model="profileForm.displayName"
              type="text"
              class="form-input"
              placeholder="請輸入顯示名稱"
              :disabled="saving"
            />
            <div class="input-counter">
              {{ profileForm.displayName.length }}/50
            </div>
          </div>
        </div>

        <!-- 個人簡介 -->
        <div class="form-group">
          <label class="form-label">個人簡介</label>
          <div class="form-input-container">
            <textarea
              v-model="profileForm.bio"
              class="form-textarea"
              placeholder="介紹一下自己..."
              rows="3"
              :disabled="saving"
            ></textarea>
            <div class="input-counter">{{ profileForm.bio.length }}/200</div>
          </div>
        </div>

        <!-- 用戶名稱 -->
        <div class="form-group">
          <label class="form-label">用戶名稱</label>
          <div class="form-input-container">
            <input
              v-model="profileForm.username"
              type="text"
              class="form-input"
              readonly
              disabled
            />
            <p class="form-help">用戶名稱無法修改</p>
          </div>
        </div>

        <!-- 電子郵件 -->
        <div class="form-group">
          <label class="form-label">電子郵件</label>
          <div class="form-input-container">
            <input
              v-model="profileForm.email"
              type="email"
              class="form-input"
              readonly
              disabled
            />
            <p class="form-help">電子郵件無法修改</p>
          </div>
        </div>

        <!-- 語言設定 -->
        <div class="form-group">
          <label class="form-label">語言</label>
          <div class="form-input-container">
            <select
              v-model="profileForm.language"
              class="form-select"
              :disabled="saving"
            >
              <option value="zh-TW">繁體中文</option>
              <option value="zh-CN">简体中文</option>
              <option value="en">English</option>
              <option value="ja">日本語</option>
            </select>
          </div>
        </div>

        <!-- 時區設定 -->
        <div class="form-group">
          <label class="form-label">時區</label>
          <div class="form-input-container">
            <select
              v-model="profileForm.timezone"
              class="form-select"
              :disabled="saving"
            >
              <option value="Asia/Taipei">台北 (GMT+8)</option>
              <option value="Asia/Shanghai">上海 (GMT+8)</option>
              <option value="Asia/Tokyo">東京 (GMT+9)</option>
              <option value="UTC">協調世界時 (GMT+0)</option>
            </select>
          </div>
        </div>
      </div>

      <!-- 保存按鈕 -->
      <div class="form-actions">
        <button
          @click="handleSave"
          :disabled="saving || !hasChanges"
          class="save-button"
        >
          <svg
            v-if="saving"
            class="w-4 h-4 animate-spin mr-2"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              d="M4 2a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V4a2 2 0 00-2-2H4z"
            />
          </svg>
          {{ saving ? "保存中..." : "保存變更" }}
        </button>
      </div>
    </div>
  </div>
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
.sidebar {
  width: 20rem;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
  overflow-x: hidden;
  max-width: 320px;
  height: 100vh;
}

.sidebar-header {
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
  background: #10b981;
  color: white;
}

.edit-form {
  flex: 1;
  overflow-y: auto;
  background: white;
}

.avatar-section {
  border-bottom: 1px solid #f3f4f6;
}

.bg-telegram-blue {
  background: linear-gradient(135deg, #41b4e6, #2696d9);
}

.form-fields {
  padding: 1rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.form-input-container {
  position: relative;
}

.form-input,
.form-textarea,
.form-select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-input:focus,
.form-textarea:focus,
.form-select:focus {
  outline: none;
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(0, 136, 204, 0.1);
}

.form-input:disabled,
.form-textarea:disabled,
.form-select:disabled {
  background-color: #f9fafb;
  color: #6b7280;
  cursor: not-allowed;
}

.form-textarea {
  resize: vertical;
  min-height: 4rem;
}

.input-counter {
  position: absolute;
  bottom: 0.5rem;
  right: 0.75rem;
  font-size: 0.75rem;
  color: #9ca3af;
  pointer-events: none;
}

.form-help {
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: #6b7280;
}

.form-actions {
  padding: 1rem;
  border-top: 1px solid #f3f4f6;
  background: #f9fafb;
}

.save-button {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem 1.5rem;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.save-button:hover:not(:disabled) {
  background: #0077b3;
}

.save-button:disabled {
  background: #d1d5db;
  color: #9ca3af;
  cursor: not-allowed;
}

/* 返回按鈕樣式 */
.back-btn {
  padding: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.05);
}

.back-btn:hover svg path {
  stroke: rgba(255, 255, 255, 1);
}

.back-btn svg {
  display: block;
  transition: all 0.2s ease;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .sidebar {
    width: 100%;
  }
}
</style>
