<template>
  <Dialog
    :visible="visible"
    @update:visible="$emit('update:visible', $event)"
    header="加入頻道"
    modal
    class="w-full md:w-96"
  >
    <!-- 頻道ID輸入 -->
    <div class="mb-4">
      <FloatLabel>
        <InputText
          id="channelId"
          v-model="channelId"
          placeholder="輸入頻道ID"
          class="w-full"
          :class="{ 'p-invalid': errors.channelId }"
        />
        <label for="channelId">頻道 ID</label>
      </FloatLabel>
      <small v-if="errors.channelId" class="p-error">{{
        errors.channelId
      }}</small>
    </div>

    <!-- 密碼輸入 -->
    <div class="mb-4">
      <FloatLabel>
        <Password
          id="password"
          v-model="password"
          placeholder="輸入頻道密碼"
          :feedback="false"
          toggle-mask
          class="w-full"
          :class="{ 'p-invalid': errors.password }"
        />
      </FloatLabel>
      <small v-if="errors.password" class="p-error">{{
        errors.password
      }}</small>
    </div>

    <!-- 錯誤訊息 -->
    <Message v-if="error" severity="error" :closable="false" class="mb-4">
      {{ error }}
    </Message>

    <!-- 成功訊息 -->
    <Message
      v-if="successMessage"
      severity="success"
      :closable="false"
      class="mb-4"
    >
      {{ successMessage }}
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
        label="加入頻道"
        @click="joinChannelById"
        :loading="loading"
        :disabled="!isFormValid"
      />
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch } from "vue";
import { useUserStore } from "~/stores/user";
import { useChannelStore } from "~/stores/channel";
import { useToast } from "primevue/usetoast";

// Props & Emits
const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["update:visible", "joined"]);

// Stores
const userStore = useUserStore();
const channelStore = useChannelStore();
const toast = useToast();
const config = useRuntimeConfig();

// Reactive data
const channelId = ref("");
const password = ref("");
const loading = ref(false);
const error = ref("");
const successMessage = ref("");
const errors = ref({
  channelId: "",
  password: "",
});

// Computed
const isFormValid = computed(() => {
  return channelId.value.trim() && !loading.value;
});

// Methods
const validateForm = () => {
  errors.value = {
    channelId: "",
    password: "",
  };

  if (!channelId.value.trim()) {
    errors.value.channelId = "請輸入頻道ID";
    return false;
  }

  // 檢查頻道ID是否為數字
  if (!/^\d+$/.test(channelId.value.trim())) {
    errors.value.channelId = "頻道ID必須是數字";
    return false;
  }

  return true;
};

const joinChannelById = async () => {
  if (!validateForm()) return;

  loading.value = true;
  error.value = "";
  successMessage.value = "";

  try {
    const response = await $fetch(
      `${config.public.apiBase}/api/v1/channelmemberapi/join-by-id`,
      {
        method: "POST",
        credentials: "include",
        headers: {
          Authorization: `Bearer ${userStore.accessToken}`,
          "Content-Type": "application/json",
        },
        body: {
          channel_id: parseInt(channelId.value),
          password: password.value,
        },
      }
    );

    if (response.success) {
      successMessage.value = response.message;

      // 顯示成功 Toast
      toast.add({
        severity: "success",
        summary: "加入成功",
        detail: response.message,
        life: 3000,
      });

      // 重新載入頻道列表
      await channelStore.fetchChannels();

      // 切換到新加入的頻道
      if (response.data?.channel?.id) {
        await channelStore.switchChannel(response.data.channel.id);
      }

      emit("joined", response.data);

      // 延遲關閉對話框讓用戶看到成功訊息
      setTimeout(() => {
        closeDialog();
      }, 2000);
    }
  } catch (err) {
    console.error("加入頻道失敗:", err);
    error.value = err.data?.error || err.message || "加入頻道失敗";

    toast.add({
      severity: "error",
      summary: "加入失敗",
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
  channelId.value = "";
  password.value = "";
  error.value = "";
  successMessage.value = "";
  errors.value = {
    channelId: "",
    password: "",
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
</script>

<style scoped>
.p-dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.p-error {
  display: block;
  margin-top: 0.25rem;
  color: var(--p-red-500);
  font-size: 0.875rem;
}
</style>
