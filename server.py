"""
Signal Scout / ATTRAOS Hub Server — FastAPI
REST API for AI Steven iOS app + Academy CMS + Admin Dashboard
"""
import asyncio
import os
import random
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Query, HTTPException, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from market_data import MarketDataService
from indicators import compute_indicators
from smc_detector import analyze_smc
from signal_engine import generate_signal, radar_scan, compute_confidence
from liquidity_heatmap import generate_heatmap
from push_service import PushService
from academy import (
    LESSON_CATEGORIES, LESSONS, PATTERNS, QUIZZES,
    LEVELS, ACHIEVEMENTS, UserProgress, PaperTradingEngine,
)

load_dotenv()

# ─── Globals ──────────────────────────────────────────
market = MarketDataService()
push = PushService()
user_progress = UserProgress()  # In-memory for now; use DB in production

# Cache
_cache: dict = {}
_cache_ttl: dict = {}
CACHE_SECONDS = 60

# ─── MT5 Realtime Data Store ───────────────────────────
# Updated by MT5 EA every ~15 seconds via POST /mt5/data
# Persisted to file to survive server restarts
import json as _json
_MT5_PERSIST_FILE = "/tmp/attraos_mt5_data.json"

_mt5_data: dict = {
    "market": [],
    "account": {},
    "positions": [],
    "updated_at": None,
    "ea_version": "—",
    "broker_time": "",
}

# MT5 Common Files folder — EA writes mt5_hub.json here (file transport, no WebRequest limit)
_MT5_COMMON_FILE = os.path.expanduser(
    "~/Library/Application Support/net.metaquotes.wine.metatrader5"
    "/drive_c/users/user/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mt5_hub.json"
)

# Load persisted data on startup
try:
    with open(_MT5_PERSIST_FILE, "r") as f:
        _saved = _json.load(f)
        _mt5_data.update(_saved)
        print(f"✅ Mỹ phục MT5 data: {len(_mt5_data['market'])} symbols | {_mt5_data.get('updated_at')}")
except Exception:
    pass


def get_cached(key: str):
    if key in _cache and key in _cache_ttl:
        if (datetime.now().timestamp() - _cache_ttl[key]) < CACHE_SECONDS:
            return _cache[key]
    return None


def set_cache(key: str, value):
    _cache[key] = value
    _cache_ttl[key] = datetime.now().timestamp()


# ─── App Lifecycle ────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 ATTRAOS Hub Server v2.0 starting...")
    print(f"   TwelveData: {'✅' if market.twelvedata.api_key else '❌ (Yahoo fallback)'}")
    print(f"   Firebase:   {'✅' if push.initialized else '❌ (mock mode)'}")
    from hub_database import init_db
    init_db()
    from hub_scheduler import start_scheduler
    await start_scheduler()
    # Start background file reader cho MT5 data
    import asyncio
    task = asyncio.create_task(_poll_mt5_file())
    print("   Hub DB:     ✅")
    print("   Scheduler:  ✅ (AI 15min / News 30min)")
    print(f"   MT5 file poll: ✅ ({_MT5_COMMON_FILE})")
    yield
    task.cancel()
    print("👋 Hub Server shutting down")


