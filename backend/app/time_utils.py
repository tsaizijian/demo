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


def to_epoch_ms(dt):
    """
    將 datetime 對象轉換為 epoch 毫秒
    @param dt: datetime 對象  
    @return: epoch 毫秒整數
    """
    if not dt:
        return None
    
    # 如果 datetime 是 naive（沒有時區信息），假設它是 UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    return int(dt.astimezone(timezone.utc).timestamp() * 1000)


def serialize_datetime_fields(obj, fields=['created_on', 'changed_on']):
    """
    序列化對象的 datetime 欄位為標準格式
    @param obj: 包含 datetime 欄位的對象
    @param fields: 要序列化的欄位列表
    @return: 包含序列化時間的字典
    """
    result = {}
    
    for field in fields:
        if hasattr(obj, field):
            dt_value = getattr(obj, field)
            result[field] = to_iso_utc(dt_value)
            result[f"{field}_ms"] = to_epoch_ms(dt_value)
    
    return result