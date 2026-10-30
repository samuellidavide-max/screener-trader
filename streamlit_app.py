"""
streamlit_app.py — Screener + Backtest "WVF + Williams A/D"
===========================================================
App web (mobile-friendly) pensata per Streamlit Community Cloud.
Due schede:
  • SCREENER  : rimbalzi da ipervenduto sull'S&P500, punteggio 0-100.
  • BACKTEST  : simulazione a N anni (top titoli ogni mese) vs S&P500.

Il calcolo gira sul server Streamlit (che raggiunge Yahoo), quindi dal
telefono basta aprire il link. Su Android: "Aggiungi a schermata Home"
per usarla come un'app.
"""

import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")

# ======================================================================
#  PARAMETRI STRATEGIA (le due porte: panico+rientro / WAD gira su)
# ======================================================================
WVF_PD = 22; WVF_MA_FAST = 3; WVF_MA_SLOW = 200
WAD_EMA_LEN = 50; WAD_MA_FAST = 3
HIGH_LB = 50; HIGH_PCT = 0.85
PEAK_WINDOW = 20; PANICO_MIN = 5.0; RIENTRO_FRAC = 0.60
SLOPE_LB = 5; CROSS_FRESH_BARS = 7
MIN_BARRE = max(WVF_MA_SLOW, WAD_EMA_LEN) + 10


SP500_FALLBACK = ["MMM","AOS","ABT","ABBV","ACN","ADBE","AMD","AES","AFL","A","APD","AKAM","ALB","ARE","ALGN","ALLE","LNT","ALL","GOOGL","MO","AMZN","AEE","AEP","AXP","AIG","AMT","AMP","AME","AMGN","APH","ADI","AON","APA","AAPL","AMAT","ADM","AJG","AIZ","T","ATO","ADSK","ADP","AZO","AVB","AVY","BKR","BALL","BAC","BAX","BDX","BBY","BIIB","BLK","BK","BA","BKNG","BSX","BMY","AVGO","BR","BRO","BF-B","BG","CDNS","CPB","COF","CAH","KMX","CCL","CAT","CBOE","CBRE","CDW","CE","CNC","CNP","CF","CHRW","SCHW","CHTR","CVX","CMG","CB","CHD","CI","CINF","CTAS","CSCO","C","CFG","CLX","CME","CMS","KO","CTSH","CL","CMCSA","CAG","COP","ED","STZ","COO","CPRT","GLW","COST","CCI","CSX","CMI","CVS","DHR","DRI","DVA","DE","DAL","DVN","DLR","DFS","DG","DLTR","D","DPZ","DOV","DOW","DHI","DTE","DUK","DD","EMN","ETN","EBAY","ECL","EIX","EW","EA","ELV","EMR","ETR","EOG","EFX","EQIX","EQR","ESS","EL","EVRG","ES","EXC","EXPE","EXPD","EXR","XOM","FFIV","FDS","FICO","FAST","FRT","FDX","FIS","FITB","FE","FI","FMC","F","FTV","BEN","FCX","GRMN","IT","GD","GE","GIS","GPC","GILD","GL","GS","HAL","HIG","HAS","HCA","HSIC","HSY","HES","HLT","HOLX","HD","HON","HRL","HST","HWM","HPQ","HUBB","HUM","HBAN","HII","IBM","IEX","IDXX","ITW","INCY","IR","INTC","ICE","IFF","IP","IPG","INTU","ISRG","IVZ","IQV","IRM","JBHT","JKHY","J","JNJ","JCI","JPM","JNPR","K","KEY","KEYS","KMB","KIM","KMI","KLAC","KHC","KR","LHX","LH","LRCX","LVS","LDOS","LEN","LLY","LIN","LKQ","LMT","L","LOW","LULU","LYB","MTB","MPC","MKTX","MAR","MMC","MLM","MAS","MA","MKC","MCD","MCK","MDT","MRK","MET","MTD","MGM","MCHP","MU","MSFT","MAA","MHK","MOH","TAP","MDLZ","MPWR","MNST","MCO","MS","MOS","MSI","MSCI","NDAQ","NTAP","NFLX","NEM","NEE","NKE","NI","NDSN","NSC","NTRS","NOC","NCLH","NRG","NUE","NVDA","NVR","NXPI","ORLY","OXY","ODFL","OMC","OKE","ORCL","OTIS","PCAR","PKG","PH","PAYX","PAYC","PYPL","PNR","PEP","PFE","PM","PSX","PNW","PNC","POOL","PPG","PPL","PFG","PG","PGR","PLD","PRU","PEG","PSA","PHM","QRVO","PWR","QCOM","DGX","RL","RJF","RTX","O","REG","REGN","RF","RSG","RMD","ROK","ROL","ROP","ROST","RCL","SPGI","CRM","SBAC","SLB","STX","SRE","NOW","SHW","SPG","SWKS","SJM","SNA","SO","LUV","SWK","SBUX","STT","STLD","STE","SYK","SNPS","SYY","TMUS","TROW","TTWO","TPR","TGT","TEL","TDY","TFX","TER","TSLA","TXN","TXT","TMO","TJX","TSCO","TT","TDG","TRV","TFC","TYL","TSN","USB","UDR","ULTA","UNP","UAL","UPS","URI","UNH","UHS","VLO","VTR","VRSN","VRSK","VZ","VRTX","VTRS","V","VMC","WAB","WBA","WMT","DIS","WM","WAT","WEC","WFC","WELL","WST","WDC","WRB","WY","WMB","WTW","GWW","WYNN","XEL","XYL","YUM","ZBRA","ZBH","ZTS"]
FTSE_MIB = ["A2A.MI","AMP.MI","AZM.MI","BGN.MI","BAMI.MI","BMED.MI","BPE.MI","BPSO.MI","BZU.MI","CPR.MI","DIA.MI","ENEL.MI","ENI.MI","ERG.MI","RACE.MI","FBK.MI","G.MI","HER.MI","IP.MI","ISP.MI","INW.MI","IG.MI","LDO.MI","MB.MI","MONC.MI","NEXI.MI","PIRC.MI","PST.MI","PRY.MI","REC.MI","SPM.MI","SRG.MI","STLAM.MI","STMMI.MI","TIT.MI","TEN.MI","TRN.MI","UCG.MI","UNI.MI"]


