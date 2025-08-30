from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./watcher.db")

# # For development, use SQLite
if DATABASE_URL.startswith("postgresql://"):
    engine = create_engine(DATABASE_URL)
else:
    # Use SQLite for development
    engine = create_engine("sqlite:///./watcher.db", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Website(Base):
    __tablename__ = "websites"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
class UptimeCheck(Base):
    __tablename__ = "uptime_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    website_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status_code = Column(Integer)
    response_time = Column(Float)  # in milliseconds
    is_up = Column(Boolean)
    error_message = Column(Text, nullable=True)

# # Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#---------------------- supabase database---------------

import psycopg2
from dotenv import load_dotenv
import hashlib
import secrets

USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        dbname=DBNAME
    )

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

def generate_otp():
    """Generate 6-digit OTP"""
    return str(secrets.randbelow(1000000)).zfill(6)

def signup_user(name, email, password):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return {"success": False, "message": "Email already exists"}
        
        # Hash password and generate OTP
        passhash = hash_password(password)
        otp = generate_otp()
        otp_expiry = datetime.now() + timedelta(minutes=1 )
        
        cursor.execute("""
            INSERT INTO users (name, email, passhash, email_verified, verification_otp, otp_expiry)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (name, email, passhash, False, otp, otp_expiry))
        
        user_id = cursor.fetchone()[0]
        connection.commit()  ; cursor.close()  ; connection.close()
        
        return {
            "success": True,
            "message": "User created successfully",
            "user_id": user_id,
            "otp": otp,
            "otp_expires": otp_expiry.isoformat()
        }
        
    except Exception as e:
        return {"success": False, "message": f"Signup failed: {str(e)}"}

def login_user(email, password):
    """Login user with email and password"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Get user by email
        cursor.execute("""
            SELECT id, name, email, passhash, email_verified 
            FROM users WHERE email = %s
        """, (email,))
        
        user = cursor.fetchone()
        if not user:
            return {"success": False, "message": "User not found"}
        
        user_id, name, email, stored_hash, email_verified = user
        
        # Verify password
        if not verify_password(password, stored_hash):
            return {"success": False, "message": "Invalid password"}
        
        cursor.close()
        connection.close()
        
        return {
            "success": True,
            "message": "Login successful",
            "user": {
                "id": user_id,
                "name": name,
                "email": email,
                "email_verified": email_verified
            }
        }
        
    except Exception as e:
        return {"success": False, "message": f"Login failed: {str(e)}"}

def verify_email_otp(email, otp):
    """Verify email with OTP"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check OTP
        cursor.execute("""
            SELECT id, verification_otp, otp_expiry, email_verified
            FROM users WHERE email = %s
        """, (email,))
        
        user = cursor.fetchone()
        if not user:
            return {"success": False, "message": "User not found"}
        
        user_id, stored_otp, otp_expiry, email_verified = user
        
        if email_verified:
            return {"success": False, "message": "Email already verified"}
        
        if not stored_otp or stored_otp != otp:
            return {"success": False, "message": "Invalid OTP"}
        
        if datetime.now() > otp_expiry:
            return {"success": False, "message": "OTP expired"}
        
        # Mark email as verified
        cursor.execute("""
            UPDATE users 
            SET email_verified = TRUE, verification_otp = NULL, otp_expiry = NULL
            WHERE id = %s
        """, (user_id,))
        
        connection.commit()  ; cursor.close()  ; connection.close()
        return {"success": True, "message": "Email verified successfully"}
        
    except Exception as e:
        return {"success": False, "message": f"Verification failed: {str(e)}"}

def test_connection():
    """Test database connection"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT NOW();")
        result = cursor.fetchone()
        print("Connection successful!")
        print("Current Time:", result)
        
        cursor.close()
        connection.close()
        print("Connection closed.")
        return True
        
    except Exception as e:
        print(f"Failed to connect: {e}")
        return False
