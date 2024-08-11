import requests
import smtplib
from email.message import EmailMessage
from datetime import timedelta, datetime
import os
import pandas as pd
from dotenv import load_dotenv

# Load the environment variables
load_dotenv('./.env')
API_KEY = os.getenv("ALPHAVANTAGE")
SECTORS = {
    'Technology': 'XLK',  
    'Energy': 'XLE',
    'Financials': 'XLF', 
    'Healthcare': 'XLV', 
    'Consumer Discretionary': 'XLY',  
    'Utilities': 'XLU', 
    'Industrials': 'XLI', 
    'Materials': 'XLB'
}
BASE_URL = 'https://www.alphavantage.co/query'

def get_etf_data(symbol):
    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': symbol,
        'apikey': API_KEY,
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    if 'Time Series (Daily)' in data:
        latest_date = next(iter(data['Time Series (Daily)']))
        prev_open =  data['Time Series (Daily)'][latest_date]['1. open']
        prev_close = data['Time Series (Daily)'][latest_date]['4. close']
        prev_delta = prev_close - prev_open
        prev_delta_perc = (prev_delta/prev_open) * 100
        prev_volume = data['Time Series (Daily)'][latest_date]['5. volume']
        return float(prev_close), int(prev_volume), float(prev_delta), float(prev_delta_perc)
    else:
        print(f"Error fetching data for ETF {symbol}")
        return None, None, None, None

def main():
    end_date = datetime.now()
    
    email_body = f"Sector ETF Performance Report\n"
    email_body += f"Report generated on {end_date.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    for sector, etf in SECTORS.items():
        print(f"Fetching data for {sector} sector (ETF: {etf})...")
        close, vol, delta, delta_perc = get_etf_data(etf)
        if not close == None and not vol == None and not delta_perc == None and not deltaS == None:
            email_body += f"Data for {sector} ({etf}): Previous day close: {close}. Previous day volume: {vol}. Yesterdays price delta: {delta} ({delta_perc})\n"    
    subject = f"Sector ETF Performance Report - {end_date.strftime('%Y-%m-%d')}"
    print("Report content:")
    print(email_body)
    # send_email(subject, email_body)
    # print("Email sent successfully!")

def send_email(type, news_content):
    email_key = os.getenv("EMAILKEY")
    # Initialize the email message
    email = EmailMessage()
    email['from'] = 'Daily News Report'
    df = pd.read_csv('./Users/users.csv')
    email_list = df['emails'].values
    email['to'] = 'email_list'
    email['subject'] = f'Daily {type} Headlines'
    body = "Hello!\n\nCatch up on industry ETF performance!\n\n"
    body += news_content
    body += "\nEnjoy your personalized finance report!"
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

if __name__ == '__main__':
    main()