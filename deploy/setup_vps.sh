#!/bin/bash
# ATTRAOS Hub — VPS Setup Script
# Chạy: bash setup_vps.sh
# OS: Ubuntu 22.04 LTS

set -e

echo "═══════════════════════════════════"
echo "  ATTRAOS Hub VPS Setup Script"
echo "═══════════════════════════════════"

# 1. Update & install deps
sudo apt update -y && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git

# 2. Clone hoặc copy code
# git clone https://github.com/phamhuuluong/SignalScout.git ~/SignalScout
# (hoặc scp từ local: scp -r SignalScout/ ubuntu@VPS_IP:~/SignalScout)

# 3. Setup Python venv
cd ~/SignalScout
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Copy env vars (edit trước khi chạy!)
cat > .env << 'EOF'
GEMINI_API_KEY=your_key_here
DEEPSEEK_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
PORT=8001
HOST=0.0.0.0
EOF
echo "⚠️  Nhớ edit .env với API keys thật!"

# 5. Systemd service
sudo cp deploy/attraos-hub.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable attraos-hub
sudo systemctl start attraos-hub
echo "✅ Service started"

# 6. Nginx config
sudo cp deploy/nginx.conf /etc/nginx/sites-available/attraos-hub
sudo ln -sf /etc/nginx/sites-available/attraos-hub /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
echo "✅ Nginx configured"

# 7. SSL (thay domain trước khi chạy dòng này)
# sudo certbot --nginx -d hub.attraos.io

echo ""
echo "✅ Done! Hub đang chạy tại http://VPS_IP:8001"
echo "🔐 Sau khi có domain: sudo certbot --nginx -d your.domain.com"
echo "📱 Update iOS app: Admin Panel → Hub Server URL → https://your.domain.com"
