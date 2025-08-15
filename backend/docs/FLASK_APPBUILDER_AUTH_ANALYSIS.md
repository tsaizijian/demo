# Flask-AppBuilder 認證機制分析

## 問題描述

在實作 JWT 認證時發現 Flask-AppBuilder 的 `@has_access` 裝飾器會跳過我們自定義的 `SecurityManager.has_access()` 方法，導致 JWT 認證失效。

## 原因分析

### Flask-AppBuilder `@has_access` 裝飾器的實作原理

Flask-AppBuilder 的 `@has_access` 裝飾器並不會調用 `SecurityManager.has_access()` 方法，而是直接依賴 Flask-Login 的認證機制：

```python
# Flask-AppBuilder 內部實作 (簡化版)
def has_access(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 直接使用 Flask-Login 的 current_user
        if not current_user.is_authenticated:
            # 重定向到登入頁面或返回 401
            return redirect('/login')

        # 檢查權限 (但不使用自定義的 SecurityManager.has_access)
        permission_name = f.__name__
        view_name = args[0].__class__.__name__

        # 直接查詢資料庫權限表，不調用 SecurityManager.has_access()
        if not _check_permission_from_db(permission_name, view_name, current_user):
            return abort(403)

        return f(*args, **kwargs)
    return decorated_function
```

### 為什麼跳過自定義的 has_access 方法

1. **架構設計**：`@has_access` 裝飾器是 Flask-AppBuilder 的核心安全機制，為了性能和穩定性，它直接操作底層權限系統

2. **Flask-Login 依賴**：`@has_access` 假設使用 Flask-Login 的 session-based 認證，期望 `current_user` 是一個已認證的 User 物件

3. **權限檢查方式**：裝飾器直接查詢資料庫中的權限表 (permission_view, role 等)，而不是透過 SecurityManager 的抽象方法

4. **繞過自定義邏輯**：這樣的設計讓 `@has_access` 無法感知到我們的 JWT 認證邏輯

## 目前的解決方案

### 使用 `@jwt_required` 裝飾器

```python
# 在 auth.py 中定義
def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'user') or not g.user:
            from flask import jsonify
            return jsonify({'error': '需要認證'}), 401
        return f(*args, **kwargs)
    return decorated_function
```

### JWT 認證流程

1. **JWT 中間件** (`jwt_auth_handler`): 在每個請求前檢查 JWT token
2. **用戶設置**: 解碼 JWT 後設置 `g.user` 和 Flask-Login 的 `current_user`
3. **API 認證**: 使用 `@jwt_required` 檢查 `g.user` 是否存在

### 實際應用

```python
# 原來使用 @has_access (不會調用自定義 has_access 方法)
@expose('/recent/<int:limit>')
@has_access  # ❌ 跳過自定義認證邏輯
def recent_messages(self, limit=50):
    # ...

# 改為使用 @jwt_required (正確使用 JWT 認證)
@expose('/recent/<int:limit>')
@jwt_required  # ✅ 使用我們的 JWT 認證
def recent_messages(self, limit=50):
    # ...
```

## 權限系統架構

### 雙層權限控制

```python
# auth.py 中的權限邏輯
def has_access(self, permission_name, view_name):
    # 管理界面權限 - 只有 Admin 可以存取
    admin_view_names = [
        'ChatMessageView', 'UserProfileView', 'ChatChannelView', 'UserView'
    ]

    # API 端點權限 - 認證用戶都可以存取
    api_view_names = [
        'ChatMessageApi', 'UserProfileApi', 'ChatChannelApi'
    ]

    if view_name in admin_view_names:
        # 管理界面：需要 Admin 角色
        return self._is_admin(current_user)
    elif view_name in api_view_names:
        # API 端點：認證用戶即可
        return True
    else:
        # 其他：使用預設行為
        return super().has_access(permission_name, view_name)
```

### 實際權限檢查順序

1. **JWT 中間件**: 檢查 Bearer token，設置 `g.user`
2. **API 層級**: `@jwt_required` 檢查 `g.user` 存在
3. **業務邏輯層級**: 在 `pre_get`, `pre_update`, `pre_delete` 中檢查具體權限

## 結論

Flask-AppBuilder 的 `@has_access` 裝飾器設計為與 Flask-Login session 認證緊密集成，無法直接支援 JWT token 認證。我們的解決方案是：

1. **保留自定義 SecurityManager**: 用於管理界面的權限控制
2. **使用 `@jwt_required` 裝飾器**: 用於 API 端點的 JWT 認證
3. **雙重認證機制**: 支援 session-based (管理界面) 和 token-based (API) 認證

這樣的架構既保持了 Flask-AppBuilder 管理界面的完整功能，又實現了現代化的 JWT API 認證。

```text
現在架構流程圖
┌───────────────────────────────────────────────┬───────────────────────────────────────────────┐
│        Session（後台 UI） / current_user     │             JWT（API） / g.user               │
├───────────────────────────────────────────────┼───────────────────────────────────────────────┤
│ [Browser]                                     │ [SPA / Client / 第三方]                       │
│   │                                           │   │                                           │
│ 1) /login 表單成功 → 設定 session cookie      │ 1) 每次請求攜帶 Authorization: Bearer <JWT>   │
│   │                                           │   │                                           │
│ 2) 每次請求：Flask-Login 由 cookie 載入使用者  │ 2) before_request：驗 JWT → 取出 user_id      │
│    → current_user = 已認證 User               │    → g.user = User（只存在於本次請求）        │
│   │                                           │   │                                           │
│ 3) @has_access                                │ 3) @jwt_required                              │
│    └─ 只檢查 current_user（不看 g.user）       │    └─ 只檢查 g.user（不需 current_user）       │
│   │                                           │   │                                           │
│ 4) SecurityManager / permission_view 檢查     │ 4) pre_get / pre_add / pre_update / pre_delete│
│    （Role ↔ can_list/show/edit/...）          │    等 hook：資源擁有者、頻道成員、租戶隔離等   │
│   │                                           │   │                                           │
│ 5) 通過 → 200 / 頁面                          │ 5) 通過 → 200 / JSON                           │
│    無權 → 403；未認證 → 302 /login            │    未認證 → 401；無權 → 403                   │
└───────────────────────────────────────────────┴───────────────────────────────────────────────┘


備註：
- @has_access 只看 flask_login.current_user，不會看 g.user
- g.user 是你在 JWT 驗證時自訂放的變數，FAB 不認

（可選）打通方案：request_loader（不寫 session，只在本次請求建立 current_user）
────────────────────────────────────────────────────────────────────────────────────────────────
[JWT] → before_request 驗證 → user_id → 查 User → request_loader 回傳 User
                                       ↓
                              current_user = 已認證 User（僅本次請求）
                                       ↓
                       讓 @has_access 也能用在 API 端點（仍可保留 @jwt_required）
```

┌─────────────────┐ ← Admin UI (高權限)
│ 管理界面 │ - 可以刪除所有資料
│ ChatMessageView │ - 可以修改系統設定
└─────────────────┘ - 可以管理用戶權限

┌─────────────────┐ ← User API (基本權限)
│ 聊天 API │ - 只能操作自己的資料
│ ChatMessageApi │ - 有業務邏輯限制
└─────────────────┘ - 受資源存取控制
