import { defineStore } from "pinia";
import { useSocket } from "~/composables/useSocket";
import { useUserStore } from "./user";

interface Channel {
  id: number;
  name: string;
  description?: string;
  is_private: boolean;
  is_active: boolean;
  creator_id: number;
  creator_name?: string;
  max_members: number;
  member_count?: number;
  created_on: string;
  lastMessage?: {
    id: number;
    content: string;
    sender_name: string;
    created_on: string;
  } | null;
}

interface ChannelMessage {
  id: number;
  content: string;
  sender_id: number;
  sender_name: string;
  message_type: string;
  channel_id: number;
  created_on: string;
}

interface ChannelMember {
  id: number;
  channel_id: number;
  user_id: number;
  username: string;
  display_name: string;
  role: "owner" | "admin" | "member";
  joined_at: string;
}

interface ApiResponse<T> {
  result: T;
  success?: boolean;
  message?: string;
}

export const useChannelStore = defineStore("channel", {
  state: () => ({
    // 頻道相關
    channels: [] as Channel[],
    currentChannel: null as Channel | null,
    currentChannelId: 1, // 預設頻道

    // 頻道訊息
    channelMessages: {} as Record<number, ChannelMessage[]>,

    // 頻道成員
    channelMembers: {} as Record<number, ChannelMember[]>,

    // UI 狀態
    loading: false,
    error: null as string | null,

    // 頻道管理 UI
    showChannelCreator: false,
    showChannelSettings: false,
    selectedChannelForSettings: null as Channel | null,
  }),

  getters: {
    // 當前頻道訊息
    currentChannelMessages: (state): ChannelMessage[] => {
      return state.channelMessages[state.currentChannelId] || [];
    },

    // 當前頻道成員
    currentChannelMembers: (state): ChannelMember[] => {
      return state.channelMembers[state.currentChannelId] || [];
    },

    // 公開頻道
    publicChannels: (state): Channel[] => {
      return state.channels.filter(
        (channel) => !channel.is_private && channel.is_active
      );
    },

    // 私人頻道
    privateChannels: (state): Channel[] => {
      return state.channels.filter(
        (channel) => channel.is_private && channel.is_active
      );
    },

    // 是否為頻道管理員
    isChannelAdmin: (state) => {
      const userStore = useUserStore();
      if (!userStore.currentUser) return false;

      const currentMembers = state.channelMembers[state.currentChannelId] || [];
      const member = currentMembers.find(
        (m: ChannelMember) => m.user_id === userStore.currentUser?.id
      );
      return member?.role === "admin" || member?.role === "owner";
    },
  },

  actions: {
    // 獲取所有頻道
    async fetchChannels() {
      this.loading = true;
      this.error = null;

      try {
        const config = useRuntimeConfig();
        const userStore = useUserStore();

        // 同時獲取公開和私人頻道
        const [publicResponse, privateResponse] = await Promise.all([
          $fetch<ApiResponse<Channel[]>>(
            `${config.public.apiBase}/api/v1/chatchannelapi/public-channels`,
            {
              credentials: "include",
              headers: {
                Authorization: `Bearer ${userStore.accessToken}`,
                "Content-Type": "application/json",
              },
            }
          ),
          $fetch<ApiResponse<Channel[]>>(
            `${config.public.apiBase}/api/v1/chatchannelapi/my-channels`,
            {
              credentials: "include",
              headers: {
                Authorization: `Bearer ${userStore.accessToken}`,
                "Content-Type": "application/json",
              },
            }
          ),
        ]);

        if (publicResponse && publicResponse.result) {
          let allChannels = [...publicResponse.result];

          // 合併私人頻道（避免重複）
          if (privateResponse && privateResponse.result) {
            const publicChannelIds = new Set(
              publicResponse.result.map((c) => c.id)
            );
            const privateChannels = privateResponse.result.filter(
              (c) => !publicChannelIds.has(c.id)
            );
            allChannels = [...allChannels, ...privateChannels];
          }

          this.channels = allChannels;

          // 如果沒有當前頻道，設定為第一個頻道
          if (!this.currentChannel && this.channels.length > 0) {
            const firstChannel = this.channels[0];
            if (firstChannel) {
              this.currentChannel = firstChannel;
              this.currentChannelId = firstChannel.id;
              // 載入該頻道的訊息
              await this.fetchChannelMessages(firstChannel.id);
            }
          }

          return { success: true, data: allChannels };
        }

        return { success: false, error: "No channels found" };
      } catch (error: any) {
        console.error("獲取頻道失敗:", error);
        this.error = error.message || "獲取頻道失敗";
        return { success: false, error: error.message };
      } finally {
        this.loading = false;
      }
    },

    // 切換頻道
    async switchChannel(channelId: number) {
      const channel = this.channels.find((c) => c.id === channelId);
      if (!channel) {
        this.error = "頻道不存在";
        return { success: false, error: "頻道不存在" };
      }

      this.currentChannel = channel;
      this.currentChannelId = channelId;

      // 載入該頻道的訊息
      await this.fetchChannelMessages(channelId);

      // 載入該頻道的成員
      await this.fetchChannelMembers(channelId);

      // 通知 Socket.IO 切換房間
      const socketStore = useSocket();
      if (socketStore.socket.value) {
        socketStore.socket.value.emit("join_channel", {
          channel_id: channelId,
        });
      }

      return { success: true };
    },

    // 獲取頻道訊息
    async fetchChannelMessages(channelId: number) {
      try {
        const config = useRuntimeConfig();
        const userStore = useUserStore();

        const response = await $fetch<ApiResponse<ChannelMessage[]>>(
          `${config.public.apiBase}/api/v1/chatmessageapi/recent/50?channel_id=${channelId}`,
          {
            credentials: "include",
            headers: {
              Authorization: `Bearer ${userStore.accessToken}`,
              "Content-Type": "application/json",
            },
          }
        );

        if (response && response.result) {
          this.channelMessages[channelId] = response.result;
          return { success: true, data: response.result };
        }

        return { success: false, error: "No messages found" };
      } catch (error: any) {
        console.error("獲取頻道訊息失敗:", error);
        return { success: false, error: error.message };
      }
    },

    // 載入歷史訊息
    async loadHistoryMessages(channelId: number, beforeTimestamp?: string, limit: number = 20) {
      try {
        const config = useRuntimeConfig();
        const userStore = useUserStore();

        // 取得最舊訊息的 ID 作為 before_id 參數
        const currentMessages = this.channelMessages[channelId] || [];
        const beforeId = currentMessages.length > 0 && currentMessages[0] ? currentMessages[0].id : undefined;

        // 構建查詢參數 (使用後端期望的格式)
        const params = new URLSearchParams({
          channel_id: channelId.toString(),
          per_page: limit.toString(),
          page: '1',
        });

        if (beforeId) {
          params.append('before_id', beforeId.toString());
        }

        // 呼叫歷史訊息 API
        const response = await $fetch<ApiResponse<ChannelMessage[]>>(
          `${config.public.apiBase}/api/v1/chatmessageapi/history?${params.toString()}`,
          {
            credentials: "include",
            headers: {
              Authorization: `Bearer ${userStore.accessToken}`,
              "Content-Type": "application/json",
            },
          }
        );

        if (response && response.result) {
          // 將歷史訊息插入到現有訊息列表的開頭
          if (!this.channelMessages[channelId]) {
            this.channelMessages[channelId] = [];
          }
          
          // 避免重複訊息
          const existingIds = new Set(this.channelMessages[channelId].map(m => m.id));
          const newMessages = response.result.filter(m => !existingIds.has(m.id));
          
          // 將新的歷史訊息加到列表開頭
          this.channelMessages[channelId] = [...newMessages, ...this.channelMessages[channelId]];
          
          return { success: true, messages: response.result };
        }

        return { success: false, error: "No history messages found", messages: [] };
      } catch (error: any) {
        console.error("載入歷史訊息失敗:", error);
        
        // 如果 API 不存在，返回空結果而不是錯誤
        if (error.status === 404) {
          console.warn("歷史訊息 API 尚未實作，跳過載入");
          return { success: false, error: "History API not implemented", messages: [] };
        }
        
        return { success: false, error: error.message, messages: [] };
      }
    },

    // 獲取頻道成員
    async fetchChannelMembers(channelId: number) {
      try {
        const config = useRuntimeConfig();
        const userStore = useUserStore();

        // 暫時使用線上使用者 API，之後可以改為頻道專用 API
        const response = await $fetch<ApiResponse<any[]>>(
          `${config.public.apiBase}/api/v1/userprofileapi/online-users`,
          {
            credentials: "include",
            headers: {
              Authorization: `Bearer ${userStore.accessToken}`,
              "Content-Type": "application/json",
            },
          }
        );

        if (response && response.result) {
          // 模擬頻道成員結構
          const members: ChannelMember[] = response.result.map((user: any) => ({
            id: user.id,
            channel_id: channelId,
            user_id: user.user_id,
            username: user.username,
            display_name: user.display_name || user.username,
            role: (user.user_id === 1 ? "owner" : "member") as
              | "owner"
              | "admin"
              | "member",
            joined_at: new Date().toISOString(),
          }));

          this.channelMembers[channelId] = members;
          return { success: true, data: members };
        }

        return { success: false, error: "No members found" };
      } catch (error: any) {
        console.error("獲取頻道成員失敗:", error);
        return { success: false, error: error.message };
      }
    },

    // 建立新頻道
    async createChannel(channelData: {
      name: string;
      description?: string;
      is_private?: boolean;
      max_members?: number;
    }) {
      this.loading = true;
      this.error = null;

      try {
        const config = useRuntimeConfig();
        const userStore = useUserStore();

        // 調試：印出 token
        console.log("Creating channel with token:", userStore.accessToken);

        const response = await $fetch(
          `${config.public.apiBase}/api/v1/chatchannelapi/create-channel`,
          {
            method: "POST",
            credentials: "include",
            headers: {
              Authorization: `Bearer ${userStore.accessToken}`,
              "Content-Type": "application/json",
            },
            body: {
              name: channelData.name,
              description: channelData.description || "",
              is_private: channelData.is_private || false,
              max_members: channelData.max_members || 100,
            },
          }
        );

        if (response) {
          // 重新獲取頻道列表
          await this.fetchChannels();

          // 關閉建立頻道對話框
          this.showChannelCreator = false;

          return { success: true, data: response };
        }

        return { success: false, error: "Failed to create channel" };
      } catch (error: any) {
        console.error("建立頻道失敗:", error);
        this.error = error.message || "建立頻道失敗";
        return { success: false, error: error.message };
      } finally {
        this.loading = false;
      }
    },

    // 更新頻道設定
    async updateChannel(channelId: number, updates: Partial<Channel>) {
      this.loading = true;
      this.error = null;

      try {
        const config = useRuntimeConfig();
        const userStore = useUserStore();

        const response = await $fetch(
          `${config.public.apiBase}/api/v1/chatchannelapi/${channelId}`,
          {
            method: "PUT",
            credentials: "include",
            headers: {
              Authorization: `Bearer ${userStore.accessToken}`,
              "Content-Type": "application/json",
            },
            body: updates,
          }
        );

        if (response) {
          // 更新本地頻道資料
          const channelIndex = this.channels.findIndex(
            (c) => c.id === channelId
          );
          if (channelIndex !== -1) {
            const updatedChannel = {
              ...this.channels[channelIndex],
              ...updates,
            } as Channel;
            this.channels[channelIndex] = updatedChannel;

            // 如果是當前頻道，也更新當前頻道
            if (this.currentChannelId === channelId) {
              this.currentChannel = updatedChannel;
            }
          }

          return { success: true, data: response };
        }

        return { success: false, error: "Failed to update channel" };
      } catch (error: any) {
        console.error("更新頻道失敗:", error);
        this.error = error.message || "更新頻道失敗";
        return { success: false, error: error.message };
      } finally {
        this.loading = false;
      }
    },

    // 發送訊息
    async sendMessage(content: string, replyToId?: number, channelId?: number) {
      const userStore = useUserStore();
      if (!userStore.accessToken) return { success: false, error: "未登入" };

      const targetChannelId = channelId || this.currentChannelId;
      this.loading = true;

      try {
        const config = useRuntimeConfig();

        const response = await $fetch(
          `${config.public.apiBase}/api/v1/chatmessageapi/send`,
          {
            method: "POST",
            credentials: "include",
            headers: {
              Authorization: `Bearer ${userStore.accessToken}`,
              "Content-Type": "application/json",
            },
            body: {
              content,
              message_type: "text",
              reply_to_id: replyToId,
              channel_id: targetChannelId,
            },
          }
        );

        // 重新獲取該頻道的訊息列表
        await this.fetchChannelMessages(targetChannelId);

        return { success: true, data: response };
      } catch (error: any) {
        this.error = error.data?.message || "發送訊息失敗";
        console.error("發送訊息失敗:", error);
        return { success: false, error: this.error };
      } finally {
        this.loading = false;
      }
    },

    // 刪除訊息
    async deleteMessage(messageId: number, channelId?: number) {
      const userStore = useUserStore();
      if (!userStore.accessToken) return { success: false, error: "未登入" };

      const targetChannelId = channelId || this.currentChannelId;

      try {
        const config = useRuntimeConfig();

        await $fetch(
          `${config.public.apiBase}/api/v1/chatmessageapi/delete/${messageId}`,
          {
            method: "POST",
            credentials: "include",
            headers: {
              Authorization: `Bearer ${userStore.accessToken}`,
              "Content-Type": "application/json",
            },
          }
        );

        // 重新獲取該頻道的訊息列表
        await this.fetchChannelMessages(targetChannelId);

        return { success: true };
      } catch (error: any) {
        this.error = error.data?.message || "刪除訊息失敗";
        console.error("刪除訊息失敗:", error);
        return { success: false, error: this.error };
      }
    },

    // 添加訊息到頻道
    addMessageToChannel(channelId: number, message: ChannelMessage) {
      if (!this.channelMessages[channelId]) {
        this.channelMessages[channelId] = [];
      }
      this.channelMessages[channelId].push(message);

      // 更新頻道的最新訊息資訊
      const channel = this.channels.find((c) => c.id === channelId);
      if (channel) {
        channel.lastMessage = {
          id: message.id,
          content: message.content,
          sender_name: message.sender_name,
          created_on: message.created_on,
        };
      }
    },

    // 從頻道移除訊息
    removeMessageFromChannel(channelId: number, messageId: number) {
      if (this.channelMessages[channelId]) {
        this.channelMessages[channelId] = this.channelMessages[
          channelId
        ].filter((m) => m.id !== messageId);
      }
    },

    // UI 控制方法
    openChannelCreator() {
      this.showChannelCreator = true;
    },

    closeChannelCreator() {
      this.showChannelCreator = false;
    },

    openChannelSettings(channel: Channel) {
      this.selectedChannelForSettings = channel;
      this.showChannelSettings = true;
    },

    closeChannelSettings() {
      this.showChannelSettings = false;
      this.selectedChannelForSettings = null;
    },

    // 清除錯誤
    clearError() {
      this.error = null;
    },

    // 切換頻道創建器顯示狀態
    toggleChannelCreator() {
      this.showChannelCreator = !this.showChannelCreator;
    },

    // 重置狀態
    reset() {
      this.channels = [];
      this.currentChannel = null;
      this.currentChannelId = 1;
      this.channelMessages = {};
      this.channelMembers = {};
      this.loading = false;
      this.error = null;
      this.showChannelCreator = false;
      this.showChannelSettings = false;
      this.selectedChannelForSettings = null;
    },
  },
});
