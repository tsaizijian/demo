📝 用戶註冊 API 測試指南

🚀 API 端點概覽

基礎 URL: http://localhost:8080

| 端點                           | 方法 | 功能                | 需要 reCAPTCHA |
| ------------------------------ | ---- | ------------------- | -------------- |
| /api/register/recaptcha-config | GET  | 獲取 reCAPTCHA 配置 | ❌             |
| /api/register/check-username   | POST | 檢查用戶名可用性    | ❌             |
| /api/register/check-email      | POST | 檢查郵箱可用性      | ❌             |
| /api/register/user             | POST | 用戶註冊            | ✅             |

📋 測試步驟

1. 獲取 reCAPTCHA 配置

curl -X GET http://localhost:8080/api/register/recaptcha-config

預期響應:
{
"data": {
"enabled": true,
"site_key": "6LcNhpYrAAAAAJCTtC2XI1R1uRJu99N7eJiersiL"
},
"success": true
}

2. 檢查用戶名可用性

✅ 測試可用用戶名

curl -X POST http://localhost:8080/api/register/check-username \
 -H "Content-Type: application/json" \
 -d '{"username": "newuser2024"}'

預期響應:
{
"available": true,
"message": "用戶名可用",
"success": true
}

❌ 測試已存在用戶名

curl -X POST http://localhost:8080/api/register/check-username \
 -H "Content-Type: application/json" \
 -d '{"username": "admin"}'

❌ 測試無效用戶名格式

curl -X POST http://localhost:8080/api/register/check-username \
 -H "Content-Type: application/json" \
 -d '{"username": "ab"}'

預期響應:
{
"available": false,
"message": "用戶名必須為 3-20 個字符，只能包含字母、數字和下劃線",
"success": false
}

3. 檢查郵箱可用性

✅ 測試可用郵箱

curl -X POST http://localhost:8080/api/register/check-email \
 -H "Content-Type: application/json" \
 -d '{"email": "newuser@example.com"}'

❌ 測試無效郵箱格式

curl -X POST http://localhost:8080/api/register/check-email \
 -H "Content-Type: application/json" \
 -d '{"email": "invalid-email"}'

預期響應:
{
"available": false,
"message": "郵箱格式不正確",
"success": false
}

4. 用戶註冊測試

❌ 測試缺少 reCAPTCHA

curl -X POST http://localhost:8080/api/register/user \
 -H "Content-Type: application/json" \
 -d '{
"username": "testuser123",
"email": "test@example.com",
"first_name": "Test",
"last_name": "User",
"password": "password123"
}'

預期響應:
{
"message": "缺少 reCAPTCHA 驗證",
"success": false
}

❌ 測試無效 reCAPTCHA token

curl -X POST http://localhost:8080/api/register/user \
 -H "Content-Type: application/json" \
 -d '{
"username": "testuser123",
"email": "test@example.com",
"first_name": "Test",
"last_name": "User",
"password": "password123",
"recaptcha_response": "invalid_token"
}'

預期響應:
{
"message": "reCAPTCHA 驗證失敗: invalid-input-response",
"success": false
}

❌ 測試缺少必要字段

curl -X POST http://localhost:8080/api/register/user \
 -H "Content-Type: application/json" \
 -d '{
"username": "testuser123",
"recaptcha_response": "valid_token_here"
}'

預期響應:
{
"message": "缺少必要字段: email, first_name, last_name, password",
"success": false
}

🎯 前端集成指南

HTML 示例

  <!DOCTYPE html>
  <html>
  <head>
      <title>用戶註冊</title>
      <script src="https://www.google.com/recaptcha/api.js" async defer></script>
  </head>
  <body>
      <form id="registerForm">
          <input type="text" id="username" placeholder="用戶名" required>
          <input type="email" id="email" placeholder="郵箱" required>
          <input type="text" id="firstName" placeholder="名字" required>
          <input type="text" id="lastName" placeholder="姓氏" required>
          <input type="password" id="password" placeholder="密碼" required>

          <!-- reCAPTCHA widget -->
          <div class="g-recaptcha" data-sitekey="YOUR_SITE_KEY"></div>

          <button type="submit">註冊</button>
      </form>

      <script>
          // 獲取 reCAPTCHA 配置
          fetch('/api/register/recaptcha-config')
              .then(response => response.json())
              .then(data => {
                  if (data.success && data.data.enabled) {
                      document.querySelector('.g-recaptcha').setAttribute('data-sitekey', data.data.site_key);
                  }
              });

          // 提交表單
          document.getElementById('registerForm').addEventListener('submit', async (e) => {
              e.preventDefault();

              const recaptchaResponse = grecaptcha.getResponse();
              if (!recaptchaResponse) {
                  alert('請完成 reCAPTCHA 驗證');
                  return;
              }

              const formData = {
                  username: document.getElementById('username').value,
                  email: document.getElementById('email').value,
                  first_name: document.getElementById('firstName').value,
                  last_name: document.getElementById('lastName').value,
                  password: document.getElementById('password').value,
                  recaptcha_response: recaptchaResponse
              };

              try {
                  const response = await fetch('/api/register/user', {
                      method: 'POST',
                      headers: {
                          'Content-Type': 'application/json'
                      },
                      body: JSON.stringify(formData)
                  });

                  const result = await response.json();
                  if (result.success) {
                      alert('註冊成功！');
                  } else {
                      alert('註冊失敗：' + result.message);
                  }
              } catch (error) {
                  alert('網絡錯誤：' + error.message);
              }
          });
      </script>

  </body>
  </html>

JavaScript 工具函數

// 檢查用戶名可用性
async function checkUsername(username) {
const response = await fetch('/api/register/check-username', {
method: 'POST',
headers: { 'Content-Type': 'application/json' },
body: JSON.stringify({ username })
});
return await response.json();
}

// 檢查郵箱可用性
async function checkEmail(email) {
const response = await fetch('/api/register/check-email', {
method: 'POST',
headers: { 'Content-Type': 'application/json' },
body: JSON.stringify({ email })
});
return await response.json();
}

// 獲取 reCAPTCHA 配置
async function getRecaptchaConfig() {
const response = await fetch('/api/register/recaptcha-config');
return await response.json();
}

🔒 安全注意事項

1. reCAPTCHA 必須: 所有註冊請求都必須包含有效的 reCAPTCHA token
2. 輸入驗證: 用戶名只能包含字母、數字和下劃線，長度 3-20 個字符
3. 郵箱格式: 必須是有效的郵箱格式
4. 密碼強度: 至少 6 個字符
5. 重複檢查: 用戶名和郵箱不能重複

🐛 常見錯誤碼

| 錯誤碼 | HTTP 狀態             | 描述                   |
| ------ | --------------------- | ---------------------- |
| 400    | Bad Request           | 缺少必要字段或格式錯誤 |
| 409    | Conflict              | 用戶名或郵箱已存在     |
| 500    | Internal Server Error | 服務器內部錯誤         |

祝測試順利！🚀
