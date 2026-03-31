import os
from datetime import datetime
from newsapi.newsapi_client import NewsApiClient
from dotenv import load_dotenv
import db
from email_utils import send_email

load_dotenv("./.env")

def get_news(news_type: str) -> str:
    newsapi = NewsApiClient(api_key=os.getenv("APIKEY"))
    if news_type == "General":
        articles = newsapi.get_top_headlines(sources="associated-press")["articles"]
    elif news_type == "Business":
        articles = newsapi.get_top_headlines(category="business", country="us")["articles"]
    elif news_type == "Sports":
        articles = newsapi.get_top_headlines(category="sports", country="us")["articles"]
    else:
        raise ValueError(f"Unknown news type: {news_type}")

    lines = []
    for a in articles:
        lines.append(f"{a['title']}\n{a['description']}\n{a['url']}\n")
    return "\n".join(lines)

def build_digest(user: dict, sections: dict) -> str | None:
    parts = []
    if user["general_news"] and "General" in sections:
        parts.append("=== GENERAL NEWS ===\n" + sections["General"])
    if user["business_news"] and "Business" in sections:
        parts.append("=== BUSINESS NEWS ===\n" + sections["Business"])
    if user["sports_news"] and "Sports" in sections:
        parts.append("=== SPORTS NEWS ===\n" + sections["Sports"])
    if not parts:
        return None
    date = datetime.now().strftime("%B %d, %Y")
    header = f"Your Daily News Digest — {date}\n\n"
    return header + "\n\n".join(parts) + "\n\nEnjoy your personalized news digest!"

if __name__ == "__main__":
    print("Fetching news...")
    sections = {
        "General": get_news("General"),
        "Business": get_news("Business"),
        "Sports": get_news("Sports"),
    }
    users = db.get_all_users()
    sent = 0
    for user in users:
        body = build_digest(user, sections)
        if body:
            try:
                send_email(
                    to=user["email"],
                    subject=f"Daily News Digest — {datetime.now().strftime('%B %d, %Y')}",
                    body=body,
                )
                print(f"Sent digest to {user['email']}")
                sent += 1
            except Exception as e:
                print(f"Error sending to {user['email']}: {e}")
    print(f"Done. Sent {sent}/{len(users)} digests.")
