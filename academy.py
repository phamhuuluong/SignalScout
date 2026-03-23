"""
Signal Scout — Trading Academy Module
Lessons, Patterns, Quiz, Replay, Paper Trading, Progress, Gamification
"""
import json
import time
import random
from datetime import datetime
from typing import Optional


from academy_lessons import LESSONS_FULL
from academy_lessons2 import LESSONS_PART2
from academy_lessons3 import LESSONS_PART3, PATTERNS_FULL, QUIZZES_FULL


# ═══════════════════════════════════════════════════════
# 1. STRUCTURED LESSONS — Merged from 3 content files
# ═══════════════════════════════════════════════════════

LESSON_CATEGORIES = [
    {"id": "basics", "name": "Trading Basics", "icon": "📚", "order": 1},
    {"id": "candles", "name": "Candlestick Patterns", "icon": "🕯️", "order": 2},
    {"id": "structure", "name": "Market Structure", "icon": "🏗️", "order": 3},
    {"id": "sr", "name": "Support & Resistance", "icon": "📊", "order": 4},
    {"id": "trend", "name": "Trend Analysis", "icon": "📈", "order": 5},
    {"id": "risk", "name": "Risk Management", "icon": "🛡️", "order": 6},
    {"id": "smc", "name": "Smart Money Concepts", "icon": "🧠", "order": 7},
    {"id": "liquidity", "name": "Liquidity & Stop Hunts", "icon": "🎯", "order": 8},
    {"id": "bos", "name": "Break of Structure", "icon": "💥", "order": 9},
    {"id": "fvg", "name": "Fair Value Gaps", "icon": "📐", "order": 10},
]

# Merge all lessons from content files (27 total)
LESSONS = LESSONS_FULL + LESSONS_PART2 + LESSONS_PART3

# Full 12-pattern library
PATTERNS = PATTERNS_FULL

# Extended 25-question quiz bank
QUIZZES = QUIZZES_FULL


# ═══════════════════════════════════════════════════════
# 4. GAMIFICATION
# ═══════════════════════════════════════════════════════

LEVELS = [
    {"level": 1, "name": "Tân Binh", "title": "Beginner", "min_xp": 0, "icon": "🌱"},
    {"level": 2, "name": "Học Viên", "title": "Student", "min_xp": 50, "icon": "📖"},
    {"level": 3, "name": "Thực Tập", "title": "Apprentice", "min_xp": 150, "icon": "📊"},
    {"level": 4, "name": "Trader", "title": "Intermediate", "min_xp": 350, "icon": "📈"},
    {"level": 5, "name": "Pro Trader", "title": "Advanced", "min_xp": 600, "icon": "⭐"},
    {"level": 6, "name": "Chuyên Gia", "title": "Expert", "min_xp": 1000, "icon": "🏆"},
    {"level": 7, "name": "Master", "title": "Master", "min_xp": 2000, "icon": "👑"},
]

ACHIEVEMENTS = [
    {"id": "first_lesson", "name": "Bước Đầu Tiên", "desc": "Hoàn thành bài học đầu tiên", "xp": 10, "icon": "🎯"},
    {"id": "10_lessons", "name": "Chăm Chỉ", "desc": "Hoàn thành 10 bài học", "xp": 50, "icon": "📚"},
    {"id": "all_basics", "name": "Nền Tảng Vững", "desc": "Hoàn thành tất cả bài cơ bản", "xp": 30, "icon": "🏗️"},
    {"id": "quiz_master", "name": "Thông Thái", "desc": "Trả lời đúng 10 câu quiz", "xp": 30, "icon": "🧠"},
    {"id": "5_wins", "name": "Chiến Thắng", "desc": "Thắng 5 lệnh paper trading", "xp": 25, "icon": "🏅"},
    {"id": "streak_7", "name": "Kiên Trì", "desc": "Học 7 ngày liên tiếp", "xp": 50, "icon": "🔥"},
    {"id": "predict_10", "name": "Nhìn Xa", "desc": "Dự đoán đúng 10 chart replay", "xp": 40, "icon": "🔮"},
    {"id": "risk_aware", "name": "An Toàn", "desc": "Hoàn thành bài Risk Management", "xp": 20, "icon": "🛡️"},
    {"id": "smc_expert", "name": "Smart Money", "desc": "Hoàn thành tất cả bài SMC", "xp": 50, "icon": "💎"},
    {"id": "paper_pro", "name": "Trader Pro", "desc": "Win rate > 60% sau 20 lệnh", "xp": 100, "icon": "👑"},
]


