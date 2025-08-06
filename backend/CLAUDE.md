# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案概述

這是一個基於 Flask-AppBuilder 的現代聊天室系統，提供完整的聊天功能、私訊系統和管理介面。系統採用 Flask-AppBuilder 的最佳實踐，包含完整的權限管理、審計追蹤和多語言支援。
本專案採用 uv 作為 Python 套件與虛擬環境的管理工具，可提供更快的依賴安裝體驗與更簡潔的開發流程。

## 開發命令

### 啟動開發伺服器

```bash
python run.py
```

伺服器運行於 http://localhost:8080，開啟 debug 模式。

### 資料庫管理

- 資料庫檔案：`app.db` (SQLite)
- 模型自動建立：透過 `app/views.py:189` 中的 `db.create_all()`
- 建立管理員：`flask fab create-admin`

### 管理介面

- 管理員介面：http://localhost:8080/login/
- API 文件：http://localhost:8080/swagger/v1
- 使用者註冊：http://localhost:8080/register/form (可設定為禁用)

### 國際化

- Babel 設定：`babel/babel.cfg`
- 提取訊息：`pybabel extract -F babel/babel.cfg -k lazy_gettext -o babel/messages.pot .`
- 更新翻譯：`pybabel update -i babel/messages.pot -d app/translations`
- 編譯翻譯：`pybabel compile -d app/translations`

## 架構概述

### Flask-AppBuilder 整合

此專案完整採用 Flask-AppBuilder 架構，包含：

- **模型系統** (`app/models.py`): 使用 Flask-AppBuilder 的 User 模型與 SQLAlchemy
- **視圖系統** (`app/views.py`): ModelView 和 ModelRestApi 自動產生 CRUD 介面
- **自訂視圖模組**:
  - `app/chatroom.py`: 聊天室建立、加入、成員管理
  - `app/message.py`: 訊息發送、檔案上傳、歷史記錄
  - `app/private_message.py`: 私訊與用戶狀態管理
  - `app/admin.py`: 管理功能（踢人、升級、刪除訊息）
  - `app/user_api.py`: 用戶註冊 API
- **基礎視圖** (`app/base_views.py`): 統一的基礎類別與權限檢查

### 資料庫模型

核心實體與關聯（遵循 Flask-AppBuilder 最佳實踐）：

- **MyUser**: 繼承 Flask-AppBuilder 的 User 模型 (`ab_user` 表)
- **ChatRoom**: 聊天室，包含隱私設定與建立者追蹤
- **RoomMember**: 用戶與聊天室的多對多關聯，包含管理員權限
- **Message**: 聊天訊息，支援多種類型（文字、檔案、圖片）
- **MessageAttachment**: 訊息附件，連結至訊息
- **PrivateMessage**: 用戶間私訊
- **UserStatus**: 用戶線上狀態與自訂狀態訊息

所有模型繼承 `Model` 和 `AuditMixin` 提供自動審計追蹤功能。

### 認證系統 ✅ **最佳實踐已實現**

**✅ 完整 Flask-AppBuilder 認證整合**

- 使用 Flask-AppBuilder 內建的 User 模型和認證系統
- 支援自動註冊：用戶可在 `/register/form` 註冊（可設定禁用）
- 無自訂 session 管理 - 完全整合 FAB 安全性
- `current_user` 在整個應用程序中可用
- `@has_access` 裝飾器正常運作
- FAB UI 登出正確清除認證狀態
- 新用戶自動獲得 "Public" 角色
- 支援 Google OAuth 登入（需設定環境變數）

### API 結構

所有自訂 API 端點返回中文 JSON 回應：

- `/chatroom/*`: 聊天室建立、加入、成員管理

  - `POST /chatroom/create`: 建立聊天室
  - `GET /chatroom/list`: 列出可用聊天室
  - `POST /chatroom/join/<room_id>`: 加入聊天室
  - `POST /chatroom/leave/<room_id>`: 離開聊天室
  - `GET /chatroom/members/<room_id>`: 查看成員列表

- `/message/*`: 訊息發送、檔案上傳/下載、歷史記錄

  - `POST /message/send`: 發送訊息
  - `GET /message/room/<room_id>`: 獲取聊天室訊息（支援分頁）
  - `DELETE /message/delete/<message_id>`: 刪除訊息
  - `POST /message/upload`: 上傳附件
  - `GET /message/download/<attachment_id>`: 下載附件

