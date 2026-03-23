"""
Academy Lessons Part 3 — SMC, Liquidity, BOS, FVG + Extended Quizzes & Patterns
"""

LESSONS_PART3 = [
    # ══════════════ SMART MONEY CONCEPTS (3 lessons) ══════════════
    {
        "id": "smc_01", "category": "smc", "order": 1,
        "title": "Smart Money là gì? — Cách Tổ Chức Giao Dịch",
        "description": "Hiểu cách ngân hàng và quỹ lớn thao túng thị trường — và cách trade CÙNG họ.",
        "content": """# Smart Money Concepts (SMC)

## Smart Money = Tiền Thông Minh
- Ngân hàng trung ương (JP Morgan, Goldman Sachs, Citibank)
- Hedge funds, quỹ đầu tư lớn
- Chiếm **~70% volume** thị trường Forex
- Họ KHÔNG trade như retail trader

## Retail vs Smart Money

| Retail Trader | Smart Money |
|--------------|-------------|
| Mua khi giá tăng (FOMO) | Mua khi giá GIẢM (accumulation) |
| Đặt SL tại đỉnh/đáy rõ ràng | SĂN stop loss của retail |
| Trade theo indicator | Trade theo ORDER FLOW |
| Theo đám đông | NGƯỢC đám đông |
| Thua 90% tài khoản | Chiếm 70% profit |

## Vòng Đời Của 1 Setup Smart Money

```
1. ACCUMULATION (Tích lũy)
   Smart money mua âm thầm tại giá thấp

2. MANIPULATION (Thao túng)  
   Đẩy giá xuống thêm → trigger SL retail
   = LIQUIDITY SWEEP

3. DISTRIBUTION (Phân phối)
   Smart money bán ở giá cao cho retail
   = REAL MOVE bắt đầu
```

> **Mẫu AMD**: Accumulation → Manipulation → Distribution

## 5 Khái Niệm Chính của SMC

| Concept | Ý nghĩa |
|---------|---------|
| Order Block (OB) | Vùng lệnh lớn của tổ chức |
| Fair Value Gap (FVG) | Khoảng trống giá chưa lấp |
| Break of Structure (BOS) | Phá vỡ cấu trúc = trend tiếp |
| Change of Character (CHoCH) | Thay đổi = đảo chiều |
| Liquidity Sweep | Quét stop loss retail |

## Tư Duy SMC
> "Đừng trade CHỐNG LẠI smart money. Hãy trade CÙNG họ."
> "Khi bạn thấy giá đuổi stop loss → đó là smart money đang thu thập thanh khoản."
> "Sau sweep luôn là real move."

## Ứng Dụng Thực Tế
1. TÌM liquidity pool (equal highs/lows, SL clusters)
2. ĐẰNG sweep xảy ra
3. ĐÁNH DẤU Order Block trước BOS
4. ENTRY khi giá retest OB sau sweep + BOS""",
        "key_points": [
            "Smart Money (SM) = ngân hàng & quỹ lớn, chiếm 70% volume thị trường",
            "Mẫu AMD: Accumulation → Manipulation (sweep SL) → Distribution (real move)",
            "5 concept chính: OB, FVG, BOS, CHoCH, Liquidity Sweep",
            "SM săn stop loss retail trước khi đẩy giá theo hướng thực sự",
            "Giao dịch CÙNG smart money, không chống lại họ"
        ],
        "xp": 30, "estimated_minutes": 12,
    },
    {
        "id": "smc_02", "category": "smc", "order": 2,
        "title": "Order Block (OB) — Vùng Lệnh Tổ Chức",
        "description": "Cách xác định nơi smart money đặt lệnh lớn — vùng entry xác suất cao nhất.",
        "content": """# Order Block (OB)

## OB là gì?
Order Block = **nến cuối cùng đi NGƯỢC CHIỀU trước khi xảy ra BOS**.

Đây là nơi smart money đặt lệnh lớn, tạo ra impulsive move.

## Bullish Order Block (Demand)
```
         ↗ BOS (phá đỉnh)
        /
       /
  ████ ← BULLISH OB (nến giảm cuối cùng trước BOS)
  ████
```
- = Nến BEARISH cuối cùng trước BOS tăng
- Dùng HIGH và LOW của nến này làm zone
- Giá quay lại → BUY

## Bearish Order Block (Supply)
```
  ████ ← BEARISH OB (nến tăng cuối cùng trước BOS)
  ████
       \\
        \\
         ↘ BOS (phá đáy)
```
- = Nến BULLISH cuối cùng trước BOS giảm
- Giá quay lại → SELL

## Xác Định OB Chất Lượng Cao

### OB Mạnh ✅
- Tạo ra BOS rõ ràng (impulsive)
- Có FVG kèm theo (nến chạy nhanh)
- Chưa được mitigate (test lần đầu)
- Volume cao tại vùng OB

### OB Yếu ❌
- BOS yếu, không rõ ràng
- Đã được mitigate (test rồi)
- Nhỏ trên TF lớn
- Nằm giữa range

## Trading OB
```
1. Xác định BOS trên M15/H1
2. Tìm nến ngược chiều cuối cùng trước BOS = OB
3. Đánh dấu OB zone (high → low)
4. Đợi giá pullback về OB
5. Entry + SL ngoài OB + TP = structure tiếp theo
```

## OB + FVG = COMBO MẠNH NHẤT
Khi OB overlap với FVG → vùng "Mitigation Block" → entry xác suất CAO NHẤT""",
        "key_points": [
            "OB = nến ngược chiều cuối cùng TRƯỚC Break of Structure",
            "Bullish OB = nến giảm trước BOS tăng → demand zone",
            "Bearish OB = nến tăng trước BOS giảm → supply zone",
            "OB chất lượng cao: tạo BOS rõ, có FVG, chưa mitigate",
            "OB + FVG overlap = Mitigation Block = setup tốt nhất trong SMC"
        ],
        "xp": 30, "estimated_minutes": 12,
    },
    {
        "id": "smc_03", "category": "smc", "order": 3,
        "title": "Mẫu AMD & Entry Model Hoàn Chỉnh",
        "description": "Accumulation-Manipulation-Distribution — mô hình entry chính xác nhất.",
        "content": """# Mẫu AMD (Accumulation-Manipulation-Distribution)

## Pha 1: Accumulation (Tích Lũy)
```
═══════════════ Range High ═══════
  ↗↘    ↗↘    ↗↘
 /  \\  /  \\  /  \\
↗    ↘↗    ↘↗    ↘
═══════════════ Range Low ════════
```
- Giá đi ngang trong range
- Volume thấp
- SM đang tích lũy lệnh

## Pha 2: Manipulation (Thao Túng)
```
═══════════════ Range High ═══════
                         ↗↘
SM push giá phá range →    ↘ ← SWEEP! (retail stops triggered)
═══════════════ Range Low ════════
                              ↘
                         FAKE BREAKOUT
```
- SM đẩy giá phá range → trigger SL retail
- = LIQUIDITY GRAB
- Retail nghĩ breakout → vào lệnh → BỊ TRAP

## Pha 3: Distribution (Phân Phối)
```
═══════════════ Range High ═══════
                         
═══════════════ Range Low ════════
                              ↗
                         ↗   ← REAL MOVE!
                    ↗
              ↗
         ↗
    BOS ← Giá phá theo hướng THẬT
```
- Sau sweep → giá đảo chiều MẠNH
- BOS xác nhận hướng thật
- = ENTRY POINT

## Complete Entry Model

```
BƯỚC 1: Tìm liquidity pool (EQH/EQL)
         ↓
BƯỚC 2: Đợi SWEEP xảy ra
         ↓
BƯỚC 3: Tìm CHoCH/BOS trên M15
         ↓
BƯỚC 4: Đánh dấu OB trước BOS
         ↓
BƯỚC 5: Entry tại OB + FVG
         ↓
SL: Ngoài sweep high/low
TP: Liquidity phía bên kia (EQL nếu sell, EQH nếu buy)
```

## Ví Dụ XAUUSD
1. Equal Highs tại 2350 (BSL — Buy Side Liquidity)
2. Giá spike lên 2352 → SWEEP equal highs ✅
3. M15 bearish engulfing + BOS giảm ✅
4. Bearish OB tại 2348-2350
5. SELL @ 2349, SL @ 2353, TP @ 2330
6. RR = 1:4.75 🔥""",
        "key_points": [
            "AMD = Accumulation (tích lũy) → Manipulation (sweep SL) → Distribution (real move)",
            "Manipulation = fake breakout để grab liquidity, KHÔNG PHẢI real breakout",
            "Entry sau sweep + BOS + tại OB/FVG → xác suất thắng rất cao",
            "SL đặt ngoài sweep high/low, TP tại liquidity phía bên kia",
            "Đây là mô hình entry CHÍNH XÁC NHẤT mà pro SMC trader sử dụng"
        ],
        "xp": 35, "estimated_minutes": 15,
    },

    # ══════════════ LIQUIDITY (2 lessons) ══════════════
    {
        "id": "liq_01", "category": "liquidity", "order": 1,
        "title": "Liquidity & Stop Hunt — Bẫy Thanh Khoản",
        "description": "Nơi SM săn stop loss của retail — vùng Equal Highs/Lows và round numbers.",
        "content": """# Liquidity (Thanh Khoản)

## Liquidity là gì?
Liquidity = **tập trung nhiều lệnh chờ** (stop loss, limit orders) tại 1 vùng giá.

Smart money CẦN liquidity để fill các lệnh lớn của họ.

## Nơi Liquidity Tập Trung

### 1. Equal Highs (EQH) — Buy Side Liquidity (BSL)
```
     ──── Equal Highs ════   ← SL của SHORT ở đây
    /    /    /
   /    /    /
```
- Nhiều đỉnh bằng nhau → retail đặt SL ở trên
- SM sẽ SWEEP lên → trigger SL → rồi bán xuống

### 2. Equal Lows (EQL) — Sell Side Liquidity (SSL)
```
   \\    \\    \\
    \\    \\    \\
     ──── Equal Lows ════   ← SL của LONG ở đây
```
- Nhiều đáy bằng nhau → retail đặt SL ở dưới
- SM sẽ SWEEP xuống → trigger SL → rồi mua lên

### 3. Round Numbers: 2000, 2050, 2100, 2200
### 4. Previous Day High/Low (PDH/PDL)
### 5. Previous Week High/Low (PWH/PWL)
### 6. Trendline touches (SL behind trendline)

## Stop Hunt (Quét Stop Loss)

```
     ════ Equal Highs ════
            ↗ WICK! (sweep lên)
    /      / \\
   /      /   \\  ← Giá đảo chiều SAU sweep
  /      /     \\
 /      /       ↘ Real move DOWN
```

**Dấu hiệu sau sweep:**
- Long wick quá đỉnh/đáy rồi close lại trong range
- Volume spike tại vùng sweep
- Sau sweep → BOS ngược hướng = xác nhận

## Liquidity Void
= Vùng giá mà giá chạy quá nhanh, không có giao dịch
- Thường trùng với FVG
- Giá có xu hướng quay lại lấp void này""",
        "key_points": [
            "Liquidity = SL clusters + pending orders tại 1 vùng giá",
            "Equal Highs (BSL) — SL short ở trên, Equal Lows (SSL) — SL long ở dưới",
            "SM cần sweep liquidity TRƯỚC KHI real move",
            "Sau sweep (wick quá đỉnh/đáy rồi close lại) → entry ngược hướng",
            "Trade SAU sweep, KHÔNG PHẢI trước sweep — đợi xác nhận BOS"
        ],
        "xp": 30, "estimated_minutes": 12,
    },
    {
        "id": "liq_02", "category": "liquidity", "order": 2,
        "title": "Liquidity Heatmap — Bản Đồ Thanh Khoản",
        "description": "Cách đọc liquidity heatmap và dự đoán nơi giá sẽ hướng tới.",
        "content": """# Liquidity Heatmap

## Tại Sao Cần Heatmap?
- Giá luôn hướng về nơi có NHIỀU liquidity nhất
- Heatmap cho thấy VÙng nào có nhiều SL/orders chờ
- Biết nơi liquidity → biết giá sẽ đi đâu

## Cách Đọc Heatmap

**Density Score (Điểm mật độ):**
| Score | Ý nghĩa |
|-------|---------|
| 80-100 | 🔴 Rất nhiều liquidity → giá CÓ THỂ hướng tới |
| 50-79 | 🟡 Liquidity trung bình |
| 20-49 | 🟢 Ít liquidity |
| 0-19 | ⚪ Không đáng kể |

## Các Vùng Trên Heatmap

### BSL (Buy Side Liquidity) — Trên giá hiện tại
- Equal Highs, Previous Day High, Round number trên
- = Nơi SM có thể sweep LÊN trước khi bán

### SSL (Sell Side Liquidity) — Dưới giá hiện tại
- Equal Lows, Previous Day Low, Round number dưới
- = Nơi SM có thể sweep XUỐNG trước khi mua

## Ứng Dụng Trading

### Xác định TP (Take Profit)
- Nếu BUY → TP tại BSL gần nhất (nơi giá hướng tới)
- Nếu SELL → TP tại SSL gần nhất

### Xác định Sweep Target
- Vùng density CAO nhất = target sweep tiếp theo
- Sau khi sweep một bên → giá hướng sang bên kia

### Trading Flow
```
1. Mở Heatmap → xem BSL và SSL
2. Giá sweep SSL (đáy) → chuẩn bị BUY
3. Entry BUY tại OB + FVG sau sweep
4. TP = BSL gần nhất (đỉnh có liquidity)
```

→ Signal Scout app có tính năng Heatmap tại /heatmap/{symbol}!""",
        "key_points": [
            "Giá luôn hướng về nơi có NHIỀU liquidity nhất",
            "BSL (trên giá) = SL shorts, SSL (dưới giá) = SL longs",
            "Density score cao = nhiều orders → giá có thể hướng tới",
            "Sau sweep 1 bên → giá hướng sang bên kia → set TP ở đó",
            "Liquidity Heatmap = bản đồ dự đoán nơi giá sẽ di chuyển"
        ],
        "xp": 25, "estimated_minutes": 10,
    },

    # ══════════════ BOS (2 lessons) ══════════════
    {
        "id": "bos_01", "category": "bos", "order": 1,
        "title": "BOS & CHoCH — Phá Vỡ Cấu Trúc",
        "description": "BOS = trend tiếp tục, CHoCH = đảo chiều — 2 tín hiệu quan trọng nhất SMC.",
        "content": """# Break of Structure (BOS) & Change of Character (CHoCH)

## BOS = Break of Structure (Phá vỡ cấu trúc)

BOS xảy ra khi giá phá vỡ swing high/low **THEO HƯỚNG** trend hiện tại.

### Bullish BOS
```
                    ┌── BOS! (phá swing high trước đó)
                   ↗|
          HL₂     / |
            \\   /   |
             \\ /    | → Trend TIẾP TỤC tăng
          HH₁     
```
- Giá phá **swing high** trước đó
- Confirm uptrend vẫn intact
- → Tìm setup BUY tại pullback

### Bearish BOS  
```
          LL₁
            /\\
           /  \\   LH₂
          /    \\ /
         /      ↘
        |       → BOS! (phá swing low trước đó)
```
- Giá phá **swing low** trước đó
- Confirm downtrend vẫn intact
- → Tìm setup SELL tại pullback

## CHoCH = Change of Character (Thay đổi tính chất)

CHoCH xảy ra khi giá phá **NGƯỢC HƯỚNG** trend → cảnh báo đảo chiều.

### Bullish CHoCH (Downtrend → Uptrend)
```
LH₁
  \\
   \\    
    \\ /  ← CHoCH! (giá phá LH = không còn lower high)
  LL₁  → Downtrend bị phá vỡ → chuẩn bị uptrend
```

### Bearish CHoCH (Uptrend → Downtrend)
```
        HH₁
       /
      /    
     /  \\  ← CHoCH! (giá phá HL = không còn higher low)
    HL₁  → Uptrend bị phá vỡ → chuẩn bị downtrend
```

## So Sánh BOS vs CHoCH

| | BOS | CHoCH |
|-|-----|-------|
| Hướng | CÙNG trend | NGƯỢC trend |
| Ý nghĩa | Trend tiếp tục | Trend đảo chiều |
| Hành động | Trade THEO trend | Đợi confirm + đổi bias |
| Độ tin cậy | Cao | Rất cao (khi confirmed) |

## Trading BOS
1. BOS xảy ra → trend confirmed
2. Tìm OB trước BOS
3. Entry khi giá retest OB
4. SL ngoài OB, TP = swing tiếp theo""",
        "key_points": [
            "BOS = phá swing point CÙNG hướng trend → trend tiếp tục",
            "CHoCH = phá swing point NGƯỢC hướng → cảnh báo đảo chiều",
            "BOS + OB retest = entry setup chuẩn SMC",
            "1 CHoCH trên M15 chưa đủ → cần confirm trên H1 để chắc",
            "BOS trên TF lớn (H4/D1) quan trọng hơn TF nhỏ (M5/M15)"
        ],
        "xp": 30, "estimated_minutes": 12,
    },

    # ══════════════ FVG (2 lessons) ══════════════
    {
        "id": "fvg_01", "category": "fvg", "order": 1,
        "title": "Fair Value Gap (FVG) — Khoảng Trống Giá",
        "description": "Vùng mất cân bằng cung/cầu — nơi giá thường quay lại lấp.",
        "content": """# Fair Value Gap (FVG)

## FVG là gì?
FVG = khoảng trống giữa **High của nến 1** và **Low của nến 3**, nơi nến 2 di chuyển quá nhanh.

## Bullish FVG (Imbalance tăng) 🟢
```
Nến 3: ┌──┤  High₃
       └──┤  Low₃
                    ← GAP (FVG) = Low₃ > High₁
Nến 2: ┌──────┤   (nến tăng mạnh)
       └──────┤

Nến 1:    ├──┐  High₁
           └──┘  Low₁
```
- **FVG zone** = từ High nến 1 đến Low nến 3
- Giá thường quay lại lấp gap → **ĐIỂM BUY**
- Entry tốt nhất: midpoint FVG (50%)

## Bearish FVG (Imbalance giảm) 🔴
```
Nến 1:    ├──┐  High₁
           └──┘  Low₁
                    ← GAP (FVG) = High₃ < Low₁
Nến 2: ┌──────┤   (nến giảm mạnh)
       └──────┤

Nến 3: ┌──┤  High₃
       └──┤  Low₃
```
- **FVG zone** = từ Low nến 1 đến High nến 3
- Giá quay lại lấp → **ĐIỂM SELL**

## FVG Chất Lượng

### FVG Mạnh ✅
- Tạo bởi impulsive candle (thân dài, ít bóng)
- Kèm theo BOS
- Chưa được fill (mitigate)
- Overlap với OB = COMBO

### FVG Yếu ❌
- Tạo bởi tin tức (spike nhanh, chỉ wick)
- Đã được fill rồi
- Nhỏ so với ATR

## Cách Trade FVG
```
1. Xác định FVG trên M15/H1 (sau impulsive move)
2. Đánh dấu zone (High nến 1 → Low nến 3)
3. Đợi giá pullback về FVG
4. Entry tại MIDPOINT (50% của FVG)
5. SL: ngoài edge FVG
6. TP: swing high/low tiếp theo

Entry tốt nhất: FVG + OB overlap = "Mitigation Block"  
```

## FVG Mitigation
- Khi giá quay lại lấp FVG = MITIGATE
- FVG đã mitigate = MẤT hiệu lực, không entry lần 2
- Chỉ trade FVG lần CHẠM ĐẦU TIÊN""",
        "key_points": [
            "FVG = gap giữa High nến 1 và Low nến 3, nơi nến 2 chạy quá nhanh",
            "Bullish FVG: Low₃ > High₁ → demand gap → BUY khi giá quay lại",
            "Entry tốt nhất tại midpoint (50%) của FVG",
            "FVG + OB overlap = Mitigation Block = xác suất thành công rất cao",
            "FVG chỉ trade lần CHẠM ĐẦU TIÊN — sau khi mitigate thì mất hiệu lực"
        ],
        "xp": 30, "estimated_minutes": 12,
    },
]

