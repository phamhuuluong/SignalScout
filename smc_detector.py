"""
Signal Scout — SMC Detection Engine
Uses smartmoneyconcepts library (github.com/joshyattridge/smart-money-concepts)
+ custom liquidity sweep / equal level detection
"""
import pandas as pd
import numpy as np
from smartmoneyconcepts import smc
from market_data import Candle


def candles_to_df(candles: list[Candle]) -> pd.DataFrame:
    """Convert Candle list → DataFrame for smc library"""
    return pd.DataFrame({
        "open": [c.open for c in candles],
        "high": [c.high for c in candles],
        "low": [c.low for c in candles],
        "close": [c.close for c in candles],
        "volume": [c.volume for c in candles],
    }, index=[pd.Timestamp(c.timestamp, unit="s") for c in candles])


# ─── Full SMC Analysis using library ─────────────────
def analyze_smc(candles: list[Candle], swing_length: int = 10) -> dict:
    """Run full SMC analysis using smartmoneyconcepts library"""
    if len(candles) < 20:
        return {"structure": "N/A", "bos": [], "mss": [], "fvg": [], "ob": [],
                "sweeps": [], "equal_levels": [], "swing_highs": [], "swing_lows": []}

    df = candles_to_df(candles)

    # 1. Swing Highs & Lows
    try:
        swings = smc.swing_highs_lows(df, swing_length=swing_length)
        swing_highs_idx = swings[swings["HighLow"] == 1].index
        swing_lows_idx = swings[swings["HighLow"] == -1].index
        swing_highs = [{"price": round(df.loc[i, "high"], 2), "time": i.timestamp()} for i in swing_highs_idx]
        swing_lows = [{"price": round(df.loc[i, "low"], 2), "time": i.timestamp()} for i in swing_lows_idx]
    except Exception:
        swing_highs, swing_lows = [], []

    # 2. BOS & CHoCH (Market Structure)
    bos_list = []
    mss_list = []
    try:
        bos_choch = smc.bos_choch(df, swings, close_break=True)
        for i, row in bos_choch.iterrows():
            if not pd.isna(row.get("BOS", np.nan)):
                bos_list.append({
                    "type": "BOS_UP" if row["BOS"] == 1 else "BOS_DN",
                    "price": round(row.get("Level", df.loc[i, "close"]), 2),
                    "time": i.timestamp()
                })
            if not pd.isna(row.get("CHOCH", np.nan)):
                mss_list.append({
                    "type": "CHOCH_UP" if row["CHOCH"] == 1 else "CHOCH_DN",
                    "price": round(row.get("Level", df.loc[i, "close"]), 2),
                    "time": i.timestamp()
                })
    except Exception:
        pass

    # 3. FVG (Fair Value Gaps)
    fvg_list = []
    try:
        fvg_result = smc.fvg(df, join_consecutive=True)
        for i, row in fvg_result.iterrows():
            if not pd.isna(row.get("FVG", np.nan)):
                mitigated = int(row.get("MitigatedIndex", 0))
                fvg_list.append({
                    "type": "FVG_UP" if row["FVG"] == 1 else "FVG_DN",
                    "top": round(row["Top"], 2),
                    "bottom": round(row["Bottom"], 2),
                    "midpoint": round((row["Top"] + row["Bottom"]) / 2, 2),
                    "time": i.timestamp(),
                    "mitigated": mitigated > 0
                })
    except Exception:
        pass
    fvg_active = [f for f in fvg_list if not f["mitigated"]]

    # 4. Order Blocks
    ob_list = []
    try:
        ob_result = smc.ob(df, swings)
        for i, row in ob_result.iterrows():
            if not pd.isna(row.get("OB", np.nan)):
                mitigated = int(row.get("MitigatedIndex", 0))
                ob_list.append({
                    "type": "OB_BULL" if row["OB"] == 1 else "OB_BEAR",
                    "top": round(row["Top"], 2),
                    "bottom": round(row["Bottom"], 2),
                    "time": i.timestamp(),
                    "mitigated": mitigated > 0
                })
    except Exception:
        pass
    ob_active = [o for o in ob_list if not o["mitigated"]]

    # 5. Liquidity levels
    liq_list = []
    try:
        liq_result = smc.liquidity(df, swings)
        for i, row in liq_result.iterrows():
            if not pd.isna(row.get("Liquidity", np.nan)):
                liq_list.append({
                    "type": "LIQ_HIGH" if row["Liquidity"] == 1 else "LIQ_LOW",
                    "level": round(row.get("Level", df.loc[i, "close"]), 2),
                    "time": i.timestamp(),
                    "swept": not pd.isna(row.get("End", np.nan))
                })
    except Exception:
        pass

    # 6. Custom: Equal Highs / Equal Lows detection
    equal_levels = _detect_equal_levels(candles)

    # 7. Custom: Liquidity Sweep (stop hunt)
    sweeps = _detect_sweeps(candles, swing_highs, swing_lows)

    # Determine overall structure
    structure = "NEUTRAL"
    if bos_list:
        last = bos_list[-1]
        structure = "BULLISH" if last["type"] == "BOS_UP" else "BEARISH"
    if mss_list and mss_list[-1]["time"] > (bos_list[-1]["time"] if bos_list else 0):
        structure = "BULLISH" if mss_list[-1]["type"] == "CHOCH_UP" else "BEARISH"

    return {
        "structure": structure,
        "bos": bos_list[-10:],
        "mss": mss_list[-5:],
        "fvg": fvg_active[-10:],
        "ob": ob_active[-10:],
        "liquidity": liq_list[-10:],
        "sweeps": sweeps[-10:],
        "equal_levels": equal_levels[:15],
        "swing_highs": swing_highs[-5:],
        "swing_lows": swing_lows[-5:],
    }


