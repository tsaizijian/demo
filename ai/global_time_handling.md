# 全球可用時間處理方案（UTC 儲存，本地顯示）

## 原則

1.  **資料庫一律存 UTC、帶時區（timezone-aware）**
2.  **API 回傳標準格式**：ISO 8601（`2025-08-13T06:21:44.123Z`）或
    epoch(ms)
3.  **顯示時才轉時區**：依使用者/瀏覽器時區格式化
4.  **人看用在地格式**；機器算用 UTC/epoch
5.  **排程、過期比較用 UTC**；不要拿本地時間做邏輯

------------------------------------------------------------------------

## 後端（Python/Flask/FAB 範例）

**模型欄位**

``` python
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime

created_on = Column(DateTime(timezone=True),
                    default=lambda: datetime.now(timezone.utc),
                    nullable=False)
updated_on = Column(DateTime(timezone=True),
                    default=lambda: datetime.now(timezone.utc),
                    onupdate=lambda: datetime.now(timezone.utc),
                    nullable=False)
```

**序列化（統一輸出 ISO UTC + 可選 epoch）**

``` python
def to_iso_utc(dt):
    return dt.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z') if dt else None

def to_epoch_ms(dt):
    return int(dt.astimezone(timezone.utc).timestamp() * 1000) if dt else None

return {
  "created_on": to_iso_utc(row.created_on),
  "created_on_ms": to_epoch_ms(row.created_on)
}
```

------------------------------------------------------------------------

## 前端（Nuxt/Vue 範例）

**依瀏覽器/使用者時區顯示**

``` ts
export function formatInTZ(isoUtc: string, tz?: string, opts?: Intl.DateTimeFormatOptions) {
  const timeZone = tz || Intl.DateTimeFormat().resolvedOptions().timeZone;
  return new Intl.DateTimeFormat('zh-TW', {
    timeZone, year:'numeric', month:'2-digit', day:'2-digit',
    hour:'2-digit', minute:'2-digit', hour12:false, ...opts
  }).format(new Date(isoUtc));
}
```

**相對時間**

``` ts
export function fromNow(isoUtc: string) {
  const rtf = new Intl.RelativeTimeFormat('zh-TW', { numeric: 'auto' });
  const sec = (new Date(isoUtc).getTime() - Date.now())/1000;
  const abs = Math.abs(sec);
  if (abs < 60) return rtf.format(Math.round(sec), 'second');
  if (abs < 3600) return rtf.format(Math.round(sec/60), 'minute');
  if (abs < 86400) return rtf.format(Math.round(sec/3600), 'hour');
  return rtf.format(Math.round(sec/86400), 'day');
}
```

------------------------------------------------------------------------

## 設定與資料欄位

-   使用者偏好：儲存 `time_zone`（如 `Asia/Taipei`）與 `locale`（如
    `zh-TW`）
-   介面預設：用 `Intl.DateTimeFormat().resolvedOptions().timeZone`
-   後端 API：可支援 `?tz=Asia/Taipei` 或 `Time-Zone` header（選配）

------------------------------------------------------------------------

## 排程 / 到期 / 比較

-   全用 UTC 做比較（例如過期、排序、重試）\
-   Cron/排程器設定成 UTC；顯示給人看再轉時區

------------------------------------------------------------------------

## 日誌與除錯

-   伺服器 log 統一 UTC（含 `Z`）；前端 console 可本地時區\
-   事件追蹤用 epoch(ms) 方便對齊

------------------------------------------------------------------------

## 常見地雷

-   ❌ 在 DB 存本地時間 → DST/換時區就悲劇\
-   ❌ 沒有 tzinfo 的 naive datetime\
-   ❌ 用字串比較時間\
-   ❌ 後端回混雜格式（有的 ISO、有的毫秒）

------------------------------------------------------------------------

## 快速檢查清單

-   [ ] DB 欄位 `DateTime(timezone=True)`、值為 UTC\
-   [ ] API 回傳 ISO 8601（`...Z`）± epoch_ms\
-   [ ] 前端用 `Intl` 依使用者時區格式化\
-   [ ] 排程/比較全用 UTC\
-   [ ] 使用者可設定 `time_zone`/`locale`
