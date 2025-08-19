<template>
  <Dialog
    :visible="visible"
    @update:visible="$emit('update:visible', $event)"
    header="建立新頻道"
    modal
    class="w-full md:w-[600px]"
  >
    <div class="space-y-6">
      <p class="text-sm text-gray-600">
        建立一個新的聊天頻道，讓團隊成員可以在此進行討論。
      </p>

      <!-- 基本設定 -->
      <div class="basic-settings">
        <h4 class="text-lg font-semibold mb-3">基本設定</h4>

        <div class="space-y-4">
          <!-- 頻道名稱 -->
          <FloatLabel>
            <InputText
              id="channelName"
              v-model="form.name"
              class="w-full"
              :class="{ 'p-invalid': errors.name }"
              placeholder="頻道名稱"
              maxlength="50"
            />
          </FloatLabel>
          <small v-if="errors.name" class="p-error">{{ errors.name }}</small>
          <small class="text-gray-500"
            >頻道名稱將會自動轉為小寫，空格會被替換為連字符</small
          >

          <!-- 頻道描述 -->
          <FloatLabel>
            <Textarea
              id="description"
              v-model="form.description"
              rows="3"
              class="w-full"
              placeholder="頻道描述"
              maxlength="200"
            />
          </FloatLabel>
        </div>
      </div>

      <!-- 頻道類型 -->
      <div class="channel-type">
        <h4 class="text-lg font-semibold mb-3">頻道類型</h4>

        <div class="space-y-3">
          <div class="flex items-center gap-3">
            <Checkbox id="isPrivate" v-model="form.is_private" binary />
            <label for="isPrivate" class="font-medium">私人頻道</label>
          </div>
          <small class="text-gray-500 ml-6"
            >只有受邀請的成員才能看到和加入此頻道</small
          >
        </div>
      </div>

      <!-- 私群密碼設定 -->
      <div v-if="form.is_private" class="private-settings">
        <h4 class="text-lg font-semibold mb-3">私群設定</h4>

        <div class="space-y-4">
          <div class="setting-item">
            <div class="flex items-center gap-3 mb-2">
              <Checkbox
                id="allowJoinById"
                v-model="form.allow_join_by_id"
                binary
              />
              <label for="allowJoinById" class="font-medium"
                >允許通過頻道ID加入</label
              >
            </div>
            <small class="text-gray-500 ml-6"
              >開啟後，其他用戶可以使用頻道ID直接加入</small
            >
          </div>

          <div class="setting-item" v-if="form.allow_join_by_id">
            <div class="flex items-center gap-3 mb-2">
              <Checkbox
                id="passwordRequired"
                v-model="form.password_required"
                binary
              />
              <label for="passwordRequired" class="font-medium"
                >需要密碼才能加入</label
              >
            </div>
            <small class="text-gray-500 ml-6"
              >開啟後，加入頻道需要輸入密碼</small
            >
          </div>

          <!-- 密碼輸入 -->
          <div v-if="form.allow_join_by_id" class="password-setting ml-6">
            <FloatLabel>
              <Password
                id="joinPassword"
                v-model="form.join_password"
                placeholder="設定頻道密碼"
                :feedback="false"
                toggle-mask
                class="w-full"
                :class="{ 'p-invalid': errors.join_password }"
              />
            </FloatLabel>
            <small v-if="errors.join_password" class="p-error">{{
              errors.join_password
            }}</small>
            <small v-else class="text-gray-500">密碼長度至少6位字符</small>
          </div>
        </div>
      </div>

      <!-- 其他設定 -->
      <div class="other-settings">
        <h4 class="text-lg font-semibold mb-3">其他設定</h4>

        <FloatLabel>
          <InputNumber
            id="maxMembers"
            v-model="form.max_members"
            :min="2"
            :max="10000"
            class="w-full"
            placeholder="最大成員數"
          />
        </FloatLabel>
        <small class="text-gray-500">設定此頻道的最大成員數量限制</small>
      </div>

      <!-- 預覽 -->
      <div v-if="form.name" class="preview-section bg-gray-50 p-4 rounded-lg">
        <h4 class="text-lg font-semibold mb-3">預覽</h4>
        <div class="flex items-center gap-2">
          <i
            :class="form.is_private ? 'pi pi-lock' : 'pi pi-hashtag'"
            class="text-gray-600"
          ></i>
          <span class="font-mono">{{ normalizeChannelName(form.name) }}</span>
          <Badge v-if="form.is_private" value="私人" severity="warn" />
          <Badge
            v-if="form.password_required"
            value="需要密碼"
            severity="info"
          />
        </div>
        <p v-if="form.description" class="text-sm text-gray-600 mt-2">
          {{ form.description }}
        </p>
      </div>
    </div>

    <!-- 錯誤訊息 -->
    <Message v-if="error" severity="error" :closable="false" class="mt-4">
      {{ error }}
    </Message>

    <!-- 操作按鈕 -->
    <template #footer>
      <Button
        label="取消"
        severity="secondary"
        @click="closeDialog"
        :disabled="loading"
      />
      <Button
        label="建立頻道"
        @click="handleCreateChannel"
        :loading="loading"
        :disabled="!isFormValid"
      />
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch } from "vue";
import { useChannelStore } from "~/stores/channel";
import { useUserStore } from "~/stores/user";
import { useToast } from "primevue/usetoast";

