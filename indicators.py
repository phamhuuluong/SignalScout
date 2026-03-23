"""
Signal Scout — Indicator Engine
EMA, RSI, ATR, MACD, Volume Analysis — server-side calculation
"""
import numpy as np
from market_data import Candle


def ema(data: list[float], period: int) -> list[float]:
    """Exponential Moving Average"""
    if len(data) < period:
        return [sum(data) / max(len(data), 1)] * len(data)
    k = 2.0 / (period + 1)
    result = [0.0] * len(data)
    result[period - 1] = sum(data[:period]) / period
    for i in range(period, len(data)):
        result[i] = data[i] * k + result[i - 1] * (1 - k)
    # Fill initial values
    for i in range(period - 1):
        result[i] = result[period - 1]
    return result


def sma(data: list[float], period: int) -> list[float]:
    """Simple Moving Average"""
    result = []
    for i in range(len(data)):
        start = max(0, i - period + 1)
        result.append(sum(data[start:i + 1]) / (i - start + 1))
    return result


def rsi(closes: list[float], period: int = 14) -> list[float]:
    """Relative Strength Index"""
    if len(closes) < period + 1:
        return [50.0] * len(closes)
    deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    gains = [max(d, 0) for d in deltas]
    losses = [abs(min(d, 0)) for d in deltas]

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    result = [50.0] * (period + 1)
    if avg_loss == 0:
        result[period] = 100.0
    else:
        rs = avg_gain / avg_loss
        result[period] = 100 - 100 / (1 + rs)

    for i in range(period, len(deltas)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        if avg_loss == 0:
            result.append(100.0)
        else:
            rs = avg_gain / avg_loss
            result.append(100 - 100 / (1 + rs))
    return result


def atr(highs: list[float], lows: list[float], closes: list[float], period: int = 14) -> list[float]:
    """Average True Range"""
    if len(closes) < 2:
        return [0.0] * len(closes)
    trs = [highs[0] - lows[0]]
    for i in range(1, len(closes)):
        tr = max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1]))
        trs.append(tr)
    return sma(trs, period)


def macd(closes: list[float], fast: int = 12, slow: int = 26, signal: int = 9):
    """MACD Line, Signal Line, Histogram"""
    ema_fast = ema(closes, fast)
    ema_slow = ema(closes, slow)
    macd_line = [f - s for f, s in zip(ema_fast, ema_slow)]
    signal_line = ema(macd_line, signal)
    histogram = [m - s for m, s in zip(macd_line, signal_line)]
    return macd_line, signal_line, histogram


def adx(highs: list[float], lows: list[float], closes: list[float], period: int = 14) -> list[float]:
    """Average Directional Index"""
    if len(closes) < period + 1:
        return [0.0] * len(closes)
    plus_dm = []
    minus_dm = []
    tr_list = []
    for i in range(1, len(closes)):
        high_diff = highs[i] - highs[i - 1]
        low_diff = lows[i - 1] - lows[i]
        plus_dm.append(max(high_diff, 0) if high_diff > low_diff else 0)
        minus_dm.append(max(low_diff, 0) if low_diff > high_diff else 0)
        tr = max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1]))
        tr_list.append(tr)
    smoothed_tr = sma(tr_list, period)
    smoothed_plus = sma(plus_dm, period)
    smoothed_minus = sma(minus_dm, period)
    dx_list = []
    for i in range(len(smoothed_tr)):
        if smoothed_tr[i] == 0:
            dx_list.append(0)
            continue
        plus_di = 100 * smoothed_plus[i] / smoothed_tr[i]
        minus_di = 100 * smoothed_minus[i] / smoothed_tr[i]
        if plus_di + minus_di == 0:
            dx_list.append(0)
        else:
            dx_list.append(100 * abs(plus_di - minus_di) / (plus_di + minus_di))
    adx_values = sma(dx_list, period)
    return [0.0] + adx_values  # pad for alignment


def volume_ratio(volumes: list[float], period: int = 20) -> list[float]:
    """Volume ratio vs average"""
    avg = sma(volumes, period)
    return [v / a if a > 0 else 1.0 for v, a in zip(volumes, avg)]


# ─── Compute All Indicators ──────────────────────────
def compute_indicators(candles: list[Candle]) -> dict:
    """Compute all indicators for a list of candles"""
    if len(candles) < 5:
        return {"error": "Not enough data"}

    closes = [c.close for c in candles]
    highs = [c.high for c in candles]
    lows = [c.low for c in candles]
    volumes = [c.volume for c in candles]

    ema9 = ema(closes, 9)
    ema21 = ema(closes, 21)
    rsi14 = rsi(closes, 14)
    atr14 = atr(highs, lows, closes, 14)
    macd_line, signal_line, histogram = macd(closes)
    adx14 = adx(highs, lows, closes, 14)
    vol_ratio = volume_ratio(volumes)

    # Current trend
    current = closes[-1]
    trend = "UPTREND" if current > ema9[-1] > ema21[-1] else "DOWNTREND" if current < ema9[-1] < ema21[-1] else "SIDEWAYS"

    # EMA cross signal
    ema_cross = "BULLISH" if ema9[-1] > ema21[-1] and ema9[-2] <= ema21[-2] else \
                "BEARISH" if ema9[-1] < ema21[-1] and ema9[-2] >= ema21[-2] else "NONE"

    return {
        "price": current,
        "ema9": round(ema9[-1], 2),
        "ema21": round(ema21[-1], 2),
        "rsi14": round(rsi14[-1], 1),
        "atr14": round(atr14[-1], 2),
        "macd": round(macd_line[-1], 4),
        "macd_signal": round(signal_line[-1], 4),
        "macd_histogram": round(histogram[-1], 4),
        "adx": round(adx14[-1], 1) if adx14 else 0,
        "volume_ratio": round(vol_ratio[-1], 2),
        "trend": trend,
        "ema_cross": ema_cross,
        # Arrays for charting
        "_ema9": [round(v, 2) for v in ema9[-50:]],
        "_ema21": [round(v, 2) for v in ema21[-50:]],
        "_rsi14": [round(v, 1) for v in rsi14[-50:]],
    }
