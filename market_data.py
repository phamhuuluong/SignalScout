"""
Signal Scout Backend — Market Data Pipeline
Fetches OHLCV data from TwelveData, Binance, Finnhub, Yahoo Finance
"""
import httpx
import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


# ─── Unified Candle Model ─────────────────────────────
class Candle:
    __slots__ = ("timestamp", "open", "high", "low", "close", "volume", "symbol", "timeframe")

    def __init__(self, timestamp: float, o: float, h: float, l: float, c: float, v: float = 0,
                 symbol: str = "", timeframe: str = ""):
        self.timestamp = timestamp
        self.open = o
        self.high = h
        self.low = l
        self.close = c
        self.volume = v
        self.symbol = symbol
        self.timeframe = timeframe

    def to_dict(self):
        return {
            "t": self.timestamp, "o": self.open, "h": self.high,
            "l": self.low, "c": self.close, "v": self.volume,
            "symbol": self.symbol, "tf": self.timeframe,
        }


# ─── TwelveData (Forex + Gold) ─────────────────────────
class TwelveDataFetcher:
    BASE = "https://api.twelvedata.com"

    def __init__(self):
        self.api_key = os.getenv("TWELVEDATA_API_KEY", "")

    async def fetch_candles(self, symbol: str, interval: str = "15min", limit: int = 100) -> list[Candle]:
        if not self.api_key:
            return []
        url = f"{self.BASE}/time_series"
        params = {"symbol": symbol, "interval": interval, "outputsize": limit, "apikey": self.api_key}
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url, params=params)
            data = r.json()
        if "values" not in data:
            return []
        candles = []
        for v in reversed(data["values"]):
            ts = datetime.strptime(v["datetime"], "%Y-%m-%d %H:%M:%S").timestamp()
            candles.append(Candle(ts, float(v["open"]), float(v["high"]), float(v["low"]),
                                  float(v["close"]), float(v.get("volume", 0)), symbol, interval))
        return candles

    async def fetch_price(self, symbol: str) -> Optional[float]:
        if not self.api_key:
            return None
        url = f"{self.BASE}/price"
        params = {"symbol": symbol, "apikey": self.api_key}
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url, params=params)
            data = r.json()
        return float(data.get("price", 0)) if "price" in data else None


# ─── Binance (Crypto) ──────────────────────────────────
class BinanceFetcher:
    BASE = "https://api.binance.com/api/v3"
    TF_MAP = {"1m": "1m", "5m": "5m", "15m": "15m", "1h": "1h", "4h": "4h", "1d": "1d"}

    async def fetch_candles(self, symbol: str = "BTCUSDT", interval: str = "15m", limit: int = 100) -> list[Candle]:
        url = f"{self.BASE}/klines"
        params = {"symbol": symbol, "interval": self.TF_MAP.get(interval, interval), "limit": limit}
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url, params=params)
            data = r.json()
        candles = []
        for k in data:
            candles.append(Candle(k[0] / 1000, float(k[1]), float(k[2]), float(k[3]),
                                  float(k[4]), float(k[5]), symbol, interval))
        return candles

    async def fetch_price(self, symbol: str = "BTCUSDT") -> Optional[float]:
        url = f"{self.BASE}/ticker/price"
        params = {"symbol": symbol}
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url, params=params)
            data = r.json()
        return float(data.get("price", 0)) if "price" in data else None


# ─── Finnhub (Fallback) ───────────────────────────────
class FinnhubFetcher:
    BASE = "https://finnhub.io/api/v1"

    def __init__(self):
        self.api_key = os.getenv("FINNHUB_API_KEY", "")

    async def fetch_candles(self, symbol: str, resolution: str = "15", limit: int = 100) -> list[Candle]:
        if not self.api_key:
            return []
        now = int(datetime.now().timestamp())
        ago = now - limit * 900  # ~15min candles
        url = f"{self.BASE}/stock/candle"
        params = {"symbol": symbol, "resolution": resolution, "from": ago, "to": now, "token": self.api_key}
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url, params=params)
            data = r.json()
        if data.get("s") != "ok":
            return []
        candles = []
        for i in range(len(data["t"])):
            candles.append(Candle(data["t"][i], data["o"][i], data["h"][i], data["l"][i],
                                  data["c"][i], data["v"][i], symbol, f"{resolution}m"))
        return candles


