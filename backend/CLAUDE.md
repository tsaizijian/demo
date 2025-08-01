# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Start Development Server

```bash
python run.py
```

The server runs on http://localhost:8080 with debug mode enabled.

### Database Management

- Database file: `app.db` (SQLite)  
- Models are auto-created via `db.create_all()` in `app/views.py:197`
- Test database operations: `python test_database.py`

### Admin Interface

- Create admin user: `flask fab create-admin`
- Admin interface: http://localhost:8080/login/
- API documentation: http://localhost:8080/swagger/v1

### Internationalization

- Babel configuration: `babel/babel.cfg`
- Extract messages: `pybabel extract -F babel/babel.cfg -k lazy_gettext -o babel/messages.pot .`
- Update translations: `pybabel update -i babel/messages.pot -d app/translations`
- Compile translations: `pybabel compile -d app/translations`

## Architecture Overview

### Flask-AppBuilder Structure

This is a Flask-AppBuilder application with a custom chat system built on top. The architecture follows Flask-AppBuilder best practices:

- **Models** (`app/models.py`): Core data models using SQLAlchemy with Flask-AppBuilder's User model
- **Views** (`app/views.py`): Flask-AppBuilder ModelViews for admin interface + API endpoints
- **Custom Views**: Separate modules for each functional area:
  - `app/chatroom.py`: Chat room creation, joining, member management
  - `app/message.py`: Message sending, file uploads, message history
  - `app/private_message.py`: Private messaging and user status
  - `app/admin.py`: Administrative functions (kick, promote, delete messages)
- **Base Views** (`app/base_views.py`): Unified base class with common functionality

### Database Models

Core entities and relationships (following Flask-AppBuilder best practices):

- **User**: Flask-AppBuilder's built-in User model (`ab_user` table)
- **ChatRoom**: Chat rooms with privacy settings and creator tracking
- **RoomMember**: Many-to-many relationship between users and rooms with admin privileges  
- **Message**: Chat messages with support for different types (text, file, image)
- **MessageAttachment**: File attachments linked to messages
- **PrivateMessage**: Direct messages between users
- **UserStatus**: Online/offline status with custom status messages

All models inherit from `Model` and `AuditMixin` for automatic audit trail functionality.

### Authentication System ✅ **BEST PRACTICES IMPLEMENTED**

**✅ 使用 Flask-AppBuilder 內建認證系統**
- Uses Flask-AppBuilder's built-in User model and authentication
- **Self-registration enabled**: Users can register at `/register/form`
- No custom session management - fully integrated with FAB security
- `current_user` available throughout the application
- `@has_access` decorators work properly
- FAB UI logout clears authentication state correctly
- New users automatically get "Public" role

### API Structure

All custom API endpoints return JSON with Chinese language responses:

- `/chatroom/*`: Room creation, joining, member management
- `/message/*`: Message sending, file upload/download, history
- `/private/*`: Private messaging, conversation lists
- `/status/*`: User online status management
- `/admin/*`: Administrative functions for room management

### File Upload System

- Upload directory: `app/static/uploads/`
- User-specific subdirectories: `uploads/{user_id}/`
- Supported file types: .txt, .md, .jpg, .jpeg, .png, .gif, .pdf, .doc, .docx
- Files stored with UUID prefixes for uniqueness

### Configuration

- Main config: `config.py` (loads from environment variables)
- Template config: `config.py.tpl`
- Required environment variables:
  - `SECRET_KEY`: Flask secret key
  - `SQLALCHEMY_DATABASE_URI`: Database connection string

### Internationalization

- Supported languages: English, Portuguese, Spanish, German, Chinese, Russian, Polish, Japanese
- Translation files in `app/translations/`
- JSON format for custom translations: `app/translations/{lang}.json`
- Babel integration for Flask-AppBuilder translations

### Key Implementation Details

- All API responses use Chinese language for error messages and responses
- File uploads use secure filenames and UUID prefixes
- Room creators automatically become admins
- Private rooms require membership to view members
- Message history supports pagination
- Admin functions check both room admin status and creator status
- User status tracking with automatic last_seen updates

## Testing

Comprehensive API testing guide available in `API_TESTING_GUIDE.md` with curl examples for all endpoints.

## ✅ 最佳實踐指導原則 (已完成實作)

**✅ Flask-AppBuilder 最佳實踐已完全實現:**

