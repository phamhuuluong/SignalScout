"""
order_flow_analyzer.py — ATTRAOS Hub v1.1
Real Order Flow Analysis từ OHLCV thật (không random, không simulation).

Thuật toán:
- CVD (Cumulative Volume Delta) từ candle data: nến tăng → buy vol, nến giảm → sell vol
- Absorption: volume lớn + body nhỏ (< 30% range) → lực đang bị hấp thụ
- Iceberg: volume spike tại cùng mức giá liên tiếp → lệnh ẩn
- Stop Hunt: spike qua swing high/low rồi đóng cửa trong range cũ
- Delta Divergence: CVD trend ≠ Price trend → phân kỳ thật
"""

from dataclasses import dataclass, field
from typing import List, Optional
import statistics

# ─── Data Structures ──────────────────────────────────────────────────────────

@dataclass
class Candle:
    time: int         # Unix timestamp
    open: float
    high: float
    low: float
    close: float
    volume: float

    @property
    def body(self) -> float:
        return abs(self.close - self.open)

    @property
    def range(self) -> float:
        r = self.high - self.low
        return r if r > 0 else 0.0001

    @property
    def body_ratio(self) -> float:
        """body / range — nhỏ = doji/absorption, lớn = momentum mạnh"""
        return self.body / self.range

    @property
    def is_bullish(self) -> bool:
        return self.close >= self.open

    @property
    def delta(self) -> float:
        """Volume delta ước tính: +vol nếu nến tăng, -vol nếu giảm.
        Nhân với body_ratio để phản ánh cường độ."""
        sign = 1.0 if self.is_bullish else -1.0
        return sign * self.volume * self.body_ratio

    @property
    def upper_wick(self) -> float:
        return self.high - max(self.open, self.close)

    @property
    def lower_wick(self) -> float:
        return min(self.open, self.close) - self.low


@dataclass
class OFSignal:
    pattern: str      # ICEBERG | ABSORPTION | STOP_HUNT | DELTA_DIV | SPOOF_HINT
    direction: str    # BULLISH | BEARISH | NEUTRAL
    strength: int     # 0-100
    price: float
    description: str


@dataclass
class OFDelta:
    cvd: float
    direction: str
    divergence: bool
    buy_pct: float
    sell_pct: float
    divergence_desc: str


@dataclass
class OFSnapshot:
    current_price: float
    overall_bias: str
    signals: List[OFSignal]
    delta: OFDelta
    signal_count: int
    top_signal: str


# ─── Core Analyzer ─────────────────────────────────────────────────────────────

