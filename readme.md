# Mitti Se Mandi

## Smart India Hackathon 2026 — Problem Statement 26132

**Strengthening Market Linkages and Price Discovery for Farmers**

Government of Maharashtra — Maharashtra State Innovation Society

---

## 1. Problem

Farmers often have limited visibility into current and expected prices across nearby markets, buyer demand, quality requirements, logistics, storage, and buyer reliability. This can reduce bargaining power and lead to weak price realization.

## 2. Solution

Mitti Se Mandi is a market-intelligence and transaction platform that:

- collects Maharashtra mandi data from Agmarknet
- shows current and nearby-market prices
- forecasts prices for the next 7 calendar days
- provides a sale-window/advisory signal
- connects farmers with suitable buyers
- supports lot creation, offers, payments, and disputes

---

## 3. Main Product Flow

```text
Farmer
  ↓
Dashboard
  ↓
Select Commodity + Market
  ↓
Current Price + Nearby Markets + 7-Day Forecast
  ↓
Advisory / Sale Window
  ↓
Find Buyer
  ↓
Create Lot
  ↓
Buyer Matching
  ↓
Digital Offer
  ↓
Payment / Transaction
  ↓
Dispute Support
```

---

## 4. Major Components

| Component | Purpose |
|---|---|
| Agmarknet Data Pipeline | Collect and update Maharashtra mandi data |
| Data Cleaning Pipeline | Convert raw data into reliable processed data |
| Price Prediction | Predict market price for the next 7 calendar days |
| Advisory | Convert forecast into a simple farmer-facing signal |
| Market Comparison | Compare prices across nearby markets |
| Buyer Matching | Match farmer lots with buyer requirements |
| Lot Management | Create and publish produce lots |
| Quality / Grading | Store and use produce quality information |
| Digital Offers | Buyer offer and farmer accept/reject flow |
| Payment Tracking | Track transaction payment status |
| Disputes | Handle transaction grievances |
| Voice Assistant | Optional speech input/output layer |
| LLM Assistant | Explain data and recommendations; not the numerical source of truth |

---

## 5. Problem Statement → Solution Mapping

| Requirement | Our Implementation |
|---|---|
| Mandi price aggregation | Agmarknet Maharashtra data pipeline |
| Localized price trends | Market + commodity price history |
| Expected price trends | Seven LightGBM forecasting models |
| Sale-window recommendation | Forecast-based advisory layer |
| Arrival information | Agmarknet arrival data |
| Buyer demand | Buyer requirements dataset / database |
| Buyer matching | Matching engine |
| Lot creation | Lot workflow |
| Quality grading | Grade / quality fields |
| Digital offers | Offer workflow |
| Logistics | Logistics/transport data layer |
| Payment tracking | Transaction/payment status |
| Dispute process | Dispute/grievance workflow |

---

## 6. Data / ML Pipeline

```text
Agmarknet API
    ↓
scraper/data.py
    ↓
scraper/update.py
    ↓
data/raw/maharashtra_prices.csv
    ↓
data/clean_and_process.py
    ↓
data/processed/df_reliable.pkl
    ↓
ml/features.py
    ↓
Saved 7 LightGBM models
    ↓
ml/predictor.py
    ↓
Flask Forecast API
```

### Current data pipeline status

- Historical Maharashtra data collected: **2021-01-01 → 2026-09-16**
- Raw records currently updated incrementally
- Processed reliable dataset regenerated after updates
- Production feature pipeline working
- Seven trained LightGBM models saved and loading successfully
- Forecast API tested successfully

### Important architecture rule

**Daily data updates do not retrain the model.**

Daily process:

```text
Scrape → Clean → Update processed data → Predict
```

Training process:

```text
Updated historical data → Train → Validate → Save new models
```

---

## 7. Current Forecasting Model

The production forecasting system uses seven separate LightGBM regressors:

