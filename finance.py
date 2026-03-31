import os
import requests
from datetime import datetime
from dotenv import load_dotenv
import db
from email_utils import send_email

load_dotenv("./.env")

API_KEY = os.getenv("ALPHAVANTAGE")
BASE_URL = "https://www.alphavantage.co/query"

SECTORS = {
    "Technology": "XLK",
    "Energy": "XLE",
    "Financials": "XLF",
    "Healthcare": "XLV",
    "Consumer Discretionary": "XLY",
    "Utilities": "XLU",
    "Industrials": "XLI",
    "Materials": "XLB",
}

def get_etf_data(symbol: str) -> dict | None:
    params = {"function": "TIME_SERIES_DAILY", "symbol": symbol, "apikey": API_KEY}
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    series = data.get("Time Series (Daily)")
    if not series:
        print(f"Error fetching {symbol}: {data.get('Note') or data.get('Information') or 'Unknown error'}")
        return None
    latest_date = next(iter(series))
    day = series[latest_date]
    open_price = float(day["1. open"])
    close_price = float(day["4. close"])
    delta = close_price - open_price
    delta_pct = (delta / open_price) * 100
    return {
        "close": close_price,
        "volume": int(day["5. volume"]),
        "delta": delta,
        "delta_pct": delta_pct,
    }

def build_report() -> str:
    date = datetime.now().strftime("%B %d, %Y")
    lines = [f"Sector ETF Performance Report — {date}\n"]
    for sector, etf in SECTORS.items():
        print(f"  Fetching {sector} ({etf})...")
        data = get_etf_data(etf)
        if data:
            sign = "+" if data["delta"] >= 0 else ""
            lines.append(
                f"{sector} ({etf}): "
                f"Close ${data['close']:.2f}  "
                f"Delta {sign}{data['delta']:.2f} ({sign}{data['delta_pct']:.2f}%)  "
                f"Volume {data['volume']:,}"
            )
        else:
            lines.append(f"{sector} ({etf}): data unavailable")
    return "\n".join(lines)

if __name__ == "__main__":
    print("Fetching ETF data...")
    report = build_report()
    users = [u for u in db.get_all_users() if u["finance_report"]]
    date_str = datetime.now().strftime("%B %d, %Y")
    subject = f"Sector ETF Performance Report — {date_str}"
    sent = 0
    for user in users:
        body = f"Hello!\n\nCatch up on sector ETF performance!\n\n{report}\n\nEnjoy your personalized finance report!"
        try:
            send_email(to=user["email"], subject=subject, body=body)
            print(f"Sent finance report to {user['email']}")
            sent += 1
        except Exception as e:
            print(f"Error sending to {user['email']}: {e}")
    print(f"Done. Sent {sent}/{len(users)} reports.")
