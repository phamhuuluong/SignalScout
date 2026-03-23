"""
Signal Scout — Push Notification Service
Firebase Cloud Messaging + Apple Push Notification Service
"""
import os
import json
import httpx
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Optional Firebase import
try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    HAS_FIREBASE = True
except ImportError:
    HAS_FIREBASE = False


class PushService:
    def __init__(self):
        self.initialized = False
        self._init_firebase()

    def _init_firebase(self):
        if not HAS_FIREBASE:
            return
        cred_path = os.getenv("FIREBASE_CREDENTIALS", "")
        if cred_path and os.path.exists(cred_path):
            try:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                self.initialized = True
                print("✅ Firebase initialized")
            except Exception as e:
                print(f"⚠️ Firebase init failed: {e}")

    async def send_signal_alert(self, token: str, signal: dict) -> bool:
        """Send push notification for a trading signal"""
        if not self.initialized:
            print(f"📱 [MOCK PUSH] {signal.get('symbol', '?')}: {signal.get('decision', 'NONE')} "
                  f"Conf={signal.get('confidence', 0)}%")
            return False

        try:
            decision = signal.get("decision", "NONE")
            symbol = signal.get("symbol", "Unknown")
            confidence = signal.get("confidence", 0)
            entry = signal.get("entry", 0)

            emoji = "🟢" if decision == "BUY" else "🔴" if decision == "SELL" else "⚪"

            message = messaging.Message(
                notification=messaging.Notification(
                    title=f"{emoji} {decision} Signal: {symbol}",
                    body=f"Confidence {confidence}% — Entry: {entry}",
                ),
                data={
                    "type": "signal",
                    "symbol": symbol,
                    "decision": decision,
                    "confidence": str(confidence),
                    "entry": str(entry),
                    "sl": str(signal.get("sl", 0)),
                    "tp": str(signal.get("tp", 0)),
                },
                token=token,
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(sound="default", badge=1)
                    )
                )
            )
            response = messaging.send(message)
            print(f"✅ Push sent: {response}")
            return True
        except Exception as e:
            print(f"❌ Push failed: {e}")
            return False

    async def send_sweep_alert(self, token: str, sweep: dict) -> bool:
        """Alert for liquidity sweep events"""
        if not self.initialized:
            print(f"📱 [MOCK PUSH] Sweep: {sweep.get('type', '')} at {sweep.get('level', 0)}")
            return False

        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=f"🎯 Liquidity Sweep Detected",
                    body=f"{sweep.get('type', '')} at {sweep.get('level', 0)} — Bias: {sweep.get('bias', 'N/A')}",
                ),
                data={"type": "sweep", **{k: str(v) for k, v in sweep.items()}},
                token=token,
            )
            messaging.send(message)
            return True
        except Exception:
            return False

    async def broadcast_signal(self, tokens: list[str], signal: dict):
        """Send signal to all registered devices"""
        for token in tokens:
            await self.send_signal_alert(token, signal)
