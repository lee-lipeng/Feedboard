import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUnreadStore = defineStore('unread', () => {
  // 使用一个Map来存储每个feed的未读文章数 { feed_id: count }
  const unreadCounts = ref(new Map<number, number>())

  // 获取指定feed的未读数
  const getUnreadCount = computed(() => {
    return (feedId: number) => unreadCounts.value.get(feedId) || 0
  })

  // 增加未读文章数
  function incrementUnreadCount(feedId: number, count: number) {
    const currentCount = unreadCounts.value.get(feedId) || 0
    unreadCounts.value.set(feedId, currentCount + count)
  }

  // 重置指定feed的未读数
  function resetUnreadCount(feedId: number) {
    if (unreadCounts.value.has(feedId)) {
      unreadCounts.value.set(feedId, 0)
    }
  }

  return {
    unreadCounts,
    getUnreadCount,
    incrementUnreadCount,
    resetUnreadCount
  }
}) 