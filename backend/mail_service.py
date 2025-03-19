from smtplib import SMTP, SMTPException
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_HOST = "localhost"
SMTP_PORT = 1025
SENDER_EMAIL = "23f2004759@ds.study.iitm.ac.in"
SENDER_PASSWORD = ""

def send_message(to, subject, content_body):
    """Send an email to the recipient."""
    msg = MIMEMultipart()
    msg["To"] = to 
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg.attach(MIMEText(content_body, "html"))

    try:
        client = SMTP(host=SMTP_HOST, port=SMTP_PORT)
        client.send_message(msg)
        client.quit()
        print("Email sent successfully")
    except SMTPException as e:
        print(f"Failed to send email: {e}")

