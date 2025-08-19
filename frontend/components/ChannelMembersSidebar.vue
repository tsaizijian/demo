<template>
  <div class="channel-members-sidebar h-full flex flex-col">
    <!-- 成員列表標題 -->
    <div class="members-header p-4 border-b flex items-center justify-between">
      <h3 class="text-lg font-semibold">成員 ({{ members.length }})</h3>
      <div class="flex items-center gap-2">
        <!-- 頻道設定按鈕 -->
        <Button
          v-if="canManageChannel"
          icon="pi pi-cog"
          size="small"
          @click="showSettingsDialog = true"
          v-tooltip="'頻道設定'"
        />
      </div>
    </div>

    <!-- 成員列表 -->
    <div class="members-list flex-1 overflow-y-auto p-4">
      <div v-if="loading" class="text-center py-4">
        <ProgressSpinner size="30px" />
        <p class="text-gray-500 mt-2">載入中...</p>
      </div>

      <div v-else-if="members.length === 0" class="text-center py-8 text-gray-500">
        <i class="pi pi-users text-3xl mb-2"></i>
        <p>此頻道暫無成員</p>
      </div>

      <div v-else class="space-y-2">
        <div
          v-for="member in sortedMembers"
          :key="member.id"
          class="member-item p-3 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <Avatar 
                :label="member.display_name ? member.display_name[0] : 'U'"
                :class="{
                  'bg-yellow-100 text-yellow-700': member.role === 'owner',
                  'bg-blue-100 text-blue-700': member.role === 'admin',
                  'bg-gray-100 text-gray-700': member.role === 'member'
                }"
                size="normal"
              />
              <div class="flex-1">
                <div class="font-medium flex items-center gap-2">
                  {{ member.display_name || member.username }}
                  <i 
                    v-if="member.role === 'owner'" 
                    class="pi pi-crown text-yellow-600" 
                    v-tooltip="'頻道擁有者'"
                  ></i>
                  <i 
                    v-else-if="member.role === 'admin'" 
                    class="pi pi-shield text-blue-600" 
                    v-tooltip="'管理員'"
                  ></i>
                </div>
                <div class="text-sm text-gray-500">@{{ member.username }}</div>
              </div>
            </div>
            
            <div class="flex items-center gap-2">
              <Badge 
                :value="getRoleLabel(member.role)" 
                :severity="getRoleSeverity(member.role)"
              />
              
              <!-- 成員操作選單 -->
              <Button
                v-if="canManageMember(member)"
                icon="pi pi-ellipsis-v"
                size="small"
                text
                @click="showMemberActions($event, member)"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 成員操作選單 -->
    <Menu ref="memberActionsMenu" :model="memberActionItems" :popup="true" />

    <!-- 對話框 -->
    <ChannelSettingsDialog
      v-model:visible="showSettingsDialog"
      :channel="currentChannel"
      @updated="handleChannelUpdated"
    />

    <TransferOwnershipDialog
      v-model:visible="showTransferDialog"
      :channel-id="currentChannel?.id"
      :available-members="transferAvailableMembers"
      @transferred="handleOwnershipTransferred"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useChannelStore } from '~/stores/channel'
import { useUserStore } from '~/stores/user'
import { useToast } from 'primevue/usetoast'

// Components
import ChannelSettingsDialog from './ChannelSettingsDialog.vue'
import TransferOwnershipDialog from './TransferOwnershipDialog.vue'

// Stores
const channelStore = useChannelStore()
const userStore = useUserStore()
const toast = useToast()
const config = useRuntimeConfig()

// Reactive data
const members = ref([])
const loading = ref(false)
const showSettingsDialog = ref(false)
const showTransferDialog = ref(false)
const selectedMember = ref(null)
const memberActionsMenu = ref(null)

// Computed
const currentChannel = computed(() => channelStore.currentChannel)

const sortedMembers = computed(() => {
  const roleOrder = { owner: 0, admin: 1, member: 2 }
  return [...members.value].sort((a, b) => {
    const roleCompare = roleOrder[a.role] - roleOrder[b.role]
    if (roleCompare !== 0) return roleCompare
    return a.display_name?.localeCompare(b.display_name) || 0
  })
})

const currentUserMember = computed(() => {
  return members.value.find(m => m.user_id === userStore.userProfile?.user_id)
})

const canManageChannel = computed(() => {
  const member = currentUserMember.value
  return member && (member.role === 'owner' || member.role === 'admin')
})

const transferAvailableMembers = computed(() => {
  return members.value.filter(m => 
    m.user_id !== userStore.userProfile?.user_id && 
    m.status === 'active'
  )
})

