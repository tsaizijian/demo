# 聊天室 API 測試指南

## 🚀 快速開始

### 1. 啟動應用
```bash
cd /home/jian/Desktop/chatroom_v2/backend
python run.py
```

應用將在 http://localhost:8080 啟動

### 2. 登入獲取 Token
```bash
curl -X POST http://localhost:8080/api/v1/security/login \
  -H "Content-Type: application/json" \
  -d '{"username": "jerry", "password": "h94y3ru04", "provider": "db"}'
```

**回應範例：**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## 📋 API 端點測試

### 🔐 認證相關

#### 登入
```bash
curl -X POST http://localhost:8080/api/v1/security/login \
  -H "Content-Type: application/json" \
  -d '{"username": "jerry", "password": "h94y3ru04", "provider": "db"}'
```

**注意：** 將返回的 `access_token` 用於後續所有API調用

---

### 💬 ChatMessage API

#### 1. 獲取所有訊息
```bash
curl -X GET "http://localhost:8080/api/v1/chatmessageapi/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

#### 2. 創建新訊息
```bash
curl -X POST "http://localhost:8080/api/v1/chatmessageapi/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello World", "message_type": "text"}'
```

#### 3. 獲取指定訊息
```bash
curl -X GET "http://localhost:8080/api/v1/chatmessageapi/1" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

#### 4. 更新訊息
```bash
curl -X PUT "http://localhost:8080/api/v1/chatmessageapi/1" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"content": "Updated message content"}'
```

#### 5. 刪除訊息
```bash
curl -X DELETE "http://localhost:8080/api/v1/chatmessageapi/1" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

#### 6. 自定義端點 - 獲取最近訊息
```bash
curl -X GET "http://localhost:8080/api/v1/chatmessageapi/recent/10" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

#### 7. 自定義端點 - 發送訊息
```bash
curl -X POST "http://localhost:8080/api/v1/chatmessageapi/send" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello from custom endpoint!", "message_type": "text"}'
```

#### 8. 自定義端點 - 歷史訊息
```bash
curl -X GET "http://localhost:8080/api/v1/chatmessageapi/history?page=1&per_page=20" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

#### 9. 自定義端點 - 軟刪除訊息
```bash
curl -X POST "http://localhost:8080/api/v1/chatmessageapi/delete/1" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

---

### 👤 UserProfile API

#### 1. 獲取所有使用者資料
```bash
curl -X GET "http://localhost:8080/api/v1/userprofileapi/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

#### 2. 創建使用者資料
```bash
curl -X POST "http://localhost:8080/api/v1/userprofileapi/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"display_name": "My Display Name", "bio": "This is my bio"}'
```

#### 3. 自定義端點 - 獲取我的資料
```bash
curl -X GET "http://localhost:8080/api/v1/userprofileapi/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

#### 4. 自定義端點 - 更新個人資料
```bash
curl -X POST "http://localhost:8080/api/v1/userprofileapi/update-profile" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"display_name": "Updated Name", "bio": "Updated bio", "timezone": "Asia/Taipei"}'
```

#### 5. 自定義端點 - 線上使用者列表
```bash
curl -X GET "http://localhost:8080/api/v1/userprofileapi/online-users" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

#### 6. 自定義端點 - 設定線上狀態
```bash
curl -X POST "http://localhost:8080/api/v1/userprofileapi/set-online-status" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"is_online": true}'
```

---

### 🏠 ChatChannel API

#### 1. 獲取所有頻道
```bash
curl -X GET "http://localhost:8080/api/v1/chatchannelapi/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

#### 2. 創建新頻道
```bash
curl -X POST "http://localhost:8080/api/v1/chatchannelapi/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"name": "General Chat", "description": "General discussion channel"}'
```

#### 3. 自定義端點 - 公開頻道列表
```bash
curl -X GET "http://localhost:8080/api/v1/chatchannelapi/public-channels" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

#### 4. 自定義端點 - 建立頻道
```bash
curl -X POST "http://localhost:8080/api/v1/chatchannelapi/create-channel" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"name": "New Channel", "description": "My new channel", "is_private": false, "max_members": 50}'
```

#### 5. 自定義端點 - 我的頻道
```bash
curl -X GET "http://localhost:8080/api/v1/chatchannelapi/my-channels" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

---

## 🔧 完整測試流程

### 1. 登入並保存 Token
```bash
# 登入獲取 token
TOKEN=$(curl -s -X POST http://localhost:8080/api/v1/security/login \
  -H "Content-Type: application/json" \
  -d '{"username": "jerry", "password": "h94y3ru04", "provider": "db"}' | \
  grep -o '"access_token":"[^"]*' | \
  grep -o '[^"]*$')

echo "Token: $TOKEN"
```

### 2. 創建使用者資料
```bash
curl -X POST "http://localhost:8080/api/v1/userprofileapi/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"display_name": "Test User", "bio": "I am a test user"}'
```

### 3. 創建頻道
```bash
curl -X POST "http://localhost:8080/api/v1/chatchannelapi/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Channel", "description": "Channel for testing"}'
```

### 4. 發送訊息
```bash
curl -X POST "http://localhost:8080/api/v1/chatmessageapi/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello from API test!", "message_type": "text"}'
```

### 5. 獲取所有訊息
```bash
curl -X GET "http://localhost:8080/api/v1/chatmessageapi/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

---

## 🐛 常見問題

### 1. 401 Unauthorized
- 確認 Token 是否正確
- 確認 Token 是否已過期（預設1小時）
- 重新登入獲取新 Token

### 2. 400 Bad Request
- 檢查 JSON 格式是否正確
- 確認必要欄位是否都有提供

### 3. 500 Internal Server Error
- 查看 Flask 應用的日誌輸出
- 確認資料庫連接是否正常

---

## 📊 API 回應格式

### 成功回應
```json
{
  "count": 10,
  "result": [...],
  "list_columns": [...],
  "label_columns": {...}
}
```

### 錯誤回應
```json
{
  "message": "Error description",
  "error": "Detailed error message"
}
```

---

## 🎯 測試檢查點

- [ ] 登入API正常工作
- [ ] 獲取訊息列表
- [ ] 創建新訊息（自動設定sender_id）
- [ ] 更新訊息內容
- [ ] 軟刪除訊息
- [ ] 創建使用者資料
- [ ] 更新個人資料
- [ ] 設定線上狀態
- [ ] 創建聊天頻道
- [ ] 獲取公開頻道列表
- [ ] 自定義端點正常工作

## 💡 提示

1. 使用 `jq` 工具格式化 JSON 回應：
```bash
curl ... | jq .
```

2. 將常用的 Token 存為環境變數：
```bash
export CHAT_TOKEN="your_token_here"
curl -H "Authorization: Bearer $CHAT_TOKEN" ...
```

3. 使用 Postman 或 Insomnia 等工具進行更方便的API測試

---

**祝測試順利！** 🎉