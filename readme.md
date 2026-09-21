# Mitti Se Mandi

## Smart India Hackathon 2026 — Problem Statement 26132

**Strengthening Market Linkages and Price Discovery for Farmers**

Government of Maharashtra — Maharashtra State Innovation Society

---

## 1. Problem

Farmers often have limited visibility into current and expected prices across nearby markets, buyer demand, quality requirements, logistics, storage, and buyer reliability. This can reduce bargaining power and lead to weak price realization.

---

## 2. Solution

Mitti Se Mandi is a market-intelligence and transaction platform that:

* collects and incrementally updates Maharashtra mandi data from Agmarknet
* shows current market price information
* supports market and commodity selection
* forecasts prices for the next 7 calendar days
* provides a sale-window/advisory signal
* connects farmers with suitable buyers
* supports buyer requirements and matching
* supports lot creation and publishing
* supports digital offers
* creates marketplace transactions after accepted offers
* supports Razorpay Test Mode payment processing and payment verification
* tracks transaction and payment status
* provides a foundation for dispute and grievance handling

---

## 3. Main Product Flow

```text
Farmer
   ↓
Login / Registration
   ↓
Farmer Dashboard
   ↓
Market Prices
   ↓
Select Commodity + Market
   ↓
Current Price + 7-Day Forecast
   ↓
Advisory / Sale Window
   ↓
Find Buyer
   ↓
Create / Publish Lot
   ↓
Buyer Matching
   ↓
Digital Offer
   ↓
Offer Acceptance
   ↓
Transaction Created
   ↓
Buyer My Orders
   ↓
Payment
   ↓
Razorpay Test Mode
   ↓
Payment Verification
   ↓
Transaction Confirmed
   ↓
Dispute Support
```

---

## 4. Major Components

| Component               | Purpose                                                             |
| ----------------------- | ------------------------------------------------------------------- |
| Agmarknet Data Pipeline | Collect and update Maharashtra mandi data                           |
| Data Cleaning Pipeline  | Convert raw data into reliable processed data                       |
| Price Prediction        | Predict market price for the next 7 calendar days                   |
| Advisory                | Convert forecast into a simple farmer-facing signal                 |
| Market Comparison       | Compare market price information                                    |
| Buyer Requirements      | Store buyer crop, quantity, grade, location and price requirements  |
| Buyer Matching          | Match farmer lots with buyer requirements                           |
| Lot Management          | Create and publish produce lots                                     |
| Listings                | Make published lots available to buyers                             |
| Quality / Grading       | Store and use produce quality information                           |
| Digital Offers          | Buyer offer and farmer accept/reject workflow                       |
| Transaction Management  | Create and track marketplace transactions                           |
| Payment Integration     | Razorpay Test Mode payment creation and verification                |
| Payment Tracking        | Track payment status and transaction confirmation                   |
| Disputes                | Planned transaction grievance workflow                              |
| Voice Assistant         | Optional speech input/output layer                                  |
| LLM Assistant           | Explain data and recommendations; not the numerical source of truth |

---

## 5. Problem Statement → Solution Mapping

| Requirement                | Our Implementation                       |
| -------------------------- | ---------------------------------------- |
| Mandi price aggregation    | Agmarknet Maharashtra data pipeline      |
| Localized price trends     | Market + commodity price history         |
| Expected price trends      | Seven LightGBM forecasting models        |
| Sale-window recommendation | Forecast-based advisory layer            |
| Arrival information        | Agmarknet arrival data                   |
| Buyer demand               | Buyer requirements database              |
| Buyer matching             | Matching engine                          |
| Lot creation               | Lot workflow                             |
| Quality grading            | Grade / quality fields                   |
| Digital offers             | Offer workflow                           |
| Logistics                  | Planned logistics / transport data layer |
| Payment tracking           | Transaction + payment status workflow    |
| Online payment             | Razorpay Test Mode integration           |
| Payment verification       | Razorpay signature verification          |
| Dispute process            | Dispute/grievance workflow planned next  |

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
      ↓
Farmer Dashboard
```

### Current data pipeline status

* Historical/raw Maharashtra data collected from **2021-01-01 onward**
* Raw master CSV is updated incrementally
* Current raw CSV was verified through **2026-09-17** for the latest scraped records
* Cleaned reliable dataset was verified through **2026-09-16**
* Raw dataset contains market, commodity, arrival, grade, and price information
* Data cleaning removes invalid prices, unsupported price units, extreme values, and insufficiently long market/commodity series
* Production feature pipeline is working
* Seven LightGBM models are trained and saved
* Predictor loads all seven models successfully
* Forecast API has been integrated into the Flask farmer dashboard
* Market and commodity dropdown APIs are working
* Farmer dashboard is loading live MySQL data
* Buyer and marketplace workflows are integrated with the Flask application

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

* current market price
* forecast date for each horizon
* predicted price for each horizon
* predicted 7-day percentage change
* advisory signal

Current advisory rule:

```text
7-day change > +10%  → HOLD

