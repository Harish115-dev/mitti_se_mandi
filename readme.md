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


go file by  file  with minimum description

run.py — starts the Flask app
app/__init__.py — creates app, loads models, registers all routes
app/config.py — stores settings (DB path, API keys, transport rate)
Routes

forecast.py — returns predicted price + history
recommend.py — ranks mandis by price minus transport cost
advisory.py — returns hold/sell suggestion
listings.py — create/view farmer listings
buyers.py — create/view buyers
matching.py — returns matching buyer-listing pairs
offers.py — create offer, accept/reject
payments.py — mark offer as paid
disputes.py — raise a dispute
lots.py — group listings into one lot
voice.py — audio in → transcribe → predict → answer → speak out
Models (logic)

forecasting_model.py — loads models, predicts price
recommendation_engine.py — distance + net-price math
matching_engine.py — filters listings/buyers by crop/qty/distance
advisory_engine.py — turns price trend into hold/sell text
llm_assistant.py — builds prompt, calls LLM
DB

schema.sql — table definitions
database.py — opens/closes DB connection
Services

agmarknet_loader.py — reads processed data, builds feature row
stt_service.py — speech-to-text
tts_service.py — text-to-speech
Utils

geo.py — distance calculation
Mock data

buyers.json — sample buyers
logistics_partners.json — sample transport options
Data

raw/ — original CSVs
processed/ — cleaned weekly dataset
scraper/agmarknet_scraper.py — pulls data from Agmarknet
config/target_crops_markets.yaml — which crops/markets to use
notebooks/ — exploration/experiments
ML

build_dataset.py — cleans + engineers features
train_forecast_model.py — trains model per crop-mandi
saved_models/ — trained model files
evaluate.py — accuracy/backtesting
Tests

test_forecasting.py — checks model output is sane
test_matching.py — checks match filter works
test_offers.py — checks offer status transitions are valid
Docs

architecture.png — system diagram
pitch_deck.pptx — presentation
problem_statement.md — official PS text
feature_ps_mapping.md — feature-to-requirement table