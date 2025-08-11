<template>
  <UModal 
    v-model="channelStore.showChannelSettings"
    :ui="{ 
      overlay: { background: 'bg-gray-200/75 dark:bg-gray-800/75' },
      container: 'items-center'
    }"
  >
    <UCard 
      :ui="{ 
        ring: '', 
        divide: 'divide-y divide-gray-100 dark:divide-gray-800',
        header: { padding: 'px-6 py-4' },
        body: { padding: 'px-6' },
        footer: { padding: 'px-6 py-4' }
      }"
    >
      <template #header>
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-cog-6-tooth" class="w-5 h-5 text-blue-600" />
            <h3 id="channel-settings-title" class="text-lg font-semibold text-gray-900">頻道設定</h3>
          </div>
          <UButton
            @click="channelStore.closeChannelSettings()"
            variant="ghost"
            icon="i-heroicons-x-mark"
            size="sm"
          />
        </div>
      </template>

      <div class="py-4" v-if="channelStore.selectedChannelForSettings">
        <!-- 頻道基本資訊 -->
        <div class="mb-6">
          <div class="flex items-center gap-3 mb-3">
            <UIcon 
              :name="channelStore.selectedChannelForSettings.is_private ? 'i-heroicons-lock-closed' : 'i-heroicons-hashtag'" 
              class="w-6 h-6 text-gray-600"
            />
            <div>
              <h4 class="text-lg font-medium text-gray-900">{{ channelStore.selectedChannelForSettings.name }}</h4>
              <p class="text-sm text-gray-500">
                {{ channelStore.selectedChannelForSettings.is_private ? '私人頻道' : '公開頻道' }}
                • 建立於 {{ formatDate(channelStore.selectedChannelForSettings.created_on) }}
              </p>
            </div>
          </div>
          
          <p v-if="channelStore.selectedChannelForSettings.description" class="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
            {{ channelStore.selectedChannelForSettings.description }}
          </p>
        </div>

        <!-- 頻道統計 -->
        <div class="mb-6">
          <h5 class="text-sm font-medium text-gray-900 mb-3">頻道統計</h5>
          <div class="grid grid-cols-2 gap-4">
            <div class="bg-blue-50 p-3 rounded-lg">
              <div class="text-2xl font-bold text-blue-600">{{ getChannelMemberCount() }}</div>
              <div class="text-xs text-blue-600">成員數量</div>
            </div>
            <div class="bg-green-50 p-3 rounded-lg">
              <div class="text-2xl font-bold text-green-600">{{ channelStore.selectedChannelForSettings.max_members || 100 }}</div>
              <div class="text-xs text-green-600">最大成員</div>
            </div>
          </div>
        </div>

        <!-- 頻道設定表單 -->
        <form @submit.prevent="handleUpdateChannel" class="space-y-4">
          <!-- 頻道名稱 -->
          <div>
            <label for="settings-channel-name" class="block text-sm font-medium text-gray-700 mb-1">
              頻道名稱 <span class="text-red-500">*</span>
            </label>
            <UInput
              id="settings-channel-name"
              v-model="form.name"
              placeholder="頻道名稱"
              :disabled="loading || !isChannelOwner"
              required
              maxlength="50"
              icon="i-heroicons-hashtag"
            />
            <p v-if="errors.name" class="mt-1 text-sm text-red-600">{{ errors.name }}</p>
          </div>

          <!-- 頻道描述 -->
          <div>
            <label for="settings-channel-description" class="block text-sm font-medium text-gray-700 mb-1">
              頻道描述
            </label>
            <UTextarea
              id="settings-channel-description"
              v-model="form.description"
              placeholder="描述這個頻道的用途..."
              :disabled="loading || !isChannelOwner"
              rows="3"
              maxlength="200"
            />
            <p v-if="errors.description" class="mt-1 text-sm text-red-600">{{ errors.description }}</p>
          </div>

          <!-- 最大成員數 -->
          <div v-if="isChannelOwner">
            <label for="settings-max-members" class="block text-sm font-medium text-gray-700 mb-1">
              最大成員數
            </label>
            <UInput
              id="settings-max-members"
              v-model.number="form.max_members"
              type="number"
              min="2"
              max="1000"
              :disabled="loading"
              placeholder="100"
              icon="i-heroicons-user-group"
            />
            <p v-if="errors.max_members" class="mt-1 text-sm text-red-600">{{ errors.max_members }}</p>
          </div>

          <!-- 權限提示 -->
          <UAlert
            v-if="!isChannelOwner"
            icon="i-heroicons-information-circle"
            color="blue"
            variant="soft"
            title="只有頻道擁有者可以修改頻道設定"
            description="您可以查看頻道資訊，但無法進行修改。"
          />

          <!-- 錯誤訊息 -->
          <UAlert
            v-if="channelStore.error"
            icon="i-heroicons-exclamation-triangle"
            color="red"
            variant="soft"
            :title="channelStore.error"
          />
        </form>

        <!-- 成員列表 -->
        <div class="mt-6">
          <h5 class="text-sm font-medium text-gray-900 mb-3">頻道成員</h5>
          <div class="max-h-40 overflow-y-auto space-y-2">
            <div
              v-for="member in getChannelMembers()"
              :key="member.id"
              class="flex items-center justify-between p-2 bg-gray-50 rounded-lg"
            >
              <div class="flex items-center gap-2">
                <div class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                  <span class="text-xs font-medium text-gray-700">
                    {{ getInitials(member.display_name) }}
                  </span>
                </div>
                <div>
                  <div class="text-sm font-medium text-gray-900">{{ member.display_name }}</div>
                  <div class="text-xs text-gray-500">@{{ member.username }}</div>
                </div>
              </div>
              <UBadge
                v-if="member.role !== 'member'"
                :label="member.role === 'owner' ? '擁有者' : '管理員'"
                :color="member.role === 'owner' ? 'red' : 'blue'"
                variant="soft"
                size="xs"
              />
            </div>
          </div>
        </div>

        <!-- 危險區域 -->
        <div v-if="isChannelOwner" class="mt-6 pt-6 border-t border-gray-200">
          <h5 class="text-sm font-medium text-red-600 mb-3">危險區域</h5>
          <div class="bg-red-50 border border-red-200 rounded-lg p-4">
            <div class="flex items-start gap-3">
              <UIcon name="i-heroicons-exclamation-triangle" class="w-5 h-5 text-red-600 mt-0.5" />
              <div class="flex-1">
                <h6 class="text-sm font-medium text-red-800">刪除頻道</h6>
                <p class="text-xs text-red-600 mt-1">
                  刪除後將無法復原，所有訊息和設定都會永久消失。
                </p>
                <UButton
                  @click="showDeleteConfirm = true"
                  color="red"
                  variant="soft"
                  size="xs"
                  class="mt-2"
                  icon="i-heroicons-trash"
                >
                  刪除頻道
                </UButton>
              </div>
            </div>
          </div>
        </div>
      </div>

      <template #footer v-if="isChannelOwner">
        <div class="flex justify-end gap-2">
          <UButton 
            color="gray" 
            variant="soft" 
            @click="channelStore.closeChannelSettings()"
            :disabled="loading"
          >
            取消
          </UButton>
          <UButton 
            @click="handleUpdateChannel"
            :loading="loading"
            :disabled="loading || !hasChanges"
            icon="i-heroicons-check"
          >
            {{ loading ? "儲存中..." : "儲存變更" }}
          </UButton>
        </div>
      </template>

      <template #footer v-else>
        <div class="flex justify-end">
          <UButton 
            color="gray" 
            variant="soft" 
            @click="channelStore.closeChannelSettings()"
          >
            關閉
          </UButton>
        </div>
      </template>
    </UCard>
  </UModal>

  <!-- 刪除確認對話框 -->
  <UModal 
    v-model="showDeleteConfirm"
    :ui="{ 
      overlay: { background: 'bg-gray-200/75 dark:bg-gray-800/75' },
      container: 'items-center'
    }"
  >
    <UCard 
      :ui="{ 
        ring: '', 
        divide: 'divide-y divide-gray-100 dark:divide-gray-800',
        header: { padding: 'px-4 py-4' },
        body: { padding: 'px-4' },
        footer: { padding: 'px-4 py-4' }
      }"
    >
      <template #header>
        <div class="flex items-center gap-2">
          <UIcon name="i-heroicons-exclamation-triangle" class="w-5 h-5 text-red-500" />
          <h3 class="text-lg font-semibold text-gray-900">確認刪除頻道</h3>
        </div>
      </template>

      <div class="py-4">
        <p class="text-sm text-gray-600 mb-4">
          您確定要刪除頻道 <strong>{{ channelStore.selectedChannelForSettings?.name }}</strong> 嗎？
        </p>
        <div class="bg-red-50 border border-red-200 rounded-lg p-3">
          <p class="text-sm text-red-800 font-medium mb-2">此操作將會：</p>
          <ul class="text-xs text-red-700 space-y-1">
            <li class="flex items-center gap-2">
              <UIcon name="i-heroicons-chat-bubble-left-ellipsis" class="w-3 h-3" />
              永久刪除所有頻道訊息
            </li>
            <li class="flex items-center gap-2">
              <UIcon name="i-heroicons-users" class="w-3 h-3" />
              移除所有頻道成員
            </li>
            <li class="flex items-center gap-2">
              <UIcon name="i-heroicons-cog-6-tooth" class="w-3 h-3" />
              清除所有頻道設定
            </li>
            <li class="flex items-center gap-2">
              <UIcon name="i-heroicons-exclamation-triangle" class="w-3 h-3" />
              <strong>此操作無法復原</strong>
            </li>
          </ul>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-end gap-2">
          <UButton 
            color="gray" 
            variant="soft" 
            @click="showDeleteConfirm = false"
            :disabled="deleting"
          >
            取消
          </UButton>
          <UButton 
            color="red" 
            @click="handleDeleteChannel"
            :loading="deleting"
            :disabled="deleting"
            icon="i-heroicons-trash"
          >
            {{ deleting ? "刪除中..." : "確認刪除" }}
          </UButton>
        </div>
      </template>
    </UCard>
  </UModal>
