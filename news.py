import requests
import smtplib
from email.message import EmailMessage
from newsapi.newsapi_client import NewsApiClient
from datetime import timedelta, datetime
import os
import pandas as pd
from dotenv import load_dotenv

# Load the environment variables
load_dotenv('./.env')

def get_news(type):
    key = os.getenv('APIKEY')
    newsapi = NewsApiClient(api_key=key) 

    today = datetime.now()
    yesterday = today - timedelta(days=1)
    from_date_str = yesterday.strftime('%Y-%m-%d')
    to_date_str = today.strftime('%Y-%m-%d')

    if type == 'General':
        news = newsapi.get_top_headlines(sources='associated-press')
    elif type == 'Business':
        news = newsapi.get_top_headlines(category='business', country='us', language='en')
    elif type == 'Sports':
        news = newsapi.get_top_headlines(category='sports', country='us', language='en')
    else:
        raise ValueError("Invalid news type")

    articles = news['articles']
    news_content = ""
    for article in articles:
        news_content += f"{article['title']}\nBrief Summary: {article['description']}\n{article['url']}\n\n"
    return news_content

def send_email(type, news_content):
    email_key = os.getenv("EMAILKEY")
    df = pd.read_csv('./Users/users.csv')
    
    for _, user in df.iterrows():
        if (type == 'General' and user['general_news']) or \
           (type == 'Business' and user['business_news']) or \
           (type == 'Sports' and user['sports_news']):
            email = EmailMessage()
            email['from'] = 'Daily News Report'
            email['to'] = user['email']
            email['subject'] = f'Daily {type} Headlines'
            body = f"Hello!\n\nHere's your personalized {type.lower()} news update!\n\n"
            body += news_content
            body += "\nEnjoy your personalized news digest!"
            email.set_content(body)
            
            try:
                with smtplib.SMTP(host='smtp.gmail.com', port=587) as smtp:
                    smtp.ehlo()
                    smtp.starttls()
                    smtp.login('avery.clapp@gmail.com', email_key)
                    smtp.send_message(email)
                print(f"Sent {type} news to {user['email']}")
            except Exception as e:
                print(f"Error sending email to {user['email']}: {e}")

if __name__ == '__main__':
    general_news = get_news('General')
    send_email('General', general_news)
    business_news = get_news('Business')
    send_email('Business', business_news)
    sports_news = get_news('Sports')
    send_email('Sports', sports_news)