- `/private/*`: 私訊、對話列表

  - `POST /private/send`: 發送私訊
  - `GET /private/conversations`: 獲取對話列表
  - `GET /private/messages/<user_id>`: 獲取與特定用戶的私訊
  - `DELETE /private/delete/<message_id>`: 刪除私訊
  - `PUT /private/mark_read/<message_id>`: 標記已讀

- `/status/*`: 用戶線上狀態管理

  - `PUT /status/update`: 更新用戶狀態
  - `GET /status/users`: 獲取所有用戶狀態

- `/admin/*`: 聊天室管理功能

  - `POST /admin/room/<room_id>/kick/<user_id>`: 踢出用戶
  - `POST /admin/room/<room_id>/promote/<user_id>`: 升級為管理員
  - `POST /admin/room/<room_id>/demote/<user_id>`: 撤銷管理員
  - `DELETE /admin/room/<room_id>/delete`: 刪除聊天室
  - `PUT /admin/room/<room_id>/update`: 更新聊天室資訊
  - `DELETE /admin/message/<message_id>/delete`: 管理員刪除訊息
  - `POST /admin/room/<room_id>/ban/<user_id>`: 禁止用戶

- `/api/register/*`: 用戶註冊 API
  - `POST /api/register/user`: 註冊新用戶
  - `POST /api/register/check-username`: 檢查用戶名可用性
  - `POST /api/register/check-email`: 檢查郵箱可用性
  - `GET /api/register/recaptcha-config`: 獲取 reCAPTCHA 設定

### 檔案上傳系統

- 上傳目錄：`app/static/uploads/`
- 用戶專屬子目錄：`uploads/{user_id}/`
- 支援檔案類型：.txt, .md, .jpg, .jpeg, .png, .gif, .pdf, .doc, .docx
- 檔案以 UUID 前綴儲存確保唯一性
- 檔案下載需要聊天室成員權限驗證

### 設定

- 主要設定：`config.py`（從環境變數載入）
- 範本設定：`config.py.tpl`
- 必要環境變數：
  - `SECRET_KEY`: Flask 密鑰
  - `SQLALCHEMY_DATABASE_URI`: 資料庫連接字串
  - `GOOGLE_CLIENT_ID`: Google OAuth 客戶端 ID（可選）
  - `GOOGLE_CLIENT_SECRET`: Google OAuth 客戶端密鑰（可選）
  - `RECAPTCHA_PUBLIC_KEY`: reCAPTCHA 公鑰（可選）
  - `RECAPTCHA_PRIVATE_KEY`: reCAPTCHA 私鑰（可選）

### 國際化

- 支援語言：英語、葡萄牙語、西班牙語、德語、中文、俄語、波蘭語、日語
- 翻譯檔案位於 `app/translations/`
- 自訂翻譯 JSON 格式：`app/translations/{lang}.json`
- Babel 整合用於 Flask-AppBuilder 翻譯

### 關鍵實作細節

- 所有 API 回應使用中文錯誤訊息和回應
- 檔案上傳使用安全檔名和 UUID 前綴
- 聊天室建立者自動成為管理員
- 私密聊天室需要成員身份才能查看成員
- 訊息歷史支援分頁
- 管理功能檢查聊天室管理員狀態和建立者狀態
- 用戶狀態追蹤與自動 last_seen 更新
- 軟刪除機制用於訊息和私訊

## 安全特性

- **reCAPTCHA 支援**: 註冊時可選的 reCAPTCHA 驗證
- **密碼驗證**: 密碼長度和複雜度要求
- **輸入驗證**: 用戶名、郵箱格式驗證
- **權限控制**: 基於 Flask-AppBuilder 的完整權限系統
- **檔案上傳安全**: 檔案類型限制和安全檔名
- **存取控制**: 聊天室成員驗證和管理員權限檢查

## ✅ 最佳實踐實現狀態

**✅ Flask-AppBuilder 最佳實踐已完全實現：**

### ✅ 模型設計

