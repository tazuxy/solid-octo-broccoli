//+------------------------------------------------------------------+
//| GotobiPostFix_USDJPY.mq5 - METHOD 2 (round 11, hypothesis F2)    |
//| Rule tested (USDJPY, histdata bid M5 2005-2024, cost 0.5 pip;    |
//|   re-checked on FXCM real bid/ask 2012-2024):                    |
//|   G = Gotobi day (JST date 5,10,15,20,25,30 or last business day |
//|       of the month; weekend -> previous Friday; no JP holidays). |
//|       Month-end G IS traded (unlike method 1).                   |
//|   SELL at 09:55 JST on G (Tokyo fix), CLOSE at 15:00 JST on G.   |
//|   Size: risk InpRiskPercent of equity per 1R,                    |
//|         R = InpRiskATRMult x ATR(14) of the last closed D1 bar.  |
//|   Stop: 1R above entry (pre-registered choice, r11_m2_stop_report)|
//|   = about 20 pips; caps intervention-day losses (2011: -343 pips).|
//| Result 2005-2021 (screen): N 1294, +2.9 pips/trade, t 3.20;      |
//|   2022-2024 (one look): N 232, +5.8 pips; 2005-2024 t 3.46.      |
//| Runs next to method 1 (GotobiEve_USDJPY.mq5): method 1 closes    |
//|   its long at 09:55 JST, this EA opens a short at 09:55 JST.     |
//|   Use a HEDGING account or different symbols/accounts; on a      |
//|   NETTING account the two EAs would net each other's positions.  |
//| NOT COMPILED / NOT TESTED in MT5. See assumptions at the bottom. |
//+------------------------------------------------------------------+
#property copyright "research prototype - use at your own risk"
#property version   "0.10"

#include <Trade\Trade.mqh>

enum ENUM_DST_MODE { DST_NONE = 0, DST_US = 1, DST_EU = 2 };

//--- time / calendar
input int           InpBrokerGMTOffsetStd = 2;        // Broker server GMT offset in northern WINTER (hours)
input ENUM_DST_MODE InpBrokerDST          = DST_US;   // Broker DST rule (+1h in summer): US (NY-close brokers), EU, none
input bool          InpAutoGMTLive        = false;    // Live only: derive offset from TimeTradeServer()-TimeGMT()
input string        InpEntryJST           = "09:55";  // Entry time (JST) on G = Gotobi day (Tokyo fix)
input string        InpExitJST            = "15:00";  // Exit time (JST) on the same day
input int           InpEntryWindowMin     = 5;        // Minutes after entry time in which entry is still allowed
input string        InpExtraHolidays      = "";       // Extra JP non-business days, JST, "yyyy.mm.dd,..." (backtest: none)
//--- risk
input double        InpRiskPercent        = 0.25;     // % of equity per 1R (no stop) or at the stop (stop set)
input double        InpRiskATRMult        = 0.25;     // R = this x ATR(14, D1)
input double        InpStopR              = 1.0;      // Stop in R above entry (1.0 = chosen in r11_m2_stop; 0 = no stop)
input double        InpFixedLots          = 0.0;      // >0: fixed lots instead of risk sizing
input double        InpMaxSpreadPips      = 1.5;      // Skip entry if spread > this (pips); spread widens around 09:53-09:55
input int           InpSlippagePoints     = 20;       // Max deviation (points)
input bool          InpSkipMonthEndG      = false;    // Backtest traded month-end G (default false = as tested)
input double        InpMaxHoldHours       = 8.0;      // Safety: close any EA position older than this
input long          InpMagic              = 20261105;

CTrade   trade;
int      atrHandle = INVALID_HANDLE;
datetime holidays[];
int      entryMin = 0, exitMin = 0;
string   gvLast;                      // global variable: last G traded (survives restart)

