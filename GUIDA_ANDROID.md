# Mettere l'app sul telefono Android (via Streamlit Cloud)

L'app gira su un server gratuito di Streamlit; tu la apri col browser del
telefono e la aggiungi alla schermata Home: funziona come un'app.
Tempo richiesto: ~10 minuti, una volta sola.

Ti servono due file (già pronti in questa cartella):
- `streamlit_app.py`
- `requirements.txt`

---

## Passo 1 — Account GitHub
Vai su https://github.com e accedi (o crea un account gratuito).

## Passo 2 — Crea un repository
1. In alto a destra: **+ → New repository**.
2. Nome a piacere, es. `screener-wvf`.
3. Lascia **Public** (Streamlit gratuito richiede repo pubblici).
4. Spunta **Add a README file**.
5. **Create repository**.

## Passo 3 — Carica i due file
1. Nel repo appena creato: **Add file → Upload files**.
2. Trascina `streamlit_app.py` e `requirements.txt`.
3. In basso: **Commit changes**.

> Importante: il file DEVE chiamarsi esattamente `streamlit_app.py`
> (è il nome che Streamlit cerca di default).

## Passo 4 — Pubblica su Streamlit Cloud
1. Vai su https://share.streamlit.io e accedi **con GitHub** (bottone
   "Continue with GitHub", autorizza).
2. Clicca **Create app → Deploy a public app from GitHub**.
3. Compila:
   - **Repository**: `TUO-UTENTE/screener-wvf`
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
4. **Deploy**. La prima build dura 2-5 minuti (installa le librerie).
5. Al termine ottieni un link tipo:
   `https://screener-wvf-xxxx.streamlit.app`

## Passo 5 — Aggiungi alla Home del telefono (Android, Chrome)
1. Apri quel link in **Chrome** sul telefono.
2. Menu **⋮** (tre puntini) in alto a destra.
3. **Aggiungi a schermata Home** → **Aggiungi**.
4. Ora hai l'icona come una vera app: la apri a schermo intero.

---

## Uso
- **Scheda Screener**: scegli universo, premi **Analizza** → classifica dei
  rimbalzi da ipervenduto.
- **Scheda Backtest**: scegli anni e numero titoli, premi **Esegui** →
  grafico strategia vs S&P 500.

## Aggiornare l'app in futuro
Ti basta ricaricare `streamlit_app.py` nel repo GitHub (Add file → Upload,
sovrascrivi, Commit): Streamlit ripubblica da solo in un minuto.

---

## Note e limiti
- Il server gratuito ha memoria limitata: il **backtest S&P500 a 10 anni** può
  richiedere 1-3 minuti ed è l'operazione più pesante. Se dovesse andare in
  errore di memoria, riduci gli anni (es. 5) o usa FTSE MIB.
- L'app "dorme" dopo un po' di inattività: alla prima apertura dopo giorni può
  metterci ~30s a risvegliarsi. Normale sul piano gratuito.
- Dati Yahoo ritardati. Strumento di studio, **non è consulenza finanziaria**.
