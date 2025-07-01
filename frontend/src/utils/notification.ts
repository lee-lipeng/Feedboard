import { createApp, h } from 'vue';
import MessageNotification from '@/components/common/MessageNotification.vue';

type NotificationType = 'success' | 'error' | 'warning' | 'info';

let notificationCount = 0;
const notificationInstances: Record<string, any> = {};

const createNotification = (
  message: string, 
  type: NotificationType = 'info', 
  duration: number = 3000
) => {
  // 创建一个唯一ID
  const id = `notification-${Date.now()}-${notificationCount++}`;
  
  // 创建容器
  const container = document.createElement('div');
  container.id = id;
  document.body.appendChild(container);
  
  // 创建通知组件实例
  const app = createApp({
    render() {
      return h(MessageNotification, {
        message,
        type,
        duration,
        visible: true,
        onClose: () => {
          // 通知关闭时移除实例
          app.unmount();
          document.body.removeChild(container);
          delete notificationInstances[id];
        }
      });
    }
  });
  
  // 挂载组件
  app.mount(container);
  
  // 存储实例，便于后续管理
  notificationInstances[id] = {
    app,
    container
  };
  
  // 返回ID，以便调用者可以手动关闭
  return id;
};

// 关闭指定通知
const closeNotification = (id: string) => {
  if (notificationInstances[id]) {
    const { app, container } = notificationInstances[id];
    app.unmount();
    document.body.removeChild(container);
    delete notificationInstances[id];
  }
};

// 关闭所有通知
const closeAllNotifications = () => {
  Object.keys(notificationInstances).forEach(closeNotification);
};

// 辅助方法，用于不同类型的通知
const notification = {
  success: (message: string, duration?: number) => createNotification(message, 'success', duration),
  error: (message: string, duration?: number) => createNotification(message, 'error', duration),
  warning: (message: string, duration?: number) => createNotification(message, 'warning', duration),
  info: (message: string, duration?: number) => createNotification(message, 'info', duration),
  close: closeNotification,
  closeAll: closeAllNotifications
};

export default notification; 