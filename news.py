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
    # Initialize the newsapi client
    newsapi = NewsApiClient(api_key=key) 

    # Get the current date and the date of yesterday for the news
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    from_date_str = yesterday.strftime('%Y-%m-%d')
    to_date_str = today.strftime('%Y-%m-%d')

    # Get the top headlines from the Associated Press
    news = newsapi.get_top_headlines(sources='associated-press')
    if (type):
        # Get the top business headlines instead
        news = newsapi.get_top_headlines(category='business', country='us', language='en')

    # Get the articles from the news
    articles = news['articles']
    news_content = ""
    # Get Aggregated News Content and Return It
    for article in articles:
        news_content += f"{article['title']}\nBrief Summary: {article['description']}\n{article['url']}\n\n"
    return news_content

def send_email(type, news_content):
    email_key = os.getenv("EMAILKEY")
    # Initialize the email message
    email = EmailMessage()
    email['from'] = 'Daily News Report'
    df = pd.read_csv('./Users/users.csv')
    email_list = df['emails'].values
    email['to'] = 'email_list'
    email['subject'] = f'Daily {type} Headlines'
    body = "Hello!\n\nHere's your personalized news update!\n\n"
    body += news_content
    body += "\nEnjoy your personalized news digest!"
    email.set_content(body)
    try:
        with smtplib.SMTP(host='smtp.gmail.com', port=587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            #Enter your own information here
            smtp.login('avery.clapp@gmail.com', 'email_key')
            smtp.send_message(email)
    except Exception as e:
        print(e)

# Main Function Handling Logic of What to Send
if __name__ == '__main__':
    news = get_news(True)
    send_email('Business', news)
    news = get_news(False)
    send_email('General', news)