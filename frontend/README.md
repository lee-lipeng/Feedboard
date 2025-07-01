# Feedboard - 前端

这是 Feedboard 项目的前端部分，一个使用 Vue 3 和 Vite 构建的现代化应用。

## 技术栈

- **框架**: [Vue 3](https://vuejs.org/)
- **构建工具**: [Vite](https://vitejs.dev/)
- **语言**: [TypeScript](https://www.typescriptlang.org/)
- **路由**: [Vue Router](https://router.vuejs.org/)
- **状态管理**: [Pinia](https://pinia.vuejs.org/)
- **UI 框架**: [TailwindCSS](https://tailwindcss.com/)
- **HTTP客户端**: [axios](https://axios-http.com/)

## 项目设置 (本地开发)

### 安装依赖

```sh
npm install
```

### 编译和热重载 (开发模式)

```sh
npm run dev
```

此命令会启动一个本地开发服务器，通常在 `http://localhost:5173`。前端应用会通过 Vite 的代理设置连接到在 `http://localhost:8000` 运行的后端 API。请确保后端服务正在运行。

### 类型检查、编译和压缩 (生产构建)

```sh
npm run build
```

## 代码规范

- **格式化**: [Prettier](https://prettier.io/)
- **Linter**: [ESLint](https://eslint.org/)
