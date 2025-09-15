import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from dotenv import load_dotenv
from pydantic import EmailStr

load_dotenv()


class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.email = os.getenv("MAIL_FROM")
        self.password = os.getenv("MAIL_PASSWORD")

        if not self.email:
            raise ValueError("MAIL_FROM environment variable is required")
        if not self.password:
            raise ValueError("MAIL_PASSWORD environment variable is required")

        print(
            f"✅ Email service initialized with: {self.email[:3]}***@{self.email.split('@')[1]}"
        )

    def send_mail(
        self,
        recipient_email: str,
        subject: str,
        text: Optional[str] = None,
        html: Optional[str] = None,
    ) -> bool:
        """
        Send an email with optional text + HTML versions.
        """
        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = f"The Watcher <{self.email}>"
            msg["To"] = recipient_email
            msg["Subject"] = subject

            if text:
                msg.attach(MIMEText(text, "plain"))
            if html:
                msg.attach(MIMEText(html, "html"))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            server.sendmail(self.email, recipient_email, msg.as_string())
            server.quit()

            print(f"📧 Email sent successfully to {recipient_email}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ SMTP Authentication failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False
        
    def send_otp_email(self, recipient_email: str, otp: str, expire: int) -> bool:
        """Send an OTP email."""
        subject = "Your The Watcher OTP Code"
        html_content = self.get_otp_template(otp, expire)
        return self.send_mail(recipient_email, subject, html=html_content)
    

    def get_otp_template(self, otp: str, expire: int) -> str:
        """Return an HTML OTP template."""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; background:#0f0f23; color:#fff; padding:20px;">
            <div style="max-width:600px; margin:auto; background:#1a1a2e; padding:30px; border-radius:10px;">
                <h2 style="color:#00ff7f;">The Watcher</h2>
                <p>👋 Hello,</p>
                <p>Your OTP is:</p>
                <h1 style="color:#00ff7f; letter-spacing:5px;">{otp}</h1>
                <p style="color:#ffc107;">⏰ This code is valid for {expire} minutes.</p>
                <p style="margin-top:30px;">Stay secure,<br>The Watcher Team</p>
            </div>
        </body>
        </html>
        """

    