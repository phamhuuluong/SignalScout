"""
Academy Lessons — Full Content Database
30+ lessons across all 10 categories with detailed Vietnamese content
"""

LESSONS_FULL = [
    # ══════════════ TRADING BASICS (5 lessons) ══════════════
    {
        "id": "basics_01", "category": "basics", "order": 1,
        "title": "Forex thị trường là gì?",
        "description": "Thị trường ngoại hối lớn nhất thế giới — giao dịch $6.6 nghìn tỷ/ngày.",
        "content": """# Forex = Foreign Exchange

Forex là thị trường mua bán tiền tệ giữa các quốc gia. Đây là thị trường tài chính **lớn nhất thế giới** với khối lượng giao dịch hơn **$6.6 nghìn tỷ USD mỗi ngày**.

## Cặp Tiền Phổ Biến

| Cặp tiền | Tên gọi | Đặc điểm |
|----------|---------|----------|
| EUR/USD | Fiber | Phổ biến nhất, spread thấp |
| GBP/USD | Cable | Biến động mạnh |
| USD/JPY | Gopher | Safe haven, nghịch vàng |
| XAU/USD | Gold | Biến động rất mạnh |
| USD/CHF | Swissy | Safe haven |
| AUD/USD | Aussie | Liên quan hàng hoá |

## 3 Phiên Giao Dịch Chính

| Phiên | Giờ VN | Đặc điểm |
|-------|--------|----------|
| [Asia] Tokyo | 06:00-15:00 | Bien dong thap, range nho |
| [EU] London | 14:00-23:00 | Bien dong CAO nhat |
| [US] New York | 19:00-04:00 | Volume lon, tin tuc |
| [GOLD] London-NY Overlap | 19:00-23:00 | **THOI DIEM VANG** |

## Thuật Ngữ Cơ Bản

**Pip** = Đơn vị thay đổi nhỏ nhất
- EUR/USD: 0.0001 = 1 pip
- USD/JPY: 0.01 = 1 pip
- XAU/USD: 0.10 = 1 pip

**Lot** = Đơn vị giao dịch
- 1 Standard Lot = 100,000 đơn vị = $10/pip
- 1 Mini Lot = 10,000 đơn vị = $1/pip
- 1 Micro Lot = 1,000 đơn vị = $0.10/pip

**Spread** = Chênh lệch giá Bid và Ask
- EUR/USD spread thường ~1-2 pips
- XAU/USD spread thường ~10-30 pips
- Spread THẤP hơn = chi phí giao dịch THẤP hơn

**Leverage (Đòn bẩy)**
- 1:100 nghĩa là $100 có thể giao dịch $10,000
- Đòn bẩy cao = lợi nhuận CAO nhưng rủi ro cũng CAO
- Người mới nên dùng đòn bẩy thấp (1:10 — 1:30)""",
        "key_points": [
            "Forex giao dịch $6.6 nghìn tỷ USD/ngày — thị trường lớn nhất thế giới",
            "3 phiên chính: Asia, London, New York — overlap London-NY là thời điểm vàng",
            "1 pip EUR/USD = 0.0001, 1 standard lot = $10/pip",
            "Spread = chi phí giao dịch, leverage = con dao 2 lưỡi",
            "Người mới PHẢI bắt đầu với tài khoản demo + đòn bẩy thấp"
        ],
        "xp": 15, "estimated_minutes": 8,
    },
    {
        "id": "basics_02", "category": "basics", "order": 2,
        "title": "Biểu đồ nến Nhật (Japanese Candlestick)",
        "description": "Công cụ phân tích quan trọng nhất — cách đọc OHLC và ý nghĩa của nến.",
        "content": """# Biểu Đồ Nến Nhật

Biểu đồ nến được phát minh bởi Munehisa Homma vào thế kỷ 18 tại Nhật Bản. Đây là cách trình bày giá phổ biến nhất trong trading.

## Cấu Trúc 1 Nến

```
     │  ← Bóng trên (Upper Shadow/Wick)
     │
   ┌─┤  ← Open hoặc Close (tuỳ nến tăng/giảm)
   │ │
   │ │  ← THÂN NẾN (Body)
   │ │
   └─┤  ← Open hoặc Close
     │
     │  ← Bóng dưới (Lower Shadow/Wick)
```

Mỗi nến chứa 4 mức giá: **Open, High, Low, Close (OHLC)**

## Nến Tăng (Bullish) 🟢
- **Close > Open** (giá đóng cao hơn giá mở)
- Thân nến thường màu xanh/trắng
- Buyer (người mua) mạnh hơn trong khoảng thời gian đó
- Thân nến càng DÀI = lực mua càng MẠNH

## Nến Giảm (Bearish) 🔴
- **Close < Open** (giá đóng thấp hơn giá mở)
- Thân nến thường màu đỏ/đen
- Seller (người bán) mạnh hơn
- Thân nến càng DÀI = lực bán càng MẠNH

## Ý Nghĩa Bóng Nến

| Loại bóng | Ý nghĩa |
|-----------|---------|
| Bóng trên DÀI | Seller reject giá cao → áp lực bán |
| Bóng dưới DÀI | Buyer reject giá thấp → áp lực mua |
| Không có bóng (Marubozu) | Một bên kiểm soát hoàn toàn |
| Bóng 2 bên dài, thân nhỏ | Thị trường do dự mạnh |

## Quy Tắc Quan Trọng

1. **Timeframe lớn hơn = tín hiệu mạnh hơn** — nến D1 quan trọng hơn M15
2. **Context quan trọng hơn pattern** — nến búa tại support mới có ý nghĩa
3. **Volume xác nhận** — nến với volume cao = tín hiệu đáng tin
4. **Không trade 1 nến đơn lẻ** — luôn cần confirmation""",
        "key_points": [
            "Mỗi nến = 4 mức giá: Open, High, Low, Close (OHLC)",
            "Nến xanh (bullish) = Close > Open, nến đỏ (bearish) = Close < Open",
            "Bóng nến dài = rejection mạnh tại vùng giá đó",
            "Timeframe lớn hơn cho tín hiệu đáng tin hơn",
            "Luôn xem nến trong CONTEXT — vị trí trên chart quan trọng hơn hình dạng"
        ],
        "xp": 15, "estimated_minutes": 8,
    },
    {
        "id": "basics_03", "category": "basics", "order": 3,
        "title": "Timeframe & Multi-Timeframe Analysis",
        "description": "Chọn timeframe phù hợp và phân tích đa khung thời gian — bí quyết của pro trader.",
        "content": """# Timeframe & MTF Analysis

## Các Timeframe Phổ Biến

| TF | Loại trader | Thời gian giữ lệnh | SL trung bình |
|----|-------------|--------------------|--------------| 
| M1-M5 | Scalper | Vài phút | 5-15 pips |
| M15-M30 | Day trader | Vài giờ | 15-30 pips |
| H1-H4 | Swing trader | 1-5 ngày | 30-80 pips |
| D1-W1 | Position trader | Vài tuần-tháng | 80-200 pips |

## Multi-Timeframe Analysis (MTF)

MTF = nhìn chart từ TF lớn đến TF nhỏ. Đây là phương pháp của 90% pro trader.

### Quy Trình MTF (Top-Down)

**Bước 1: TF Lớn (D1/H4)** — Xác định XU HƯỚNG CHÍNH
- Uptrend hay Downtrend hay Sideways?
- Vùng S/R quan trọng nào gần nhất?
- → Quyết định: Chỉ BUY hoặc chỉ SELL

**Bước 2: TF Trung (H1)** — Xác định VÙNG ENTRY
- Tìm vùng demand/supply
- Xác định Order Block, FVG
- → Quyết định: Entry ở vùng nào?

**Bước 3: TF Nhỏ (M15/M5)** — TIMING VÀO LỆNH
- Đợi confirmation pattern (engulfing, BOS)
- Đặt SL/TP chính xác
- → Quyết định: Entry NGAY hoặc đợi

## Ví Dụ Thực Tế

```
D1: XAUUSD đang UPTREND (HH + HL)
    → Chỉ tìm cơ hội BUY

H1: Giá pullback về vùng demand 2300-2305
    → Đợi giá đến vùng này

M15: Bullish Engulfing tại 2302 + BOS
    → BUY @ 2303, SL 2295, TP 2320
```

## Quy Tắc Vàng MTF
1. **KHÔNG BAO GIỜ** trade ngược TF lớn
2. TF lớn + TF nhỏ cùng hướng = STRONG signal
3. TF lớn và TF nhỏ xung đột = **KHÔNG VÀO LỆNH**
4. Luôn bắt đầu từ TF lớn, drill down xuống TF nhỏ""",
        "key_points": [
            "MTF = Top-Down: TF lớn (trend) → TF trung (zone) → TF nhỏ (entry timing)",
            "KHÔNG BAO GIỜ giao dịch ngược xu hướng TF lớn",
            "M15 là TF phổ biến nhất cho day trading, H4 cho swing",
            "TF lớn + TF nhỏ cùng hướng = xác suất thắng cao nhất",
            "Nếu TF lớn và TF nhỏ xung đột → skip, không vào lệnh"
        ],
        "xp": 20, "estimated_minutes": 10,
    },
    {
        "id": "basics_04", "category": "basics", "order": 4,
        "title": "Bid/Ask, Spread và Chi Phí Giao Dịch",
        "description": "Hiểu rõ chi phí ẩn khi giao dịch — spread, commission, swap.",
        "content": """# Chi Phí Giao Dịch

## Bid và Ask

- **Bid** = Giá BÁN (bạn bán cho sàn ở giá này)
- **Ask** = Giá MUA (bạn mua từ sàn ở giá này)
- **Ask luôn > Bid** — chênh lệch = Spread

```
EUR/USD:
  Bid: 1.08520
  Ask: 1.08535
  → Spread = 1.5 pips
```

## Spread

| Cặp tiền | Spread thường | Phiên tốt nhất |
|----------|---------------|----------------|
| EUR/USD | 0.5-2 pips | London-NY |
| GBP/USD | 1-3 pips | London |
| XAU/USD | 10-50 pips | London-NY |
| BTC/USD | 5-20 USD | 24/7 |

**Spread mở rộng khi:** Tin tức quan trọng, đầu/cuối phiên, cuối tuần

## Commission
- Một số sàn thu thêm phí commission từng lệnh
- Thường $3-7/lot/side (mở + đóng)
- Sàn ECN: spread thấp nhưng có commission

## Swap (Phí qua đêm)
- Giữ lệnh qua đêm bị tính phí swap
- Swap có thể DƯƠNG hoặc ÂM
- Thứ 4 tính swap x3 (cuối tuần)
- **Scalper/Day trader** thường không bị ảnh hưởng""",
        "key_points": [
            "Ask > Bid luôn, chênh lệch = Spread = chi phí giao dịch chính",
            "Spread thấp nhất vào giờ overlap London-NY (19:00-23:00 VN)",
            "Spread mở rộng khi tin tức quan trọng — tránh trade lúc này",
            "Commission là phí cố định mỗi lot, swap là phí giữ qua đêm",
            "Day trader tránh swap bằng cách đóng lệnh trước cuối ngày"
        ],
        "xp": 10, "estimated_minutes": 6,
    },
    {
        "id": "basics_05", "category": "basics", "order": 5,
        "title": "Các Loại Lệnh (Order Types)",
        "description": "Market, Limit, Stop — biết khi nào dùng loại nào là kỹ năng sống còn.",
        "content": """# Các Loại Lệnh

## 1. Market Order (Lệnh thị trường)
- Mua/bán NGAY LẬP TỨC tại giá hiện tại
- Ưu: Nhanh, chắc chắn được khớp
- Nhược: Có thể bị slippage (trượt giá)
- **Dùng khi:** Cần vào NGAY, giá đang tại vùng mong muốn

## 2. Limit Order (Lệnh giới hạn)
- Buy Limit: Đặt mua ở giá THẤP hơn hiện tại
- Sell Limit: Đặt bán ở giá CAO hơn hiện tại
- **Dùng khi:** Đợi giá pullback về vùng entry

```
Giá hiện tại: 2320
Buy Limit: 2305 (đợi giá giảm về 2305 rồi mua)
```

## 3. Stop Order
- Buy Stop: Đặt mua ở giá CAO hơn (breakout)
- Sell Stop: Đặt bán ở giá THẤP hơn (breakdown)
- **Dùng khi:** Trade breakout

## 4. Stop Loss (SL) — BẮT BUỘC
- Tự động đóng lệnh khi thua
- **LUÔN LUÔN** đặt SL trước khi vào lệnh
- Không bao giờ gỡ SL hoặc dời SL ra xa

## 5. Take Profit (TP)
- Tự động đóng lệnh khi thắng
- Đặt tại vùng S/R, target tiếp theo
- Có thể chia TP thành nhiều phần (partial TP)

## So Sánh

| Loại | Khi nào dùng | Ưu điểm |
|------|-------------|---------|
| Market | Vào ngay | Nhanh |
| Buy Limit | Đợi pullback | Entry tốt hơn |
| Buy Stop | Trade breakout | Bắt momentum |""",
        "key_points": [
            "Market Order = vào ngay, Limit Order = đợi giá về vùng mong muốn",
            "Buy Limit: mua thấp hơn, Sell Limit: bán cao hơn hiện tại",
            "Buy Stop: breakout lên, Sell Stop: breakdown xuống",
            "Stop Loss là BẮT BUỘC — không bao giờ trade mà không có SL",
            "Take Profit nên chia thành 2-3 phần để bảo toàn lợi nhuận"
        ],
        "xp": 15, "estimated_minutes": 8,
    },

    # ══════════════ CANDLESTICK PATTERNS (5 lessons) ══════════════
    {
        "id": "candles_01", "category": "candles", "order": 1,
        "title": "Bullish Engulfing — Đảo Chiều Tăng",
        "description": "Mô hình 2 nến đảo chiều mạnh nhất — nến tăng bao trùm nến giảm.",
        "content": """# Bullish Engulfing 🟢

## Hình Dạng
```
      │
    ┌─┤   ← Nến 1: Bearish (nhỏ)
    └─┤
      │

  ┌───┤   ← Nến 2: Bullish (LỚN, bao trùm hoàn toàn nến 1)
  │   │
  │   │
  └───┤
```

## Điều Kiện Hợp Lệ
1. ✅ Nến 1: Bearish (giảm)
2. ✅ Nến 2: Bullish (tăng), thân **HOÀN TOÀN** bao trùm thân nến 1
3. ✅ Xuất hiện sau downtrend hoặc tại vùng demand/support
4. ✅ Volume nến 2 cao hơn nến 1

## Tín Hiệu Mạnh Khi
- Tại vùng Support/Demand quan trọng
- Nến 2 có volume GẤP ĐÔI nến 1
- Overlap với Order Block hoặc FVG
- Sau 3-5 nến giảm liên tiếp (exhaustion)

## Tín Hiệu Yếu Khi
- Giữa trend, không tại S/R
- Volume thấp
- Bóng trên nến 2 quá dài (seller vẫn mạnh)

## Cách Giao Dịch
```
Entry: Close của nến engulfing
SL:    Low của pattern (bóng dưới nến 2)
TP1:   1:1 RR
TP2:   Resistance tiếp theo
```

## Ví Dụ Thực Tế
XAUUSD M15 tại demand zone 2300:
- Nến 1: Bearish, body = 3 pips
- Nến 2: Bullish, body = 8 pips, engulf hoàn toàn
- Entry: 2302, SL: 2296, TP: 2314
- RR = 1:2 ✅""",
        "key_points": [
            "Nến 2 phải bao trùm HOÀN TOÀN thân nến 1 (không chỉ bóng)",
            "Tại support/demand = tín hiệu rất mạnh, giữa chart = yếu",
            "Volume nến 2 phải cao hơn nến 1 để xác nhận",
            "SL đặt dưới low toàn bộ pattern, RR tối thiểu 1:2",
            "Kết hợp với SMC (OB, FVG) tăng xác suất thành công"
        ],
        "xp": 15, "estimated_minutes": 7,
    },
    {
        "id": "candles_02", "category": "candles", "order": 2,
        "title": "Bearish Engulfing — Đảo Chiều Giảm",
        "description": "Ngược lại Bullish Engulfing — nến giảm bao trùm nến tăng tại đỉnh.",
        "content": """# Bearish Engulfing 🔴

## Hình Dạng
```
  ┌───┤   ← Nến 2: Bearish (LỚN)
  │   │
  │   │
  └───┤
      │
    ┌─┤   ← Nến 1: Bullish (nhỏ)
    └─┤
```

## Điều Kiện
1. Nến 1: Bullish (tăng)
2. Nến 2: Bearish (giảm), bao trùm hoàn toàn
3. Tại resistance/supply zone hoặc cuối uptrend
4. Volume nến 2 cao

## Cách Giao Dịch
```
Entry: Close nến engulfing
SL:    Trên high của pattern
TP:    Support tiếp theo, RR ≥ 1:2
```

## Combo Mạnh
- Bearish Engulfing + tại Supply Zone = 🔥
- Bearish Engulfing + Liquidity Sweep (wick quá đỉnh) = 🔥🔥
- Bearish Engulfing + FVG fill = 🔥🔥🔥""",
        "key_points": [
            "Ngược lại Bullish Engulfing — nến giảm bao trùm nến tăng",
            "Mạnh nhất tại resistance/supply zone",
            "Nếu có sweep (bóng trên vượt đỉnh trước) = rất mạnh",
            "SL trên high pattern, TP support tiếp theo",
            "Combo với SMC concepts tăng xác suất"
        ],
        "xp": 15, "estimated_minutes": 5,
    },
    {
        "id": "candles_03", "category": "candles", "order": 3,
        "title": "Hammer & Shooting Star — Đảo Chiều 1 Nến",
        "description": "Hai mô hình nến đơn mạnh mẽ nhất cho tín hiệu reversal.",
        "content": """# Hammer & Shooting Star

## Hammer 🔨 (Đảo chiều TĂNG)

```
   ├──┐  ← Thân nhỏ ở TRÊN
   │  │
   │
   │  ← Bóng dưới DÀI (≥ 2x thân)
   │
   │
```

**Quy tắc:**
- Bóng dưới ≥ 2x chiều dài thân
- Bóng trên rất nhỏ hoặc không có
- Xuất hiện cuối DOWNTREND
- Màu nến KHÔNG quan trọng (xanh càng tốt)

**Ý nghĩa:** Giá giảm rất sâu trong phiên nhưng buyer đã đẩy giá lên lại → buyer MẠNH.

## Shooting Star ⭐ (Đảo chiều GIẢM)

```
   │
   │  ← Bóng trên DÀI (≥ 2x thân)
   │
   │
   ├──┐  ← Thân nhỏ ở DƯỚI
   │  │
```

**Quy tắc:**
- Bóng trên ≥ 2x chiều dài thân
- Bóng dưới rất nhỏ hoặc không có
- Xuất hiện cuối UPTREND
- Tại resistance = tín hiệu mạnh

**Ý nghĩa:** Giá tăng cao trong phiên nhưng seller đã ép giá xuống → seller MẠNH.

## Inverted Hammer & Hanging Man

- **Inverted Hammer:** Hình dạng giống Shooting Star nhưng ở cuối downtrend → Bullish
- **Hanging Man:** Hình dạng giống Hammer nhưng ở cuối uptrend → Bearish

## Trading Rules
1. LUÔN đợi nến tiếp theo xác nhận
2. Hammer → nến tiếp phải tăng = BUY
3. Shooting Star → nến tiếp phải giảm = SELL
4. SL đặt ngoài bóng dài""",
        "key_points": [
            "Hammer: bóng dưới dài ≥ 2x thân, cuối downtrend = buy signal",
            "Shooting Star: bóng trên dài ≥ 2x thân, cuối uptrend = sell signal",
            "Inverted Hammer & Hanging Man là bản ngược",
            "LUÔN đợi nến confirmation trước khi vào lệnh",
            "SL đặt ngoài bóng dài của pattern"
        ],
        "xp": 15, "estimated_minutes": 8,
    },
    {
        "id": "candles_04", "category": "candles", "order": 4,
        "title": "Doji — Nến Do Dự & 4 Biến Thể",
        "description": "Khi buyer và seller ngang sức — tín hiệu đảo chiều tiềm năng.",
        "content": """# Doji Patterns

Doji xuất hiện khi Open ≈ Close (thân nến cực nhỏ hoặc không có).

## 4 Loại Doji

### 1. Standard Doji ✚
```
  │
  ·  ← Open ≈ Close
  │
```
- Bóng trên = bóng dưới
- = Thị trường HOÀN TOÀN do dự
- Cần context: tại S/R mới có ý nghĩa

### 2. Dragonfly Doji 🐉
```
  ·  ← Open = High = Close
  │
  │  ← Bóng dưới rất dài
  │
```
- = Giống Hammer nhưng thân = 0
- **BULLISH** tại support
- Buyer reject giá thấp rất mạnh

### 3. Gravestone Doji ⚰️
```
  │
  │  ← Bóng trên rất dài
  │
  ·  ← Open = Low = Close
```
- = Giống Shooting Star nhưng thân = 0
- **BEARISH** tại resistance
- Seller reject giá cao rất mạnh

### 4. Long-Legged Doji
```
  │
  │  ← Bóng trên rất dài
  ·
  │  ← Bóng dưới rất dài
  │
```
- Cả buyer và seller đều mạnh
- Biến động lớn nhưng kết quả = 0
- Thường xuất hiện trước big move

## Cách Giao Dịch Doji
1. **KHÔNG** trade Doji đơn lẻ
2. Doji + Engulfing tiếp theo = setup mạnh
3. Doji tại S/R quan trọng = chuẩn bị reversal
4. Nhiều Doji liên tiếp = thị trường sắp bùng nổ""",
        "key_points": [
            "Doji = Open ≈ Close, thị trường do dự",
            "4 loại: Standard, Dragonfly (bullish), Gravestone (bearish), Long-Legged",
            "KHÔNG bao giờ trade Doji đơn lẻ — cần nến xác nhận",
            "Doji tại vùng S/R quan trọng = tín hiệu đảo chiều rất mạnh",
            "Nhiều Doji liên tiếp = thị trường sắp có big move"
        ],
        "xp": 15, "estimated_minutes": 7,
    },
    {
        "id": "candles_05", "category": "candles", "order": 5,
        "title": "Morning Star, Evening Star & Three Pattern",
        "description": "Mô hình 3 nến đảo chiều đáng tin nhất trong technical analysis.",
        "content": """# Mô Hình 3 Nến

## Morning Star ⭐🌅 (Bullish Reversal)
```
Nến 1:  ┌──┐
        │  │  ← Bearish LỚN (lực bán mạnh)
        └──┘
                  ↕ Gap
Nến 2:       ·   ← Thân nhỏ/Doji (do dự, lực bán yếu dần)

Nến 3:    ┌──┐
           │  │  ← Bullish LỚN (buyer chiếm quyền)
           └──┘   Close > 50% nến 1
```

**Điều kiện:**
- Nến 1: Bearish lớn (downtrend)
- Nến 2: Thân nhỏ, có thể gap down
- Nến 3: Bullish lớn, close > 50% thân nến 1

## Evening Star 🌙 (Bearish Reversal)
```
Nến 1:   ┌──┐
          │  │  ← Bullish LỚN
          └──┘
                   ↕ Gap
Nến 2:        ·   ← Thân nhỏ/Doji

Nến 3: ┌──┐
        │  │  ← Bearish LỚN
        └──┘   Close < 50% nến 1
```

## Three White Soldiers 🟢🟢🟢
- 3 nến tăng liên tiếp, mỗi nến đóng CAO hơn
- Không có bóng trên dài
- = Uptrend rất mạnh bắt đầu

## Three Black Crows 🔴🔴🔴
- 3 nến giảm liên tiếp, mỗi nến đóng THẤP hơn
- = Downtrend rất mạnh bắt đầu

## So Sánh Độ Tin Cậy

| Pattern | Tin cậy | Tại S/R |
|---------|---------|---------|
| Morning/Evening Star | ★★★★ | ★★★★★ |
| Three Soldiers/Crows | ★★★★ | ★★★★ |
| Engulfing | ★★★ | ★★★★ |
| Hammer/Star | ★★★ | ★★★★ |
| Doji | ★★ | ★★★ |""",
        "key_points": [
            "Morning Star: 3 nến đảo chiều tăng — Bearish→Doji→Bullish",
            "Evening Star: 3 nến đảo chiều giảm — Bullish→Doji→Bearish",
            "Nến 3 phải close > 50% thân nến 1 để hợp lệ",
            "Three Soldiers/Crows = 3 nến liên tiếp cùng chiều = trend mạnh",
            "Mô hình 3 nến ĐÁ TIN CẬY hơn 1-2 nến"
        ],
        "xp": 20, "estimated_minutes": 10,
    },
]
