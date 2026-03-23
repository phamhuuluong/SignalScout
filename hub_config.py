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