</template>

<script setup>
import { useChannelStore } from '~/stores/channel'
import { useUserStore } from '~/stores/user'

const channelStore = useChannelStore()
const userStore = useUserStore()

// 表單資料
const form = reactive({
  name: '',
  description: '',
  max_members: 100
})

// 表單狀態
const loading = ref(false)
const deleting = ref(false)
const errors = ref({})
const showDeleteConfirm = ref(false)

// 監聽選中的頻道變化，更新表單資料
watch(() => channelStore.selectedChannelForSettings, (channel) => {
  if (channel) {
    form.name = channel.name || ''
    form.description = channel.description || ''
    form.max_members = channel.max_members || 100
  }
}, { immediate: true })

// 計算屬性
const isChannelOwner = computed(() => {
  if (!userStore.currentUser || !channelStore.selectedChannelForSettings) return false
  return channelStore.selectedChannelForSettings.creator_id === userStore.currentUser.id
})

const hasChanges = computed(() => {
  const channel = channelStore.selectedChannelForSettings
  if (!channel) return false
  
  return (
    form.name !== channel.name ||
    form.description !== (channel.description || '') ||
    form.max_members !== (channel.max_members || 100)
  )
})

// 工具方法
const getChannelMemberCount = () => {
  const channelId = channelStore.selectedChannelForSettings?.id
  if (!channelId) return 0
  
  const members = channelStore.channelMembers[channelId] || []
  return members.length
}