7-day change < -10%  → SELL

otherwise             → NO STRONG SIGNAL
```

The numerical prediction remains ML-driven. The advisory is a deterministic rule applied to the forecast.

The LLM layer, when added, should explain the numerical output rather than replace the ML model as the numerical source of truth.

---

## 8. Backend / Frontend Plan

### Phase 1 — Data + ML ✅

* [x] Agmarknet scraper
* [x] Incremental data updater
* [x] Raw master CSV
* [x] Data cleaning / processing script
* [x] Processed reliable dataset
* [x] Production feature pipeline
* [x] Seven LightGBM models
* [x] Predictor
* [x] Forecast API
* [x] Forecast integrated into farmer dashboard

### Phase 2 — Core Backend ✅ / 🔄

* [x] Flask application setup
* [x] MySQL connection
* [x] User registration / login
* [x] Session-based authentication
* [x] Farmer dashboard route
* [x] Buyer dashboard route
* [x] Market API
* [x] Commodity-by-market API
* [x] Forecast service integration
* [x] Recent-market filtering
* [ ] Advisory service as a separate backend service
* [ ] Advanced nearby-market comparison

### Phase 3 — Farmer Marketplace ✅

* [x] Farmer dashboard UI
* [x] My Crop Listings display
* [x] Crop database table
* [x] Add Crop Flask route
* [x] Crop data shown on dashboard
* [x] Lot creation
* [x] Lot publishing
* [x] Listing creation
* [x] Buyer requirements
* [x] Buyer requirement matching
* [x] Digital offers
* [x] Offer accept / reject workflow
* [x] Buyer offers page
* [x] Farmer offers page
* [ ] Final multi-crop end-to-end testing refinement

### Phase 4 — Transaction Layer 🔄

* [x] MySQL schema includes transactions, payments, and disputes tables
* [x] Transaction creation after accepted offer
* [x] Buyer orders page
* [x] Farmer sales/orders page
* [x] Transaction status tracking
* [x] Payment record creation
* [x] Razorpay Test Mode integration
* [x] Razorpay order creation
* [x] Razorpay order reuse validation
* [x] Razorpay payment checkout
* [x] Razorpay signature verification
* [x] Payment status update
* [x] Transaction confirmation after successful payment
* [x] High-value Razorpay payment handling
* [ ] Dispute / grievance workflow

### Phase 5 — Intelligence / Accessibility

* [ ] Recommendation engine beyond the current forecast advisory rule
* [ ] Logistics / storage suggestions
* [ ] Voice input/output
* [ ] LLM explanation layer
* [ ] Language support

### Phase 6 — UI / Deployment 🔄

* [x] Farmer dashboard
* [x] Buyer dashboard
* [x] Market prices + forecast interface
* [x] Buyer requirements interface
* [x] Buyer matching interface
* [x] Offers interface
* [x] Orders / transactions interface
* [x] Payment checkout interface
* [ ] Charts and advanced market comparison UI
* [ ] Mobile responsive refinement
* [ ] Full integration testing
* [ ] Deployment

---

## Current Working Product Flow

```text
Farmer
  ↓
Login / Registration
  ↓
Farmer Dashboard
  ↓
Market Prices
  ↓
Select Market
  ↓
Select Commodity
  ↓
7-Day LightGBM Forecast
  ↓
Current Price + 7 Forecasted Dates
  ↓
7-Day Price Change
  ↓
Advisory Signal
  ↓
Add Crop
  ↓
My Crops
  ↓
Create / Publish Lot
  ↓
Find Buyers
  ↓
Buyer Requirement Matching
  ↓
Buyer Makes Offer
  ↓
Farmer Accepts Offer
  ↓
Transaction Created
  ↓
Buyer My Orders
  ↓
Pay Now
  ↓
Razorpay Test Mode
  ↓
Payment Signature Verification
  ↓
Payment = Paid
  ↓
Transaction = Confirmed
```

---

## Current Database

The Flask/MySQL application currently uses these core tables:

```text
users

crops

lots

buyer_requirements

listings

offers

transactions

payments

disputes
```

### Marketplace relationship

```text
Farmer
  ↓
