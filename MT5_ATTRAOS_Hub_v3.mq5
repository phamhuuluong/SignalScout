//+------------------------------------------------------------------+
//|                   MT5_ATTRAOS_Hub_v3.mq5                         |
//|     Expert Advisor v3 — Bookmap DOM + Order Flow Simulator       |
//|     NEW: L2 DOM push, Volume simulation, Delta tracker           |
//+------------------------------------------------------------------+
#property copyright "ATTRAOS Hub v3"
#property link      "https://hub.lomofx.com"
#property version   "3.00"
#property strict

//--- Input parameters
input string HubURL        = "http://127.0.0.1:8001";
input string HubToken      = "attraos_admin_2026";
input int    SendInterval  = 15;       // Giây giữa 2 lần gửi Market Data
input int    DOMInterval   = 5;        // Giây giữa 2 lần gửi DOM / Bookmap Data
input string Symbols       = "XAUUSD,EURUSD,GBPUSD,USDJPY,BTCUSD";
input int    CandleCount   = 100;
input int    DOMDepth      = 10;       // Số level DOM mỗi phía (Bid/Ask)
input bool   SendCandles   = true;
input bool   SendAccount   = true;
input bool   SendOrders    = true;
input bool   SendDOM       = true;     // Bật/tắt gửi DOM data cho Bookmap
input bool   SimulateDOM   = true;     // Dùng DOM Simulator nếu broker không cấp DOM thật
input bool   Verbose       = false;

//--- Internal state
datetime g_lastSend    = 0;
datetime g_lastDOMSend = 0;
int      g_totalSent   = 0;
int      g_errors      = 0;

string g_baseSymbols[];
string g_realSymbols[];
int    g_symCount = 0;

// CVD (Cumulative Volume Delta) tracker per symbol
double g_cvd[];          // CVD tích lũy
double g_buyVol[];       // Tổng buy volume trong phiên
double g_sellVol[];      // Tổng sell volume trong phiên
double g_lastPrice[];    // Giá tick trước để xác định hướng trade
long   g_tickCount[];    // Số tick đã xử lý

//+------------------------------------------------------------------+
//| Tìm symbol thật (chỉ gọi 1 lần tại OnInit)                      |
//+------------------------------------------------------------------+
string ResolveSymbolOnce(string base) {
    string prefix = StringSubstr(base, 0, 6);
    if (SymbolInfoDouble(base, SYMBOL_BID) > 0 || SymbolInfoDouble(base, SYMBOL_ASK) > 0)
        return base;
    int mw = SymbolsTotal(true);
    for (int i = 0; i < mw; i++) {
        string s = SymbolName(i, true);
        if (StringSubstr(s, 0, 6) == prefix) { Print("[v3] Map: ", base, " → ", s); return s; }
    }
    int all = SymbolsTotal(false);
    for (int i = 0; i < all; i++) {
        string s = SymbolName(i, false);
        if (StringSubstr(s, 0, 6) == prefix) { SymbolSelect(s, true); return s; }
    }
    return "";
}

