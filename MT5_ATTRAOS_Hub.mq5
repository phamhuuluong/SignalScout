//+------------------------------------------------------------------+
//|                     MT5_ATTRAOS_Hub_v2.mq5                       |
//|       Expert Advisor v2 — Full OHLCV + SMC data cho Hub         |
//|   STABLE: không Sleep() trong timer, cache symbol map           |
//+------------------------------------------------------------------+
#property copyright "ATTRAOS Hub v2"
#property link      "http://127.0.0.1:8001"
#property version   "2.10"
#property strict

//--- Input parameters
input string HubURL        = "http://127.0.0.1:8001";
input string HubToken      = "attraos_admin_2026";
input int    SendInterval  = 15;
input string Symbols       = "XAUUSD,EURUSD,GBPUSD,USDJPY,BTCUSD";
input int    CandleCount   = 30;
input bool   SendCandles   = true;
input bool   SendAccount   = true;
input bool   SendOrders    = true;
input bool   Verbose       = false;

//--- Internal
datetime g_lastSend  = 0;
int      g_totalSent = 0;
int      g_errors    = 0;

// Symbol cache: input name → real broker name (resolved at init)
// Giải quyết 1 lần duy nhất tại OnInit, không scan mỗi timer tick
string g_baseSymbols[];   // XAUUSD, EURUSD, ...
string g_realSymbols[];   // XAUUSDc, EURUSDc, ...
int    g_symCount = 0;

//+------------------------------------------------------------------+
//| Tìm symbol thật (chỉ gọi 1 lần tại OnInit)                     |
//+------------------------------------------------------------------+
string ResolveSymbolOnce(string base) {
    string prefix = StringSubstr(base, 0, 6);

    // 1. Thử exact match
    if (SymbolInfoDouble(base, SYMBOL_BID) > 0 || SymbolInfoDouble(base, SYMBOL_ASK) > 0)
        return base;

    // 2. Scan MarketWatch (nhanh, ít symbols)
    int mw = SymbolsTotal(true);
    for (int i = 0; i < mw; i++) {
        string s = SymbolName(i, true);
        if (StringSubstr(s, 0, 6) == prefix) {
            Print("[ATTRAOS] Map: ", base, " → ", s, " (MarketWatch)");
            return s;
        }
    }

    // 3. Scan toàn bộ symbols (chậm hơn nhưng chỉ làm 1 lần)
    int all = SymbolsTotal(false);
    for (int i = 0; i < all; i++) {
        string s = SymbolName(i, false);
        if (StringSubstr(s, 0, 6) == prefix) {
            SymbolSelect(s, true);  // Add vào MarketWatch
            Print("[ATTRAOS] Map: ", base, " → ", s, " (added to MW)");
            return s;
        }
    }

    Print("[ATTRAOS] ⚠️ Không tìm thấy symbol: ", base);
    return "";
}

//+------------------------------------------------------------------+
int OnInit() {
    // Build symbol cache — làm 1 lần, không lặp mỗi timer
    string arr[];
    g_symCount = StringSplit(Symbols, ',', arr);
    ArrayResize(g_baseSymbols, g_symCount);
    ArrayResize(g_realSymbols, g_symCount);

    int valid = 0;
    for (int i = 0; i < g_symCount; i++) {
        string b = arr[i];
        StringTrimLeft(b); StringTrimRight(b);
        string r = ResolveSymbolOnce(b);
        if (r != "") {
            g_baseSymbols[valid] = StringSubstr(b, 0, 6);  // standard 6-char
            g_realSymbols[valid] = r;
            valid++;
        }
    }
    g_symCount = valid;

    EventSetTimer(SendInterval);
    Print("[ATTRAOS v2.10] ✅ Khởi động | Hub: ", HubURL,
          " | Symbols: ", g_symCount, " | Interval: ", SendInterval, "s");
    for (int i = 0; i < g_symCount; i++)
        Print("[ATTRAOS] ", g_baseSymbols[i], " → ", g_realSymbols[i]);

    SendAllData();
    return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) {
    EventKillTimer();
    Print("[ATTRAOS v2.10] Dừng | Sent=", g_totalSent, " Errors=", g_errors);
}

