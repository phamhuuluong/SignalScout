"""
hub_ai.py — AI Proxy with Admin Keys
Endpoints (API contract — DO NOT CHANGE URLs):
  POST /v1/ai/analyze   → 7-dimension analysis with admin Gemini/DeepSeek key
  POST /v1/ai/discuss   → AI Council 3 rounds (Gemini + DeepSeek + Judge)
  POST /v1/ai/chat      → Freestyle AI chat
"""
import os
import json
import httpx
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session

from hub_database import SessionLocal, get_config, get_prompt

router = APIRouter()

GEMINI_KEY  = os.getenv("ADMIN_GEMINI_KEY", "")
DEEPSEEK_KEY = os.getenv("ADMIN_DEEPSEEK_KEY", "")
OPENAI_KEY  = os.getenv("ADMIN_OPENAI_KEY", "")

# Rate limiting (simple in-memory — replace with Redis in production)
_usage: dict[str, list] = {}
MAX_ANALYZE_PER_HOUR = int(os.getenv("MAX_ANALYZE_PER_HOUR", "20"))


def _get_mt5_smc_text(symbol: str) -> str:
    """Lấy SMC summary từ MT5 data để inject vào AI prompt."""
    try:
        import server as _srv
        from market_data import Candle as _Candle
        from smc_detector import analyze_smc

        mt5 = _srv._mt5_data
        if not mt5.get("updated_at") or not mt5.get("market"):
            return ""

        sym_d = next((m for m in mt5["market"] if m.get("symbol", "").upper() == symbol.upper()), None)
        if not sym_d:
            return ""

        lines = [f"\n=== MT5 Realtime SMC: {symbol} ===",
                 f"Bid: {sym_d.get('bid')} | Ask: {sym_d.get('ask')} | ATR: {sym_d.get('atr'):.4f}"]

        for tf_key, tf_name in (("m15", "M15"), ("h1", "H1"), ("h4", "H4")):
            raw = sym_d.get(tf_key, [])
            if len(raw) < 20:
                continue
            candles = [_Candle(int(c["t"]), float(c["o"]), float(c["h"]),
                               float(c["l"]), float(c["c"]), int(c.get("v", 0)))
                       for c in raw]
            smc = analyze_smc(candles)
            lines.append(
                f"{tf_name}: struct={smc.get('structure')} "
                f"FVG={len(smc.get('fvg', []))} OB={len(smc.get('ob', []))} "
                f"BOS_last={smc.get('bos', [{}])[-1] if smc.get('bos') else 'N/A'}"
            )
        return "\n".join(lines)
    except Exception:
        return ""


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_rate_limit(device_id: str, action: str):
    """Allow max N calls per hour per device per action."""
    import time
    key = f"{device_id}:{action}"
    now = time.time()
    calls = [t for t in _usage.get(key, []) if now - t < 3600]
    if len(calls) >= MAX_ANALYZE_PER_HOUR:
        raise HTTPException(429, "Rate limit exceeded. Try again in 1 hour.")
    calls.append(now)
    _usage[key] = calls


# ── Request Models ────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    asset: str          # e.g. "XAUUSD"
    market_data: dict   # {price, change_pct, ema200, rsi, atr...}
    news: str = ""      # recent news summary
    sentiment: str = "" # market sentiment
    device_id: str = "" # for rate limiting


class DiscussRequest(BaseModel):
    asset: str
    market_data: dict
    news: str = ""
    sentiment: str = ""
    round: int = 1      # 1=Gemini, 2=DeepSeek, 3=Judge
    previous: str = ""  # previous round's analysis
    force_refresh: bool = False
    device_id: str = ""


class ChatRequest(BaseModel):
    message: str        # user's question
    context: str = ""   # market context (current prices)
    device_id: str = ""


# ── Gemini Call ───────────────────────────────────────────────────────────

async def call_gemini(system: str, user: str, temperature: float = 0.1) -> str:
    if not GEMINI_KEY:
        return "[Gemini key not configured on server]"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GEMINI_KEY}"
    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"parts": [{"text": user}]}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": 1500}
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]


