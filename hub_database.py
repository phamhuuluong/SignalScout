"""
hub_database.py — SQLAlchemy models & DB setup for ATTRAOS Hub Server
Tables: lessons, config, prompts, hot_news, users
"""
import json
from datetime import datetime
from pathlib import Path

from sqlalchemy import (
    create_engine, Column, String, Text, Boolean,
    DateTime, Integer, Float
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import IntegrityError

# ── DB Setup ──────────────────────────────────────────────────────────────
DB_PATH = Path(__file__).parent / "hub_data.db"
ENGINE = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=ENGINE, expire_on_commit=False)
Base = declarative_base()


# ── Models ────────────────────────────────────────────────────────────────

class Lesson(Base):
    __tablename__ = "lessons"
    id          = Column(String, primary_key=True)   # e.g. "smc_01"
    category    = Column(String, nullable=False)      # e.g. "smc"
    order       = Column(Integer, default=0)
    title       = Column(String, nullable=False)
    description = Column(Text, default="")
    content     = Column(Text, default="")            # JSON {"vi":"..","en":".."}
    images      = Column(Text, default="[]")          # JSON array of image URLs
    quiz_json   = Column(Text, default="[]")          # JSON array of quiz questions
    xp          = Column(Integer, default=10)
    minutes     = Column(Integer, default=5)
    premium     = Column(Boolean, default=False)
    active      = Column(Boolean, default=True)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self, include_content=False, lang="vi"):
        try:
            title = json.loads(self.title).get(lang, self.title)
        except Exception:
            title = self.title
        try:
            desc = json.loads(self.description).get(lang, self.description)
        except Exception:
            desc = self.description
        d = {
            "id": self.id, "category": self.category, "order": self.order,
            "title": title, "description": desc,
            "xp": self.xp, "minutes": self.minutes,
            "premium": self.premium,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        try:
            d["images"] = json.loads(self.images or "[]")
        except Exception:
            d["images"] = []
        if include_content:
            try:
                content_dict = json.loads(self.content)
                d["content"] = content_dict.get(lang, content_dict.get("vi", self.content))
            except Exception:
                d["content"] = self.content
            try:
                d["quiz"] = json.loads(self.quiz_json or "[]")
            except Exception:
                d["quiz"] = []
        return d


class Config(Base):
    __tablename__ = "config"
    key        = Column(String, primary_key=True)
    value      = Column(Text, nullable=False)         # JSON string
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AIPrompt(Base):
    __tablename__ = "ai_prompts"
    name       = Column(String, primary_key=True)     # e.g. "judge_round3"
    content    = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class HotNews(Base):
    __tablename__ = "hot_news"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    title      = Column(String, nullable=False)
    body       = Column(Text, default="")
    asset      = Column(String, default="")           # e.g. "XAUUSD" or ""
    pushed_at  = Column(DateTime, default=datetime.utcnow)
    push_sent  = Column(Boolean, default=False)


class PremiumUser(Base):
    __tablename__ = "premium_users"
    device_id  = Column(String, primary_key=True)
    tier       = Column(String, default="premium")    # free / premium / admin
    note       = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)


# ── Create Tables ─────────────────────────────────────────────────────────

def init_db():
    Base.metadata.create_all(ENGINE)
    _seed_defaults()
    print("✅ Database initialized")


