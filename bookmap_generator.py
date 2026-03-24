"""
bookmap_generator.py — ATTRAOS Hub v1.1
Vẽ biểu đồ nến Nhật thật (Japanese Candlestick) với Volume + CVD overlay.
Không còn heatmap mù mờ — đây là chart thật từ dữ liệu MT5.
"""

import os
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import matplotlib.gridspec as gridspec
from datetime import datetime
from typing import List, Optional

OUTPUT_PATH = "/tmp/bookmap_latest.png"

# Màu sắc premium
COLOR_BG       = "#0D1117"
COLOR_CARD     = "#161B22"
COLOR_BULL     = "#26a641"   # Nến tăng - xanh GitHub
COLOR_BEAR     = "#da3633"   # Nến giảm - đỏ
COLOR_BULL_CVD = "#58D68D"
COLOR_BEAR_CVD = "#E74C3C"
COLOR_WICK     = "#8E9BAE"
COLOR_VOL_BULL = "#1a6b30"
COLOR_VOL_BEAR = "#7a1e1e"
COLOR_TEXT     = "#C9D1D9"
COLOR_MUTED    = "#6E7681"
COLOR_GOLD     = "#FFC107"
COLOR_GRID     = "#21262D"
COLOR_SIGNAL   = "#F0960A"


def parse_candles(raw: list) -> list:
    result = []
    for c in raw:
        try:
            result.append({
                "t": int(c.get("t", 0)),
                "o": float(c.get("o", 0)),
                "h": float(c.get("h", 0)),
                "l": float(c.get("l", 0)),
                "c": float(c.get("c", 0)),
                "v": max(float(c.get("v", 1)), 1.0),
            })
        except Exception:
            pass
    return result


def compute_cvd(candles: list) -> list:
    """CVD tích lũy từ volume delta thật (không random)."""
    cvd = 0.0
    series = []
    for c in candles:
        body = abs(c["c"] - c["o"])
        rng  = max(c["h"] - c["l"], 0.0001)
        body_ratio = body / rng
        delta = (1 if c["c"] >= c["o"] else -1) * c["v"] * body_ratio
        cvd  += delta
        series.append(cvd)
    return series


def find_signals(candles: list) -> list:
    """Tìm vị trí các signal để annotate trên chart."""
    signals = []
    if len(candles) < 10:
        return signals

    vols = [c["v"] for c in candles]
    avg_vol = np.mean(vols)
    
    for i in range(5, len(candles)):
        c = candles[i]
        body = abs(c["c"] - c["o"])
        rng  = max(c["h"] - c["l"], 0.0001)
        body_ratio = body / rng
        vol_ratio  = c["v"] / avg_vol

        # Absorption: vol cao + body nhỏ
        if vol_ratio > 1.8 and body_ratio < 0.25:
            signals.append((i, "ABS", "🧱", COLOR_GOLD))

        # Volume spike / climax
        if vol_ratio > 2.8:
            icon = "🔥" if c["c"] >= c["o"] else "❄️"
            signals.append((i, "VOL", icon, COLOR_SIGNAL))

        # Stop Hunt: wick dài bất thường
        upper_wick = c["h"] - max(c["o"], c["c"])
        lower_wick = min(c["o"], c["c"]) - c["l"]
        if upper_wick / rng > 0.6 and vol_ratio > 1.3:
            signals.append((i, "HUNT_UP", "🎯", "#ff6b9d"))
        elif lower_wick / rng > 0.6 and vol_ratio > 1.3:
            signals.append((i, "HUNT_DN", "🎯", "#6bcbff"))

    return signals[-8:]  # Chỉ show 8 signals gần nhất


