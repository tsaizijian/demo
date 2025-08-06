<template>
  <div
    class="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50 relative overflow-hidden flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8"
  >
    <!-- Background decoration -->
    <div
      class="absolute inset-0 bg-grid-slate-100 bg-[size:20px_20px] opacity-20"
    ></div>
    <div
      class="absolute top-20 left-10 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"
    ></div>
    <div
      class="absolute bottom-20 right-10 w-72 h-72 bg-blue-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"
    ></div>
    <div
      class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-72 h-72 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"
    ></div>

    <div class="relative z-10 max-w-lg w-full">
      <!-- Header -->
      <div class="text-center mb-8 animate-fade-in">
        <div
          class="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl mb-6 shadow-lg"
        >
          <svg
            class="w-[32px] h-[32px] text-white"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"
            ></path>
          </svg>
        </div>

        <h2
          class="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent mb-2"
        >
          加入我們
        </h2>
        <p class="text-gray-600">
          已有帳號？
          <NuxtLink
            to="/login"
            class="font-semibold text-purple-600 hover:text-purple-700 transition-colors"
          >
            立即登入
          </NuxtLink>
        </p>
      </div>

      <!-- Register Form Card -->
      <div
        class="bg-white/80 backdrop-blur-sm rounded-3xl shadow-2xl border border-gray-100 p-8 animate-slide-up"
      >
        <form class="space-y-6" @submit.prevent="handleRegister">
          <!-- Username Field -->
          <div class="space-y-2">
            <label
              for="username"
              class="block text-sm font-semibold text-gray-700"
              >使用者名稱</label
            >
            <div class="relative group">
              <div
                class="absolute top-1/2 left-3 transform -translate-y-1/2 text-gray-400 pointer-events-none"
              >
                <svg
                  class="w-5 h-5 group-focus-within:text-purple-500 transition-colors"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                  />
                </svg>
              </div>
              <input
                id="username"
                v-model="registerForm.username"
                name="username"
                type="text"
                required
                class="block w-full pl-10 pr-3 py-3 border border-gray-200 rounded-xl text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200 bg-gray-50 focus:bg-white"
                :class="{
                  'border-red-300 bg-red-50': usernameError,
                  'border-green-300 bg-green-50': usernameValid,
                }"
                placeholder="請輸入使用者名稱"
                @blur="checkUsernameAvailability"
              />
              <div
                v-if="usernameValid"
                class="absolute inset-y-0 right-0 pr-3 flex items-center"
              >
                <svg
                  class="w-[20px] h-[20px] text-green-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M5 13l4 4L19 7"
                  ></path>
                </svg>
              </div>
            </div>
            <p
              v-if="usernameError"
              class="text-sm text-red-600 animate-fade-in"
            >
              {{ usernameError }}
            </p>
            <p
              v-if="usernameValid"
              class="text-sm text-green-600 animate-fade-in"
            >
              ✓ 使用者名稱可用
            </p>
          </div>

          <!-- Email Field -->
          <div class="space-y-2">
            <label for="email" class="block text-sm font-semibold text-gray-700"
              >電子郵件</label
            >
            <div class="relative group">
              <div
                class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none"
              >
                <svg
                  class="w-[20px] h-[20px] text-gray-400 group-focus-within:text-purple-500 transition-colors"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207"
                  ></path>
                </svg>
              </div>
              <input
                id="email"
                v-model="registerForm.email"
                name="email"
                type="email"
                required
                class="block w-full pl-10 pr-3 py-3 border border-gray-200 rounded-xl text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200 bg-gray-50 focus:bg-white"
                :class="{
                  'border-red-300 bg-red-50': emailError,
                  'border-green-300 bg-green-50': emailValid,
                }"
                placeholder="請輸入電子郵件"
                @blur="checkEmailAvailability"
              />
              <div
                v-if="emailValid"
                class="absolute inset-y-0 right-0 pr-3 flex items-center"
              >
                <svg
                  class="w-[20px] h-[20px] text-green-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M5 13l4 4L19 7"
                  ></path>
                </svg>
              </div>
            </div>
            <p v-if="emailError" class="text-sm text-red-600 animate-fade-in">
              {{ emailError }}
            </p>
            <p v-if="emailValid" class="text-sm text-green-600 animate-fade-in">
              ✓ 電子郵件可用
            </p>
          </div>

          <!-- Password Field -->
          <div class="space-y-2">
            <label
              for="password"
              class="block text-sm font-semibold text-gray-700"
              >密碼</label
            >
            <div class="relative group">
              <div
                class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none"
              >
                <svg
                  class="w-[20px] h-[20px] text-gray-400 group-focus-within:text-purple-500 transition-colors"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                  ></path>
                </svg>
              </div>
              <input
                id="password"
                v-model="registerForm.password"
                name="password"
                type="password"
                required
                class="block w-full pl-10 pr-3 py-3 border border-gray-200 rounded-xl text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200 bg-gray-50 focus:bg-white"
                placeholder="請輸入密碼（至少8位）"
              />
            </div>
            <div class="flex items-center justify-between text-xs">
              <span class="text-gray-500"
                >密碼強度：
                <span :class="passwordStrengthClass" class="font-medium">{{
                  passwordStrengthText
                }}</span>
              </span>
              <div class="flex space-x-1">
                <div
                  v-for="i in 5"
                  :key="i"
                  class="h-1 w-4 rounded-full transition-colors duration-200"
                  :class="
                    i <= passwordStrength
                      ? passwordStrengthClass.replace('text-', 'bg-')
                      : 'bg-gray-200'
                  "
                ></div>
              </div>
            </div>
          </div>

          <!-- Confirm Password Field -->
          <div class="space-y-2">
            <label
              for="confirmPassword"
              class="block text-sm font-semibold text-gray-700"
              >確認密碼</label
            >
            <div class="relative group">
              <div
                class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none"
              >
                <svg
                  class="w-[20px] h-[20px] text-gray-400 group-focus-within:text-purple-500 transition-colors"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  ></path>
                </svg>
              </div>
              <input
                id="confirmPassword"
                v-model="registerForm.confirmPassword"
                name="confirmPassword"
                type="password"
                required
                class="block w-full pl-10 pr-3 py-3 border border-gray-200 rounded-xl text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200 bg-gray-50 focus:bg-white"
                :class="{
                  'border-red-300 bg-red-50': passwordMismatch,
                  'border-green-300 bg-green-50':
                    registerForm.confirmPassword && !passwordMismatch,
                }"
                placeholder="請再次輸入密碼"
              />
              <div
                v-if="registerForm.confirmPassword && !passwordMismatch"
                class="absolute inset-y-0 right-0 pr-3 flex items-center"
              >
                <svg
                  class="w-[20px] h-[20px] text-green-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M5 13l4 4L19 7"
                  ></path>
                </svg>
              </div>
            </div>
            <p
              v-if="passwordMismatch"
              class="text-sm text-red-600 animate-fade-in"
            >
              密碼不相符
            </p>
          </div>

          <!-- Terms Agreement -->
          <div class="flex items-start pt-2">
            <div class="flex items-center h-5">
              <input
                id="agree-terms"
                v-model="registerForm.agreeTerms"
                name="agree-terms"
                type="checkbox"
                required
                class="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded transition-colors"
              />
            </div>
            <div class="ml-3 text-sm">
              <label for="agree-terms" class="text-gray-700">
                我同意
                <a
                  href="#"
                  class="font-semibold text-purple-600 hover:text-purple-700 transition-colors"
                  >服務條款</a
                >
                和
                <a
                  href="#"
                  class="font-semibold text-purple-600 hover:text-purple-700 transition-colors"
                  >隱私政策</a
                >
              </label>
            </div>
          </div>

          <!-- Submit Button -->
          <div class="pt-4">
            <button
              type="submit"
              :disabled="isLoading || !isFormValid"
              class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-base font-semibold rounded-xl text-white bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-[1.02] transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              <span
                v-if="isLoading"
                class="absolute left-0 inset-y-0 flex items-center pl-3"
              >
                <svg
                  class="animate-spin w-[20px] h-[20px] text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    class="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    stroke-width="4"
                  ></circle>
                  <path
                    class="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
              </span>
              <span class="flex items-center">
                <svg
                  v-if="!isLoading"
                  class="w-[20px] h-[20px] mr-[8px] group-hover:animate-pulse"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"
                  ></path>
                </svg>
                {{ isLoading ? "註冊中..." : "立即註冊" }}
              </span>
            </button>
          </div>

          <!-- Error Message -->
          <div
            v-if="errorMessage"
            class="animate-shake bg-red-50 border border-red-200 rounded-xl p-4"
          >
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg
                  class="w-[20px] h-[20px] text-red-400"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fill-rule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z"
                    clip-rule="evenodd"
                  />
                </svg>
              </div>
              <div class="ml-3">
                <h3 class="text-sm font-semibold text-red-800">註冊失敗</h3>
                <div class="mt-1 text-sm text-red-700">{{ errorMessage }}</div>
              </div>
            </div>
          </div>

          <!-- Success Message -->
          <div
            v-if="successMessage"
            class="animate-bounce-in bg-green-50 border border-green-200 rounded-xl p-4"
          >
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg
                  class="w-[20px] h-[20px] text-green-400"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fill-rule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.236 4.53L7.53 10.23a.75.75 0 00-1.06 1.06l2.5 2.5a.75.75 0 001.137-.089l4-5.5z"
                    clip-rule="evenodd"
                  />
                </svg>
              </div>
              <div class="ml-3">
                <h3 class="text-sm font-semibold text-green-800">註冊成功</h3>
                <div class="mt-1 text-sm text-green-700">
                  {{ successMessage }}
                </div>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
