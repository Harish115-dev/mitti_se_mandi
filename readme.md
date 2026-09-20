**# Mitti Se Mandi**

**## Smart India Hackathon 2026 — Problem Statement 26132**

**\*\*Strengthening Market Linkages and Price Discovery for Farmers\*\***

Government of Maharashtra — Maharashtra State Innovation Society

**---**

**## 1. Problem**

Farmers often have limited visibility into current and expected prices across nearby markets, buyer demand, quality requirements, logistics, storage, and buyer reliability. This can reduce bargaining power and lead to weak price realization.

**## 2. Solution**

Mitti Se Mandi is a market-intelligence and transaction platform that:

\- collects and incrementally updates Maharashtra mandi data from Agmarknet

\- shows current and nearby-market prices

\- forecasts prices for the next 7 calendar days

\- provides a sale-window/advisory signal

\- connects farmers with suitable buyers

\- supports lot creation, offers, payments, and disputes

**---**

**## 3. Main Product Flow**

\`\`\`text

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

\`\`\`

**---**

**## 4. Major Components**

\| Component | Purpose |

\|---|---|

\| Agmarknet Data Pipeline | Collect and update Maharashtra mandi data |

\| Data Cleaning Pipeline | Convert raw data into reliable processed data |

\| Price Prediction | Predict market price for the next 7 calendar days |

\| Advisory | Convert forecast into a simple farmer-facing signal |

\| Market Comparison | Compare prices across nearby markets |

\| Buyer Matching | Match farmer lots with buyer requirements |

\| Lot Management | Create and publish produce lots |

\| Quality / Grading | Store and use produce quality information |

\| Digital Offers | Buyer offer and farmer accept/reject flow |

\| Payment Tracking | Track transaction payment status |

\| Disputes | Handle transaction grievances |

\| Voice Assistant | Optional speech input/output layer |

\| LLM Assistant | Explain data and recommendations; not the numerical source of truth |

**---**

**## 5. Problem Statement → Solution Mapping**

\| Requirement | Our Implementation |

\|---|---|

\| Mandi price aggregation | Agmarknet Maharashtra data pipeline |

\| Localized price trends | Market + commodity price history |

\| Expected price trends | Seven LightGBM forecasting models |

\| Sale-window recommendation | Forecast-based advisory layer |

\| Arrival information | Agmarknet arrival data |

\| Buyer demand | Buyer requirements dataset / database |

\| Buyer matching | Matching engine |

\| Lot creation | Lot workflow |

\| Quality grading | Grade / quality fields |

\| Digital offers | Offer workflow |

\| Logistics | Logistics/transport data layer |

\| Payment tracking | Transaction/payment status |

\| Dispute process | Dispute/grievance workflow |

**---**

**## 6. Data / ML Pipeline**

\`\`\`text

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

\`\`\`

**### Current data pipeline status**

- Historical/raw Maharashtra data collected from **2021-01-01 onward**
- Raw master CSV is updated incrementally
- Current raw CSV verified through **2026-09-17** for the latest scraped records
- Cleaned reliable dataset currently verified through **2026-09-16**
- Raw dataset contains market, commodity, arrival, grade, and price information
- Data cleaning removes invalid prices, unsupported price units, extreme values, and insufficiently long market/commodity series
- Production feature pipeline is working
- Seven LightGBM models are trained and saved
- Predictor loads all seven models successfully
- Forecast API has been integrated into the Flask farmer dashboard
- Market and commodity dropdown APIs are working
- Farmer dashboard is successfully loading live MySQL data

**### Important architecture rule**

**\*\*Daily data updates do not retrain the model.\*\***

Daily process:

\`\`\`text

Scrape → Clean → Update processed data → Predict

\`\`\`

Training process:

\`\`\`text

Updated historical data → Train → Validate → Save new models

\`\`\`

**---**

**## 7. Current Forecasting Model**

The production forecasting system uses seven separate LightGBM regressors:

\`\`\`text

Model 1 → t+1

Model 2 → t+2

Model 3 → t+3

Model 4 → t+4

Model 5 → t+5

Model 6 → t+6

Model 7 → t+7

\`\`\`

The predictor returns:

\- current market price

\- forecast date for each horizon

\- predicted price for each horizon

\- predicted 7-day percentage change

\- advisory signal

Current advisory rule:

\`\`\`text

7-day change > +10%  → HOLD

7-day change < -10%  → SELL

otherwise             → NO STRONG SIGNAL

\`\`\`

The numerical prediction remains ML-driven; explanatory text can be added later through the advisory/LLM layers.

**---**

**## 8. Backend / Frontend Plan**

**### Phase 1 — Data + ML ✅**

- [x] Agmarknet scraper
- [x] Incremental data updater
- [x] Raw master CSV
- [x] Data cleaning / processing script
- [x] Processed reliable dataset
- [x] Production feature pipeline
- [x] Seven LightGBM models
- [x] Predictor
- [x] Forecast API
- [x] Forecast integrated into farmer dashboard

### Phase 2 — Core Backend 🔄

- [x] Flask application setup
- [x] MySQL connection
- [x] User registration / login
- [x] Session-based farmer authentication
- [x] Farmer dashboard route
- [x] Market API
- [x] Commodity-by-market API
- [x] Forecast service integration
- [x] Recent-market filtering
- [ ] Advisory service as a separate backend service
- [ ] Nearby-market comparison

### Phase 3 — Farmer Marketplace 🔄

- [x] Farmer dashboard UI
- [x] My Crop Listings display
- [x] Crop database table
- [x] Add Crop Flask route
- [x] Crop data shown on dashboard
- [ ] Final Add Crop end-to-end test with multiple crops
- [ ] Farmer listings management
- [ ] Buyer profiles / requirements
- [ ] Buyer matching
- [ ] Digital offers

### Phase 4 — Transaction Layer

- [x] MySQL schema includes transactions, payments, and disputes tables
- [ ] Transaction workflow
- [ ] Payment status workflow
- [ ] Offer acceptance flow
- [ ] Dispute / grievance workflow

### Phase 5 — Intelligence / Accessibility

- [ ] Recommendation engine beyond the current forecast advisory rule
- [ ] Logistics / storage suggestions
- [ ] Voice input/output
- [ ] LLM explanation layer
- [ ] Language support

### Phase 6 — UI / Deployment 🔄

- [x] Farmer dashboard
- [x] Market prices + forecast interface
- [ ] Buyer dashboard
- [ ] Charts and advanced market comparison UI
- [ ] Mobile responsive refinement
- [ ] Full integration testing
- [ ] Deployment

**### Current working product flow**

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
Current Price + 7 Forecasted Dates + 7-Day Change
  ↓
Advisory Signal

Farmer Dashboard
  ↓
Add Crop
  ↓
Save Crop to MySQL
  ↓
My Crop Listings
```

