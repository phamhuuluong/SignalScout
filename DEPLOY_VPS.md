# ATTRAOS Hub — Hướng Dẫn Deploy VPS (Ubuntu Linux)

> File này dành cho AI Antigravity hoặc sysadmin deploy ATTRAOS Hub Server lên VPS Linux.
> **Server**: FastAPI Python — phục vụ iOS app + MT5 EA
> **Domain**: `hub.lomofx.com` qua Cloudflare Tunnel

---

## 1. Yêu Cầu VPS

- **OS**: Ubuntu 22.04+ LTS
- **RAM**: tối thiểu 1GB (khuyến nghị 2GB)
- **Disk**: 10GB+
- **Python**: 3.10+
- **Ports**: KHÔNG cần mở port — dùng Cloudflare Tunnel

---

## 2. Upload Code Lên VPS

### Cách 1: SCP từ Mac
```bash
scp -r /Users/hx/Documents/SignalScout/ ubuntu@VPS_IP:~/SignalScout/
```

### Cách 2: Git clone (nếu đã push)
```bash
git clone https://github.com/phamhuuluong/SignalScout.git ~/SignalScout
```

---

## 3. Cài Đặt Dependencies

```bash
# Update system
sudo apt update -y && sudo apt upgrade -y

# Cài Python + tools
sudo apt install -y python3 python3-pip python3-venv curl wget

# Tạo virtual environment
cd ~/SignalScout
python3 -m venv venv
source venv/bin/activate

# Cài Python packages
pip install -r requirements.txt
```

---

## 4. Cấu Hình Environment

```bash
# Copy file mẫu và sửa
cp .env.example .env
nano .env
```

**Nội dung `.env` cần sửa:**
```env
GEMINI_API_KEY=AIzaSy...         # API key Gemini thật
DEEPSEEK_API_KEY=sk-...          # API key DeepSeek thật
OPENAI_API_KEY=sk-...            # API key OpenAI (tùy chọn)
PORT=8001
HOST=0.0.0.0
```

---

## 5. Chạy Thử (Test)

```bash
cd ~/SignalScout
source venv/bin/activate
python3 server.py
```

Mở browser: `http://VPS_IP:8001` — phải thấy JSON response `{"name":"ATTRAOS Hub","status":"running",...}`

**Kiểm tra admin panel:** `http://VPS_IP:8001/admin?token=attraos_admin_2026`

> ⚠️ Nhấn `Ctrl+C` để dừng sau khi test xong.

---

## 6. Systemd Service (Chạy Nền Vĩnh Viễn)

```bash
# Copy service file
sudo cp ~/SignalScout/deploy/attraos-hub.service /etc/systemd/system/

# ⚠️ SỬA FILE SERVICE — đổi User và WorkingDirectory cho đúng
sudo nano /etc/systemd/system/attraos-hub.service
```

**Kiểm tra và sửa các dòng này:**
```ini
User=ubuntu                                    # ← user VPS của anh (có thể là root, ubuntu, etc.)
WorkingDirectory=/home/ubuntu/SignalScout       # ← đường dẫn thực tế
ExecStart=/home/ubuntu/venv/bin/python3 server.py   # ← nếu venv nằm trong SignalScout thì: /home/ubuntu/SignalScout/venv/bin/python3 server.py
```

```bash
# Reload + enable + start
sudo systemctl daemon-reload
sudo systemctl enable attraos-hub
sudo systemctl start attraos-hub

# Kiểm tra status
sudo systemctl status attraos-hub

# Xem log real-time
sudo journalctl -u attraos-hub -f
```

---

## 7. Cloudflare Tunnel (Domain hub.lomofx.com)

### 7.1 Cài cloudflared
```bash
# Ubuntu/Debian
curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | sudo tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null
echo 'deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared focal main' | sudo tee /etc/apt/sources.list.d/cloudflared.list
sudo apt update
sudo apt install -y cloudflared
```

### 7.2 Setup credentials
```bash
# Copy cert file
mkdir -p ~/.cloudflared
cp ~/SignalScout/deploy/22332de5-791d-4e37-bb05-bd3c1317e464.json ~/.cloudflared/

# Copy tunnel config
cp ~/SignalScout/deploy/tunnel_config.yml ~/.cloudflared/config.yml
```

### 7.3 Thêm DNS record trong Cloudflare Dashboard
1. Đăng nhập https://dash.cloudflare.com
2. Vào domain `lomofx.com` → DNS → Add Record
3. Thêm CNAME:
   - **Type**: CNAME
   - **Name**: `hub`
   - **Target**: `22332de5-791d-4e37-bb05-bd3c1317e464.cfargotunnel.com`
   - **Proxy**: ON (orange cloud)

