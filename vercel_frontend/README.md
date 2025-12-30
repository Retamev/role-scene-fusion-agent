# 角色与场景融合优化 Agent - Vercel前端部署

## 部署说明

此目录包含为Vercel部署优化的前端应用。由于角色与场景融合优化Agent包含复杂的图像处理和AI模型调用，需要将前端和后端分离部署：

1. 前端应用部署到Vercel
2. 后端API服务部署到支持长连接的云平台（如Render、Railway等）

## 部署步骤

### 1. 部署后端API服务

首先需要部署后端服务，推荐使用Render或Railway：

```bash
# 在主项目目录部署后端服务
cd /path/to/role_scene_fusion_agent
# 按照对应平台的部署指南部署FastAPI应用
```

### 2. 配置前端环境变量

在Vercel项目设置中添加环境变量：

- `REACT_APP_API_BASE_URL`: 后端API服务的完整URL（例如：https://your-app.onrender.com）

### 3. 部署前端到Vercel

可以通过以下方式部署：

#### 方法1: 使用Vercel CLI

```bash
# 安装Vercel CLI
npm i -g vercel

# 进入前端目录
cd /path/to/role_scene_fusion_agent/vercel_frontend

# 部署
vercel --prod
```

#### 方法2: 通过Vercel Dashboard

1. 访问 [Vercel Dashboard](https://vercel.com/dashboard)
2. 点击"New Project"
3. 连接您的GitHub/GitLab账户
4. 选择包含此前端代码的仓库
5. 在项目设置中配置环境变量
6. 点击"Deploy"

## 注意事项

1. **API超时**: 由于AI图像处理可能需要较长时间，前端设置了60秒超时。如果后端处理时间更长，可能需要调整超时时间或实现轮询机制。

2. **CORS配置**: 确保后端API正确配置了CORS，允许前端域名访问。

3. **资源限制**: Vercel的无服务器函数有执行时间限制，不适合直接部署需要长时间处理的AI模型。因此必须将后端部署到其他支持长时间运行的平台。

4. **成本考虑**: 频繁的AI图像处理会产生较高的计算成本，请在生产环境中考虑适当的限流措施。

## 项目结构

```
vercel_frontend/
├── package.json          # 依赖配置
├── vite.config.js        # 构建配置
├── vercel.json           # Vercel部署配置
├── index.html            # 主HTML文件
├── public/               # 静态资源
└── src/                  # 源代码
    ├── main.jsx          # 应用入口
    ├── App.jsx           # 主应用组件
    └── App.css           # 样式文件
```

## 开发

本地开发：

```bash
cd vercel_frontend
npm install
npm run dev
```

构建生产版本：

```bash
npm run build
```