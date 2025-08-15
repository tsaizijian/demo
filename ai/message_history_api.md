# 聊天歷史訊息 API（游標式分頁）

## 簡介
此 API 提供指定聊天室的歷史訊息查詢，支援 **游標式分頁**（Cursor-based Pagination），適合聊天訊息的「上拉載入更多」場景。  
相較於傳統的 page-based 分頁，游標式更穩定且效能更佳。

---

## 目前問題點（原實作）
1. **過濾與排序欄位不一致**  
   - 使用 `before_id` 過濾資料，但排序是 `created_on.desc()`  
   - 若 `id` 與 `created_on` 不完全同步遞增，可能出現漏資料或重複資料  
   - ✅ 建議：過濾與排序欄位一致，例如都用 `id`。

2. **COUNT 成本高**  
   - `.paginate()` 會執行 `COUNT(*)`，當訊息量大時效能差  
   - ✅ 建議：用 `per_page+1` 判斷是否有下一頁，避免全表 COUNT。

3. **回傳方向複雜**  
   - 原本先 `desc` 排序再反轉，雖然可行，但可直接用 `id DESC` 抓最新在前，再反轉顯示舊到新。

4. **適合游標式分頁**  
   - 聊天紀錄用 page 參數不直覺，游標（`before_id`）更自然。

5. **資料庫索引**  
   - 若沒有 `(channel_id, id)` 複合索引，過濾效能差。

---

## 改良後 API 實作範例（游標式）

```python
def message_history(self):
    """
    取得歷史訊息（游標式，上拉載入）
    GET /api/v1/chatmessageapi/history?channel_id=1&per_page=20&before_id=1001
    - 不帶 before_id：抓最新一頁
    - 帶 before_id：抓該 id 之前的舊訊息
    """
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    before_id = request.args.get('before_id', type=int)
    channel_id = request.args.get('channel_id', 1, type=int)

    q = (
        self.datamodel.session.query(ChatMessage)
        .filter(ChatMessage.is_deleted.is_(False))
        .filter(ChatMessage.channel_id == channel_id)
    )

    if before_id:
        q = q.filter(ChatMessage.id < before_id)

    rows = (
        q.order_by(ChatMessage.id.desc())
         .limit(per_page + 1)
         .all()
    )

    has_next = len(rows) > per_page
    if has_next:
        rows = rows[:per_page]

    rows = list(reversed(rows))
    next_before_id = rows[0].id if has_next and rows else None

    return jsonify({
        "result": [r.to_dict() for r in rows],
        "pagination": {
            "per_page": per_page,
            "has_next": has_next,
            "next_before_id": next_before_id
        }
    })
```

---

## 回應格式
```json
{
  "result": [
    {
      "id": 98,
      "channel_id": 1,
      "sender_id": 2,
      "content": "Hello!",
      "created_on": "2025-08-15T10:15:00Z"
    }
  ],
  "pagination": {
    "per_page": 20,
    "has_next": true,
    "next_before_id": 78
  }
}
```

### 欄位說明
| 欄位                | 描述 |
|---------------------|------|
| `result`            | 本次查詢的訊息列表（由舊到新排序） |
| `pagination.per_page` | 每頁筆數 |
| `pagination.has_next` | 是否有更舊的訊息 |
| `pagination.next_before_id` | 下一次請求應帶的 `before_id` 值 |

---

## 前端整合建議
1. 初次載入：不帶 `before_id` → 顯示最新訊息。
2. 使用者上拉到頂時：帶 `before_id = currentMessages[0].id` 再請求。
3. 回傳資料用 **prepend** 加到現有訊息前。
4. 若 `has_next == false` → 停止顯示「載入更多」提示。

---

## 資料庫索引建議
```python
Index('ix_chatmessage_channel_id_id', ChatMessage.channel_id, ChatMessage.id)
```

確保 `(channel_id, id)` 複合索引存在，可以顯著提升查詢效能。
