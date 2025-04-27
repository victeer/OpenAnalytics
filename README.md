# 数据分析机器人

一个基于人工智能的数据分析工具，帮助用户快速进行数据分析和可视化。

## 主要功能

### 数据分析
- 数据上传和预览
- 智能分析计划生成
- 自动代码执行
- 结果展示和下载

### 用户界面
- 专家/小白模式切换
- 分析结果表格展示
- 数据下载功能
- 错误提示和修复

### 技术特点
- 基于React的前端界面
- FastAPI后端服务
- Pandas数据处理
- 智能错误处理

## 使用说明

### 安装
1. 克隆项目
```bash
git clone [项目地址]
```

2. 安装依赖
```bash
# 前端
cd frontend
npm install

# 后端
cd backend
pip install -r requirements.txt
```

3. 配置环境变量
```bash
# 前端
cp frontend/.env.example frontend/.env

# 后端
cp backend/.env.example backend/.env
```

### 运行
1. 启动后端服务
```bash
cd backend
uvicorn app.main:app --reload
```

2. 启动前端服务
```bash
cd frontend
npm start
```

## 开发指南

详细开发指南请参考 [开发指南.md](docs/开发指南.md)

## 项目路线图

详细路线图请参考 [开发路线图.md](docs/开发路线图.md)

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License 