//+------------------------------------------------------------------+
int ParseHHMM(string s)
{
   string p[];
   if(StringSplit(s, ':', p) != 2) return -1;
   int h = (int)StringToInteger(p[0]), m = (int)StringToInteger(p[1]);
   if(h < 0 || h > 23 || m < 0 || m > 59) return -1;
   return h * 60 + m;
}
datetime DateOnly(datetime t) { return t - (t % 86400); }
datetime MakeDate(int y, int m, int d)
{
   MqlDateTime s; ZeroMemory(s);
   s.year = y; s.mon = m; s.day = d; s.hour = 0; s.min = 0; s.sec = 0;
   return StructToTime(s);
}
int DaysInMonth(int y, int m)
{
   int ny = (m == 12) ? y + 1 : y, nm = (m == 12) ? 1 : m + 1;
   return (int)((MakeDate(ny, nm, 1) - MakeDate(y, m, 1)) / 86400);
}
int DayOfWeek(datetime t) { MqlDateTime s; TimeToStruct(t, s); return s.day_of_week; }   // 0 = Sunday

//--- n-th Sunday (n>=1) or last Sunday (n=0) of a month, as a date
datetime SundayOf(int y, int m, int n)
{
   if(n == 0)
   {
      datetime last = MakeDate(y, m, DaysInMonth(y, m));
      return last - DayOfWeek(last) * 86400;
   }
   datetime first = MakeDate(y, m, 1);
   int firstSun = 1 + (7 - DayOfWeek(first)) % 7;
   return MakeDate(y, m, firstSun + 7 * (n - 1));
}

//--- broker offset (hours) for a given server time
int BrokerOffsetHours(datetime server)
{
   if(InpAutoGMTLive && !MQLInfoInteger(MQL_TESTER))
      return (int)MathRound((double)(TimeTradeServer() - TimeGMT()) / 3600.0);
   int off = InpBrokerGMTOffsetStd;
   if(InpBrokerDST == DST_NONE) return off;
   datetime gmt = server - off * 3600;           // approx. GMT (error <= 1h only near the switch)
   MqlDateTime s; TimeToStruct(gmt, s);
   datetime st, en;
   if(InpBrokerDST == DST_US)
   {
      if(s.year >= 2007) { st = SundayOf(s.year, 3, 2) + 7 * 3600; en = SundayOf(s.year, 11, 1) + 6 * 3600; }
      else               { st = SundayOf(s.year, 4, 1) + 7 * 3600; en = SundayOf(s.year, 10, 0) + 6 * 3600; }
   }
   else { st = SundayOf(s.year, 3, 0) + 3600; en = SundayOf(s.year, 10, 0) + 3600; }
   if(gmt >= st && gmt < en) off += 1;
   return off;
}
//--- JST wall clock (as a datetime value) from server time
datetime ServerToJST(datetime server) { return server - BrokerOffsetHours(server) * 3600 + 9 * 3600; }

//--- JP business-day calendar (weekends + extra holidays only)
bool IsHoliday(datetime d)
{
   for(int i = 0; i < ArraySize(holidays); i++) if(holidays[i] == d) return true;
   return false;
}
bool IsBusinessDay(datetime d)
{
   int w = DayOfWeek(d);
   return (w >= 1 && w <= 5 && !IsHoliday(d));
}
datetime NextBusinessDay(datetime d) { datetime t = d + 86400; while(!IsBusinessDay(t)) t += 86400; return t; }
datetime PrevBusinessDay(datetime d) { datetime t = d - 86400; while(!IsBusinessDay(t)) t -= 86400; return t; }
//--- last business day of the month of d (same calendar as IsGotobi: weekends + InpExtraHolidays)
bool IsLastBusinessDayOfMonth(datetime d)
{
   MqlDateTime s; TimeToStruct(d, s);
   datetime t = MakeDate(s.year, s.mon, DaysInMonth(s.year, s.mon));
   while(!IsBusinessDay(t)) t -= 86400;
   return (t == d);
}
bool IsGotobi(datetime d)
{
   if(!IsBusinessDay(d)) return false;
   MqlDateTime s; TimeToStruct(d, s);
   int dim = DaysInMonth(s.year, s.mon);
   //--- last business day of month
   datetime t = MakeDate(s.year, s.mon, dim);
   while(!IsBusinessDay(t)) t -= 86400;
   if(t == d) return true;
   //--- 5,10,...,30 rolled back to the previous business day in the same month
   for(int n = 5; n <= 30; n += 5)
   {
      if(n > dim) break;
      datetime g = MakeDate(s.year, s.mon, n);
      while(!IsBusinessDay(g))
      {
         g -= 86400;
         MqlDateTime gs; TimeToStruct(g, gs);
         if(gs.mon != s.mon) { g = 0; break; }
      }
      if(g == d) return true;
   }
   return false;
}