**### Current database**

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

The marketplace/transaction tables exist in the schema, while their full workflows are still under development.

**### Current forecasting result**

The production model uses seven separate LightGBM regressors for horizons **t+1 through t+7**.

The current test evaluation showed improvement over a naive last-price baseline across all seven horizons. The aligned seven-day-path test set contains **11,492 paths**.

The current advisory rule is:

```text
7-day predicted change > +10%  → HOLD
7-day predicted change < -10%  → SELL
otherwise                       → NO STRONG SIGNAL
```

This advisory is a deterministic rule applied to the ML forecast; the model remains responsible for the numerical price prediction.

**### Data availability example**

The raw Agmarknet data can contain commodities that are not present in `df_reliable.pkl`.

For example, APMC Aatpadi has several commodities in the raw CSV, but the current reliability-cleaned dataset keeps only **Pomegranate** because the other series are too sparse or use an unsupported price unit such as `Rs./Unit`.

This means the market/commodity API intentionally exposes combinations supported by the reliable ML dataset rather than every raw record.

**---**

**## 9. Project Structure**

```text
mitti se mandi/
│
├── data/
│   ├── raw/
│   │   └── maharashtra_prices.csv
│   ├── processed/
│   │   └── df_reliable.pkl
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
│   ├── scraper/
│   │   ├── data.py
│   │   ├── update.py
│   │   └── check.py
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
│   ├── db/
│   │   ├── database.py
│   │   └── schema.sql
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── forecast.py
│   │   ├── markets.py
│   │   └── crops.py
│   ├── services/
│   │   └── market_service.py
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── templates/
│       ├── index.html
│       ├── login.html
│       ├── registration.html
│       └── farmer_dashboard.html
│
├── tests/
├── docs/
├── run.py
├── requirements.txt
└── README.md
```