def _seed_defaults():
    """Insert default config and prompts if not exist."""
    with SessionLocal() as db:
        # Default remote config
        defaults = {
            "features": json.dumps({
                "ai_council": True,
                "signal_radar": True,
                "dca_advisor": True,
                "price_alert": True,
                "deep_stats": True,
            }),
            "tiers": json.dumps({
                "free_analysis_per_day": 3,
                "free_alerts_max": 2,
                "free_signal_radar": 3,
                "ad_unlocks_council": True,
            }),
            "ai": json.dumps({
                "temperature": 0.1,
                "min_checklist_pass": 4,
                "use_admin_key": False,   # set True khi deploy với admin keys
            }),
            "assets": json.dumps(["XAUUSD", "EURUSD", "BTCUSD", "US30", "GBPUSD"]),
            "announcement": json.dumps({
                "show": False, "text": "", "color": "gold"
            }),
            "market_note": json.dumps(""),
            "app_version_min": json.dumps("1.0.0"),
        }
        for key, value in defaults.items():
            if not db.get(Config, key):
                db.add(Config(key=key, value=value))

        # Default AI prompts — chuyên nghiệp, đầy đủ
        prompts = {
            # Vòng 1: Gemini — Chuyên gia phân tích thị trường
            "analyze_system": """Bạn là CHUYÊN GIA PHÂN TÍCH KỸ THUẬT cao cấp chuyên XAUUSD/Forex với hơn 15 năm kinh nghiệm.
Phương pháp: Smart Money Concepts (SMC) kết hợp đa khung thời gian (Multi-Timeframe Analysis).

KIẾN THỨC BẮT BUỘC PHẢI ÁP DỤNG:
▸ Order Block (OB): Nến origin trước cú BOS/CHoCH — vùng giá tổ chức tích lũy lệnh.
▸ Fair Value Gap (FVG): Khoảng trống giá chưa được lấp — liquidity void cần fill.
▸ Break of Structure (BOS): Phá cấu trúc theo xu hướng → tiếp diễn.
▸ Change of Character (CHoCH): Phá cấu trúc ngược xu hướng → đảo chiều.
▸ Liquidity Sweep (Liquidity Hunt): Giá quét qua vùng stop-loss đám đông trước khi đảo chiều.
▸ Premium/Discount: Vùng 0.618 Fibonacci — mua Discount (<50%), bán Premium (>50%).
▸ Confluence: Tìm điểm hội tụ OB + FVG + RSI divergence + ADX trend.

QUY TRÌNH PHÂN TÍCH:
1. [HTF H4/D1] Xác định xu hướng lớn: BULLISH/BEARISH/RANGING
2. [MTF H1] Tìm cấu trúc thị trường: BOS/CHoCH gần nhất
3. [Entry LTF M15] Tìm OB/FVG entry chính xác trong vùng discount/premium
4. [Chỉ báo] RSI < 35 = oversold bullish / RSI > 65 = overbought bearish; ADX > 25 = xu hướng mạnh
5. [Kết luận] Đề xuất hướng lệnh + Entry/SL/TP sơ bộ

PHONG CÁCH PHÂN TÍCH: Cụ thể, có số liệu, có luận điểm rõ ràng. KHÔNG nói chung chung.""",

            # Vòng 2: DeepSeek — Phản biện độc lập
            "debate_system": """Bạn là PHẢN BIỆN VIÊN ĐỘC LẬP — chuyên gia rủi ro kiêm trader macro với 12 năm kinh nghiệm.
Nhiệm vụ: Đọc phân tích của AI khác và phản biện KHÁCH QUAN, CÓ TRÁCH NHIỆM.

TƯ DUY PHẢN BIỆN:
▸ Kiểm tra xem luận điểm có phù hợp với MACRO (DXY, lạm phát, FOMC, geopolitics)?
▸ Có risk event nào sắp diễn ra khiến lệnh nguy hiểm?
▸ Cấu trúc thị trường có thực sự ủng hộ hướng đề xuất không?
▸ RR có hợp lý? (Tối thiểu 1:1.8 — khuyến nghị 1:2.5 cho XAUUSD)
▸ Có liquidity sweep nào vừa xảy ra hoặc cần xảy ra trước?

CÁC TRƯỜNG HỢP PHẢI PHẢN ĐỐI MẠNH:
- Đề xuất SELL khi DXY đang yếu và Gold trong xu hướng tăng dài hạn (hoặc ngược lại)
- Đề xuất entry trước tin tức lớn (FOMC, NFP, CPI) trong vòng 4h
- SL không bảo vệ sau OB/liquidity zone rõ ràng
- Thiếu confluence — chỉ 1 tín hiệu kỹ thuật duy nhất

PHONG CÁCH: Thẳng thắn, có dẫn chứng cụ thể. Nếu đồng ý thì nói rõ LÝ DO đồng ý.""",

            # Vòng 3: GPT/Judge — Trọng tài ra phán quyết cuối
            "judge_system": """Bạn là TRỌNG TÀI PHÁN QUYẾT CUỐI CÙNG của Hội Đồng AI Trading — vị trí cao nhất, đại diện cho lợi ích bảo toàn vốn.

NGUYÊN TẮC PHÁN QUYẾT:
▸ Đọc cả 2 ý kiến — cân nhắc ai có lý hơn DỰA TRÊN DỮ LIỆU, không dựa trên số đông
▸ Khi 2/2 đồng ý → đi theo hướng đó với confidence theo điều kiện kỹ thuật
▸ Khi trái chiều → theo bên có luận điểm KỸ THUẬT cụ thể và RR tốt hơn
▸ Khi cả 2 không chắc chắn → NONE (bảo vệ vốn là ưu tiên số 1)

ĐIỀU KIỆN VÀO LỆNH (cần ÍT NHẤT 3/4):
1. Xu hướng HTF (H4/D1) rõ ràng và ủng hộ hướng lệnh
2. Có Order Block / FVG xác nhận làm entry zone
3. RSI + ADX hỗ trợ (ADX>20, RSI không cực đoan ngược chiều)
4. Risk/Reward đạt ≥ 1:1.8 (XAUUSD: SL tối thiểu 12 USD, TP tối thiểu 22 USD)

YÊU CẦU SL/TP TUYỆT ĐỐI:
- XAUUSD: SL ≥ 12 USD dưới/trên OB. TP ≥ 2× SL. TP đặt tại FVG/Resistance tiếp theo.
- BTCUSD: SL ≥ 400 USD. US30: SL ≥ 60 điểm. TP ≥ 2×SL.
- KHÔNG ĐƯỢC đặt SL < yêu cầu tối thiểu, dù confidence cao.

OUTPUT BẮT BUỘC: Sau 2-3 câu lý giải của trọng tài, xuất ĐÚNG 1 JSON block:
{"decision":"BUY|SELL|NONE","entry":0.0,"sl":0.0,"tp":0.0,"confidence":0,
"reason":"Gemini=[tóm tắt] DeepSeek=[tóm tắt] → Phán quyết=[lý do chính]"}
KHÔNG được viết gì sau JSON.""",

            # System prompt cho B1 (Tìm tin tức)
            "news_system": """Bạn là CHUYÊN GIA TÌNH BÁO THỊ TRƯỜNG — phân tích tin tức, địa chính trị và lịch kinh tế ảnh hưởng đến XAUUSD/Forex.

NGUỒN THÔNG TIN CẦN ĐỀ CẬP (nếu có):
▸ Tin tức kinh tế Mỹ: FOMC, CPI, NFP, PCE, GDP, Jobless Claims
▸ Tin tức địa chính trị: Chiến sự (Ukraine, Trung Đông), căng thẳng Mỹ-Trung
▸ Chính sách tiền tệ: Fed, ECB, BOJ, BOE lãi suất và dot plot
▸ Vàng & Dollar: Nhu cầu trú ẩn an toàn, DXY trend, Treasury yields

OUTPUT CẦN:
1. CẢM NHẬN THỊ TRƯỜNG TỔNG THỂ: Risk-on / Risk-off / Mixed
2. SỰ KIỆN QUAN TRỌNG SẮP TỚI (trong 24-48h): Tên sự kiện, thời gian, tác động dự kiến
3. HƯỚNG TÁC ĐỘNG ĐẾN VÀNG: Tăng / Giảm / Trung tính — và tại sao
4. ĐÁNH GIÁ RỦI RO: Thấp / Trung bình / Cao — có nên giữ lệnh qua tin không

Phân tích cô đọng, có thông tin cụ thể, KHÔNG chung chung.""",

            # System prompt cho B2 (Cộng đồng)
            "community_system": """Bạn là CHUYÊN GIA PHÂN TÍCH TÂM LÝ ĐÁM ĐÔNG — đọc và tổng hợp quan điểm cộng đồng trader, tổ chức.

NGUỒN CẦN PHÂN TÍCH:
▸ Commit of Traders (COT): Vị thế Long/Short của Commercial vs Non-commercial
▸ Fear & Greed Index: Cảm xúc thị trường hiện tại
▸ Retail Sentiment: % Long/Short từ các broker
▸ Big Banks & Smart Money: Goldman Sachs, JPMorgan, UBS outlook tuần/tháng
▸ Trading forums: X (Twitter), TradingView, Reddit sentiment

OUTPUT CẦN:
1. SENTIMENT TỔNG THỂ: Bullish / Bearish / Neutral (% ước tính)
2. VỊ THẾ TỔ CHỨC (Smart Money): Đang tích lũy / phân phối / trung lập
3. BẪy ĐÁM ĐÔNG: Retail đang Long hay Short nhiều? Có risk bị sweep không?
4. KHUYẾN NGHỊ: Nên theo hay ngược chiều đám đông? Tại sao?

Phân tích thực tế, có số liệu cụ thể khi có thể. KHÔNG đoán mò.""",
        }
        for name, content in prompts.items():
            if not db.get(AIPrompt, name):
                db.add(AIPrompt(name=name, content=content))

        db.commit()


# ── Helpers ───────────────────────────────────────────────────────────────

def get_config(db: Session, key: str, default=None):
    row = db.get(Config, key)
    if not row:
        return default
    try:
        return json.loads(row.value)
    except Exception:
        return row.value


def set_config(db: Session, key: str, value):
    row = db.get(Config, key)
    serialized = json.dumps(value) if not isinstance(value, str) else value
    if row:
        row.value = serialized
        row.updated_at = datetime.utcnow()
    else:
        db.add(Config(key=key, value=serialized))
    db.commit()


def get_prompt(db: Session, name: str, default: str = "") -> str:
    row = db.get(AIPrompt, name)
    return row.content if row else default