# ═══════════════════════════════════════════════════════
# 5. PAPER TRADING ENGINE
# ═══════════════════════════════════════════════════════

class PaperTradingEngine:
    """Simulated trading with virtual balance"""

    def __init__(self, initial_balance: float = 10000.0):
        self.balance = initial_balance
        self.initial_balance = initial_balance
        self.positions: list[dict] = []
        self.history: list[dict] = []
        self.trade_count = 0

    def open_trade(self, symbol: str, trade_type: str, entry_price: float,
                   sl: float, tp: float, lot_size: float = 0.1) -> dict:
        """Open a paper trade"""
        risk = abs(entry_price - sl) * lot_size * 100
        if risk > self.balance * 0.02:
            return {"error": "Rủi ro > 2% vốn. Giảm lot size hoặc thu hẹp SL."}

        self.trade_count += 1
        trade = {
            "id": f"PT{self.trade_count:04d}",
            "symbol": symbol,
            "type": trade_type.upper(),
            "entry_price": entry_price,
            "stop_loss": sl,
            "take_profit": tp,
            "lot_size": lot_size,
            "status": "OPEN",
            "opened_at": datetime.now().isoformat(),
            "pnl": 0.0,
        }
        self.positions.append(trade)
        return trade

    def close_trade(self, trade_id: str, close_price: float) -> dict:
        """Close a paper trade"""
        trade = next((t for t in self.positions if t["id"] == trade_id), None)
        if not trade:
            return {"error": "Trade not found"}

        if trade["type"] == "BUY":
            pnl = (close_price - trade["entry_price"]) * trade["lot_size"] * 100
        else:
            pnl = (trade["entry_price"] - close_price) * trade["lot_size"] * 100

        trade["status"] = "CLOSED"
        trade["close_price"] = close_price
        trade["pnl"] = round(pnl, 2)
        trade["closed_at"] = datetime.now().isoformat()
        trade["result"] = "WIN" if pnl > 0 else "LOSS"

        self.balance += pnl
        self.positions.remove(trade)
        self.history.append(trade)
        return trade

    def check_positions(self, current_prices: dict):
        """Check if any positions hit SL or TP"""
        triggered = []
        for trade in list(self.positions):
            price = current_prices.get(trade["symbol"])
            if not price:
                continue

            hit = False
            if trade["type"] == "BUY":
                if price <= trade["stop_loss"]:
                    hit = True
                elif price >= trade["take_profit"]:
                    hit = True
            else:
                if price >= trade["stop_loss"]:
                    hit = True
                elif price <= trade["take_profit"]:
                    hit = True

            if hit:
                result = self.close_trade(trade["id"], price)
                triggered.append(result)
        return triggered

    def get_stats(self) -> dict:
        """Get paper trading statistics"""
        if not self.history:
            return {
                "balance": self.balance,
                "initial_balance": self.initial_balance,
                "total_pnl": 0, "trades": 0, "wins": 0, "losses": 0,
                "win_rate": 0, "avg_win": 0, "avg_loss": 0, "open_positions": len(self.positions),
            }

        wins = [t for t in self.history if t["result"] == "WIN"]
        losses = [t for t in self.history if t["result"] == "LOSS"]
        return {
            "balance": round(self.balance, 2),
            "initial_balance": self.initial_balance,
            "total_pnl": round(self.balance - self.initial_balance, 2),
            "trades": len(self.history),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": round(len(wins) / len(self.history) * 100, 1) if self.history else 0,
            "avg_win": round(sum(t["pnl"] for t in wins) / len(wins), 2) if wins else 0,
            "avg_loss": round(sum(t["pnl"] for t in losses) / len(losses), 2) if losses else 0,
            "open_positions": len(self.positions),
            "best_trade": max(t["pnl"] for t in self.history) if self.history else 0,
            "worst_trade": min(t["pnl"] for t in self.history) if self.history else 0,
        }


# ═══════════════════════════════════════════════════════
# 6. USER PROGRESS
# ═══════════════════════════════════════════════════════

