"""
bookmap_council.py — ATTRAOS Hub v1.1
═══════════════════════════════════════════════════════════════════
BOOKMAP AI COUNCIL — Hội Đồng Phân Tích Chuyên Sâu

3-stage pipeline chạy hoàn toàn trên VPS, không cần iOS code:
  Stage 1 — FLOOR TRADER (Order Flow Expert): Đọc dấu vết tổ chức
  Stage 2 — MARKET PROFILE ANALYST: Phân tích cấu trúc auction
  Stage 3 — RISK ARBITRAGE DESK: Ra lệnh Entry / SL / TP / R:R

AI Fallback: Gemini → DeepSeek → GPT-4o-mini
═══════════════════════════════════════════════════════════════════
"""

import os
import json
import re
import asyncio
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Optional

# ─── Cache & Config ───────────────────────────────────────────────────────────
_council_cache: dict = {}
_council_lock  = asyncio.Lock()
_executor      = ThreadPoolExecutor(max_workers=3)

SYMBOLS          = ["XAUUSD", "XAGUSD", "DXY", "BTCUSD"]
REFRESH_INTERVAL = 300   # 5 phút


# ─── AI Fallback Chain ────────────────────────────────────────────────────────

def _call_ai_sync(prompt: str, system: str = "") -> tuple[str, str]:
    """
    Gọi AI đồng bộ theo chain: Gemini → DeepSeek → GPT.
    Trả về (text, source_name).
    """
    errors = []

    # 1 ── Gemini
    key = os.environ.get("GEMINI_API_KEY", "")
    if key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=key)
            m = genai.GenerativeModel("gemini-2.0-flash")
            full_prompt = f"{system}\n\n{prompt}" if system else prompt
            r = m.generate_content(full_prompt)
            return r.text.strip(), "Gemini"
        except Exception as e:
            errors.append(f"Gemini={e}")

    # 2 ── DeepSeek (OpenAI-compatible)
    key = os.environ.get("DEEPSEEK_API_KEY", "")
    if key:
        try:
            import openai as _oai
            c = _oai.OpenAI(api_key=key, base_url="https://api.deepseek.com/v1")
            msgs = []
            if system: msgs.append({"role": "system", "content": system})
            msgs.append({"role": "user", "content": prompt})
            r = c.chat.completions.create(model="deepseek-chat", messages=msgs,
                                          max_tokens=700, temperature=0.2)
            return r.choices[0].message.content.strip(), "DeepSeek"
        except Exception as e:
            errors.append(f"DeepSeek={e}")

    # 3 ── OpenAI GPT
    key = os.environ.get("OPENAI_API_KEY", "")
    if key:
        try:
            import openai as _oai
            c = _oai.OpenAI(api_key=key)
            msgs = []
            if system: msgs.append({"role": "system", "content": system})
            msgs.append({"role": "user", "content": prompt})
            r = c.chat.completions.create(model="gpt-4o-mini", messages=msgs,
                                          max_tokens=700, temperature=0.2)
            return r.choices[0].message.content.strip(), "GPT-4o-mini"
        except Exception as e:
            errors.append(f"GPT={e}")

    raise RuntimeError("All AI failed: " + " | ".join(errors))


async def call_ai(prompt: str, system: str = "", timeout: int = 25) -> tuple[str, str]:
    loop = asyncio.get_event_loop()
    return await asyncio.wait_for(
        loop.run_in_executor(_executor, _call_ai_sync, prompt, system),
        timeout=timeout
    )


# ─── Stage Prompts ────────────────────────────────────────────────────────────

FLOOR_TRADER_SYSTEM = """You are a veteran FLOOR TRADER with 20 years at CME Group.
You specialize in reading ORDER FLOW — the real-time footprint of institutional activity
hidden within the price tape. Your edge is detecting:
  • ABSORPTION: When market makers silently absorb aggressive orders at a level,
    indicating a major player defending a price zone.
  • ICEBERG ORDERS: Hidden supply/demand that repeatedly refreshes, preventing
    price from moving through a level.
  • STOP HUNTS: Engineered liquidity grabs where smart money sweeps retail stops
    before reversing — the classic "shake and bake" pattern.
  • CVD DIVERGENCE: When Cumulative Volume Delta disagrees with price direction,
    signaling that the move is NOT supported by real buying/selling pressure.

You think in terms of WHO is trapped, WHERE liquidity sits, and HOW institutional
players will force price to move next. You do NOT use conventional indicators.
You speak in precise, professional terms. Your analysis is data-driven and specific.
Always respond in Vietnamese."""

