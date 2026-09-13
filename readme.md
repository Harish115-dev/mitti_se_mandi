# Market Linkage & Price Discovery Platform
### Smart India Hackathon 2026 — Problem Statement 26132
**Strengthening Market Linkages and Price Discovery for Farmers**
Government of Maharashtra — Maharashtra State Innovation Society

---

## Problem Statement Summary

Many farmers, especially smallholders and producer groups, have limited visibility of current and expected prices across nearby markets, processors, institutional buyers, and digital trading channels. Information on quality specifications, demand, logistics, storage, payment reliability, and buyer credentials is fragmented. Farmers often sell immediately after harvest due to liquidity or storage constraints, resulting in weak bargaining power. Buyers, meanwhile, struggle to aggregate consistent volumes and verify quality.

**Goal:** Build a market-intelligence and transaction-enablement platform that improves transparent price discovery and creates reliable, efficient linkages from farm gate to suitable buyers.

---

## Our Solution

A data-driven platform that aggregates real historical mandi price data (Agmarknet, Maharashtra, 2021–2026), forecasts price trends, recommends optimal sale timing, and connects farmers/FPOs with verified buyers through a structured lot → offer → payment → dispute workflow.

---

## Components We're Building

| Component | What It Does |
|---|---|
| **Price Prediction Model** | Forecasts commodity prices per market for the next 7–14 days |
| **Sale-Window Recommender** | Advises farmer to "sell now" or "wait" based on the forecast |
| **Backend API** | Serves predictions, buyer matches, and lot/offer data |
| **Frontend App** | Farmer-facing UI — select commodity/market, view trend + recommendation |
| **Buyer-Matching Module** | Matches a farmer's produce to buyer requirements (commodity, quantity, quality, location) |
| **Lot Creation + Grading** | Farmer creates a "lot" (produce batch); app assigns a quality grade |
| **Digital Offers** | Matched buyers make offers on a lot; farmer accepts/rejects |
| **Payment Tracking** | Status tracker: Pending → Paid → Disputed |
| **Dispute/Grievance System** | Farmer can raise a ticket if an issue occurs |

### Problem Statement → Solution Mapping

| PS Requirement | Our Component |
|---|---|
| Aggregates mandi prices | Agmarknet data pipeline (2021–2026, Maharashtra) |
| Buyer demand, quality requirements | Buyer dataset with requirements |
| Arrival volumes | `arrival_quantity` field from scraped data |
| Transport and storage options | Static logistics/storage partner list |
| Localised price trends & sale-window recommendations | Forecasting model + rule-based recommender |
| Matches farmers/FPOs with verified buyers | Buyer-matching module |
| Lot creation | Lot creation workflow |
| Quality grading | Reuses `grade` field already in scraped data (Faq, Grade A, etc.) |
| Digital offers | Offer accept/reject flow |
| Logistics coordination | Roadmap item — third-party logistics API integration |
| Payment tracking | Mock payment status tracker |
| Dispute or grievance processes | Ticket/flag system |

### Outcomes We're Targeting

- **Improved farmer price realisation** → sale-window recommender
- **Reduced information asymmetry** → price dashboard + trends
- **Lower transaction cost** → direct buyer matching (cuts out middlemen)
- **Stronger FPO aggregation** → lots can pool produce from multiple farmers
- **Reduced post-harvest loss** → sale-window recommender + storage suggestions
- **More reliable buyer sourcing** → verified buyer matching
- **Transparent transaction records** → payment/offer status log

---

## Build Process — Steps in Order

1. **Clean & merge** scraped CSVs into one master dataset
2. **Exploratory data analysis** — trends, seasonality, per-commodity patterns
3. **Build the forecasting model** (start with Prophet/ARIMA; XGBoost/LSTM as a stretch goal)
4. **Sale-window recommendation logic** on top of the forecast
5. **Backend API** (FastAPI) wrapping the model + buyer/lot/offer/payment logic
6. **Frontend** (React or Streamlit) — the farmer-facing dashboard
7. **Buyer-matching demo layer** — buyer dataset + filter logic
8. **Polish** — Marathi language toggle, dashboard visuals, pitch alignment

---

