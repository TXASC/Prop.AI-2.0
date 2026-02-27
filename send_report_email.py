import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
TO_EMAIL = os.getenv("TO_EMAIL")

REPORT_PATH = "output/morning_report.csv"

def send_report():
    if not os.path.exists(REPORT_PATH):
        print("No report found.")
        return
    with open(REPORT_PATH, "r") as f:
        report_content = f.read()
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = TO_EMAIL
    msg["Subject"] = "Prop.AI Morning Report"
    body = MIMEText(report_content, "plain")
    msg.attach(body)
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, TO_EMAIL, msg.as_string())
        server.quit()
        print("Report email sent.")
    except Exception as e:
        print(f"Error sending email: {e}")

if __name__ == "__main__":
    send_report()