MARKET_PROFILE_ANALYST_SYSTEM = """You are a MARKET PROFILE ANALYST trained in
J. Peter Steidlmayer's Auction Theory and Volume Profile methodology.

You interpret markets as an ongoing auction mechanism where price seeks FAIR VALUE
and rejects EXCESS. Your framework:
  • POC (Point of Control): The price printed most frequently — the market's
    definition of 'fair value' for the current period.
  • VALUE AREA (70% rule): The price range containing 70% of volume — accepted
    value by the majority of participants.
  • VAH/VAL as dynamic support/resistance: Price returning to value = responsive
    opportunity; Price breaking value = initiative move.
  • SINGLE PRINTS & LEDGES: Thin areas in the profile = fast markets ahead.
  • PROFILE SHAPE: Bell curve = balanced; P/b-shape = directional imbalance.

You synthesize Volume Profile structure with Order Flow signals to identify
HIGH-PROBABILITY zones where price is likely to react. Always respond in Vietnamese."""

RISK_DESK_SYSTEM = """You are the HEAD OF RISK at a proprietary trading firm.
Your job is to synthesize intelligence from the Floor Trader and Market Profile Analyst
into ONE executable trade recommendation with exact parameters.

Your output must be institutional-grade:
  • Entry precision: Exact price or specific trigger condition
  • SL placement: Always BEYOND structural levels (not arbitrary pips)
  • TP levels: Based on next Profile structure (VAH/VAL/POC of adjacent sessions)
  • Risk-Reward: Minimum 1:2, prefer 1:3+
  • Confidence: Honest assessment based on confluence of signals

You REJECT low-quality setups. If signals conflict or context is unclear,
you say WAIT and explain why. Capital preservation is priority #1.
You speak in precise, actionable terms with Vietnamese output.

CRITICAL: Respond ONLY with valid JSON, no markdown, no explanation outside JSON."""


def build_floor_trader_prompt(symbol, price, bias, cvd, buy_pct, sell_pct, signals):
    sig_text = "\n".join([
        f"  [{s.get('type','?')}] {s.get('desc','')} (strength={s.get('strength',0):.0f})"
        for s in signals[:6]
    ]) or "  Không có tín hiệu Order Flow đặc biệt."

    return f"""Phân tích ORDER FLOW cho {symbol}:

TAPE READING:
  Giá hiện tại: {price:.4f}
  Xu hướng Delta tổng: {bias}
  CVD tích lũy: {cvd:+.2f}
  Áp lực phiên: MUA {buy_pct:.1f}% vs BÁN {sell_pct:.1f}%

FOOTPRINT SIGNALS PHÁT HIỆN:
{sig_text}

Nhiệm vụ: Dựa trên dấu vết Order Flow này, hãy:
1. Xác định ai đang KIỂM SOÁT thị trường (smart money hay retail)?
2. Phát hiện bẫy nào đang được dựng (bull trap / bear trap)?
3. Vùng giá nào đang có institutional interest (absorption cluster)?
4. CVD có xác nhận price action không? Có divergence không?

Trả lời 3-4 câu súc tích, chuyên nghiệp. Không dùng indicator thông thường."""


def build_profile_analyst_prompt(symbol, price, poc, vah, val, vp_min, vp_max, bias):
    poc_dist = ((price - poc) / poc * 100) if poc > 0 else 0
    va_width = vah - val if vah > val else 0

    position = "INSIDE VALUE AREA"
    if price > vah:
        position = f"ABOVE VALUE AREA (+{(price-vah):.2f} khỏi VAH)"
    elif price < val:
        position = f"BELOW VALUE AREA (-{(val-price):.2f} dưới VAL)"

    return f"""Phân tích MARKET PROFILE / VOLUME PROFILE cho {symbol}:

AUCTION STRUCTURE:
  Giá hiện tại: {price:.4f} → {position}
  POC (giá giao dịch nhiều nhất): {poc:.4f} (giá cách POC: {poc_dist:+.2f}%)
  VAH (Value Area High): {vah:.4f}
  VAL (Value Area Low):  {val:.4f}
  Value Area Width: {va_width:.2f} ({va_width/poc*100:.1f}% của POC)
  Session Range: {vp_min:.4f} → {vp_max:.4f}
  Xu hướng: {bias}

Nhiệm vụ: Phân tích theo Auction Theory:
1. Là cuộc đấu giá CÂN BẰNG hay MẤT CÂN BẰNG? Hình dạng profile nói gì?
2. Giá đang ở đâu trong cấu trúc — responsive hay initiative?
3. Trader nên kỳ vọng price return to value hay break out of value?
4. Level nào là HIGH-PROBABILITY reaction point tiếp theo?

Trả lời 3-4 câu chuyên nghiệp theo framework Steidlmayer. Không dùng RSI/MACD."""


