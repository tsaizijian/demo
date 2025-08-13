/**
 * 全球時間處理工具函數
 * 遵循 UTC 儲存、本地顯示的最佳實踐
 */

/**
 * 使用 Intl API 依瀏覽器/使用者時區格式化時間
 * @param isoUtc - ISO 8601 UTC 時間字符串（如 2025-08-13T06:21:44.123Z）
 * @param tz - 可選時區，預設使用瀏覽器時區
 * @param opts - 格式選項
 */
export function formatInTZ(isoUtc: string, tz?: string, opts?: Intl.DateTimeFormatOptions) {
  if (!isoUtc) return ''
  
  const timeZone = tz || Intl.DateTimeFormat().resolvedOptions().timeZone
  return new Intl.DateTimeFormat('zh-TW', {
    timeZone,
    year: 'numeric',
    month: '2-digit', 
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
    ...opts
  }).format(new Date(isoUtc))
}


/**
 * 格式化本地時間（智能顯示模式）
 * @param isoUtc - ISO 8601 UTC 時間字符串
 */
export const formatLocalTime = (isoUtc: string): string => {
  if (!isoUtc) return ''
  
  // 確保正確處理不同格式的時間戳
  let dateToUse = isoUtc
  if (typeof isoUtc === 'string') {
    // 如果沒有 Z 或時區標記，且包含 T，假設是 UTC
    if (isoUtc.includes('T') && !isoUtc.includes('Z') && !isoUtc.includes('+') && !isoUtc.includes('-')) {
      dateToUse = isoUtc + 'Z'
    }
  }
  
  const date = new Date(dateToUse)
  
  // 檢查日期是否有效
  if (isNaN(date.getTime())) {
    console.warn('Invalid date:', isoUtc)
    return ''
  }
  
  const now = new Date()
  const diffInMs = now.getTime() - date.getTime()
  
  // 小於一分鐘
  if (diffInMs < 60000) {
    return '剛剛'
  }
  
  // 小於一小時
  if (diffInMs < 3600000) {
    const minutes = Math.floor(diffInMs / 60000)
    return `${minutes} 分鐘前`
  }
  
  // 小於 24 小時
  if (diffInMs < 86400000) {
    const hours = Math.floor(diffInMs / 3600000)
    return `${hours} 小時前`
  }
  
  // 今天
  if (isToday(date)) {
    return formatInTZ(dateToUse, undefined, {
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  
  // 昨天
  if (isYesterday(date)) {
    const time = formatInTZ(dateToUse, undefined, {
      hour: '2-digit',
      minute: '2-digit'
    })
    return `昨天 ${time}`
  }
  
  // 本週內
  if (diffInMs < 604800000) { // 7 天
    return formatInTZ(dateToUse, undefined, {
      weekday: 'short',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  
  // 同一年
  if (date.getFullYear() === now.getFullYear()) {
    return formatInTZ(dateToUse, undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  
  // 不同年份
  return formatInTZ(dateToUse, undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * 獲取詳細的時間信息（用於 tooltip）
 * @param isoUtc - ISO 8601 UTC 時間字符串
 * @returns 詳細的時間字符串，包含時區信息
 */
export const getDetailedTime = (isoUtc: string): string => {
  if (!isoUtc) return ''
  
  // 確保正確處理不同格式的時間戳
  let dateToUse = isoUtc
  if (typeof isoUtc === 'string') {
    // 如果沒有 Z 或時區標記，且包含 T，假設是 UTC
    if (isoUtc.includes('T') && !isoUtc.includes('Z') && !isoUtc.includes('+') && !isoUtc.includes('-')) {
      dateToUse = isoUtc + 'Z'
    }
  }
  
  return formatInTZ(dateToUse, undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric', 
    weekday: 'long',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    timeZoneName: 'short'
  })
}

/**
 * 檢查是否為今天
 */
const isToday = (date: Date): boolean => {
  const today = new Date()
  return (
    date.getDate() === today.getDate() &&
    date.getMonth() === today.getMonth() &&
    date.getFullYear() === today.getFullYear()
  )
}

/**
 * 檢查是否為昨天
 */
const isYesterday = (date: Date): boolean => {
  const yesterday = new Date()
  yesterday.setDate(yesterday.getDate() - 1)
  return (
    date.getDate() === yesterday.getDate() &&
    date.getMonth() === yesterday.getMonth() &&
    date.getFullYear() === yesterday.getFullYear()
  )
}
