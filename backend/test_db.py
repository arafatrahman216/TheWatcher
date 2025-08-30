import psycopg2
from dotenv import load_dotenv
import os
import hashlib
import secrets
from datetime import datetime, timedelta

# Load environment variables from .env
load_dotenv()

# Fetch variables
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
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Verify password against hash"""
    return hash_password(password) == hashed

def generate_otp():
    """Generate 6-digit OTP"""
    return str(secrets.randbelow(1000000)).zfill(6)

def signup_user(name, email, password):
    """Sign up a new user"""
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
        
        # Insert new user
        cursor.execute("""
            INSERT INTO users (name, email, passhash, email_verified, verification_otp, otp_expiry)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (name, email, passhash, False, otp, otp_expiry))
        
        user_id = cursor.fetchone()[0]
        connection.commit()
        
        cursor.close()
        connection.close()
        
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
        
        connection.commit()
        cursor.close()
        connection.close()
        
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

def test_auth_functions():
    """Test authentication functions"""
    print("\n=== Testing Authentication Functions ===")
    
    # Test signup
    print("\n1. Testing Signup...")
    signup_result = signup_user("Arafat", "arafat@gmail.com", "1234")
    print(f"Signup result: {signup_result}")
    
    if signup_result["success"]:
        otp = signup_result["otp"]
        

        # Test login
        print("\n3. Testing Login...")
        login_result = login_user("arafat@gmail.com", "1234")
        print(f"Login result: {login_result}")

        # Test email verification
        print("\n2. Testing Email Verification...")
        verify_result = verify_email_otp("arafat@gmail.com", otp)
        print(f"Verification result: {verify_result}")
        
        # Test login
        print("\n3. Testing Login...")
        login_result = login_user("arafat@gmail.com", "1234")
        print(f"Login result: {login_result}")
        
        # Test wrong password
        print("\n4. Testing Wrong Password...")
        wrong_login = login_user("arafat@gmail.com", "wrongpassword")
        print(f"Wrong password result: {wrong_login}")

if __name__ == "__main__":
    # Test connection first
    if test_connection():
        # Run authentication tests
        test_auth_functions()
        
    else:
        print("Database connection failed. Please check your .env file.")
