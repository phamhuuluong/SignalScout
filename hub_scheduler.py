"""
hub_scheduler.py — Background Scheduler for ATTRAOS Hub
Council AI runs server-side every 5 min using LIVE MT5 data.
All users see same cached result — no per-user AI calls needed.
Users need own API key / Premium to trigger manually on iOS.
"""
import asyncio
import json
import os
import logging
from datetime import datetime, timezone

logger = logging.getLogger("hub_scheduler")

# ── Shared result cache (in-memory) ───────────────────────────────────────
_broadcast_cache: dict = {
    "signals": {},          # {asset: full signal dict}
    "council": {},          # {asset: council_signal with Entry/SL/TP}
    "news_summary": "",     # B1 result from hub
    "community_summary": "",# B2 result from hub
    "last_council_run": None,
    "last_news_run": None,
    "next_council_run": None,
}

ASSETS_TO_SCAN  = os.getenv("BROADCAST_ASSETS", "XAUUSD").split(",")
# Council runs every 5–10 min (configurable), news/community every 30 min
COUNCIL_INTERVAL = int(os.getenv("COUNCIL_INTERVAL_MIN", "7")) * 60   # 7 min default
NEWS_INTERVAL    = int(os.getenv("NEWS_INTERVAL_MIN", "30")) * 60     # 30 min


def get_broadcast_cache() -> dict:
    """iOS app polls this to get latest broadcast result."""
    return _broadcast_cache


def get_council_signal(asset: str = "XAUUSD") -> dict:
    """Return latest council signal for an asset."""
    return _broadcast_cache["council"].get(asset.upper(), {})


# ── Council (B3) Auto-Run ─────────────────────────────────────────────────

async def run_council_broadcast():
    """
    Every COUNCIL_INTERVAL seconds:
    3-round AI debate (Server-side, single shared result for all users):
    Round 1 (Gemini): Phân tích MT5 + news + community → quan điểm sơ bộ
    Round 2 (DeepSeek): Phản biện Gemini → quan điểm riêng
    Round 3 (Gemini/Judge): Tổng hợp → phán quyết cuối + JSON Entry/SL/TP
    """
    await asyncio.sleep(30)

    while True:
        try:
            logger.info(f"🏛️ Council 3-round debate for {ASSETS_TO_SCAN}")
            from hub_ai import call_gemini, call_deepseek
            from hub_database import SessionLocal, get_config

            db = SessionLocal()
            ai_cfg = get_config(db, "ai", {})
            db.close()
            temp = ai_cfg.get("temperature", 0.2)

            for asset in ASSETS_TO_SCAN:
                try:
                    mt5_ctx = _get_mt5_context(asset)
                    if not mt5_ctx:
                        logger.warning(f"⚠️ No MT5 data for {asset}")
                        continue

                    news_ctx      = _broadcast_cache.get("news_summary", "")
                    community_ctx = _broadcast_cache.get("community_summary", "")
                    prev          = _broadcast_cache["council"].get(asset, {})
                    prev_txt = (
                        f"Lần trước: {prev.get('decision','NONE')} "
                        f"| Entry {prev.get('entry',0)} | {prev.get('confidence',0)}%"
                    ) if prev else ""

                    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

                    newline = "\n"
                    prev_section = (f"=== LẦN TRƯỚC ==={newline}" + prev_txt) if prev_txt else ""
                    base = f"""Asset: {asset} | {now}
=== DỮ LIỆU MT5 (THỰC TẾ) ===
{mt5_ctx}
=== TIN TỨC (B1) ===
{news_ctx[:600] if news_ctx else "Chưa có."}
=== CỘNG ĐỒNG (B2) ===
{community_ctx[:400] if community_ctx else "Chưa có."}
{prev_section}"""

                    # ── Round 1: Gemini ──
                    r1_system = (
                        f"Bạn là chuyên gia phân tích {asset}. "
                        "Phân tích kỹ thuật + fundamentals, đưa ra quan điểm BUY/SELL/NONE và lý do. "
                        "KHÔNG cần JSON ở vòng này."
                    )
                    r1_prompt = f"""{base}

Nhiệm vụ (Vòng 1): Phân tích xu hướng HTF, vùng kỹ thuật (OB/FVG/BOS), RSI/ADX.
Nêu quan điểm: nên BUY, SELL hay chờ. Entry/SL/TP đề xuất sơ bộ. 4-6 câu tiếng Việt."""
                    round1 = await call_gemini(r1_system, r1_prompt, temp)
                    logger.info(f"  ✅ Round 1 (Gemini) done for {asset}")

                    # ── Round 2: DeepSeek phản biện ──
                    r2_system = (
                        f"Bạn là AI phản biện độc lập cho {asset}. "
                        "Đọc phân tích của Gemini và đưa ra quan điểm riêng. KHÔNG cần JSON."
                    )
                    r2_prompt = f"""{base}

=== Ý KIẾN GEMINI (VÒNG 1) ===
{round1}

Nhiệm vụ (Vòng 2): Phản biện Gemini. Đồng ý hay không? Yếu tố nào Gemini bỏ qua?
Quan điểm của bạn: BUY/SELL/NONE với Entry/SL/TP đề xuất? 3-5 câu tiếng Việt."""
                    round2 = await call_deepseek(r2_system, r2_prompt, temp)
                    logger.info(f"  ✅ Round 2 (DeepSeek) done for {asset}")

                    # ── Round 3: Judge (Gemini as arbiter) ──
                    r3_system = (
                        f"Bạn là TRỌNG TÀI phán quyết cuối cho {asset}. "
                        "Đọc cả 2 ý kiến. Ra phán quyết final. Output ONLY JSON, no markdown wrapper."
                    )
                    r3_prompt = f"""{base}

=== VÒNG 1 — GEMINI ===
{round1}

=== VÒNG 2 — DEEPSEEK (Phản Biện) ===
{round2}

Nhiệm vụ (Vòng 3 — Trọng Tài): 2 câu lý giải, xong output JSON:
{{"decision":"BUY|SELL|NONE","entry":0.0,"sl":0.0,"tp":0.0,"confidence":0,"reason":"Gemini=[...] DeepSeek=[...] → [kết luận]"}}
ONLY JSON output."""
                    round3 = await call_gemini(r3_system, r3_prompt, 0.1)
                    logger.info(f"  ✅ Round 3 (Judge) done for {asset}")

                    # ── Parse signal JSON ──
                    signal = _parse_signal_json(round3)
                    signal["asset"] = asset
                    signal["debate"] = {
                        "round1_gemini": round1[:500],
                        "round2_deepseek": round2[:500],
                        "round3_judge": round3[:500],
                    }
                    signal["generated_at"] = now
                    signal["source"] = "hub_auto_3round"

                    _broadcast_cache["council"][asset] = signal
                    _broadcast_cache["signals"][asset] = {
                        **signal,
                        "direction": signal.get("decision", "NONE")
                    }

                    logger.info(
                        f"✅ Council {asset}: {signal.get('decision','NONE')} "
                        f"E={signal.get('entry',0)} | {signal.get('confidence',0)}%"
                    )

                except Exception as e:
                    logger.error(f"❌ Council error {asset}: {e}")

            _broadcast_cache["last_council_run"] = datetime.now(timezone.utc).isoformat()
            import datetime as dt_mod
            _broadcast_cache["next_council_run"] = (
                datetime.now(timezone.utc) + dt_mod.timedelta(seconds=COUNCIL_INTERVAL)
            ).isoformat()

        except Exception as e:
            logger.error(f"❌ Council broadcast error: {e}")

        await asyncio.sleep(COUNCIL_INTERVAL)


