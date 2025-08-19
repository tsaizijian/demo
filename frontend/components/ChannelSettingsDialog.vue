<template>
  <Dialog
    :visible="visible"
    @update:visible="$emit('update:visible', $event)"
    header="頻道設定"
    modal
    class="w-full md:w-[600px]"
  >
    <div class="space-y-6">
      <!-- 基本設定 -->
      <div class="basic-settings mb-6">
        <h4 class="text-lg font-semibold mb-3">基本設定</h4>

        <div class="space-y-4">
          <FloatLabel>
            <InputText
              id="channelName"
              v-model="form.name"
              class="w-full"
              :class="{ 'p-invalid': errors.name }"
              placeholder="頻道名稱"
            />
          </FloatLabel>
          <small v-if="errors.name" class="p-error">{{ errors.name }}</small>

          <FloatLabel>
            <Textarea
              id="description"
              v-model="form.description"
              rows="3"
              class="w-full"
              placeholder="頻道描述"
            />
          </FloatLabel>
        </div>
      </div>

      <!-- 隱私設定 -->
      <div class="privacy-settings">
        <h4 class="text-lg font-semibold mb-3">隱私設定</h4>

        <div class="space-y-3">
          <div class="flex items-center gap-3">
            <Checkbox
              id="isPrivate"
              v-model="form.is_private"
              binary
              :disabled="true"
            />
            <label for="isPrivate" class="font-medium text-gray-500">
              {{ form.is_private ? "私人頻道" : "公開頻道" }}
            </label>
          </div>
          <small class="text-gray-500 ml-6">頻道建立後無法更改隱私設定</small>
        </div>
      </div>

      <!-- 密碼設定 (僅私人頻道) -->
      <div v-if="form.is_private" class="password-settings">
        <h4 class="text-lg font-semibold mb-3">密碼設定</h4>

        <div class="space-y-4">
          <!-- 密碼輸入 -->
          <div class="password-setting">
            <FloatLabel>
              <Password
                id="joinPassword"
                v-model="form.join_password"
                placeholder="設定或更新頻道密碼"
                :feedback="false"
                toggle-mask
                class="w-full"
                :class="{ 'p-invalid': errors.join_password }"
              />
            </FloatLabel>
            <small v-if="errors.join_password" class="p-error">{{
              errors.join_password
            }}</small>
            <small v-else class="text-gray-500">留空表示不更改現有密碼</small>
          </div>
        </div>
      </div>

      <!-- 頻道資訊顯示 -->
      <div class="channel-info border-t pt-4">
        <h4 class="text-lg font-semibold mb-3">頻道資訊</h4>
        <div class="bg-gray-50 p-4 rounded-lg space-y-3">
          <div class="flex items-center justify-between">
            <div>
              <span class="font-medium">頻道 ID:</span>
              <span class="ml-2 font-mono text-lg">{{
                channel?.id || "N/A"
              }}</span>
            </div>
            <Button
              label="複製ID"
              size="small"
              severity="secondary"
              @click="copyChannelId"
            />
          </div>

          <div>
            <span class="font-medium">成員數量:</span>
            <span class="ml-2">{{ channel?.member_count || 0 }} 人</span>
          </div>

          <!-- 密碼狀態顯示 (僅私人頻道) -->
          <div v-if="form.is_private">
            <span class="font-medium">密碼狀態:</span>
            <span class="ml-2 text-gray-500">
              {{ channel?.password_required ? "已設定密碼" : "未設定密碼" }}
            </span>
          </div>
        </div>
      </div>

      <!-- 管理員列表 -->
      <div v-if="isOwnerOrAdmin" class="admin-info border-t pt-4">
        <h4 class="text-lg font-semibold mb-3">管理團隊</h4>
        <div class="bg-blue-50 p-4 rounded-lg">
          <div v-if="loadingAdmins" class="text-center py-2">
            <ProgressSpinner size="20px" />
            <span class="ml-2 text-sm">載入中...</span>
          </div>

          <div v-else-if="adminList.length === 0" class="text-gray-500 text-sm">
            暫無管理員資訊
          </div>

          <div v-else class="space-y-2">
            <div
              v-for="admin in adminList"
              :key="admin.user_id"
              class="flex items-center justify-between bg-white p-2 rounded"
            >
              <div class="flex items-center gap-2">
                <Avatar
                  :label="admin.display_name ? admin.display_name[0] : 'U'"
                  :class="{
                    'bg-yellow-100 text-yellow-700': admin.role === 'owner',
                    'bg-blue-100 text-blue-700': admin.role === 'admin',
                  }"
                  size="small"
                />
                <div>
                  <div class="font-medium text-sm">
                    {{ admin.display_name || admin.username }}
                  </div>
                  <div class="text-xs text-gray-500">@{{ admin.username }}</div>
                </div>
              </div>
              <Badge
                :value="admin.role === 'owner' ? '創建者' : '管理員'"
                :severity="admin.role === 'owner' ? 'warn' : 'info'"
                size="small"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- 成員限制設定 -->
      <div class="member-limit-settings">
        <h4 class="text-lg font-semibold mb-3">成員限制</h4>

        <FloatLabel>
          <InputNumber
            id="maxMembers"
            v-model="form.max_members"
            :min="1"
            :max="10000"
            class="w-full"
            placeholder="最大成員數"
          />
        </FloatLabel>
        <small class="text-gray-500">設定此頻道的最大成員數量限制</small>
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
        label="儲存設定"
        @click="saveSettings"
        :loading="loading"
        :disabled="!hasChanges"
      />
    </template>
  </Dialog>

  <!-- 密碼重置對話框 -->
  <Dialog
    :visible="showResetPasswordDialog"
    @update:visible="showResetPasswordDialog = $event"
    header="重置頻道密碼"
    modal
    class="w-full md:w-[400px]"
  >
    <Message severity="warn" :closable="false" class="mb-4">
      ⚠️ 重置後舊密碼將失效，請將新密碼告知需要加入的成員
    </Message>

    <FloatLabel>
      <Password
        id="newPassword"
        v-model="resetPassword"
        placeholder="設定新密碼"
        :feedback="false"
        toggle-mask
        class="w-full"
        :class="{ 'p-invalid': resetPasswordError }"
      />
      <label for="newPassword">新密碼</label>
    </FloatLabel>
    <small v-if="resetPasswordError" class="p-error">{{
      resetPasswordError
    }}</small>
    <small v-else class="text-gray-500">密碼長度至少6位字符</small>

    <template #footer>
      <Button
        label="取消"
        severity="secondary"
        @click="closeResetPasswordDialog"
        :disabled="resettingPassword"
      />
      <Button
        label="重置密碼"
        severity="warn"
        @click="resetChannelPassword"
        :loading="resettingPassword"
        :disabled="!resetPassword || resetPassword.length < 6"
      />
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch, nextTick } from "vue";
import { useChannelStore } from "~/stores/channel";
import { useUserStore } from "~/stores/user";
import { useToast } from "primevue/usetoast";