const config = useRuntimeConfig();
const { $api } = useNuxtApp();

useSeoMeta({
  title: "註冊 - 聊天室應用",
  description: "註冊聊天室帳號，加入我們的社群開始聊天",
});

definePageMeta({
  layout: false,
});

const registerForm = reactive({
  username: "",
  email: "",
  password: "",
  confirmPassword: "",
  agreeTerms: false,
});

const isLoading = ref(false);
const errorMessage = ref("");
const successMessage = ref("");
const usernameError = ref("");
const emailError = ref("");
const usernameValid = ref(false);
const emailValid = ref(false);

const passwordStrength = computed(() => {
  const password = registerForm.password;
  if (!password) return 0;

  let strength = 0;
  if (password.length >= 8) strength++;
  if (/[a-z]/.test(password)) strength++;
  if (/[A-Z]/.test(password)) strength++;
  if (/[0-9]/.test(password)) strength++;
  if (/[^A-Za-z0-9]/.test(password)) strength++;

  return strength;
});

const passwordStrengthText = computed(() => {
  const strength = passwordStrength.value;
  if (strength === 0) return "很弱";
  if (strength <= 2) return "弱";
  if (strength <= 3) return "中等";
  if (strength <= 4) return "強";
  return "很強";
});

const passwordStrengthClass = computed(() => {
  const strength = passwordStrength.value;
  if (strength <= 1) return "text-red-500";
  if (strength <= 2) return "text-orange-500";
  if (strength <= 3) return "text-yellow-500";
  if (strength <= 4) return "text-blue-500";
  return "text-green-500";
});