### ✅ 模型設計
- **✅ 使用 Flask-AppBuilder 內建的 User 模型** - 不再使用自定義 ChatUser
- **✅ 所有模型繼承 `Model` 和 `AuditMixin`** - 提供標準化審計欄位
- **✅ 正確的外鍵關聯** - 所有用戶關聯使用 `ForeignKey('ab_user.id')`

### ✅ 視圖架構  
- **✅ 統一基礎類別** - 所有 View 繼承 `ChatBaseView` 避免程式碼重複
- **✅ 使用 `current_user`** - 透過 `_get_current_user()` 方法獲取 Flask-AppBuilder 的當前用戶
- **✅ 權限裝飾器** - 所有端點使用 `@has_access` 確保權限控制
- **✅ 基礎權限設定** - 每個 View 定義 `base_permissions` 清單

### ✅ 認證系統
- **✅ 移除自定義認證** - 完全移除 `app/auth.py` 和手工 session 驗證
- **✅ 整合 FAB 認證** - 使用 Flask-AppBuilder 標準登入/登出機制
- **✅ 權限相容性** - `@has_access` 裝飾器正常運作
- **✅ 用戶管理** - 透過 FAB 內建用戶管理介面

### ✅ 資料庫結構
- **✅ 標準 FAB 表結構** - 使用 `ab_user`, `ab_role` 等標準表
- **✅ 審計欄位** - 所有模型自動包含 `created_on`, `changed_on`, `created_by`, `changed_by`
- **✅ 關聯完整性** - 所有外鍵正確指向 Flask-AppBuilder User 模型

## 開發風格

### ✅ 已實現的模式
- **✅ 裝飾器驅動權限** - 使用 `@has_access` 而非手動權限檢查
- **✅ 統一權限方法** - `_check_room_access()`, `_is_room_admin()`, `_is_room_creator()` 等共用方法
- **✅ 模組化視圖** - 每個功能區域獨立的視圖模組
- **✅ AppBuilder 相容** - 完全相容 Flask-AppBuilder 的設計模式

### 持續改進方向
- 優先使用 `ModelRestApi` 自動生成 REST API 而非手寫端點
- 考慮將更多 CRUD 操作遷移到 `ModelView` 配置
- 擴展使用 Flask-AppBuilder 的角色和群組管理功能

## 專案架構特色

### ✅ 基礎類別系統 (已完成)
- **`ChatBaseView`** (`app/base_views.py`): 
  - 提供統一的 `_get_current_user()` 方法回傳 Flask-AppBuilder 的 `current_user`
  - 實作共用權限檢查邏輯
  - 所有自定義視圖繼承此類別

### ✅ 認證整合 (已完成)
- **完全移除自定義認證系統** - 不再有 session 手工管理
- **Flask-AppBuilder 標準流程** - 登入/登出透過 FAB 處理
- **current_user 全域可用** - 在所有視圖中可直接存取當前用戶

### ✅ 資料庫最佳化 (已完成)
- **AuditMixin 審計** - 所有變更自動記錄時間和用戶
- **標準關聯** - 外鍵統一指向 `ab_user.id`
- **關聯完整性** - UserStatus 等模型正確指定 foreign_keys

# 預設導入元件

本專案預設已匯入以下常用元件:

```python
from flask_appbuilder import ModelView, Model, AppBuilder, expose, has_access
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.models.mixins import AuditMixin
from flask_appbuilder.security.sqla.models import User  # FAB User model
from flask_login import current_user
from .base_views import ChatBaseView
```

## 🎉 重構完成總結

此專案已成功從「低階的手工 session 驗證」升級為完整的 Flask-AppBuilder 最佳實踐實作：

- ✅ **使用 FAB User 模型** - 移除自定義 ChatUser，直接使用 Flask-AppBuilder 標準用戶模型
- ✅ **整合 FAB 認證** - `@has_access` 裝飾器正常運作，`current_user` 全域可用
- ✅ **統一權限管理** - 透過 Flask-AppBuilder 權限框架處理所有存取控制
- ✅ **標準資料庫結構** - 使用 `ab_user` 等 FAB 標準表結構
- ✅ **審計欄位支援** - 所有模型繼承 `AuditMixin` 提供變更追蹤

現在的系統完全符合 Flask-AppBuilder 的設計哲學和最佳實踐！