// Props & Emits
const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
  channel: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(["update:visible", "updated"]);

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
  join_password: "",
  max_members: 100,
});

const originalForm = ref({});
const loading = ref(false);
const error = ref("");
const errors = ref({
  name: "",
  join_password: "",
});

// 管理員資訊
const adminList = ref([]);
const loadingAdmins = ref(false);
const currentUserRole = ref("");

// 密碼重置
const showResetPasswordDialog = ref(false);
const resetPassword = ref("");
const resetPasswordError = ref("");
const resettingPassword = ref(false);

// Computed
const hasChanges = computed(() => {
  return JSON.stringify(form.value) !== JSON.stringify(originalForm.value);
});

const isOwnerOrAdmin = computed(() => {
  return currentUserRole.value === "owner" || currentUserRole.value === "admin";
});

const canResetPassword = computed(() => {
  return currentUserRole.value === "owner" || currentUserRole.value === "admin";
});

// Methods
const validateForm = () => {
  errors.value = {
    name: "",
    join_password: "",
  };

  if (!form.value.name.trim()) {
    errors.value.name = "頻道名稱不能為空";
    return false;
  }

  if (
    form.value.is_private &&
    form.value.join_password &&
    form.value.join_password.length < 6
  ) {
    errors.value.join_password = "密碼長度至少6位字符";
    return false;
  }

  return true;
};

const saveSettings = async () => {
  if (!validateForm()) return;

  loading.value = true;
  error.value = "";

  try {
    // 準備更新資料 - 包含所有設定
    const updateData = {
      name: form.value.name,
      description: form.value.description,
      max_members: form.value.max_members,
    };

    // 如果是私人頻道，包含私人頻道相關設定
    if (form.value.is_private) {
      updateData.allow_join_by_id = form.value.allow_join_by_id;
      updateData.password_required = form.value.password_required;
    }

    // 先更新基本設定
    const response = await $fetch(
      `${config.public.apiBase}/api/v1/chatchannelapi/${props.channel.id}`,
      {
        method: "PUT",
        credentials: "include",
        headers: {
          Authorization: `Bearer ${userStore.accessToken}`,
          "Content-Type": "application/json",
        },
        body: updateData,
      }
    );

    // 如果是私人頻道且有密碼更改，單獨處理密碼更新
    if (
      form.value.is_private &&
      form.value.join_password &&
      form.value.join_password.trim()
    ) {
      await $fetch(
        `${config.public.apiBase}/api/v1/channelmemberapi/channel/${props.channel.id}/reset-password`,
        {
          method: "POST",
          credentials: "include",
          headers: {
            Authorization: `Bearer ${userStore.accessToken}`,
            "Content-Type": "application/json",
          },
          body: {
            new_password: form.value.join_password.trim(),
          },
        }
      );
    }

    if (response) {
      toast.add({
        severity: "success",
        summary: "設定已儲存",
        detail: "頻道設定更新成功",
        life: 3000,
      });

      // 重新載入頻道資料
      await channelStore.fetchChannels();

      emit("updated", response);
      closeDialog();
    }
  } catch (err) {
    console.error("儲存設定失敗:", err);
    error.value = err.data?.error || err.message || "儲存失敗";

    toast.add({
      severity: "error",
      summary: "儲存失敗",
      detail: error.value,
      life: 5000,
    });
  } finally {
    loading.value = false;
  }
};

