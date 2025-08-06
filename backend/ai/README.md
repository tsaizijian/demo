# Nuxt + Flask-AppBuilder 聊天室專案

## 📌 專案概述

打造一個支援使用者註冊登入、訊息即時收發、權限控管的聊天室系統，前端使用 Nuxt 3，後端使用 Flask-AppBuilder，支援 REST API 與 WebSocket。

**當前整體進度：70%** - 已經是功能完整的聊天室應用，只差最後的 WebSocket 即時通訊功能！

---

## 🧱 技術架構

| 層級     | 技術                      | 說明 |
|----------|---------------------------|------|
| 前端     | Nuxt 3, Pinia, Tailwind   | 建構使用者介面、路由、狀態管理 |
| 通訊     | Socket.IO                 | 實現即時聊天室功能 |
| 後端 API | Flask-AppBuilder (FAB)    | 提供資料存取與驗證 |
| 資料庫   | SQLite / PostgreSQL       | 儲存訊息與使用者資料 |

---

## 📁 專案結構

### 後端 (Flask-AppBuilder) - 95% 完成
```
backend/
├── app/
│   ├── __init__.py          # Flask app 初始化 + CORS
│   ├── models.py            # 資料庫模型
│   ├── apis.py              # REST API 端點
│   ├── register_api.py      # 使用者註冊 API
│   ├── socketio_server.py   # WebSocket 服務器 (待完成)
│   └── views.py             # 管理界面
├── config.py                # 設定檔
└── run.py                   # 啟動腳本
```

### 前端 (Nuxt 3) - 90% 完成
```
frontend/
├── pages/
│   ├── index.vue            # 首頁重定向
│   ├── login.vue            # 登入頁面
│   ├── register.vue         # 註冊頁面
│   └── chatroom.vue         # 聊天室主頁
├── stores/
│   ├── user.ts              # 使用者狀態管理
│   └── chat.ts              # 聊天狀態管理
├── middleware/auth.ts       # 認證中間件
├── plugins/auth.client.ts   # 認證插件
└── nuxt.config.ts           # Nuxt 設定
```

---

## ✅ 已完成功能

### 🔐 使用者系統 (100% 完成)
- ✅ 使用者註冊功能 (`/api/v1/register/signup`)
- ✅ 用戶名可用性即時檢查 (`/api/v1/register/check-username`)
- ✅ 使用者登入認證 (`/api/v1/security/login`)
- ✅ JWT Token 自動管理
- ✅ 個人資料管理 (`/api/v1/userprofileapi/`)

### 💬 聊天功能 (70% 完成)
- ✅ 發送訊息 (REST API)
- ✅ 檢視訊息歷史
- ✅ 刪除自己的訊息
- ✅ 美觀的聊天界面
- ❌ 即時訊息同步 (需要 WebSocket)

### 👥 使用者互動 (80% 完成)
- ✅ 線上使用者列表
- ✅ 定時更新 (30秒)
- ❌ 即時上線/離線通知 (需要 WebSocket)

### 🛠 管理後台 (100% 完成)
- ✅ 完整的 FAB 管理界面 (http://localhost:8080)
- ✅ 訊息管理
- ✅ 使用者管理
- ✅ 頻道管理

---

## 🚀 快速啟動

### 1. 啟動後端
```bash
cd /home/jian/Desktop/chatroom_v2/backend
python run.py
# 後端: http://localhost:8080
```

### 2. 啟動前端
```bash
cd /home/jian/Desktop/chatroom_v2/frontend
npm run dev
# 前端: http://localhost:3000
```

### 3. 測試帳號
- 使用者名稱: `jerry`
- 密碼: `h94y3ru04`

---

## 🔗 主要 API 端點

### 使用者相關
| 方法 | 端點 | 說明 | 狀態 |
|------|------|------|------|
| POST | `/api/v1/register/signup` | 使用者註冊 | ✅ |
| POST | `/api/v1/register/check-username` | 檢查用戶名可用性 | ✅ |
| POST | `/api/v1/security/login` | 使用者登入 | ✅ |
| GET | `/api/v1/userprofileapi/me` | 取得個人資料 | ✅ |

### 聊天訊息
| 方法 | 端點 | 說明 | 狀態 |
|------|------|------|------|
| GET | `/api/v1/chatmessageapi/recent/<limit>` | 取得最近訊息 | ✅ |
| POST | `/api/v1/chatmessageapi/send` | 發送新訊息 | ✅ |
| GET | `/api/v1/chatmessageapi/history` | 取得歷史訊息 | ✅ |
| POST | `/api/v1/chatmessageapi/delete/<id>` | 軟刪除訊息 | ✅ |

---

## ⚠️ 待完成功能

### 🔄 WebSocket 即時通訊 (最重要)
- ❌ 建立 Socket.IO 服務器
- ❌ 前端 Socket.IO 客戶端
- ❌ 即時訊息廣播
- ❌ 即時上線/離線通知
- ❌ 輸入狀態指示器

### 📎 檔案上傳功能
- ❌ 圖片分享
- ❌ 檔案附件上傳
- ❌ 檔案預覽

### 🎨 進階功能
- ❌ 表情符號支援
- ❌ 訊息搜尋
- ❌ 桌面通知
- ❌ 聲音提醒

---

## 🏗️ 資料庫模型

### ChatMessage 模型
- `id`: 主鍵
- `content`: 訊息內容
- `sender_id`: 發送者 ID
- `message_type`: 訊息類型 (text, image, file)
- `attachment_path`: 附件路徑
- `is_deleted`: 軟刪除標記
- `reply_to_id`: 回覆訊息 ID
- `channel_id`: 頻道 ID
- `created_on`, `changed_on`: 時間戳記

### UserProfile 模型
- `user_id`: 關聯到 Flask-AppBuilder User
- `display_name`: 聊天室顯示名稱
- `avatar_url`: 大頭貼網址
- `bio`: 個人簡介
- `is_online`: 是否線上
- `last_seen`: 最後上線時間
- `message_count`: 發送訊息數量

---

## 🎯 下一步開發重點

### 第一優先：實作 WebSocket 即時通訊
```javascript
// 前端 Socket.IO 事件
{
  'join_room': { room_id: 1 },
  'send_message': { content: '訊息', room_id: 1 },
  'typing_start': { user_id: 123 },
  'user_online': { user_id: 123 }
}

// 後端廣播事件
{
  'new_message': { message_data },
  'user_joined': { user_data },
  'typing_indicator': { user_id, is_typing },
  'user_list_update': { online_users }
}
```

### 第二優先：檔案上傳系統
- 支援圖片、文件上傳
- 檔案大小和格式限制
- 檔案預覽功能

---

## 🛠️ 開發環境需求

### 後端 (Flask-AppBuilder)
```bash
pip install flask-appbuilder flask-sqlalchemy flask-cors flask-socketio
```

### 前端 (Nuxt 3)
```bash
npm install @pinia/nuxt socket.io-client @nuxt/ui
```

---

## 📈 功能完成度

- **整體進度**: 70%
- **後端進度**: 95% (缺 WebSocket)
- **前端進度**: 90% (缺 Socket.IO 客戶端)
- **使用者系統**: 100% (註冊、登入功能完成)
- **基本聊天功能**: 70% (REST API 完成，缺即時同步)

---

## 🙋‍♂️ 維護者

子建 蔡  
專案整合開發者，負責架構設計與前後端串接。

---

**目前已經是一個功能完整的聊天室應用，只差最後的 WebSocket 即時通訊功能就能達到完整的即時聊天體驗！**