## Tech Stack

| Layer | Tool |
|---|---|
| Data processing | Python, pandas, numpy |
| Forecasting | Prophet or statsmodels (ARIMA); XGBoost/LSTM as stretch goal |
| Backend | FastAPI |
| Frontend | React + Tailwind, or Streamlit for speed |
| Database | SQLite (hackathon scale) |
| Data source | Agmarknet API (`api.agmarknet.gov.in`) — Maharashtra, 2021–2026 |
| Deployment | Render/Railway (backend), Vercel (frontend) |

---

## Project Structure

```
market-linkage-app/
│
├── data/
│   ├── raw/                       # daily scraped CSVs, per date
│   ├── processed/                 # cleaned, merged master dataset
│   └── scraper/
│       └── agmarknet_scraper.py   # daily-report scraping script
│
├── notebooks/
│   ├── 01_data_cleaning.ipynb
│   ├── 02_eda.ipynb
│   └── 03_model_experiments.ipynb
│
├── models/
│   ├── train_model.py             # trains per-commodity forecast models
│   ├── model_utils.py
│   └── saved_models/              # pickled/serialized trained models
│
├── backend/
│   ├── main.py                    # FastAPI app
│   ├── routes/
│   │   ├── predict.py
│   │   ├── recommend.py
│   │   ├── match_buyers.py
│   │   ├── lots.py                # lot creation + grading
│   │   ├── offers.py              # digital offer accept/reject
│   │   ├── payments.py            # mock payment status tracker
│   │   └── disputes.py            # grievance ticket system
│   ├── schemas.py
│   └── mock_data/
│       ├── buyers.json
│       └── logistics_partners.json
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.jsx
│   └── package.json
│
├── requirements.txt
├── README.md
└── .env
```

---

## Data Source

Historical daily mandi price and arrival data for Maharashtra (2021–2026), collected directly from Agmarknet's backend API (`api.agmarknet.gov.in/v1/prices-and-arrivals/market-report/daily`), covering 429 markets across the state.

**Fields collected:** date, state, district, market, commodity, variety, grade, arrival quantity, min price, max price, modal price.

---

## Status

- [x] Data collection pipeline built and tested (Maharashtra, 2021–2026)
- [ ] Data cleaning & merging
- [ ] Exploratory data analysis
- [ ] Forecasting model
- [ ] Sale-window recommendation logic
- [ ] Backend API
- [ ] Frontend dashboard
- [ ] Buyer-matching module
- [ ] Lot/offer/payment/dispute workflow




