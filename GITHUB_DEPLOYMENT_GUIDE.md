# GitHub 部署指南

## 1. 创建 GitHub 仓库

1. 登录 GitHub 账户
2. 点击 "New repository" 按钮
3. 输入仓库名称（例如：`role-scene-fusion-agent`）
4. 选择 "Public" 或 "Private"（根据需要）
5. **不要** 勾选 "Initialize this repository with a README"
6. **不要** 添加 .gitignore 或 license（我们已有这些文件）
7. 点击 "Create repository"

## 2. 配置 Git 凭据

### 方法一：使用 Personal Access Token（推荐）

1. 访问 GitHub，进入 Settings → Developer settings → Personal access tokens → Tokens (classic)
2. 点击 "Generate new token"
3. 选择适当的权限（至少需要 repo 权限）
4. 复制生成的 token

5. 在终端中配置：
```bash
git remote set-url origin https://<your-username>:<your-token>@github.com/<your-username>/role-scene-fusion-agent.git
```

### 方法二：使用 SSH（推荐用于长期使用）

1. 生成 SSH 密钥：
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

2. 将 SSH 公钥添加到 GitHub：
```bash
cat ~/.ssh/id_ed25519.pub
```
复制输出内容，然后在 GitHub 的 Settings → SSH and GPG keys 中添加

3. 更改远程 URL：
```bash
git remote set-url origin git@github.com:<your-username>/role-scene-fusion-agent.git
```

## 3. 推送代码

配置好凭据后，运行以下命令：

```bash
# 确保在项目根目录
cd /Users/reta/Public/codebase/role_scene_fusion_agent

# 设置主分支名称
git branch -M main

# 推送代码
git push -u origin main
```

## 4. 验证部署

推送完成后，访问 `https://github.com/<your-username>/role-scene-fusion-agent` 验证代码是否成功上传。

## 5. 项目特色

### 主要功能
- AI 驱动的角色与场景融合优化
- 智能图像预处理（扩图、裁切、透视变换）
- 结构化约束提取与应用
- 闭环验证与重试机制

### 技术栈
- **后端**: FastAPI
- **前端**: React + Vite
- **图像处理**: OpenCV, PIL
- **AI模型**: doubao-seed 系列模型

### 项目结构
```
role_scene_fusion_agent/
├── main.py                    # FastAPI主应用
├── requirements.txt           # 依赖包列表
├── .env                      # 环境变量配置
├── .gitignore                # Git忽略文件
├── test_agent.py             # 测试脚本
├── api/                      # API路由（预留）
├── models/                   # 数据模型（预留）
├── utils/                    # 工具模块
│   ├── vlm_client.py         # VLM客户端
│   ├── image_processor.py    # 图像处理器
│   ├── image_generator.py    # 图像生成器
│   └── validation.py         # 验证引擎
├── frontend/                 # React前端
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       └── App.css
└── vercel_frontend/          # 适配Vercel部署的前端
    ├── package.json
    ├── vercel.json
    ├── index.html
    └── src/
        ├── main.jsx
        ├── App.jsx
        └── App.css
```

## 6. 后续步骤

1. **添加 Issues 模板**：创建 `.github/ISSUE_TEMPLATE/` 目录
2. **配置 Actions**：创建 `.github/workflows/` 目录以添加 CI/CD
3. **设置 Pages**：如果需要托管前端应用
4. **添加贡献指南**：创建 `CONTRIBUTING.md`
5. **添加代码行为准则**：创建 `CODE_OF_CONDUCT.md`

## 7. 部署到生产环境

项目包含两个部署选项：

### 选项一：分离部署（推荐）
- 前端部署到 Vercel
- 后端部署到 Render/Railway

### 选项二：本地部署
- 克隆仓库到服务器
- 按照 README 中的说明运行

## 8. 问题排查

如果推送失败，请检查：
1. 网络连接是否正常
2. GitHub 凭据是否正确配置
3. 仓库名称是否拼写正确
4. 是否有权限访问目标仓库

如需帮助，请参考：
- [GitHub 官方文档](https://docs.github.com/)
- [Git 指南](https://git-scm.com/doc)