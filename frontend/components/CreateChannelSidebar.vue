<template>
  <Card class="create-channel-sidebar">
    <!-- 標題 -->
    <template #header>
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-semibold">建立新頻道</h2>
        <Button
          @click="$emit('back')"
          icon="pi pi-arrow-left"
          text
          rounded
          size="small"
          class="back-button"
          v-tooltip.bottom="'返回頻道列表'"
        />
      </div>
    </template>

    <!-- 表單內容 -->
    <template #content>
      <div class="create-form">
      <p class="text-sm text-gray-600 mb-4">
        建立一個新的聊天頻道，讓團隊成員可以在此進行討論。
      </p>

      <form @submit.prevent="handleCreateChannel" class="space-y-4">
          <!-- 頻道名稱 -->
          <div class="form-group">
            <label for="channel-name" class="form-label">
              頻道名稱 <span class="text-red-500">*</span>
            </label>
            <InputText
              id="channel-name"
              v-model="form.name"
              placeholder="例如：general、random、dev-team"
              :disabled="loading"
              required
              maxlength="50"
              class="w-full"
            />
            <small v-if="errors.name" class="form-error">
              {{ errors.name }}
            </small>
            <small class="form-help">
              頻道名稱將會自動轉為小寫，空格會被替換為連字符
            </small>
          </div>

          <!-- 頻道描述 -->
          <div class="form-group">
            <label for="channel-description" class="form-label">
              頻道描述
            </label>
            <Textarea
              id="channel-description"
              v-model="form.description"
              placeholder="描述這個頻道的用途..."
              :disabled="loading"
              :rows="3"
              maxlength="200"
              class="w-full"
            />
            <small v-if="errors.description" class="form-error">
              {{ errors.description }}
            </small>
          </div>

        <!-- 頻道設定 -->
        <div class="space-y-3">
          <div class="text-sm font-medium text-gray-700">頻道設定</div>

          <!-- 私人頻道 -->
          <div class="form-group">
            <div class="flex items-start gap-3">
              <Checkbox
                v-model="form.is_private"
                inputId="is-private"
                :disabled="loading"
                binary
              />
              <div class="flex-1">
                <label for="is-private" class="form-label cursor-pointer">
                  私人頻道
                </label>
                <small class="form-help">
                  只有受邀請的成員才能看到和加入此頻道
                </small>
              </div>
            </div>
          </div>

          <!-- 最大成員數 -->
          <div class="form-group">
            <label for="max-members" class="form-label">
              最大成員數
            </label>
            <InputNumber
              id="max-members"
              v-model="form.max_members"
              :min="2"
              :max="1000"
              :disabled="loading"
              placeholder="100"
              class="w-full"
              showButtons
            />
            <small v-if="errors.max_members" class="form-error">
              {{ errors.max_members }}
            </small>
          </div>
        </div>

          <!-- 預覽 -->
          <div v-if="form.name" class="preview-section">
            <div class="preview-title">
              預覽
            </div>
            <div class="flex items-center preview-content">
              <i
                :class="
                  form.is_private
                    ? 'pi pi-lock'
                    : 'pi pi-hashtag'
                "
                class="preview-icon"
              ></i>
              {{ normalizeChannelName(form.name) }}
              <Tag
                v-if="form.is_private"
                value="私人"
                severity="warn"
                class="ml-2"
              />
            </div>
            <small v-if="form.description" class="preview-description">
              {{ form.description }}
            </small>
          </div>

          <!-- 錯誤訊息 -->
          <Message
            v-if="channelStore.error"
            severity="error"
            :closable="true"
            @close="channelStore.clearError()"
          >
            {{ channelStore.error }}
          </Message>
        </form>
      </div>
    </template>

    <!-- 底部按鈕 -->
    <template #footer>
      <div class="form-actions">
        <div class="flex gap-2">
          <Button
            severity="secondary"
            outlined
            @click="$emit('back')"
            :disabled="loading"
            class="flex-1"
            label="取消"
          />
          <Button
            @click="handleCreateChannel"
            :loading="loading"
            :disabled="loading || !form.name.trim()"
            icon="pi pi-plus"
            class="flex-1"
            :label="loading ? '建立中...' : '建立頻道'"
            severity="success"
          />
        </div>
      </div>
    </template>
  </Card>
</template>

<script setup>
import { useChannelStore } from "~/stores/channel";

// 定義事件
const emit = defineEmits(["back"]);

const channelStore = useChannelStore();

// 表單資料
const form = reactive({
  name: "",
  description: "",
  is_private: false,
  max_members: 100,
});

// 表單狀態
const loading = ref(false);
const errors = ref({});

// 表單驗證
const validateForm = () => {
  errors.value = {};

  // 頻道名稱驗證
  if (!form.name.trim()) {
    errors.value.name = "頻道名稱為必填";
    return false;
  }

  if (form.name.length < 2) {
    errors.value.name = "頻道名稱至少需要2個字元";
    return false;
  }

  if (form.name.length > 50) {
    errors.value.name = "頻道名稱不能超過50個字元";
    return false;
  }

  // 頻道名稱格式驗證
  if (!/^[a-zA-Z0-9\u4e00-\u9fa5\s\-_]+$/.test(form.name)) {
    errors.value.name = "頻道名稱只能包含字母、數字、中文、空格、連字符和底線";
    return false;
  }

  // 描述長度驗證
  if (form.description && form.description.length > 200) {
    errors.value.description = "頻道描述不能超過200個字元";
    return false;
  }

  // 最大成員數驗證
  if (form.max_members < 2 || form.max_members > 1000) {
    errors.value.max_members = "最大成員數必須在2-1000之間";
    return false;
  }

  return true;
};

