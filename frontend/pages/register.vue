<script setup>
import { useUserStore } from "~/stores/user";

// 設定頁面元資訊
definePageMeta({
  layout: false
});

const userStore = useUserStore();
const router = useRouter();

// 表單資料
const form = reactive({
  username: "",
  first_name: "",
  last_name: "",
  email: "",
  password: "",
  confirmPassword: ""
});

// 表單狀態
const loading = ref(false);
const errors = ref({});
const showPassword = ref(false);
const showConfirmPassword = ref(false);

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
    console.log('正在發送註冊請求...', {
      username: form.username.trim(),
      first_name: form.first_name.trim(),
      last_name: form.last_name.trim(),
      email: form.email.trim()
    });
    
    const result = await userStore.register({
      username: form.username.trim(),
      first_name: form.first_name.trim(),
      last_name: form.last_name.trim(),
      email: form.email.trim(),
      password: form.password
    });
    
    console.log('註冊結果:', result);
    
    if (result.success) {
      // 註冊成功，顯示成功訊息並跳轉
      const toast = useToast();
      toast.add({
        title: "註冊成功！",
        description: "歡迎加入聊天室！",
        icon: "i-heroicons-check-circle",
        color: "green"
      });
      
      // 等待一下再跳轉到登入頁面
      setTimeout(() => {
        router.push('/login');
      }, 2000);
    } else {
      // 顯示註冊失敗的錯誤訊息
      const toast = useToast();
      toast.add({
        title: "註冊失敗",
        description: result.error || userStore.error || "註冊過程中發生錯誤，請稍後再試",
        icon: "i-heroicons-exclamation-triangle",
        color: "red"
      });
      console.error('註冊失敗:', result.error);
    }
  } catch (error) {
    console.error('註冊過程發生錯誤:', error);
    // 顯示網路錯誤訊息
    const toast = useToast();
    toast.add({
      title: "網路錯誤",
      description: "無法連接到服務器，請檢查網路連線",
      icon: "i-heroicons-exclamation-triangle",
      color: "red"
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
      console.error('檢查使用者名稱失敗:', error);
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
    router.push('/chatroom');
  }
});
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
    <div class="max-w-md w-full space-y-8">
      <!-- Logo 和標題 -->
      <div class="text-center">
        <div class="mx-auto w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mb-4">
          <UIcon name="i-heroicons-chat-bubble-left-right" class="w-8 h-8 text-white" />
        </div>
        <h2 class="text-3xl font-bold text-gray-900 mb-2">加入聊天室</h2>
        <p class="text-gray-600">創建您的帳號，開始與大家聊天</p>
      </div>

      <!-- 註冊表單 -->
      <UCard class="shadow-xl">
        <form @submit.prevent="handleRegister" class="space-y-4">
          
          <!-- 使用者名稱 -->
          <div>
            <UFormGroup 
              label="使用者名稱" 
              :error="errors.username"
              required
              help="使用者名稱必須是獨一無二的，至少3個字元，只能包含字母、數字和底線"
            >
              <UInput
                v-model="form.username"
                placeholder="請輸入使用者名稱"
                :loading="checkingUsername"
                :disabled="loading"
                icon="i-heroicons-user"
              />
            </UFormGroup>
          </div>

          <!-- 姓名 -->
          <div class="grid grid-cols-2 gap-4">
            <UFormGroup 
              label="名字" 
              :error="errors.first_name"
              required
            >
              <UInput
                v-model="form.first_name"
                placeholder="名字"
                :disabled="loading"
                icon="i-heroicons-identification"
              />
            </UFormGroup>
            
            <UFormGroup 
              label="姓氏" 
              :error="errors.last_name"
              required
            >
              <UInput
                v-model="form.last_name"
                placeholder="姓氏"
                :disabled="loading"
              />
            </UFormGroup>
          </div>

          <!-- 電子郵件 -->
          <div>
            <UFormGroup 
              label="電子郵件" 
              :error="errors.email"
              required
            >
              <UInput
                v-model="form.email"
                type="email"
                placeholder="請輸入電子郵件"
                :disabled="loading"
                icon="i-heroicons-envelope"
              />
            </UFormGroup>
          </div>

          <!-- 密碼 -->
          <div>
            <UFormGroup 
              label="密碼" 
              :error="errors.password"
              required
            >
              <UInput
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="請輸入密碼"
                :disabled="loading"
                icon="i-heroicons-lock-closed"
              >
                <template #trailing>
                  <UButton
                    @click="showPassword = !showPassword"
                    variant="ghost"
                    size="xs"
                    :icon="showPassword ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'"
                  />
                </template>
              </UInput>
            </UFormGroup>
          </div>

          <!-- 確認密碼 -->
          <div>
            <UFormGroup 
              label="確認密碼" 
              :error="errors.confirmPassword"
              required
            >
              <UInput
                v-model="form.confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                placeholder="請再次輸入密碼"
                :disabled="loading"
                icon="i-heroicons-lock-closed"
              >
                <template #trailing>
                  <UButton
                    @click="showConfirmPassword = !showConfirmPassword"
                    variant="ghost"
                    size="xs"
                    :icon="showConfirmPassword ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'"
                  />
                </template>
              </UInput>
            </UFormGroup>
          </div>

          <!-- 密碼強度指示 -->
          <div v-if="form.password" class="text-xs text-gray-500">
            <div class="flex items-center gap-2 mt-1">
              <div class="flex space-x-1">
                <div 
                  v-for="i in 4" 
                  :key="i"
                  class="w-2 h-2 rounded-full"
                  :class="{
                    'bg-red-300': form.password.length < 6,
                    'bg-green-300': form.password.length >= 6,
                    'bg-gray-200': form.password.length === 0
                  }"
                />
              </div>
              <span class="text-xs">
                {{ form.password.length < 6 ? '弱' : '強' }}
              </span>
            </div>
          </div>

          <!-- 錯誤訊息 -->
          <UAlert
            v-if="userStore.error"
            icon="i-heroicons-exclamation-triangle"
            color="red"
            variant="soft"
            :title="userStore.error"
            class="mb-4"
          />

          <!-- 註冊按鈕 -->
          <UButton
            type="submit"
            size="lg"
            :loading="loading"
            :disabled="loading"
            block
            icon="i-heroicons-user-plus"
          >
            {{ loading ? '註冊中...' : '創建帳號' }}
          </UButton>
        </form>
      </UCard>

      <!-- 登入連結 -->
      <div class="text-center">
        <p class="text-gray-600">
          已經有帳號了？
          <NuxtLink 
            to="/login" 
            class="font-medium text-blue-600 hover:text-blue-500 transition-colors"
          >
            立即登入
          </NuxtLink>
        </p>
      </div>

      <!-- 服務條款 -->
      <div class="text-center text-xs text-gray-500">
        <p>
          註冊即表示您同意我們的
          <a href="#" class="text-blue-600 hover:text-blue-500">服務條款</a>
          和
          <a href="#" class="text-blue-600 hover:text-blue-500">隱私政策</a>
        </p>
      </div>
    </div>
  </div>
</template>