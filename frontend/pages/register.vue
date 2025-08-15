<script setup>
import Card from "primevue/card";
import InputText from "primevue/inputtext";
import Password from "primevue/password";
import Button from "primevue/button";
import Message from "primevue/message";
import { useUserStore } from "~/stores/user";
import { useToast } from "primevue/usetoast";

// 設定頁面元資訊
definePageMeta({
  layout: "default",
});

const userStore = useUserStore();
const toast = useToast();

// 表單資料
const form = reactive({
  username: "",
  first_name: "",
  last_name: "",
  email: "",
  password: "",
  confirmPassword: "",
});

// 表單狀態
const loading = ref(false);
const errors = ref({});

// 表單驗證規則
const validateForm = () => {
  errors.value = {};

  // 使用者名稱驗證
  if (!form.username.trim()) {
    errors.value.username = "使用者名稱為必填";
  } else if (form.username.length < 3) {
    errors.value.username = "使用者名稱至少需要3個字元";
  } else if (!/^[a-zA-Z0-9_]+$/.test(form.username)) {
    errors.value.username = "使用者名稱只能包含字母、數字和底線";
  }

  // 姓名驗證
  if (!form.first_name.trim()) {
    errors.value.first_name = "名字為必填";
  }

  if (!form.last_name.trim()) {
    errors.value.last_name = "姓氏為必填";
  }

  // 電子郵件驗證
  if (!form.email.trim()) {
    errors.value.email = "電子郵件為必填";
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    errors.value.email = "請輸入有效的電子郵件格式";
  }

  // 密碼驗證
  if (!form.password) {
    errors.value.password = "密碼為必填";
  } else if (form.password.length < 6) {
    errors.value.password = "密碼至少需要6個字元";
  }

  // 確認密碼驗證
  if (!form.confirmPassword) {
    errors.value.confirmPassword = "請確認密碼";
  } else if (form.password !== form.confirmPassword) {
    errors.value.confirmPassword = "密碼不一致";
  }

  return Object.keys(errors.value).length === 0;
};

// 處理註冊
const handleRegister = async () => {
  // 清除之前的錯誤
  userStore.error = null;

  if (!validateForm()) return;

  loading.value = true;

  try {
    console.log("正在發送註冊請求...", {
      username: form.username.trim(),
      first_name: form.first_name.trim(),
      last_name: form.last_name.trim(),
      email: form.email.trim(),
    });

    const result = await userStore.register({
      username: form.username.trim(),
      first_name: form.first_name.trim(),
      last_name: form.last_name.trim(),
      email: form.email.trim(),
      password: form.password,
    });

    console.log("註冊結果:", result);

    if (result.success) {
      // 註冊成功，顯示成功訊息並跳轉
      toast.add({
        severity: "success",
        summary: "註冊成功",
        detail: "您的帳號已成功建立，請登入。",
        life: 3000,
      });
      // 等待一下再跳轉到登入頁面
      setTimeout(() => {
        navigateTo("/login");
      }, 2000);
    } else {
      // 顯示註冊失敗的錯誤訊息

      toast.add({
        severity: "error",
        summary: "註冊失敗",
        detail:
          result.error || userStore.error || "註冊過程中發生錯誤，請稍後再試",
        life: 5000,
      });
      console.error("註冊失敗:", result.error);
    }
  } catch (error) {
    console.error("註冊過程發生錯誤:", error);
    // 顯示網路錯誤訊息
    toast.add({
      severity: "error",
      summary: "網路錯誤",
      detail: "無法連接到服務器，請檢查網路連線",
      life: 5000,
    });
  } finally {
    loading.value = false;
  }
};

// 檢查使用者名稱是否可用（防抖處理）
const checkUsernameTimeout = ref(null);
const checkingUsername = ref(false);

const checkUsername = async () => {
  if (!form.username.trim() || form.username.length < 3) return;

  clearTimeout(checkUsernameTimeout.value);
  checkUsernameTimeout.value = setTimeout(async () => {
    checkingUsername.value = true;

    try {
      const result = await userStore.checkUsername(form.username.trim());
      if (!result.available) {
        errors.value.username = "此使用者名稱已被使用";
      } else if (errors.value.username === "此使用者名稱已被使用") {
        delete errors.value.username;
      }
    } catch (error) {
      console.error("檢查使用者名稱失敗:", error);
    } finally {
      checkingUsername.value = false;
    }
  }, 500);
};

// 監聽使用者名稱變化
watch(() => form.username, checkUsername);

// 如果已經登入，導向聊天室
onMounted(() => {
  if (userStore.isAuthenticated) {
    navigateTo("/chatroom");
  }
});
</script>