# ── DeepSeek Call ─────────────────────────────────────────────────────────

async def call_deepseek(system: str, user: str, temperature: float = 0.1) -> str:
    if not DEEPSEEK_KEY:
        return "[DeepSeek key not configured on server]"
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://api.deepseek.com/chat/completions",
            headers={"Authorization": f"Bearer {DEEPSEEK_KEY}"},
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": temperature,
                "max_tokens": 1500,
            }
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


# ── Endpoints ─────────────────────────────────────────────────────────────

@router.post("/v1/ai/analyze")
async def ai_analyze(body: AnalyzeRequest, db: Session = Depends(get_db)):
    """7-dimension market analysis using admin API key."""
    if body.device_id:
        check_rate_limit(body.device_id, "analyze")

    ai_cfg = get_config(db, "ai", {})
    temp = ai_cfg.get("temperature", 0.1)
    system_prompt = get_prompt(db, "analyze_system",
        "Bạn là chuyên gia phân tích kỹ thuật Gold/Forex với 10 năm kinh nghiệm SMC/ICT.")

    user_prompt = f"""
Phân tích {body.asset} với dữ liệu sau:
{json.dumps(body.market_data, ensure_ascii=False, indent=2)}

Tin tức gần đây: {body.news or 'Không có'}
Sentiment: {body.sentiment or 'Neutral'}

Phân tích 7 chiều: Trend, Momentum, News, Sentiment, Volume, SMC Structure, Risk.
Trả lời bằng tiếng Việt, ngắn gọn và chuyên nghiệp.
"""
    try:
        result = await call_gemini(system_prompt, user_prompt, temp)
        return {
            "asset": body.asset,
            "analysis": result,
            "model": "gemini-2.0-flash",
            "source": "admin_key",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(500, f"AI analysis failed: {str(e)}")


@router.post("/v1/ai/discuss")
async def ai_discuss(body: DiscussRequest, db: Session = Depends(get_db)):
    """AI Council — 3 rounds: Gemini → DeepSeek → Judge."""
    if body.device_id:
        check_rate_limit(body.device_id, f"discuss_r{body.round}")

    ai_cfg = get_config(db, "ai", {})
    temp = ai_cfg.get("temperature", 0.1)
    min_pass = ai_cfg.get("min_checklist_pass", 4)

    market_str = json.dumps(body.market_data, ensure_ascii=False)

    if body.round == 1:
        # Round 1: Gemini — HTF & Structure Analyst
        system = get_prompt(db, "round1_system",
            "Bạn là AI-1 (Gemini) trong Hội Đồng AI. Chuyên phân tích HTF trend và market structure. "
            "Sử dụng SMC data thực tế từ MT5 broker.")

        # Tự động thêm SMC data mt5 vào analyze
        smc_addition = _get_mt5_smc_text(body.asset)
        user = f"Phân tích {body.asset}: {market_str}\nTin tức: {body.news}\n{smc_addition}"
        result = await call_gemini(system, user, temp)
        return {"round": 1, "model": "gemini", "result": result, "timestamp": datetime.utcnow().isoformat()}

    elif body.round == 2:
        # Round 2: DeepSeek — SMC & LTF Confirmation
        system = get_prompt(db, "round2_system",
            "Bạn là AI-2 (DeepSeek) trong Hội Đồng AI. Chuyên SMC: Order Block, FVG, Break of Structure.")
        user = f"Phân tích SMC {body.asset}: {market_str}\nPhân tích vòng 1: {body.previous}"
        result = await call_deepseek(system, user, temp)
        return {"round": 2, "model": "deepseek", "result": result, "timestamp": datetime.utcnow().isoformat()}

    elif body.round == 3:
        # Round 3: AI Judge — Final Verdict with 5-point checklist
        judge_prompt = get_prompt(db, "judge_system",
            f"""Bạn là AI Judge (Thẩm phán) trong Hội Đồng AI Trading. Kiểm tra 5 điều kiện:
1. HTF Trend (H4/D1) rõ ràng không?
2. SMC Zone (OB/FVG) xác nhận không?
3. LTF (M15) entry confirmation không?
4. Risk/Reward >= 1:2 không?
5. Không có high-impact news trong 2h không?

Cần {min_pass}/5 PASS mới cho BUY/SELL. Ngược lại output NONE.

Output JSON: {{"direction":"BUY/SELL/NONE","entry":0,"sl":0,"tp":0,"checklist":[true/false x5],"reason":"..."}}""")

        user = f"""
Asset: {body.asset}
Data: {market_str}
Vòng 1 (Gemini): {body.previous[:500] if body.previous else 'N/A'}
Tin tức: {body.news}

Đưa ra phán quyết cuối.
"""
        result = await call_gemini(judge_prompt, user, temp)
        return {"round": 3, "model": "judge", "result": result, "timestamp": datetime.utcnow().isoformat()}

    raise HTTPException(400, "Round must be 1, 2, or 3")


@router.post("/v1/ai/chat")
async def ai_chat(body: ChatRequest, db: Session = Depends(get_db)):
    """Freestyle AI chat — tự động lấy MT5 realtime context + SMC."""
    if body.device_id:
        check_rate_limit(body.device_id, "chat")

    # Tự động lấy MT5 context nếu chưa có
    mt5_context = body.context
    if not mt5_context:
        try:
            import server as _srv
            mt5 = _srv._mt5_data
            if mt5.get("updated_at") and mt5.get("market"):
                from market_data import Candle as _Candle
                from smc_detector import analyze_smc

                ctx_lines = ["=== MT5 Realtime Data ==="]
                for sym_d in mt5["market"][:3]:  # Tối đa 3 symbols
                    sym = sym_d.get("symbol", "")
                    bid = sym_d.get("bid", 0)
                    ask = sym_d.get("ask", 0)
                    atr = sym_d.get("atr", 0)
                    ctx_lines.append(f"{sym}: Bid={bid:.5f} Ask={ask:.5f} ATR={atr:.4f}")

                    # SMC M15
                    raw15 = sym_d.get("m15", [])
                    if len(raw15) >= 20:
                        try:
                            c15 = [_Candle(int(c["t"]), float(c["o"]), float(c["h"]),
                                           float(c["l"]), float(c["c"]), int(c.get("v", 0)))
                                   for c in raw15]
                            smc = analyze_smc(c15)
                            ctx_lines.append(
                                f"  SMC M15: structure={smc.get('structure')} "
                                f"FVG={len(smc.get('fvg', []))} "
                                f"OB={len(smc.get('ob', []))} "
                                f"BOS={smc.get('bos', [{}])[-1:] if smc.get('bos') else 'N/A'}"
                            )
                        except Exception:
                            pass

                # Open positions
                positions = mt5.get("positions", [])
                if positions:
                    ctx_lines.append(f"Lệnh mở: " + ", ".join(
                        f"{p.get('symbol')} {p.get('type')} {p.get('volume')}lot P/L=${p.get('profit'):.2f}"
                        for p in positions
                    ))

                mt5_context = "\n".join(ctx_lines)
        except Exception:
            pass  # nếu lỏi, chat bình thường không có context

    system = get_prompt(db, "chat_system",
        "Bạn là trợ lý trading AI thông minh của ATTRAOS. "
        "Dùng data realtime từ MT5 broker, SMC analysis thực tế. "
        "Trả lời ngắn gọn, thực tế, bằng tiếng Việt.")

    user = body.message
    if mt5_context:
        user = f"[Dữ liệu thị trường thực tế từ MT5:\n{mt5_context}]\n\n{body.message}"

    try:
        result = await call_gemini(system, user, temperature=0.3)
        return {
            "reply": result,
            "model": "gemini",
            "has_mt5_context": bool(mt5_context),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(500, f"AI chat failed: {str(e)}")