@st.cache_data(show_spinner=False, ttl=86400)
def get_sp500():
    try:
        t = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
        syms = [s.replace(".", "-") for s in t[0]["Symbol"].astype(str).str.strip() if s and s != "nan"]
        if len(syms) > 400:
            return syms
    except Exception:
        pass
    return SP500_FALLBACK


# ======================================================================
#  SCORING (una fetta di storico -> punteggio, come lo screener)
# ======================================================================
def _score_core(close, high, low, dettagli=False):
    if len(close) < MIN_BARRE:
        return (0.0, {}) if dettagli else 0.0
    hc = close.rolling(WVF_PD).max()
    wvf = (hc - low) / hc * 100.0
    ma3 = wvf.rolling(WVF_MA_FAST).mean()
    ma200 = wvf.rolling(WVF_MA_SLOW).mean()
    rH = wvf.rolling(HIGH_LB).max() * HIGH_PCT

    pc = close.shift(1)
    trh = np.maximum(pc, high); trl = np.minimum(pc, low)
    t = pd.Series(0.0, index=close.index)
    t = t.where(~(close > pc), close - trl)
    t = t.where(~(close < pc), close - trh)
    ad = t.cumsum()
    lag = int(round((WAD_EMA_LEN - 1) / 2))
    ed = ad + (ad - ad.shift(lag))
    w50 = ed.ewm(span=WAD_EMA_LEN, adjust=False).mean()
    w3 = ad.rolling(WAD_MA_FAST).mean()

    L = lambda s, i=0: s.iloc[-1 - i]
    if any(pd.isna(x) for x in [L(ma3), L(w50), L(rH)]):
        return (0.0, {}) if dettagli else 0.0

    win = wvf.iloc[-PEAK_WINDOW:]; thr = rH.iloc[-PEAK_WINDOW:]
    picco = float(win.max()); ora = float(L(wvf))
    zona_alta = (picco >= PANICO_MIN) or (bool((win >= thr).any()) and picco >= PANICO_MIN * 0.6)
    rientro = picco > 0 and ora < picco * RIENTRO_FRAC
    scende = L(ma3) < L(ma3, 1)
    gateA = zona_alta and rientro and scende

    sl_now = L(w50) - L(w50, SLOPE_LB); sl_prev = L(w50, SLOPE_LB) - L(w50, 2 * SLOPE_LB)
    accel = sl_now > sl_prev and sl_now > -abs(sl_prev) * 0.1
    e3, e50 = w3.values, w50.values
    bars_since = None
    for k in range(1, CROSS_FRESH_BARS + 1):
        if (len(e3) > k + 5 and e3[-1 - k] <= e50[-1 - k] and e3[-k] > e50[-k]
                and all(e3[-1 - k - j] <= e50[-1 - k - j] for j in range(1, 4))):
            bars_since = k - 1; break
    gateB = accel or (bars_since is not None)

    d = {"WVF_picco": round(picco, 1), "WVF_ora": round(ora, 2),
         "Zona_alta": "si" if zona_alta else "no",
         "Rientro": "si" if (rientro and scende) else "no",
         "Regime": "neutrale/buy" if L(ma200) > L(ma3) else "discesa",
         "WAD_accel": "si" if accel else "no",
         "WAD_cross": "oggi" if bars_since == 0 else (f"{bars_since}gg fa" if bars_since is not None else "-")}

    if not (gateA and gateB):
        return (0.0, d) if dettagli else 0.0
    s = 35 * min((picco - ora) / max(picco, 1e-9), 1.0)
    s += 15 if L(ma200) > L(ma3) else 0
    if bars_since == 0: s += 30
    elif bars_since is not None: s += 30 * max(1 - bars_since / CROSS_FRESH_BARS, 0)
    s += 20 if accel else 0
    s = round(min(s, 100), 1)
    return (s, d) if dettagli else s