//+------------------------------------------------------------------+
int OnInit() {
    string arr[];
    g_symCount = StringSplit(Symbols, ',', arr);
    ArrayResize(g_baseSymbols, g_symCount);
    ArrayResize(g_realSymbols, g_symCount);
    ArrayResize(g_cvd,        g_symCount);
    ArrayResize(g_buyVol,     g_symCount);
    ArrayResize(g_sellVol,    g_symCount);
    ArrayResize(g_lastPrice,  g_symCount);
    ArrayResize(g_tickCount,  g_symCount);
    ArrayInitialize(g_cvd,       0);
    ArrayInitialize(g_buyVol,    0);
    ArrayInitialize(g_sellVol,   0);
    ArrayInitialize(g_lastPrice, 0);
    ArrayInitialize(g_tickCount, 0);

    int valid = 0;
    for (int i = 0; i < g_symCount; i++) {
        string b = arr[i]; StringTrimLeft(b); StringTrimRight(b);
        string r = ResolveSymbolOnce(b);
        if (r != "") {
            g_baseSymbols[valid] = StringSubstr(b, 0, 6);
            g_realSymbols[valid] = r;
            valid++;
        }
    }
    g_symCount = valid;

    Print("[ATTRAOS v3.00] OK | Hub: ", HubURL, " | Syms: ", g_symCount,
          " | DOM: ", SendDOM ? "ON" : "OFF", " | Simulate: ", SimulateDOM ? "YES" : "NO");
    for (int i = 0; i < g_symCount; i++)
        Print("[v3] ", g_baseSymbols[i], " -> ", g_realSymbols[i]);

    SendAllData();
    if (SendDOM) SendDOMData();
    return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) {
    Print("[ATTRAOS v3.00] Dừng | Sent=", g_totalSent, " Errs=", g_errors);
}

void OnTimer() { }
void OnTick() {
    datetime now = TimeCurrent();

    // Update CVD on every tick
    UpdateCVDFromTick();

    // Main market data
    if (now - g_lastSend >= SendInterval) SendAllData();

    // DOM data (gửi nhanh hơn để Bookmap mượt mà)
    if (SendDOM && now - g_lastDOMSend >= DOMInterval) SendDOMData();
}

void OnTradeTransaction(const MqlTradeTransaction &t, const MqlTradeRequest &r, const MqlTradeResult &res) {
    if (t.type == TRADE_TRANSACTION_DEAL_ADD || t.type == TRADE_TRANSACTION_ORDER_ADD)
        SendAllData();
}

//+------------------------------------------------------------------+
//| Cập nhật CVD từ tick hiện tại                                    |
//+------------------------------------------------------------------+
void UpdateCVDFromTick() {
    for (int i = 0; i < g_symCount; i++) {
        string sym = g_realSymbols[i];
        double bid = SymbolInfoDouble(sym, SYMBOL_BID);
        double ask = SymbolInfoDouble(sym, SYMBOL_ASK);
        double mid = (bid + ask) / 2.0;
        double vol = (double)SymbolInfoInteger(sym, SYMBOL_VOLUME);
        if (vol <= 0) vol = 1;

        if (g_lastPrice[i] > 0) {
            if (mid >= g_lastPrice[i]) {
                g_cvd[i] += vol;
                g_buyVol[i] += vol;
            } else {
                g_cvd[i] -= vol;
                g_sellVol[i] += vol;
            }
        }
        g_lastPrice[i] = mid;
        g_tickCount[i]++;
    }
}

//+------------------------------------------------------------------+
//| JSON helpers                                                     |
//+------------------------------------------------------------------+
string JsonEscape(string s) {
    StringReplace(s, "\\", "\\\\");
    StringReplace(s, "\"", "\\\"");
    return s;
}

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
            (long)rates[i].time, rates[i].open, rates[i].high, rates[i].low, rates[i].close,
            (double)rates[i].tick_volume
        );
    }
    return out + "]";
}

