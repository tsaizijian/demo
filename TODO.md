# 聊天室系統 v2 - 開發 TODO 清單

## 🎯 PrimeVue UI 框架遷移

### 已完成 ✅

- [x] 檢查當前 PrimeVue 配置狀態
- [x] 搜尋專案中剩餘的 Nuxt UI 組件
- [x] 轉換 login.vue 中的 Nuxt UI 組件
- [x] 檢查 assets 檔案影響並解決 Card 組件顯示問題
- [x] 轉換 logout.vue 中的 Nuxt UI 組件為 PrimeVue
- [x] 轉換 register.vue 中的 Nuxt UI 組件為 PrimeVue
- [x] 修復 toast 服務和 hydration 問題
- [x] 修復註冊 API 自動創建 UserProfile
- [x] 創建 ab_user 表的管理介面視圖
- [x] 逐步將其他檔案中的 Nuxt UI 組件轉換為 PrimeVue
- [x] 檢查 CreateChannelSidebar.vue
- [x] 檢查 ChannelSidebar.vue
- [x] 檢查 ChannelSettingsModal.vue
- [x] 檢查其他可能的組件檔案

### 待辦事項 📋

#### 前端功能完善

- [ ] 測試轉換後的功能
  - [ ] 註冊功能完整測試
  - [ ] 登入功能完整測試
  - [ ] 登出功能完整測試
  - [ ] Toast 通知功能測試
- [ ] 優化 UI/UX 設計
  - [ ] 統一組件樣式
  - [ ] 響應式設計調整
  - [ ] 暗色主題支援檢查
- [ ] 移除舊的 Nuxt UI 依賴項

#### 聊天室核心功能

- [ ] 修復訊息換行問題 (message can't newline)
- [ ] WebSocket 連接測試
- [ ] 即時訊息傳送功能
- [ ] 用戶線上狀態管理
- [ ] 聊天記錄儲存與讀取
- [ ] 檔案上傳功能

#### 後端功能完善

- [ ] 確認 UserProfile 自動創建邏輯
- [ ] 測試註冊後的資料完整性
- [ ] 優化 API 錯誤處理
- [ ] 添加 API 文檔

#### 系統管理功能

- [ ] 管理員介面完善
  - [x] 註冊用戶查看介面
  - [ ] 聊天訊息管理介面
  - [ ] 用戶權限管理
- [ ] 系統監控與日誌
- [ ] 效能優化

#### 版本更新與部署

- [ ] 更新版本號 (update version)
- [ ] 輸入驗證強化
- [ ] CSRF 保護
- [ ] Rate Limiting
- [ ] Docker 容器化
- [ ] 生產環境配置

---

## 📝 近期重點任務

1. **完成 PrimeVue 遷移** - 確保所有 UI 組件都已轉換
2. **修復訊息換行問題** - 解決聊天室訊息顯示問題
3. **功能測試** - 驗證所有轉換後的功能正常運作
4. **聊天室核心功能** - 實現基本的即時通訊功能

---

## 🐛 已知問題

- [x] ~~Hydration mismatch 警告~~ (已修復)
- [x] ~~Toast 服務未正確初始化~~ (已修復)
- [x] ~~註冊後 UserProfile 未自動創建~~ (已修復)
- [ ] 訊息換行問題 (傳送字體時有換行符不會自動換行且字體多時也不會換行會跑出 div 外)
- [ ] 所有使用者都能登入 flask 後端查看別人資料

---

## 💡 改進建議

- [ ] 考慮添加 TypeScript 嚴格模式
- [ ] 實施自動化測試
- [ ] 添加國際化支援
- [ ] 優化打包大小
