# 聊天室網站開發分階段計畫

## 階段 1：資料表設計與建立 ✅ 已完成 (2025-07-29)

- 設計資料表結構
- 建立資料庫與資料表
- 檢查資料表關聯

- [x] 完成資料表設計
- [x] 建立資料庫
- [x] 建立所有資料表
- [x] 資料表關聯測試通過

**完成項目：**
- 實作完整的資料模型 (models.py)
- 創建 .env 環境配置檔案
- 建立資料庫測試腳本 (test_database.py)
- 驗證所有資料表關聯正確運作

---

## 階段 2：用戶註冊與登入功能 ✅ 已完成 (2025-07-29)

- 實作用戶註冊、登入、登出
- 密碼加密與驗證
- 基本用戶資料管理

- [x] 註冊功能
- [x] 登入/登出功能
- [x] 密碼加密驗證
- [x] 用戶資料管理

**完成項目：**
- 創建認證 API (app/auth.py)
- 實作 bcrypt 密碼加密
- 用戶註冊 API: POST /authview/register
- 用戶登入 API: POST /authview/login  
- 用戶登出 API: POST /authview/logout
- 用戶資料管理 API: GET/PUT /authview/profile
- Session 管理機制

---

## 階段 3：聊天室與訊息功能 ✅ 已完成 (2025-07-29)

- 建立聊天室、加入/退出聊天室
- 訊息發送、接收、刪除
- 支援多種訊息型態（文字、圖片、檔案）

- [x] 聊天室建立/管理
- [x] 加入/退出聊天室
- [x] 訊息發送/接收
- [x] 訊息刪除
- [x] 圖片/檔案訊息

**完成項目：**
- 創建聊天室管理 API (app/chatroom.py)
- 創建訊息系統 API (app/message.py)
- 聊天室 API: POST /chatroomview/create, GET /chatroomview/list
- 成員管理 API: POST /chatroomview/join/<id>, POST /chatroomview/leave/<id>
- 訊息 API: POST /messageview/send, GET /messageview/room/<id>, DELETE /messageview/delete/<id>
- 檔案上傳 API: POST /messageview/upload
- 權限管理與安全檢查
- 分頁查詢支援

---

## 階段 4：進階功能與優化 ✅ 已完成 (2025-07-29)

- 私訊功能
- 權限與管理員功能
- 多語系、UI 優化

- [x] 私訊功能
- [x] 管理員權限
- [x] 多語系支援
- [x] UI/UX 優化

**完成項目：**
- 創建私訊系統 (app/private_message.py)
  - 一對一私人訊息
  - 對話列表管理
  - 未讀訊息標記
  - 用戶在線狀態
- 管理員權限系統 (app/admin.py)
  - 踢出用戶
  - 提升/降級管理員
  - 聊天室管理
  - 訊息管理權限
- 多語系支援 (app/i18n.py, app/translations/)
  - 中文、英文、日文介面
  - 動態語言切換
  - API 響應本地化
- UI/UX 優化
  - 現代化響應式介面
  - Bootstrap 5 設計
  - API 端點總覽頁面
  - 管理介面優化

---

# 資料表設計

## 1. users（用戶表）

- id（主鍵，自增）
- username（用戶名，唯一）
- password_hash（密碼雜湊）
- email（電子郵件，唯一）
- avatar_url（頭像連結，可選）
- created_at（註冊時間）

## 2. chat_rooms（聊天室表）

- id（主鍵，自增）
- name（聊天室名稱）
- description（聊天室描述，可選）
- is_private（是否為私密聊天室）
- created_by（建立者 id，外鍵 users.id）
- created_at（建立時間）

## 3. room_members（聊天室成員表）

- id（主鍵，自增）
- room_id（聊天室 id，外鍵 chat_rooms.id）
- user_id（用戶 id，外鍵 users.id）
- joined_at（加入時間）
- is_admin（是否為管理員）

## 4. messages（訊息表）

- id（主鍵，自增）
- room_id（聊天室 id，外鍵 chat_rooms.id）
- user_id（發送者 id，外鍵 users.id）
- content（訊息內容）
- message_type（訊息型態：文字、圖片、檔案等）
- created_at（發送時間）
- is_deleted（是否已刪除）

## 5. message_attachments（訊息附件表，可選）

- id（主鍵，自增）
- message_id（訊息 id，外鍵 messages.id）
- file_url（檔案連結）
- file_type（檔案型態）
- uploaded_at（上傳時間）

> 如需支援私訊，可再加一個 private_messages 表。
