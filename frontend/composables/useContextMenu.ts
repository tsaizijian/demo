import { ref, reactive } from 'vue'

interface ContextMenuState {
  visible: boolean
  position: {
    top: string
    left: string
  }
  messageId: string | null
}

const contextMenuState = reactive<ContextMenuState>({
  visible: false,
  position: { top: '0px', left: '0px' },
  messageId: null
})

export const useContextMenu = () => {
  const showContextMenu = (event: MouseEvent, messageId: string) => {
    const { clientX, clientY } = event
    contextMenuState.position = {
      top: `${clientY}px`,
      left: `${clientX}px`
    }
    contextMenuState.messageId = messageId
    contextMenuState.visible = true
  }

  const hideContextMenu = () => {
    contextMenuState.visible = false
    contextMenuState.messageId = null
  }

  const isMenuVisible = (messageId: string) => {
    return contextMenuState.visible && contextMenuState.messageId === messageId
  }

  return {
    contextMenuState,
    showContextMenu,
    hideContextMenu,
    isMenuVisible
  }
}