// Props & Emits
const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["update:visible", "created"]);

// Stores
const channelStore = useChannelStore();
const userStore = useUserStore();
const toast = useToast();
const config = useRuntimeConfig();

// Reactive data
const form = ref({
  name: "",
  description: "",
  is_private: false,
  allow_join_by_id: false,
  password_required: false,
  join_password: "",
  max_members: 100,
});

const loading = ref(false);
const error = ref("");
const errors = ref({
  name: "",
  join_password: "",
});

// Computed
const isFormValid = computed(() => {
  if (!form.value.name.trim()) return false;
  if (
    form.value.is_private &&
    form.value.password_required &&
    form.value.join_password.length < 6
  )
    return false;
  return !loading.value;
});

// Methods
const normalizeChannelName = (name) => {
  return name
    .toLowerCase()
    .replace(/\s+/g, "-")
    .replace(/[^a-z0-9-]/g, "");
};

const validateForm = () => {
  errors.value = {
    name: "",
    join_password: "",
  };

  if (!form.value.name.trim()) {
    errors.value.name = "頻道名稱不能為空";
    return false;
  }

  // 如果是私群且需要密碼，檢查密碼
  if (
    form.value.is_private &&
    form.value.password_required &&
    form.value.join_password.length < 6
  ) {
    errors.value.join_password = "密碼長度至少6位字符";
    return false;
  }

  return true;
};

const handleCreateChannel = async () => {
  if (!validateForm()) return;

  loading.value = true;
  error.value = "";

  try {
    const channelData = {
      name: normalizeChannelName(form.value.name),
      description: form.value.description,
      is_private: form.value.is_private,
      max_members: form.value.max_members,
    };

    // 如果是私群且設置了密碼
    if (form.value.is_private) {
      channelData.allow_join_by_id = form.value.allow_join_by_id;
      channelData.password_required = form.value.password_required;
      if (form.value.password_required) {
        channelData.join_password = form.value.join_password;
      }
    }

    const response = await $fetch(
      `${config.public.apiBase}/api/v1/chatchannelapi/create-channel`,
      {
        method: "POST",
        credentials: "include",
        headers: {
          Authorization: `Bearer ${userStore.accessToken}`,
          "Content-Type": "application/json",
        },
        body: channelData,
      }
    );

    if (response) {
      toast.add({
        severity: "success",
        summary: "頻道建立成功",
        detail: `頻道「${form.value.name}」已成功建立`,
        life: 3000,
      });

      // 重新載入頻道列表
      await channelStore.fetchChannels();

      // 切換到新建立的頻道
      if (response.data?.id) {
        await channelStore.switchChannel(response.data.id);
      }

      emit("created", response.data);
      closeDialog();
    }
  } catch (err) {
    console.error("建立頻道失敗:", err);
    error.value = err.data?.error || err.message || "建立頻道失敗";

    toast.add({
      severity: "error",
      summary: "建立失敗",
      detail: error.value,
      life: 5000,
    });
  } finally {
    loading.value = false;
  }
};

const closeDialog = () => {
  emit("update:visible", false);
};

const resetForm = () => {
  form.value = {
    name: "",
    description: "",
    is_private: false,
    allow_join_by_id: false,
    password_required: false,
    join_password: "",
    max_members: 100,
  };
  error.value = "";
  errors.value = {
    name: "",
    join_password: "",
  };
};

// Watchers
watch(
  () => props.visible,
  (newValue) => {
    if (newValue) {
      resetForm();
    }
  }
);

// 當私人頻道取消選中時，重置相關設定
watch(
  () => form.value.is_private,
  (newValue) => {
    if (!newValue) {
      form.value.allow_join_by_id = false;
      form.value.password_required = false;
      form.value.join_password = "";
    }
  }
);

// 當關閉 allow_join_by_id 時，也關閉密碼要求
watch(
  () => form.value.allow_join_by_id,
  (newValue) => {
    if (!newValue) {
      form.value.password_required = false;
      form.value.join_password = "";
    }
  }
);

// 當關閉密碼要求時，清空密碼
watch(
  () => form.value.password_required,
  (newValue) => {
    if (!newValue) {
      form.value.join_password = "";
    }
  }
);
</script>

<style scoped>
.space-y-3 > * + * {
  margin-top: 0.75rem;
}

.space-y-4 > * + * {
  margin-top: 1rem;
}

.space-y-6 > * + * {
  margin-top: 1.5rem;
}

.p-error {
  display: block;
  margin-top: 0.25rem;
  color: var(--p-red-500);
  font-size: 0.875rem;
}

.setting-item {
  transition: opacity 0.2s ease-in-out;
}
</style>
