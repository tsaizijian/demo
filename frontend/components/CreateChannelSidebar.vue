<template>
  <aside class="w-64 border-l border-gray-200 flex flex-col">
    <!-- 標題 -->
    <div class="p-4 border-b border-gray-200 bg-white">
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-semibold text-gray-900">建立新頻道</h2>
        <UButton
          @click="$emit('back')"
          variant="ghost"
          size="xs"
          icon="i-heroicons-arrow-left"
          title="返回頻道列表"
        />
      </div>
    </div>

    <!-- 表單內容 -->
    <div class="flex-1 overflow-y-auto p-4">
      <p class="text-sm text-gray-600 mb-4">
        建立一個新的聊天頻道，讓團隊成員可以在此進行討論。
      </p>

      <form @submit.prevent="handleCreateChannel" class="space-y-4">
        <!-- 頻道名稱 -->
        <div>
          <label
            for="channel-name"
            class="block text-sm font-medium text-gray-700 mb-1"
          >
            頻道名稱 <span class="text-red-500">*</span>
          </label>
          <UInput
            id="channel-name"
            v-model="form.name"
            placeholder="例如：general、random、dev-team"
            :disabled="loading"
            required
            maxlength="50"
            icon="i-heroicons-hashtag"
          />
          <p v-if="errors.name" class="mt-1 text-sm text-red-600">
            {{ errors.name }}
          </p>
          <p class="mt-1 text-xs text-gray-500">
            頻道名稱將會自動轉為小寫，空格會被替換為連字符
          </p>
        </div>

        <!-- 頻道描述 -->
        <div>
          <label
            for="channel-description"
            class="block text-sm font-medium text-gray-700 mb-1"
          >
            頻道描述
          </label>
          <UTextarea
            id="channel-description"
            v-model="form.description"
            placeholder="描述這個頻道的用途..."
            :disabled="loading"
            :rows="3"
            maxlength="200"
          />
          <p v-if="errors.description" class="mt-1 text-sm text-red-600">
            {{ errors.description }}
          </p>
        </div>

        <!-- 頻道設定 -->
        <div class="space-y-3">
          <div class="text-sm font-medium text-gray-700">頻道設定</div>

          <!-- 私人頻道 -->
          <div class="flex items-start gap-3">
            <input
              id="is-private"
              type="checkbox"
              v-model="form.is_private"
              :disabled="loading"
              class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 mt-0.5"
            />
            <div class="flex-1">
              <label
                for="is-private"
                class="text-sm font-medium text-gray-700 cursor-pointer"
              >
                私人頻道
              </label>
              <p class="text-xs text-gray-500">
                只有受邀請的成員才能看到和加入此頻道
              </p>
            </div>
          </div>

          <!-- 最大成員數 -->
          <div>
            <label
              for="max-members"
              class="block text-sm font-medium text-gray-700 mb-1"
            >
              最大成員數
            </label>
            <UInput
              id="max-members"
              v-model.number="form.max_members"
              type="number"
              min="2"
              max="1000"
              :disabled="loading"
              placeholder="100"
              icon="i-heroicons-user-group"
            />
            <p v-if="errors.max_members" class="mt-1 text-sm text-red-600">
              {{ errors.max_members }}
            </p>
          </div>
        </div>

        <!-- 預覽 -->
        <div v-if="form.name" class="bg-gray-50 rounded-lg p-3">
          <div class="text-xs font-medium text-gray-500 uppercase mb-2">
            預覽
          </div>
          <div class="flex items-center text-sm text-gray-700">
            <UIcon
              :name="
                form.is_private
                  ? 'i-heroicons-lock-closed'
                  : 'i-heroicons-hashtag'
              "
              class="w-4 h-4 mr-2"
            />
            {{ normalizeChannelName(form.name) }}
            <UBadge
              v-if="form.is_private"
              label="私人"
              color="orange"
              variant="soft"
              size="xs"
              class="ml-2"
            />
          </div>
          <p v-if="form.description" class="text-xs text-gray-500 mt-1">
            {{ form.description }}
          </p>
        </div>

        <!-- 錯誤訊息 -->
        <UAlert
          v-if="channelStore.error"
          icon="i-heroicons-exclamation-triangle"
          color="red"
          variant="soft"
          :title="channelStore.error"
        />
      </form>
    </div>

    <!-- 底部按鈕 -->
    <div class="p-4 border-t border-gray-200 bg-white">
      <div class="flex gap-2">
        <UButton
          color="gray"
          variant="soft"
          @click="$emit('back')"
          :disabled="loading"
          class="flex-1"
        >
          取消
        </UButton>
        <UButton
          @click="handleCreateChannel"
          :loading="loading"
          :disabled="loading || !form.name.trim()"
          icon="i-heroicons-plus"
          class="flex-1"
        >
          {{ loading ? "建立中..." : "建立頻道" }}
        </UButton>
      </div>
    </div>
  </aside>
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
</style>