// 正規化頻道名稱
const normalizeChannelName = (name) => {
  return name
    .toLowerCase()
    .trim()
    .replace(/\s+/g, "-")
    .replace(/[^a-z0-9\u4e00-\u9fa5\-_]/g, "");
};

// 處理建立頻道
const handleCreateChannel = async () => {
  // 清除之前的錯誤
  channelStore.clearError();

  if (!validateForm()) return;

  loading.value = true;

  try {
    const channelData = {
      name: normalizeChannelName(form.name),
      description: form.description.trim(),
      is_private: form.is_private,
      max_members: form.max_members,
    };

    console.log("建立頻道:", channelData);

    const result = await channelStore.createChannel(channelData);

    if (result.success) {
      console.log("頻道建立成功");

      // 重設表單
      form.name = "";
      form.description = "";
      form.is_private = false;
      form.max_members = 100;
      errors.value = {};

      // 顯示成功訊息
      const toast = useToast();
      toast.add({
        title: "頻道建立成功！",
        description: `頻道 "${channelData.name}" 已成功建立`,
        icon: "i-heroicons-check-circle",
        color: "green",
      });

      // 返回頻道列表
      emit("back");
    } else {
      console.error("頻道建立失敗:", result.error);
    }
  } catch (error) {
    console.error("建立頻道時發生錯誤:", error);
  } finally {
    loading.value = false;
  }
};

// 監聽頻道名稱變化，即時驗證
watch(
  () => form.name,
  () => {
    if (errors.value.name) {
      // 清除名稱錯誤，讓使用者看到即時反饋
      delete errors.value.name;
    }
  }
);
</script>

<style scoped>
/* 建立頻道側邊欄卡片樣式 */
.create-channel-sidebar {
  width: 20rem;
  max-width: 320px;
  height: 100vh;
  border: 0;
  border-radius: 0;
  border-left: 1px solid var(--surface-border);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  background: linear-gradient(135deg, var(--surface-50) 0%, var(--surface-100) 100%);
}

.create-channel-sidebar :deep(.p-card-header) {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border-bottom: 1px solid var(--surface-border);
  padding: 1rem;
}

.create-channel-sidebar :deep(.p-card-content) {
  padding: 0;
  height: calc(100% - 140px);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.create-channel-sidebar :deep(.p-card-footer) {
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

/* 建立表單 */
.create-form {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  background: var(--surface-0);
}

.create-form > p {
  color: var(--text-color-secondary);
  margin-bottom: 1rem;
  font-size: 0.875rem;
  line-height: 1.5;
}

/* 表單組件 */
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

.form-error {
  display: block;
  margin-top: 0.25rem;
  color: var(--red-500);
  font-size: 0.75rem;
}

.form-help {
  display: block;
  margin-top: 0.25rem;
  color: var(--text-color-secondary);
  font-size: 0.75rem;
  line-height: 1.4;
}

/* 頻道設定區域 */
.space-y-3 > * + * {
  margin-top: 0.75rem;
}

.space-y-3 > .text-sm {
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 0.75rem;
}

/* 預覽區域 */
.preview-section {
  background: var(--surface-100);
  border-radius: 0.5rem;
  padding: 0.75rem;
  border: 1px solid var(--surface-border);
}

.preview-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-color-secondary);
  text-transform: uppercase;
  margin-bottom: 0.5rem;
  letter-spacing: 0.025em;
}

.preview-content {
  font-size: 0.875rem;
  color: var(--text-color);
  font-weight: 500;
}

.preview-icon {
  width: 1rem;
  height: 1rem;
  margin-right: 0.5rem;
  color: var(--text-color-secondary);
}

.preview-description {
  display: block;
  margin-top: 0.25rem;
  color: var(--text-color-secondary);
  font-size: 0.75rem;
  line-height: 1.4;
}

/* 底部動作按鈕 */
.form-actions {
  padding: 0;
}

/* 自訂滾動條樣式 */
.create-form::-webkit-scrollbar {
  width: 4px;
}

.create-form::-webkit-scrollbar-track {
  background: transparent;
}

.create-form::-webkit-scrollbar-thumb {
  background: var(--surface-300);
  border-radius: 4px;
}

.create-form::-webkit-scrollbar-thumb:hover {
  background: var(--surface-400);
}

/* 動畫效果 */
.create-channel-sidebar {
  animation: slideInLeft 0.3s ease-out;
}

.create-form {
  animation: fadeInUp 0.4s ease-out;
}

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
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
  .create-channel-sidebar {
    width: 100%;
    max-width: none;
  }
}

/* 暗色主題支援 */
@media (prefers-color-scheme: dark) {
  .create-channel-sidebar {
    background: linear-gradient(135deg, var(--surface-800) 0%, var(--surface-900) 100%);
  }
  
  .create-form {
    background: var(--surface-800);
  }
  
  .preview-section {
    background: var(--surface-700);
  }
}
</style>
