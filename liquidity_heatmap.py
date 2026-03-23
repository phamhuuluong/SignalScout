"""
Signal Scout — Liquidity Heatmap
The feature 95% of trading apps are missing!
Clusters stop-loss levels, equal levels, and sweep probability zones.
"""
from market_data import Candle
from smc_detector import analyze_smc


def generate_heatmap(candles: list[Candle], current_price: float = 0) -> dict:
    """
    Generate liquidity heatmap data.
    Returns price levels with density scores indicating where stops cluster.
    """
    if len(candles) < 20:
        return {"levels": [], "zones": []}

    smc_data = analyze_smc(candles)
    if current_price == 0:
        current_price = candles[-1].close

    levels: list[dict] = []
    zones: list[dict] = []

    # 1. Equal Highs/Lows → high liquidity areas (stop loss clusters)
    for eq in smc_data.get("equal_levels", []):
        density = min(eq["count"] * 20, 100)
        levels.append({
            "price": eq["price"],
            "type": eq["type"],
            "density": density,
            "label": f"{'Equal Highs' if eq['type'] == 'EQH' else 'Equal Lows'} x{eq['count']}",
            "bias": "SELL" if eq["type"] == "EQH" else "BUY",
            "distance_pct": round(abs(eq["price"] - current_price) / current_price * 100, 2)
        })

    # 2. Unfilled FVG → magnetic zones
    for fvg in smc_data.get("fvg", []):
        density = 60
        zones.append({
            "top": fvg["top"],
            "bottom": fvg["bottom"],
            "midpoint": fvg["midpoint"],
            "type": fvg["type"],
            "density": density,
            "label": f"{'Bullish' if fvg['type'] == 'FVG_UP' else 'Bearish'} FVG",
            "bias": "BUY" if fvg["type"] == "FVG_UP" else "SELL"
        })

    # 3. Order Block zones → institutional interest
    for ob in smc_data.get("ob", []):
        density = 75
        zones.append({
            "top": ob["top"],
            "bottom": ob["bottom"],
            "midpoint": round((ob["top"] + ob["bottom"]) / 2, 2),
            "type": ob["type"],
            "density": density,
            "label": f"{'Bullish' if ob['type'] == 'OB_BULL' else 'Bearish'} OB",
            "bias": "BUY" if ob["type"] == "OB_BULL" else "SELL"
        })

    # 4. Library liquidity levels
    for liq in smc_data.get("liquidity", []):
        density = 85 if not liq["swept"] else 30
        levels.append({
            "price": liq["level"],
            "type": liq["type"],
            "density": density,
            "label": f"{'BSL' if liq['type'] == 'LIQ_HIGH' else 'SSL'} {'(swept)' if liq['swept'] else '(active)'}",
            "bias": "SELL" if liq["type"] == "LIQ_HIGH" else "BUY",
            "swept": liq["swept"],
            "distance_pct": round(abs(liq["level"] - current_price) / current_price * 100, 2)
        })

    # 5. Swing highs/lows → natural stop levels
    for sh in smc_data.get("swing_highs", []):
        levels.append({
            "price": sh["price"],
            "type": "SWING_HIGH",
            "density": 40,
            "label": "Swing High",
            "bias": "RESIST",
            "distance_pct": round(abs(sh["price"] - current_price) / current_price * 100, 2)
        })
    for sl in smc_data.get("swing_lows", []):
        levels.append({
            "price": sl["price"],
            "type": "SWING_LOW",
            "density": 40,
            "label": "Swing Low",
            "bias": "SUPPORT",
            "distance_pct": round(abs(sl["price"] - current_price) / current_price * 100, 2)
        })

    # 6. Recent sweeps → already hunted
    recent_sweeps = smc_data.get("sweeps", [])

    # Sort by density (strongest first)
    levels.sort(key=lambda x: -x["density"])
    zones.sort(key=lambda x: -x["density"])

    # Identify the strongest upcoming liquidity targets
    above = [l for l in levels if l["price"] > current_price and not l.get("swept", False)]
    below = [l for l in levels if l["price"] < current_price and not l.get("swept", False)]

    targets = {
        "above": above[:3],
        "below": below[:3],
    }

    return {
        "current_price": round(current_price, 2),
        "levels": levels[:20],
        "zones": zones[:10],
        "targets": targets,
        "sweeps": recent_sweeps,
        "summary": _generate_summary(levels, zones, current_price, recent_sweeps)
    }


def _generate_summary(levels, zones, price, sweeps) -> str:
    """Human-readable summary of liquidity landscape"""
    parts = []
    above = [l for l in levels if l["price"] > price and l["density"] >= 60]
    below = [l for l in levels if l["price"] < price and l["density"] >= 60]

    if above:
        parts.append(f"⬆️ {len(above)} mức thanh khoản phía trên (BSL)")
    if below:
        parts.append(f"⬇️ {len(below)} mức thanh khoản phía dưới (SSL)")
    if zones:
        bull_zones = [z for z in zones if z["bias"] == "BUY"]
        bear_zones = [z for z in zones if z["bias"] == "SELL"]
        if bull_zones:
            parts.append(f"🟢 {len(bull_zones)} vùng demand (OB/FVG)")
        if bear_zones:
            parts.append(f"🔴 {len(bear_zones)} vùng supply (OB/FVG)")
    if sweeps:
        parts.append(f"🎯 {len(sweeps)} sweep gần đây")

    return " | ".join(parts) if parts else "Chưa có dữ liệu liquidity"