class OrderFlowAnalyzer:
    def __init__(self, candles_m15: List[dict], candles_h1: List[dict], symbol: str = "XAUUSD"):
        self.symbol = symbol
        self.m15 = [self._to_candle(c) for c in candles_m15] if candles_m15 else []
        self.h1  = [self._to_candle(c) for c in candles_h1]  if candles_h1  else []

    def _to_candle(self, d: dict) -> Candle:
        return Candle(
            time=int(d.get("t", 0)),
            open=float(d.get("o", 0)),
            high=float(d.get("h", 0)),
            low=float(d.get("l", 0)),
            close=float(d.get("c", 0)),
            volume=max(float(d.get("v", 1)), 1.0)
        )

    # ── CVD calculation ─────────────────────────────────────────────────────

    def compute_cvd_series(self, candles: List[Candle]) -> List[float]:
        """Tính CVD tích lũy từ từng nến."""
        cvd = 0.0
        series = []
        for c in candles:
            cvd += c.delta
            series.append(cvd)
        return series

    def compute_buy_sell_volumes(self, candles: List[Candle]):
        """Tổng buy vol / sell vol từ toàn bộ candle set."""
        buy_vol = sum(c.volume * c.body_ratio for c in candles if c.is_bullish)
        sell_vol = sum(c.volume * c.body_ratio for c in candles if not c.is_bullish)
        return buy_vol, sell_vol

    # ── Pattern Detectors ───────────────────────────────────────────────────

    def detect_absorption(self, candles: List[Candle]) -> Optional[OFSignal]:
        """
        Absorption: nến có volume > 1.5× trung bình nhưng body < 25% range.
        Tức là lực lớn nhưng giá không đi được xa → đang bị hấp thụ.
        """
        if len(candles) < 10:
            return None

        recent = candles[-20:]
        avg_vol = statistics.mean(c.volume for c in recent)
        
        # Tìm nến absorption mạnh nhất trong 5 nến gần nhất
        best = None
        best_score = 0
        for c in candles[-5:]:
            if c.volume < avg_vol * 1.5:
                continue
            if c.body_ratio > 0.30:
                continue
            # Tỉ lệ vol/avgvol càng cao, body càng nhỏ → absorption càng mạnh
            score = (c.volume / avg_vol) * (1.0 - c.body_ratio)
            if score > best_score:
                best_score = score
                best = c

        if best is None or best_score < 1.5:
            return None

        strength = min(int((best_score - 1.5) / 3.0 * 100), 98)
        # Direction: nếu price đang giảm mà absorption xảy ra → BULLISH (mua đang hấp thụ áp lực bán)
        last_3 = candles[-3:]
        price_down = all(c.close < c.open for c in last_3)
        price_up   = all(c.close > c.open for c in last_3)
        direction = "BULLISH" if price_down else ("BEARISH" if price_up else "NEUTRAL")

        return OFSignal(
            pattern="ABSORPTION",
            direction=direction,
            strength=max(strength, 55),
            price=best.close,
            description=f"Nến khổng lồ vol={best.volume:.0f} ({best.volume/avg_vol:.1f}×TB) nhưng body chỉ {best.body_ratio*100:.0f}% range → lực đang bị hấp thụ, sắp đảo chiều"
        )

    def detect_iceberg(self, candles: List[Candle]) -> Optional[OFSignal]:
        """
        Iceberg: nhiều nến liên tiếp test cùng mức giá (high hoặc low) với volume cao
        nhưng không thể break qua → lệnh ẩn đang đặt tại đó.
        """
        if len(candles) < 8:
            return None

        recent = candles[-10:]
        avg_vol = statistics.mean(c.volume for c in candles[-20:]) if len(candles) >= 20 else statistics.mean(c.volume for c in candles)

        # Nhóm các mức high/low gần nhau (trong 0.1% giá)
        tolerance = recent[-1].close * 0.001

        # Test resistance (Iceberg bán ở đỉnh)
        highs = [c.high for c in recent[-5:]]
        if max(highs) - min(highs) < tolerance:
            # Cùng mức high → resistance iceberg
            high_vols = [c.volume for c in recent[-5:]]
            avg_high_vol = statistics.mean(high_vols)
            if avg_high_vol > avg_vol * 1.2:
                strength = min(int((avg_high_vol / avg_vol - 1.0) * 60), 92)
                level = statistics.mean(highs)
                return OFSignal(
                    pattern="ICEBERG",
                    direction="BEARISH",
                    strength=max(strength, 62),
                    price=level,
                    description=f"5 nến liên tiếp test vùng kháng cự {level:.2f} với volume cao ({avg_high_vol:.0f}) → Iceberg bán tại đỉnh, thị trường khó vượt"
                )

        # Test support (Iceberg mua ở đáy)
        lows = [c.low for c in recent[-5:]]
        if max(lows) - min(lows) < tolerance:
            low_vols = [c.volume for c in recent[-5:]]
            avg_low_vol = statistics.mean(low_vols)
            if avg_low_vol > avg_vol * 1.2:
                strength = min(int((avg_low_vol / avg_vol - 1.0) * 60), 92)
                level = statistics.mean(lows)
                return OFSignal(
                    pattern="ICEBERG",
                    direction="BULLISH",
                    strength=max(strength, 62),
                    price=level,
                    description=f"5 nến liên tiếp giữ vùng hỗ trợ {level:.2f} với volume cao ({avg_low_vol:.0f}) → Iceberg mua tại đáy, cá vờ đang bảo vệ"
                )

        return None

    def detect_stop_hunt(self, candles: List[Candle]) -> Optional[OFSignal]:
        """
        Stop Hunt: nến đột ngột spike qua swing high/low (wick dài > 60% range)
        rồi đóng cửa bên trong range cũ + volume cao.
        """
        if len(candles) < 15:
            return None

        avg_vol = statistics.mean(c.volume for c in candles[-20:]) if len(candles) >= 20 else statistics.mean(c.volume for c in candles)

        # Tính swing high/low từ 10-20 nến trước
        lookback = candles[-15:-1]
        swing_high = max(c.high for c in lookback)
        swing_low  = min(c.low  for c in lookback)

        last = candles[-1]

        # Stop Hunt ở đỉnh: spike lên trên swing_high rồi đóng cửa dưới
        if last.high > swing_high and last.close < swing_high:
            hunt_size = (last.high - swing_high) / last.range
            vol_ratio = last.volume / avg_vol
            if hunt_size > 0.15 and vol_ratio > 1.3:
                strength = min(int(hunt_size * 200 + vol_ratio * 20), 95)
                return OFSignal(
                    pattern="STOP_HUNT",
                    direction="BEARISH",
                    strength=max(strength, 70),
                    price=last.high,
                    description=f"Spike phá đỉnh {swing_high:.2f} rồi reject ngay — Stop Hunt bẫy lệnh BUY, Smart Money đang bán"
                )

        # Stop Hunt ở đáy: spike xuống dưới swing_low rồi đóng cửa trên
        if last.low < swing_low and last.close > swing_low:
            hunt_size = (swing_low - last.low) / last.range
            vol_ratio = last.volume / avg_vol
            if hunt_size > 0.15 and vol_ratio > 1.3:
                strength = min(int(hunt_size * 200 + vol_ratio * 20), 95)
                return OFSignal(
                    pattern="STOP_HUNT",
                    direction="BULLISH",
                    strength=max(strength, 70),
                    price=last.low,
                    description=f"Spike phá đáy {swing_low:.2f} rồi reject ngay — Stop Hunt bẫy lệnh SELL, Smart Money đang mua"
                )

        return None

    def detect_delta_divergence(self, candles: List[Candle]) -> Optional[OFSignal]:
        """
        Delta Divergence: CVD đang tăng nhưng giá giảm (hidden bearish)
        hoặc CVD đang giảm nhưng giá tăng (hidden bullish).
        """
        if len(candles) < 20:
            return None

        recent = candles[-20:]
        cvd_series = self.compute_cvd_series(recent)

        # Slope của CVD và Price trong 10 nến gần nhất
        cvd_start = cvd_series[-10] if len(cvd_series) >= 10 else cvd_series[0]
        cvd_end   = cvd_series[-1]
        price_start = recent[-10].close if len(recent) >= 10 else recent[0].close
        price_end   = recent[-1].close

        cvd_rising   = cvd_end > cvd_start
        price_rising = price_end > price_start

        # Phân kỳ: hướng trái ngược nhau
        if cvd_rising and not price_rising:
            magnitude = abs(cvd_end - cvd_start) / (abs(price_end - price_start) + 0.0001)
            strength = min(int(magnitude * 10), 90)
            if strength < 50:
                return None
            return OFSignal(
                pattern="DELTA_DIV",
                direction="BULLISH",
                strength=max(strength, 65),
                price=recent[-1].close,
                description=f"CVD tăng {cvd_end-cvd_start:+.0f} nhưng giá giảm — Smart Money đang tích lũy bí mật, giá thật sắp theo CVD đi lên"
            )

        if not cvd_rising and price_rising:
            magnitude = abs(cvd_end - cvd_start) / (abs(price_end - price_start) + 0.0001)
            strength = min(int(magnitude * 10), 90)
            if strength < 50:
                return None
            return OFSignal(
                pattern="DELTA_DIV",
                direction="BEARISH",
                strength=max(strength, 65),
                price=recent[-1].close,
                description=f"CVD giảm {cvd_end-cvd_start:+.0f} nhưng giá tăng — Lực bán thực đang chiếm ưu thế, tăng là bẫy, chuẩn bị đảo chiều"
            )

        return None

    def detect_volume_climax(self, candles: List[Candle]) -> Optional[OFSignal]:
        """
        Volume Climax: nến có volume cao nhất trong 50 nến gần nhất
        → thường là điểm cạn kiệt lực (exhaustion), hay đảo chiều.
        """
        if len(candles) < 20:
            return None

        recent = candles[-50:] if len(candles) >= 50 else candles
        max_vol_candle = max(recent, key=lambda c: c.volume)
        # Chỉ report nếu nó là 1 trong 5 nến cuối
        if max_vol_candle not in candles[-5:]:
            return None

        avg_vol = statistics.mean(c.volume for c in recent[:-1])
        ratio = max_vol_candle.volume / avg_vol
        if ratio < 2.5:
            return None

        direction = "BEARISH" if max_vol_candle.is_bullish else "BULLISH"
        strength = min(int((ratio - 2.5) * 25 + 60), 90)

        return OFSignal(
            pattern="ABSORPTION",
            direction=direction,
            strength=max(strength, 65),
            price=max_vol_candle.close,
            description=f"Volume Climax: nến hiện tại có vol={max_vol_candle.volume:.0f} ({ratio:.1f}×TB) — Lực {'mua' if max_vol_candle.is_bullish else 'bán'} đang cạn kiệt, sắp đảo chiều"
        )

    # ── Main Analysis ───────────────────────────────────────────────────────

    def analyze(self) -> OFSnapshot:
        candles = self.m15  # Primary timeframe M15
        if not candles:
            candles = self.h1
        if not candles:
            return self._empty_snapshot()

        current_price = candles[-1].close

        # Tính CVD
        cvd_series = self.compute_cvd_series(candles)
        cvd_total  = cvd_series[-1] if cvd_series else 0.0
        buy_vol, sell_vol = self.compute_buy_sell_volumes(candles)
        total_vol = buy_vol + sell_vol
        buy_pct  = (buy_vol / total_vol * 100) if total_vol > 0 else 50.0
        sell_pct = 100.0 - buy_pct

        # Chạy tất cả detectors
        signals: List[OFSignal] = []
        for detector in [
            self.detect_delta_divergence,
            self.detect_stop_hunt,
            self.detect_absorption,
            self.detect_iceberg,
            self.detect_volume_climax,
        ]:
            try:
                sig = detector(candles)
                if sig:
                    signals.append(sig)
            except Exception:
                pass

        # Thêm H1 analysis cho context dài hạn hơn
        if self.h1 and len(self.h1) >= 20:
            for detector in [self.detect_delta_divergence, self.detect_stop_hunt]:
                try:
                    sig = detector(self.h1)
                    if sig:
                        # Tăng strength 10% cho H1 signals (timeframe cao hơn = quan trọng hơn)
                        sig.strength = min(sig.strength + 10, 99)
                        sig.description = f"[H1] {sig.description}"
                        # Chỉ thêm nếu chưa có pattern giống rồi
                        existing = [s.pattern for s in signals]
                        if sig.pattern not in existing:
                            signals.append(sig)
                except Exception:
                    pass

        # Sort by strength
        signals.sort(key=lambda s: s.strength, reverse=True)

        # Overall bias
        bullish_count = sum(1 for s in signals if s.direction == "BULLISH")
        bearish_count = sum(1 for s in signals if s.direction == "BEARISH")
        if bullish_count > bearish_count:
            overall_bias = "BULLISH"
        elif bearish_count > bullish_count:
            overall_bias = "BEARISH"
        else:
            # Dùng CVD để tiebreak
            overall_bias = "BULLISH" if cvd_total > 0 else ("BEARISH" if cvd_total < 0 else "NEUTRAL")

        # Divergence
        price_5 = candles[-5].close if len(candles) >= 5 else candles[0].close
        price_now = candles[-1].close
        cvd_5 = cvd_series[-5] if len(cvd_series) >= 5 else cvd_series[0]
        cvd_now = cvd_series[-1]
        divergence = (cvd_now > cvd_5 and price_now < price_5) or (cvd_now < cvd_5 and price_now > price_5)
        if divergence:
            if cvd_now > cvd_5:
                div_desc = "CVD tăng nhưng giá giảm → lực mua thực sự đang ẩn, giá chuẩn bị theo CVD đi lên"
            else:
                div_desc = "CVD giảm nhưng giá tăng → lực bán thực đang chiếm ưu thế, tăng là bẫy"
        else:
            div_desc = "CVD và giá đang đồng thuận — xu hướng hiện tại đáng tin cậy"

        delta_info = OFDelta(
            cvd=cvd_total,
            direction="BULLISH" if cvd_total > 0 else ("BEARISH" if cvd_total < 0 else "NEUTRAL"),
            divergence=divergence,
            buy_pct=buy_pct,
            sell_pct=sell_pct,
            divergence_desc=div_desc
        )

        top = signals[0].description if signals else "Không phát hiện tín hiệu Order Flow đặc biệt."

        return OFSnapshot(
            current_price=current_price,
            overall_bias=overall_bias,
            signals=signals,
            delta=delta_info,
            signal_count=len(signals),
            top_signal=top
        )

    def _empty_snapshot(self) -> OFSnapshot:
        return OFSnapshot(
            current_price=0.0,
            overall_bias="NEUTRAL",
            signals=[],
            delta=OFDelta(0, "NEUTRAL", False, 50, 50, "Không có dữ liệu"),
            signal_count=0,
            top_signal="Đang chờ dữ liệu MT5..."
        )


# ─── Serialization helpers dùng cho FastAPI endpoint ──────────────────────────

def snapshot_to_dict(snap: OFSnapshot) -> dict:
    return {
        "current_price": snap.current_price,
        "overall_bias": snap.overall_bias,
        "signals": [
            {
                "pattern": s.pattern,
                "direction": s.direction,
                "strength": s.strength,
                "price": s.price,
                "description": s.description,
            }
            for s in snap.signals
        ],
        "delta": {
            "cvd": snap.delta.cvd,
            "direction": snap.delta.direction,
            "divergence": snap.delta.divergence,
            "buy_pct": snap.delta.buy_pct,
            "sell_pct": snap.delta.sell_pct,
            "divergence_desc": snap.delta.divergence_desc,
        },
        "signal_count": snap.signal_count,
        "top_signal": snap.top_signal,
    }