def build_risk_desk_prompt(symbol, price, floor_analysis, profile_analysis, cvd, bias):
    return f"""Tổng hợp phân tích từ 2 chuyên gia và ra QUYẾT ĐỊNH GIAO DỊCH cho {symbol}:

FLOOR TRADER nói:
{floor_analysis}

MARKET PROFILE ANALYST nói:
{profile_analysis}

ĐIỀU KIỆN HIỆN TẠI:
  Giá: {price:.4f} | CVD: {cvd:+.2f} | Bias: {bias}

Nhiệm vụ: Ra quyết định cuối cùng dựa trên sự đồng thuận/xung đột của 2 chuyên gia.

Trả về JSON CHÍNH XÁC (không có text nào ngoài JSON):
{{
  "action": "BUY" | "SELL" | "WAIT",
  "entry": "<giá cụ thể hoặc điều kiện ví dụ: 'retest 4350.00'>",
  "sl": <số giá SL cụ thể>,
  "tp1": <TP1>,
  "tp2": <TP2>,
  "rr_ratio": "<ví dụ: 1:2.5>",
  "confidence": <0-100>,
  "setup_type": "<tên loại setup ví dụ: 'POC Absorption Reversal'>",
  "reasoning_vi": "<nhận định 2-3 câu chuyên nghiệp bằng tiếng Việt, tích hợp cả 2 quan điểm>",
  "invalidation": "<điều kiện invalidate setup, 1 câu>",
  "session_bias": "BULLISH" | "BEARISH" | "NEUTRAL"
}}"""


# ─── Volume Profile (nhanh, không cần matplotlib) ─────────────────────────────

def quick_volume_profile(candles: list) -> dict:
    if not candles or len(candles) < 5:
        c = candles[-1] if candles else {}
        p = c.get("c", 0)
        return {"poc": p, "vah": p, "val": p, "vp_min": p, "vp_max": p}

    vp_min = min(c["l"] for c in candles)
    vp_max = max(c["h"] for c in candles)
    rng = vp_max - vp_min
    if rng < 0.0001:
        p = candles[-1]["c"]
        return {"poc": p, "vah": p, "val": p, "vp_min": vp_min, "vp_max": vp_max}

    n_levels = 80
    tick = rng / n_levels
    profile = {vp_min + i * tick: 0.0 for i in range(n_levels + 1)}

    for c in candles:
        cr = max(c["h"] - c["l"], 0.0001)
        for lvl in profile:
            if c["l"] <= lvl <= c["h"]:
                w = 1.0 - abs(lvl - c["c"]) / cr * 0.5
                profile[lvl] += c["v"] * w * (tick / cr)

    poc = max(profile, key=profile.get)
    total = sum(profile.values())
    target = total * 0.70
    sorted_lvls = sorted(profile.items(), key=lambda x: x[1], reverse=True)
    cumvol, va = 0.0, []
    for p, v in sorted_lvls:
        cumvol += v; va.append(p)
        if cumvol >= target: break

    return {
        "poc": round(poc, 5),
        "vah": round(max(va), 5) if va else round(vp_max, 5),
        "val": round(min(va), 5) if va else round(vp_min, 5),
        "vp_min": round(vp_min, 5),
        "vp_max": round(vp_max, 5),
    }


# ─── Main Council Analysis ────────────────────────────────────────────────────

