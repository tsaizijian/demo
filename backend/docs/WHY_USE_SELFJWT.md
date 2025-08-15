# 為何使用自定義 jwt

1.  Flask-AppBuilder 兼容性問題

Flask-AppBuilder 有自己的認證架構，與 Flask-JWT-Extended 存在衝突：

- Flask-AppBuilder 使用 SecurityManager 和 @has_access 裝飾器
- Flask-JWT-Extended 使用 JWTManager 和 @jwt_required 裝飾器
- 兩者的認證流程和用戶對象管理不兼容

2. 需要自定義權限邏輯

我們需要區分兩種不同的權限：

# 管理界面權限 - 只有 Admin 可以存取

admin_view_names = [
'ChatMessageView', 'UserProfileView', 'ChatChannelView'
]

# API 端點權限 - 認證用戶都可以存取

api_view_names = [
'ChatMessageApi', 'UserProfileApi', 'ChatChannelApi'
]

Flask-JWT-Extended 無法輕易實現這種複雜的權限分層。

3. 與 Flask-Login 整合

我們需要同時支援：

- Session-based 認證 (管理界面)
- Token-based 認證 (API)

# 自定義實現可以同時設置兩者

g.user = user # Flask g 對象
login_user(user) # Flask-Login current_user

4. 完全控制認證流程

自定義實現讓我們可以：

def jwt_auth_handler(self): # 1. 完全控制 token 解碼邏輯
payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])

      # 2. 自定義用戶驗證
      user = self.get_user_by_id(user_id)
      if user and user.is_active:
          g.user = user

      # 3. 靈活的錯誤處理
      except jwt.ExpiredSignatureError:
          # 自定義過期處理

5. 避免依賴衝突

Flask-JWT-Extended 可能會與 Flask-AppBuilder 的其他組件產生衝突：

- 中間件衝突
- 配置衝突
- 錯誤處理衝突

6. 為什麼 SocketIO 還用 Flask-JWT-Extended？

# socketio_server.py

from flask_jwt_extended import decode_token, get_jwt_identity

這是因為：

- SocketIO 認證是獨立的認證流程
- Flask-JWT-Extended 提供了便利的 SocketIO 整合
- 不會與主要的 API 認證產生衝突

總結

使用自定義 JWT 是為了：

1. 兼容性: 與 Flask-AppBuilder 無縫整合
2. 靈活性: 實現複雜的權限分層邏輯
3. 控制權: 完全掌控認證流程
4. 穩定性: 避免第三方套件的衝突和限制

這樣的架構雖然需要更多自定義代碼，但提供了最大的靈活性和穩定性，特別適合我們這種需要同時支援管理
界面和 API 的複雜應用場景。