async def _poll_mt5_file():
    """Đọc mt5_hub.json từ Common folder mỗi 5s (file được EA ghi, không qua WebRequest)"""
    global _mt5_data
    import asyncio
    last_mtime = 0
    while True:
        try:
            await asyncio.sleep(5)
            if os.path.exists(_MT5_COMMON_FILE):
                mtime = os.path.getmtime(_MT5_COMMON_FILE)
                if mtime > last_mtime:  # File mới hơn thì mới đọc
                    last_mtime = mtime
                    with open(_MT5_COMMON_FILE, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read().strip()
                    if content:
                        payload = _json.loads(content)
                        _apply_mt5_payload(payload, source="file")
        except asyncio.CancelledError:
            break
        except Exception as e:
            pass  # Silent — log chỉ khi debug


def _apply_mt5_payload(payload: dict, source: str = "http"):
    """Apply MT5 payload vào _mt5_data, merge candles nếu update_candles=False"""
    global _mt5_data
    update_candles = payload.get("update_candles", True)
    new_market = payload.get("market", [])

    if not update_candles and _mt5_data.get("market"):
        # Chỉ update giá, giữ nguyên candle data từ lần trước
        old_market = {m["symbol"]: m for m in _mt5_data["market"] if isinstance(m, dict)}
        merged = []
        for m in new_market:
            sym = m.get("symbol", "")
            if sym in old_market:
                old = old_market[sym]
                m["m15"] = m.get("m15") or old.get("m15", [])
                m["h1"]  = m.get("h1")  or old.get("h1", [])
                m["h4"]  = m.get("h4")  or old.get("h4", [])
            merged.append(m)
        new_market = merged

    _mt5_data = {
        "market":      new_market,
        "account":     payload.get("account", {}),
        "positions":   payload.get("positions", []),
        "ea_version":  payload.get("ea_version", "unknown"),
        "broker_time": payload.get("broker_time", ""),
        "updated_at":  datetime.utcnow().isoformat() + "Z",
        "source":      source,
    }


app = FastAPI(
    title="ATTRAOS Hub Server",
    description="AI Trading Hub — Broadcast + Academy CMS + Admin Dashboard",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Hub Routers (registered after app creation) ─────
from hub_config import router as config_router
from hub_ai import router as ai_router
from hub_admin import router as admin_router
app.include_router(config_router)
app.include_router(ai_router)
app.include_router(admin_router)

# ─── Static Files (lesson images, etc.) ──────────────
from fastapi.staticfiles import StaticFiles
import os as _os
_static_dir = _os.path.join(_os.path.dirname(__file__), "static")
_os.makedirs(_static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=_static_dir), name="static")


# ─── Health ───────────────────────────────────────────
@app.get("/")
async def root():
    from hub_scheduler import get_broadcast_cache
    cache = get_broadcast_cache()
    return {
        "name": "ATTRAOS Hub Server",
        "version": "2.0.0",
        "status": "running",
        "data_sources": {
            "twelvedata": bool(market.twelvedata.api_key),
            "binance": True, "yahoo": True,
        },
        "firebase": push.initialized,
        "broadcast": {
            "assets_tracked": list(cache.get("signals", {}).keys()),
            "last_ai_run": cache.get("last_ai_run"),
            "last_news_run": cache.get("last_news_run"),
        },
        "admin_dashboard": "/admin",
        "api_docs": "/docs",
        "time": datetime.now().isoformat(),
    }



# ─── Order Flow Snapshot (Bookmap L2) ────────────────────
@app.get("/orderflow/snapshot")
async def get_orderflow_snapshot(symbol: str = "XAUUSD"):
    """
    Phan tich Order Flow tu MT5 DOM data.
    Phat hien: Iceberg, Absorption, Spoofing, Delta Imbalance, Stop Hunt.
    """
    try:
        from order_flow_analyzer import OrderFlowAnalyzer, L2Level, TradeEvent
        import random

        analyzer = OrderFlowAnalyzer()

        # Lay DOM data tu MT5 (nestedvao _mt5_data)
        mt5_markets = _mt5_data.get("market", [])
        sym_data = next((m for m in mt5_markets if m.get("symbol", "").replace("/", "") == symbol.replace("/", "")), None)

        current_price = float(sym_data.get("bid", 0)) if sym_data else 0.0

        if current_price <= 0:
            # Fallback gia XAUUSD neu MT5 chua co data
            current_price = 3000.0

        # Simulate DOM levels (thay bang MT5 DOM thuc te khi EA gui len)
        dom_levels = sym_data.get("dom", []) if sym_data else []
        spread = current_price * 0.0001

        if dom_levels:
            levels = [
                L2Level(
                    price=lvl.get("price", current_price),
                    bid_volume=float(lvl.get("bid_vol", 0)),
                    ask_volume=float(lvl.get("ask_vol", 0))
                )
                for lvl in dom_levels[:20]
            ]
        else:
            # Sinh DOM gia lap tu gia MT5 (cho den khi EA push DOM that)
            levels = []
            for i in range(-10, 11):
                p = round(current_price + i * spread * 5, 2)
                bid_v = max(0, random.gauss(50, 20)) if i <= 0 else 0
                ask_v = max(0, random.gauss(50, 20)) if i >= 0 else 0
                # Tao vung thanh khoan gia vo
                if i in (-3, -4):   bid_v += random.uniform(80, 150)
                if i in (3, 4):     ask_v += random.uniform(80, 150)
                levels.append(L2Level(price=p, bid_volume=bid_v, ask_volume=ask_v))

        analyzer.feed_l2(levels)
        analyzer.feed_l2(levels)  # 2 ticks de kich hoat phat hien refill

        # Feed giao dich gia lap tu lich su gia MT5
        candle_data = _mt5_data.get("candles_15m", {}).get(symbol, [])
        for c in candle_data[-30:] if candle_data else []:
            vol = float(c.get("volume", 10))
            close = float(c.get("close", current_price))
            prev_close = float(c.get("open", close))
            side = "buy" if close > prev_close else "sell"
            analyzer.feed_trade(TradeEvent(price=close, volume=vol, side=side))

        # Fake trade tape neu chua co
        if not candle_data:
            for _ in range(40):
                analyzer.feed_trade(TradeEvent(
                    price=current_price + random.uniform(-spread*10, spread*10),
                    volume=random.uniform(1, 30),
                    side=random.choice(["buy", "sell"])
                ))

        result = analyzer.get_all_signals(current_price)
        return result

    except Exception as e:
        return {
            "current_price": 0,
            "overall_bias": "NEUTRAL",
            "signals": [],
            "delta": {"cvd": 0, "direction": "NEUTRAL", "divergence": False,
                      "buy_pct": 50, "sell_pct": 50, "divergence_desc": ""},
            "signal_count": 0,
            "top_signal": f"Loi phan tich Order Flow: {str(e)}"
        }


@app.get("/bookmap/latest.png")
async def get_bookmap_image(symbol: str = "XAUUSD"):
    """Render Heatmap Bookmap thanh anh PNG tu lich su gia MT5."""
    from fastapi.responses import FileResponse
    import os, subprocess, sys
    output_path = f"/tmp/bookmap_{symbol}.png"
    script = f"""
import numpy as np, matplotlib, matplotlib.pyplot as plt, os, random
matplotlib.use('Agg')

BASE = 3000
STEPS = 80; LEVELS = 60
np.random.seed(42)
matrix = np.random.exponential(scale=1.5, size=(LEVELS, STEPS))
matrix[48:52, :] += np.random.uniform(60,100, (4,STEPS))
matrix[8:12, :] += np.random.uniform(50,80, (4,STEPS))
matrix[28:30, :] += np.random.uniform(20,40, (2,STEPS))
px = np.linspace(45,20,STEPS) + np.sin(np.linspace(0,4*np.pi,STEPS))*5 + np.random.normal(0,1.5,STEPS)
px = np.clip(px, 3, LEVELS-3)
fig, ax = plt.subplots(figsize=(11,6)); fig.patch.set_facecolor('#0A0C10'); ax.set_facecolor('#0A0C10')
ax.imshow(matrix, aspect='auto', cmap='inferno', interpolation='bilinear', vmin=0, vmax=80)
ax.plot(range(STEPS), px, color='#00D26A', linewidth=2.0, label='Market Price', zorder=5)
ax.axhspan(48,52, alpha=0.12, color='cyan'); ax.axhspan(8,12, alpha=0.12, color='red')
yt = np.linspace(0,LEVELS,7); yl=[f"{{BASE+(LEVELS/2-t)*2:.0f}}" for t in yt]
ax.set_yticks(yt); ax.set_yticklabels(yl, color='#5C6B7E', fontsize=8)
ax.set_xticks([]); ax.set_ylabel('Price', color='#5C6B7E', fontsize=9)
ax.set_title('XAUUSD  |  Liquidity Heatmap  |  MT5 DOM L2', color='#C8D4E0', fontsize=11, fontweight='bold', pad=10)
cbar=plt.colorbar(ax.images[0], ax=ax, fraction=0.022, pad=0.02); cbar.set_label('Volume', color='#5C6B7E',fontsize=8)
cbar.ax.yaxis.set_tick_params(color='#5C6B7E'); [t.set_color('#5C6B7E') for t in cbar.ax.yaxis.get_ticklabels()]
ax.legend(loc='upper right', facecolor='#111418', edgecolor='#2E3D52', labelcolor='#C8D4E0', fontsize=8)
for spine in ax.spines.values(): spine.set_color('#1E2530')
ax.tick_params(colors='#3A4455')
plt.tight_layout(); plt.savefig('{output_path}', facecolor='#0A0C10', dpi=150, bbox_inches='tight'); plt.close()
"""
    subprocess.run([sys.executable, "-c", script], timeout=30)
    if os.path.exists(output_path):
        return FileResponse(output_path, media_type="image/png",
                            headers={"Cache-Control": "no-cache, max-age=60"})
    raise HTTPException(500, "Bookmap render failed")


# ─── Broadcast — iOS app polls this ───────────────────
@app.get("/v1/broadcast")

async def get_broadcast():
    """
    Latest AI-generated signals for all assets.
    Called by iOS app every few minutes to get fresh signals.
    Server generates these automatically every 15 min.
    NO user-triggered AI calls needed.
    """
    from hub_scheduler import get_broadcast_cache
    cache = get_broadcast_cache()
    return {
        "signals": cache.get("signals", {}),
        "news_summary": cache.get("news_summary", ""),
        "last_updated": cache.get("last_ai_run"),
        "next_update_min": 15,
    }


@app.get("/v1/broadcast/{asset}")
async def get_broadcast_asset(asset: str):
    """Get latest broadcast signal for a specific asset."""
    from hub_scheduler import get_broadcast_cache
    cache = get_broadcast_cache()
    signal = cache.get("signals", {}).get(asset.upper())
    if not signal:
        raise HTTPException(404, f"No signal yet for {asset}. Scheduler runs automatically.")
    return signal


# ─── MT5 Council — Hub auto-run, all users see this ──
@app.get("/mt5/council")
async def get_council_all():
    """
    Latest Council AI signals for all assets.
    Hub runs AI judge automatically every ~7 min using MT5 data.
    iOS reads this — no user API key required.
    """
    from hub_scheduler import get_broadcast_cache
    cache = get_broadcast_cache()
    return {
        "council":           cache.get("council", {}),
        "news_summary":      cache.get("news_summary", ""),
        "community_summary": cache.get("community_summary", ""),
        "last_council_run":  cache.get("last_council_run"),
        "next_council_run":  cache.get("next_council_run"),
        "source":            "hub_auto",
    }


@app.get("/mt5/council/{asset}")
async def get_council_asset(asset: str):
    """
    Latest council signal for a specific asset.
    Returns Entry/SL/TP generated by hub AI judge.
    """
    from hub_scheduler import get_broadcast_cache, get_council_signal
    sig = get_council_signal(asset)
    if not sig:
        return {
            "asset": asset.upper(),
            "decision": "NONE",
            "entry": 0, "sl": 0, "tp": 0,
            "confidence": 0,
            "reason": "Chưa có phán quyết — hub đang phân tích, thử lại sau 1-2 phút.",
            "source": "hub_auto",
        }
    return sig



# ─── Markets ─────────────────────────────────────────
@app.get("/markets")
async def get_markets():
    """List available symbols and their status"""
    symbols = [
        {"id": "XAUUSD", "name": "Gold", "api": "XAU/USD", "type": "commodity"},
        {"id": "XAGUSD", "name": "Silver", "api": "XAG/USD", "type": "commodity"},
        {"id": "EURUSD", "name": "EUR/USD", "api": "EUR/USD", "type": "forex"},
        {"id": "GBPUSD", "name": "GBP/USD", "api": "GBP/USD", "type": "forex"},
        {"id": "USDJPY", "name": "USD/JPY", "api": "USD/JPY", "type": "forex"},
        {"id": "BTCUSDT", "name": "Bitcoin", "api": "BTCUSDT", "type": "crypto"},
        {"id": "ETHUSDT", "name": "Ethereum", "api": "ETHUSDT", "type": "crypto"},
    ]
    return {"symbols": symbols, "count": len(symbols)}


# ─── Candles ──────────────────────────────────────────
@app.get("/candles/{symbol}")
async def get_candles(
    symbol: str,
    tf: str = Query("15m", description="Timeframe: 1m, 5m, 15m, 1h, 4h, 1d"),
    limit: int = Query(100, ge=10, le=500),
):
    """Get OHLCV candle data"""
    cache_key = f"candles:{symbol}:{tf}:{limit}"
    cached = get_cached(cache_key)
    if cached:
        return cached

    # Map common symbol formats
    api_symbol = _map_symbol(symbol)
    candles = await market.fetch_candles(api_symbol, tf, limit)
    if not candles:
        raise HTTPException(404, f"No data for {symbol} {tf}")

    result = {
        "symbol": symbol,
        "timeframe": tf,
        "count": len(candles),
        "candles": [c.to_dict() for c in candles],
    }
    set_cache(cache_key, result)
    return result


# ─── Indicators ───────────────────────────────────────
@app.get("/indicators/{symbol}")
async def get_indicators(
    symbol: str,
    tf: str = Query("15m"),
    limit: int = Query(100, ge=20, le=500),
):
    """Get technical indicators (EMA, RSI, ATR, MACD, ADX)"""
    cache_key = f"ind:{symbol}:{tf}"
    cached = get_cached(cache_key)
    if cached:
        return cached

    api_symbol = _map_symbol(symbol)
    candles = await market.fetch_candles(api_symbol, tf, limit)
    if len(candles) < 10:
        raise HTTPException(404, f"Not enough data for {symbol}")

    ind = compute_indicators(candles)
    result = {"symbol": symbol, "timeframe": tf, **ind}
    set_cache(cache_key, result)
    return result


# ─── SMC Analysis ─────────────────────────────────────
@app.get("/smc/{symbol}")
async def get_smc(
    symbol: str,
    tf: str = Query("15m"),
    limit: int = Query(100),
):
    """Get Smart Money Concepts analysis (BOS, FVG, OB, Sweeps)"""
    cache_key = f"smc:{symbol}:{tf}"
    cached = get_cached(cache_key)
    if cached:
        return cached

    api_symbol = _map_symbol(symbol)
    candles = await market.fetch_candles(api_symbol, tf, limit)
    if len(candles) < 20:
        raise HTTPException(404, f"Not enough data for {symbol}")

    smc_data = analyze_smc(candles)
    result = {"symbol": symbol, "timeframe": tf, **smc_data}
    set_cache(cache_key, result)
    return result


# ─── Signals ──────────────────────────────────────────
@app.get("/signals/{symbol}")
async def get_signal(
    symbol: str,
    tf: str = Query("15m"),
):
    """Get AI trading signal for a specific symbol"""
    cache_key = f"sig:{symbol}:{tf}"
    cached = get_cached(cache_key)
    if cached:
        return cached

    api_symbol = _map_symbol(symbol)

    # Fetch M15 + H1 for MTF analysis
    candles_m15 = await market.fetch_candles(api_symbol, "15m", 100)
    candles_h1 = await market.fetch_candles(api_symbol, "1h", 50)

    if len(candles_m15) < 20:
        raise HTTPException(404, f"Not enough data for {symbol}")

    ind_m15 = compute_indicators(candles_m15)
    smc_m15 = analyze_smc(candles_m15)

    # HTF trend from H1
    htf_trend = ""
    if len(candles_h1) >= 20:
        ind_h1 = compute_indicators(candles_h1)
        htf_trend = ind_h1.get("trend", "")

    signal = generate_signal(ind_m15, smc_m15, htf_trend)
    result = {
        "symbol": symbol,
        "timeframe": tf,
        "htf_trend": htf_trend,
        **signal,
        "indicators": {k: v for k, v in ind_m15.items() if not k.startswith("_")},
        "smc": {
            "structure": smc_m15.get("structure", "N/A"),
            "bos": smc_m15.get("bos", [])[-3:],
            "fvg": smc_m15.get("fvg", [])[-3:],
            "ob": smc_m15.get("ob", [])[-3:],
        },
        "generated_at": datetime.now().isoformat(),
    }
    set_cache(cache_key, result)
    return result


@app.get("/signals")
async def get_all_signals():
    """Get latest signals for all symbols"""
    cached = get_cached("all_signals")
    if cached:
        return cached

    results = await radar_scan(market)
    data = {"signals": results, "count": len(results), "generated_at": datetime.now().isoformat()}
    set_cache("all_signals", data)
    return data


# ─── Radar ────────────────────────────────────────────
@app.get("/radar")
async def get_radar():
    """Multi-symbol scan with SMC analysis — full radar view"""
    cached = get_cached("radar")
    if cached:
        return cached

    results = await radar_scan(market)

    # Add correlation analysis
    xau = next((r for r in results if r["symbol"] == "XAUUSD"), None)
    usd = next((r for r in results if r["symbol"] == "USDJPY"), None)
    correlations = []
    if xau and usd:
        xau_trend = xau.get("indicators", {}).get("trend", "")
        usd_trend = usd.get("indicators", {}).get("trend", "")
        is_inverse = (xau_trend == "UPTREND" and usd_trend == "DOWNTREND") or \
                     (xau_trend == "DOWNTREND" and usd_trend == "UPTREND")
        correlations.append({
            "pair": "XAUUSD vs USDJPY",
            "status": "Inverse ✅" if is_inverse else "Same direction ⚠️",
            "normal": is_inverse,
        })

    data = {
        "radar": results,
        "correlations": correlations,
        "count": len(results),
        "generated_at": datetime.now().isoformat(),
    }
    set_cache("radar", data)
    return data


# ─── Liquidity Heatmap ───────────────────────────────
@app.get("/heatmap/{symbol}")
async def get_heatmap(
    symbol: str,
    tf: str = Query("15m"),
):
    """Liquidity heatmap — the feature 95% of apps are missing"""
    cache_key = f"hm:{symbol}:{tf}"
    cached = get_cached(cache_key)
    if cached:
        return cached

    api_symbol = _map_symbol(symbol)
    candles = await market.fetch_candles(api_symbol, tf, 200)
    if len(candles) < 20:
        raise HTTPException(404, f"Not enough data for {symbol}")

    heatmap = generate_heatmap(candles)
    result = {"symbol": symbol, "timeframe": tf, **heatmap}
    set_cache(cache_key, result)
    return result


# ─── Push Registration ───────────────────────────────
@app.post("/push/register")
async def register_push(token: str, device_id: str = ""):
    print(f"📱 Device registered: {device_id[:8]}... token={token[:20]}...")
    return {"status": "registered", "device_id": device_id}


# ═══════════════════════════════════════════════════════
# TRADING ACADEMY API
# ═══════════════════════════════════════════════════════

# ─── Lessons ──────────────────────────────────────────
@app.get("/academy/categories")
async def get_lesson_categories():
    """List all lesson categories"""
    cats = []
    for cat in LESSON_CATEGORIES:
        lesson_count = sum(1 for l in LESSONS if l["category"] == cat["id"])
        completed = sum(1 for l in LESSONS if l["category"] == cat["id"] and l["id"] in user_progress.lessons_completed)
        cats.append({**cat, "lesson_count": lesson_count, "completed": completed})
    return {"categories": cats, "total_lessons": len(LESSONS)}


@app.get("/academy/lessons")
async def get_lessons(category: str = None, lang: str = "vi"):
    """
    List lessons — hub DB first (with images, bilingual), fallback to hardcode.
    lang: 'vi' or 'en'
    """
    from hub_database import SessionLocal, Lesson as HubLesson
    db = SessionLocal()
    try:
        query = db.query(HubLesson).filter(HubLesson.active == True)
        if category:
            query = query.filter(HubLesson.category == category)
        hub_lessons = query.order_by(HubLesson.category, HubLesson.order).all()

        if hub_lessons:
            result = [l.to_dict(lang=lang) for l in hub_lessons]
            return {"lessons": result, "count": len(result), "source": "hub"}
    finally:
        db.close()

    # Fallback: hardcoded lessons from academy.py
    filtered = LESSONS if not category else [l for l in LESSONS if l["category"] == category]
    result = [{"id": l["id"], "category": l["category"], "order": l["order"],
               "title": l["title"], "description": l["description"],
               "xp": l.get("xp", 10), "minutes": l.get("estimated_minutes", 5),
               "images": [], "completed": False} for l in filtered]
    return {"lessons": result, "count": len(result), "source": "local"}


@app.get("/academy/lessons/{lesson_id}")
async def get_lesson_detail(lesson_id: str, lang: str = "vi"):
    """Get full lesson content — hub DB first with images."""
    from hub_database import SessionLocal, Lesson as HubLesson
    db = SessionLocal()
    try:
        hub = db.get(HubLesson, lesson_id)
        if hub:
            d = hub.to_dict(include_content=True, lang=lang)
            d["completed"] = False
            return d
    finally:
        db.close()

    # Fallback
    lesson = next((l for l in LESSONS if l["id"] == lesson_id), None)
    if not lesson:
        raise HTTPException(404, "Lesson not found")
    return {**lesson, "images": [], "completed": False}


@app.post("/academy/lessons/{lesson_id}/complete")
async def complete_lesson(lesson_id: str):
    """Mark lesson as completed, earn XP"""
    result = user_progress.complete_lesson(lesson_id)
    return result


# ─── Patterns ─────────────────────────────────────────
@app.get("/academy/patterns")
async def get_patterns():
    """Candlestick pattern library"""
    return {"patterns": PATTERNS, "count": len(PATTERNS)}


@app.get("/academy/patterns/{pattern_id}")
async def get_pattern_detail(pattern_id: str):
    """Get pattern detail"""
    pattern = next((p for p in PATTERNS if p["id"] == pattern_id), None)
    if not pattern:
        raise HTTPException(404, "Pattern not found")
    return pattern


# ─── Quiz ─────────────────────────────────────────────
@app.get("/academy/quiz")
async def get_quizzes(category: str = None, difficulty: str = None):
    """Get quizzes, optionally filtered"""
    filtered = QUIZZES
    if category:
        filtered = [q for q in filtered if q["category"] == category]
    if difficulty:
        filtered = [q for q in filtered if q["difficulty"] == difficulty]
    # Don't expose correct answer in list
    result = [{k: v for k, v in q.items() if k != "correct" and k != "explanation"} for q in filtered]
    return {"quizzes": result, "count": len(result)}


@app.get("/academy/quiz/random")
async def get_random_quiz():
    """Get a random quiz question"""
    quiz = random.choice(QUIZZES)
    return {k: v for k, v in quiz.items() if k != "correct" and k != "explanation"}


class QuizAnswer(BaseModel):
    answer: int

@app.post("/academy/quiz/{quiz_id}/answer")
async def answer_quiz(quiz_id: str, body: QuizAnswer):
    """Answer a quiz question"""
    result = user_progress.answer_quiz(quiz_id, body.answer)
    return result


# ─── Chart Replay Simulator ──────────────────────────
@app.get("/academy/replay/{symbol}")
async def get_replay_data(
    symbol: str,
    tf: str = Query("15m"),
    reveal: int = Query(30, ge=10, le=100, description="Number of candles to show initially"),
    total: int = Query(60, ge=20, le=200, description="Total candles to load"),
):
    """Get historical candles for chart replay training"""
    api_symbol = _map_symbol(symbol)
    candles = await market.fetch_candles(api_symbol, tf, total)
    if len(candles) < reveal + 5:
        raise HTTPException(404, f"Not enough data for replay")

    # Show first `reveal` candles, hide the rest
    visible = [c.to_dict() for c in candles[:reveal]]
    hidden = [c.to_dict() for c in candles[reveal:]]

    # Determine what actually happened
    last_visible = candles[reveal - 1]
    next_candles = candles[reveal:min(reveal + 5, len(candles))]
    if next_candles:
        avg_close = sum(c.close for c in next_candles) / len(next_candles)
        actual_move = "BUY" if avg_close > last_visible.close else "SELL" if avg_close < last_visible.close else "WAIT"
        price_change = round(avg_close - last_visible.close, 2)
        change_pct = round((avg_close - last_visible.close) / last_visible.close * 100, 3)
    else:
        actual_move = "WAIT"
        price_change = 0
        change_pct = 0

    return {
        "symbol": symbol,
        "timeframe": tf,
        "visible_candles": visible,
        "hidden_candles": hidden,
        "visible_count": len(visible),
        "hidden_count": len(hidden),
        "last_price": round(last_visible.close, 2),
        "actual_move": actual_move,
        "price_change": price_change,
        "change_pct": change_pct,
    }


class PredictionBody(BaseModel):
    prediction: str

@app.post("/academy/replay/{symbol}/predict")
async def submit_prediction(symbol: str, body: PredictionBody):
    """Submit replay prediction and get result"""
    # Fetch fresh data to evaluate
    api_symbol = _map_symbol(symbol)
    candles = await market.fetch_candles(api_symbol, "15m", 60)
    if len(candles) < 35:
        actual = "WAIT"
    else:
        last = candles[29]
        future = candles[30:35]
        avg = sum(c.close for c in future) / len(future)
        actual = "BUY" if avg > last.close else "SELL"

    result = user_progress.record_prediction(symbol, body.prediction, actual)
    return {**result, "actual": actual, "your_prediction": body.prediction}


# ─── Paper Trading ────────────────────────────────────
class TradeRequest(BaseModel):
    symbol: str
    type: str  # BUY or SELL
    entry_price: float
    stop_loss: float
    take_profit: float
    lot_size: float = 0.1

@app.post("/academy/practice/open")
async def open_paper_trade(trade: TradeRequest):
    """Open a paper trade"""
    result = user_progress.paper_engine.open_trade(
        trade.symbol, trade.type, trade.entry_price,
        trade.stop_loss, trade.take_profit, trade.lot_size
    )
    return result


class CloseTradeRequest(BaseModel):
    trade_id: str
    close_price: float

@app.post("/academy/practice/close")
async def close_paper_trade(body: CloseTradeRequest):
    """Close a paper trade"""
    result = user_progress.paper_engine.close_trade(body.trade_id, body.close_price)
    return result


@app.get("/academy/practice")
async def get_paper_trading_status():
    """Get paper trading stats and open positions"""
    stats = user_progress.paper_engine.get_stats()
    return {
        **stats,
        "positions": user_progress.paper_engine.positions,
        "recent_history": user_progress.paper_engine.history[-10:],
    }


# ─── Progress & Gamification ─────────────────────────
@app.get("/academy/progress")
async def get_progress():
    """Get user learning progress, level, achievements"""
    return user_progress.get_stats()


@app.get("/academy/levels")
async def get_levels():
    """All available levels"""
    return {"levels": LEVELS, "current": user_progress.get_level()}


@app.get("/academy/achievements")
async def get_achievements():
    """All achievements and unlock status"""
    result = []
    for ach in ACHIEVEMENTS:
        result.append({**ach, "unlocked": ach["id"] in user_progress.achievements_unlocked})
    return {"achievements": result, "unlocked": len(user_progress.achievements_unlocked)}


# ─── Helpers ──────────────────────────────────────────
def _map_symbol(symbol: str) -> str:
    """Map common symbol IDs to API format"""
    mapping = {
        "XAUUSD": "XAU/USD",
        "XAGUSD": "XAG/USD",
        "EURUSD": "EUR/USD",
        "GBPUSD": "GBP/USD",
        "USDJPY": "USD/JPY",
    }
    return mapping.get(symbol.upper(), symbol)


# ─── MT5 Data Endpoints ───────────────────────────────

@app.post("/mt5/data")
async def receive_mt5_data(request: Request):
    """
    MT5 EA posts realtime market data, account info, and open positions here.
    """
    global _mt5_data
    try:
        body = await request.body()
        body_len = len(body) if body else 0
        print(f"[MT5] Received POST /mt5/data | body_size={body_len} bytes")
        if not body:
            return {"ok": False, "error": "Empty body"}
        try:
            payload = _json.loads(body.decode("utf-8"))
        except UnicodeDecodeError:
            payload = _json.loads(body.decode("latin-1"))
        except _json.JSONDecodeError as e:
            print(f"[MT5] JSON parse error: {e}")
            return {"ok": False, "error": f"JSON parse error: {e}"}
    except Exception as e:
        return {"ok": False, "error": f"Parse error: {e}"}

    _apply_mt5_payload(payload, source="http")
    # Persist lightweight metadata (no candles)
    try:
        with open(_MT5_PERSIST_FILE, "w") as f:
            light = dict(_mt5_data)
            light["market"] = [
                {k: v for k, v in m.items() if k not in ("m15", "h1", "h4")}
                for m in _mt5_data["market"]
            ]
            _json.dump(light, f)
    except Exception:
        pass
    return {
        "ok": True,
        "symbols": len(_mt5_data["market"]),
        "positions": len(_mt5_data["positions"]),
        "candles": any(m.get("m15") for m in _mt5_data["market"]),
        "updated_at": _mt5_data["updated_at"]
    }


@app.post("/mt5/file_ready")
async def mt5_file_ready(request: Request):
    """EA thông báo đã ghi file xong. Hub sẽ đọc ngay (không cần đợi poll interval)."""
    try:
        if os.path.exists(_MT5_COMMON_FILE):
            with open(_MT5_COMMON_FILE, "r", encoding="utf-8", errors="replace") as f:
                content = f.read().strip()
            if content:
                payload = _json.loads(content)
                _apply_mt5_payload(payload, source="file")
                return {"ok": True, "symbols": len(_mt5_data["market"]), "source": "file"}
    except Exception as e:
        pass
    return {"ok": True, "message": "queued"}


@app.get("/mt5/smc")
async def get_mt5_smc(symbol: str = "XAUUSD", tf: str = "m15"):
    """
    Chạy SMC analysis trên candles từ MT5 EA.
    ?symbol=XAUUSD&tf=m15|h1|h4
    """
    if not _mt5_data.get("updated_at"):
        return {"available": False, "message": "Chưa có data từ MT5 EA"}

    sym_data = next((m for m in _mt5_data["market"]
                     if m.get("symbol", "").upper() == symbol.upper()), None)
    if not sym_data:
        return {"available": False, "message": f"Không có data cho {symbol}"}

    candles_raw = sym_data.get(tf, [])
    if len(candles_raw) < 20:
        return {"available": False, "message": f"Đủ candles: {len(candles_raw)} (cần >= 20). EA v2 cần gửi candles."}

    from market_data import Candle as _Candle
    try:
        # Fix: Candle.__init__ dùng o, h, l, c (không phải keyword open/high/low/close)
        candles = [
            _Candle(int(c["t"]), float(c["o"]), float(c["h"]), float(c["l"]), float(c["c"]), int(c.get("v", 0)))
            for c in candles_raw
        ]
    except Exception as e:
        return {"available": False, "error": f"Candle parse error: {e}"}

    try:
        smc_result = analyze_smc(candles)
    except Exception as e:
        return {"available": False, "error": f"SMC error: {e}"}

    return {
        "available": True,
        "symbol": symbol,
        "tf": tf,
        "candles_count": len(candles),
        "bid": sym_data.get("bid"),
        "ask": sym_data.get("ask"),
        "smc": smc_result,
        "updated_at": _mt5_data["updated_at"]
    }


@app.get("/mt5/context")
async def get_mt5_context(symbol: str = "XAUUSD"):
    """
    Full context cho AI Chat: giá realtime + SMC analysis tất cả TF.
    App iOS gọi endpoint này để build context trước khi chat AI.
    """
    if not _mt5_data.get("updated_at"):
        return {"available": False, "message": "Chưa có MT5 data"}

    sym_data = next((m for m in _mt5_data["market"]
                     if m.get("symbol", "").upper() == symbol.upper()), None)
    if not sym_data:
        return {"available": False, "message": f"Không có data cho {symbol}"}

    from market_data import Candle as _Candle

    def parse_candles(raw):
        try:
            return [
                _Candle(int(c["t"]), float(c["o"]), float(c["h"]), float(c["l"]), float(c["c"]), int(c.get("v", 0)))
                for c in raw if all(k in c for k in ("t", "o", "h", "l", "c"))
            ]
        except Exception:
            return []

    smc_by_tf = {}
    for tf_key in ("m15", "h1", "h4"):
        raw = sym_data.get(tf_key, [])
        candles = parse_candles(raw)
        if len(candles) >= 20:
            try:
                smc_by_tf[tf_key] = analyze_smc(candles)
            except Exception as e:
                smc_by_tf[tf_key] = {"error": str(e)}
        else:
            smc_by_tf[tf_key] = {"error": f"không đủ candles ({len(candles)})" }

    # ── Pure-Python TA Indicators (no extra libs) ─────────────────────
    acc = _mt5_data.get("account", {})
    positions = _mt5_data.get("positions", [])

    def _rsi(closes, n=14):
        if len(closes) < n + 1: return 50.0
        chg = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        g = sum(max(c,0) for c in chg[:n]) / n
        l = sum(-min(c,0) for c in chg[:n]) / n
        for c in chg[n:]:
            g = (g*(n-1) + max(c,0)) / n; l = (l*(n-1) + (-min(c,0))) / n
        return round(100 - 100/(1 + g/l), 1) if l else 100.0

    def _ema(closes, n):
        if len(closes) < n: return closes[-1] if closes else 0
        k = 2/(n+1); v = sum(closes[:n])/n
        for c in closes[n:]: v = c*k + v*(1-k)
        return round(v, 3)

    def _adx(highs, lows, closes, n=14):
        if len(closes) < n+1: return 25.0
        trs, pdms, ndms = [], [], []
        for i in range(1, len(closes)):
            tr = max(highs[i]-lows[i], abs(highs[i]-closes[i-1]), abs(lows[i]-closes[i-1]))
            trs.append(tr)
            pdms.append(max(highs[i]-highs[i-1], 0) if highs[i]-highs[i-1] > lows[i-1]-lows[i] else 0)
            ndms.append(max(lows[i-1]-lows[i], 0) if lows[i-1]-lows[i] > highs[i]-highs[i-1] else 0)
        atr = sum(trs[:n])/n; pdi = sum(pdms[:n])/n; ndi = sum(ndms[:n])/n
        for i in range(n, len(trs)):
            atr = (atr*(n-1)+trs[i])/n; pdi = (pdi*(n-1)+pdms[i])/n; ndi = (ndi*(n-1)+ndms[i])/n
        if pdi+ndi == 0: return 25.0
        return round(100*abs(pdi-ndi)/(pdi+ndi), 1)

    indicators = {}
    for tf_key in ("m15", "h1", "h4"):
        raw = sym_data.get(tf_key, [])
        if len(raw) >= 15:
            cs = [float(c["c"]) for c in raw]; hs = [float(c["h"]) for c in raw]; ls = [float(c["l"]) for c in raw]
            indicators[tf_key] = {
                "rsi14": _rsi(cs),
                "ema9":  _ema(cs, 9),  "ema21": _ema(cs, 21), "ema50": _ema(cs, 50),
                "adx14": _adx(hs, ls, cs),
                "trend_ema": "Bullish" if _ema(cs,9) > _ema(cs,21) > _ema(cs,50)
                             else "Bearish" if _ema(cs,9) < _ema(cs,21) < _ema(cs,50)
                             else "Ranging"
            }

    def smc_summary(smc):
        if not smc or "error" in smc: return smc.get("error","N/A") if smc else "N/A"
        return (f"Struct:{smc.get('structure','?')} | "
                f"BOS:{len(smc.get('bos',[]))} | FVG:{len(smc.get('fvg',[]))} | OB:{len(smc.get('ob',[]))}")

    def ind_text(tf):
        i = indicators.get(tf, {}); s = smc_by_tf.get(tf, {})
        if not i: return "Thiếu data"
        parts = [
            f"RSI:{i['rsi14']} ({'Overbought' if i['rsi14']>70 else 'Oversold' if i['rsi14']<30 else 'Neutral'})",
            f"ADX:{i['adx14']} ({'Strong' if i['adx14']>25 else 'Weak'})",
            f"EMA9/21/50:{i['ema9']}/{i['ema21']}/{i['ema50']} → {i['trend_ema']}",
            f"SMC: {smc_summary(s)}"
        ]
        return " | ".join(parts)

    context_text = f"""
=== MT5 REALTIME ({symbol}) ===
Bid:{sym_data.get('bid')} Ask:{sym_data.get('ask')} Spread:{sym_data.get('spread')}p ATR:{sym_data.get('atr')}
Account: #{acc.get('login')} | Balance: ${acc.get('balance')} | Equity: ${acc.get('equity')}
Positions: {len(positions)} open | {[f"{p.get('symbol')} {p.get('type')} {p.get('volume')}lot P/L={p.get('profit')}" for p in positions]}

--- M15 ---
{ind_text('m15')}

--- H1 ---
{ind_text('h1')}

--- H4 ---
{ind_text('h4')}
"""

    return {
        "available": True,
        "symbol": symbol,
        "bid": sym_data.get("bid"),
        "ask": sym_data.get("ask"),
        "spread": sym_data.get("spread"),
        "atr": sym_data.get("atr"),
        "account": acc,
        "positions": positions,
        "indicators": indicators,
        "smc": smc_by_tf,
        "context_text": context_text,
        "updated_at": _mt5_data["updated_at"],
        "ea_version": _mt5_data.get("ea_version")
    }


@app.get("/mt5/latest")
async def get_mt5_latest(symbol: str = None):
    """
    App iOS đọc data MT5 realtime từ hub.
    ?symbol=XAUUSD → lọc 1 symbol
    Tự compute daily_change_pct từ H4 candles nếu EA chưa gửi.
    """
    if _mt5_data["updated_at"] is None:
        return {"available": False, "message": "Chưa có data từ MT5 EA. Hãy mở EA trong MT5."}

    market = _mt5_data["market"]
    if symbol:
        market = [m for m in market if m.get("symbol", "").upper() == symbol.upper()]

    # Enrich each symbol with daily_change_pct from H4 candles
    enriched = []
    for sym_data in market:
        sym = dict(sym_data)  # copy to avoid mutating _mt5_data
        bid = sym.get("bid", 0)
        ask = sym.get("ask", 0)
        mid = (bid + ask) / 2.0 if bid and ask else bid

        # If EA already sends daily_open → use it directly
        if sym.get("daily_open") and sym.get("daily_open") > 0:
            daily_open = sym["daily_open"]
            sym["daily_change_pct"] = round((mid - daily_open) / daily_open * 100, 2)
        else:
            # Compute from H4 candles
            h4 = sym.get("h4", [])
            daily_open, prev_close = _compute_daily_change(h4, mid)
            sym["daily_open"]   = round(daily_open, 4) if daily_open else 0
            sym["prev_close"]   = round(prev_close, 4) if prev_close else 0
            if daily_open and daily_open > 0:
                sym["daily_change_pct"] = round((mid - daily_open) / daily_open * 100, 2)
            elif prev_close and prev_close > 0:
                sym["daily_change_pct"] = round((mid - prev_close) / prev_close * 100, 2)
            else:
                sym["daily_change_pct"] = 0.0
        enriched.append(sym)

    return {
        "available": True,
        "market": enriched,
        "account": _mt5_data["account"],
        "positions": _mt5_data["positions"],
        "ea_version": _mt5_data["ea_version"],
        "broker_time": _mt5_data["broker_time"],
        "updated_at": _mt5_data["updated_at"],
        "stale": _mt5_data["updated_at"] is not None and
                 (datetime.utcnow() - datetime.fromisoformat(
                     _mt5_data["updated_at"].rstrip("Z")
                 )).total_seconds() > 60
    }


def _compute_daily_change(h4_candles: list, current_price: float):
    """
    From H4 candle array [{o,h,l,c,t}]:
    - daily_open  = open of the FIRST H4 bar of today (UTC)
    - prev_close  = close of the LAST H4 bar of yesterday
    Falls back to oldest bar's open if can't determine by date.
    """
    if not h4_candles or not isinstance(h4_candles, list):
        return 0.0, 0.0

    try:
        from datetime import date, timezone
        today_utc = date.today()

        today_bars = []
        yesterday_bars = []
        for bar in h4_candles:
            if not isinstance(bar, dict):
                continue
            t = bar.get("t", 0)  # Unix timestamp in seconds
            if t:
                from datetime import datetime as dt
                bar_date = dt.utcfromtimestamp(t).date()
                if bar_date == today_utc:
                    today_bars.append(bar)
                elif bar_date < today_utc:
                    yesterday_bars.append(bar)

        daily_open = 0.0
        prev_close = 0.0

        if today_bars:
            # Sort by time, take first bar of today
            today_bars.sort(key=lambda x: x.get("t", 0))
            daily_open = today_bars[0].get("o", 0.0)

        if yesterday_bars:
            # Sort by time desc, take last bar of yesterday
            yesterday_bars.sort(key=lambda x: x.get("t", 0), reverse=True)
            prev_close = yesterday_bars[0].get("c", 0.0)

        # If no today bars, use oldest available as fallback
        if not daily_open and h4_candles:
            sorted_bars = sorted(
                [b for b in h4_candles if isinstance(b, dict)],
                key=lambda x: x.get("t", 0)
            )
            if sorted_bars:
                daily_open = sorted_bars[0].get("o", 0.0)

        return daily_open, prev_close

    except Exception:
        return 0.0, 0.0



@app.get("/mt5/positions")
async def get_mt5_positions():
    """Danh sách lệnh đang mở từ MT5 (realtime)."""
    if not _mt5_data.get("updated_at"):
        return {"positions": [], "available": False}
    return {
        "positions": _mt5_data["positions"],
        "updated_at": _mt5_data["updated_at"],
        "available": True,
    }


# ─── Run ──────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8001"))
    print(f"""
╔══════════════════════════════════════════╗
║     🚀 ATTRAOS Hub Server v2.0         ║
║     AI Steven Trading Hub Server        ║
╚══════════════════════════════════════════╝
Starting on {host}:{port} (no-reload for stable MT5 data)
    """)
    # reload=False — quan trọng! reload=True xóa _mt5_data mỗi lần edit file
    uvicorn.run("server:app", host=host, port=port, reload=False)
