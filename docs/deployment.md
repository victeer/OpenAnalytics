# 部署指南

## 前置条件
- 服务器操作系统：Ubuntu 20.04 LTS 或更高版本
- 已安装 Python 3.8 或更高版本
- 已安装 Node.js 14 或更高版本
- 已安装 NGINX

## 1. 安装依赖

### 后端依赖
```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 前端依赖
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 构建前端
npm run build
```

## 2. 环境变量配置

### 开发环境
1. 创建 `.env.development` 文件：
```bash
# API配置
REACT_APP_API_HOST=localhost
REACT_APP_API_PORT=8000
REACT_APP_API_BASE_PATH=/api

# 基础路径配置
REACT_APP_BASE_PATH=/

# 其他配置
REACT_APP_MAX_FILE_SIZE=104857600
REACT_APP_SESSION_TIMEOUT=1800000
```

### 生产环境
1. 创建 `.env.production` 文件：
```bash
# API配置
REACT_APP_API_HOST=your_domain.com
REACT_APP_API_PORT=80
REACT_APP_API_BASE_PATH=/op

# 基础路径配置
REACT_APP_BASE_PATH=/analysis

# 其他配置
REACT_APP_MAX_FILE_SIZE=104857600
REACT_APP_SESSION_TIMEOUT=1800000
```

2. 确保环境变量正确加载：
```bash
# 开发环境
npm start

# 生产环境
npm run build
```

3. 检查环境变量：
- 打开浏览器开发者工具
- 查看控制台输出
- 确认没有环境变量缺失警告

## 3. 配置 NGINX

1. 安装 NGINX：
```bash
sudo apt update
sudo apt install nginx
```

2. 配置 NGINX：
```bash
# 备份默认配置
sudo mv /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak

# 复制我们的配置
sudo cp nginx.conf /etc/nginx/nginx.conf

# 修改配置文件中的路径
sudo nano /etc/nginx/nginx.conf
```

3. 在配置文件中修改以下内容：
- `server_name`: 替换为您的域名
- `alias`: 替换为前端构建文件的路径
- `alias`: 替换为后端上传文件的路径

4. 测试配置：
```bash
sudo nginx -t
```

5. 重启 NGINX：
```bash
sudo systemctl restart nginx
## or 
nginx -s reload
```

## 4. 启动后端服务

1. 使用 systemd 创建服务：
```bash
sudo nano /etc/systemd/system/data-analysis.service
```

2. 添加以下内容：
```ini
[Unit]
Description=Data Analysis Backend Service
After=network.target

[Service]
User=your_username
Group=your_group
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/backend/venv/bin"
ExecStart=/path/to/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

3. 启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl start data-analysis
sudo systemctl enable data-analysis
```

## 5. 文件权限设置

```bash
# 设置上传目录权限
sudo mkdir -p /path/to/backend/uploads
sudo chown -R www-data:www-data /path/to/backend/uploads
sudo chmod -R 755 /path/to/backend/uploads
```

## 6. 防火墙配置

```bash
# 只允许 HTTP
sudo ufw allow 80/tcp

# 启用防火墙
sudo ufw enable
```

## 7. 监控和维护

1. 查看服务状态：
```bash
# 查看后端服务状态
sudo systemctl status data-analysis

# 查看 NGINX 状态
sudo systemctl status nginx
```

2. 查看日志：
```bash
# 后端日志
sudo journalctl -u data-analysis

# NGINX 日志
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

## 8. 访问方式

- 开发环境：
  - 前端：`http://localhost:3000`
  - 后端：`http://localhost:8000/api`

- 生产环境：
  - 前端：`http://your_domain.com/analysis`
  - 后端：`http://your_domain.com/op`

## 故障排除

1. 如果环境变量未加载：
- 检查环境变量文件名是否正确
- 确保环境变量以 `REACT_APP_` 开头
- 检查构建命令是否正确
- 查看浏览器控制台的环境变量检查输出

2. 如果遇到 502 Bad Gateway：
- 检查后端服务是否运行
- 检查 NGINX 错误日志
- 检查防火墙设置
- 检查后端服务是否绑定到 127.0.0.1

3. 如果遇到文件上传问题：
- 检查上传目录权限
- 检查 NGINX 的 `client_max_body_size` 设置
- 检查后端服务的文件处理逻辑

4. 如果遇到跨域问题：
- 确保后端服务允许来自前端的跨域请求
- 检查后端服务的 CORS 配置
- 检查 NGINX 的代理配置 