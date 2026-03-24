"""
hub_config.py — Remote Config API + Admin CRUD for config/prompts
Endpoints:
  GET  /v1/config                  → app fetches on startup (cache 1h)
  POST /admin/config               → update a config key
  GET  /admin/prompts              → list all prompts
  PUT  /admin/prompts/{name}       → update an AI prompt
"""
import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Header, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from hub_database import SessionLocal, get_config, set_config, get_prompt, Config, AIPrompt

router = APIRouter()

# ── Cache ──────────────────────────────────────────────────────────────────
_config_cache: dict = {}
_config_cache_time: float = 0
CONFIG_CACHE_SECONDS = 3600  # 1 hour


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_admin(request: Request, x_admin_token: str = Header(None)):
    """Accept token from Header (API) or query param (browser)."""
    import os
    token = os.getenv("ADMIN_TOKEN", "attraos_admin_2026")
    provided = x_admin_token or request.query_params.get("token")
    if provided != token:
        raise HTTPException(status_code=401, detail="Invalid admin token")
    return True


# ── App Config Endpoint ────────────────────────────────────────────────────

@router.get("/v1/config")
async def get_app_config(db: Session = Depends(get_db)):
    """
    Remote config — iOS app fetches on startup.
    Returns full config object. Cached 1h server-side.
    """
    global _config_cache, _config_cache_time
    import time
    if _config_cache and (time.time() - _config_cache_time) < CONFIG_CACHE_SECONDS:
        return _config_cache

    config = {
        "features":        get_config(db, "features", {}),
        "tiers":           get_config(db, "tiers", {}),
        "ai":              get_config(db, "ai", {}),
        "assets":          get_config(db, "assets", ["XAUUSD"]),
        "announcement":    get_config(db, "announcement", {"show": False}),
        "market_note":     get_config(db, "market_note", ""),
        "app_version_min": get_config(db, "app_version_min", "1.0.0"),
        "server_time":     datetime.utcnow().isoformat(),
    }

    # Embed AI prompts into config so app can use server-side prompts
    config["ai"]["judge_prompt"] = get_prompt(db, "judge_system")
    config["ai"]["analyze_prompt"] = get_prompt(db, "analyze_system")

    _config_cache = config
    _config_cache_time = time.time()
    return config


# ── Admin Config CRUD ──────────────────────────────────────────────────────

class ConfigUpdate(BaseModel):
    key: str
    value: object  # any JSON-serializable


@router.post("/admin/config")
async def update_config(
    body: ConfigUpdate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin),
):
    """Update a config key. Clears cache so app picks up change within 1h."""
    global _config_cache, _config_cache_time
    set_config(db, body.key, body.value)
    _config_cache = {}
    _config_cache_time = 0
    return {"status": "ok", "key": body.key, "updated": datetime.utcnow().isoformat()}


@router.get("/admin/config")
async def list_all_config(
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin),
):
    """List all config keys for admin dashboard."""
    rows = db.query(Config).all()
    result = []
    for row in rows:
        try:
            val = json.loads(row.value)
        except Exception:
            val = row.value
        result.append({
            "key": row.key,
            "value": val,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        })
    return {"config": result, "count": len(result)}


# ── Admin Prompt CRUD ──────────────────────────────────────────────────────

class PromptUpdate(BaseModel):
    content: str


@router.get("/admin/prompts")
async def list_prompts(
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin),
):
    rows = db.query(AIPrompt).all()
    return {"prompts": [
        {"name": r.name, "content": r.content,
         "updated_at": r.updated_at.isoformat() if r.updated_at else None}
        for r in rows
    ]}


@router.put("/admin/prompts/{name}")
async def update_prompt(
    name: str,
    body: PromptUpdate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin),
):
    """Update an AI prompt. Clears config cache."""
    global _config_cache, _config_cache_time
    row = db.get(AIPrompt, name)
    if row:
        row.content = body.content
        row.updated_at = datetime.utcnow()
    else:
        db.add(AIPrompt(name=name, content=body.content))
    db.commit()
    _config_cache = {}
    _config_cache_time = 0
    return {"status": "ok", "name": name}


# ── AI Keys Management ─────────────────────────────────────────────────────
# Admin có thể set key từ iOS app hoặc web — không cần SSH vào VPS

AI_KEY_NAMES = {
    "gemini":   "ai_key_gemini",
    "deepseek": "ai_key_deepseek",
    "openai":   "ai_key_openai",
}


class AIKeyUpdate(BaseModel):
    provider: str   # gemini | deepseek | openai
    key: str        # API key value


@router.get("/admin/ai-keys")
async def list_ai_keys(
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin),
):
    """List all AI key providers (masked) for admin dashboard."""
    result = {}
    for provider, db_key in AI_KEY_NAMES.items():
        val = get_config(db, db_key, "")
        result[provider] = {
            "configured": bool(val),
            "masked": (val[:8] + "..." + val[-4:]) if len(val) > 12 else ("***" if val else ""),
        }
    return {"ai_keys": result}


@router.post("/admin/ai-keys")
async def set_ai_key(
    body: AIKeyUpdate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin),
):
    """
    Set API key cho AI provider (gemini / deepseek / openai).
    Key được lưu vào DB — bookmap_council.py sẽ đọc tự động.
    Không cần SSH hay restart server.
    """
    provider = body.provider.lower()
    if provider not in AI_KEY_NAMES:
        raise HTTPException(400, f"Provider không hợp lệ. Chọn: {list(AI_KEY_NAMES.keys())}")
    db_key = AI_KEY_NAMES[provider]
    set_config(db, db_key, body.key)
    # Apply vào os.environ ngay để Council dùng được không cần restart
    import os
    env_map = {
        "gemini":   "GEMINI_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
        "openai":   "OPENAI_API_KEY",
    }
    os.environ[env_map[provider]] = body.key
    return {
        "status": "ok",
        "provider": provider,
        "applied": True,
        "message": f"✅ {provider.title()} API key đã được lưu và kích hoạt ngay. Hội Đồng AI sẽ dùng trong lần phân tích tiếp theo."
    }


@router.delete("/admin/ai-keys/{provider}")
async def delete_ai_key(
    provider: str,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin),
):
    """Xóa API key của provider."""
    import os
    provider = provider.lower()
    if provider not in AI_KEY_NAMES:
        raise HTTPException(400, f"Provider không hợp lệ")
    set_config(db, AI_KEY_NAMES[provider], "")
    env_map = {"gemini": "GEMINI_API_KEY", "deepseek": "DEEPSEEK_API_KEY", "openai": "OPENAI_API_KEY"}
    os.environ.pop(env_map.get(provider, ""), None)
    return {"status": "ok", "provider": provider, "message": f"{provider} key đã xóa."}
