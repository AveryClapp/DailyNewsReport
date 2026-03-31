import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv("./.env")

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("EMAILKEY")

def send_email(to: str, subject: str, body: str) -> None:
    msg = EmailMessage()
    msg["From"] = SENDER_EMAIL
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    with smtplib.SMTP(host="smtp.gmail.com", port=587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
        smtp.send_message(msg)