const getChannelMembers = () => {
  const channelId = channelStore.selectedChannelForSettings?.id
  if (!channelId) return []
  
  return channelStore.channelMembers[channelId] || []
}

const getInitials = (name) => {
  if (!name) return '?'
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

const formatDate = (dateString) => {
  if (!dateString) return '未知'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-TW', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// 表單驗證
const validateForm = () => {
  errors.value = {}
  
  // 頻道名稱驗證
  if (!form.name.trim()) {
    errors.value.name = '頻道名稱為必填'
    return false
  }
  
  if (form.name.length < 2) {
    errors.value.name = '頻道名稱至少需要2個字元'
    return false
  }
  
  if (form.name.length > 50) {
    errors.value.name = '頻道名稱不能超過50個字元'
    return false
  }
  
  // 頻道名稱格式驗證
  if (!/^[a-zA-Z0-9\u4e00-\u9fa5\s\-_]+$/.test(form.name)) {
    errors.value.name = '頻道名稱只能包含字母、數字、中文、空格、連字符和底線'
    return false
  }
  
  // 描述長度驗證
  if (form.description && form.description.length > 200) {
    errors.value.description = '頻道描述不能超過200個字元'
    return false
  }
  
  // 最大成員數驗證
  if (form.max_members < 2 || form.max_members > 1000) {
    errors.value.max_members = '最大成員數必須在2-1000之間'
    return false
  }
  
  return true
}

// 處理更新頻道
const handleUpdateChannel = async () => {
  // 清除之前的錯誤
  channelStore.clearError()
  
  if (!validateForm()) return
  
  loading.value = true
  
  try {
    const channelId = channelStore.selectedChannelForSettings?.id
    if (!channelId) return
    
    const updates = {
      name: form.name.trim(),
      description: form.description.trim(),
      max_members: form.max_members
    }
    
    console.log('更新頻道設定:', updates)
    
    const result = await channelStore.updateChannel(channelId, updates)
    
    if (result.success) {
      console.log('頻道設定更新成功')
      
      // 顯示成功訊息
      const toast = useToast()
      toast.add({
        title: "設定已儲存！",
        description: `頻道 "${form.name}" 的設定已成功更新`,
        icon: "i-heroicons-check-circle",
        color: "green"
      })
      
      // 關閉對話框
      channelStore.closeChannelSettings()
      
    } else {
      console.error('頻道設定更新失敗:', result.error)
    }
    
  } catch (error) {
    console.error('更新頻道設定時發生錯誤:', error)
  } finally {
    loading.value = false
  }
}

// 處理刪除頻道
const handleDeleteChannel = async () => {
  deleting.value = true
  
  try {
    const channelId = channelStore.selectedChannelForSettings?.id
    if (!channelId) return
    
    // TODO: 實作刪除頻道 API
    console.log('刪除頻道:', channelId)
    
    // 暫時模擬刪除成功
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 顯示成功訊息
    const toast = useToast()
    toast.add({
      title: "頻道已刪除",
      description: `頻道 "${channelStore.selectedChannelForSettings?.name}" 已成功刪除`,
      icon: "i-heroicons-trash",
      color: "red"
    })
    
    // 關閉所有對話框
    showDeleteConfirm.value = false
    channelStore.closeChannelSettings()
    
    // 重新載入頻道列表
    await channelStore.fetchChannels()
    
  } catch (error) {
    console.error('刪除頻道時發生錯誤:', error)
  } finally {
    deleting.value = false
  }
}

// 監聽對話框關閉，重設狀態
watch(() => channelStore.showChannelSettings, (isOpen) => {
  if (!isOpen) {
    // 重設表單狀態
    errors.value = {}
    showDeleteConfirm.value = false
    channelStore.clearError()
  }
})
</script>