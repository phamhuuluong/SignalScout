"""
Order Flow Analyzer — ATTRAOS Hub
Phát hiện các hiện tượng Order Flow theo chiến lược Bookmap:
- Iceberg Orders
- Absorption
- Spoofing
- CVD Delta Imbalance
- Liquidity Hunt
"""

import numpy as np
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import List, Optional
import time


# ─────────────────────────────────────────────
#  Data Structures
# ─────────────────────────────────────────────

@dataclass
class L2Level:
    price: float
    bid_volume: float
    ask_volume: float
    timestamp: float = field(default_factory=time.time)


@dataclass
class TradeEvent:
    price: float
    volume: float
    side: str          # 'buy' or 'sell'
    timestamp: float = field(default_factory=time.time)


@dataclass
class OrderFlowSignal:
    pattern: str       # 'ICEBERG' | 'ABSORPTION' | 'SPOOF' | 'HUNT' | 'DELTA_DIV'
    direction: str     # 'BULLISH' | 'BEARISH' | 'NEUTRAL'
    strength: int      # 0-100
    price: float
    description: str
    timestamp: float = field(default_factory=time.time)


# ─────────────────────────────────────────────
#  Order Flow Analyzer Core
# ─────────────────────────────────────────────

class OrderFlowAnalyzer:
    def __init__(self, window_size: int = 200):
        self.window_size = window_size

        # L2 snapshot history: price → list of volumes over time
        self.bid_history: dict[float, deque] = defaultdict(lambda: deque(maxlen=window_size))
        self.ask_history: dict[float, deque] = defaultdict(lambda: deque(maxlen=window_size))

        # Trade tape
        self.trade_tape: deque[TradeEvent] = deque(maxlen=window_size)

        # CVD (Cumulative Volume Delta)
        self.cvd: float = 0.0
        self.cvd_history: deque[float] = deque(maxlen=window_size)
        self.price_history: deque[float] = deque(maxlen=window_size)

        # Iceberg tracking: price → refill count
        self.refill_count: dict[float, int] = defaultdict(int)
        self.prev_l2: dict[float, tuple] = {}   # price → (bid_vol, ask_vol)

    # ─── Feed Data ───────────────────────────

    def feed_l2(self, levels: List[L2Level]):
        """Nhập snapshot L2 mới từ Hub/Binance."""
        for lvl in levels:
            self.bid_history[lvl.price].append(lvl.bid_volume)
            self.ask_history[lvl.price].append(lvl.ask_volume)

            # Iceberg refill detection: giá bị xóa sạch rồi lại xuất hiện
            prev = self.prev_l2.get(lvl.price)
            if prev is not None:
                prev_bid, prev_ask = prev
                # Refill: volume lớn xuất hiện lại sau khi giảm về gần 0
                if prev_bid < 5 and lvl.bid_volume > 20:
                    self.refill_count[lvl.price] += 1
                if prev_ask < 5 and lvl.ask_volume > 20:
                    self.refill_count[lvl.price] += 1
            self.prev_l2[lvl.price] = (lvl.bid_volume, lvl.ask_volume)

    def feed_trade(self, trade: TradeEvent):
        """Nhập lệnh đã khớp từ tape."""
        self.trade_tape.append(trade)
        if trade.side == 'buy':
            self.cvd += trade.volume
        else:
            self.cvd -= trade.volume
        self.cvd_history.append(self.cvd)
        self.price_history.append(trade.price)

    # ─── Detectors ───────────────────────────

    def detect_icebergs(self, refill_threshold: int = 3) -> List[OrderFlowSignal]:
        """Phát hiện Iceberg Orders — lệnh lớn bị chia nhỏ và nạp lại."""
        signals = []
        for price, count in self.refill_count.items():
            if count >= refill_threshold:
                # Xác định hướng: nếu nhiều bid refill → đây là vùng hỗ trợ âm mưu
                bid_sum = sum(self.bid_history.get(price, [0]))
                ask_sum = sum(self.ask_history.get(price, [0]))
                direction = 'BULLISH' if bid_sum > ask_sum else 'BEARISH'
                strength = min(100, count * 15)
                signals.append(OrderFlowSignal(
                    pattern='ICEBERG',
                    direction=direction,
                    strength=strength,
                    price=price,
                    description=f"Iceberg tại {price:.2f} — nạp lại {count} lần. "
                                f"Hỗ trợ {'Mua' if direction == 'BULLISH' else 'Bán'} ẩn."
                ))
        # Reset sau khi báo (tránh báo liên tục)
        self.refill_count.clear()
        return signals

    def detect_absorption(self, price: float, lookback: int = 20) -> Optional[OrderFlowSignal]:
        """
        Phát hiện Absorption — áp lực mạnh nhưng giá không đi được.
        Dấu hiệu: CVD tăng mạnh (nhiều lệnh Buy thị trường) nhưng giá đứng yên hoặc đi ngang.
        """
        if len(self.cvd_history) < lookback or len(self.price_history) < lookback:
            return None

        cvd_arr = np.array(list(self.cvd_history)[-lookback:])
        price_arr = np.array(list(self.price_history)[-lookback:])

        cvd_change = cvd_arr[-1] - cvd_arr[0]
        price_change_pct = abs(price_arr[-1] - price_arr[0]) / max(price_arr[0], 0.01)

        # Nhiều lực mua nhưng giá không tăng → bên Bán đang hấp thụ
        if cvd_change > 50 and price_change_pct < 0.001:
            return OrderFlowSignal(
                pattern='ABSORPTION',
                direction='BEARISH',
                strength=75,
                price=price,
                description=f"Absorption tại {price:.2f} — Lực mua mạnh nhưng giá bị chặn. "
                            f"Seller đang hấp thụ toàn bộ. Cảnh báo đảo chiều xuống."
            )
        # Nhiều lực bán nhưng giá không giảm → bên Mua đang hấp thụ
        if cvd_change < -50 and price_change_pct < 0.001:
            return OrderFlowSignal(
                pattern='ABSORPTION',
                direction='BULLISH',
                strength=75,
                price=price,
                description=f"Absorption tại {price:.2f} — Lực bán mạnh nhưng giá bị giữ. "
                            f"Buyer đang hấp thụ toàn bộ. Cảnh báo đảo chiều lên."
            )
        return None

    def detect_spoofing(self, large_volume_threshold: float = 100) -> List[OrderFlowSignal]:
        """
        Phát hiện Spoofing — lệnh lớn xuất hiện rồi biến mất.
        Dấu hiệu: volume lớn ở L2 nhưng sau 1-2 tick thì biến mất mà không khớp lệnh.
        """
        signals = []
        for price, bid_q in self.bid_history.items():
            if len(bid_q) < 3:
                continue
            recent = list(bid_q)[-3:]
            # Xuất hiện rồi biến mất: [lớn, lớn, nhỏ]
            if recent[0] > large_volume_threshold and recent[1] > large_volume_threshold and recent[2] < 5:
                signals.append(OrderFlowSignal(
                    pattern='SPOOF',
                    direction='BEARISH',   # Giả vờ mua để đẩy giá, thực ra muốn bán
                    strength=65,
                    price=price,
                    description=f"⚠️ SPOOF tại BID {price:.2f} — Lệnh khủng biến mất! "
                                f"Đây là bẫy — Bỏ qua tín hiệu mua vùng này."
                ))
        for price, ask_q in self.ask_history.items():
            if len(ask_q) < 3:
                continue
            recent = list(ask_q)[-3:]
            if recent[0] > large_volume_threshold and recent[1] > large_volume_threshold and recent[2] < 5:
                signals.append(OrderFlowSignal(
                    pattern='SPOOF',
                    direction='BULLISH',   # Giả vờ bán để đẩy giá xuống, thực ra muốn mua
                    strength=65,
                    price=price,
                    description=f"⚠️ SPOOF tại ASK {price:.2f} — Lệnh bán khủng biến mất! "
                                f"Đây là bẫy — Bỏ qua tín hiệu bán vùng này."
                ))
        return signals

    def calculate_delta(self, lookback: int = 50) -> dict:
        """
        Tính CVD Delta và phát hiện phân kỳ với giá.
        Trả về dict chứa cvd, direction, divergence.
        """
        if len(self.cvd_history) < 2:
            return {"cvd": 0, "direction": "NEUTRAL", "divergence": False, "buy_pct": 50, "sell_pct": 50}

        cvd_arr = np.array(list(self.cvd_history)[-min(lookback, len(self.cvd_history)):])
        price_arr = np.array(list(self.price_history)[-min(lookback, len(self.price_history)):])

        cvd_trend = cvd_arr[-1] - cvd_arr[0]
        price_trend = price_arr[-1] - price_arr[0] if len(price_arr) > 1 else 0

        # Phân kỳ: CVD tăng nhưng giá giảm = Bullish divergence (giả mạo xu hướng giảm)
        divergence = (cvd_trend > 30 and price_trend < 0) or (cvd_trend < -30 and price_trend > 0)

        # Tính % mua bán thực sự
        buys = sum(t.volume for t in self.trade_tape if t.side == 'buy')
        sells = sum(t.volume for t in self.trade_tape if t.side == 'sell')
        total = buys + sells
        buy_pct = round((buys / total * 100) if total > 0 else 50, 1)
        sell_pct = round(100 - buy_pct, 1)

        return {
            "cvd": round(self.cvd, 2),
            "direction": "BULLISH" if cvd_trend > 0 else "BEARISH",
            "divergence": divergence,
            "buy_pct": buy_pct,
            "sell_pct": sell_pct,
            "divergence_desc": (
                "CVD tăng nhưng giá giảm → Lực mua thực sự vẫn mạnh, giảm là giả tạo!"
                if cvd_trend > 0 and price_trend < 0
                else "CVD giảm nhưng giá tăng → Lực bán thực sự đang chiếm ưu thế, tăng là bẫy!"
                if cvd_trend < 0 and price_trend > 0
                else "Không có phân kỳ — xu hướng giá và Delta đang đồng thuận."
            ) if divergence else "Không có phân kỳ — xu hướng nhất quán."
        }

    def detect_liquidity_hunt(self, current_price: float) -> Optional[OrderFlowSignal]:
        """
        Phát hiện Stop Hunt / Liquidity Hunt — giá đột ngột xuyên vùng rồi quay lại.
        Dấu hiệu: giá spike sharply qua một mức rồi quay lại trong 2-3 tick.
        """
        if len(self.price_history) < 5:
            return None

        prices = list(self.price_history)[-5:]
        high = max(prices[:-1])
        low = min(prices[:-1])
        last = prices[-1]

        # Spike lên rồi quay lại = Stop Hunt kiểu Buy Stop
        if high > current_price * 1.002 and last < high * 0.999:
            return OrderFlowSignal(
                pattern='HUNT',
                direction='BEARISH',
                strength=70,
                price=current_price,
                description=f"Stop Hunt phía trên {high:.2f} — Buy Stops đã bị quét! "
                            f"Cơ hội SELL sau khi retest. Entry tối ưu: {current_price:.2f}"
            )
        # Spike xuống rồi quay lại = Stop Hunt kiểu Sell Stop
        if low < current_price * 0.998 and last > low * 1.001:
            return OrderFlowSignal(
                pattern='HUNT',
                direction='BULLISH',
                strength=70,
                price=current_price,
                description=f"Stop Hunt phía dưới {low:.2f} — Sell Stops đã bị quét! "
                            f"Cơ hội BUY sau khi retest. Entry tối ưu: {current_price:.2f}"
            )
        return None

    def get_all_signals(self, current_price: float) -> dict:
        """Chạy tất cả detector và trả về dict tổng hợp."""
        signals = []
        signals.extend(self.detect_icebergs())
        signals.extend(self.detect_spoofing())

        abs_sig = self.detect_absorption(current_price)
        if abs_sig:
            signals.append(abs_sig)

        hunt_sig = self.detect_liquidity_hunt(current_price)
        if hunt_sig:
            signals.append(hunt_sig)

        delta = self.calculate_delta()

        # Tổng hợp hướng chung từ các signals
        bull_score = sum(s.strength for s in signals if s.direction == 'BULLISH')
        bear_score = sum(s.strength for s in signals if s.direction == 'BEARISH')
        overall = 'BULLISH' if bull_score > bear_score else ('BEARISH' if bear_score > bull_score else 'NEUTRAL')

        return {
            "current_price": current_price,
            "overall_bias": overall,
            "signals": [
                {
                    "pattern": s.pattern,
                    "direction": s.direction,
                    "strength": s.strength,
                    "price": s.price,
                    "description": s.description
                }
                for s in signals
            ],
            "delta": delta,
            "signal_count": len(signals),
            "top_signal": signals[0].description if signals else "Không phát hiện tín hiệu Order Flow đáng chú ý."
        }