# ======================================================================
#  DOWNLOAD (con cache)
# ======================================================================
@st.cache_data(show_spinner=False, ttl=3600)
def scarica(tickers, period=None, start=None):
    """Ritorna dict ticker -> DataFrame OHLC (adjusted)."""
    dati = {}
    B = 100
    for i in range(0, len(tickers), B):
        blk = tickers[i:i + B]
        try:
            if start:
                raw = yf.download(blk, start=start, interval="1d", progress=False,
                                  auto_adjust=True, threads=True, group_by="ticker")
            else:
                raw = yf.download(blk, period=period, interval="1d", progress=False,
                                  auto_adjust=True, threads=True, group_by="ticker")
        except Exception:
            continue
        for tk in blk:
            try:
                sub = raw[tk].dropna() if isinstance(raw.columns, pd.MultiIndex) else raw.dropna()
                if not sub.empty:
                    dati[tk] = sub[["Open", "High", "Low", "Close"]]
            except Exception:
                pass
    return dati


# ======================================================================
#  DATI FONDAMENTALI (nome, capitalizzazione, PEG, P/E, ROE)
#  Scaricati SOLO per i candidati tecnici (veloce), uno per uno con cache.
# ======================================================================
@st.cache_data(show_spinner=False, ttl=21600)
def get_fondamentali(ticker):
    tko = yf.Ticker(ticker)
    try:
        info = tko.info or {}
    except Exception:
        info = {}

    def g(*keys):
        for k in keys:
            v = info.get(k)
            if v is not None:
                return v
        return None

    mktcap = g("marketCap")
    if mktcap is None:                 # canale alternativo per la capitalizzazione
        try:
            fi = tko.fast_info
            mktcap = fi.get("market_cap") if hasattr(fi, "get") else getattr(fi, "market_cap", None)
        except Exception:
            pass

    pe = g("trailingPE", "forwardPE")
    peg = g("trailingPegRatio", "pegRatio")
    if peg is None:                    # PEG calcolato se Yahoo non lo fornisce
        growth = g("earningsGrowth", "earningsQuarterlyGrowth")
        if pe is not None and growth is not None and growth > 0:
            peg = round(pe / (growth * 100), 2)

    return {
        "Azienda": g("shortName", "longName") or ticker,
        "MktCap": mktcap,                     # in valuta (USD/EUR)
        "PEG": peg,
        "PE": pe,
        "ROE": g("returnOnEquity"),           # frazione: 0.15 = 15%
    }