class UserProgress:
    """Track user learning progress"""

    def __init__(self):
        self.xp = 0
        self.lessons_completed: list[str] = []
        self.quiz_answers: list[dict] = []
        self.replay_predictions: list[dict] = []
        self.achievements_unlocked: list[str] = []
        self.streak_days = 0
        self.last_activity: Optional[str] = None
        self.paper_engine = PaperTradingEngine()

    def complete_lesson(self, lesson_id: str) -> dict:
        if lesson_id in self.lessons_completed:
            return {"status": "already_completed"}
        lesson = next((l for l in LESSONS if l["id"] == lesson_id), None)
        if not lesson:
            return {"error": "Lesson not found"}

        self.lessons_completed.append(lesson_id)
        xp_earned = lesson.get("xp", 10)
        self.xp += xp_earned
        self._update_streak()

        new_achievements = self._check_achievements()
        return {
            "status": "completed",
            "xp_earned": xp_earned,
            "total_xp": self.xp,
            "level": self.get_level(),
            "new_achievements": new_achievements,
        }

    def answer_quiz(self, quiz_id: str, answer: int) -> dict:
        quiz = next((q for q in QUIZZES if q["id"] == quiz_id), None)
        if not quiz:
            return {"error": "Quiz not found"}

        correct = answer == quiz["correct"]
        xp = quiz["xp"] if correct else 0
        self.xp += xp
        self.quiz_answers.append({"quiz_id": quiz_id, "answer": answer, "correct": correct})
        self._update_streak()

        return {
            "correct": correct,
            "correct_answer": quiz["correct"],
            "explanation": quiz["explanation"],
            "xp_earned": xp,
            "total_xp": self.xp,
        }

    def record_prediction(self, symbol: str, prediction: str, actual: str) -> dict:
        correct = prediction.upper() == actual.upper()
        xp = 5 if correct else 0
        self.xp += xp
        self.replay_predictions.append({
            "symbol": symbol, "prediction": prediction, "actual": actual, "correct": correct
        })
        return {"correct": correct, "xp_earned": xp}

    def get_level(self) -> dict:
        current = LEVELS[0]
        for lv in LEVELS:
            if self.xp >= lv["min_xp"]:
                current = lv
        next_lv = next((l for l in LEVELS if l["min_xp"] > self.xp), None)
        return {
            **current,
            "xp": self.xp,
            "next_level_xp": next_lv["min_xp"] if next_lv else current["min_xp"],
            "progress": min(100, round((self.xp - current["min_xp"]) / max(
                (next_lv["min_xp"] if next_lv else current["min_xp"] + 1) - current["min_xp"], 1) * 100)),
        }

    def get_stats(self) -> dict:
        correct_quizzes = sum(1 for q in self.quiz_answers if q["correct"])
        correct_predictions = sum(1 for p in self.replay_predictions if p["correct"])
        return {
            "level": self.get_level(),
            "lessons_completed": len(self.lessons_completed),
            "total_lessons": len(LESSONS),
            "quiz_total": len(self.quiz_answers),
            "quiz_correct": correct_quizzes,
            "quiz_accuracy": round(correct_quizzes / max(len(self.quiz_answers), 1) * 100, 1),
            "predictions_total": len(self.replay_predictions),
            "predictions_correct": correct_predictions,
            "prediction_accuracy": round(correct_predictions / max(len(self.replay_predictions), 1) * 100, 1),
            "paper_trading": self.paper_engine.get_stats(),
            "achievements": self.achievements_unlocked,
            "streak_days": self.streak_days,
        }

    def _update_streak(self):
        today = datetime.now().strftime("%Y-%m-%d")
        if self.last_activity != today:
            self.last_activity = today
            self.streak_days += 1

    def _check_achievements(self) -> list[dict]:
        new = []
        checks = [
            ("first_lesson", len(self.lessons_completed) >= 1),
            ("10_lessons", len(self.lessons_completed) >= 10),
            ("quiz_master", sum(1 for q in self.quiz_answers if q["correct"]) >= 10),
            ("streak_7", self.streak_days >= 7),
            ("predict_10", sum(1 for p in self.replay_predictions if p["correct"]) >= 10),
            ("5_wins", self.paper_engine.get_stats()["wins"] >= 5),
        ]
        for ach_id, condition in checks:
            if condition and ach_id not in self.achievements_unlocked:
                ach = next((a for a in ACHIEVEMENTS if a["id"] == ach_id), None)
                if ach:
                    self.achievements_unlocked.append(ach_id)
                    self.xp += ach["xp"]
                    new.append(ach)
        return new
