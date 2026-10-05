import smtplib
from email.mime.text import MIMEText

SENDER_EMAIL = "adityakfx99@gmail.com"
APP_PASSWORD = "okxa rnkz ghas kufr"  # Spaces automatic handle ho jayenge
RECIPIENT_EMAIL = "ayoaditya7@gmail.com"

try:
    print("🔄 Connecting to Gmail SMTP via Port 587 (TLS)...")
    server = smtplib.SMTP('smtp.gmail.com', 587, timeout=15)
    server.ehlo()
    server.starttls()
    server.ehlo()
    
    print("🔐 Logging in...")
    server.login(SENDER_EMAIL, APP_PASSWORD.replace(" ", "").strip())
    
    print("📤 Sending test email...")
    msg = MIMEText("Testing AI Analytics Agent Email System via Port 587!")
    msg['Subject'] = "🚨 Test Alert Email"
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    
    server.sendmail(SENDER_EMAIL, [RECIPIENT_EMAIL], msg.as_string())
    server.quit()
    print("✅ Success! Email sent successfully!")

except Exception as e:
    print(f"❌ Failed to send email! Error: {e}")