# ─── Yahoo Finance (Free Backup) ──────────────────────
class YahooFetcher:
    SYMBOL_MAP = {
        "XAU/USD": "GC=F", "XAUUSD": "GC=F",
        "XAG/USD": "SI=F", "XAGUSD": "SI=F",
        "EUR/USD": "EURUSD=X", "EURUSD": "EURUSD=X",
        "GBP/USD": "GBPUSD=X", "GBPUSD": "GBPUSD=X",
        "USD/JPY": "JPY=X", "USDJPY": "JPY=X",
        "DXY": "DX-Y.NYB",
        "BTCUSD": "BTC-USD", "BTC/USD": "BTC-USD",
        "ETHUSDT": "ETH-USD", "ETH/USD": "ETH-USD",
    }
    TF_MAP = {"1m": ("1m", "1d"), "5m": ("5m", "5d"), "15m": ("15m", "5d"),
              "1h": ("1h", "30d"), "4h": ("1h", "60d"), "1d": ("1d", "365d")}

    async def fetch_candles(self, symbol: str, interval: str = "15m", limit: int = 100) -> list[Candle]:
        yf_sym = self.SYMBOL_MAP.get(symbol, symbol)
        tf_info = self.TF_MAP.get(interval, ("15m", "5d"))
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yf_sym}"
        params = {"interval": tf_info[0], "range": tf_info[1], "includePrePost": "false"}
        headers = {"User-Agent": "Mozilla/5.0"}
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url, params=params, headers=headers)
            data = r.json()
        result = data.get("chart", {}).get("result", [])
        if not result:
            return []
        meta = result[0]
        timestamps = meta.get("timestamp", [])
        quote = meta.get("indicators", {}).get("quote", [{}])[0]
        opens = quote.get("open", [])
        highs = quote.get("high", [])
        lows = quote.get("low", [])
        closes = quote.get("close", [])
        volumes = quote.get("volume", [])
        candles = []
        for i in range(len(timestamps)):
            if opens[i] is None:
                continue
            candles.append(Candle(timestamps[i], opens[i], highs[i], lows[i],
                                  closes[i], volumes[i] or 0, symbol, interval))
        return candles[-limit:]


# ─── Unified Market Data Service ──────────────────────
class MarketDataService:
    def __init__(self):
        self.twelvedata = TwelveDataFetcher()
        self.binance = BinanceFetcher()
        self.finnhub = FinnhubFetcher()
        self.yahoo = YahooFetcher()

    def _is_crypto(self, symbol: str) -> bool:
        return symbol.upper() in ("BTCUSDT", "ETHUSDT", "SOLUSDT", "BTC/USD", "ETH/USD", "BTCUSD")

    async def fetch_candles(self, symbol: str, interval: str = "15m", limit: int = 100) -> list[Candle]:
        """Fetch candles with automatic fallback chain"""
        # Crypto → Binance
        if self._is_crypto(symbol):
            try:
                candles = await self.binance.fetch_candles(symbol, interval, limit)
                if candles:
                    return candles
            except Exception:
                pass

        # Forex/Gold → TwelveData
        td_interval = {"1m": "1min", "5m": "5min", "15m": "15min", "1h": "1h", "4h": "4h", "1d": "1day"}.get(interval, interval)
        try:
            candles = await self.twelvedata.fetch_candles(symbol, td_interval, limit)
            if candles:
                return candles
        except Exception:
            pass

        # Fallback → Yahoo Finance (free)
        try:
            candles = await self.yahoo.fetch_candles(symbol, interval, limit)
            if candles:
                return candles
        except Exception:
            pass

        return []

    async def fetch_multi_tf(self, symbol: str) -> dict[str, list[Candle]]:
        """Fetch M15, H1, H4 for full analysis"""
        results = await asyncio.gather(
            self.fetch_candles(symbol, "15m", 100),
            self.fetch_candles(symbol, "1h", 100),
            self.fetch_candles(symbol, "4h", 50),
            return_exceptions=True
        )
        return {
            "M15": results[0] if isinstance(results[0], list) else [],
            "H1": results[1] if isinstance(results[1], list) else [],
            "H4": results[2] if isinstance(results[2], list) else [],
        }