const passwordMismatch = computed(() => {
  return (
    registerForm.confirmPassword &&
    registerForm.password !== registerForm.confirmPassword
  );
});
const isFormValid = computed(() => {
  return (
    registerForm.username &&
    registerForm.email &&
    registerForm.password &&
    registerForm.confirmPassword &&
    registerForm.agreeTerms &&
    !passwordMismatch.value &&
    usernameValid.value &&
    emailValid.value
  );
});

const { register, checkUsername } = useAuth()

const checkUsernameAvailability = async () => {
  if (!registerForm.username) {
    usernameError.value = "";
    usernameValid.value = false;
    return;
  }

  if (registerForm.username.length < 3) {
    usernameError.value = "使用者名稱至少需要3個字元";
    usernameValid.value = false;
    return;
  }

  try {
    const result = await checkUsername(registerForm.username)

    if (result.success && result.available) {
      usernameError.value = "";
      usernameValid.value = true;
    } else {
      usernameError.value = result.message || "此使用者名稱已被使用";
      usernameValid.value = false;
    }
  } catch (error) {
    console.error("檢查使用者名稱錯誤:", error);
    usernameError.value = "無法驗證使用者名稱";
    usernameValid.value = false;
  }
};

const { checkEmail } = useAuth()

const checkEmailAvailability = async () => {
  if (!registerForm.email) {
    emailError.value = "";
    emailValid.value = false;
    return;
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(registerForm.email)) {
    emailError.value = "請輸入有效的電子郵件地址";
    emailValid.value = false;
    return;
  }

  try {
    const result = await checkEmail(registerForm.email)

    if (result.success && result.available) {
      emailError.value = "";
      emailValid.value = true;
    } else {
      emailError.value = result.message || "此電子郵件已被使用";
      emailValid.value = false;
    }
  } catch (error) {
    console.error("檢查電子郵件錯誤:", error);
    emailError.value = "無法驗證電子郵件";
    emailValid.value = false;
  }
};

// reCAPTCHA v3 事件處理
import { useRecaptchaToken } from "~/composables/useRecaptchaToken";

const handleRegister = async () => {
  errorMessage.value = "";
  successMessage.value = "";
  isLoading.value = true;

  try {
    const token = await useRecaptchaToken("register");

    if (!token) {
      alert("reCAPTCHA 驗證失敗，請再試一次");
      isLoading.value = false;
      return;
    }

    const result = await register({
      username: registerForm.username,
      email: registerForm.email,
      password: registerForm.password,
      first_name: registerForm.username, // 直接重用用戶名作為名字
      last_name: "user", // 預設姓氏
      recaptcha_response: token,
    });

    if (result.success) {
      successMessage.value = result.message || "註冊成功，請前往登入頁面";
      registerForm.username = "";
      registerForm.email = "";
      registerForm.password = "";
      registerForm.confirmPassword = "";
      registerForm.agreeTerms = false;
      usernameValid.value = false;
      emailValid.value = false;
    } else {
      errorMessage.value = result.message || "註冊失敗，請稍後再試";
    }
  } catch (error) {
    console.error("註冊錯誤:", error);
    errorMessage.value = error?.message || "註冊失敗，請稍後再試";
  } finally {
    isLoading.value = false;
  }
};
</script>