Root level
requirements.txt — pinned Python package versions (Flask, pandas, xgboost, whisper, etc.) so pip install -r requirements.txt sets up an identical environment for every teammate.
.env.example — a template listing which environment variables the app needs (API keys, DB path) without containing real secrets. Teammates copy it to .env and fill in their own values.
.gitignore — tells git which files/folders to never commit (secrets, generated data, trained models, caches).
run.py — the single command that starts the app (python run.py). Creates the Flask app via the factory in app/__init__.py and runs the dev server.
app/ — the Flask application
app/__init__.py — the "app factory." Builds the Flask app object, initializes the database, loads trained models into memory once at startup, and registers every blueprint (route file) so the app knows all its endpoints exist.
app/config.py — central settings: database file path, model directory, LLM API key, the transport-cost-per-km constant used in mandi recommendations. Change a setting here once instead of hunting through route files.
app/routes/ — one file per feature, each defines the actual URL endpoints
forecast.py — /forecast/<crop>/<mandi> (next-week price), /history/<crop>/<mandi> (past prices for the chart)
recommend.py — /recommend/<crop> — ranks nearby mandis by net price (predicted price minus transport cost)
advisory.py — /advisory/<crop>/<mandi> — "hold" or "sell now" recommendation based on price trend
listings.py — lets a farmer create/view produce listings (crop, quantity, grade, location)
buyers.py — lets a buyer register/view their crop interest and location; carries the "verified" badge
matching.py — /match/<crop> — runs the rule-based farmer-buyer matching logic
offers.py — buyer creates an offer on a listing; farmer accepts/rejects it
payments.py — updates payment status (unpaid/paid) on an accepted offer
disputes.py — lets someone raise a grievance ticket against an offer
lots.py — groups multiple farmers' same-crop-and-grade listings into one FPO-sellable "lot"
voice.py — the endpoint the voice assistant hits: takes an audio file, returns a spoken/text answer
app/models/ — the decision-making logic (not database models — "ML/business logic")
forecasting_model.py — loads the trained .pkl files from ml/saved_models/ into memory and exposes a predict() function
recommendation_engine.py — the actual net-price math (distance × transport rate, subtracted from predicted price)
matching_engine.py — the filtering logic that decides which buyers match which listings
advisory_engine.py — turns a price trend into a plain-English "hold" or "sell" suggestion
llm_assistant.py — builds the prompt sent to the LLM for the voice assistant, injecting real forecast numbers so it answers from data, not guesswork
app/db/
schema.sql — the SQL CREATE TABLE statements for listings, buyers, offers, disputes, lots — this is your entire database structure in one file
database.py — a small helper that opens/closes the SQLite connection and runs schema.sql once when the app first starts
app/services/ — code that talks to something outside your own app
agmarknet_loader.py — reads the processed price data file and builds the "latest feature row" the model needs to make one prediction
stt_service.py — sends an audio file to Whisper, gets back transcribed text
tts_service.py — sends text to a text-to-speech engine, gets back an audio file
app/utils/
geo.py — one function (haversine distance) that calculates the distance between two lat/lon points. Used by both the recommendation engine (mandi distance) and the matching engine (buyer distance).
app/mock_data/
buyers.json — a hand-written sample list of buyers (name, crop interest, location, verified status) so the demo has believable buyers without needing real signups
logistics_partners.json — a similar sample list for the "transport/logistics options" part of the problem statement, shown as static reference data rather than a live booking integration
app/templates/ and app/static/
templates/ — HTML page templates, if you render pages directly from Flask instead of building a separate frontend app
static/ — CSS, JavaScript, and generated files (like the voice assistant's spoken-response audio clips) served directly to the browser
data/ — everything data-related
data/raw/ — untouched CSV exports exactly as downloaded from Agmarknet/India Data Portal. Never edited by hand — new files just get added here.
data/processed/ — the one cleaned, feature-engineered file (weekly_features.parquet) that the training script actually reads. This is the pipeline's output, regenerated by re-running build_dataset.py.
data/scraper/agmarknet_scraper.py — a script to pull fresh price data directly from Agmarknet's site/API, if you build one, as an alternative/supplement to manually downloading CSVs.
data/config/target_crops_markets.yaml — the editable list of which crops and markets the pipeline should keep, plus any market-name aliases to merge. This is the file you change to expand coverage, instead of touching code.
data/notebooks/ — Jupyter notebooks for exploratory work: cleaning experiments, visualizing trends, trying out different model approaches before finalizing what goes into the real pipeline scripts.
ml/ — model training (offline, not called per web request)
build_dataset.py — the data pipeline: ingests raw CSVs, cleans them, filters to your configured crops/markets, aggregates to weekly, engineers features, writes the processed parquet file.
train_forecast_model.py — trains one XGBoost model per crop-mandi pair, evaluates it with a time-based train/test split, saves the result.
saved_models/ — where the trained .pkl model files land; this is what app/models/forecasting_model.py loads at app startup.
evaluate.py — a script for deeper backtesting/error analysis, useful for generating accuracy numbers and charts for your pitch deck.
tests/
test_forecasting.py — checks the forecasting model returns sane output (right shape, plausible price range) rather than crashing or returning garbage
test_matching.py — checks the matching logic actually filters correctly (right crop, enough quantity, within distance)
test_offers.py — checks the offer state machine behaves correctly (can't mark payment on a pending offer, can't accept an already-rejected offer, etc.)
docs/
architecture.png — the system diagram showing how the pieces connect
pitch_deck.pptx — your SIH presentation slides
problem_statement.md — the official SIH26132 text, kept for reference so anyone on the team can re-check requirements without hunting for the original PDF
feature_ps_mapping.md — the table mapping each feature you built to the specific line in the official problem statement it satisfies — this is what you'll actually walk judges through