//--- helpers
double PipSize() { return (_Digits == 3 || _Digits == 5) ? 10 * _Point : _Point; }
bool   GetPosition(ulong &ticket)
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) == _Symbol && PositionGetInteger(POSITION_MAGIC) == InpMagic)
      { ticket = tk; return true; }
   }
   return false;
}
double LastATR()
{
   double b[];
   if(CopyBuffer(atrHandle, 0, 1, 1, b) != 1) return 0.0;  // shift 1 = last CLOSED D1 bar
   return b[0];
}
double LotsFor(double distPrice)
{
   if(InpFixedLots > 0) return InpFixedLots;
   double tickVal = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double tickSz  = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   if(tickVal <= 0 || tickSz <= 0 || distPrice <= 0) return 0.0;
   double money   = AccountInfoDouble(ACCOUNT_EQUITY) * InpRiskPercent / 100.0;
   double perLot  = distPrice / tickSz * tickVal;
   double lots    = money / perLot;
   double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN), vmax = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   lots = MathFloor(lots / step) * step;
   if(lots < vmin) return 0.0;                 // too small for the account: do not trade
   return MathMin(lots, vmax);
}

//+------------------------------------------------------------------+
int OnInit()
{
   entryMin = ParseHHMM(InpEntryJST); exitMin = ParseHHMM(InpExitJST);
   if(entryMin < 0 || exitMin < 0 || exitMin <= entryMin) { Print("bad JST time input"); return INIT_PARAMETERS_INCORRECT; }
   string p[]; int n = StringSplit(InpExtraHolidays, ',', p);
   ArrayResize(holidays, 0);
   for(int i = 0; i < n; i++)
   {
      string s = p[i]; StringTrimLeft(s); StringTrimRight(s);
      if(StringLen(s) < 8) continue;
      int k = ArraySize(holidays); ArrayResize(holidays, k + 1); holidays[k] = DateOnly(StringToTime(s));
   }
   atrHandle = iATR(_Symbol, PERIOD_D1, 14);
   if(atrHandle == INVALID_HANDLE) return INIT_FAILED;
   trade.SetExpertMagicNumber(InpMagic);
   trade.SetDeviationInPoints(InpSlippagePoints);
   trade.SetTypeFillingBySymbol(_Symbol);
   gvLast = "m2EA_lastG_" + _Symbol + "_" + IntegerToString(InpMagic);
   if(StringFind(_Symbol, "USDJPY") < 0) Print("warning: rule was tested on USDJPY only");
   if(AccountInfoInteger(ACCOUNT_MARGIN_MODE) != ACCOUNT_MARGIN_MODE_RETAIL_HEDGING)
      Print("warning: netting account - do not run together with method 1 on the same symbol");
   EventSetTimer(15);
   return INIT_SUCCEEDED;
}
void OnDeinit(const int reason) { EventKillTimer(); if(atrHandle != INVALID_HANDLE) IndicatorRelease(atrHandle); }
void OnTick()  { Process(); }
void OnTimer() { Process(); }