// KHÔNG Sleep() trong các hàm này!
void OnTimer() { SendAllData(); }
void OnTick() {
    if (TimeCurrent() - g_lastSend < SendInterval) return;
    SendAllData();
}
void OnTradeTransaction(const MqlTradeTransaction &t, const MqlTradeRequest &r, const MqlTradeResult &res) {
    if (t.type == TRADE_TRANSACTION_DEAL_ADD || t.type == TRADE_TRANSACTION_ORDER_ADD)
        SendAllData();
}

//+------------------------------------------------------------------+
//| JSON escape                                                       |
//+------------------------------------------------------------------+
string JsonEscape(string s) {
    StringReplace(s, "\\", "\\\\");
    StringReplace(s, "\"", "\\\"");
    return s;
}

//+------------------------------------------------------------------+
//| Build candle array JSON                                          |
//+------------------------------------------------------------------+
string BuildCandlesJSON(string realSym, ENUM_TIMEFRAMES tf, int count) {
    MqlRates rates[];
    int copied = CopyRates(realSym, tf, 0, count, rates);
    if (copied < 5) return "[]";
    ArraySetAsSeries(rates, true);

    string out = "[";
    for (int i = copied - 1; i >= 0; i--) {
        if (i < copied - 1) out += ",";
        out += StringFormat(
            "{\"t\":%I64d,\"o\":%.5f,\"h\":%.5f,\"l\":%.5f,\"c\":%.5f,\"v\":%.0f}",
            (long)rates[i].time,
            rates[i].open, rates[i].high, rates[i].low, rates[i].close,
            (double)rates[i].tick_volume
        );
    }
    return out + "]";
}