```text
Model 1 → t+1
Model 2 → t+2
Model 3 → t+3
Model 4 → t+4
Model 5 → t+5
Model 6 → t+6
Model 7 → t+7
```

The predictor returns:

- current market price
- forecast date for each horizon
- predicted price for each horizon
- predicted 7-day percentage change
- advisory signal

Current advisory rule:

```text
7-day change > +10%  → HOLD
7-day change < -10%  → SELL
otherwise             → NO STRONG SIGNAL
```

The numerical prediction remains ML-driven; explanatory text can be added later through the advisory/LLM layers.

---

## 8. Backend / Frontend Plan

### Phase 1 — Data + ML ✅

- [x] Agmarknet scraper
- [x] Incremental data updater
- [x] Raw master CSV
- [x] Data cleaning / processing script
- [x] Processed reliable dataset
- [x] Feature pipeline
- [x] Seven LightGBM models
- [x] Predictor
- [x] Forecast API

### Phase 2 — Core Backend

- [x] Basic authentication
- [ ] Dashboard routes
- [ ] Market / commodity APIs
- [ ] Forecast service integration
- [ ] Advisory service
- [ ] Nearby-market comparison

### Phase 3 — Marketplace

- [ ] Farmer lot creation
- [ ] Farmer listings
- [ ] Buyer profiles / requirements
- [ ] Buyer matching
- [ ] Digital offers

### Phase 4 — Transaction Layer

- [ ] Payment status tracking
- [ ] Transaction workflow
- [ ] Dispute / grievance workflow

### Phase 5 — Intelligence / Accessibility

- [ ] Recommendation engine
- [ ] Logistics / storage suggestions
- [ ] Voice input/output
- [ ] LLM explanation layer
- [ ] Language support

### Phase 6 — UI / Deployment

- [ ] Farmer dashboard
- [ ] Buyer dashboard
- [ ] Charts and market comparison UI
- [ ] Mobile responsive UI
- [ ] Final testing
- [ ] Deployment

---

## 9. Project Structure

```text
mitti se mandi/
│
├── data/
│   ├── raw/                       # master raw scraped data
│   │   └── maharashtra_prices.csv
│   ├── processed/                 # cleaned reliable dataset
│   │   └── df_reliable.pkl
│   ├── models/                    # saved forecasting models
│   └── clean_and_process.py       # raw → processed pipeline
│
├── scraper/
│   ├── data.py                    # historical Agmarknet scraper
│   ├── update.py                  # incremental updater
│   └── check.py                   # coverage diagnostic
│
├── ml/
│   ├── features.py                # production feature engineering
│   ├── predictor.py               # loads models + produces forecast
│   └── train_forecast_model.py    # offline retraining
│
├── app/
│   ├── __init__.py                # Flask app + blueprint registration
│   ├── config.py                  # application configuration
│   │
│   ├── db/
│   │   ├── database.py            # MySQL connection
│   │   └── schema.sql             # database tables
│   │
│   ├── models/                    # application/business logic
│   │   ├── advisory_engine.py     # advisory logic
│   │   ├── forecasting_model.py   # forecast model wrapper if used
│   │   ├── matching_engine.py      # buyer/listing matching
│   │   ├── recommendation_engine.py# recommendation logic
│   │   └── llm_assistant.py       # LLM explanation layer
│   │
│   ├── routes/                    # Flask endpoints
│   │   ├── auth.py                # login/register
│   │   ├── forecast.py            # forecast endpoint
│   │   ├── advisory.py             # advisory endpoint
│   │   ├── listings.py             # farmer listings
│   │   ├── buyers.py               # buyer data
│   │   ├── matching.py             # buyer matching
│   │   ├── lots.py                 # lot management
│   │   ├── offers.py               # digital offers
│   │   ├── payments.py             # payment status
│   │   ├── disputes.py             # dispute workflow
│   │   ├── recommend.py            # recommendations
│   │   └── voice.py                # voice interface
│   │
│   ├── services/
│   │   ├── agmarknet_loader.py     # data loading helpers
│   │   ├── stt_service.py          # speech-to-text
│   │   └── tts_service.py          # text-to-speech
│   │
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   │
│   ├── templates/
│   │   ├── index.html              # home / hero
│   │   ├── login.html              # login
│   │   └── registration.html       # registration
│   │
│   └── utils/                      # reusable utilities
│
├── tests/
│   ├── test_forecasting.py         # forecast tests
│   ├── test_matching.py            # matching tests
│   └── test_offers.py              # offer-state tests
│
├── docs/
│   ├── architecture.png            # system diagram
│   ├── problem_statement.md        # PS details
│   └── feature_ps_mapping.md       # requirement mapping
│
├── run.py                          # starts Flask
├── requirements.txt
└── README.md
```