# ─── Custom: Equal Highs/Lows ─────────────────────────
def _detect_equal_levels(candles: list[Candle], tolerance_pct: float = 0.001) -> list[dict]:
    levels = []
    n = len(candles)
    for i in range(n):
        for j in range(i + 3, min(i + 30, n)):
            h_diff = abs(candles[i].high - candles[j].high) / max(candles[i].high, 1)
            l_diff = abs(candles[i].low - candles[j].low) / max(candles[i].low, 1)
            if h_diff < tolerance_pct:
                levels.append({"type": "EQH", "price": round((candles[i].high + candles[j].high) / 2, 2),
                               "count": 2, "time": candles[j].timestamp})
            if l_diff < tolerance_pct:
                levels.append({"type": "EQL", "price": round((candles[i].low + candles[j].low) / 2, 2),
                               "count": 2, "time": candles[j].timestamp})
    # Merge clusters
    if not levels:
        return []
    merged = sorted(levels, key=lambda x: x["price"])
    result = [merged[0]]
    for lv in merged[1:]:
        if abs(lv["price"] - result[-1]["price"]) / max(result[-1]["price"], 1) < 0.002:
            result[-1]["count"] += lv["count"]
            result[-1]["price"] = round((result[-1]["price"] + lv["price"]) / 2, 2)
        else:
            result.append(lv)
    return sorted(result, key=lambda x: -x["count"])[:20]


# ─── Custom: Sweep Detection ──────────────────────────
def _detect_sweeps(candles: list[Candle], swing_highs: list[dict], swing_lows: list[dict]) -> list[dict]:
    sweeps = []
    for i in range(2, len(candles)):
        for sh in swing_highs:
            if candles[i].high > sh["price"] and candles[i].close < sh["price"]:
                sweeps.append({"type": "SWEEP_HIGH", "sweep_price": round(candles[i].high, 2),
                               "level": sh["price"], "time": candles[i].timestamp, "bias": "BEARISH"})
                break
        for sl in swing_lows:
            if candles[i].low < sl["price"] and candles[i].close > sl["price"]:
                sweeps.append({"type": "SWEEP_LOW", "sweep_price": round(candles[i].low, 2),
                               "level": sl["price"], "time": candles[i].timestamp, "bias": "BULLISH"})
                break
    return sweeps