<template>
  <div class="flex items-center justify-center py-12 px-4 bg-gray-50">
    <div class="mx-auto max-w-md w-full">
      <ClientOnly>
        <Card class="shadow-lg border border-gray-200">
          <template #header>
            <div class="text-center">
              <h2 class="text-2xl font-semibold text-gray-900 mb-2">
                註冊新帳號
              </h2>
              <hr class="border-gray-200" />
            </div>
          </template>
          <template #content>
            <div class="registration-form">
              <form @submit.prevent="handleRegister">
                <!-- 名字 -->
                <div class="form-group">
                  <label for="first_name" class="form-label">名字 *</label>
                  <div class="input-text">
                    <InputText
                      id="first_name"
                      v-model="form.first_name"
                      type="text"
                      placeholder="請輸入名字"
                      :disabled="loading"
                      class="w-full"
                    />
                  </div>
                </div>
                <p v-if="errors.first_name" class="error-text">
                  {{ errors.first_name }}
                </p>

                <!-- 姓氏 -->
                <div class="form-group">
                  <label for="last_name" class="form-label">姓氏 *</label>
                  <div class="input-text">
                    <InputText
                      id="last_name"
                      v-model="form.last_name"
                      type="text"
                      placeholder="請輸入姓氏"
                      :disabled="loading"
                      class="w-full"
                    />
                  </div>
                </div>
                <p v-if="errors.last_name" class="error-text">
                  {{ errors.last_name }}
                </p>

                <!-- 電子郵件 -->
                <div class="form-group">
                  <label for="email" class="form-label">電子郵件 *</label>
                  <div class="input-text">
                    <InputText
                      id="email"
                      v-model="form.email"
                      type="email"
                      placeholder="請輸入電子郵件"
                      :disabled="loading"
                      class="w-full"
                    />
                  </div>
                </div>
                <p v-if="errors.email" class="error-text">{{ errors.email }}</p>

                <!-- 登入帳號 -->
                <div class="form-group">
                  <label for="username" class="form-label">登入帳號 *</label>
                  <div class="input-text">
                    <InputText
                      id="username"
                      v-model="form.username"
                      type="text"
                      placeholder="聊天室使用帳號"
                      :disabled="loading"
                      :loading="checkingUsername"
                      class="w-full"
                    />
                  </div>
                </div>
                <p v-if="errors.username" class="error-text">
                  {{ errors.username }}
                </p>

                <!-- 帳號密碼 -->
                <div class="form-group">
                  <label for="password" class="form-label">帳號密碼 *</label>
                  <div class="input-text password-field">
                    <Password
                      input-id="password"
                      v-model="form.password"
                      placeholder="聊天室帳號密碼"
                      :disabled="loading"
                      autocomplete="new-password"
                      class="w-full"
                      :feedback="false"
                      toggleMask
                    />
                  </div>
                </div>
                <p v-if="errors.password" class="error-text">
                  {{ errors.password }}
                </p>

                <!-- 重複密碼 -->
                <div class="form-group">
                  <label for="confirmPassword" class="form-label"
                    >重複密碼 *</label
                  >
                  <div class="input-text password-field">
                    <Password
                      input-id="confirmPassword"
                      v-model="form.confirmPassword"
                      placeholder="再次輸入密碼"
                      :disabled="loading"
                      autocomplete="new-password"
                      class="w-full"
                      :feedback="false"
                      toggleMask
                    />
                  </div>
                </div>
                <p v-if="errors.confirmPassword" class="error-text">
                  {{ errors.confirmPassword }}
                </p>

                <!-- 按鈕組 -->
                <div class="button-group">
                  <Button
                    class="cancel-button"
                    severity="secondary"
                    @click="navigateTo('/login')"
                    :disabled="loading"
                    outlined
                    label="取消"
                  />
                  <Button
                    type="submit"
                    class="register-button"
                    :loading="loading"
                    :disabled="loading"
                    :label="loading ? '註冊中...' : '註冊'"
                  />
                </div>
              </form>

              <!-- 錯誤訊息 -->
              <Message
                v-if="userStore.error"
                severity="error"
                :closable="false"
                class="my-4"
              >
                {{ userStore.error }}
              </Message>
            </div>
          </template>
        </Card>
      </ClientOnly>
    </div>
  </div>
</template>

<style scoped>
.registration-form {
  display: flex;
  flex-direction: column;
  align-items: center;
  white-space: nowrap;
}

.form-group {
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  width: 100%;
  justify-content: space-between;
  font-weight: 550;
}

.form-label {
  display: block;
  font-weight: 550;
  color: #374151;
  min-width: 100px;
  text-align: left;
}

.input-text {
  padding: 5px;
  margin-left: 10px;
  width: 280px;
}

.error-text {
  color: #dc2626;
  font-size: 0.875rem;
  margin-top: 4px;
  margin-left: 110px;
  width: 280px;
  text-align: left;
}

.button-group {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-top: 2rem;
}

.cancel-button {
  padding: 0 2rem;
}

.register-button {
  padding: 0 2rem;
}

h2 {
  text-align: center;
  color: #1f2937;
}

/* PrimeVue Password 自定義樣式 */
.password-field :deep(.p-password) {
  width: 100%;
}

.password-field :deep(.p-password .p-inputtext) {
  width: 100%;
}

/* PrimeVue Card 自定義樣式 */
:deep(.p-card) {
  border-radius: 12px;
}

:deep(.p-card .p-card-content) {
  padding: 1.5rem;
}

/* PrimeVue Button 自定義樣式 */
:deep(.p-button) {
  border-radius: 8px;
  font-weight: 600;
}

/* PrimeVue InputText 自定義樣式 */
:deep(.p-inputtext) {
  border-radius: 8px;
}

/* PrimeVue Message 自定義樣式 */
:deep(.p-message) {
  border-radius: 8px;
}
</style>