---

## 10. File-by-File Responsibilities

### Root

`run.py` — starts the Flask app.

### App

`app/__init__.py` — creates Flask app and registers blueprints.

`app/config.py` — application settings and configuration.

### Routes

`auth.py` — login and registration.

`forecast.py` — returns current price and seven-day forecast.

`advisory.py` — returns farmer-facing sale-window guidance.

`listings.py` — create/view farmer listings.

`buyers.py` — create/view buyer information and requirements.

`matching.py` — match farmer listings with buyers.

`lots.py` — create and manage produce lots.

`offers.py` — create, accept, reject, or update offers.

`payments.py` — track payment status.

`disputes.py` — create and manage dispute tickets.

`recommend.py` — market/logistics recommendations.

`voice.py` — voice input/output workflow.

### Models / Logic

`forecasting_model.py` — forecast model wrapper when application-level wrapping is needed.

`recommendation_engine.py` — recommendation calculations.

`matching_engine.py` — buyer/listing matching logic.

`advisory_engine.py` — converts price/market signals into advisory text.

`llm_assistant.py` — LLM-based explanation/interface layer.

### Database

`schema.sql` — table definitions.

`database.py` — database connection handling.

### Services

`agmarknet_loader.py` — loads processed mandi data for application use.

`stt_service.py` — speech-to-text.

`tts_service.py` — text-to-speech.

### Data / ML

`data.py` — historical Agmarknet scraper.

`update.py` — incremental scraper for new/missing dates.

`check.py` — raw-data coverage diagnostics.

`clean_and_process.py` — raw CSV → reliable processed dataset.

`features.py` — production feature engineering.

`predictor.py` — loads saved forecasting models and generates predictions.

`train_forecast_model.py` — offline model retraining.

### Tests

`test_forecasting.py` — checks forecast behavior.

`test_matching.py` — checks matching filters.

`test_offers.py` — checks offer state transitions.

---

## 11. Technology Stack

| Layer | Technology |
|---|---|
| Data | Python, pandas, NumPy |
| Scraping | Python `requests`, Agmarknet API |
| ML | LightGBM |
| Backend | Flask |
| Frontend | HTML, CSS, JavaScript |
| Database | MySQL |
| Authentication | Flask session + bcrypt |
| Deployment | To be finalized |

---

## 12. Data Source

Historical daily mandi price and arrival data for Maharashtra is collected from the Agmarknet backend API.

Current raw data covers:

```text
2021-01-01 → 2026-09-16
```

The master raw dataset is kept in:

```text
data/raw/maharashtra_prices.csv
```

The processed dataset used by the ML pipeline is:

```text
data/processed/df_reliable.pkl
```

---

## 13. Development Rule

Build in this order and avoid implementing unused modules prematurely:

```text
Data pipeline
    ↓
ML / Forecasting
    ↓
Core Backend
    ↓
Farmer Dashboard
    ↓
Market Comparison + Advisory
    ↓
Lots + Listings
    ↓
Buyer Matching
    ↓
Offers
    ↓
Payments + Disputes
    ↓
Voice / LLM / Advanced Recommendations
    ↓
UI polish + deployment
```

This README is the project's **master roadmap and architecture reference**.