Crop
  ↓
Lot
  ↓
Listing
  ↓
Buyer Requirement Matching
  ↓
Offer
  ↓
Accepted Offer
  ↓
Transaction
  ↓
Payment
```

### Current transaction/payment flow

```text
Accepted Offer
      ↓
Transaction Created
      ↓
Payment Record Created
      ↓
Buyer Opens My Orders
      ↓
Pay Now
      ↓
Razorpay Order
      ↓
Razorpay Checkout
      ↓
Payment
      ↓
Server-side Signature Verification
      ↓
payments.status = paid
      ↓
transactions.status = confirmed
```

The `disputes` table is already present in the schema, while the full dispute/grievance interface and workflow remain to be implemented.

---

## Current Forecasting Result

The production model uses seven separate LightGBM regressors for horizons **t+1 through t+7**.

The current test evaluation showed improvement over a naive last-price baseline across all seven horizons.

The aligned seven-day-path test set contains **11,492 paths**.

The current advisory rule is:

```text
7-day predicted change > +10%  → HOLD

7-day predicted change < -10%  → SELL

otherwise                       → NO STRONG SIGNAL
```

This advisory is a deterministic rule applied to the ML forecast; the model remains responsible for the numerical price prediction.

---

## Data Availability Example

The raw Agmarknet data can contain commodities that are not present in `df_reliable.pkl`.

For example, APMC Aatpadi has several commodities in the raw CSV, but the current reliability-cleaned dataset keeps only **Pomegranate** because the other series are too sparse or use an unsupported price unit such as `Rs./Unit`.

This means the market/commodity API intentionally exposes combinations supported by the reliable ML dataset rather than every raw record.

---

## 9. Project Structure

```text
mitti se mandi/
│
├── data/
│   ├── raw/
│   │   └── maharashtra_prices.csv
│   │
│   ├── processed/
│   │   └── df_reliable.pkl
│   │
│   ├── models/
│   │   ├── lightgbm_7day_1d.txt
│   │   ├── lightgbm_7day_2d.txt
│   │   ├── lightgbm_7day_3d.txt
│   │   ├── lightgbm_7day_4d.txt
│   │   ├── lightgbm_7day_5d.txt
│   │   ├── lightgbm_7day_6d.txt
│   │   ├── lightgbm_7day_7d.txt
│   │   ├── feature_cols_7day.json
│   │   └── decision_config_7day.json
│   │
│   ├── scraper/
│   │   ├── data.py
│   │   ├── update.py
│   │   └── check.py
│   │
│   └── clean_and_process.py
│
├── ml/
│   ├── __init__.py
│   ├── features.py
│   ├── predictor.py
│   └── train_forecast_model.py
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   │
│   ├── db/
│   │   ├── database.py
│   │   └── schema.sql
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── forecast.py
│   │   ├── markets.py
│   │   ├── crops.py
│   │   ├── lots.py
│   │   ├── offers.py
│   │   ├── buyer_requirements.py
│   │   ├── transactions.py
│   │   └── payments.py
│   │
│   ├── services/
│   │   └── market_service.py
│   │
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   │
│   └── templates/
│       ├── index.html
│       ├── login.html
│       ├── registration.html
│       ├── farmer_dashboard.html
│       ├── buyer_dashboard.html
│       ├── farmer_buyer_requirements.html
│       ├── farmer_offers.html
│       ├── buyer_offers.html
│       ├── farmer_transactions.html
│       ├── buyer_transactions.html
│       └── payment_checkout.html
│
├── tests/
├── docs/
├── run.py
├── requirements.txt
└── README.md
```

**Current implementation note:** the older PHP prototype is not part of the backend architecture. The active application uses **Flask + MySQL + Jinja/HTML/CSS/JavaScript**.

---

## 10. File-by-File Responsibilities

### Root

`run.py` — starts the Flask application.

### App

`app/__init__.py` — creates the Flask app and registers blueprints.

`app/config.py` — application configuration, including MySQL settings.

### Routes

`auth.py` — registration, login and logout.

`dashboard.py` — farmer and buyer dashboards and MySQL-backed application data.

`forecast.py` — forecast endpoint.

`markets.py` — market and commodity API endpoints.

`crops.py` — authenticated farmer crop creation.

`lots.py` — lot creation and publishing.

`offers.py` — buyer offer creation and farmer accept/reject workflow.

`buyer_requirements.py` — buyer requirements and farmer-side matching.

`transactions.py` — buyer and farmer transaction/order pages.

`payments.py` — Razorpay order creation, checkout support, payment signature verification and payment status updates.

### Services

`market_service.py` — loads the processed market dataset and provides recent markets and commodities.

### Database

`schema.sql` — application database tables.

`database.py` — MySQL connection handling.

### Data / ML

`data.py` — historical Agmarknet scraper.

`update.py` — incremental scraper for new/missing dates.

`check.py` — raw-data coverage diagnostics.

`clean_and_process.py` — raw CSV → reliable processed dataset.

`features.py` — production feature engineering used by inference.

`predictor.py` — loads all seven saved LightGBM models and generates the seven-day forecast.

`train_forecast_model.py` — offline model training/retraining.

### Frontend

`farmer_dashboard.html` — farmer dashboard, crop listing UI, market and forecast UI.

`farmer_dashboard.js` — dashboard interactions, market/commodity loading and forecast API calls.

`farmer_dashboard.css` — farmer dashboard styling.

`buyer_dashboard.html` — buyer dashboard, requirements and marketplace navigation.

`buyer_offers.html` — buyer-side offer tracking.

`farmer_offers.html` — farmer-side received offer management.

`buyer_transactions.html` — buyer order and payment tracking.

`farmer_transactions.html` — farmer sales and transaction tracking.

`payment_checkout.html` — Razorpay payment checkout interface.

### Planned modules

Disputes, advanced recommendations, logistics/storage, voice, LLM explanation, language support and final deployment remain planned.

---

## 11. Technology Stack

| Layer                     | Technology                              |
| ------------------------- | --------------------------------------- |
| Data                      | Python, pandas, NumPy                   |
| Scraping                  | Python `requests`, Agmarknet API        |
| ML                        | LightGBM                                |
| Backend                   | Flask                                   |
| Frontend                  | HTML, CSS, JavaScript, Jinja            |
| Database                  | MySQL                                   |
| Authentication            | Flask session + bcrypt                  |
| Payments                  | Razorpay Python SDK / Razorpay Checkout |
| Environment Configuration | python-dotenv                           |
| Deployment                | To be finalized                         |

---

## 12. Data Source

Historical daily mandi price and arrival data for Maharashtra is collected from the Agmarknet backend API.

Current raw data coverage:

```text
2021-01-01 → latest verified raw records: 2026-09-17
```

The master raw dataset is kept in:

```text
data/raw/maharashtra_prices.csv
```

The processed dataset used by the ML pipeline is:

```text
data/processed/df_reliable.pkl
```

The cleaned reliable dataset is currently verified through:

```text
2026-09-16
```

---

## 13. Development Rule

Build and verify one working layer at a time.

Do not implement unused modules prematurely.

```text
Data pipeline ✅
    ↓