def link_grafico(ticker, provider="Yahoo Finance"):
    if provider == "TradingView":
        return f"https://www.tradingview.com/chart/?symbol={ticker}"
    return f"https://finance.yahoo.com/quote/{ticker}"


# ======================================================================
#  UI
# ======================================================================
st.set_page_config(page_title="WVF + Williams A/D", page_icon="📈", layout="centered")
st.title("📈 WVF + Williams A/D")
st.caption("Rimbalzi da ipervenduto · timeframe D1 · dati Yahoo Finance")

tab_scr, tab_bt, tab_info = st.tabs(["🎯 Screener", "📊 Backtest", "ℹ️ Info"])


# ----------------------------- SCREENER -----------------------------
with tab_scr:
    universo = st.radio("Universo", ["S&P 500", "FTSE MIB", "Lista mia"], horizontal=True)
    if universo == "Lista mia":
        txt = st.text_area("Ticker (uno per riga)", "AAPL\nMSFT\nENEL.MI\nISP.MI", height=120)
        tickers_s = [x.strip().upper() for x in txt.splitlines() if x.strip()]
    else:
        tickers_s = get_sp500() if universo == "S&P 500" else FTSE_MIB

    soglia = st.slider("Punteggio minimo", 0, 100, 0, 5)
    chart_src = st.selectbox("Il click sul ticker apre il grafico su",
                             ["Yahoo Finance", "TradingView"])

    with st.expander("🔎 Filtri fondamentali", expanded=True):
        usa_fond = st.checkbox("Applica filtri fondamentali", True)
        f1, f2 = st.columns(2)
        min_mktcap = f1.number_input("Capitalizzazione minima (miliardi)", 0.0, 5000.0, 10.0, 1.0)
        max_peg = f2.number_input("PEG massimo", 0.0, 20.0, 1.0, 0.1)
        f3, f4 = st.columns(2)
        max_pe = f3.number_input("P/E massimo", 0.0, 500.0, 35.0, 1.0)
        min_roe = f4.number_input("ROE minimo (%)", -100.0, 200.0, 10.0, 1.0)
        escludi_mancanti = st.checkbox("Escludi titoli con dati fondamentali mancanti", True)

    if st.button("🚀 Analizza", type="primary", use_container_width=True):
        with st.spinner(f"Scarico e analizzo {len(tickers_s)} titoli…"):
            dati = scarica(tuple(tickers_s), period="2y")
            rows = []
            for tk, df in dati.items():
                sc, d = _score_core(df["Close"], df["High"], df["Low"], dettagli=True)
                d["Ticker"] = tk; d["Punteggio"] = sc
                d["_pass"] = sc > 0
                rows.append(d)

        if not rows:
            st.warning("Nessun dato scaricato. Riprova tra poco.")
        else:
            full = pd.DataFrame(rows)
            promossi = int(full["_pass"].sum())
            # i candidati tecnici su cui ha senso guardare i fondamentali
            cand = full[(full["_pass"]) & (full["Punteggio"] >= soglia)].copy()
            cand = cand.sort_values("Punteggio", ascending=False).reset_index(drop=True)

            # --- fondamentali solo per i candidati (veloce) ---
            if len(cand):
                prog = st.progress(0.0, text="Scarico i dati fondamentali dei candidati…")
                fond = []
                for i, tk in enumerate(cand["Ticker"], 1):
                    fond.append(get_fondamentali(tk))
                    prog.progress(i / len(cand))
                prog.empty()
                fdf = pd.DataFrame(fond)
                for c in ["Azienda", "MktCap", "PEG", "PE", "ROE"]:
                    cand[c] = fdf[c].values if c in fdf else None

            # quanti candidati hanno davvero ricevuto dati da Yahoo?
            dati_fond_ok = 0
            if len(cand) and "MktCap" in cand:
                dati_fond_ok = int(cand[["MktCap", "PE", "ROE"]].notna().any(axis=1).sum())
            fond_in_blocco_assenti = len(cand) > 0 and dati_fond_ok == 0

            # --- applica i filtri fondamentali ---
            scartati_fond = 0
            if usa_fond and len(cand) and fond_in_blocco_assenti:
                st.warning("⚠️ Yahoo non ha restituito i dati fondamentali per i candidati "
                           "(di solito è un limite di richieste del server gratuito). "
                           "Mostro i candidati tecnici **senza** filtro fondamentale: "
                           "riprova tra qualche minuto per applicare i filtri.")
            elif usa_fond and len(cand):
                def passa(r):
                    checks = [
                        (r["MktCap"], lambda v: v >= min_mktcap * 1e9),
                        (r["PEG"],    lambda v: v < max_peg),
                        (r["PE"],     lambda v: v < max_pe),
                        (r["ROE"],    lambda v: v * 100 > min_roe),
                    ]
                    for val, cond in checks:
                        if val is None or (isinstance(val, float) and pd.isna(val)):
                            if escludi_mancanti:
                                return False
                            continue
                        if not cond(val):
                            return False
                    return True
                mask = cand.apply(passa, axis=1)
                scartati_fond = int((~mask).sum())
                cand = cand[mask].reset_index(drop=True)

            # --- metriche di testa ---
            c1, c2, c3 = st.columns(3)
            c1.metric("Passano tutto", len(cand))
            c2.metric("Candidati tecnici", promossi)
            c3.metric("Scartati dai fond.", scartati_fond if usa_fond else "—")

            if not len(cand):
                st.info("Nessun titolo supera sia lo screen tecnico sia i filtri fondamentali. "
                        "Prova ad allentare i filtri o abbassa il punteggio minimo.")
            else:
                # colonne leggibili
                def num(col):   # converte in numerico; i mancanti -> NaN (cella vuota)
                    return pd.to_numeric(cand[col], errors="coerce") if col in cand else np.nan

                view = pd.DataFrame()
                view["Grafico"] = [link_grafico(t, chart_src) for t in cand["Ticker"]]
                view["Ticker"] = cand["Ticker"].values
                view["Azienda"] = cand["Azienda"].values if "Azienda" in cand else ""
                view["Punteggio"] = cand["Punteggio"].values
                view["MktCap (mld)"] = (num("MktCap") / 1e9).round(1).values
                view["PEG"] = num("PEG").round(2).values
                view["P/E"] = num("PE").round(1).values
                view["ROE %"] = (num("ROE") * 100).round(1).values
                view["Regime"] = cand["Regime"].values
                view["WVF_picco"] = cand["WVF_picco"].values
                view["WAD_cross"] = cand["WAD_cross"].values

                st.dataframe(
                    view,
                    use_container_width=True, hide_index=True,
                    column_config={
                        "Grafico": st.column_config.LinkColumn(
                            "📈", display_text="apri", width="small"),
                        "Punteggio": st.column_config.NumberColumn(format="%.1f"),
                    },
                )
                st.caption("Tocca **apri** nella colonna 📈 per vedere il grafico del titolo.")
                st.download_button("⬇️ CSV", view.to_csv(index=False).encode(),
                                   "screener.csv", "text/csv", use_container_width=True)


