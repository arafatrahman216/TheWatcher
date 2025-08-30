"""
Authentication Service
Business logic for user authentication operations
"""

from database import signup_user, login_user, verify_email_otp, test_connection
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class AuthService:
    """Authentication service class with business logic"""
    
    @staticmethod
    def validate_signup_data(name: str, email: str, password: str) -> Dict[str, Any]:
        """Validate signup data"""
        errors = []
        
        if len(name.strip()) < 2:
            errors.append("Name must be at least 2 characters")
        
        if len(password) < 6:
            errors.append("Password must be at least 6 characters")
        
        if len(password) > 128:
            errors.append("Password too long")
        
        # Basic email validation (additional to Pydantic)
        if len(email) > 255:
            errors.append("Email too long")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    @staticmethod
    def validate_login_data(email: str, password: str) -> Dict[str, Any]:
        """Validate login data"""
        errors = []
        
        if not email.strip():
            errors.append("Email is required")
        
        if not password:
            errors.append("Password is required")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    @staticmethod
    def validate_otp(otp: str) -> Dict[str, Any]:
        """Validate OTP format"""
        errors = []
        
        if not otp.isdigit():
            errors.append("OTP must contain only digits")
        
        if len(otp) != 6:
            errors.append("OTP must be exactly 6 digits")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    @staticmethod
    def register_user(name: str, email: str, password: str) -> Dict[str, Any]:
        """
        Register a new user with validation
        """
        try:
            # Validate input
            validation = AuthService.validate_signup_data(name, email, password)
            if not validation["valid"]:
                return {
                    "success": False,
                    "message": "; ".join(validation["errors"]),
                    "errors": validation["errors"]
                }
            
            # Call database function
            result = signup_user(name.strip(), email.lower().strip(), password)
            
            if result["success"]:
                logger.info(f"User registered successfully: {email}")
            else:
                logger.warning(f"User registration failed: {email} - {result['message']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Registration service error: {str(e)}")
            return {
                "success": False,
                "message": "Registration service error",
                "error": str(e)
            }
    
    @staticmethod
    def authenticate_user(email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user with validation
        """
        try:
            # Validate input
            validation = AuthService.validate_login_data(email, password)
            if not validation["valid"]:
                return {
                    "success": False,
                    "message": "; ".join(validation["errors"]),
                    "errors": validation["errors"]
                }
            
            # Call database function
            result = login_user(email.lower().strip(), password)
            
            if result["success"]:
                logger.info(f"User authenticated successfully: {email}")
            else:
                logger.warning(f"User authentication failed: {email} - {result['message']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Authentication service error: {str(e)}")
            return {
                "success": False,
                "message": "Authentication service error",
                "error": str(e)
            }
    
    @staticmethod
    def verify_user_email(email: str, otp: str) -> Dict[str, Any]:
        """
        Verify user email with OTP validation
        """
        try:
            # Validate OTP
            validation = AuthService.validate_otp(otp)
            if not validation["valid"]:
                return {
                    "success": False,
                    "message": "; ".join(validation["errors"]),
                    "errors": validation["errors"]
                }
            
            # Call database function
            result = verify_email_otp(email.lower().strip(), otp)
            
            if result["success"]:
                logger.info(f"Email verified successfully: {email}")
            else:
                logger.warning(f"Email verification failed: {email} - {result['message']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Email verification service error: {str(e)}")
            return {
                "success": False,
                "message": "Email verification service error",
                "error": str(e)
            }
    
    @staticmethod
    def check_service_health() -> Dict[str, Any]:
        """
        Check authentication service health
        """
        try:
            db_status = test_connection()
            
            return {
                "healthy": db_status,
                "database": db_status,
                "service": "AuthService",
                "timestamp": logger.created if hasattr(logger, 'created') else None
            }
            
        except Exception as e:
            logger.error(f"Health check error: {str(e)}")
            return {
                "healthy": False,
                "database": False,
                "service": "AuthService",
                "error": str(e)
            }

# Create service instance
auth_service = AuthService()

# Export service
__all__ = ["AuthService", "auth_service"]
