#!/bin/bash
# Awakening Demo 一键部署脚本
# 在腾讯云Ubuntu轻量云上运行

set -e

echo "=== Awakening Demo 部署脚本 ==="

# 1. 安装系统依赖
echo "[1/4] 安装系统依赖..."
sudo apt update -qq
sudo apt install -y python3 python3-pip python3-venv nginx

# 2. 创建虚拟环境并安装Python依赖
echo "[2/4] 安装Python依赖..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

# 3. 配置Nginx
echo "[3/4] 配置Nginx..."
sudo tee /etc/nginx/sites-available/awakening > /dev/null <<'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /home/ubuntu/awakening-demo;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/awakening /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl restart nginx

# 4. 启动Flask（用gunicorn守护进程）
echo "[4/4] 启动Flask服务..."
mkdir -p logs
nohup venv/bin/gunicorn -w 2 -b 127.0.0.1:8080 app:app \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    > logs/stdout.log 2>&1 &

sleep 2
echo ""
echo "=== 部署完成 ==="
echo "服务运行在: http://服务器IP"
echo "查看日志: tail -f logs/error.log"
echo "停止服务: pkill gunicorn"
echo "重启服务: pkill gunicorn && nohup venv/bin/gunicorn -w 2 -b 127.0.0.1:8080 app:app > logs/stdout.log 2>&1 &"
