"""
Authentication Routes
Clean and reusable API endpoints for user authentication
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from database.database import signup_user, login_user, verify_email_otp
import logging

logger = logging.getLogger(__name__)

auth_router = APIRouter(prefix="/auth", tags=["authentication"])

class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class VerifyEmailRequest(BaseModel):
    email: EmailStr
    otp: str

class AuthResponse(BaseModel):
    success: bool
    message: str
    user: Optional[dict] = None
    user_id: Optional[int] = None
    otp: Optional[str] = None
    otp_expires: Optional[str] = None

@auth_router.post("/signup", response_model=AuthResponse)
async def signup(request: SignupRequest):
    """
    Register a new user
    """
    try:
        # Validate input
        if len(request.password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters"
            )
        
        if len(request.name.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Name must be at least 2 characters"
            )
        
        # Call database function
        result = signup_user(request.name.strip(), request.email, request.password)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        logger.info(f"User signup successful: {request.email}")
        
        return AuthResponse(
            success=True,
            message=result["message"],
            user_id=result["user_id"],
            otp=result["otp"],
            otp_expires=result["otp_expires"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during signup"
        )

@auth_router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Login user with email and password
    """
    try:
        # Call database function
        result = login_user(request.email, request.password)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result["message"]
            )
        
        logger.info(f"User login successful: {request.email}")
        
        return AuthResponse(
            success=True,
            message=result["message"],
            user=result["user"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )

@auth_router.post("/verify-email", response_model=AuthResponse)
async def verify_email(request: VerifyEmailRequest):
    """
    Verify email with OTP
    """
    try:
        # Validate OTP format
        if not request.otp.isdigit() or len(request.otp) != 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP must be 6 digits"
            )
        
        # Call database function
        result = verify_email_otp(request.email, request.otp)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        logger.info(f"Email verification successful: {request.email}")
        
        return AuthResponse(
            success=True,
            message=result["message"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during email verification"
        )

@auth_router.get("/health")
async def auth_health():
    """
    Health check for authentication service
    """
    try:
        from database import test_connection
        db_status = test_connection()
        
        return {
            "status": "healthy" if db_status else "unhealthy",
            "database_connected": db_status,
            "service": "authentication"
        }
    except Exception as e:
        logger.error(f"Auth health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "database_connected": False,
            "service": "authentication",
            "error": str(e)
        }

# Export router
__all__ = ["auth_router"]