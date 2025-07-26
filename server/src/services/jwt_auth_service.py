"""
JWT Authentication Service for handling JWT token validation and user authentication
"""

import jwt
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class JWTAuthService:
    """Service for JWT token validation and user authentication"""

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        """
        Initialize JWT auth service
        
        Args:
            secret_key: Secret key for JWT encoding/decoding
            algorithm: JWT algorithm (default: HS256)
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        logger.info("JWT Auth Service initialized successfully")

    def validate_token_format(self, authorization: Optional[str]) -> str:
        """
        Validate authorization header format and extract token
        
        Args:
            authorization: Authorization header value
            
        Returns:
            JWT token string
            
        Raises:
            HTTPException: If authorization header is invalid
        """
        try:
            if not authorization:
                raise HTTPException(
                    status_code=401,
                    detail={"message": "Authorization header is required"}
                )
            
            if not authorization.startswith("Bearer "):
                raise HTTPException(
                    status_code=401,
                    detail={"message": "Authorization header must start with 'Bearer '"}
                )
            
            token = authorization.split(" ")[1]
            if not token:
                raise HTTPException(
                    status_code=401,
                    detail={"message": "JWT token is required"}
                )
            
            return token
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error validating token format: {e}")
            raise HTTPException(
                status_code=401,
                detail={"message": "Invalid authorization header format"}
            )

    def extract_user_info(self, token: str) -> Dict[str, Any]:
        """
        Extract user information from JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Dictionary containing user information
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            # Decode JWT token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Extract required fields
            user_id = payload.get("user_id")
            role = payload.get("role")
            
            if not user_id:
                raise HTTPException(
                    status_code=401,
                    detail={"message": "JWT token must contain 'user_id' claim"}
                )
            
            if not role:
                raise HTTPException(
                    status_code=401,
                    detail={"message": "JWT token must contain 'role' claim"}
                )
            
            # Validate role
            valid_roles = ["safety_head", "cxo", "safety_manager"]
            if role not in valid_roles:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "message": f"Invalid role: {role}",
                        "supported_roles": valid_roles
                    }
                )
            
            # Extract region for safety_manager role
            region = payload.get("region")

            # Validate region for safety_manager
            if role == "safety_manager":
                if not region:
                    raise HTTPException(
                        status_code=401,
                        detail={"message": "JWT token must contain 'region' claim for safety_manager role"}
                    )

                valid_regions = ["NR 1", "NR 2", "SR 1", "SR 2", "WR 1", "WR 2", "INFRA/TRD"]
                if region not in valid_regions:
                    raise HTTPException(
                        status_code=403,
                        detail={
                            "message": f"Invalid region: {region}",
                            "supported_regions": valid_regions
                        }
                    )

            result = {
                "user_id": user_id,
                "role": role,
                "exp": payload.get("exp"),
                "iat": payload.get("iat")
            }

            # Add region to result if present
            if region:
                result["region"] = region

            return result
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail={"message": "JWT token has expired"}
            )
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid JWT token: {e}")
            raise HTTPException(
                status_code=401,
                detail={"message": "Invalid JWT token"}
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error extracting user info from token: {e}")
            raise HTTPException(
                status_code=401,
                detail={"message": "Failed to process JWT token"}
            )

    def create_test_token(self, user_id: str, role: str, region: str = None, expires_in_hours: int = 24) -> str:
        """
        Create a test JWT token for development/testing purposes
        
        Args:
            user_id: User identifier
            role: User role (safety_head, cxo, safety_manager)
            region: Required for safety_manager role (NR 1, NR 2, SR 1, SR 2, WR 1, WR 2, INFRA/TRD)
            expires_in_hours: Token expiration time in hours
            
        Returns:
            JWT token string
            
        Raises:
            HTTPException: If role is invalid
        """
        try:
            # Validate role
            valid_roles = ["safety_head", "cxo", "safety_manager"]
            if role not in valid_roles:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "message": f"Invalid role: {role}",
                        "supported_roles": valid_roles
                    }
                )

            # Validate region for safety_manager
            if role == "safety_manager":
                if not region:
                    raise HTTPException(
                        status_code=400,
                        detail={"message": "Region is required for safety_manager role"}
                    )

                valid_regions = ["NR 1", "NR 2", "SR 1", "SR 2", "WR 1", "WR 2", "INFRA/TRD"]
                if region not in valid_regions:
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "message": f"Invalid region: {region}",
                            "supported_regions": valid_regions
                        }
                    )
            
            # Create token payload
            now = datetime.now(timezone.utc)
            payload = {
                "user_id": user_id,
                "role": role,
                "iat": now,
                "exp": now + timedelta(hours=expires_in_hours)
            }

            # Add region for safety_manager
            if role == "safety_manager" and region:
                payload["region"] = region
            
            # Generate token
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            
            logger.info(f"Generated test token for user: {user_id}, role: {role}")
            return token
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating test token: {e}")
            raise HTTPException(
                status_code=500,
                detail={"message": "Failed to create test token"}
            )

    def verify_token(self, token: str) -> bool:
        """
        Verify if a JWT token is valid
        
        Args:
            token: JWT token string
            
        Returns:
            True if token is valid, False otherwise
        """
        try:
            jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return True
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return False
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return False

    def get_token_payload(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Get the payload from a JWT token without validation
        
        Args:
            token: JWT token string
            
        Returns:
            Token payload dictionary or None if invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except Exception as e:
            logger.error(f"Error getting token payload: {e}")
            return None

    def refresh_token(self, token: str, expires_in_hours: int = 24) -> str:
        """
        Refresh a JWT token with new expiration time
        
        Args:
            token: Current JWT token
            expires_in_hours: New expiration time in hours
            
        Returns:
            New JWT token string
            
        Raises:
            HTTPException: If current token is invalid
        """
        try:
            # Extract user info from current token
            user_info = self.extract_user_info(token)
            
            # Create new token with same user info but new expiration
            region = user_info.get("region")
            return self.create_test_token(
                user_info["user_id"],
                user_info["role"],
                expires_in_hours,
                region
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise HTTPException(
                status_code=500,
                detail={"message": "Failed to refresh token"}
            )