//+------------------------------------------------------------------+
//| Main send — KHÔNG được gọi Sleep() ở đây                       |
//+------------------------------------------------------------------+
void SendAllData() {
    g_lastSend = TimeCurrent();

    // ── 1. Market data (dùng cache, không scan symbols) ─────────────
    string marketJSON = "[";
    bool firstSym = true;
    for (int i = 0; i < g_symCount; i++) {
        string baseSym = g_baseSymbols[i];
        string realSym = g_realSymbols[i];

        double bid = SymbolInfoDouble(realSym, SYMBOL_BID);
        double ask = SymbolInfoDouble(realSym, SYMBOL_ASK);
        if (bid <= 0 && ask <= 0) continue;

        double pt = SymbolInfoDouble(realSym, SYMBOL_POINT);
        double spread = (pt > 0) ? (ask - bid) / pt : 0;

        // ATR14 H1
        double atr = 0;
        MqlRates atrR[];
        if (CopyRates(realSym, PERIOD_H1, 0, 15, atrR) == 15) {
            double sum = 0;
            for (int j = 0; j < 14; j++) sum += (atrR[j].high - atrR[j].low);
            atr = sum / 14.0;
        }

        // Candles (nếu enabled)
        string c_m15 = "[]", c_h1 = "[]", c_h4 = "[]";
        if (SendCandles) {
            c_m15 = BuildCandlesJSON(realSym, PERIOD_M15, CandleCount);
            c_h1  = BuildCandlesJSON(realSym, PERIOD_H1,  CandleCount);
            c_h4  = BuildCandlesJSON(realSym, PERIOD_H4,  MathMin(CandleCount, 25));
        }

        if (!firstSym) marketJSON += ",";
        firstSym = false;
        // Gửi tên chuẩn 6 ký tự, không phải tên broker
        marketJSON += StringFormat(
            "{\"symbol\":\"%s\",\"bid\":%.5f,\"ask\":%.5f,\"spread\":%.1f,\"atr\":%.5f,"
            "\"m15\":%s,\"h1\":%s,\"h4\":%s}",
            baseSym, bid, ask, spread, atr, c_m15, c_h1, c_h4
        );
        if (Verbose) Print("[ATTRAOS] ", baseSym, "(", realSym, "): bid=", DoubleToString(bid, 5));
    }
    marketJSON += "]";

    // ── 2. Account ───────────────────────────────────────────────────
    string accountJSON = "{}";
    if (SendAccount) {
        accountJSON = StringFormat(
            "{\"login\":%d,\"name\":\"%s\",\"server\":\"%s\","
            "\"balance\":%.2f,\"equity\":%.2f,\"margin\":%.2f,"
            "\"free_margin\":%.2f,\"profit\":%.2f,\"leverage\":%d,\"currency\":\"%s\"}",
            AccountInfoInteger(ACCOUNT_LOGIN),
            JsonEscape(AccountInfoString(ACCOUNT_NAME)),
            JsonEscape(AccountInfoString(ACCOUNT_SERVER)),
            AccountInfoDouble(ACCOUNT_BALANCE),
            AccountInfoDouble(ACCOUNT_EQUITY),
            AccountInfoDouble(ACCOUNT_MARGIN),
            AccountInfoDouble(ACCOUNT_FREEMARGIN),
            AccountInfoDouble(ACCOUNT_PROFIT),
            (int)AccountInfoInteger(ACCOUNT_LEVERAGE),
            AccountInfoString(ACCOUNT_CURRENCY)
        );
    }

    // ── 3. Positions ─────────────────────────────────────────────────
    string ordersJSON = "[]";
    int total = PositionsTotal();
    if (SendOrders && total > 0) {
        ordersJSON = "[";
        bool first = true;
        for (int i = 0; i < total; i++) {
            if (!PositionSelectByTicket(PositionGetTicket(i))) continue;
            if (!first) ordersJSON += ",";
            first = false;
            ordersJSON += StringFormat(
                "{\"ticket\":%I64d,\"symbol\":\"%s\",\"type\":\"%s\","
                "\"volume\":%.2f,\"open_price\":%.5f,\"current_price\":%.5f,"
                "\"sl\":%.5f,\"tp\":%.5f,\"profit\":%.2f,\"swap\":%.2f}",
                (long)PositionGetTicket(i),
                StringSubstr(PositionGetString(POSITION_SYMBOL), 0, 6),
                (int)PositionGetInteger(POSITION_TYPE) == 0 ? "BUY" : "SELL",
                PositionGetDouble(POSITION_VOLUME),
                PositionGetDouble(POSITION_PRICE_OPEN),
                PositionGetDouble(POSITION_PRICE_CURRENT),
                PositionGetDouble(POSITION_SL),
                PositionGetDouble(POSITION_TP),
                PositionGetDouble(POSITION_PROFIT),
                PositionGetDouble(POSITION_SWAP)
            );
        }
        ordersJSON += "]";
    }

    // ── 4. Full payload ──────────────────────────────────────────────
    string payload = StringFormat(
        "{\"market\":%s,\"account\":%s,\"positions\":%s,"
        "\"ea_version\":\"2.10\",\"broker_time\":\"%s\",\"timestamp\":%I64d}",
        marketJSON, accountJSON, ordersJSON,
        TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS),
        (long)TimeCurrent()
    );

    // ── 5. HTTP POST (StringGetCharacter — tránh truncation) ─────────
    string url     = HubURL + "/mt5/data";
    string headers = "Content-Type: application/json\r\n";
    if (HubToken != "") headers += "X-Admin-Token: " + HubToken + "\r\n";

    int payLen = StringLen(payload);
    char postData[], result[];
    string resultHeaders;
    ArrayResize(postData, payLen);
    for (int ki = 0; ki < payLen; ki++)
        postData[ki] = (char)StringGetCharacter(payload, ki);

    int code = WebRequest("POST", url, headers, 8000, postData, result, resultHeaders);

    if (code == 200 || code == 201) {
        g_totalSent++;
        if (Verbose) Print("[ATTRAOS] ✅ Sent #", g_totalSent, " | ", payLen, " bytes");
    } else {
        g_errors++;
        Print("[ATTRAOS] ❌ HTTP ", code, " | errors=", g_errors);
        if (code == 1003) {
            Print("[ATTRAOS] → Tools > Options > Expert Advisors > Allow WebRequest: ", HubURL);
            Print("[ATTRAOS] → Sau đó RESTART MT5 hoàn toàn");
        }
    }
}
