from fastapi import FastAPI, HTTPException
from httpcore import request
from pydantic import BaseModel, EmailStr
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
import os
from typing import Optional
from dotenv import load_dotenv
load_dotenv()

class EmailRequest(BaseModel):
    email: EmailStr
    subject: Optional[str] = "OTP Verification"

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.email = os.getenv("MAIL_FROM")
        self.password = os.getenv("MAIL_PASSWORD")
        
        # Validate required credentials
        if not self.email:
            raise ValueError("MAIL_FROM environment variable is required")
        if not self.password:
            raise ValueError("MAIL_PASSWORD environment variable is required")
            
        print(f"Email service initialized with: {self.email[:3]}***@{self.email.split('@')[1] if '@' in self.email else 'unknown'}")
        
    def send_otp_email(self, recipient_email: str, otp: str, expire: int, subject: str = "🔐 OTP Verification - The Watcher") -> bool:
        """Send OTP via email"""
        try:
            # Create HTML email body with OTP
            email_body = self.get_otp_template(otp=otp, expire=expire)

            # Use the existing send_mail method
            return self.send_mail(recipient_email, subject, email_body)
        except Exception as e:
            print(f"Error in send_otp_email: {e}")
            return False
        

    def send_mail(self, recipient_email:str, subject:str , text:str):
        try:
            # Additional validation
            if not self.email or not self.password:
                print("Error: Email credentials not properly configured")
                return False
                
            msg = MIMEMultipart()
            msg['From'] = f"The Watcher <{self.email}>"
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            body = text
            
            msg.attach(MIMEText(body, 'html'))
            
            print(f"Connecting to SMTP server: {self.smtp_server}:{self.smtp_port}")
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            
            print(f"Logging in with email: {self.email}")
            server.login(self.email, self.password)
            
            text = msg.as_string()
            server.sendmail(self.email, recipient_email, text)
            server.quit()
            
            print(f"Email sent successfully to {recipient_email}")
            return True
            
        except ValueError as e:
            print(f"Configuration error: {e}")
            return False
        except smtplib.SMTPAuthenticationError as e:
            print(f"SMTP Authentication failed: {e}")
            print("Please check your email and password, and ensure 2FA/App Password is configured")
            return False
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
        
    def get_otp_template(self, otp:str , expire: int):
        temp = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background-color: #0f0f23;
                        color: #ffffff;
                        margin: 0;
                        padding: 20px;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                        border-radius: 15px;
                        padding: 30px;
                        box-shadow: 0 8px 32px rgba(0, 255, 127, 0.1);
                        border: 1px solid rgba(0, 255, 127, 0.2);
                    }}
                    .header {{
                        text-align: center;
                        margin-bottom: 30px;
                    }}
                    .logo {{
                        font-size: 2.5em;
                        margin-bottom: 10px;
                    }}
                    .brand {{
                        font-size: 1.8em;
                        font-weight: bold;
                        color: #00ff7f;
                        margin-bottom: 20px;
                    }}
                    .greeting {{
                        font-size: 1.2em;
                        margin-bottom: 20px;
                        color : #00ff7f;
                    }}
                    .otp-container {{
                        background: rgba(0, 255, 127, 0.1);
                        border: 2px solid #00ff7f;
                        border-radius: 10px;
                        padding: 20px;
                        text-align: center;
                        margin: 20px 0;
                    }}
                    .otp-label {{
                        font-size: 1.1em;
                        margin-bottom: 10px;
                        color: #00ff7f;
                    }}
                    .otp-code {{
                        font-size: 2.5em;
                        font-weight: bold;
                        color: #00ff7f;
                        letter-spacing: 5px;
                        font-family: 'Courier New', monospace;
                    }}
                    .warning {{
                        background: rgba(255, 193, 7, 0.1);
                        border-left: 4px solid #ffc107;
                        padding: 15px;
                        margin: 20px 0;
                        border-radius: 5px;
                        color: #ffc107;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid rgba(0, 255, 127, 0.2);
                    }}
                    .signature {{
                        font-size: 1.1em;
                        color: #00ff7f;
                        font-weight: bold;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="brand">The Watcher</div>
                    </div>
                    
                    <div class="greeting">
                        👋 Hello there!
                    </div>
                    
                    <div class="otp-container">
                        <div class="otp-label">🔑 Your OTP for verification is:</div>
                        <div class="otp-code">{otp}</div>
                    </div>
                    
                    <div class="warning">
                        ⏰ <strong>Important:</strong> This OTP is valid for {expire} minutes. Please do not share this code with anyone for security reasons.
                    </div>
                    
                    <div  style="text-align: center; margin: 20px 0; color : #ffff00">
                        🛡️ Stay secure and keep watching!
                    </div>
                    
                    <div class="footer">
                        <div class="signature">
                            Best regards,<br>
                            The Watcher Team
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
        return temp


