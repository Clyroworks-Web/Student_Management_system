import os
import secrets
import smtplib
import ssl
from email.mime.text import MIMEText
from email.utils import parseaddr

from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


def generate_otp():
    return f"{secrets.randbelow(1_000_000):06d}"


def send_otp(receiver_email: str, otp: str) -> bool:
    """Send an OTP email. Returns True on success, False on failure.

    Note: this uses Gmail SMTP and requires a valid app password.
    """
    sender_email = os.getenv("GMAIL_SENDER", "").strip()
    app_password = os.getenv("GMAIL_APP_PASSWORD", "")

    if not sender_email or not app_password:
        print("Email is not configured. Set GMAIL_SENDER and GMAIL_APP_PASSWORD.")
        return False

    if parseaddr(receiver_email)[1] != receiver_email or "@" not in receiver_email:
        return False

    if len(otp) != 6 or not otp.isdigit():
        return False

    subject = "Student Management System OTP"
    body = f"Your OTP is: {otp}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        tls_context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as server:
            server.ehlo()
            server.starttls(context=tls_context)
            server.ehlo()
            server.login(sender_email, app_password)
            server.send_message(msg)
        return True
    except smtplib.SMTPAuthenticationError:
        print("Email could not be sent because the Gmail credentials are invalid.")
        return False
    except (smtplib.SMTPException, OSError):
        print("Email could not be sent because the mail service is unavailable.")
        return False