# ── B1: News Summary (30 min) ─────────────────────────────────────────────

async def run_news_broadcast():
    """Every 30 min: generate news + geopolitical summary for XAUUSD."""
    await asyncio.sleep(15)  # offset from council start

    while True:
        try:
            from hub_ai import call_gemini
            import datetime as dt_mod

            now = dt_mod.datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            mt5_ctx = _get_mt5_context("XAUUSD")

            system = (
                "Bạn là chuyên gia tổng hợp tin tức thị trường. "
                "Chỉ nêu sự kiện khách quan, KHÔNG đưa ra lệnh mua/bán."
            )
            prompt = f"""Thời gian: {now}
{("Dữ liệu MT5: " + mt5_ctx[:300]) if mt5_ctx else ""}

Tóm tắt các yếu tố đang ảnh hưởng đến XAUUSD hôm nay:
1. Lịch kinh tế quan trọng (FOMC, CPI, NFP nếu có)
2. Địa chính trị và chiến sự
3. Chính sách tiền tệ Fed/ECB/BOJ
4. DXY, trái phiếu, Bitcoin

Bullet points, tiếng Việt, ngắn gọn. KHÔNG có khuyến nghị lệnh."""

            summary = await call_gemini(system, prompt, temperature=0.4)
            _broadcast_cache["news_summary"] = summary
            _broadcast_cache["last_news_run"] = dt_mod.datetime.now(timezone.utc).isoformat()
            logger.info("📰 News summary updated")

        except Exception as e:
            logger.error(f"❌ News broadcast error: {e}")

        await asyncio.sleep(NEWS_INTERVAL)


# ── B2: Community Summary (30 min) ────────────────────────────────────────

