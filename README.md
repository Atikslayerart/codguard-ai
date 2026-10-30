# CODGuard AI

CODGuard AI is a decision-support prototype that helps a D2C haircare brand reduce Cash on Delivery (COD) Return to Origin (RTO) losses without automatically cancelling genuine customer orders.

It analyzes historical COD orders, calculates an explainable risk score, recommends one of four actions, and shows the likely business impact in a dashboard.

## Actions

| Risk level | Action |
|---|---|
| Low | Ship as-is |
| Low-medium | Nudge customer to prepaid |
| Medium | Confirm order on WhatsApp |
| High | Hold for manual review |

## Features

- Cleans and validates historical order data
- Detects duplicate orders and normalizes statuses
- Scores customer, address, phone, city and order-value risk signals
- Recommends an action with plain-English reasons
- Provides an interactive WhatsApp confirmation and prepaid-nudge simulator
- Shows historical RTO patterns by city, address quality and prior RTO count
- Lets non-technical users edit thresholds in `config/rules.json`

## Tech stack

- Python
- Flask
- pandas
- HTML
- CSS
- JavaScript

## Project structure

```text
backend/
  app.py
  data_cleaning.py
  data_analysis.py
  risk_rules.py
  financial_calculator.py
  whatsapp_simulator.py

config/
  rules.json

data/
  orders_sample.csv
  cleaned_orders.csv

frontend/
  index.html
  style.css
  dashboard.js

reports/
  business_memo.md
```

## Run in under 10 minutes

### 1. Create and activate a virtual environment

From the project root:

```bash
python -m venv .venv
.venv\Scripts\activate
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Clean the dataset

```bash
cd backend
python data_cleaning.py
```

This creates:

```text
data/cleaned_orders.csv
```

### 4. Start the app

Still inside `backend`:

```bash
python app.py
```

### 5. Open the dashboard

```text
http://127.0.0.1:5000/
```

## Configuration

Edit `config/rules.json` to change:

```json
{
  "risk_thresholds": {
    "ship_as_is": 25,
    "nudge_prepaid": 45,
    "confirm_whatsapp": 70,
    "hold_review": 100
  },
  "business_rules": {
    "prepaid_discount_percent": 3,
    "confirmation_timeout_hours": 24
  }
}
```

No Python code changes are required to adjust these thresholds.

## Important limitation

This is a historical replay prototype. It does not send real WhatsApp messages, process payments, or automatically cancel orders. Financial savings shown in the dashboard are illustrative estimates, not measured intervention results.

## Documentation

- `reports/business_memo.md`: founder-facing business memo
- `DECISION_LOG.md`: engineering and product decisions
- `AI_USAGE_LOG.md`: AI use, errors found, and verification steps