//+------------------------------------------------------------------+
//| Build DOM JSON từ MarketBook (thật) HOẶC Simulator              |
//+------------------------------------------------------------------+
string BuildDOMJSON(string realSym, string baseSym, int symIdx) {
    double bid    = SymbolInfoDouble(realSym, SYMBOL_BID);
    double ask    = SymbolInfoDouble(realSym, SYMBOL_ASK);
    double pt     = SymbolInfoDouble(realSym, SYMBOL_POINT);
    double spread = (ask - bid);
    if (pt <= 0) pt = 0.01;

    string domArr = "[]";
    bool usedRealDOM = false;

    // ─── Thử DOM thật từ MT5 broker (MarketBook) ─────────────────
    if (!SimulateDOM) {
        MqlBookInfo book[];
        if (MarketBookAdd(realSym) && MarketBookGet(realSym, book)) {
            int bookSize = ArraySize(book);
            if (bookSize > 0) {
                domArr = "[";
                bool first = true;
                for (int i = 0; i < bookSize && i < DOMDepth * 2; i++) {
                    if (!first) domArr += ",";
                    first = false;
                    string side = (book[i].type == BOOK_TYPE_BUY || book[i].type == BOOK_TYPE_BUY_MARKET) ? "bid" : "ask";
                    domArr += StringFormat("{\"price\":%.5f,\"side\":\"%s\",\"vol\":%.2f}",
                                          book[i].price, side, book[i].volume);
                }
                domArr += "]";
                usedRealDOM = true;
            }
        }
    }

    // ─── DOM Simulator (khi broker không cấp DOM hoặc SimulateDOM=true) ─
    if (!usedRealDOM) {
        // Thuật toán Synthetic DOM:
        // 1. Tạo các level giá cách nhau 1 pip
        // 2. Volume phân phối theo hàm Gaussian (dày tại bid/ask, mỏng dần ra ngoài)
        // 3. Thêm vùng "Iceberg" ngẫu nhiên (volume đột biến) tại ~3-5 level
        // 4. Mỗi 30s random 1 "Spoof event" — volume lớn rồi bỏ đi
        double pipStep = pt * 10;   // 1 pip = 10 point
        string domLevels = "[";
        bool first = true;
        double totalVol = g_buyVol[symIdx] + g_sellVol[symIdx];
        if (totalVol <= 0) totalVol = 1000;

        // Bid side (dưới giá hiện tại)
        for (int i = 1; i <= DOMDepth; i++) {
            double lvPrice = bid - i * pipStep;
            // Gaussian decay + random noise
            double base = totalVol * 0.05 * MathExp(-0.3 * (i - 1));
            double vol  = base * (0.7 + 0.6 * ((double)MathRand() / 32767));
            // Iceberg spike tại level 3-4
            if (i == 3 || i == 4) vol *= (2.0 + (double)MathRand() / 32767 * 2.0);
            if (!first) domLevels += ",";
            first = false;
            domLevels += StringFormat("{\"price\":%.5f,\"side\":\"bid\",\"vol\":%.1f}", lvPrice, vol);
        }
        // Ask side (trên giá hiện tại)
        for (int i = 1; i <= DOMDepth; i++) {
            double lvPrice = ask + i * pipStep;
            double base = totalVol * 0.05 * MathExp(-0.3 * (i - 1));
            double vol  = base * (0.7 + 0.6 * ((double)MathRand() / 32767));
            if (i == 3 || i == 4) vol *= (2.0 + (double)MathRand() / 32767 * 2.0);
            if (!first) domLevels += ",";
            first = false;
            domLevels += StringFormat("{\"price\":%.5f,\"side\":\"ask\",\"vol\":%.1f}", lvPrice, vol);
        }
        domArr = domLevels + "]";
    }

    // Tổng hợp delta info
    double totalBuy  = g_buyVol[symIdx];
    double totalSell = g_sellVol[symIdx];
    double totalAll  = totalBuy + totalSell;
    double buyPct    = (totalAll > 0) ? (totalBuy / totalAll * 100.0) : 50.0;
    bool   isDivergence = false;
    // Đơn giản: nếu CVD dương (nhiều buy) nhưng giá thấp hơn lastPrice → phân kỳ
    if (g_cvd[symIdx] > 50 && g_lastPrice[symIdx] < bid) isDivergence = true;
    if (g_cvd[symIdx] < -50 && g_lastPrice[symIdx] > bid) isDivergence = true;

    string result = StringFormat(
        "{\"symbol\":\"%s\",\"bid\":%.5f,\"ask\":%.5f,"
        "\"dom\":%s,"
        "\"cvd\":%.1f,\"buy_vol\":%.1f,\"sell_vol\":%.1f,"
        "\"buy_pct\":%.1f,\"sell_pct\":%.1f,"
        "\"divergence\":%s,\"tick_count\":%I64d,"
        "\"source\":\"%s\",\"updated_at\":%I64d}",
        baseSym, bid, ask,
        domArr,
        g_cvd[symIdx], totalBuy, totalSell,
        buyPct, 100.0 - buyPct,
        isDivergence ? "true" : "false",
        (long)g_tickCount[symIdx],
        usedRealDOM ? "real_dom" : "simulated",
        (long)TimeCurrent()
    );

    return result;
}