//+------------------------------------------------------------------+
void Process()
{
   datetime server = TimeTradeServer();
   datetime jst    = ServerToJST(server);
   datetime jday   = DateOnly(jst);
   int      jmin   = (int)((jst - jday) / 60);

   //--- 1) exit management
   ulong tk;
   if(GetPosition(tk))
   {
      string cm = PositionGetString(POSITION_COMMENT);          // "PFX yyyy.mm.dd" = G (JST)
      datetime G = 0;
      if(StringFind(cm, "PFX ") == 0) G = DateOnly(StringToTime(StringSubstr(cm, 4)));
      if(G == 0) G = DateOnly(ServerToJST((datetime)PositionGetInteger(POSITION_TIME)));
      datetime exitJST = G + exitMin * 60;
      double heldH = (double)(server - (datetime)PositionGetInteger(POSITION_TIME)) / 3600.0;
      if(jst >= exitJST || heldH >= InpMaxHoldHours)
      {
         if(!trade.PositionClose(tk)) Print("close failed: ", trade.ResultRetcode());
      }
      return;                                                     // one position at a time
   }

   //--- 2) entry: today (JST) must be a Gotobi day, inside the entry window
   if(!IsGotobi(jday)) return;
   if(jmin < entryMin || jmin >= entryMin + InpEntryWindowMin) return;
   if(GlobalVariableCheck(gvLast) && (datetime)GlobalVariableGet(gvLast) == jday) return;   // already handled
   if(InpSkipMonthEndG && IsLastBusinessDayOfMonth(jday)) { GlobalVariableSet(gvLast, (double)jday); return; }

   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK), bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   if(ask <= 0 || bid <= 0) return;
   if((ask - bid) / PipSize() > InpMaxSpreadPips) return;       // retry until the entry window ends

   double atr = LastATR();
   if(atr <= 0) return;
   double R    = InpRiskATRMult * atr;
   double dist = (InpStopR > 0) ? InpStopR * R : R;
   double lots = LotsFor(dist);
   if(lots <= 0) { Print("lot size below minimum - skipped"); GlobalVariableSet(gvLast, (double)jday); return; }
   double sl = (InpStopR > 0) ? NormalizeDouble(bid + InpStopR * R, _Digits) : 0.0;
   string cm = "PFX " + TimeToString(jday, TIME_DATE);
   if(trade.Sell(lots, _Symbol, 0.0, sl, 0.0, cm))
      GlobalVariableSet(gvLast, (double)jday);
   else
      Print("sell failed: ", trade.ResultRetcode(), " ", trade.ResultRetcodeDescription());
}
//+------------------------------------------------------------------+
// ASSUMPTIONS / NOTES
// 1. Not compiled here. Check with MetaEditor; CTrade::SetTypeFillingBySymbol needs a recent build.
// 2. JST = GMT+9 (no DST). Server->GMT uses InpBrokerGMTOffsetStd (+1h in summer per InpBrokerDST). Verify with your broker.
// 3. Gotobi calendar = weekends + InpExtraHolidays only (backtest used NO JP holidays: leave empty to match it).
// 4. Backtest: sell at the open of the M5 bar starting 09:55 JST, buy back at the open of the M5 bar starting 15:00 JST,
//    cost 0.5 pip round trip, no swap (the hold does not cross the NY rollover), no slippage.
//    Real FXCM bid/ask 2012-2024: paid spread 0.2-0.5 pip; result +4.5 pips/trade. Retail reports show 0.5-2 pip slippage
//    per leg at 09:55; the backtest edge (~3-6 pips/trade) is about used up at ~4 pips of extra round-trip cost.
// 5. Results depend on a few large trades (mean without the top 5% of trades is slightly negative). Use small risk.
// 6. One position per symbol/magic. A missed entry window (no tick, spread > InpMaxSpreadPips) skips that Gotobi day.
// 7. With method 1 on the same account: use a hedging account (the long close and the short open both happen at 09:55).
// 8. Stop (InpStopR=1): with a stop, InpRiskPercent is the loss AT the stop; lot size is the same as R-sizing
//    without a stop. 2005-21: 25% of trades stopped, mean kept at 93%; worst trade -1.08R in M5 data.
//    Real fills during interventions can slip far beyond the stop (M5 data cannot show this).