### 7.4 Chạy tunnel
```bash
# Test trước
cloudflared tunnel --config ~/.cloudflared/config.yml run

# Nếu OK, cài làm system service
sudo cloudflared service install
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
```

### 7.5 Verify
```bash
curl https://hub.lomofx.com/
# Phải trả về: {"name":"ATTRAOS Hub","status":"running",...}

curl https://hub.lomofx.com/admin?token=attraos_admin_2026
# Phải trả về HTML admin panel
```

---

## 8. Seed Database (Lần Đầu)

```bash
cd ~/SignalScout
source venv/bin/activate

# DB tự tạo khi chạy server.py lần đầu
# Seed Academy lessons:
python3 hub_seed_lessons.py

# Verify:
python3 -c "
from hub_database import SessionLocal, AIPrompt
with SessionLocal() as db:
    prompts = db.query(AIPrompt).all()
    for p in prompts:
        print(f'{p.name}: {len(p.content)} chars')
"
```

---

## 9. Cấu Trúc File Quan Trọng

```
SignalScout/
├── server.py              # FastAPI main — ENTRY POINT
├── hub_database.py        # SQLAlchemy models + DB init
├── hub_admin.py           # Admin panel routes (/admin/*)
├── hub_ai.py              # AI analysis (Gemini/DeepSeek)
├── hub_config.py          # Remote config endpoint
├── hub_scheduler.py       # Auto-run AI council (5-10 min)
├── push_service.py        # Push notification service
├── academy.py             # Academy API
├── market_data.py         # Market data helpers
├── indicators.py          # Technical indicators
├── signal_engine.py       # Signal generation engine
├── smc_detector.py        # SMC pattern detection
├── liquidity_heatmap.py   # Liquidity heatmap
├── requirements.txt       # Python dependencies
├── .env                   # ⚠️ API keys (KHÔNG commit)
├── hub_data.db            # SQLite DB (auto-created)
├── deploy/
│   ├── tunnel_config.yml  # Cloudflare tunnel config
│   ├── attraos-hub.service # Systemd service
│   ├── nginx.conf         # Nginx config (nếu dùng Nginx thay Cloudflare)
│   ├── setup_vps.sh       # Auto-setup script
│   └── 22332de5-...json   # Cloudflare tunnel credentials
└── MT5_ATTRAOS_Hub.mq5    # MT5 EA (chạy trên máy MT5, KHÔNG chạy trên VPS)
```

---

## 10. Admin Panel Endpoints

| URL | Chức năng |
|-----|-----------|
| `/admin?token=attraos_admin_2026` | Tổng quan |
| `/admin/prompts?token=attraos_admin_2026` | Quản lý AI prompts |
| `/admin/signals?token=attraos_admin_2026` | Xem signal history |
| `/admin/users?token=attraos_admin_2026` | Quản lý users/premium |
| `/admin/news?token=attraos_admin_2026` | Quản lý hot news |
| `/admin/academy?token=attraos_admin_2026` | Quản lý bài học |

---

## 11. Troubleshooting

### Server không khởi động
```bash
# Xem log
sudo journalctl -u attraos-hub -n 50

# Check port
sudo lsof -i :8001

# Restart
sudo systemctl restart attraos-hub
```

### Cloudflare tunnel không kết nối
```bash
# Check credential file
ls -la ~/.cloudflared/22332de5*.json

# Check config
cat ~/.cloudflared/config.yml

# Test manual
cloudflared tunnel --config ~/.cloudflared/config.yml run
```

### DB lỗi / cần reset
```bash
cd ~/SignalScout
rm hub_data.db
python3 -c "from hub_database import init_db; init_db()"
python3 hub_seed_lessons.py
```

---

## 12. Cập Nhật Code

```bash
cd ~/SignalScout
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart attraos-hub
```

---

## 13. iOS App Đồng Bộ

Sau khi deploy, iOS app tự kết nối `hub.lomofx.com` (đã hardcode default).

Nếu cần đổi URL trên app:
1. Mở app → More → tap logo "AF" 5 lần → Admin Panel
2. Scroll xuống **Hub Admin Panel** → sửa URL
3. Hoặc: Settings → Signal Server → sửa URL

---

> **⚠️ BẢO MẬT**: Sau khi deploy xong, hãy đổi admin token trong `server.py` (tìm `attraos_admin_2026`) thành chuỗi ngẫu nhiên.
