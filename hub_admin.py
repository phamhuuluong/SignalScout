"""
hub_admin.py — Admin Dashboard Web UI
Truy cập: http://localhost:8000/admin
Đăng nhập bằng ADMIN_TOKEN trong .env
"""
import json
import os
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Form, Header
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from hub_database import (
    SessionLocal, Config, AIPrompt, Lesson, HotNews, PremiumUser,
    get_config, set_config
)

router = APIRouter(prefix="/admin")

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "attraos_admin_2026")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_token(request: Request):
    """Check token from query param or cookie."""
    token = request.query_params.get("token") or request.cookies.get("admin_token")
    if token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized. Add ?token=YOUR_TOKEN")
    return True


def page(title: str, body: str, token: str = "") -> HTMLResponse:
    """Wrap content in admin layout."""
    nav = f"""
    <nav style="background:#1a1a2e;padding:12px 24px;display:flex;gap:20px;align-items:center;border-bottom:1px solid #333">
      <span style="color:#FFD700;font-weight:bold;font-size:18px">⚙️ ATTRAOS Admin</span>
      <a href="/admin?token={token}" style="color:#aaa;text-decoration:none">🏠 Overview</a>
      <a href="/admin/mt5?token={token}" style="color:#00ff88;text-decoration:none;font-weight:bold">📡 MT5 Live</a>
      <a href="/admin/config?token={token}" style="color:#aaa;text-decoration:none">⚙️ Config</a>
      <a href="/admin/lessons?token={token}" style="color:#aaa;text-decoration:none">📚 Academy</a>
      <a href="/admin/prompts?token={token}" style="color:#aaa;text-decoration:none">🤖 AI Prompts</a>
      <a href="/admin/news?token={token}" style="color:#aaa;text-decoration:none">📰 News Push</a>
      <a href="/admin/users?token={token}" style="color:#aaa;text-decoration:none">👥 Users</a>
    </nav>"""

    return HTMLResponse(f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} — ATTRAOS Admin</title>
  <script src="https://unpkg.com/htmx.org@1.9.12"></script>
  <style>
    * {{ box-sizing:border-box; margin:0; padding:0 }}
    body {{ background:#0d0d1a; color:#e0e0e0; font-family:system-ui,sans-serif }}
    .container {{ max-width:1100px; margin:0 auto; padding:24px }}
    h1 {{ color:#FFD700; margin-bottom:20px }}
    h2 {{ color:#ccc; margin:16px 0 8px }}
    .card {{ background:#1a1a2e; border:1px solid #2a2a4a; border-radius:10px; padding:20px; margin-bottom:16px }}
    input, textarea, select {{
      width:100%; padding:10px; background:#0d0d1a; border:1px solid #333;
      color:#e0e0e0; border-radius:6px; font-size:14px; margin:4px 0 12px
    }}
    textarea {{ min-height:120px; font-family:monospace }}
    button, .btn {{
      background:#FFD700; color:#000; border:none; padding:10px 20px;
      border-radius:6px; cursor:pointer; font-weight:bold; font-size:14px
    }}
    button:hover {{ background:#FFC400 }}
    .btn-red {{ background:#c0392b; color:#fff }}
    .btn-gray {{ background:#444; color:#fff }}
    table {{ width:100%; border-collapse:collapse }}
    th,td {{ padding:10px 12px; text-align:left; border-bottom:1px solid #2a2a4a; font-size:14px }}
    th {{ color:#FFD700; font-weight:600 }}
    .badge {{ padding:3px 8px; border-radius:12px; font-size:12px; font-weight:bold }}
    .badge-green {{ background:#1a4a1a; color:#4CAF50 }}
    .badge-gray {{ background:#2a2a2a; color:#888 }}
    .badge-gold {{ background:#3a2a00; color:#FFD700 }}
    .success {{ color:#4CAF50; margin:8px 0 }}
    .error {{ color:#f44336; margin:8px 0 }}
  </style>
</head>
<body>
{nav}
<div class="container">
  <h1>{title}</h1>
  {body}
</div>
</body></html>""")


# ── Overview ──────────────────────────────────────────────────────────────

@router.get("", response_class=HTMLResponse)
async def admin_home(request: Request, db: Session = Depends(get_db)):
    verify_token(request)
    token = request.query_params.get("token", "")

    lesson_count = db.query(Lesson).count()
    user_count = db.query(PremiumUser).count()
    news_count = db.query(HotNews).count()
    ai_on = get_config(db, "features", {}).get("ai_council", True)
    market_note = get_config(db, "market_note", "")

    body = f"""
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:24px">
      <div class="card" style="text-align:center">
        <div style="font-size:32px">📚</div>
        <div style="font-size:28px;color:#FFD700;font-weight:bold">{lesson_count}</div>
        <div style="color:#888">Bài học</div>
      </div>
      <div class="card" style="text-align:center">
        <div style="font-size:32px">👥</div>
        <div style="font-size:28px;color:#FFD700;font-weight:bold">{user_count}</div>
        <div style="color:#888">User Premium</div>
      </div>
      <div class="card" style="text-align:center">
        <div style="font-size:32px">📰</div>
        <div style="font-size:28px;color:#FFD700;font-weight:bold">{news_count}</div>
        <div style="color:#888">Tin đã push</div>
      </div>
      <div class="card" style="text-align:center">
        <div style="font-size:32px">{'🟢' if ai_on else '🔴'}</div>
        <div style="font-size:28px;color:#FFD700;font-weight:bold">{'ON' if ai_on else 'OFF'}</div>
        <div style="color:#888">AI Council</div>
      </div>
    </div>

    <div class="card">
      <h2>📝 Nhận định thị trường hôm nay</h2>
      <p style="color:#888;font-size:13px">Hiển thị ngay trên app sau khi lưu (không cần update)</p>
      <form method="post" action="/admin/market-note?token={token}">
        <textarea name="note" placeholder="Nhập nhận định thị trường...">{market_note}</textarea>
        <button type="submit">💾 Lưu & Publish Ngay</button>
      </form>
    </div>

    <div class="card">
      <h2>🔗 API Endpoints</h2>
      <table>
        <tr><th>Endpoint</th><th>Dùng bởi</th><th>Cache</th></tr>
        <tr><td><code>GET /v1/config</code></td><td>iOS startup</td><td>1h</td></tr>
        <tr><td><code>POST /v1/ai/analyze</code></td><td>Analysis screen</td><td>No</td></tr>
        <tr><td><code>POST /v1/ai/discuss</code></td><td>AI Council</td><td>No</td></tr>
        <tr><td><code>GET /academy/lessons</code></td><td>Academy list</td><td>No</td></tr>
        <tr><td><code>GET /signals</code></td><td>Signal Radar</td><td>60s</td></tr>
      </table>
    </div>
    """
    return page("🏠 Overview", body, token)


@router.post("/market-note", response_class=HTMLResponse)
async def update_market_note(request: Request, note: str = Form(""), db: Session = Depends(get_db)):
    verify_token(request)
    token = request.query_params.get("token", "")
    set_config(db, "market_note", note)
    from hub_config import _config_cache
    _config_cache.clear() if isinstance(_config_cache, dict) else None
    from fastapi.responses import RedirectResponse
    return RedirectResponse(f"/admin?token={token}", status_code=303)


# ── Config ────────────────────────────────────────────────────────────────

@router.get("/config", response_class=HTMLResponse)
async def admin_config(request: Request, db: Session = Depends(get_db)):
    verify_token(request)
    token = request.query_params.get("token", "")

    rows = db.query(Config).all()
    rows_html = ""
    for row in rows:
        try:
            val = json.dumps(json.loads(row.value), ensure_ascii=False, indent=2)
        except Exception:
            val = row.value
        rows_html += f"""
        <div class="card">
          <h2><code>{row.key}</code></h2>
          <form method="post" action="/admin/config/update?token={token}">
            <input type="hidden" name="key" value="{row.key}">
            <textarea name="value">{val}</textarea>
            <button type="submit">💾 Lưu</button>
          </form>
        </div>"""

    return page("⚙️ Remote Config", rows_html, token)


@router.post("/config/update", response_class=HTMLResponse)
async def update_config_form(request: Request, key: str = Form(...), value: str = Form(...), db: Session = Depends(get_db)):
    verify_token(request)
    token = request.query_params.get("token", "")
    try:
        parsed = json.loads(value)
    except Exception:
        parsed = value
    set_config(db, key, parsed)
    from fastapi.responses import RedirectResponse
    return RedirectResponse(f"/admin/config?token={token}", status_code=303)


# ── Academy Lessons ───────────────────────────────────────────────────────

@router.get("/lessons", response_class=HTMLResponse)
async def admin_lessons(request: Request, db: Session = Depends(get_db)):
    verify_token(request)
    token = request.query_params.get("token", "")
    lessons = db.query(Lesson).order_by(Lesson.category, Lesson.order).all()

    rows = ""
    for l in lessons:
        status = '<span class="badge badge-green">Active</span>' if l.active else '<span class="badge badge-gray">Hidden</span>'
        premium = '<span class="badge badge-gold">Premium</span>' if l.premium else ''
        rows += f"""<tr>
          <td>{l.id}</td><td>{l.category}</td><td>{l.title}</td>
          <td>{status} {premium}</td>
          <td>{l.xp} XP</td>
          <td>
            <a href="/admin/lessons/{l.id}/edit?token={token}" class="btn btn-gray" style="padding:4px 10px;text-decoration:none;font-size:12px">✏️ Sửa</a>
          </td>
        </tr>"""

    body = f"""
    <a href="/admin/lessons/new?token={token}" class="btn" style="text-decoration:none;display:inline-block;margin-bottom:16px">➕ Tạo Bài Mới</a>
    <div class="card">
      <table>
        <tr><th>ID</th><th>Category</th><th>Tiêu đề</th><th>Trạng thái</th><th>XP</th><th></th></tr>
        {rows if rows else '<tr><td colspan="6" style="color:#666;text-align:center">Chưa có bài học nào</td></tr>'}
      </table>
    </div>"""
    return page("📚 Academy Lessons", body, token)


@router.get("/lessons/new", response_class=HTMLResponse)
@router.get("/lessons/{lesson_id}/edit", response_class=HTMLResponse)
async def lesson_form(request: Request, lesson_id: str = "new", db: Session = Depends(get_db)):
    verify_token(request)
    token = request.query_params.get("token", "")
    lesson = db.get(Lesson, lesson_id) if lesson_id != "new" else None

    def v(field, default=""):
        return getattr(lesson, field, default) or default

    action = f"/admin/lessons/save?token={token}"
    body = f"""
    <div class="card">
      <form method="post" action="{action}">
        <input type="hidden" name="original_id" value="{v('id')}">
        <label>ID (không đổi sau khi tạo)</label>
        <input name="id" value="{v('id')}" placeholder="smc_01" {'readonly' if lesson else ''}>
        <label>Category</label>
        <input name="category" value="{v('category')}" placeholder="smc / ict / risk">
        <label>Tiêu đề</label>
        <input name="title" value="{v('title')}" placeholder="Order Block là gì?">
        <label>Mô tả ngắn</label>
        <input name="description" value="{v('description')}" placeholder="Học cách nhận diện OB...">
        <label>Nội dung (Markdown)</label>
        <textarea name="content" style="min-height:200px">{v('content')}</textarea>
        <label>Quiz (JSON array)</label>
        <textarea name="quiz_json">{v('quiz_json', '[]')}</textarea>
        <label>XP</label>
        <input name="xp" type="number" value="{v('xp', 10)}">
        <label>Phút học ước tính</label>
        <input name="minutes" type="number" value="{v('minutes', 5)}">
        <label><input type="checkbox" name="premium" {'checked' if v('premium') else ''}> Premium only</label><br><br>
        <label><input type="checkbox" name="active" {'checked' if v('active', True) else ''}> Active (hiển thị)</label><br><br>
        <button type="submit">💾 Lưu Bài Học</button>
        <a href="/admin/lessons?token={token}" class="btn btn-gray" style="text-decoration:none;margin-left:10px">Hủy</a>
      </form>
    </div>"""
    return page("✏️ Bài Học", body, token)


@router.post("/lessons/save")
async def save_lesson(
    request: Request,
    id: str = Form(...), original_id: str = Form(""),
    category: str = Form(...), title: str = Form(...),
    description: str = Form(""), content: str = Form(""),
    quiz_json: str = Form("[]"), xp: int = Form(10),
    minutes: int = Form(5), premium: str = Form(None),
    active: str = Form(None),
    db: Session = Depends(get_db)
):
    verify_token(request)
    token = request.query_params.get("token", "")
    existing = db.get(Lesson, id) or (db.get(Lesson, original_id) if original_id else None)
    if existing:
        existing.category = category
        existing.title = title
        existing.description = description
        existing.content = content
        existing.quiz_json = quiz_json
        existing.xp = xp
        existing.minutes = minutes
        existing.premium = premium is not None
        existing.active = active is not None
        existing.updated_at = datetime.utcnow()
    else:
        db.add(Lesson(
            id=id, category=category, title=title,
            description=description, content=content,
            quiz_json=quiz_json, xp=xp, minutes=minutes,
            premium=premium is not None, active=active is not None
        ))
    db.commit()
    from fastapi.responses import RedirectResponse
    return RedirectResponse(f"/admin/lessons?token={token}", status_code=303)


# ── AI Prompts ────────────────────────────────────────────────────────────

@router.get("/prompts", response_class=HTMLResponse)
async def admin_prompts(request: Request, db: Session = Depends(get_db)):
    verify_token(request)
    token = request.query_params.get("token", "")
    prompts = db.query(AIPrompt).all()

    cards = ""
    for p in prompts:
        cards += f"""
        <div class="card">
          <h2>🤖 <code>{p.name}</code></h2>
          <p style="color:#888;font-size:12px">Cập nhật: {p.updated_at.strftime('%d/%m/%Y %H:%M') if p.updated_at else 'N/A'}</p>
          <form method="post" action="/admin/prompts/update?token={token}">
            <input type="hidden" name="name" value="{p.name}">
            <textarea name="content">{p.content}</textarea>
            <button type="submit">💾 Lưu Prompt</button>
          </form>
        </div>"""

    body = f"""
    <p style="color:#888;margin-bottom:16px">⚠️ Thay đổi prompt sẽ ảnh hưởng đến hành vi AI ngay lập tức (không cần update app)</p>
    {cards}"""
    return page("🤖 AI Prompts", body, token)


@router.post("/prompts/update")
async def save_prompt(
    request: Request,
    name: str = Form(...), content: str = Form(...),
    db: Session = Depends(get_db)
):
    verify_token(request)
    token = request.query_params.get("token", "")
    row = db.get(AIPrompt, name)
    if row:
        row.content = content
        row.updated_at = datetime.utcnow()
    else:
        db.add(AIPrompt(name=name, content=content))
    db.commit()
    from fastapi.responses import RedirectResponse
    return RedirectResponse(f"/admin/prompts?token={token}", status_code=303)


# ── News Push ─────────────────────────────────────────────────────────────

@router.get("/news", response_class=HTMLResponse)
async def admin_news(request: Request, db: Session = Depends(get_db)):
    verify_token(request)
    token = request.query_params.get("token", "")
    recent = db.query(HotNews).order_by(HotNews.pushed_at.desc()).limit(10).all()

    rows = "".join(f"""<tr>
      <td>{n.title}</td><td>{n.asset or 'All'}</td>
      <td>{'✅' if n.push_sent else '⏳'}</td>
      <td>{n.pushed_at.strftime('%d/%m %H:%M') if n.pushed_at else ''}</td>
    </tr>""" for n in recent)

    body = f"""
    <div class="card">
      <h2>📤 Push Tin Nóng</h2>
      <form method="post" action="/admin/news/push?token={token}">
        <input name="title" placeholder="Tiêu đề tin nóng..." required>
        <textarea name="body" placeholder="Nội dung chi tiết (optional)..." style="min-height:80px"></textarea>
        <input name="asset" placeholder="Asset liên quan (XAUUSD / để trống = all)">
        <button type="submit">🚀 Push Ngay</button>
      </form>
    </div>
    <div class="card">
      <h2>📋 Lịch sử Push</h2>
      <table>
        <tr><th>Tiêu đề</th><th>Asset</th><th>Đã gửi</th><th>Thời gian</th></tr>
        {rows or '<tr><td colspan="4" style="color:#666">Chưa có</td></tr>'}
      </table>
    </div>"""
    return page("📰 News Push", body, token)


@router.post("/news/push")
async def push_news(
    request: Request,
    title: str = Form(...), body: str = Form(""), asset: str = Form(""),
    db: Session = Depends(get_db)
):
    verify_token(request)
    token = request.query_params.get("token", "")
    news = HotNews(title=title, body=body, asset=asset, push_sent=False)
    db.add(news)
    db.commit()
    # TODO: integrate Firebase FCM push here
    news.push_sent = True
    db.commit()
    from fastapi.responses import RedirectResponse
    return RedirectResponse(f"/admin/news?token={token}", status_code=303)


# ── Users ─────────────────────────────────────────────────────────────────

@router.get("/users", response_class=HTMLResponse)
async def admin_users(request: Request, db: Session = Depends(get_db)):
    verify_token(request)
    token = request.query_params.get("token", "")
    users = db.query(PremiumUser).order_by(PremiumUser.created_at.desc()).all()

    rows = "".join(f"""<tr>
      <td style="font-size:12px;font-family:monospace">{u.device_id[:16]}...</td>
      <td><span class="badge badge-gold">{u.tier}</span></td>
      <td>{u.note}</td>
      <td>{u.created_at.strftime('%d/%m/%Y') if u.created_at else ''}</td>
    </tr>""" for u in users)

    body = f"""
    <div class="card">
      <h2>➕ Thêm User Premium</h2>
      <form method="post" action="/admin/users/add?token={token}">
        <input name="device_id" placeholder="Device ID từ app..." required>
        <select name="tier"><option value="premium">Premium</option><option value="admin">Admin</option></select>
        <input name="note" placeholder="Ghi chú (tên, liên hệ...)">
        <button type="submit">➕ Thêm</button>
      </form>
    </div>
    <div class="card">
      <h2>👥 Danh sách ({len(users)} users)</h2>
      <table>
        <tr><th>Device ID</th><th>Tier</th><th>Ghi chú</th><th>Ngày thêm</th></tr>
        {rows or '<tr><td colspan="4" style="color:#666">Chưa có</td></tr>'}
      </table>
    </div>"""
    return page("👥 Premium Users", body, token)


@router.post("/users/add")
async def add_user(
    request: Request,
    device_id: str = Form(...), tier: str = Form("premium"), note: str = Form(""),
    db: Session = Depends(get_db)
):
    verify_token(request)
    token = request.query_params.get("token", "")
    existing = db.get(PremiumUser, device_id)
    if not existing:
        db.add(PremiumUser(device_id=device_id, tier=tier, note=note))
        db.commit()
    from fastapi.responses import RedirectResponse
    return RedirectResponse(f"/admin/users?token={token}", status_code=303)


# ── MT5 Live Dashboard ─────────────────────────────────────────────────────

@router.get("/mt5", response_class=HTMLResponse)
async def admin_mt5(request: Request):
    verify_token(request)
    token = request.query_params.get("token", "")

    # Lấy MT5 data từ server.py global
    import server as _srv
    mt5 = _srv._mt5_data

    now = datetime.utcnow()
    updated_at = mt5.get("updated_at")
    ea_version  = mt5.get("ea_version", "—")
    broker_time = mt5.get("broker_time", "—")

    # Tính trạng thái kết nối
    if not updated_at:
        ea_status = "offline"
        ea_age_s  = -1
    else:
        dt = datetime.fromisoformat(updated_at.rstrip("Z"))
        ea_age_s  = (now - dt).total_seconds()
        if ea_age_s < 30:
            ea_status = "live"
        elif ea_age_s < 120:
            ea_status = "stale"
        else:
            ea_status = "offline"

    status_color = {"live": "#00ff88", "stale": "#FFD700", "offline": "#f44336"}[ea_status]
    status_icon  = {"live": "🟢", "stale": "🟡", "offline": "🔴"}[ea_status]
    age_str      = f"{int(ea_age_s)}s trước" if ea_age_s >= 0 else "—"

    # Market table
    market_rows = ""
    for m in mt5.get("market", []):
        sym   = m.get("symbol", "")
        bid   = m.get("bid", 0)
        ask   = m.get("ask", 0)
        spread= m.get("spread", 0)
        atr   = m.get("atr", 0)
        n_m15 = len(m.get("m15", []))
        n_h1  = len(m.get("h1", []))
        n_h4  = len(m.get("h4", []))
        smc_link = f"/mt5/smc?symbol={sym}&tf=m15"
        mid = (bid + ask) / 2.0
        market_rows += f"""<tr>
          <td><b style="color:#FFD700">{sym}</b></td>
          <td style="font-family:monospace;color:#4fc3f7">{mid:.5f}</td>
          <td style="font-family:monospace;color:#888;font-size:11px">{bid:.5f}</td>
          <td style="font-family:monospace;color:#888;font-size:11px">{ask:.5f}</td>
          <td style="color:#888">{spread:.1f}</td>
          <td style="color:#aaa">{atr:.4f}</td>
          <td style="color:#4CAF50">M15:{n_m15} H1:{n_h1} H4:{n_h4}</td>
          <td><a href="{smc_link}" target="_blank" style="color:#00bcd4;font-size:12px">🔍 SMC</a></td>
        </tr>"""

    if not market_rows:
        market_rows = "<tr><td colspan='8' style='color:#666;text-align:center'>EA chưa gửi data — Cần mở MT5 và chạy EA v2</td></tr>"

    # Account
    acc = mt5.get("account", {})
    acc_html = ""
    if acc:
        profit_color = "#4CAF50" if acc.get("profit", 0) >= 0 else "#f44336"
        acc_html = f"""
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px">
          <div class="card" style="text-align:center;padding:12px">
            <div style="color:#888;font-size:12px">Balance</div>
            <div style="color:#FFD700;font-size:20px;font-weight:bold">${acc.get('balance',0):,.2f}</div>
          </div>
          <div class="card" style="text-align:center;padding:12px">
            <div style="color:#888;font-size:12px">Equity</div>
            <div style="color:#4CAF50;font-size:20px;font-weight:bold">${acc.get('equity',0):,.2f}</div>
          </div>
          <div class="card" style="text-align:center;padding:12px">
            <div style="color:#888;font-size:12px">Profit</div>
            <div style="color:{profit_color};font-size:20px;font-weight:bold">${acc.get('profit',0):+,.2f}</div>
          </div>
          <div class="card" style="text-align:center;padding:12px">
            <div style="color:#888;font-size:12px">Free Margin</div>
            <div style="color:#aaa;font-size:20px;font-weight:bold">${acc.get('free_margin',0):,.2f}</div>
          </div>
        </div>
        <p style="color:#666;font-size:12px;margin-top:8px">
          {acc.get('name','—')} | {acc.get('server','—')} | #{acc.get('login','—')} | 1:{acc.get('leverage',0)}
        </p>"""
    else:
        acc_html = "<p style='color:#666'>Chưa có account data</p>"

    # Positions
    pos_rows = ""
    for p in mt5.get("positions", []):
        pcolor = "#4CAF50" if p.get("profit",0) >= 0 else "#f44336"
        pos_rows += f"""<tr>
          <td>{p.get('symbol')}</td>
          <td style="color:{'#4CAF50' if p.get('type')=='BUY' else '#f44336'}">{p.get('type')}</td>
          <td>{p.get('volume')} lot</td>
          <td style="font-family:monospace">{p.get('open_price',0):.5f}</td>
          <td style="font-family:monospace">{p.get('current_price',0):.5f}</td>
          <td style="color:{pcolor};font-weight:bold">${p.get('profit',0):+.2f}</td>
        </tr>"""

    body = f"""
    <!-- Auto-refresh mỗi 10 giây -->
    <script>setTimeout(()=>location.reload(),10000)</script>

    <!-- EA Status Banner -->
    <div class="card" style="border:1px solid {status_color};margin-bottom:16px">
      <div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap">
        <div style="font-size:32px">{status_icon}</div>
        <div>
          <div style="color:{status_color};font-size:18px;font-weight:bold">
            MT5 EA {'🔴 OFFLINE' if ea_status=='offline' else '🟡 STALE' if ea_status=='stale' else '🟢 LIVE — Đang kết nối'}
          </div>
          <div style="color:#888;font-size:13px">
            EA v{ea_version} | Broker time: {broker_time} | Cập nhật: {age_str}
            {'<br><span style="color:#f44336">⚠️ EA đã ngắt kết nối hoặc chưa chạy trong MT5</span>' if ea_status=='offline' else ''}
            {'<br><span style="color:#FFD700">⚠️ Data cũ hơn 30s — EA có thể bị treo</span>' if ea_status=='stale' else ''}
          </div>
        </div>
        <div style="margin-left:auto;text-align:right">
          <div style="color:#555;font-size:11px">Auto-refresh: 10s</div>
          <div style="color:#555;font-size:11px">{now.strftime('%H:%M:%S')} UTC</div>
        </div>
      </div>
    </div>

    <!-- Fix MT5 EA nếu offline -->
    {'<div class="card" style="border:1px solid #f44336;margin-bottom:16px"><h2>🔧 Fix EA Kết Nối</h2>' +
     '<ol style="color:#ccc;font-size:13px;line-height:2">' +
     '<li>MT5 → <b>Tools → Options → Expert Advisors</b></li>' +
     '<li>✅ Allow WebRequest → Thêm: <code style="color:#FFD700">http://127.0.0.1:8001</code></li>' +
     '<li><b>Đóng hoàn toàn MT5 rồi mở lại</b> (restart bắt buộc)</li>' +
     '<li>Kéo <code>MT5_ATTRAOS_Hub_v2</code> vào chart XAUUSD</li>' +
     '<li>Journal tab → phải thấy <code style="color:#4CAF50">✅ Gửi #1 OK</code></li>' +
     '</ol></div>' if ea_status == 'offline' else ''}

    <!-- Live Prices -->
    <div class="card">
      <h2>📊 Giá Live ({len(mt5.get('market',[]))} symbols)</h2>
      <table>
        <tr><th>Symbol</th><th style="color:#4fc3f7">Mid (App)</th><th>Bid</th><th>Ask</th><th>Spread</th><th>ATR</th><th>Candles</th><th>SMC</th></tr>
        {market_rows}
      </table>
    </div>

    <!-- Account -->
    <div class="card">
      <h2>💼 Account MT5</h2>
      {acc_html}
    </div>

    <!-- Positions -->
    <div class="card">
      <h2>📋 Open Positions ({len(mt5.get('positions',[]))})</h2>
      <table>
        <tr><th>Symbol</th><th>Type</th><th>Volume</th><th>Open</th><th>Current</th><th>P/L</th></tr>
        {pos_rows or "<tr><td colspan='6' style='color:#666;text-align:center'>Không có lệnh mở</td></tr>"}
      </table>
    </div>

    <!-- Hướng dẫn setup -->
    <div class="card" style="border:1px solid #333">
      <h2>📋 Cách kết nối đầy đủ</h2>
      <ol style="color:#ccc;font-size:13px;line-height:2.2">
        <li>Copy <code>MT5_ATTRAOS_Hub_v2.mq5</code> vào <code>MQL5/Experts/</code></li>
        <li>MT5 → Tools → Options → Expert Advisors → Allow WebRequest: <code style="color:#FFD700">http://127.0.0.1:8001</code></li>
        <li><b>Restart MT5 hoàn toàn</b> sau khi thêm URL whitelist</li>
        <li>MetaEditor (F4) → compile EA → kéo vào chart XAUUSD</li>
        <li>Trang này sẽ tự refresh, EA status chuyển sang 🟢 LIVE</li>
        <li>App iOS sẽ nhận giá từ hub trong 15 giây tiếp theo</li>
      </ol>
    </div>
    """

    return page("📡 MT5 Live Dashboard", body, token)