# ══════════════════════════════════════════════════════════
# EXTENDED PATTERNS (12 patterns)
# ══════════════════════════════════════════════════════════

PATTERNS_FULL = [
    {"id": "doji", "name": "Doji", "type": "neutral",
     "description": "Thân nến cực nhỏ (Open ≈ Close). Thể hiện sự do dự giữa buyer và seller. Cần xem context và nến tiếp theo để xác nhận hướng đi.",
     "when": "Tại đỉnh/đáy trend, tại vùng S/R quan trọng, sau chuỗi nến mạnh",
     "signal": "Cảnh báo đảo chiều tiềm năng — KHÔNG trade Doji đơn lẻ, luôn đợi confirmation",
     "tips": ["Doji tại S/R = reversal signal mạnh", "Doji + Engulfing = combo tuyệt vời", "Volume thấp kèm Doji = do dự thực sự", "Nhiều Doji liên tiếp = sắp big move"],
     "visual": "  │\n  ·  ← Open ≈ Close\n  │"},
    {"id": "hammer", "name": "Hammer", "type": "bullish",
     "description": "Bóng dưới dài ≥ 2x thân, thân nhỏ ở phía trên. Buyer đã reject giá thấp — tín hiệu đảo chiều tăng mạnh tại support.",
     "when": "Cuối downtrend, tại support/demand zone, sau 3-5 nến giảm liên tiếp",
     "signal": "Bullish reversal — buyer từ chối để giá giảm thêm, sẵn sàng đẩy giá lên",
     "tips": ["Bóng dưới ≥ 2x thân nến", "Màu nến không quan trọng (xanh tốt hơn)", "LUÔN đợi nến tăng confirmation", "SL đặt dưới low của hammer"],
     "visual": "  ┌┐\n  ││\n  └┘\n   │\n   │\n   │"},
    {"id": "inverted_hammer", "name": "Inverted Hammer", "type": "bullish",
     "description": "Bóng trên dài, thân nhỏ ở dưới. Giống Shooting Star nhưng ở cuối DOWNTREND → bullish signal.",
     "when": "Cuối downtrend, tại support", "signal": "Bullish reversal — attempts tăng giá bắt đầu",
     "tips": ["Cần confirmation mạnh hơn Hammer", "Nến tiếp theo phải engulf thân", "Volume cao = đáng tin hơn"],
     "visual": "   │\n   │\n   │\n  ┌┐\n  ││\n  └┘"},
    {"id": "shooting_star", "name": "Shooting Star", "type": "bearish",
     "description": "Bóng trên dài ≥ 2x thân, thân nhỏ ở dưới. Seller reject giá cao — đảo chiều giảm.",
     "when": "Cuối uptrend, tại resistance/supply zone, sau chuỗi tăng",
     "signal": "Bearish reversal — seller từ chối để giá tăng thêm",
     "tips": ["Bóng trên ≥ 2x thân", "Tại resistance = rất mạnh", "Đợi nến giảm confirmation", "SL trên high shooting star"],
     "visual": "   │\n   │\n   │\n  ┌┐\n  ││\n  └┘"},
    {"id": "hanging_man", "name": "Hanging Man", "type": "bearish",
     "description": "Hình dạng giống Hammer nhưng xuất hiện cuối UPTREND → bearish warning signal.",
     "when": "Cuối uptrend, tại resistance", "signal": "Bearish reversal — selling pressure bắt đầu",
     "tips": ["Giống Hammer nhưng ở đỉnh trend", "Cần nến giảm xác nhận", "Không mạnh bằng Shooting Star", "Volume quan trọng"],
     "visual": "  ┌┐\n  ││\n  └┘\n   │\n   │\n   │"},
    {"id": "bullish_engulfing", "name": "Bullish Engulfing", "type": "bullish",
     "description": "Nến tăng lớn bao trùm HOÀN TOÀN thân nến giảm trước đó. 1 trong những pattern đảo chiều mạnh nhất.",
     "when": "Cuối downtrend, tại support/demand/OB, sau chuỗi giảm",
     "signal": "Strong bullish reversal — buyer chiếm quyền kiểm soát hoàn toàn",
     "tips": ["Thân nến 2 phải bao trùm HOÀN TOÀN thân nến 1", "Volume nến 2 phải > nến 1", "Tại OB/FVG = setup cực mạnh", "RR tối thiểu 1:2"],
     "visual": "  ┌┐ ← Bearish nhỏ\n  └┘\n┌──┐\n│  │ ← Bullish LỚN\n└──┘"},
    {"id": "bearish_engulfing", "name": "Bearish Engulfing", "type": "bearish",
     "description": "Nến giảm lớn bao trùm hoàn toàn thân nến tăng. Đảo chiều giảm tại resistance/supply.",
     "when": "Cuối uptrend, tại resistance/supply zone",
     "signal": "Strong bearish reversal — seller chiếm quyền kiểm soát",
     "tips": ["Ngược lại bullish engulfing", "+ Sweep (wick quá đỉnh) = siêu mạnh", "Volume xác nhận", "Tại supply/OB = A+ setup"],
     "visual": "┌──┐\n│  │ ← Bearish LỚN\n└──┘\n  ┌┐ ← Bullish nhỏ\n  └┘"},
    {"id": "morning_star", "name": "Morning Star", "type": "bullish",
     "description": "Mô hình 3 nến: Bearish lớn → Doji/nhỏ (do dự) → Bullish lớn. Đáng tin cậy nhất.",
     "when": "Cuối downtrend, tại support mạnh, trên TF H1/H4/D1 càng tốt",
     "signal": "Strong bullish reversal — 1 trong những patterns đáng tin nhất trong technical analysis",
     "tips": ["Nến 3 close > 50% nến 1", "Gap giữa nến 1-2 tăng độ tin cậy", "Volume nến 3 cao", "TF lớn hơn = đáng tin hơn"],
     "visual": "┌┐\n││ ← Bear\n└┘\n  · ← Doji\n ┌┐\n ││ ← Bull\n └┘"},
    {"id": "evening_star", "name": "Evening Star", "type": "bearish",
     "description": "Mô hình 3 nến: Bullish lớn → Doji/nhỏ → Bearish lớn. Đảo chiều giảm đáng tin nhất.",
     "when": "Cuối uptrend, tại resistance mạnh",
     "signal": "Strong bearish reversal — momentum tăng đã cạn kiệt",
     "tips": ["Ngược lại Morning Star", "Nến 3 close < 50% nến 1", "Gap = tín hiệu mạnh hơn"],
     "visual": " ┌┐\n ││ ← Bull\n └┘\n  · ← Doji\n┌┐\n││ ← Bear\n└┘"},
    {"id": "three_soldiers", "name": "Three White Soldiers", "type": "bullish",
     "description": "3 nến tăng liên tiếp, mỗi nến close CAO hơn nến trước, thân dài, ít bóng.",
     "when": "Cuối downtrend hoặc đầu uptrend mới",
     "signal": "Bullish continuation rất mạnh — trend tăng bắt đầu hoặc tiếp tục",
     "tips": ["3 nến thân dài, ít bóng trên", "Mỗi nến open trong thân nến trước", "Volume tăng dần = tốt nhất", "Cảnh giác nếu RSI > 70 (overbought)"],
     "visual": "      ┌┐\n    ┌┐││\n  ┌┐││││\n  ││││││\n  └┘└┘└┘"},
    {"id": "three_crows", "name": "Three Black Crows", "type": "bearish",
     "description": "3 nến giảm liên tiếp, mỗi nến close THẤP hơn nến trước. Downtrend mạnh.",
     "when": "Cuối uptrend hoặc đầu downtrend mới",
     "signal": "Bearish continuation mạnh — selling pressure rất lớn",
     "tips": ["Ngược lại Three Soldiers", "Volume cao = xác nhận", "Sau long uptrend = reversal mạnh"],
     "visual": "  ┌┐\n  ││┌┐\n  ││││┌┐\n  ││││││\n  └┘└┘└┘"},
    {"id": "pin_bar", "name": "Pin Bar", "type": "neutral",
     "description": "Nến có bóng dài ≥ 3x thân, thể hiện rejection mạnh. Bullish/Bearish tuỳ vị trí.",
     "when": "Tại S/R quan trọng, sau sweep liquidity",
     "signal": "Strong rejection — tại support = bullish, tại resistance = bearish",
     "tips": ["Bóng ≥ 3x thân mới gọi là Pin Bar", "Pin Bar sau sweep = setup A+", "Cần context — tại S/R mới có ý nghĩa", "Combo với OB/FVG = entry chính xác"],
     "visual": "   │\n   │\n   │ ← Bóng rất dài\n  ┌┐\n  └┘ ← Thân nhỏ"},
]