const copyChannelId = async () => {
  if (!props.channel?.id) return;

  try {
    await navigator.clipboard.writeText(props.channel.id.toString());
    toast.add({
      severity: "success",
      summary: "已複製",
      detail: `頻道ID ${props.channel.id} 已複製到剪貼板`,
      life: 2000,
    });
  } catch (err) {
    console.error("複製失敗:", err);
    toast.add({
      severity: "error",
      summary: "複製失敗",
      detail: "無法複製到剪貼板",
      life: 3000,
    });
  }
};

const closeDialog = () => {
  emit("update:visible", false);
};

const fetchAdminInfo = async () => {
  if (!props.channel?.id) return;

  loadingAdmins.value = true;
  try {
    const response = await $fetch(
      `${config.public.apiBase}/api/v1/channelmemberapi/channel/${props.channel.id}/info`,
      {
        credentials: "include",
        headers: {
          Authorization: `Bearer ${userStore.accessToken}`,
          "Content-Type": "application/json",
        },
      }
    );

    if (response.success) {
      adminList.value = response.data.admins || [];

      // 找到當前用戶的角色
      const currentUser = adminList.value.find(
        (admin) => admin.user_id === userStore.userProfile?.user_id
      );
      currentUserRole.value = currentUser?.role || "";
    }
  } catch (error) {
    console.error("獲取管理員資訊失敗:", error);
    // 如果權限不足，不顯示錯誤訊息
    if (error.status !== 403) {
      toast.add({
        severity: "error",
        summary: "載入失敗",
        detail: "無法載入管理員資訊",
        life: 3000,
      });
    }
  } finally {
    loadingAdmins.value = false;
  }
};

const resetChannelPassword = async () => {
  if (!resetPassword.value || resetPassword.value.length < 6) {
    resetPasswordError.value = "密碼長度至少6位字符";
    return;
  }

  resettingPassword.value = true;
  resetPasswordError.value = "";

  try {
    const response = await $fetch(
      `${config.public.apiBase}/api/v1/channelmemberapi/channel/${props.channel.id}/reset-password`,
      {
        method: "POST",
        credentials: "include",
        headers: {
          Authorization: `Bearer ${userStore.accessToken}`,
          "Content-Type": "application/json",
        },
        body: {
          new_password: resetPassword.value,
        },
      }
    );

    if (response.success) {
      toast.add({
        severity: "success",
        summary: "密碼重置成功",
        detail: `新密碼：${response.data.new_password}`,
        life: 10000, // 顯示較長時間讓用戶記錄
      });

      // 自動複製新密碼到剪貼板
      try {
        await navigator.clipboard.writeText(response.data.new_password);
        toast.add({
          severity: "info",
          summary: "新密碼已複製",
          detail: "請將密碼分享給需要加入的成員",
          life: 5000,
        });
      } catch (err) {
        console.error("自動複製失敗:", err);
      }

      closeResetPasswordDialog();
    }
  } catch (err) {
    console.error("重置密碼失敗:", err);
    resetPasswordError.value = err.data?.error || err.message || "重置失敗";

    toast.add({
      severity: "error",
      summary: "重置失敗",
      detail: resetPasswordError.value,
      life: 5000,
    });
  } finally {
    resettingPassword.value = false;
  }
};

const closeResetPasswordDialog = () => {
  showResetPasswordDialog.value = false;
  resetPassword.value = "";
  resetPasswordError.value = "";
};

const initForm = () => {
  if (props.channel) {
    form.value = {
      name: props.channel.name || "",
      description: props.channel.description || "",
      is_private: props.channel.is_private || false,
      join_password: "", // 不顯示現有密碼
      max_members: props.channel.max_members || 100,
    };

    // 保存原始表單狀態
    originalForm.value = { ...form.value };
  }
};

const resetForm = () => {
  form.value = {
    name: "",
    description: "",
    is_private: false,
    join_password: "",
    max_members: 100,
  };
  originalForm.value = { ...form.value };
  error.value = "";
  errors.value = {
    name: "",
    join_password: "",
  };

  // 重置管理員相關資料
  adminList.value = [];
  currentUserRole.value = "";
  loadingAdmins.value = false;
};

// Watchers
watch(
  () => props.visible,
  (newValue) => {
    if (newValue) {
      nextTick(() => {
        initForm();
        fetchAdminInfo(); // 載入管理員資訊
      });
    } else {
      resetForm();
    }
  }
);

watch(
  () => props.channel,
  () => {
    if (props.visible) {
      initForm();
      fetchAdminInfo(); // 載入管理員資訊
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
