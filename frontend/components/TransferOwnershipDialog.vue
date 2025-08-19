<template>
  <Dialog 
    :visible="visible"
    @update:visible="$emit('update:visible', $event)"
    header="轉移頻道擁有權" 
    modal 
    class="w-full md:w-[500px]"
  >
    <!-- 警告訊息 -->
    <Message severity="warn" :closable="false" class="mb-4">
      <p class="font-semibold">⚠️ 重要警告</p>
      <p>轉移後您將失去頻道擁有權，此操作無法撤銷！</p>
    </Message>

    <!-- 選擇新的擁有者 -->
    <div class="mb-6">
      <h4 class="text-lg font-semibold mb-3">選擇新的頻道擁有者</h4>
      
      <div v-if="availableMembers.length === 0" class="text-center py-4 text-gray-500">
        沒有可選擇的成員
      </div>
      
      <div v-else class="space-y-2 max-h-60 overflow-y-auto">
        <div
          v-for="member in availableMembers"
          :key="member.user_id"
          class="member-option p-3 border rounded-lg cursor-pointer transition-all"
          :class="{
            'border-primary-500 bg-primary-50': selectedMemberId === member.user_id,
            'border-gray-200 hover:border-gray-300': selectedMemberId !== member.user_id
          }"
          @click="selectedMemberId = member.user_id"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <Avatar 
                :label="member.display_name ? member.display_name[0] : 'U'" 
                class="bg-primary-100 text-primary-700"
                size="normal"
              />
              <div>
                <div class="font-medium">{{ member.display_name || member.username }}</div>
                <div class="text-sm text-gray-500">@{{ member.username }}</div>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <Badge :value="member.role" severity="info" />
              <RadioButton 
                :value="member.user_id"
                v-model="selectedMemberId"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 確認輸入 -->
    <div class="mb-4">
      <FloatLabel>
        <InputText
          id="confirmText"
          v-model="confirmText"
          placeholder="請輸入 '轉移擁有權' 來確認"
          class="w-full"
          :class="{ 'p-invalid': errors.confirmText }"
        />
        <label for="confirmText">確認轉移</label>
      </FloatLabel>
      <small v-if="errors.confirmText" class="p-error">{{ errors.confirmText }}</small>
      <small class="text-gray-500">請輸入「轉移擁有權」來確認此操作</small>
    </div>

    <!-- 錯誤訊息 -->
    <Message v-if="error" severity="error" :closable="false" class="mb-4">
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
        label="確認轉移"
        severity="danger"
        @click="confirmTransfer"
        :loading="loading"
        :disabled="!canTransfer"
      />
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useUserStore } from '~/stores/user'
import { useChannelStore } from '~/stores/channel'
import { useToast } from 'primevue/usetoast'

// Props & Emits
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  channelId: {
    type: Number,
    required: true
  },
  availableMembers: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:visible', 'transferred'])

// Stores
const userStore = useUserStore()
const channelStore = useChannelStore()
const toast = useToast()
const config = useRuntimeConfig()

// Reactive data
const selectedMemberId = ref(null)
const confirmText = ref('')
const loading = ref(false)
const error = ref('')
const errors = ref({
  confirmText: ''
})

// Computed
const canTransfer = computed(() => {
  return selectedMemberId.value && 
         confirmText.value === '轉移擁有權' && 
         !loading.value &&
         props.availableMembers.length > 0
})

// Methods
const validateForm = () => {
  errors.value = { confirmText: '' }

  if (!selectedMemberId.value) {
    error.value = '請選擇新的擁有者'
    return false
  }

  if (confirmText.value !== '轉移擁有權') {
    errors.value.confirmText = '請正確輸入確認文字'
    return false
  }

  return true
}

const confirmTransfer = async () => {
  if (!validateForm()) return

  loading.value = true
  error.value = ''

  try {
    const response = await $fetch(
      `${config.public.apiBase}/api/v1/channelmemberapi/channel/${props.channelId}/transfer-ownership/${selectedMemberId.value}`,
      {
        method: 'POST',
        credentials: 'include',
        headers: {
          Authorization: `Bearer ${userStore.accessToken}`,
          'Content-Type': 'application/json',
        },
      }
    )

    if (response.success) {
      // 顯示成功訊息
      toast.add({
        severity: 'success',
        summary: '轉移成功',
        detail: response.message,
        life: 5000
      })

      // 重新載入頻道資料
      await channelStore.fetchChannels()
      
      emit('transferred', response.data)
      closeDialog()
    }
  } catch (err) {
    console.error('轉移擁有權失敗:', err)
    error.value = err.data?.error || err.message || '轉移失敗'
    
    toast.add({
      severity: 'error',
      summary: '轉移失敗',
      detail: error.value,
      life: 5000
    })
  } finally {
    loading.value = false
  }
}

const closeDialog = () => {
  emit('update:visible', false)
}

const resetForm = () => {
  selectedMemberId.value = null
  confirmText.value = ''
  error.value = ''
  errors.value = { confirmText: '' }
}

// Watchers
watch(() => props.visible, (newValue) => {
  if (newValue) {
    resetForm()
    // 如果只有一個可選成員，自動選中
    if (props.availableMembers.length === 1) {
      selectedMemberId.value = props.availableMembers[0].user_id
    }
  }
})

watch(() => props.availableMembers, () => {
  // 重置選擇當成員列表改變時
  selectedMemberId.value = null
})
</script>

<style scoped>
.member-option {
  transition: all 0.2s ease-in-out;
}

.member-option:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.p-error {
  display: block;
  margin-top: 0.25rem;
  color: var(--p-red-500);
  font-size: 0.875rem;
}

.space-y-2 > * + * {
  margin-top: 0.5rem;
}
</style>