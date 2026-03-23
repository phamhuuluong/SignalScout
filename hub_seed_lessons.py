"""
hub_seed_lessons.py — Seed 10 best trading lessons (bilingual VI/EN)
Run: python3 hub_seed_lessons.py
"""
import json
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from hub_database import init_db, SessionLocal, Lesson
from datetime import datetime

def seed():
    init_db()
    db = SessionLocal()

    lessons = [
        # ── Category: smc ──────────────────────────────────────────────────
        {
            "id": "smc_01",
            "category": "smc",
            "order": 1,
            "title": json.dumps({"vi": "Order Block (OB) là gì?", "en": "What is an Order Block (OB)?"}),
            "description": json.dumps({
                "vi": "Hiểu cách Smart Money đặt lệnh khổng lồ và để lại dấu vết trên chart",
                "en": "Understand how Smart Money places massive orders and leaves footprints on the chart"
            }),
            "content": json.dumps({
                "vi": """Order Block (OB) là vùng giá nơi các tổ chức tài chính lớn (Smart Money) đặt lệnh khối lượng lớn.

**Cách nhận biết Order Block:**
• **Bearish OB**: Nến tăng cuối cùng trước khi giá giảm mạnh
• **Bullish OB**: Nến giảm cuối cùng trước khi giá tăng mạnh
• Thường có volume lớn hơn bình thường

**Cách trade OB:**
1. Xác định xu hướng HTF (H4, Daily)
2. Tìm Order Block trên LTF (M15, H1)
3. Chờ giá retest về vùng OB
4. Vào lệnh với SL phía sau OB
5. TP tối thiểu 1:2 RR

**Lưu ý quan trọng:**
• OB chỉ valid khi giá chưa quay lại "mitigate" (lấp đầy) vùng đó
• Kết hợp với FVG để tăng độ chính xác
• Không vào lệnh khi OB đã bị test nhiều lần""",
                "en": """An Order Block (OB) is a price zone where large financial institutions (Smart Money) place massive orders.

**How to identify Order Blocks:**
• **Bearish OB**: Last bullish candle before a strong price drop
• **Bullish OB**: Last bearish candle before a strong price rally
• Usually has higher than average volume

**How to trade OBs:**
1. Identify HTF trend (H4, Daily)
2. Find Order Block on LTF (M15, H1)
3. Wait for price to retest the OB zone
4. Enter with SL behind the OB
5. TP minimum 1:2 RR

**Important notes:**
• OB is only valid if price hasn't returned to "mitigate" (fill) the zone
• Combine with FVG for better accuracy
• Don't enter when OB has been tested multiple times"""
            }),
            "quiz_json": json.dumps([
                {
                    "q": {"vi": "Bearish Order Block là gì?", "en": "What is a Bearish Order Block?"},
                    "options": {
                        "vi": ["Nến giảm cuối trước khi tăng", "Nến tăng cuối trước khi giảm mạnh", "Vùng giá bất kỳ có volume cao", "Điểm pivot cao nhất"],
                        "en": ["Last bearish candle before rally", "Last bullish candle before strong drop", "Any high volume price zone", "The highest pivot point"]
                    },
                    "answer": 1,
                    "explanation": {"vi": "Bearish OB = nến tăng cuối cùng trước khi Smart Money bán mạnh", "en": "Bearish OB = last bullish candle before Smart Money sold aggressively"}
                }
            ]),
            "xp": 20,
            "minutes": 8,
            "premium": False,
        },
        {
            "id": "smc_02",
            "category": "smc",
            "order": 2,
            "title": json.dumps({"vi": "Fair Value Gap (FVG) — Khoảng trống thanh khoản", "en": "Fair Value Gap (FVG) — Liquidity Gap"}),
            "description": json.dumps({
                "vi": "FVG là khoảng trống giá phát sinh khi Smart Money di chuyển giá quá nhanh",
                "en": "FVG is a price gap created when Smart Money moves price too fast"
            }),
            "content": json.dumps({
                "vi": """Fair Value Gap (FVG) xuất hiện khi 3 nến liên tiếp tạo ra một khoảng trống không chồng chéo.

**Cách xác định FVG:**
• Nến 1 có High/Low nhất định
• Nến 2 di chuyển mạnh (impulse)
• Nến 3 có Low/High không chạm đến High/Low của nến 1

**Bullish FVG:**
Low nến 3 > High nến 1 → Có gap ở giữa → Giá sẽ quay về lấp đầy

**Bearish FVG:**
High nến 3 < Low nến 1 → Có gap ở giữa → Giá sẽ quay về lấp đầy

**Chiến lược:**
• Vào BUY khi giá fill vào Bullish FVG (50% của gap)
• SL: Dưới body FVG
• TP: Đỉnh swing gần nhất

**Tip nâng cao:** FVG nằm trong Order Block = xác suất cao nhất!""",
                "en": """Fair Value Gap (FVG) appears when 3 consecutive candles create a non-overlapping gap.

**How to identify FVG:**
• Candle 1 has a specific High/Low
• Candle 2 moves strongly (impulse)  
• Candle 3's Low/High doesn't touch Candle 1's High/Low

**Bullish FVG:**
Candle 3 Low > Candle 1 High → Gap exists → Price will return to fill it

**Bearish FVG:**
Candle 3 High < Candle 1 Low → Gap exists → Price will return to fill it

**Strategy:**
• Enter BUY when price fills into Bullish FVG (50% of gap)
• SL: Below FVG body
• TP: Nearest swing high

**Advanced tip:** FVG inside an Order Block = highest probability!"""
            }),
            "quiz_json": json.dumps([
                {
                    "q": {"vi": "FVG (bullish) được xác nhận khi:", "en": "A Bullish FVG is confirmed when:"},
                    "options": {
                        "vi": ["3 nến tăng liên tiếp", "Low nến 3 > High nến 1", "Volume nến 2 rất cao", "RSI > 70"],
                        "en": ["3 consecutive bullish candles", "Candle 3 Low > Candle 1 High", "Candle 2 has very high volume", "RSI > 70"]
                    },
                    "answer": 1,
                    "explanation": {"vi": "Bullish FVG = Low(nến 3) > High(nến 1) — có khoảng trống không chồng chéo", "en": "Bullish FVG = Low(candle 3) > High(candle 1) — non-overlapping gap exists"}
                }
            ]),
            "xp": 20,
            "minutes": 7,
            "premium": False,
        },
        {
            "id": "smc_03",
            "category": "smc",
            "order": 3,
            "title": json.dumps({"vi": "BOS & CHoCH — Cấu trúc thị trường", "en": "BOS & CHoCH — Market Structure"}),
            "description": json.dumps({
                "vi": "Phân biệt Break of Structure vs Change of Character để xác định trend",
                "en": "Distinguish Break of Structure vs Change of Character to identify trends"
            }),
            "content": json.dumps({
                "vi": """**Break of Structure (BOS)** — Tiếp diễn xu hướng
Xảy ra khi giá phá vỡ swing high/low trong xu hướng hiện tại.

Uptrend: BOS = phá vỡ Higher High trước → Trend tiếp tục tăng
Downtrend: BOS = phá vỡ Lower Low trước → Trend tiếp tục giảm

**Change of Character (CHoCH)** — Dấu hiệu đảo chiều
Xảy ra khi giá phá vỡ swing ngược chiều xu hướng LẦN ĐẦU TIÊN.

Trong uptrend: CHoCH = phá vỡ Higher Low → Cảnh báo trend sắp đảo
Trong downtrend: CHoCH = phá vỡ Lower High → Cảnh báo đảo chiều lên

**Thứ tự xác nhận:**
1. Xem HTF (Daily, H4) để biết trend chính
2. Dùng LTF (M15, H1) tìm CHoCH → BOS để xác nhận
3. CHoCH xuất hiện: chưa vào lệnh, cảnh giác
4. BOS theo hướng mới: xác nhận đảo chiều, tìm điểm vào""",
                "en": """**Break of Structure (BOS)** — Trend Continuation
Occurs when price breaks a swing high/low in the current trend direction.

Uptrend: BOS = breaks previous Higher High → Trend continues up
Downtrend: BOS = breaks previous Lower Low → Trend continues down

**Change of Character (CHoCH)** — Reversal Signal
Occurs when price breaks a swing point COUNTER to the current trend FOR THE FIRST TIME.

In uptrend: CHoCH = breaks Higher Low → Warning of potential reversal
In downtrend: CHoCH = breaks Lower High → Warning of reversal to upside

**Confirmation sequence:**
1. Check HTF (Daily, H4) for main trend
2. Use LTF (M15, H1) to find CHoCH → BOS for confirmation
3. CHoCH appears: don't enter yet, stay alert
4. BOS in new direction: reversal confirmed, look for entry"""
            }),
            "quiz_json": json.dumps([]),
            "xp": 25,
            "minutes": 10,
            "premium": False,
        },

        # ── Category: risk ─────────────────────────────────────────────────
        {
            "id": "risk_01",
            "category": "risk",
            "order": 1,
            "title": json.dumps({"vi": "Quy tắc 1% — Bảo toàn vốn tuyệt đối", "en": "The 1% Rule — Absolute Capital Preservation"}),
            "description": json.dumps({
                "vi": "Không bao giờ rủi ro quá 1% tài khoản cho 1 lệnh. Đây là quy tắc sống còn.",
                "en": "Never risk more than 1% of your account per trade. This is the survival rule."
            }),
            "content": json.dumps({
                "vi": """**Quy tắc 1% là gì?**
Mỗi lệnh chỉ được rủi ro tối đa 1% tổng tài khoản.

Tài khoản $10,000 → Rủi ro tối đa $100/lệnh
Tài khoản $1,000 → Rủi ro tối đa $10/lệnh

**Tại sao quan trọng:**
• Thua 10 lệnh liên tiếp: chỉ mất 10% tài khoản → Vẫn còn $9,000
• Nếu rủi ro 10%/lệnh: thua 10 lệnh liên tiếp → Mất 90% → Phá sản

**Công thức tính Lot Size:**
Lot Size = (Tài khoản × 1%) ÷ (Khoảng cách SL tính bằng pip × Pip value)

**Ví dụ XAUUSD:**
Tài khoản: $10,000
Rủi ro 1%: $100
SL: 20 pip (= $200 với lot 0.1)
→ Lot size = $100 ÷ ($200) × 0.1 = 0.05 lot

**Risk:Reward tối thiểu:**
• RR 1:2 → Chỉ cần thắng 40% là BEP
• RR 1:3 → Chỉ cần thắng 30% là có lãi
• KHÔNG bao giờ mở lệnh khi RR < 1:1.5""",
                "en": """**What is the 1% Rule?**
Each trade can only risk a maximum of 1% of total account.

$10,000 account → Max risk $100/trade
$1,000 account → Max risk $10/trade

**Why it matters:**
• Lose 10 trades in a row: only lose 10% → Still have $9,000
• If risking 10%/trade: lose 10 in a row → Lose 90% → Bankruptcy

**Lot Size formula:**
Lot Size = (Account × 1%) ÷ (SL distance in pips × Pip value)

**XAUUSD example:**
Account: $10,000
1% risk: $100
SL: 20 pips (= $200 with 0.1 lot)
→ Lot size = $100 ÷ ($200) × 0.1 = 0.05 lot

**Minimum Risk:Reward:**
• RR 1:2 → Only need 40% win rate to break even
• RR 1:3 → Only need 30% win rate to profit
• NEVER open a trade when RR < 1:1.5"""
            }),
            "quiz_json": json.dumps([
                {
                    "q": {"vi": "Tài khoản $5,000, áp dụng quy tắc 1%, mỗi lệnh rủi ro tối đa bao nhiêu?", "en": "Account $5,000, applying 1% rule, max risk per trade is?"},
                    "options": {
                        "vi": ["$50", "$100", "$500", "$5"],
                        "en": ["$50", "$100", "$500", "$5"]
                    },
                    "answer": 0,
                    "explanation": {"vi": "$5,000 × 1% = $50", "en": "$5,000 × 1% = $50"}
                }
            ]),
            "xp": 30,
            "minutes": 10,
            "premium": False,
        },
        {
            "id": "risk_02",
            "category": "risk",
            "order": 2,
            "title": json.dumps({"vi": "Tâm lý giao dịch — FOMO & Revenge Trading", "en": "Trading Psychology — FOMO & Revenge Trading"}),
            "description": json.dumps({
                "vi": "Đây là nguyên nhân chết 80% trader. Biết bệnh là bước đầu chữa bệnh.",
                "en": "This kills 80% of traders. Knowing the disease is the first step to curing it."
            }),
            "content": json.dumps({
                "vi": """**FOMO (Fear of Missing Out):**
Cảm giác sợ bỏ lỡ khi thấy giá đang chạy mạnh.

Triệu chứng:
• Nhảy vào lệnh khi nến đã chạy 50-100 pip
• Tăng lot size để "bù" lệnh bỏ lỡ
• Vào lệnh không có setup rõ ràng

Chữa bệnh:
• Luôn đặt câu hỏi: "Setup này có valid không?"
• Nhớ rằng: cơ hội sẽ luôn xuất hiện lại
• Tick lại checklist trước khi vào lệnh

**Revenge Trading:**
Mở lệnh ngay sau khi thua để "lấy lại tiền".

Triệu chứng:
• Thua 1-2 lệnh → tăng lot gấp đôi lần sau
• Mở nhiều lệnh cùng lúc để bù
• Không còn theo plan

Chữa bệnh:
• Quy tắc: Thua 2 lệnh liên tiếp → DỪNG ngay hôm đó
• Viết journal sau mỗi lệnh thua
• Trading là marathon, không phải sprint""",
                "en": """**FOMO (Fear of Missing Out):**
The feeling of fear when you see price running strongly.

Symptoms:
• Jumping in when the candle has already run 50-100 pips
• Increasing lot size to "compensate" for missed trade
• Entering trades without a clear setup

Cure:
• Always ask: "Is this setup valid?"
• Remember: opportunities will always come again
• Check your checklist before entering

**Revenge Trading:**
Opening a trade immediately after a loss to "get money back".

Symptoms:
• Lose 1-2 trades → double lot size on next trade
• Open multiple trades simultaneously to compensate
• No longer following the plan

Cure:
• Rule: Lose 2 consecutive trades → STOP for that day
• Write a journal after each losing trade
• Trading is a marathon, not a sprint"""
            }),
            "quiz_json": json.dumps([]),
            "xp": 25,
            "minutes": 8,
            "premium": False,
        },

        # ── Category: ict ──────────────────────────────────────────────────
        {
            "id": "ict_01",
            "category": "ict",
            "order": 1,
            "title": json.dumps({"vi": "Kill Zone — Giờ vàng giao dịch", "en": "Kill Zones — Golden Trading Hours"}),
            "description": json.dumps({
                "vi": "ICT Kill Zones là các khung giờ thanh khoản cao nhất trong ngày",
                "en": "ICT Kill Zones are the highest liquidity time windows during the day"
            }),
            "content": json.dumps({
                "vi": """ICT Kill Zones là những giờ vàng mà Smart Money di chuyển thị trường mạnh nhất.

**4 Kill Zones chính (giờ VN):**

🇨🇳 **Asian Session** (06:00 - 09:00)
• Thanh khoản thấp, giá đi sideways
• Smart Money tích lũy, quét stop loss
• Tránh trade (đặc biệt XAUUSD)

🇬🇧 **London Open** (15:00 - 17:00)
• Bắt đầu ngày trading châu Âu
• Volatility tăng mạnh
• Setup tốt cho EURUSD, GBPUSD, XAUUSD

⚡ **London-NY Overlap** (20:00 - 23:00)
• THỜI GIAN VÀNG — Volatility cao nhất
• Volume lớn nhất trong ngày
• Best setup cho tất cả pairs
• XAUUSD di chuyển 30-80 pip

🗽 **New York Close** (23:00 - 01:00)
• Đóng vị thế của traders Mỹ
• Có thể có spike bất ngờ
• Tránh mở lệnh mới

**Tip thực chiến:**
Tập trung 100% vào London-NY Overlap (20:00-23:00 VN).
Đây là lúc ATTRAOS Signal Radar hoạt động chính xác nhất.""",
                "en": """ICT Kill Zones are the golden hours when Smart Money moves markets the most.

**4 Main Kill Zones (Vietnam time):**

🇨🇳 **Asian Session** (06:00 - 09:00)
• Low liquidity, price moves sideways
• Smart Money accumulates, sweeps stop losses
• Avoid trading (especially XAUUSD)

🇬🇧 **London Open** (15:00 - 17:00)
• Start of European trading day
• Volatility increases strongly
• Good setups for EURUSD, GBPUSD, XAUUSD

⚡ **London-NY Overlap** (20:00 - 23:00)
• GOLDEN TIME — Highest volatility
• Highest volume of the day
• Best setups for all pairs
• XAUUSD moves 30-80 pips

🗽 **New York Close** (23:00 - 01:00)
• US traders closing positions
• Can have unexpected spikes
• Avoid opening new trades

**Practical tip:**
Focus 100% on London-NY Overlap (20:00-23:00 VN time).
This is when ATTRAOS Signal Radar is most accurate."""
            }),
            "quiz_json": json.dumps([
                {
                    "q": {"vi": "Kill Zone có volatility cao nhất trong ngày là:", "en": "The Kill Zone with highest volatility is:"},
                    "options": {
                        "vi": ["Asian Session (06:00-09:00)", "London Open (15:00-17:00)", "London-NY Overlap (20:00-23:00)", "Cuối tuần"],
                        "en": ["Asian Session (06:00-09:00)", "London Open (15:00-17:00)", "London-NY Overlap (20:00-23:00)", "Weekend"]
                    },
                    "answer": 2,
                    "explanation": {"vi": "London-NY Overlap là lúc 2 thị trường lớn nhất cùng mở → Volume và volatility cao nhất", "en": "London-NY Overlap is when the 2 biggest markets are both open → Highest volume and volatility"}
                }
            ]),
            "xp": 20,
            "minutes": 7,
            "premium": False,
        },
        {
            "id": "ict_02",
            "category": "ict",
            "order": 2,
            "title": json.dumps({"vi": "Liquidity — Thanh khoản & Khu vực sweep", "en": "Liquidity — Sweeps & Liquidity Zones"}),
            "description": json.dumps({
                "vi": "Hiểu cách Smart Money săn stop loss của retail traders trước khi đi đúng hướng",
                "en": "Understand how Smart Money hunts retail trader stop losses before moving in the real direction"
            }),
            "content": json.dumps({
                "vi": """**Liquidity là gì?**
Thanh khoản là nơi tập trung nhiều stop loss orders của traders. Smart Money cần thanh khoản này để fill lệnh lớn của họ.

**Nơi tích lũy Liquidity:**
• Đỉnh/đáy gần nhất (recent highs/lows)
• Vùng Equal Highs / Equal Lows
• Phía trên điểm kháng cự (buy-side liquidity)
• Phía dưới điểm hỗ trợ (sell-side liquidity)

**Liquidity Sweep:**
Smart Money đẩy giá vượt qua vùng liquidity để kích hoạt stop loss → Sau đó đảo chiều.

Ví dụ:
1. Retail traders đặt BUY với SL dưới vùng support
2. Smart Money đẩy giá xuống dưới support (sweep)
3. Kích hoạt toàn bộ SL → Có thanh khoản để fill lệnh BUY lớn
4. Giá bật tăng mạnh

**Cách trade:**
• Nhận biết vùng liquidity (Equal H/L, swing points)
• Chờ giá sweep → Tìm OB/FVG ngay sau sweep
• Vào lệnh ngược chiều sweep
• SL: Phía sau cây nến sweep đó""",
                "en": """**What is Liquidity?**
Liquidity is where many stop loss orders from traders are clustered. Smart Money needs this liquidity to fill their large orders.

**Where Liquidity Accumulates:**
• Recent highs/lows
• Equal Highs / Equal Lows zones
• Above resistance (buy-side liquidity)
• Below support (sell-side liquidity)

**Liquidity Sweep:**
Smart Money pushes price past liquidity zones to trigger stop losses → Then reverses direction.

Example:
1. Retail traders place BUY with SL below support
2. Smart Money pushes price below support (sweep)
3. All SLs triggered → Liquidity available to fill large BUY order
4. Price rallies strongly

**How to trade:**
• Identify liquidity zones (Equal H/L, swing points)
• Wait for price to sweep → Find OB/FVG immediately after sweep
• Enter trade opposite to sweep direction
• SL: Behind the sweep candle"""
            }),
            "quiz_json": json.dumps([]),
            "xp": 30,
            "minutes": 10,
            "premium": False,
        },

        # ── Category: basics ───────────────────────────────────────────────
        {
            "id": "basics_01",
            "category": "basics",
            "order": 1,
            "title": json.dumps({"vi": "Pip, Lot, Spread — Kiến thức nền tảng", "en": "Pip, Lot, Spread — Foundation Knowledge"}),
            "description": json.dumps({
                "vi": "Những khái niệm cơ bản bắt buộc phải biết trước khi trade",
                "en": "Basic concepts you must know before trading"
            }),
            "content": json.dumps({
                "vi": """**Pip là gì?**
Pip = đơn vị thay đổi giá nhỏ nhất (Percentage In Point)

EURUSD: 1 pip = 0.0001 (điểm thứ 4 sau dấu phẩy)
XAUUSD (Gold): 1 pip = 0.01 (điểm thứ 2 sau dấu phẩy)
USDJPY: 1 pip = 0.01 (điểm thứ 2 sau dấu phẩy)

**Lot Size:**
• 1 Standard Lot = 100,000 đơn vị tiền tệ cơ sở
• 0.1 Lot (Mini) = 10,000 đơn vị
• 0.01 Lot (Micro) = 1,000 đơn vị

Với XAUUSD:
• 0.01 lot = $0.1/pip
• 0.1 lot = $1/pip  
• 1.0 lot = $10/pip

**Spread là gì?**
Chênh lệch giữa giá mua (Ask) và giá bán (Bid).
Spread = phí giao dịch bạn trả cho broker.

XAUUSD spread thường: 20-40 pip (tiêu chuẩn)
Chọn broker spread thấp để giảm chi phí!

**Leverage (Đòn bẩy):**
Cho phép kiểm soát vị thế lớn hơn vốn thực.
Leverage 1:100 → $1,000 kiểm soát $100,000
⚠️ Đòn bẩy cao = Lợi nhuận cao = Rủi ro CAO""",
                "en": """**What is a Pip?**
Pip = smallest unit of price movement (Percentage In Point)

EURUSD: 1 pip = 0.0001 (4th decimal place)
XAUUSD (Gold): 1 pip = 0.01 (2nd decimal place)
USDJPY: 1 pip = 0.01 (2nd decimal place)

**Lot Size:**
• 1 Standard Lot = 100,000 base currency units
• 0.1 Lot (Mini) = 10,000 units
• 0.01 Lot (Micro) = 1,000 units

With XAUUSD:
• 0.01 lot = $0.1/pip
• 0.1 lot = $1/pip
• 1.0 lot = $10/pip

**What is Spread?**
The difference between buy price (Ask) and sell price (Bid).
Spread = the trading fee you pay to your broker.

Typical XAUUSD spread: 20-40 pips
Choose low-spread broker to reduce costs!

**Leverage:**
Allows you to control a position larger than your actual capital.
Leverage 1:100 → $1,000 controls $100,000
⚠️ High leverage = High profit = HIGH risk"""
            }),
            "quiz_json": json.dumps([
                {
                    "q": {"vi": "Với 0.1 lot XAUUSD, mỗi pip tương đương bao nhiêu USD?", "en": "With 0.1 lot XAUUSD, how much is each pip worth in USD?"},
                    "options": {
                        "vi": ["$0.1", "$1", "$10", "$100"],
                        "en": ["$0.1", "$1", "$10", "$100"]
                    },
                    "answer": 1,
                    "explanation": {"vi": "XAUUSD: 0.1 lot = $1/pip", "en": "XAUUSD: 0.1 lot = $1/pip"}
                }
            ]),
            "xp": 15,
            "minutes": 8,
            "premium": False,
        },

        # ── Category: advanced (premium) ────────────────────────────────────
        {
            "id": "adv_01",
            "category": "advanced",
            "order": 1,
            "title": json.dumps({"vi": "Multi-Timeframe Analysis (MTF)", "en": "Multi-Timeframe Analysis (MTF)"}),
            "description": json.dumps({
                "vi": "Kết hợp nhiều khung thời gian để có setup chất lượng cao nhất",
                "en": "Combine multiple timeframes for the highest quality setups"
            }),
            "content": json.dumps({
                "vi": """MTF (Multi-Timeframe Analysis) là bí quyết của các trader chuyên nghiệp.

**Top-Down Analysis:**
1. **Monthly/Weekly (HTF)**: Xu hướng tổng thể — BUY hay SELL bias?
2. **Daily/H4**: Xác nhận bias, tìm key levels (OB, FVG lớn)
3. **H1**: Xác nhận cấu trúc thị trường (BOS/CHoCH)
4. **M15/M5 (LTF)**: Điểm vào lệnh chính xác

**Nguyên tắc vàng:**
→ Chỉ trade theo hướng HTF
→ LTF dùng để tìm điểm vào tốt nhất

**Ví dụ XAUUSD:**
• Daily: BUY bias (Higher High structure)
• H4: Có Bullish OB tại 3,020-3,025
• H1: CHoCH bearish → BOS bullish xác nhận
• M15: FVG bullish tại 3,022 → ENTRY

**Tại sao MTF hiệu quả:**
• Giảm false signals dramatically
• Hệ thống lọc tự nhiên
• RR ratio tốt hơn nhiều so với trade single TF""",
                "en": """MTF (Multi-Timeframe Analysis) is the secret of professional traders.

**Top-Down Analysis:**
1. **Monthly/Weekly (HTF)**: Overall trend — BUY or SELL bias?
2. **Daily/H4**: Confirm bias, find key levels (OB, large FVG)
3. **H1**: Confirm market structure (BOS/CHoCH)
4. **M15/M5 (LTF)**: Precise entry point

**Golden rules:**
→ Only trade in the HTF direction
→ LTF is for finding the best entry point

**XAUUSD example:**
• Daily: BUY bias (Higher High structure)
• H4: Bullish OB at 3,020-3,025
• H1: Bearish CHoCH → Bullish BOS confirms
• M15: Bullish FVG at 3,022 → ENTRY

**Why MTF works:**
• Dramatically reduces false signals
• Natural filtering system
• Much better RR ratio vs single TF trading"""
            }),
            "quiz_json": json.dumps([]),
            "xp": 40,
            "minutes": 15,
            "premium": True,
        },
        {
            "id": "adv_02",
            "category": "advanced",
            "order": 2,
            "title": json.dumps({"vi": "Confluence — Xếp chồng xác nhận", "en": "Confluence — Stacking Confirmations"}),
            "description": json.dumps({
                "vi": "Trade chỉ khi có 3+ yếu tố cùng xác nhận — Chiến lược của trader thắng đều",
                "en": "Trade only with 3+ factors confirming — Strategy of consistently winning traders"
            }),
            "content": json.dumps({
                "vi": """Confluence = nhiều yếu tố cùng trỏ về một hướng tại cùng một vùng giá.

**5-Factor Checklist (dùng trong ATTRAOS AICouncil):**
1. ✅ HTF Trend (H4/Daily) theo hướng lệnh?
2. ✅ SMC Zone (OB hoặc FVG) tại entry?
3. ✅ LTF Confirmation (M15 BOS, FVG fill)?
4. ✅ Risk:Reward ≥ 1:2?
5. ✅ Không có news high-impact trong 2 giờ?

**Cần tối thiểu 4/5 mới vào lệnh!**

**Các yếu tố confluence phổ biến:**
• OB + FVG cùng vùng = Strong zone
• OB + FVG + Fibonacci 61.8% = Premium zone
• Kill Zone timing (London/NY open) + OB = High prob
• HTF structure + LTF entry = Professional entry

**Thực tế:**
Trader nghiệp dư: vào bất kỳ khi nào họ "cảm thấy"
Trader chuyên nghiệp: chờ đủ confluence, setup ít nhưng RR cao

Ít lệnh + Win rate cao + RR tốt = Tăng trưởng bền vững""",
                "en": """Confluence = multiple factors pointing in the same direction at the same price zone.

**5-Factor Checklist (used in ATTRAOS AI Council):**
1. ✅ HTF Trend (H4/Daily) in trade direction?
2. ✅ SMC Zone (OB or FVG) at entry?
3. ✅ LTF Confirmation (M15 BOS, FVG fill)?
4. ✅ Risk:Reward ≥ 1:2?
5. ✅ No high-impact news within 2 hours?

**Need minimum 4/5 to enter!**

**Common confluence factors:**
• OB + FVG in same zone = Strong zone
• OB + FVG + Fibonacci 61.8% = Premium zone
• Kill Zone timing (London/NY open) + OB = High probability
• HTF structure + LTF entry = Professional entry

**Reality:**
Amateur traders: enter whenever they "feel like it"
Professional traders: wait for full confluence, fewer trades but high RR

Fewer trades + High win rate + Good RR = Sustainable growth"""
            }),
            "quiz_json": json.dumps([]),
            "xp": 50,
            "minutes": 12,
            "premium": True,
        },
    ]

    added = 0
    updated = 0
    for l in lessons:
        existing = db.get(Lesson, l["id"])
        if existing:
            existing.category = l["category"]
            existing.order = l["order"]
            existing.title = l["title"]
            existing.description = l["description"]
            existing.content = l["content"]
            existing.quiz_json = l["quiz_json"]
            existing.xp = l["xp"]
            existing.minutes = l["minutes"]
            existing.premium = l["premium"]
            existing.active = True
            existing.updated_at = datetime.utcnow()
            updated += 1
        else:
            db.add(Lesson(**l, active=True))
            added += 1

    db.commit()
    db.close()
    print(f"✅ Seeded: {added} new + {updated} updated lessons")
    print(f"   Categories: SMC (3), Risk (2), ICT (2), Basics (1), Advanced/Premium (2)")

if __name__ == "__main__":
    seed()