def generate_chart(
    candles_m15: list,
    symbol: str = "XAUUSD",
    output_path: str = OUTPUT_PATH,
    n_candles: int = 60,
) -> Optional[str]:
    """
    Vẽ biểu đồ nến thật gồm 3 panel:
    - Panel 1 (lớn): Japanese Candlestick chart + EMA20
    - Panel 2 (nhỏ): Volume histogram (xanh/đỏ theo hướng nến)
    - Panel 3 (nhỏ): CVD line (Cumulative Volume Delta thật)
    """
    candles = parse_candles(candles_m15)
    if len(candles) < 10:
        return None

    # Lấy N nến gần nhất
    candles = candles[-n_candles:]
    n = len(candles)
    xs = list(range(n))

    opens  = [c["o"] for c in candles]
    highs  = [c["h"] for c in candles]
    lows   = [c["l"] for c in candles]
    closes = [c["c"] for c in candles]
    vols   = [c["v"] for c in candles]
    times  = [c["t"] for c in candles]
    cvd    = compute_cvd(candles)
    signals = find_signals(candles)

    # EMA 20
    def ema(prices, period):
        result = [None] * period
        k = 2 / (period + 1)
        val = np.mean(prices[:period])
        result = [None] * (period - 1) + [val]
        for i in range(period, len(prices)):
            val = prices[i] * k + val * (1 - k)
            result.append(val)
        return result

    ema20 = ema(closes, min(20, n))
    ema50 = ema(closes, min(50, n))

    # ── Figure setup ──────────────────────────────────────────────────────
    fig = plt.figure(figsize=(18, 10), facecolor=COLOR_BG)
    fig.patch.set_facecolor(COLOR_BG)

    gs = gridspec.GridSpec(3, 1, height_ratios=[5, 1.5, 1.5],
                           hspace=0.06, left=0.06, right=0.97,
                           top=0.92, bottom=0.07)

    ax_candle = fig.add_subplot(gs[0])
    ax_vol    = fig.add_subplot(gs[1], sharex=ax_candle)
    ax_cvd    = fig.add_subplot(gs[2], sharex=ax_candle)

    for ax in [ax_candle, ax_vol, ax_cvd]:
        ax.set_facecolor(COLOR_CARD)
        ax.tick_params(colors=COLOR_MUTED, labelsize=8)
        ax.yaxis.label.set_color(COLOR_MUTED)
        for spine in ax.spines.values():
            spine.set_edgecolor(COLOR_GRID)
        ax.grid(True, color=COLOR_GRID, linewidth=0.5, alpha=0.6)

    # ── Candlestick ──────────────────────────────────────────────────────
    candle_width  = 0.6
    wick_width    = 0.8

    for i in xs:
        o, h, l, c_ = opens[i], highs[i], lows[i], closes[i]
        color  = COLOR_BULL if c_ >= o else COLOR_BEAR
        # Wick
        ax_candle.plot([i, i], [l, h], color=COLOR_WICK, linewidth=wick_width, alpha=0.7)
        # Body
        body_bottom = min(o, c_)
        body_height = max(abs(c_ - o), (h - l) * 0.005)  # Tối thiểu để thấy doji
        rect = mpatches.FancyBboxPatch(
            (i - candle_width / 2, body_bottom),
            candle_width, body_height,
            boxstyle="square,pad=0",
            facecolor=color, edgecolor=color, linewidth=0.3, alpha=0.9
        )
        ax_candle.add_patch(rect)

    # EMA lines
    ema_xs20 = [i for i, v in enumerate(ema20) if v is not None]
    ema_ys20 = [ema20[i] for i in ema_xs20]
    if ema_xs20:
        ax_candle.plot(ema_xs20, ema_ys20, color="#58a6ff", linewidth=1.2,
                       alpha=0.8, label="EMA 20", zorder=5)

    ema_xs50 = [i for i, v in enumerate(ema50) if v is not None]
    ema_ys50 = [ema50[i] for i in ema_xs50]
    if ema_xs50:
        ax_candle.plot(ema_xs50, ema_ys50, color="#e3b341", linewidth=1.0,
                       alpha=0.7, linestyle="--", label="EMA 50", zorder=4)

    # Signal annotations
    for idx, sig_type, icon, color in signals:
        if idx < n:
            y_pos = highs[idx] * 1.001 if "UP" in sig_type or sig_type in ["VOL", "ABS"] else lows[idx] * 0.999
            ax_candle.annotate(
                icon,
                xy=(idx, y_pos),
                fontsize=10,
                ha="center", va="bottom",
                fontfamily="Apple Color Emoji"
            )

    # Price label tại nến cuối
    last_price = closes[-1]
    last_color = COLOR_BULL if closes[-1] >= opens[-1] else COLOR_BEAR
    ax_candle.axhline(y=last_price, color=last_color, linewidth=0.8, linestyle=":", alpha=0.9)
    ax_candle.text(n - 0.5, last_price, f"  {last_price:.2f}",
                   color=last_color, fontsize=9, fontweight="bold",
                   va="center", ha="left")

    ax_candle.set_xlim(-1, n + 1)
    ax_candle.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.1f}"))
    ax_candle.tick_params(labelbottom=False)
    ax_candle.legend(loc="upper left", fontsize=8,
                     facecolor=COLOR_CARD, edgecolor=COLOR_GRID,
                     labelcolor=COLOR_TEXT, framealpha=0.9)

    # ── Volume bars ──────────────────────────────────────────────────────
    for i in xs:
        color = COLOR_VOL_BULL if closes[i] >= opens[i] else COLOR_VOL_BEAR
        ax_vol.bar(i, vols[i], width=candle_width, color=color, alpha=0.85)

    avg_vol = np.mean(vols)
    ax_vol.axhline(avg_vol, color=COLOR_MUTED, linewidth=0.7, linestyle="--", alpha=0.7)
    ax_vol.set_ylabel("VOL", color=COLOR_MUTED, fontsize=7)
    ax_vol.tick_params(labelbottom=False)
    ax_vol.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v/1000:.0f}k" if v > 1000 else f"{v:.0f}"))

    # ── CVD line ─────────────────────────────────────────────────────────
    cvd_color_arr = [COLOR_BULL_CVD if cvd[i] >= (cvd[i-1] if i > 0 else 0) else COLOR_BEAR_CVD for i in range(n)]
    ax_cvd.fill_between(xs, cvd, 0, where=[c > 0 for c in cvd],
                        color=COLOR_BULL_CVD, alpha=0.25)
    ax_cvd.fill_between(xs, cvd, 0, where=[c < 0 for c in cvd],
                        color=COLOR_BEAR_CVD, alpha=0.25)
    ax_cvd.plot(xs, cvd, color=COLOR_GOLD, linewidth=1.5, alpha=0.9)
    ax_cvd.axhline(0, color=COLOR_MUTED, linewidth=0.6, alpha=0.5)
    ax_cvd.set_ylabel("CVD", color=COLOR_MUTED, fontsize=7)

    # CVD label
    cvd_now = cvd[-1]
    cvd_color = COLOR_BULL_CVD if cvd_now >= 0 else COLOR_BEAR_CVD
    ax_cvd.text(n - 0.5, cvd_now, f"  {cvd_now:+.0f}",
                color=cvd_color, fontsize=8, fontweight="bold", va="center")

    # ── X-axis labels (time) ─────────────────────────────────────────────
    step = max(n // 8, 1)
    tick_pos   = list(range(0, n, step))
    tick_labels = []
    for i in tick_pos:
        try:
            dt = datetime.utcfromtimestamp(times[i])
            tick_labels.append(dt.strftime("%m/%d\n%H:%M"))
        except Exception:
            tick_labels.append(str(i))

    ax_cvd.set_xticks(tick_pos)
    ax_cvd.set_xticklabels(tick_labels, fontsize=7, color=COLOR_MUTED)

    # ── Title ─────────────────────────────────────────────────────────────
    now_str  = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    price_str = f"{last_price:.2f}"
    change    = closes[-1] - opens[0]
    pct       = change / opens[0] * 100
    change_str = f"{change:+.2f} ({pct:+.2f}%)"
    change_col = COLOR_BULL if change >= 0 else COLOR_BEAR

    fig.text(0.06, 0.955, f"{symbol}", fontsize=16, fontweight="bold",
             color=COLOR_TEXT, va="top")
    fig.text(0.18, 0.958, price_str, fontsize=14, fontweight="bold",
             color=last_color, va="top")
    fig.text(0.30, 0.958, change_str, fontsize=11,
             color=change_col, va="top")
    fig.text(0.97, 0.958, f"M15 • {now_str} • ATTRAOS Hub v1.1",
             fontsize=8, color=COLOR_MUTED, va="top", ha="right")

    # ── Save ──────────────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(output_path), exist_ok=True) if os.path.dirname(output_path) else None
    plt.savefig(output_path, dpi=150, bbox_inches="tight",
                facecolor=COLOR_BG, edgecolor="none")
    plt.close(fig)
    return output_path


# ─── CLI test ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Test với data mẫu
    import random
    random.seed(42)
    price = 3300.0
    candles = []
    for i in range(80):
        o = price
        c = o + random.gauss(0, 3)
        h = max(o, c) + abs(random.gauss(0, 1.5))
        l = min(o, c) - abs(random.gauss(0, 1.5))
        v = abs(random.gauss(500, 200))
        candles.append({"t": 1700000000 + i * 900, "o": o, "h": h, "l": l, "c": c, "v": v})
        price = c

    out = generate_chart(candles, "XAUUSD_TEST")
    print(f"Chart saved: {out}")