# ══════════════════════════════════════════════════════════
# EXTENDED QUIZZES (25 questions)
# ══════════════════════════════════════════════════════════

QUIZZES_FULL = [
    {"id": "q01", "category": "basics", "difficulty": "easy",
     "question": "1 pip của EUR/USD = bao nhiêu?",
     "options": ["A. 0.01", "B. 0.001", "C. 0.0001", "D. 0.00001"],
     "correct": 2, "xp": 5,
     "explanation": "1 pip EUR/USD = 0.0001. Với 1 standard lot (100,000 units), 1 pip = $10."},
    {"id": "q02", "category": "basics", "difficulty": "easy",
     "question": "Phiên giao dịch nào có biến động (volume) lớn nhất?",
     "options": ["A. Asia (Tokyo)", "B. London", "C. New York", "D. Sydney"],
     "correct": 1, "xp": 5,
     "explanation": "Phiên London có volume và biến động lớn nhất. Overlap London-NY (19:00-23:00 VN) là thời điểm tốt nhất."},
    {"id": "q03", "category": "candles", "difficulty": "easy",
     "question": "Hammer xuất hiện cuối downtrend cho tín hiệu gì?",
     "options": ["A. Sell", "B. Buy (đảo chiều tăng)", "C. Tiếp tục giảm", "D. Không ý nghĩa"],
     "correct": 1, "xp": 5,
     "explanation": "Hammer có bóng dưới dài, cho thấy buyer reject giá thấp. Tại cuối downtrend = tín hiệu đảo chiều tăng."},
    {"id": "q04", "category": "candles", "difficulty": "medium",
     "question": "Morning Star là mô hình bao nhiêu nến?",
     "options": ["A. 1 nến", "B. 2 nến", "C. 3 nến", "D. 4 nến"],
     "correct": 2, "xp": 10,
     "explanation": "Morning Star = 3 nến: Bearish lớn → Doji/nhỏ (do dự) → Bullish lớn (đảo chiều)."},
    {"id": "q05", "category": "risk", "difficulty": "easy",
     "question": "Tối đa bao nhiêu % vốn nên rủi ro cho 1 lệnh?",
     "options": ["A. 5%", "B. 10%", "C. 1-2%", "D. Không giới hạn"],
     "correct": 2, "xp": 5,
     "explanation": "Quy tắc vàng: max 1-2% vốn/lệnh. $10,000 → max risk $100-$200/lệnh."},
    {"id": "q06", "category": "risk", "difficulty": "medium",
     "question": "RR 1:2 nghĩa là gì?",
     "options": ["A. Rủi ro gấp đôi lợi nhuận", "B. Lợi nhuận gấp đôi rủi ro", "C. Win rate 50%", "D. Lot x2"],
     "correct": 1, "xp": 10,
     "explanation": "RR 1:2 = nếu risk $100 (SL), target lợi nhuận = $200 (TP). Chỉ cần win rate > 33% để profitable."},
    {"id": "q07", "category": "risk", "difficulty": "medium",
     "question": "Với RR 1:2, win rate tối thiểu cần thiết để profitable?",
     "options": ["A. 50%", "B. 40%", "C. > 33%", "D. 25%"],
     "correct": 2, "xp": 10,
     "explanation": "RR 1:2 → chỉ cần thắng 1/3 lệnh (>33%). Ví dụ: 34 thắng x $200 = $6,800, 66 thua x $100 = $6,600 → profit $200."},
    {"id": "q08", "category": "structure", "difficulty": "easy",
     "question": "Uptrend được xác định bởi?",
     "options": ["A. LH + LL", "B. HH + HL", "C. EMA cross", "D. RSI > 50"],
     "correct": 1, "xp": 5,
     "explanation": "Uptrend = Higher Highs + Higher Lows (HH + HL). Đỉnh sau cao hơn đỉnh trước, đáy sau cao hơn đáy trước."},
    {"id": "q09", "category": "structure", "difficulty": "medium",
     "question": "Khi giá đi ngang không tạo HH/HL hay LH/LL, bạn nên?",
     "options": ["A. Buy", "B. Sell", "C. Không trade / đợi breakout", "D. Scalp"],
     "correct": 2, "xp": 10,
     "explanation": "Sideways = không có trend. Tốt nhất KHÔNG trade hoặc chỉ trade bouncing S/R trong range, đợi breakout."},
    {"id": "q10", "category": "sr", "difficulty": "easy",
     "question": "Khi Resistance bị phá, nó trở thành gì?",
     "options": ["A. Vẫn Resistance", "B. Support", "C. FVG", "D. Order Block"],
     "correct": 1, "xp": 5,
     "explanation": "Role Reversal: Resistance bị phá → trở thành Support. Giá thường retest vùng này trước khi tiếp tục."},
    {"id": "q11", "category": "trend", "difficulty": "medium",
     "question": "Golden Cross xảy ra khi?",
     "options": ["A. EMA ngắn cắt XUỐNG EMA dài", "B. EMA ngắn cắt LÊN EMA dài", "C. RSI > 70", "D. Price = EMA"],
     "correct": 1, "xp": 10,
     "explanation": "Golden Cross = EMA ngắn (9) cắt LÊN EMA dài (21) → Buy signal. Death Cross = ngược lại."},
    {"id": "q12", "category": "trend", "difficulty": "medium",
     "question": "ADX > 40 cho biết điều gì?",
     "options": ["A. Không có trend", "B. Trend yếu", "C. Trend MẠNH", "D. Thị trường đóng"],
     "correct": 2, "xp": 10,
     "explanation": "ADX đo sức mạnh trend: <20 = no trend, 20-40 = moderate, >40 = strong trend. ADX KHÔNG chỉ hướng."},
    {"id": "q13", "category": "smc", "difficulty": "medium",
     "question": "AMD pattern trong SMC là viết tắt của gì?",
     "options": ["A. Analysis-Market-Decision", "B. Accumulation-Manipulation-Distribution", "C. Average-Moving-Dynamic", "D. Asset-Money-Derivative"],
     "correct": 1, "xp": 10,
     "explanation": "AMD = Accumulation (tích lũy) → Manipulation (sweep/trap) → Distribution (real move). Mẫu entry chính của SMC."},
    {"id": "q14", "category": "smc", "difficulty": "hard",
     "question": "Order Block (OB) là gì?",
     "options": ["A. Vùng S/R cổ điển", "B. Nến cuối cùng ngược chiều trước BOS", "C. EMA convergence", "D. Volume cluster"],
     "correct": 1, "xp": 15,
     "explanation": "OB = nến cuối cùng đi NGƯỢC CHIỀU trước khi xảy ra Break of Structure. Nơi institutions đặt lệnh lớn."},
    {"id": "q15", "category": "smc", "difficulty": "hard",
     "question": "Liquidity Sweep xảy ra khi?",
     "options": ["A. Breakout thành công", "B. Giá spike qua equal highs/lows rồi đảo chiều", "C. Volume giảm", "D. EMA cross"],
     "correct": 1, "xp": 15,
     "explanation": "Sweep = SM đẩy giá qua vùng SL (equal highs/lows) để grab liquidity, rồi đảo chiều. Đây KHÔNG phải breakout thật."},
    {"id": "q16", "category": "bos", "difficulty": "medium",
     "question": "BOS và CHoCH khác nhau thế nào?",
     "options": ["A. BOS = đảo chiều, CHoCH = tiếp tục", "B. BOS = tiếp tục trend, CHoCH = đảo chiều", "C. Giống nhau", "D. BOS mạnh hơn"],
     "correct": 1, "xp": 10,
     "explanation": "BOS = phá swing CÙNG hướng trend (tiếp tục). CHoCH = phá swing NGƯỢC hướng (cảnh báo đảo chiều)."},
    {"id": "q17", "category": "fvg", "difficulty": "hard",
     "question": "Fair Value Gap (FVG) hình thành bởi?",
     "options": ["A. 2 nến liên tiếp", "B. Gap giữa High nến 1 và Low nến 3", "C. EMA cross", "D. Volume gap"],
     "correct": 1, "xp": 15,
     "explanation": "FVG = khoảng trống giữa High nến 1 và Low nến 3, nơi nến 2 di chuyển quá nhanh. Giá thường quay lại lấp."},
    {"id": "q18", "category": "fvg", "difficulty": "hard",
     "question": "Entry tốt nhất tại FVG là ở đâu?",
     "options": ["A. Edge trên", "B. Edge dưới", "C. Midpoint (50%)", "D. Ngoài FVG"],
     "correct": 2, "xp": 15,
     "explanation": "Entry tối ưu tại MIDPOINT (50%) của FVG. Cho SL hẹp hơn và RR tốt hơn so với entry tại edge."},
    {"id": "q19", "category": "liquidity", "difficulty": "medium",
     "question": "Equal Highs chứa loại liquidity gì?",
     "options": ["A. SSL (Sell Side)", "B. BSL (Buy Side)", "C. Không có liquidity", "D. FVG"],
     "correct": 1, "xp": 10,
     "explanation": "Equal Highs = BSL (Buy Side Liquidity). SL của shorts nằm ở trên equal highs → SM sweep lên để grab liquidity."},
    {"id": "q20", "category": "risk", "difficulty": "hard",
     "question": "Sau 2 lệnh thua liên tiếp, hành động đúng nhất?",
     "options": ["A. Gấp đôi lot để gỡ", "B. Tiếp tục trade bình thường", "C. Dừng lại, review, nghỉ ngơi", "D. Chuyển cặp tiền khác"],
     "correct": 2, "xp": 15,
     "explanation": "Sau 2 thua liên tiếp → BẮT BUỘC dừng lại. Review journal, kiểm tra setup, nghỉ ít nhất vài giờ. Revenge trading = con đường nhanh nhất cháy tài khoản."},
    {"id": "q21", "category": "basics", "difficulty": "medium",
     "question": "MTF Analysis nên bắt đầu từ TF nào?",
     "options": ["A. M1 (nhỏ nhất)", "B. D1/H4 (lớn nhất)", "C. M15", "D. Tuỳ ý"],
     "correct": 1, "xp": 10,
     "explanation": "MTF = Top-Down: bắt đầu từ TF LỚN (D1/H4) xác định trend, xuống TF trung (H1) tìm zone, và TF nhỏ (M15) timing entry."},
    {"id": "q22", "category": "candles", "difficulty": "medium",
     "question": "Bearish Engulfing mạnh nhất khi xuất hiện tại?",
     "options": ["A. Giữa range", "B. Support", "C. Resistance/Supply zone", "D. Bất kỳ đâu"],
     "correct": 2, "xp": 10,
     "explanation": "Bearish Engulfing mạnh nhất tại resistance/supply zone. Nếu có sweep (wick vượt đỉnh) trước engulfing = A+ setup."},
    {"id": "q23", "category": "smc", "difficulty": "hard",
     "question": "OB + FVG overlap được gọi là gì?",
     "options": ["A. Confluence Zone", "B. Mitigation Block", "C. Breaker Block", "D. Fair Value Block"],
     "correct": 1, "xp": 15,
     "explanation": "OB + FVG overlap = Mitigation Block. Đây là vùng entry có xác suất thành công CAO NHẤT trong SMC methodology."},
    {"id": "q24", "category": "trend", "difficulty": "easy",
     "question": "RSI < 30 cho biết điều gì?",
     "options": ["A. Overbought", "B. Oversold", "C. No trend", "D. Breakout"],
     "correct": 1, "xp": 5,
     "explanation": "RSI < 30 = Oversold (quá bán). Giá CÓ THỂ đảo chiều tăng, nhưng cần confirmation. RSI > 70 = Overbought (quá mua)."},
    {"id": "q25", "category": "liquidity", "difficulty": "hard",
     "question": "Sau khi SM sweep SSL (đáy), giá thường?",
     "options": ["A. Tiếp tục giảm", "B. Đảo chiều tăng mạnh", "C. Đi ngang", "D. Không đoán được"],
     "correct": 1, "xp": 15,
     "explanation": "Sau sweep SSL (đáy): SM grab liquidity (SL longs) → có đủ liquidity để BUY → giá đảo chiều tăng. Entry BUY tại OB/FVG sau sweep."},
]