async def run_council_for_symbol(symbol: str, market_service) -> dict:
    """
    3-stage AI Council pipeline cho 1 symbol.
    """
    from order_flow_analyzer import OrderFlowAnalyzer, snapshot_to_dict

    # ── Symbol mapping ──────────────────────────────────────────────────────
    sym = symbol.replace("/", "").upper()
    api_map = {
        "XAUUSD": "XAU/USD", "XAGUSD": "XAG/USD",
        "BTCUSD": "BTC/USD", "DXY": "DXY", "USDX": "DXY",
    }
    api_sym = api_map.get(sym, f"{sym[:3]}/{sym[3:]}" if len(sym) == 6 else sym)

    # ── Lấy candles ────────────────────────────────────────────────────────
    raw_m15 = await market_service.fetch_candles(api_sym, "15m", 80)
    raw_h1  = await market_service.fetch_candles(api_sym, "1h",  30)

    def fmt(lst):
        out = []
        for c in lst:
            d = c.to_dict() if hasattr(c, "to_dict") else c
            out.append({
                "t": int(d.get("time", d.get("t", 0))),
                "o": float(d.get("open",   d.get("o", 0))),
                "h": float(d.get("high",   d.get("h", 0))),
                "l": float(d.get("low",    d.get("l", 0))),
                "c": float(d.get("close",  d.get("c", 0))),
                "v": max(float(d.get("volume", d.get("v", 1)) or 1), 1.0),
            })
        return out

    m15 = fmt(raw_m15)
    h1  = fmt(raw_h1)

    if len(m15) < 10:
        return {"symbol": symbol, "error": "Không đủ candle data"}

    # ── Order Flow Analysis ─────────────────────────────────────────────────
    snap    = OrderFlowAnalyzer(candles_m15=m15, candles_h1=h1, symbol=symbol).analyze()
    snap_d  = snapshot_to_dict(snap)
    price   = snap_d.get("current_price", 0) or (m15[-1]["c"] if m15 else 0)
    bias    = snap_d.get("overall_bias", "NEUTRAL")
    cvd     = snap_d.get("delta", {}).get("cvd", 0)
    buy_pct = snap_d.get("delta", {}).get("buy_pct", 50)
    sell_pct= snap_d.get("delta", {}).get("sell_pct", 50)
    signals = snap_d.get("signals", [])

    # ── Volume Profile ──────────────────────────────────────────────────────
    vp = quick_volume_profile(m15)

    # ── Decide whether to fire AI ───────────────────────────────────────────
    run_ai = bias != "NEUTRAL" or len(signals) > 0 or abs(cvd) > 500

    if not run_ai:
        result = {
            "symbol": symbol, "price": round(price, 4), "bias": bias,
            "signal_count": 0, "cvd": round(cvd, 2),
            "buy_pct": buy_pct, "sell_pct": sell_pct,
            "signals": [], "volume_profile": vp,
            "council": {
                "action": "WAIT", "confidence": 0,
                "setup_type": "No Setup",
                "reasoning_vi": "Không có tín hiệu Order Flow đủ mạnh. Tiếp tục theo dõi.",
                "entry": "-", "sl": None, "tp1": None, "tp2": None,
                "rr_ratio": "-", "invalidation": "-", "session_bias": "NEUTRAL",
            },
            "ai_source": "rule", "stage": "skipped",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        return result

    # ── Stage 1: Floor Trader ───────────────────────────────────────────────
    p1 = build_floor_trader_prompt(symbol, price, bias, cvd, buy_pct, sell_pct, signals)
    try:
        floor_text, src1 = await call_ai(p1, FLOOR_TRADER_SYSTEM)
    except Exception as e:
        floor_text = f"Floor Trader unavailable: {e}"
        src1 = "error"

    # ── Stage 2: Market Profile Analyst ────────────────────────────────────
    p2 = build_profile_analyst_prompt(
        symbol, price,
        vp["poc"], vp["vah"], vp["val"],
        vp["vp_min"], vp["vp_max"], bias
    )
    try:
        profile_text, src2 = await call_ai(p2, MARKET_PROFILE_ANALYST_SYSTEM)
    except Exception as e:
        profile_text = f"Profile Analyst unavailable: {e}"
        src2 = "error"

    # ── Stage 3: Risk Desk → JSON decision ─────────────────────────────────
    p3 = build_risk_desk_prompt(symbol, price, floor_text, profile_text, cvd, bias)
    try:
        risk_text, src3 = await call_ai(p3, RISK_DESK_SYSTEM)
        m = re.search(r'\{[\s\S]*\}', risk_text)
        council_json = json.loads(m.group()) if m else {"action": "WAIT", "error": "parse_fail"}
    except Exception as e:
        council_json = {"action": "WAIT", "confidence": 0,
                        "reasoning_vi": f"Risk Desk error: {e}"}
        src3 = "error"

    ai_source = f"{src1}/{src2}/{src3}"

    return {
        "symbol": symbol,
        "price": round(price, 4),
        "bias": bias,
        "signal_count": len(signals),
        "cvd": round(cvd, 2),
        "buy_pct": round(buy_pct, 1),
        "sell_pct": round(sell_pct, 1),
        "signals": signals[:3],
        "volume_profile": vp,
        "council": council_json,
        "floor_analysis": floor_text,
        "profile_analysis": profile_text,
        "ai_source": ai_source,
        "stage": "3-stage",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


# ─── Background Loop ──────────────────────────────────────────────────────────

async def council_background_loop(market_service):
    """
    Chạy liên tục: mỗi 5 phút phân tích tất cả symbols,
    iOS app poll /orderflow/council là thấy kết quả mới ngay.
    """
    global _council_cache
    print("[Council] 3-Stage AI Council started — refresh every 5 min")

    while True:
        for symbol in SYMBOLS:
            try:
                result = await run_council_for_symbol(symbol, market_service)
                async with _council_lock:
                    _council_cache[symbol] = result
                c = result.get("council", {})
                print(f"[Council] {symbol}: {c.get('action','?')} "
                      f"conf={c.get('confidence','?')} "
                      f"setup={c.get('setup_type','?')} "
                      f"ai={result.get('ai_source','?')}")
            except Exception as e:
                print(f"[Council] ERROR {symbol}: {e}")
                traceback.print_exc()

            await asyncio.sleep(2)   # Tránh rate limit giữa các symbol

        await asyncio.sleep(REFRESH_INTERVAL)


def get_council_cache() -> dict:
    return _council_cache
