"""
Signal Scout — Signal Engine
Combines indicators + SMC → BUY/SELL/NONE with confidence scoring
"""
from market_data import Candle, MarketDataService
from indicators import compute_indicators
from smc_detector import analyze_smc
import asyncio


# ─── Confidence Scoring (from Prompt_Manager_OPTIMIZED_v2) ─────
def compute_confidence(indicators: dict, smc_data: dict, htf_trend: str = "") -> dict:
    """
    Objective confidence scoring based on production prompt:
    BASE: 50 + ADD/SUB factors → max 100, min trade 65
    """
    score = 50
    reasons = []

    # +15: Timeframe alignment
    if htf_trend and indicators.get("trend", "") == htf_trend:
        score += 15
        reasons.append("TF alignment")
    elif htf_trend:
        score -= 15
        reasons.append("Against HTF ⚠️")

    # +15: SMC confluence (OB + FVG + BOS all present)
    has_ob = len(smc_data.get("ob", [])) > 0
    has_fvg = len(smc_data.get("fvg", [])) > 0
    has_bos = len(smc_data.get("bos", [])) > 0
    smc_count = sum([has_ob, has_fvg, has_bos])
    if smc_count >= 3:
        score += 15
        reasons.append("Full SMC confluence")
    elif smc_count >= 2:
        score += 8
        reasons.append("Partial SMC")
    elif smc_count <= 1:
        score -= 4
        reasons.append("Weak confluence")

    # +12: Volume spike + ADX strong
    vol_ratio = indicators.get("volume_ratio", 1.0)
    adx_val = indicators.get("adx", 0)
    if vol_ratio > 1.5 and adx_val > 25:
        score += 12
        reasons.append(f"Volume {vol_ratio:.1f}x + ADX {adx_val:.0f}")
    elif vol_ratio > 1.3:
        score += 5
        reasons.append(f"Volume {vol_ratio:.1f}x")

    # +8: Indicator confluence (RSI extreme + EMA cross)
    rsi = indicators.get("rsi14", 50)
    ema_cross = indicators.get("ema_cross", "NONE")
    if (rsi < 35 and ema_cross == "BULLISH") or (rsi > 65 and ema_cross == "BEARISH"):
        score += 8
        reasons.append(f"RSI {rsi:.0f} + EMA cross")
    elif rsi < 30 or rsi > 70:
        score += 4
        reasons.append(f"RSI extreme {rsi:.0f}")

    # +6: Good RR (we estimate based on ATR)
    atr = indicators.get("atr14", 0)
    if atr > 0:
        score += 3
        reasons.append(f"ATR {atr:.1f}")

    # +5: Liquidity sweep recent
    sweeps = smc_data.get("sweeps", [])
    if sweeps:
        score += 5
        reasons.append("Liquidity sweep detected")

    # +4: CHoCH/MSS
    mss = smc_data.get("mss", [])
    if mss:
        score += 4
        reasons.append("Market structure shift")

    score = max(0, min(100, score))
    return {"confidence": score, "reasons": reasons}


# ─── Signal Decision ──────────────────────────────────
def generate_signal(indicators: dict, smc_data: dict, htf_trend: str = "") -> dict:
    """Generate trading signal with confidence score"""
    conf = compute_confidence(indicators, smc_data, htf_trend)
    confidence = conf["confidence"]
    reasons = conf["reasons"]

    trend = indicators.get("trend", "SIDEWAYS")
    structure = smc_data.get("structure", "NEUTRAL")
    rsi = indicators.get("rsi14", 50)
    ema9 = indicators.get("ema9", 0)
    ema21 = indicators.get("ema21", 0)
    price = indicators.get("price", 0)
    atr = indicators.get("atr14", 0)

    # Decision logic
    decision = "NONE"
    entry = price
    sl = 0.0
    tp = 0.0

    if confidence >= 65:
        # Bullish signals
        if (trend in ("UPTREND", "SIDEWAYS") and structure == "BULLISH") or \
           (rsi < 35 and structure != "BEARISH") or \
           (trend == "UPTREND" and ema9 > ema21):
            decision = "BUY"
            sl = round(price - atr * 2, 2)
            tp = round(price + atr * 3, 2)
            reasons.append("Buy setup confirmed")

        # Bearish signals
        elif (trend in ("DOWNTREND", "SIDEWAYS") and structure == "BEARISH") or \
             (rsi > 65 and structure != "BULLISH") or \
             (trend == "DOWNTREND" and ema9 < ema21):
            decision = "SELL"
            sl = round(price + atr * 2, 2)
            tp = round(price - atr * 3, 2)
            reasons.append("Sell setup confirmed")

    # Hard gates (from production prompt)
    if sl != 0 and abs(price - sl) > 200:
        decision = "NONE"
        reasons.append("❌ SL > 200 pips")

    if sl != 0 and tp != 0:
        rr = abs(tp - price) / max(abs(price - sl), 0.01)
        if rr < 1.5:
            decision = "NONE"
            reasons.append("❌ RR < 1.5")

    risk_level = "LOW" if confidence >= 80 else "MEDIUM" if confidence >= 70 else "HIGH"

    return {
        "decision": decision,
        "confidence": confidence,
        "entry": round(entry, 2),
        "sl": sl,
        "tp": tp,
        "risk_level": risk_level,
        "trend": trend,
        "structure": structure,
        "reasons": reasons
    }


# ─── Multi-Symbol Radar Scan ──────────────────────────
SCAN_SYMBOLS = [
    ("XAUUSD", "XAU/USD", "Gold"),
    ("XAGUSD", "XAG/USD", "Silver"),
    ("EURUSD", "EUR/USD", "Euro"),
    ("GBPUSD", "GBP/USD", "Pound"),
    ("USDJPY", "USD/JPY", "Yen"),
    ("BTCUSDT", "BTCUSDT", "Bitcoin"),
    ("ETHUSDT", "ETHUSDT", "Ethereum"),
]


async def radar_scan(market: MarketDataService) -> list[dict]:
    """Scan all symbols and return signals"""
    results = []

    async def scan_one(sym_id, api_sym, name):
        try:
            candles = await market.fetch_candles(api_sym, "15m", 100)
            if len(candles) < 20:
                return None
            ind = compute_indicators(candles)
            smc_data = analyze_smc(candles)
            signal = generate_signal(ind, smc_data)
            return {
                "symbol": sym_id,
                "name": name,
                "price": ind.get("price", 0),
                "signal": signal,
                "indicators": {k: v for k, v in ind.items() if not k.startswith("_")},
                "smc_summary": {
                    "structure": smc_data.get("structure", "N/A"),
                    "bos_count": len(smc_data.get("bos", [])),
                    "fvg_count": len(smc_data.get("fvg", [])),
                    "ob_count": len(smc_data.get("ob", [])),
                    "sweep_count": len(smc_data.get("sweeps", [])),
                }
            }
        except Exception as e:
            return {"symbol": sym_id, "name": name, "error": str(e)}

    tasks = [scan_one(s, a, n) for s, a, n in SCAN_SYMBOLS]
    raw = await asyncio.gather(*tasks)
    results = [r for r in raw if r is not None]
    # Sort by confidence (highest first)
    results.sort(key=lambda x: x.get("signal", {}).get("confidence", 0), reverse=True)
    return results
