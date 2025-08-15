# 目前 API 實現方法

## 認證系統架構

### JWT Bearer Token 認證

我們使用 JWT (JSON Web Token) Bearer Authentication 來實現 API 認證：

```
Authorization: Bearer <JWT_TOKEN>
```

### 認證流程

1. **登入獲取 Token**
   ```bash
   POST /api/v1/auth/login
   Content-Type: application/json
   
   {
     "username": "admin",
     "password": "password",
     "provider": "db"
   }
   
   # 回應
   {
     "access_token": "eyJhbGciOiJIUzI1NiIs..."
   }
   ```

2. **使用 Token 呼叫 API**
   ```bash
   GET /api/v1/chatmessageapi/recent/50?channel_id=1
   Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
   ```

## 中間件系統

### JWT 認證中間件

```python
# auth.py - JWTSecurityManager.jwt_auth_handler()
def jwt_auth_handler(self):
    # 1. 檢查 Authorization header
    auth_header = request.headers.get('Authorization')
    
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        
        # 2. 解碼 JWT token
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        
        # 3. 驗證用戶並設置認證狀態
        user_id = payload.get('user_id')
        user = self.get_user_by_id(user_id)
        
        if user and user.is_active:
            g.user = user  # Flask g 物件
            login_user(user)  # Flask-Login current_user
```

### API 端點保護

```python
# apis.py - 使用 @jwt_required 裝飾器
@expose('/recent/<int:limit>')
@jwt_required  # 檢查 g.user 是否存在
def recent_messages(self, limit=50):
    # API 邏輯...
```

## 目前 API 端點

### 聊天訊息 API (ChatMessageApi)

| 端點 | 方法 | 功能 | 認證 |
|------|------|------|------|
| `/api/v1/chatmessageapi/recent/50` | GET | 獲取最近訊息 | JWT |
| `/api/v1/chatmessageapi/history` | GET | 獲取歷史訊息 (分頁) | JWT |
| `/api/v1/chatmessageapi/send` | POST | 發送新訊息 | JWT |
| `/api/v1/chatmessageapi/delete/<id>` | POST | 軟刪除訊息 | JWT |

### 用戶資料 API (UserProfileApi)

| 端點 | 方法 | 功能 | 認證 |
|------|------|------|------|
| `/api/v1/userprofileapi/me` | GET | 獲取我的資料 | JWT |
| `/api/v1/userprofileapi/update-profile` | POST | 更新個人資料 | JWT |
| `/api/v1/userprofileapi/online-users` | GET | 獲取線上用戶 | JWT |
| `/api/v1/userprofileapi/set-online-status` | POST | 設置線上狀態 | JWT |

### 頻道 API (ChatChannelApi)

| 端點 | 方法 | 功能 | 認證 |
|------|------|------|------|
| `/api/v1/chatchannelapi/public-channels` | GET | 獲取公開頻道 | JWT |
| `/api/v1/chatchannelapi/my-channels` | GET | 獲取我的頻道 | JWT |
| `/api/v1/chatchannelapi/create-channel` | POST | 建立新頻道 | JWT |

## 前端 API 呼叫實現

### 1. 認證 Token 管理

```typescript
// stores/user.ts
export const useUserStore = defineStore("user", {
  state: () => ({
    accessToken: null as string | null,
    isAuthenticated: false,
  }),

  actions: {
    async login(credentials) {
      const response = await $fetch('/api/v1/auth/login', {
        method: 'POST',
        body: credentials
      });
      
      this.accessToken = response.access_token;
      localStorage.setItem("access_token", response.access_token);
    }
  }
});
```

### 2. API 請求配置

```typescript
// stores/channel.ts - 獲取頻道訊息
async fetchChannelMessages(channelId: number) {
  const config = useRuntimeConfig();
  const userStore = useUserStore();

  const response = await $fetch(
    `${config.public.apiBase}/api/v1/chatmessageapi/recent/50?channel_id=${channelId}`,
    {
      credentials: "include",
      headers: {
        Authorization: `Bearer ${userStore.accessToken}`,  // JWT Token
        "Content-Type": "application/json",
      },
    }
  );
  
  return response.result;
}
```

### 3. 自動 Token 驗證

```typescript
// stores/user.ts - 初始化時檢查 Token
initAuth() {
  if (import.meta.client) {
    const token = localStorage.getItem("access_token");
    if (token) {
      // 檢查 token 是否過期
      const payload = JSON.parse(atob(token.split(".")[1]));
      const currentTime = Math.floor(Date.now() / 1000);

      if (payload.exp && payload.exp > currentTime) {
        this.accessToken = token;
        this.isAuthenticated = true;
        this.fetchUserProfile();
      } else {
        this.logout(); // Token 過期，清除認證狀態
      }
    }
  }
}
```

## 安全特性

### 1. Token 過期處理

- JWT Token 設置 7 天過期時間
- 前端自動檢查 Token 有效性
- 過期時自動清除並重定向登入

### 2. 權限分層

```python
# 業務層權限檢查
def pre_get(self, obj):
    if not g.user:
        raise Exception("未認證")
    if obj.sender_id != g.user.id and not self._is_admin():
        raise Exception("無權限查看其他用戶的訊息")
```

### 3. 資料隔離

- 用戶只能存取自己的資料
- 頻道權限檢查 (公開/私人)
- 管理員權限檢查

## 請求/回應範例

### 獲取最近訊息

```bash
# 請求
GET /api/v1/chatmessageapi/recent/50?channel_id=1
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

# 回應
{
  "result": [
    {
      "id": 123,
      "content": "Hello World",
      "sender_id": 6,
      "sender_name": "admin",
      "message_type": "text",
      "channel_id": 1,
      "created_on": "2024-01-15T10:30:00Z"
    }
  ],
  "count": 1
}
```

### 發送訊息

```bash
# 請求
POST /api/v1/chatmessageapi/send
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json

{
  "content": "新訊息內容",
  "message_type": "text",
  "channel_id": 1
}

# 回應
{
  "message": "訊息發送成功",
  "data": {
    "id": 124,
    "content": "新訊息內容",
    "sender_id": 6,
    "created_on": "2024-01-15T10:31:00Z"
  }
}
```

## 總結

目前的 API 實現使用：

1. **JWT Bearer Token 認證**: 無狀態、跨域友好
2. **自定義 `@jwt_required` 裝飾器**: 取代 Flask-AppBuilder 的 `@has_access`
3. **多層權限檢查**: API 層 + 業務邏輯層
4. **前端 Token 管理**: 自動過期檢查、localStorage 持久化
5. **RESTful API 設計**: 標準 HTTP 方法和狀態碼

這個架構提供了現代化的 API 認證機制，同時保持了良好的安全性和用戶體驗。