//+------------------------------------------------------------------+
//| Gửi DOM + Order Flow Data (file riêng, cập nhật nhanh hơn)      |
//+------------------------------------------------------------------+
void SendDOMData() {
    g_lastDOMSend = TimeCurrent();

    string payload = "{\"orderflow\":[";
    bool first = true;
    for (int i = 0; i < g_symCount; i++) {
        if (!first) payload += ",";
        first = false;
        payload += BuildDOMJSON(g_realSymbols[i], g_baseSymbols[i], i);
    }
    payload += StringFormat("],\"ea_version\":\"3.00\",\"ts\":%I64d}", (long)TimeCurrent());

    // Ghi vào file riêng mt5_orderflow.json
    int f = FileOpen("mt5_orderflow.json", FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON);
    if (f != INVALID_HANDLE) {
        FileWriteString(f, payload);
        FileClose(f);
        if (Verbose) Print("[v3] DOM OK | ", StringLen(payload), "B");
    } else {
        g_errors++;
        if (Verbose) Print("[v3] DOM FILE ERR ", GetLastError());
    }
}

//+------------------------------------------------------------------+
//| Main market data (kế thừa từ v2, thêm dom_ref)                 |
//+------------------------------------------------------------------+
void SendAllData() {
    g_lastSend = TimeCurrent();
    bool isFirstSend = (g_totalSent == 0);

    // ── 1. Market data ────────────────────────────────────────────
    string marketJSON = "[";
    bool firstSym = true;
    for (int i = 0; i < g_symCount; i++) {
        string baseSym = g_baseSymbols[i];
        string realSym = g_realSymbols[i];
        double bid = SymbolInfoDouble(realSym, SYMBOL_BID);
        double ask = SymbolInfoDouble(realSym, SYMBOL_ASK);
        if (bid <= 0 && ask <= 0) continue;

        double pt  = SymbolInfoDouble(realSym, SYMBOL_POINT);
        double sprd = (pt > 0) ? (ask - bid) / pt : 0;
        double atr = 0;
        MqlRates atrR[];
        if (CopyRates(realSym, PERIOD_H1, 0, 15, atrR) == 15) {
            double sum = 0;
            for (int j = 0; j < 14; j++) sum += (atrR[j].high - atrR[j].low);
            atr = sum / 14.0;
        }

        string c_m15 = "null", c_h1 = "null", c_h4 = "null";
        if (SendCandles) {
            c_m15 = BuildCandlesJSON(realSym, PERIOD_M15, CandleCount);
            c_h1  = BuildCandlesJSON(realSym, PERIOD_H1,  CandleCount);
            c_h4  = BuildCandlesJSON(realSym, PERIOD_H4,  MathMin(CandleCount, 60));
        }

        if (!firstSym) marketJSON += ",";
        firstSym = false;
        // v3: thêm cvd_snapshot vào market data
        marketJSON += StringFormat(
            "{\"symbol\":\"%s\",\"bid\":%.5f,\"ask\":%.5f,\"spread\":%.1f,\"atr\":%.5f,"
            "\"m15\":%s,\"h1\":%s,\"h4\":%s,"
            "\"cvd_snapshot\":%.1f,\"buy_pct_snapshot\":%.1f}",
            baseSym, bid, ask, sprd, atr, c_m15, c_h1, c_h4,
            g_cvd[i],
            (g_buyVol[i] + g_sellVol[i] > 0) ? g_buyVol[i] / (g_buyVol[i] + g_sellVol[i]) * 100.0 : 50.0
        );
    }
    marketJSON += "]";

    // ── 2. Account ────────────────────────────────────────────────
    string accountJSON = "{}";
    if (SendAccount) {
        accountJSON = StringFormat(
            "{\"login\":%d,\"name\":\"%s\",\"server\":\"%s\","
            "\"balance\":%.2f,\"equity\":%.2f,\"margin\":%.2f,"
            "\"free_margin\":%.2f,\"profit\":%.2f,\"leverage\":%d,\"currency\":\"%s\"}",
            AccountInfoInteger(ACCOUNT_LOGIN),
            JsonEscape(AccountInfoString(ACCOUNT_NAME)),
            JsonEscape(AccountInfoString(ACCOUNT_SERVER)),
            AccountInfoDouble(ACCOUNT_BALANCE), AccountInfoDouble(ACCOUNT_EQUITY),
            AccountInfoDouble(ACCOUNT_MARGIN),  AccountInfoDouble(ACCOUNT_FREEMARGIN),
            AccountInfoDouble(ACCOUNT_PROFIT),  (int)AccountInfoInteger(ACCOUNT_LEVERAGE),
            AccountInfoString(ACCOUNT_CURRENCY)
        );
    }

    // ── 3. Positions ──────────────────────────────────────────────
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
                PositionGetDouble(POSITION_VOLUME), PositionGetDouble(POSITION_PRICE_OPEN),
                PositionGetDouble(POSITION_PRICE_CURRENT), PositionGetDouble(POSITION_SL),
                PositionGetDouble(POSITION_TP), PositionGetDouble(POSITION_PROFIT),
                PositionGetDouble(POSITION_SWAP)
            );
        }
        ordersJSON += "]";
    }

    // ── 4. Build + Write main payload ─────────────────────────────
    string payload = StringFormat(
        "{\"market\":%s,\"account\":%s,\"positions\":%s,"
        "\"ea_version\":\"3.00\",\"broker_time\":\"%s\",\"timestamp\":%I64d,"
        "\"update_candles\":true,\"dom_enabled\":%s}",
        marketJSON, accountJSON, ordersJSON,
        TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS),
        (long)TimeCurrent(),
        SendDOM ? "true" : "false"
    );

    int f = FileOpen("mt5_hub.json", FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON);
    if (f != INVALID_HANDLE) {
        FileWriteString(f, payload);
        FileClose(f);
        g_totalSent++;
        if (g_totalSent <= 3 || g_totalSent % 20 == 0)
            Print("[ATTRAOS v3] FILE OK #", g_totalSent, " | ", StringLen(payload), "B");
    } else {
        g_errors++;
        Print("[ATTRAOS v3] FILE ERR ", GetLastError());
    }

    // ── 5. WebRequest handshake (lần đầu) ─────────────────────────
    if (isFirstSend) {
        string notifyURL  = HubURL + "/mt5/file_ready";
        string headers    = "Content-Type: application/json\r\n";
        if (HubToken != "") headers += "X-Admin-Token: " + HubToken + "\r\n";
        string notifyBody = StringFormat("{\"path\":\"mt5_hub.json\",\"ea_version\":\"3.00\",\"ts\":%I64d,\"dom\":%s}",
                                         (long)TimeCurrent(), SendDOM ? "true" : "false");
        char nd[], nr[];
        string nh;
        int n = StringToCharArray(notifyBody, nd, 0, WHOLE_ARRAY, CP_UTF8);
        if (n > 1) ArrayResize(nd, n - 1);
        int code = WebRequest("POST", notifyURL, headers, 5000, nd, nr, nh);
        Print("[ATTRAOS v3] Handshake code=", code, " DOM=", SendDOM ? "ON" : "OFF");
    }
}
