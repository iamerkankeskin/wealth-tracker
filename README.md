# Wealth Tracker

Version: v1.0

A Django-based personal portfolio tracker.

You can track crypto, stocks, gold, and manual assets in a single dashboard, then monitor profit/loss by recording transaction history.

## Features

- Asset types: Crypto, Stock, Gold, Manual
- Automatic price updates
  - Crypto: CoinGecko
  - Stock/FX/Gold: Yahoo Finance
- Transaction history management
  - Buy
  - Sell
  - Add Quantity
  - Delete Transaction
- Profit/loss and percentage change calculations
- Portfolio summary on dashboard
- USD/TRY and EUR/TRY conversion support

## Tech Stack

- Python 3
- Django
- SQLite
- requests
- yfinance

## Installation

1. Clone the repository:

```bash
git clone <repo-url>
cd wealth
```

2. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install django requests yfinance
```

4. Apply database migrations:

```bash
python manage.py migrate
```

5. Start the development server:

```bash
python manage.py runserver
```

6. Open the app:

- http://127.0.0.1:8000/

## Usage

1. Add an asset.
2. Enter a symbol (example: BTC, ETH, TAO, AAPL).
3. Use Add Transaction on the asset detail page to enter your past buy/sell transactions.
4. Monitor total value and profit/loss from the dashboard.

## What Do Transaction Types Mean?

- Buy: Increases quantity and updates purchase price using weighted average cost.
- Sell: Decreases quantity.
- Add Quantity: Increases quantity without changing purchase price.

## Project Structure

```text
wealth/
├── config/                 # Django project settings
├── tracker/                # Main app (models, views, forms, services)
├── static/                 # CSS/JS
├── manage.py
└── db.sqlite3
```

## Notes

- This project is configured for development (DEBUG=True).
- For production, update SECRET_KEY, ALLOWED_HOSTS, and database settings.

## License

This project is intended for personal use and learning.
