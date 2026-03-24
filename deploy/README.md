# 🚀 ATTRAOS Hub v1.1 — Hướng dẫn Deploy VPS

> Chuyển file này cho người quản lý VPS. Thực hiện theo thứ tự từ trên xuống.

---

## 📋 Tóm tắt những gì mới trong v1.1

| Thành phần | Mô tả |
|---|---|
| `server.py` | Thêm 2 API mới: `/orderflow/snapshot` và `/bookmap/latest.png` |
| `order_flow_analyzer.py` | Engine phân tích Order Flow: Iceberg, Absorption, Spoofing, Delta, Hunt |
| `bookmap_generator.py` | Render Heatmap PNG từ dữ liệu giá MT5 |
| `MT5_ATTRAOS_Hub_v3.mq5` | EA mới cho MT5: push DOM data + CVD tracker mỗi 5 giây |

---

## 🖥️ Bước 1 — Deploy lên VPS Hub Server

SSH vào VPS rồi chạy lần lượt:

```bash
# ─── Lần đầu tiên (chỉ làm 1 lần) ───────────────────────────
# Clone toàn bộ code từ GitHub về VPS (không cần gửi file qua Telegram)
git clone https://github.com/phamhuuluong/SignalScout.git ~/SignalScout
cd ~/SignalScout

# ─── Mỗi lần cập nhật sau này ─────────────────────────────────
cd ~/SignalScout
git pull origin main

# 3. Cài thêm thư viện vẽ hình (chỉ cần làm 1 lần)
pip install numpy matplotlib seaborn

# 4. Restart Hub server
# Nếu dùng systemctl:
sudo systemctl restart attraos-hub

# Nếu dùng pm2:
pm2 restart hub

# Nếu chạy tay (uvicorn):
pkill -f "uvicorn server"
nohup uvicorn server:app --host 0.0.0.0 --port 8001 &
```


---

## ✅ Bước 2 — Kiểm tra Deploy Thành Công

Mở 2 URL này trong trình duyệt (thay hub.lomofx.com bằng IP/domain thực):

```
https://hub.lomofx.com/orderflow/snapshot
```
→ Phải thấy JSON có các trường: `signals`, `delta`, `buy_pct`, `sell_pct`, `overall_bias`

```
https://hub.lomofx.com/bookmap/latest.png
```
→ Phải thấy ảnh Heatmap màu đen-đỏ-cam-vàng (ảnh ~300KB)

Nếu cả 2 URL trả về đúng = **Deploy thành công!** ✅

---

## 🤖 Bước 3 — Cài EA v3 lên MT5 (máy Mac của anh Luong)

File EA nằm trong thư mục này: `MT5_ATTRAOS_Hub_v3.mq5`

1. Copy file `MT5_ATTRAOS_Hub_v3.mq5` vào thư mục:
   ```
   ~/Library/Application Support/net.metaquotes.wine.metatrader5/drive_c/Program Files/MetaTrader 5/MQL5/Experts/
   ```
2. Mở MT5 → **Navigator** → **Expert Advisors** → refresh (F5)
3. Kéo **MT5_ATTRAOS_Hub_v3** vào biểu đồ bất kỳ
4. Cài đặt:
   - `HubURL` = `http://127.0.0.1:8001` (nếu VPS trên cùng máy) hoặc URL VPS thực
   - `SimulateDOM` = `true` (để EA tự giả lập DOM, không cần broker cấp L2)
   - `DOMInterval` = `5` (gửi DOM data mỗi 5 giây)
5. Bấm **OK** → EA bắt đầu chạy

**Dấu hiệu EA chạy đúng:** Nhìn góc trên phải biểu đồ thấy mặt cười và chữ `[ATTRAOS v3.00]`

---

## 📱 Bước 4 — Build & Upload iOS v1.1 lên TestFlight

*(Thực hiện trên máy Mac của anh Luong, cần Xcode)*

1. Mở Xcode → file `ATTRAOS.xcodeproj`
2. Đổi version lên **1.1.0** (ở TARGETS → General → Version)
3. **Product → Archive**
4. Cửa sổ Organizer bật lên → **Distribute App → App Store Connect → Upload**
5. Vào [App Store Connect](https://appstoreconnect.apple.com) → chọn app ATTRAOS → TestFlight
6. Chờ bản 1.1.0 xuất hiện (5-10 phút) → Thêm vào nhóm **Team Steven AI**
7. Điện thoại tester tự cập nhật qua TestFlight — **không cần xóa cài lại app**

---

## 🆕 Tính năng mới sau khi update

Trong tab **Phân Tích** của App, kéo xuống cuối sẽ thấy section mới:

> 🔥 **Order Flow (Bookmap L2)** — `MỚI`

- Hiển thị **CVD Delta** (% Mua vs Bán theo thời gian thực)
- **Signal Cards** cho từng pattern phát hiện được (🧊 Iceberg, 🧱 Absorption, 🎯 Stop Hunt...)
- Link trực tiếp sang **Bản đồ Thanh khoản** (Heatmap zoomable)
- **Tự động lưu** tín hiệu mạnh (strength ≥ 70%) vào Trade Journal
- **Push Notification** khi xuất hiện phân kỳ CVD hoặc Stop Hunt

---

*Ngày tạo: 24/03/2026 — ATTRAOS Hub v1.1*
