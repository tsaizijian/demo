# 聊天室 v2.0

一個現代化的即時聊天應用程式，採用 Flask + Vue.js 全端架構，支援多頻道聊天、即時訊息、用戶管理等功能。

## 🚀 主要功能

### 💬 聊天功能

- **即時訊息**：基於 WebSocket 的即時通訊
- **多頻道支援**：支援公開和私人頻道
- **訊息歷史**：游標式分頁載入歷史訊息
- **訊息類型**：文字訊息、系統訊息
- **線上狀態**：即時顯示用戶線上狀態

### 🏗️ 頻道管理

- **建立頻道**：用戶可建立公開或私人頻道
- **頻道設定**：頻道創建者可編輯頻道資訊
- **軟刪除功能**：頻道可安全刪除並保留所有訊息
- **恢復功能**：已刪除的頻道可以恢復
- **權限控制**：僅創建者可管理自己的頻道

### 👥 用戶系統

- **註冊/登入**：完整的用戶認證系統
- **個人資料**：可自訂顯示名稱、頭像、個人簡介
- **JWT 認證**：安全的 Token 驗證機制
- **權限管理**：Admin 和一般用戶權限分級

## 🛠️ 技術架構

### 後端技術棧

- **Flask**: Python Web 框架
- **Flask-AppBuilder**: 快速建構管理界面
- **Flask-SocketIO**: WebSocket 即時通訊
- **Flask-Login**: 用戶會話管理
- **PyJWT**: JWT Token 驗證
- **SQLAlchemy**: ORM 數據庫操作
- **SQLite**: 輕量級資料庫

### 前端技術棧

- **Vue.js 3**: 現代化前端框架
- **Nuxt.js**: Vue.js 全端框架
- **TypeScript**: 型別安全的 JavaScript
- **Pinia**: 狀態管理
- **PrimeVue**: UI 組件庫
- **Tailwind CSS**: 實用優先的 CSS 框架
- **Socket.IO Client**: WebSocket 客戶端

## 📦 安裝與部署

### 環境需求

- Python 3.11+
- Node.js 20+
- pnpm (推薦) 或 npm

### 後端設置

1. **安裝 Python 依賴**

```bash
uv venv --python 3.11
.\.venv\Scripts\activate.ps1
uv init
# 或使用 uv
uv sync
```

2. **環境變數設置**

```bash
# 在 backend 目錄建立 .env 檔案或直接設置
SECRET_KEY="thisisatruechatroomtouse"
SQLALCHEMY_DATABASE_URI="sqlite:///../app.db"
```

3. **初始化資料庫**

```bash
flask fab create-app
flask fab create-db
flask fab create-admin
```

4. **啟動後端服務**

```bash
python run.py
```

後端服務會運行在 `http://localhost:8080`

### 前端設置

1. **安裝 Node.js 依賴**

```bash
cd frontend
pnpm install
```

2. **啟動開發服務器**

```bash
pnpm dev
```

前端應用會運行在 `http://localhost:3000`

### 生產環境部署

1. **建構前端**

```bash
cd frontend
pnpm build
```

2. **配置環境變數**

```bash
# 後端 .env
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///app.db
CORS_ORIGINS=http://localhost:3000

# 前端 nuxt.config.ts
export default defineNuxtConfig({
  runtimeConfig: {
    public: {
      apiBase: 'http://your-backend-url'
    }
  }
})
```

## 🔧 配置說明

### 後端配置 (`backend/config.py`)

```python
# 資料庫設定
SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'

# JWT 設定
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
SECRET_KEY = 'your-secret-key'

# CORS 設定
CORS_ORIGINS = ['http://localhost:3000']
```

### 前端配置 (`frontend/nuxt.config.ts`)

```typescript
export default defineNuxtConfig({
  runtimeConfig: {
    public: {
      apiBase: "http://localhost:8080",
    },
  },
});
```

## 📁 項目結構

