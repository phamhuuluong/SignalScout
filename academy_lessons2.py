"""
Academy Lessons Part 2 — Market Structure, S/R, Trend, Risk Management
"""

LESSONS_PART2 = [
    # ══════════════ MARKET STRUCTURE (3 lessons) ══════════════
    {
        "id": "structure_01", "category": "structure", "order": 1,
        "title": "Higher Highs, Lower Lows — Cấu Trúc Thị Trường",
        "description": "Nền tảng phân tích kỹ thuật — cách xác định xu hướng chính xác nhất.",
        "content": """# Market Structure (Cấu Trúc Thị Trường)

Market Structure là cách giá tạo ra các đỉnh (Highs) và đáy (Lows) liên tiếp. Đây là **nền tảng quan trọng nhất** của phân tích kỹ thuật.

## Uptrend (Xu hướng tăng) 📈
```
              HH₃
             / \\
        HH₂/   \\
       / \\ /     \\
  HH₁/   HL₂     \\
 / \\ /             \\
/   HL₁              ...
```

- **Higher High (HH):** Đỉnh sau CAO hơn đỉnh trước
- **Higher Low (HL):** Đáy sau CAO hơn đáy trước
- **Kết luận:** Buyer chiếm ưu thế → tìm cơ hội BUY tại HL

## Downtrend (Xu hướng giảm) 📉
```
\\   LH₁
 \\ / \\
  LL₁  \\   LH₂
        \\ / \\
         LL₂  \\   LH₃
               \\ /
                LL₃
```

- **Lower High (LH):** Đỉnh sau THẤP hơn đỉnh trước
- **Lower Low (LL):** Đáy sau THẤP hơn đáy trước
- **Kết luận:** Seller chiếm ưu thế → tìm cơ hội SELL tại LH

## Sideways (Đi ngang)
- Giá dao động trong range, không tạo HH/HL hay LH/LL rõ ràng
- **KHÔNG giao dịch** khi sideways trừ khi trade range bouncing

## Cách Xác Định Swing Points

**Swing High:** Nến có HIGH cao hơn ít nhất 2 nến trước và 2 nến sau
**Swing Low:** Nến có LOW thấp hơn ít nhất 2 nến trước và 2 nến sau

## Quy Tắc Giao Dịch Theo Structure
1. **Uptrend:** CHỈ BUY, entry tại HL (pullback)
2. **Downtrend:** CHỈ SELL, entry tại LH (pullback)
3. **Sideways:** KHÔNG trade hoặc trade range
4. Structure bị phá → đổi hướng (xem bài BOS/CHoCH)""",
        "key_points": [
            "Uptrend = HH + HL liên tiếp → chỉ BUY tại pullback (HL)",
            "Downtrend = LH + LL liên tiếp → chỉ SELL tại pullback (LH)",
            "Sideways = không có trend rõ → KHÔNG giao dịch",
            "Swing High/Low = đỉnh/đáy có ít nhất 2 nến xác nhận mỗi bên",
            "Giao dịch THEO cấu trúc, KHÔNG BAO GIỜ chống lại trend"
        ],
        "xp": 25, "estimated_minutes": 10,
    },
    {
        "id": "structure_02", "category": "structure", "order": 2,
        "title": "Swing Points & Key Levels",
        "description": "Cách xác định điểm swing quan trọng và vùng giá then chốt.",
        "content": """# Swing Points & Key Levels

## Swing High là gì?
Swing High là đỉnh cục bộ nơi giá tạm dừng và quay đầu giảm:
```
      ★ ← Swing High
     / \\
    /   \\
   /     \\
  /       \\
```

## Swing Low là gì?
Swing Low là đáy cục bộ nơi giá tạm dừng và quay đầu tăng:
```
  \\       /
   \\     /
    \\   /
     \\ /
      ★ ← Swing Low
```

## Phân Loại Key Levels

### Major Swing (Quan trọng)
- Tạo trên TF H4/D1
- Nhiều lần được test
- Gần round number (2000, 2050, 2100)
- → Dùng cho SL/TP chính

### Minor Swing (Phụ)
- Tạo trên TF M15/H1
- Ít lần được test
- → Dùng cho entry timing

## Cách Đánh Dấu Key Levels
1. Mở chart D1, đánh dấu swing highs/lows gần nhất
2. Chuyển H4, đánh dấu thêm các swing quan trọng
3. Chuyển H1, tìm các internal structure
4. Kết quả: bạn có bản đồ các vùng giá quan trọng

## Ứng Dụng
- SL đặt sau swing high/low gần nhất
- TP đặt tại swing high/low tiếp theo
- BOS = phá vỡ swing point → trend tiếp tục
- CHoCH = phá vỡ ngược → trend đảo chiều""",
        "key_points": [
            "Swing High = đỉnh cục bộ, Swing Low = đáy cục bộ",
            "Major Swings (D1/H4) quan trọng hơn Minor Swings (M15/H1)",
            "Đánh dấu swing từ TF lớn xuống TF nhỏ (top-down)",
            "SL đặt sau swing gần nhất, TP tại swing tiếp theo",
            "Khi swing bị phá = BOS hoặc CHoCH"
        ],
        "xp": 20, "estimated_minutes": 8,
    },
    {
        "id": "structure_03", "category": "structure", "order": 3,
        "title": "Range, Consolidation & Accumulation",
        "description": "Khi giá đi ngang — dấu hiệu tích lũy trước big move.",
        "content": """# Range & Consolidation

## Range (Vùng dao động)
```
═══════════════ Resistance ═══════
  ↗↘    ↗↘    ↗↘
 /  \\  /  \\  /  \\    ← Giá đi ngang
↗    ↘↗    ↘↗    ↘
═══════════════ Support ══════════
```

Giá dao động giữa support và resistance, không breakout.

## Accumulation (Tích lũy)
- Smart money âm thầm mua/bán
- Volume thấp, biên độ hẹp
- Thường xảy ra trước BREAKOUT mạnh
- Tích lũy càng lâu → breakout càng mạnh

## Distribution (Phân phối)
- Ngược lại accumulation
- Smart money đang bán ra
- Thường ở đỉnh trend
- Sau distribution → downtrend

## Trading Range
1. **Range bouncing:** BUY tại support, SELL tại resistance
   - SL ngoài range, TP phía bên kia
   - RR thường kém

2. **Breakout trading:** Đợi phá range + retest
   - Breakout + volume cao = thực sự
   - Breakout + volume thấp = fakeout
   - Luôn đợi retest trước khi entry

## Cách nhận biết Accumulation vs Distribution
- Accumulation: Near support, volume giảm dần → breakout UP
- Distribution: Near resistance, volume giảm dần → breakout DOWN""",
        "key_points": [
            "Range = giá dao động giữa S/R cố định",
            "Accumulation = smart money mua âm thầm → breakout tăng",
            "Distribution = smart money bán ra → breakout giảm",
            "Tích lũy càng lâu → breakout càng mạnh",
            "Breakout + volume cao = thực, volume thấp = fakeout"
        ],
        "xp": 20, "estimated_minutes": 8,
    },

    # ══════════════ SUPPORT & RESISTANCE (3 lessons) ══════════════
    {
        "id": "sr_01", "category": "sr", "order": 1,
        "title": "Support & Resistance Cơ Bản",
        "description": "Vùng giá nơi cung/cầu tập trung — nền tảng mọi phương pháp giao dịch.",
        "content": """# Support & Resistance

## Support (Hỗ trợ) 🟢
Vùng giá nơi **BUYER mạnh hơn SELLER**:
- Giá đến đây thường bật lên (bounce)
- Có nhiều pending buy orders
- Đã được test ít nhất 2 lần

## Resistance (Kháng cự) 🔴
Vùng giá nơi **SELLER mạnh hơn BUYER**:
- Giá đến đây thường bị reject
- Có nhiều pending sell orders
- Đã được test ít nhất 2 lần

## Quy Tắc Vẽ S/R

### DO ✅
1. Vẽ VÙNG (zone), không vẽ đường đơn lẻ
2. Dùng TF H1/H4/D1 để vẽ
3. Ít nhất 2 lần chạm
4. Vùng gần price hiện tại = quan trọng nhất
5. Đánh dấu round numbers (2000, 2050, 1900)

### DON'T ❌
1. Vẽ quá nhiều đường → rối chart
2. Vẽ trên TF quá nhỏ (M1/M5)
3. Force-fit S/R vào mọi đỉnh/đáy
4. Quên cập nhật khi price thay đổi

## Role Reversal (Đổi Vai Trò)
```
══ Resistance ═══════
                     ↓  BREAKOUT!
══════════════════════════════
       ↑ RETEST       → Giờ trở thành SUPPORT
══════════════════════════════
```

Khi Resistance bị phá → trở thành Support (và ngược lại). Đây là concept RẤT QUAN TRỌNG.

## Cách Trade S/R
1. BUY tại Support + confirmation (engulfing, hammer)
2. SELL tại Resistance + confirmation
3. Breakout + Retest = entry mạnh nhất
4. SL đặt ngoài vùng S/R""",
        "key_points": [
            "Support = buyer mạnh, Resistance = seller mạnh",
            "Vẽ VÙNG (zone) không phải đường chính xác, trên TF H1/H4",
            "Role Reversal: S bị phá → R, R bị phá → S",
            "Cần confirmation (candle pattern) trước khi entry tại S/R",
            "Vùng được test nhiều lần sẽ yếu dần → cuối cùng bị phá"
        ],
        "xp": 25, "estimated_minutes": 10,
    },
    {
        "id": "sr_02", "category": "sr", "order": 2,
        "title": "Dynamic S/R — EMA, Trendline, Fibonacci",
        "description": "S/R không cố định — sử dụng EMA, trendline và Fib để tìm vùng giá động.",
        "content": """# Dynamic Support & Resistance

## 1. EMA làm Dynamic S/R

EMA 21 và EMA 50 thường hoạt động như S/R di động:

**Trong Uptrend:**
- Giá pullback về EMA 21 → bounce → BUY
- EMA 21 = dynamic support

**Trong Downtrend:**
- Giá pullback lên EMA 21 → reject → SELL
- EMA 21 = dynamic resistance

**EMA 200:** Support/Resistance cực mạnh trên D1

## 2. Trendline

Vẽ đường nối 2+ swing lows (uptrend) hoặc swing highs (downtrend):
```
Uptrend trendline:
         /
        / ← Giá bounce tại trendline
       /
      / ← Touch 2
     /
    / ← Touch 1
```

**Quy tắc:** Cần ít nhất 3 touches để trendline có strength

## 3. Fibonacci Retracement

Các mức Fib quan trọng: **38.2%, 50%, 61.8%**

**Cách dùng:**
1. Kéo Fib từ swing low đến swing high (uptrend)
2. Đợi giá pullback về các mức Fib
3. Mức 61.8% = "Golden Ratio" — vùng entry tốt nhất
4. Kết hợp Fib + S/R cố định = vùng confluence

## Confluence Zone (Vùng Hội Tụ)

Khi nhiều yếu tố trùng tại 1 vùng giá = SETUP MẠNH NHẤT:
- EMA 21 + Fib 61.8% + Support cũ
- Trendline + Order Block + FVG
- Round number + Previous day high/low""",
        "key_points": [
            "EMA 21/50 hoạt động như dynamic S/R trong trending market",
            "Trendline cần ít nhất 3 touches mới đáng tin",
            "Fibonacci 61.8% là mức retracement quan trọng nhất (Golden Ratio)",
            "Confluence = nhiều yếu tố hội tụ tại 1 vùng = xác suất rất cao",
            "Kết hợp Static S/R + Dynamic S/R để có bản đồ chính xác nhất"
        ],
        "xp": 25, "estimated_minutes": 12,
    },

    # ══════════════ TREND ANALYSIS (2 lessons) ══════════════
    {
        "id": "trend_01", "category": "trend", "order": 1,
        "title": "EMA Cross & Trend Following",
        "description": "Sử dụng EMA 9/21 để xác định xu hướng và tìm entry theo trend.",
        "content": """# Trend Following với EMA

## EMA 9 & EMA 21 — Combo Phổ Biến Nhất

| Điều kiện | Tín hiệu |
|-----------|----------|
| EMA 9 > EMA 21 | ✅ Uptrend |
| EMA 9 < EMA 21 | ✅ Downtrend |
| EMA 9 cắt lên EMA 21 | 🟢 BUY signal (Golden Cross) |
| EMA 9 cắt xuống EMA 21 | 🔴 SELL signal (Death Cross) |
| Giá > cả 2 EMA | Strong uptrend |
| Giá < cả 2 EMA | Strong downtrend |
| Giá giữa 2 EMA | ⚠️ Transition zone |

## Cách Trade EMA Cross

### Setup BUY:
1. EMA 9 cắt lên EMA 21 (Golden Cross)
2. Giá pullback về EMA 21
3. Nến confirmation tại EMA 21 (hammer, engulfing)
4. Entry BUY, SL dưới swing low gần nhất

### Setup SELL:
1. EMA 9 cắt xuống EMA 21 (Death Cross)
2. Giá pullback lên EMA 21
3. Nến confirmation tại EMA 21
4. Entry SELL, SL trên swing high gần nhất

## RSI — Bộ Lọc Trend

| RSI | Ý nghĩa | Hành động |
|-----|---------|-----------|
| > 70 | Overbought | ⚠️ Có thể reversal, KHÔNG mua thêm |
| 50-70 | Bullish momentum | ✅ BUY tốt |
| 30-50 | Bearish momentum | ✅ SELL tốt |
| < 30 | Oversold | ⚠️ Có thể reversal, KHÔNG bán thêm |

## Combo EMA + RSI

**BUY mạnh:** EMA cross UP + RSI < 45 (còn room tăng)

**SELL mạnh:** EMA cross DOWN + RSI > 55 (còn room giảm)""",
        "key_points": [
            "EMA 9 > EMA 21 = uptrend, EMA 9 < EMA 21 = downtrend",
            "Golden Cross (cắt lên) = BUY, Death Cross (cắt xuống) = SELL",
            "Trade khi giá pullback về EMA, KHÔNG đuổi giá",
            "RSI > 70 = overbought, RSI < 30 = oversold",
            "EMA cross + RSI confirmation = setup có xác suất cao"
        ],
        "xp": 20, "estimated_minutes": 10,
    },
    {
        "id": "trend_02", "category": "trend", "order": 2,
        "title": "ATR, MACD & ADX — Đo Sức Mạnh Trend",
        "description": "Các indicator đo độ mạnh yếu của xu hướng và biến động thị trường.",
        "content": """# Indicators Đo Sức Mạnh Trend

## ATR (Average True Range) — Đo Biến Động
- ATR = trung bình biên độ nến gần nhất (14 nến)
- **ATR cao** = thị trường biến động mạnh → SL rộng hơn
- **ATR thấp** = thị trường yên tĩnh → SL hẹp hơn

**Ứng dụng thực tiễn:**
- SL = 1.5 x ATR (chuẩn)
- TP = 2 x ATR (RR 1:1.3) hoặc 3 x ATR (RR 1:2)
- ATR đang tăng → trend mạnh, tốt để trade
- ATR đang giảm → sideways, hạn chế trade

## MACD — Đo Momentum

MACD = EMA 12 - EMA 26, Signal = EMA 9 của MACD

| Tín hiệu | Ý nghĩa |
|-----------|---------|
| MACD > Signal | ✅ Bullish momentum |
| MACD < Signal | ✅ Bearish momentum |
| MACD cross UP Signal | 🟢 BUY signal |
| MACD cross DOWN Signal | 🔴 SELL signal |
| Histogram tăng dần | Momentum đang mạnh lên |
| Divergence (MACD ngược giá) | ⚠️ Trend sắp đổi |

## ADX — Đo Sức Mạnh Trend

| ADX | Ý nghĩa |
|-----|---------|
| < 20 | Không có trend, ĐỪNG trade trend |
| 20-40 | Trend trung bình, có thể trade |
| > 40 | Trend MẠNH, setup tốt |
| > 60 | Trend cực mạnh (hiếm) |

**ADX không chỉ hướng**, chỉ cho biết trend mạnh hay yếu.

## Bảng Quyết Định

| EMA | RSI | MACD | ADX | Hành động |
|-----|-----|------|-----|-----------|
| Cross UP | < 50 | Cross UP | > 25 | 🟢 BUY mạnh |
| Cross DOWN | > 50 | Cross DOWN | > 25 | 🔴 SELL mạnh |
| Mixed | 40-60 | Near zero | < 20 | ⚪ KHÔNG trade |""",
        "key_points": [
            "ATR đo biến động — dùng để tính SL/TP: SL = 1.5x ATR",
            "MACD đo momentum — cross UP = buy, cross DOWN = sell",
            "ADX đo sức mạnh trend — > 25 mới nên trade, < 20 = skip",
            "MACD Divergence (giá ngược MACD) = cảnh báo đổi trend sắp tới",
            "Kết hợp EMA + RSI + MACD + ADX cho quyết định chính xác nhất"
        ],
        "xp": 25, "estimated_minutes": 12,
    },

    # ══════════════ RISK MANAGEMENT (3 lessons) ══════════════
    {
        "id": "risk_01", "category": "risk", "order": 1,
        "title": "Quy Tắc 1-2% và Position Sizing",
        "description": "Bảo toàn vốn là ưu tiên SỐ 1 — cách tính lot size chính xác.",
        "content": """# Risk Management — Quy Tắc Sống Còn

> "Bạn không cần THẮNG nhiều. Bạn cần KHÔNG THUA lớn." — Pro Trader Rule

## Quy Tắc 1-2%

**KHÔNG BAO GIỜ rủi ro > 2% vốn cho 1 lệnh**

| Vốn | 1% Risk | 2% Risk |
|-----|---------|---------|
| $1,000 | $10 | $20 |
| $5,000 | $50 | $100 |
| $10,000 | $100 | $200 |
| $50,000 | $500 | $1,000 |

## Công Thức Tính Lot Size

```
Lot Size = Risk Amount / (SL pips × Pip Value)
```

### Ví Dụ 1: EUR/USD
- Vốn: $10,000
- Risk: 1% = $100
- SL: 20 pips
- Pip value (1 lot) = $10/pip

```
Lot = $100 / (20 × $10) = 0.50 lot
```

### Ví Dụ 2: XAU/USD
- Vốn: $5,000
- Risk: 1% = $50
- SL: 50 pips (= $5 giá vàng)
- Gold pip value (1 lot) ≈ $1/pip (0.01 lot)

```
Lot = $50 / (50 × $10) = 0.10 lot
```

## Quy Tắc Quản Lý Vốn Nâng Cao

1. **Max 3 lệnh mở cùng lúc** (tổng risk ≤ 5% vốn)
2. **Không mở 2 lệnh cùng cặp tiền** (double risk)
3. **Sau 2 lệnh thua liên tiếp → nghỉ 1 ngày**
4. **Mất 5% vốn trong tuần → nghỉ tuần đó**
5. **Khi thắng: giữ lot size, KHÔNG tăng vội**""",
        "key_points": [
            "KHÔNG BAO GIỜ rủi ro > 2% vốn / lệnh — lý tưởng 1%",
            "Lot Size = Risk Amount ÷ (SL pips × Pip Value)",
            "Tối đa 3 lệnh cùng lúc, tổng risk ≤ 5% vốn",
            "Sau 2 lệnh thua liên tiếp → dừng lại, review",
            "Kỷ luật quản lý vốn quan trọng hơn bất kỳ strategy nào"
        ],
        "xp": 30, "estimated_minutes": 12,
    },
    {
        "id": "risk_02", "category": "risk", "order": 2,
        "title": "Risk:Reward Ratio — Chìa Khóa Profitable",
        "description": "Tại sao RR 1:2 có thể profitable ngay cả khi win rate chỉ 40%.",
        "content": """# Risk:Reward Ratio (RR)

## RR là gì?

RR = Khoảng cách TP ÷ Khoảng cách SL

```
BUY @ 2300
SL  @ 2290 (risk 10 pips)
TP  @ 2320 (reward 20 pips)
→ RR = 20/10 = 1:2
```

## Bảng Win Rate Cần Thiết

| RR | Win Rate tối thiểu | Ý nghĩa |
|----|--------------------| ---------|
| 1:1 | > 50% | Thắng nhiều hơn thua |
| 1:1.5 | > 40% | Break even tại 40% |
| 1:2 | > 33% | Chỉ cần thắng 1/3 |
| 1:3 | > 25% | Thắng 1/4 vẫn profitable |

## Ví Dụ Thực Tế

**100 lệnh, RR 1:2, Win Rate 45%:**
- 45 lệnh thắng × $200 = $9,000
- 55 lệnh thua × $100 = $5,500
- **Lợi nhuận ròng: +$3,500** 🟢

**100 lệnh, RR 1:1, Win Rate 45%:**
- 45 lệnh thắng × $100 = $4,500
- 55 lệnh thua × $100 = $5,500
- **Lỗ ròng: -$1,000** 🔴

→ Cùng win rate, RR cao hơn = profitable!

## Quy Tắc RR
1. **Tối thiểu RR 1:2** cho mọi lệnh
2. Nếu RR < 1:1.5 → SKIP lệnh đó
3. Đặt SL trước, tính TP, rồi kiểm tra RR
4. Nếu RR < 1:2 vì TP gần S/R → giảm lot hoặc skip

## Partial Take Profit
```
BUY @ 2300, SL @ 2290
TP1: 2310 (1:1) — đóng 50% lệnh
TP2: 2320 (1:2) — đóng 30% lệnh  
TP3: 2330 (1:3) — đóng 20% lệnh
```
→ Bảo toàn profit + chạy theo trend""",
        "key_points": [
            "RR 1:2 = lời gấp đôi rủi ro, chỉ cần win rate > 33% để profitable",
            "KHÔNG BAO GIỜ vào lệnh nếu RR < 1:1.5",
            "Đặt SL trước → tính TP → kiểm tra RR → quyết định",
            "Partial TP (chia lệnh) vừa bảo toàn profit vừa chạy trend",
            "RR là yếu tố quan trọng nhất quyết định LỢI NHUẬN DÀI HẠN"
        ],
        "xp": 25, "estimated_minutes": 10,
    },
    {
        "id": "risk_03", "category": "risk", "order": 3,
        "title": "Psychology — Tâm Lý Trading",
        "description": "80% trading là tâm lý — kiểm soát cảm xúc là kỹ năng quan trọng nhất.",
        "content": """# Tâm Lý Trading

> "Trading is 80% psychology, 20% technique." — Mark Douglas

## 5 Sai Lầm Tâm Lý Chết Người

### 1. 🔴 Revenge Trading (Giao dịch trả thù)
- Sau khi thua → vào lệnh ngay để gỡ → thua tiếp → vòng xoáy
- **Giải pháp:** Sau 2 lệnh thua → TẮT MÁY, nghỉ ngơi

### 2. 🔴 FOMO (Fear Of Missing Out)
- Thấy giá chạy → nhảy vào muộn → bị trap
- **Giải pháp:** "Thị trường luôn có cơ hội mới. Bỏ lỡ 1 trade KHÔNG phải thảm họa."

### 3. 🔴 Overtrading
- Trade quá nhiều lệnh mỗi ngày → chi phí cao + quyết định kém
- **Giải pháp:** Max 3-5 lệnh/ngày, chỉ trade A+ setup

### 4. 🔴 Moving SL
- Dời SL ra xa khi giá gần chạm → thua nhiều hơn dự tính
- **Giải pháp:** SL là SL. ĐẶT RỒI KHÔNG CHẠM VÀO.

### 5. 🔴 Greed (Tham lam)
- Không chốt lời khi đạt TP → giá quay lại → mất hết profit
- **Giải pháp:** Đặt TP cố định hoặc dùng trailing stop

## Trading Plan — Kỷ Luật Số 1

Mỗi ngày cần có plan rõ ràng TRƯỚC khi mở chart:
1. Hôm nay trade cặp nào?
2. Timeframe nào?
3. Chỉ BUY hay SELL? (dựa trên HTF trend)
4. Vùng entry nào? (đã đánh dấu sẵn)
5. SL/TP cụ thể?
6. Risk bao nhiêu %?

**KHÔNG có plan = KHÔNG trade.**

## Daily Routine của Pro Trader
- 07:00 — Phân tích D1/H4, vẽ S/R, xác định bias
- 14:00 — London open: tìm setup trên H1/M15
- 19:00 — NY overlap: thời gian trade tốt nhất
- 23:00 — Đóng chart, review journal, nghỉ ngơi""",
        "key_points": [
            "80% trading = tâm lý, kiểm soát cảm xúc quan trọng hơn kỹ thuật",
            "5 sai lầm: Revenge Trading, FOMO, Overtrading, Moving SL, Greed",
            "Sau 2 lệnh thua liên tiếp → BẮT BUỘC dừng lại nghỉ",
            "Phải có Trading Plan TRƯỚC khi mở chart mỗi ngày",
            "SL đặt rồi KHÔNG ĐƯỢC DỜI — đây là quy tắc sắt"
        ],
        "xp": 30, "estimated_minutes": 12,
    },
]
