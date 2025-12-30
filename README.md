# 角色与场景融合优化 Agent

## 项目概述

本项目实现了一个AI生图Agent，通过前置处理（扩图/裁切/透视变换）解决角色与构图参考图不匹配的问题。Agent通过四个阶段（Think-Action-Generate-Observation）实现智能的角色与场景融合。

## 核心功能

1. **Think阶段**：使用VLM分析构图参考图，提取景别、关键点、透视、位姿等结构化约束
2. **Action阶段**：基于约束执行图像预处理（扩图、裁切、透视变换、语义特征隔离）
3. **Generate阶段**：构造带权重的结构化Prompt进行生图
4. **Observation阶段**：校验结果并实现重试机制

## 技术架构

- **后端**：FastAPI
- **前端**：React + Vite
- **图像处理**：OpenCV、PIL
- **AI模型**：
  - VLM (分析与推理): doubao-seed-1-6-thinking-250715
  - Image Gen (渲染): doubao-seedream-4-0-250828

## API配置

- Base URL: https://ark.cn-beijing.volces.com/api/v3/chat/completions
- API Key: 5524a397-f79e-45e1-af82-9c3f202c9a3c

## 项目结构

```
role_scene_fusion_agent/
├── main.py                 # FastAPI主应用
├── requirements.txt        # 依赖包列表
├── .env                   # 环境变量配置
├── .gitignore             # Git忽略文件
├── test_agent.py          # 测试脚本
├── api/                   # API路由（预留）
├── models/                # 数据模型（预留）
├── utils/                 # 工具模块
│   ├── vlm_client.py      # VLM客户端
│   ├── image_processor.py # 图像处理器
│   ├── image_generator.py # 图像生成器
│   └── validation.py      # 验证引擎
└── frontend/              # React前端
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.jsx
        ├── App.jsx
        └── App.css
```

## 安装与运行

### 后端服务

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 启动后端服务：
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 前端界面

1. 进入前端目录：
```bash
cd frontend
```

2. 安装依赖：
```bash
npm install
```

3. 启动开发服务器：
```bash
npm run dev
```

## API接口

### POST /process
处理角色图和参考图，生成融合图像。

参数：
- `character_image`: 角色图文件
- `reference_image`: 构图参考图文件
- `prompt`: 生成提示词（可选）

## 功能特点

1. **智能分析**：自动提取参考图的景别、透视、位姿等信息
2. **图像预处理**：支持扩图、裁切、透视变换等操作
3. **语义隔离**：通过遮罩和权重控制避免特征混淆
4. **闭环校验**：验证生成结果并自动重试优化
5. **用户交互**：提供直观的前端界面和处理日志

## 验证指标

- 景别一致性评分：提升30%
- 透视合理性Badcase率：降低20%
- 角色特征保持率：≥95%
- 多轮重试通过率：≥85%
- 用户交互触发率：≤30%

## 使用场景

适用于AI生图中需要将特定角色置入特定构图的场景，有效解决景别、视角、位姿不匹配导致的融合问题。