- **✅ 使用 Flask-AppBuilder 內建的 User 模型** - MyUser 繼承自 FAB User
- **✅ 所有模型繼承 `Model` 和 `AuditMixin`** - 提供標準化審計欄位
- **✅ 正確的外鍵關聯** - 所有用戶關聯使用 `ForeignKey('ab_user.id')`

### ✅ 視圖架構

- **✅ 統一基礎類別** - 所有 View 繼承 `ChatBaseView` 避免程式碼重複
- **✅ 使用 `current_user`** - 透過 `_get_current_user()` 方法獲取 Flask-AppBuilder 的當前用戶
- **✅ 權限裝飾器** - 所有端點使用 `@has_access` 確保權限控制
- **✅ 基礎權限設定** - 每個 View 定義 `base_permissions` 清單

### ✅ 認證系統

- **✅ 完整 FAB 認證整合** - 使用 Flask-AppBuilder 標準登入/登出機制
- **✅ 權限相容性** - `@has_access` 裝飾器正常運作
- **✅ 用戶管理** - 透過 FAB 內建用戶管理介面
- **✅ 註冊系統** - 自訂註冊 API 與 FAB 整合

### ✅ 資料庫結構

- **✅ 標準 FAB 表結構** - 使用 `ab_user`, `ab_role` 等標準表
- **✅ 審計欄位** - 所有模型自動包含 `created_on`, `changed_on`, `created_by`, `changed_by`
- **✅ 關聯完整性** - 所有外鍵正確指向 Flask-AppBuilder User 模型

## 開發模式

### ✅ 已實現的模式

- **✅ 裝飾器驅動權限** - 使用 `@has_access` 而非手動權限檢查
- **✅ 統一權限方法** - `_check_room_access()`, `_is_room_admin()`, `_is_room_creator()` 等共用方法
- **✅ 模組化視圖** - 每個功能區域獨立的視圖模組
- **✅ AppBuilder 相容** - 完全相容 Flask-AppBuilder 的設計模式
- **✅ API 優先設計** - 前後端分離架構

### 持續改進方向

- 考慮擴展使用 Flask-AppBuilder 的角色和群組管理功能
- 實作 WebSocket 支援即時訊息推送
- 添加更多檔案類型支援和檔案管理功能
- 實作聊天室黑名單功能

## 專案架構特色

### ✅ 基礎類別系統 (已完成)

- **`ChatBaseView`** (`app/base_views.py`):
  - 提供統一的 `_get_current_user()` 方法回傳 Flask-AppBuilder 的 `current_user`
  - 實作共用權限檢查邏輯
  - 所有自訂視圖繼承此類別

### ✅ 認證整合 (已完成)

- **完整 Flask-AppBuilder 認證系統** - 使用標準 FAB 登入/登出流程
- **`current_user` 全域可用** - 在所有視圖中可直接存取當前用戶
- **自訂註冊 API** - 與 FAB 用戶系統完整整合

### ✅ 資料庫最佳化 (已完成)

- **AuditMixin 審計** - 所有變更自動記錄時間和用戶
- **標準關聯** - 外鍵統一指向 `ab_user.id`
- **關聯完整性** - UserStatus 等模型正確指定 foreign_keys

# 預設導入元件

本專案預設已匯入以下常用元件：

```python
from flask_appbuilder import ModelView, Model, AppBuilder, expose, has_access, BaseView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.models.mixins import AuditMixin
from flask_appbuilder.security.sqla.models import User  # FAB User model
from flask_appbuilder.api import BaseApi
from flask_login import current_user
from .base_views import ChatBaseView
```

## 系統特色總結

此專案已成功實現了完整的 Flask-AppBuilder 聊天室系統：

- ✅ **完整 FAB 整合** - 使用 Flask-AppBuilder 標準用戶模型、認證系統
- ✅ **現代化 API 設計** - RESTful API 設計與完整權限控制
- ✅ **多功能聊天系統** - 公開/私密聊天室、私訊、檔案分享
- ✅ **完整管理功能** - 聊天室管理、用戶管理、訊息管理
- ✅ **安全性最佳實踐** - 權限驗證、輸入驗證、檔案上傳安全
- ✅ **國際化支援** - 多語言介面與 API 回應
- ✅ **審計追蹤** - 所有操作自動記錄審計資訊

現在的系統完全符合 Flask-AppBuilder 的設計哲學和現代 Web 應用程式的最佳實踐！