const memberActionItems = computed(() => {
  if (!selectedMember.value) return []
  
  const items = []
  const currentMember = currentUserMember.value
  const target = selectedMember.value
  
  if (currentMember?.role === 'owner') {
    if (target.role === 'member') {
      items.push({
        label: '設為管理員',
        icon: 'pi pi-shield',
        command: () => updateMemberRole(target.user_id, 'admin')
      })
    } else if (target.role === 'admin') {
      items.push({
        label: '取消管理員',
        icon: 'pi pi-user',
        command: () => updateMemberRole(target.user_id, 'member')
      })
    }
    
    if (target.role !== 'owner') {
      items.push({
        label: '移除成員',
        icon: 'pi pi-user-minus',
        command: () => removeMember(target.user_id)
      })
    }
    
    items.push({
      label: '轉移擁有權',
      icon: 'pi pi-crown',
      command: () => {
        showTransferDialog.value = true
      }
    })
  } else if (currentMember?.role === 'admin' && target.role === 'member') {
    items.push({
      label: '移除成員',
      icon: 'pi pi-user-minus',
      command: () => removeMember(target.user_id)
    })
  }
  
  return items
})

// Methods
const fetchMembers = async () => {
  if (!currentChannel.value?.id) return
  
  loading.value = true
  try {
    const response = await $fetch(
      `${config.public.apiBase}/api/v1/channelmemberapi/channel/${currentChannel.value.id}/members`,
      {
        credentials: 'include',
        headers: {
          Authorization: `Bearer ${userStore.accessToken}`,
          'Content-Type': 'application/json',
        },
      }
    )
    
    if (response?.result) {
      members.value = response.result
    }
  } catch (error) {
    console.error('獲取成員列表失敗:', error)
    toast.add({
      severity: 'error',
      summary: '載入失敗',
      detail: '無法載入成員列表',
      life: 3000
    })
  } finally {
    loading.value = false
  }
}

const canManageMember = (member) => {
  const currentMember = currentUserMember.value
  if (!currentMember) return false
  
  // 不能對自己操作
  if (member.user_id === userStore.userProfile?.user_id) return false
  
  // Owner 可以管理所有人
  if (currentMember.role === 'owner') return true
  
  // Admin 只能管理 Member
  if (currentMember.role === 'admin' && member.role === 'member') return true
  
  return false
}

const showMemberActions = (event, member) => {
  selectedMember.value = member
  memberActionsMenu.value.toggle(event)
}

const updateMemberRole = async (userId, newRole) => {
  try {
    await $fetch(
      `${config.public.apiBase}/api/v1/channelmemberapi/channel/${currentChannel.value.id}/role/${userId}`,
      {
        method: 'PUT',
        credentials: 'include',
        headers: {
          Authorization: `Bearer ${userStore.accessToken}`,
          'Content-Type': 'application/json',
        },
        body: { role: newRole }
      }
    )
    
    toast.add({
      severity: 'success',
      summary: '角色更新成功',
      life: 3000
    })
    
    await fetchMembers()
  } catch (error) {
    console.error('更新角色失敗:', error)
    toast.add({
      severity: 'error',
      summary: '更新失敗',
      detail: error.data?.error || '角色更新失敗',
      life: 3000
    })
  }
}

const removeMember = async (userId) => {
  try {
    await $fetch(
      `${config.public.apiBase}/api/v1/channelmemberapi/channel/${currentChannel.value.id}/remove/${userId}`,
      {
        method: 'POST',
        credentials: 'include',
        headers: {
          Authorization: `Bearer ${userStore.accessToken}`,
          'Content-Type': 'application/json',
        },
      }
    )
    
    toast.add({
      severity: 'success',
      summary: '成員已移除',
      life: 3000
    })
    
    await fetchMembers()
  } catch (error) {
    console.error('移除成員失敗:', error)
    toast.add({
      severity: 'error',
      summary: '移除失敗',
      detail: error.data?.error || '移除成員失敗',
      life: 3000
    })
  }
}

const getRoleLabel = (role) => {
  const labels = {
    owner: '擁有者',
    admin: '管理員',
    member: '成員'
  }
  return labels[role] || '成員'
}

const getRoleSeverity = (role) => {
  const severities = {
    owner: 'warn',
    admin: 'info',
    member: 'secondary'
  }
  return severities[role] || 'secondary'
}

const handleChannelUpdated = () => {
  // 頻道設定更新後重新載入
}

const handleOwnershipTransferred = () => {
  fetchMembers()
}

// Lifecycle
onMounted(() => {
  if (currentChannel.value) {
    fetchMembers()
  }
})

// Watchers
watch(() => currentChannel.value?.id, (newChannelId) => {
  if (newChannelId) {
    fetchMembers()
  } else {
    members.value = []
  }
})
</script>

<style scoped>
.space-y-2 > * + * {
  margin-top: 0.5rem;
}
</style>