# ----------------------------- BACKTEST -----------------------------
with tab_bt:
    st.write("Ogni inizio mese investe in parti uguali sui titoli col punteggio più alto, "
             "li tiene un mese, poi rivaluta. Confronto con S&P 500 (SPY).")
    cc1, cc2 = st.columns(2)
    anni = cc1.slider("Anni", 3, 10, 10)
    top_n = cc2.slider("Top N titoli/mese", 3, 20, 10)
    univ_bt = st.radio("Universo backtest", ["S&P 500", "FTSE MIB"], horizontal=True, key="ubt")
    st.caption("⚠️ Sul server gratuito il backtest S&P500 a 10 anni può richiedere 1-3 minuti.")

    if st.button("▶️ Esegui backtest", type="primary", use_container_width=True):
        tickers_b = get_sp500() if univ_bt == "S&P 500" else FTSE_MIB
        bench = "SPY" if univ_bt == "S&P 500" else "^GDAXI"  # proxy benchmark
        start = (pd.Timestamp.today() - pd.DateOffset(years=anni + 1)).strftime("%Y-%m-%d")

        with st.spinner("Scarico lo storico…"):
            dati = scarica(tuple(tickers_b + [bench]), start=start)

        if bench not in dati:
            st.error("Benchmark non disponibile, riprova.")
        else:
            bser = dati[bench]["Close"]
            idx_all = bser.index
            pdm = (pd.Series(idx_all, index=idx_all).groupby([idx_all.year, idx_all.month]).first().values)
            pdm = pd.DatetimeIndex(sorted(pdm))
            cutoff = pd.Timestamp.today() - pd.DateOffset(years=anni)
            mesi = [d for d in pdm if d >= cutoff]

            eq_s, eq_b, date_eq = [10000.0], [10000.0], [mesi[0]]
            prog = st.progress(0.0)
            for j in range(len(mesi) - 1):
                t0, t1 = mesi[j], mesi[j + 1]
                punteggi = []
                for tk, df in dati.items():
                    if tk == bench:
                        continue
                    c = df["Close"]; c0 = c[c.index <= t0]
                    if len(c0) < MIN_BARRE:
                        continue
                    h0 = df["High"][df["High"].index <= t0]; l0 = df["Low"][df["Low"].index <= t0]
                    sc = _score_core(c0, h0, l0)
                    if sc > 0:
                        punteggi.append((tk, sc))
                punteggi.sort(key=lambda x: -x[1])
                top = punteggi[:top_n]
                rets = []
                for tk, _ in top:
                    c = dati[tk]["Close"]
                    p0, p1 = c.asof(t0), c.asof(t1)
                    if p0 and p1 and p0 > 0:
                        rets.append(p1 / p0 - 1)
                r_s = float(np.mean(rets)) if rets else 0.0
                pb0, pb1 = bser.asof(t0), bser.asof(t1)
                r_b = (pb1 / pb0 - 1) if (pb0 and pb1 and pb0 > 0) else 0.0
                eq_s.append(eq_s[-1] * (1 + r_s))
                eq_b.append(eq_b[-1] * (1 + r_b))
                date_eq.append(t1)
                prog.progress((j + 1) / (len(mesi) - 1))
            prog.empty()

            def met(eq):
                eq = np.array(eq); yrs = (date_eq[-1] - date_eq[0]).days / 365.25
                tot = eq[-1] / eq[0] - 1
                cagr = (eq[-1] / eq[0]) ** (1 / yrs) - 1 if yrs > 0 else 0
                r = np.diff(eq) / eq[:-1]
                sh = (np.mean(r) / np.std(r) * np.sqrt(12)) if np.std(r) > 0 else 0
                dd = ((eq - np.maximum.accumulate(eq)) / np.maximum.accumulate(eq)).min()
                return tot, cagr, sh, dd

            ts, cs, ss, ds = met(eq_s); tb, cb, sb, db = met(eq_b)
            m1, m2 = st.columns(2)
            m1.metric("Strategia — totale", f"{ts*100:+.0f}%", f"CAGR {cs*100:+.1f}%")
            m2.metric("S&P500 — totale", f"{tb*100:+.0f}%", f"CAGR {cb*100:+.1f}%")
            m3, m4 = st.columns(2)
            m3.metric("Sharpe (S / SP)", f"{ss:.2f} / {sb:.2f}")
            m4.metric("MaxDD (S / SP)", f"{ds*100:.0f}% / {db*100:.0f}%")

            chart_df = pd.DataFrame({"Strategia": eq_s, "S&P500": eq_b},
                                    index=[d.strftime("%Y-%m") for d in date_eq])
            st.line_chart(chart_df)
            st.caption(f"Capitale finale strategia: {eq_s[-1]:,.0f}€ (da 10.000€)")


# ----------------------------- INFO -----------------------------
with tab_info:
    st.markdown("""
**Come funziona il punteggio (rimbalzo da ipervenduto).**
Un titolo entra in classifica solo se supera **due porte**:

1. **Panico + rientro** — il Williams Vix Fix è salito di recente in zona di
   vero stress (ipervenduto) ed ora sta rientrando.
2. **WAD gira su** — il Williams A/D sta accelerando al rialzo o ha incrociato
   al rialzo di recente (cross confermato, non rumore).

Chi passa entrambe riceve un punteggio **0–100** per freschezza e nettezza del
segnale.

**Limiti onesti.** I dati arrivano da Yahoo (ritardati). Il backtest usa
l'S&P500 di oggi (*survivorship bias* → rendimenti un po' ottimistici), non
include costi, slippage né tasse, e tiene la liquidità nei mesi senza candidati.

*Strumento di studio, non è consulenza finanziaria.*
""")