ML / Forecasting ✅
    ↓
Flask + MySQL Core Backend ✅
    ↓
Farmer Dashboard ✅
    ↓
Market + Commodity APIs ✅
    ↓
7-Day Forecast UI ✅
    ↓
Crop Management ✅
    ↓
Buyer Requirements ✅
    ↓
Buyer Matching ✅
    ↓
Lots + Listings ✅
    ↓
Offers ✅
    ↓
Transactions ✅
    ↓
Payments ✅
    ↓
Disputes ⏳
    ↓
Advanced Recommendations
    ↓
Logistics / Storage
    ↓
Voice / LLM
    ↓
UI polish + deployment
```

### Current Position

**Completed and working:**

* Maharashtra Agmarknet ingestion and incremental update pipeline
* Reliable processed dataset
* Production feature engineering
* Seven LightGBM forecasting models
* Forecast predictor and Flask API
* Flask authentication
* MySQL database connection
* Farmer dashboard
* Buyer dashboard
* Market → commodity selection
* Seven-day forecast display
* MySQL-backed crop listing display
* Add Crop backend route
* Lot creation and publishing
* Buyer requirements
* Buyer requirement matching
* Digital offers
* Offer accept / reject workflow
* Buyer offers page
* Farmer offers page
* Transaction creation
* Buyer orders page
* Farmer transactions/sales page
* Razorpay Test Mode integration
* Razorpay order creation
* Razorpay Checkout
* Razorpay signature verification
* Payment status tracking
* Transaction confirmation after successful payment
* High-value payment handling for transactions above the Razorpay online limit

**Currently being developed:**

* Dispute / grievance workflow
* Advanced nearby-market comparison
* Recommendation engine
* Logistics / storage suggestions
* Voice / LLM accessibility layer
* Language support
* Full integration testing
* Deployment

This README is the project's **master roadmap and current architecture reference**. It should be updated whenever an implemented feature is verified in the working application.