```
chatroom_v2/
├── backend/                 # 後端 Flask 應用
│   ├── app/
│   │   ├── __init__.py     # Flask 應用初始化
│   │   ├── models.py       # 資料模型
│   │   ├── apis.py         # REST API 端點
│   │   ├── auth.py         # 認證系統
│   │   ├── socketio_server.py # WebSocket 處理
│   │   └── views.py        # 視圖層
│   ├── config.py           # 配置文件
│   ├── run.py             # 應用啟動點
│   └── pyproject.toml     # Python 依賴管理
├── frontend/               # 前端 Vue.js 應用
│   ├── components/         # Vue 組件
│   ├── pages/             # 頁面路由
│   ├── stores/            # Pinia 狀態管理
│   ├── composables/       # 組合式函數
│   ├── middleware/        # 路由中間件
│   └── nuxt.config.ts     # Nuxt 配置
└── README.md              # 項目說明
```

## 🎯 API 文檔

### 認證 API

```http
POST /api/v1/auth/login
POST /api/v1/register/signup
GET  /api/v1/auth/me
```

### 頻道 API

```http
GET  /api/v1/chatchannelapi/public-channels
GET  /api/v1/chatchannelapi/my-channels
POST /api/v1/chatchannelapi/create-channel
POST /api/v1/chatchannelapi/delete-channel/<id>
POST /api/v1/chatchannelapi/restore-channel/<id>
GET  /api/v1/chatchannelapi/deleted-channels
```

### 訊息 API

```http
GET  /api/v1/chatmessageapi/recent/<limit>
GET  /api/v1/chatmessageapi/history
POST /api/v1/chatmessageapi/send
POST /api/v1/chatmessageapi/delete/<id>
```

### 用戶 API

```http
GET  /api/v1/userprofileapi/me
POST /api/v1/userprofileapi/update-profile
GET  /api/v1/userprofileapi/online-users
POST /api/v1/userprofileapi/set-online-status
```

## 🔐 安全特性

- **JWT 認證**：安全的 Token 驗證機制
- **權限控制**：基於角色的訪問控制
- **CORS 保護**：跨域請求安全控制
- **輸入驗證**：前後端雙重數據驗證
- **軟刪除**：數據安全刪除，可恢復
- **會話管理**：自動 Token 過期和刷新

## 🚦 開發指南

### 添加新功能

1. **後端 API**

   - 在 `models.py` 中定義數據模型
   - 在 `apis.py` 中實現 REST API
   - 在 `socketio_server.py` 中添加 WebSocket 事件

2. **前端組件**
   - 在 `stores/` 中添加狀態管理
   - 在 `components/` 中建立 Vue 組件
   - 在 `pages/` 中添加路由頁面

### 頻道刪除與恢復功能

#### 使用流程

1. **刪除頻道**：

   - 頻道創建者在頻道列表中懸停自己創建的頻道
   - 點擊出現的齒輪圖標設定按鈕
   - 選擇「刪除頻道」
   - 確認刪除操作

2. **恢復頻道**：
   - 進入設定 → 已刪除的頻道
   - 查看已刪除頻道列表
   - 點擊「恢復」按鈕
   - 確認恢復操作

#### 技術實現

- **軟刪除**：設定 `is_active = False`，保留所有訊息數據
- **權限控制**：僅創建者可刪除和恢復自己的頻道
- **安全防護**：防止刪除預設頻道 (ID=1)
- **用戶體驗**：確認彈窗、成功/錯誤提示、載入狀態

### 代碼風格

- **後端**：遵循 PEP 8 Python 編碼規範
- **前端**：使用 ESLint + Prettier 格式化

## 📝 更新日誌

### v2.0.0 (2024-08-16)

- ✨ 新增頻道軟刪除功能
- ✨ 新增頻道恢復功能
- ✨ 改進權限控制系統
- 🐛 修復 WebSocket 連接問題
- 🎨 改進 UI/UX 設計
- 🔧 更新 PrimeVue 組件 (OverlayPanel → Popover)

### v1.0.0 (2024-08-01)

- 🎉 初始版本發布
- ✨ 基本聊天功能
- ✨ 用戶認證系統
- ✨ 頻道管理功能

## 🤝 貢獻指南

1. Fork 這個倉庫
2. 建立功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

## 📄 授權條款

本項目採用 MIT 授權條款

## 🐛 問題回報

如果您發現任何問題，請在 GitHub Issues 頁面提交問題回報。

---

⭐ 如果這個項目對您有幫助，請給個 Star 支持一下！