async def run_community_broadcast():
    """Every 30 min: generate smart money / sentiment summary."""
    await asyncio.sleep(90)  # offset further

    while True:
        try:
            from hub_ai import call_gemini
            import datetime as dt_mod

            now = dt_mod.datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            mt5_ctx = _get_mt5_context("XAUUSD")

            system = (
                "Bạn là chuyên gia phân tích tâm lý thị trường và Cộng đồng. "
                "KHÔNG đưa ra lệnh mua/bán."
            )
            prompt = f"""Thời gian: {now}
{("Dữ liệu MT5: " + mt5_ctx[:300]) if mt5_ctx else ""}

Tổng hợp quan điểm cộng đồng về XAUUSD:
1. Smart money vs retail positioning (COT nếu biết)
2. Fear & Greed index và tâm lý chung
3. Nhận định đa số chuyên gia
4. Các vùng Liquidity trap / stop hunt cần lưu ý

Bullet points, tiếng Việt. KHÔNG có khuyến nghị lệnh."""

            summary = await call_gemini(system, prompt, temperature=0.4)
            _broadcast_cache["community_summary"] = summary
            _broadcast_cache["last_community_run"] = dt_mod.datetime.now(timezone.utc).isoformat()
            logger.info("🔍 Community summary updated")

        except Exception as e:
            logger.error(f"❌ Community broadcast error: {e}")

        await asyncio.sleep(NEWS_INTERVAL)


# ── Start All Tasks ───────────────────────────────────────────────────────

async def start_scheduler():
    """Called at app startup to launch all background tasks."""
    logger.info(
        f"⏰ Scheduler started — "
        f"Council every {COUNCIL_INTERVAL//60}min, "
        f"News/Community every {NEWS_INTERVAL//60}min"
    )
    asyncio.create_task(run_council_broadcast())
    asyncio.create_task(run_news_broadcast())
    asyncio.create_task(run_community_broadcast())


# ── Helpers ───────────────────────────────────────────────────────────────

def _get_mt5_context(asset: str) -> str:
    """Pull latest MT5 data from server _state and format for AI prompt."""
    try:
        # Import server state (same process)
        import server as _srv
        state = getattr(_srv, "_state", {})
        if not state:
            return ""

        sym = state.get("symbol", "")
        price = state.get("price", 0)
        acc = state.get("account", {})

        # Indicators computed by /mt5/context
        m15 = state.get("candles_m15", [])
        h1  = state.get("candles_h1",  [])
        h4  = state.get("candles_h4",  [])

        lines = [f"Symbol: {sym or asset} | Price: {price}"]

        # Add RSI/EMA/ADX from computed indicators
        if state.get("indicators"):
            ind = state["indicators"]
            lines.append(
                f"RSI14(M15): {ind.get('rsi_m15','-')} | "
                f"ADX(M15): {ind.get('adx_m15','-')} | "
                f"EMA9/21: {ind.get('ema9_m15','-')}/{ind.get('ema21_m15','-')}"
            )
            if ind.get('rsi_h1'):
                lines.append(f"RSI(H1): {ind['rsi_h1']} | ADX(H1): {ind.get('adx_h1','-')}")

        # SMC
        if state.get("smc"):
            smc = state["smc"]
            lines.append(f"SMC: {smc.get('structure','?')} | BOS: {len(smc.get('bos_levels',[]))} levels")
            if smc.get("order_blocks"):
                ob = smc["order_blocks"][0]
                lines.append(f"Order Block: {ob.get('type','?')} @ {ob.get('price',0):.2f}")
            if smc.get("fvgs"):
                fvg = smc["fvgs"][0]
                lines.append(f"FVG: {fvg.get('type','?')} @ {fvg.get('price',0):.2f}")

        # Account / spread
        if acc:
            lines.append(f"Balance: {acc.get('balance',0)} | Spread: {state.get('spread',0)}")

        return "\n".join(lines)

    except Exception as e:
        logger.debug(f"_get_mt5_context error: {e}")
        return ""


def _parse_signal_json(text: str) -> dict:
    """Extract JSON from AI response."""
    try:
        clean = text.strip()
        # Strip code fences
        if "```" in clean:
            parts = clean.split("```")
            for p in parts:
                p = p.strip()
                if p.startswith("json"):
                    p = p[4:]
                if p.strip().startswith("{"):
                    clean = p.strip()
                    break
        # Find JSON boundaries
        s = clean.find("{")
        e = clean.rfind("}")
        if s != -1 and e != -1 and s < e:
            clean = clean[s:e+1]
        return json.loads(clean)
    except Exception:
        return {
            "decision": "NONE",
            "entry": 0.0, "sl": 0.0, "tp": 0.0,
            "confidence": 0,
            "reason": text[:300]
        }


def _map_symbol(symbol: str) -> str:
    mapping = {
        "XAUUSD": "XAU/USD", "EURUSD": "EUR/USD",
        "GBPUSD": "GBP/USD", "BTCUSD": "BTCUSDT",
    }
    return mapping.get(symbol.upper(), symbol)
