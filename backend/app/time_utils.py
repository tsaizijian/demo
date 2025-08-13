"""
全球時間處理工具函數
遵循 UTC 儲存、本地顯示的最佳實踐
"""

from datetime import datetime, timezone


def to_iso_utc(dt):
    """
    將 datetime 對象轉換為 ISO 8601 UTC 格式
    @param dt: datetime 對象
    @return: ISO 8601 字符串（如 2025-08-13T06:21:44.123Z）
    """
    if not dt:
        return None
    
    # 如果 datetime 是 naive（沒有時區信息），假設它是 UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    return dt.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')