**Current implementation note:** the older PHP prototype is not part of the backend architecture. The active application uses **Flask + MySQL + Jinja/HTML/CSS/JavaScript**.

**---**

**## 10. File-by-File Responsibilities**

### Root

`run.py` — starts the Flask application.

### App

`app/__init__.py` — creates the Flask app and registers blueprints.

`app/config.py` — application configuration, including MySQL settings.

### Routes

`auth.py` — registration and login.

`dashboard.py` — farmer dashboard and MySQL-backed farmer/crop data.

`forecast.py` — forecast endpoint.

`markets.py` — market and commodity API endpoints.

`crops.py` — authenticated farmer crop creation.

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

`farmer_dashboard.html` — farmer dashboard, crop listing UI, and market forecast UI.

`farmer_dashboard.js` — dashboard interactions, market/commodity loading, and forecast API calls.

`farmer_dashboard.css` — dashboard styling.

### Planned modules

Buyer matching, lots, offers, transactions, payments, disputes, recommendations, voice, and LLM explanation layers are planned next and should only be added as their workflows are implemented.

**---**

**## 11. Technology Stack**

\| Layer | Technology |

\|---|---|

\| Data | Python, pandas, NumPy |

\| Scraping | Python \`requests\`, Agmarknet API |

\| ML | LightGBM |

\| Backend | Flask |

\| Frontend | HTML, CSS, JavaScript |

\| Database | MySQL |

\| Authentication | Flask session + bcrypt |

\| Deployment | To be finalized |

**---**

**## 12. Data Source**

Historical daily mandi price and arrival data for Maharashtra is collected from the Agmarknet backend API.

Current raw data covers:

\`\`\`text

2021-01-01 → 2026-09-16

\`\`\`

The master raw dataset is kept in:

\`\`\`text

data/raw/maharashtra_prices.csv

\`\`\`

The processed dataset used by the ML pipeline is:

\`\`\`text

data/processed/df_reliable.pkl

\`\`\`

**---**

**## 13. Development Rule**

Build and verify one working layer at a time. Do not implement unused modules prematurely.

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
Add Crop / My Crops 🔄
    ↓
Buyer Requirements
    ↓
Buyer Matching
    ↓
Lots + Listings
    ↓
Offers
    ↓
Transactions + Payments
    ↓
Disputes
    ↓
Advanced Recommendations
    ↓
Voice / LLM
    ↓
UI polish + deployment
```

### Current position

**Completed and working:**

- Maharashtra Agmarknet ingestion and incremental update pipeline
- Reliable processed dataset
- Production feature engineering
- Seven LightGBM forecasting models
- Forecast predictor and Flask API
- Flask authentication
- MySQL database connection
- Farmer dashboard
- Market → commodity selection
- Seven-day forecast display
- MySQL-backed crop listing display
- Add Crop backend route

**Currently being developed:**

- Complete farmer crop-management workflow
- Buyer requirements
- Buyer matching
- Marketplace offers
- Transaction/payment/dispute workflows

This README is the project's **master roadmap and current architecture reference**. It should be updated whenever an implemented feature is verified in the working application.
