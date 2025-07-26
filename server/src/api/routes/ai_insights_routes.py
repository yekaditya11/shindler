"""
AI Insights routes for role-based safety insights generation with JWT authentication
"""

from fastapi import APIRouter, Header, HTTPException, Depends, Body
from typing import Dict, Any, Optional
import logging
from sqlalchemy.orm import Session

from src.api.controllers.ai_insights_controller import AIInsightsController
from src.services.jwt_auth_service import JWTAuthService
from src.config.settings import settings
from src.config.database import get_db
from src.models.base_models import InsightFeedbackCreate


logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize controller and JWT service
ai_insights_controller = AIInsightsController()
jwt_auth_service = JWTAuthService(
    secret_key=settings.jwt_secret_key,
    algorithm=settings.jwt_algorithm
)


@router.post("/insights/generate/{schema_type}", response_model=Dict[str, Any])
async def generate_ai_insights(
    schema_type: str,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate AI-powered safety insights using JWT authentication

    **Path Parameters:**
    - schema_type: srs, ei_tech, ni_tct, ni_tct_augmented

    **Headers:**
    - Authorization: Bearer <jwt_token>

    **JWT Token Requirements:**
    - Must contain 'user_id' and 'role' claims
    - Supported roles: safety_head, cxo, safety_manager
    - safety_manager role must also contain 'region' claim (NR 1, NR 2, SR 1, SR 2, WR 1, WR 2, INFRA/TRD)

    **Enhanced Features for ni_tct_augmented:**
    - Weather impact analysis on safety incidents
    - Employee experience and training effectiveness insights
    - Site risk assessment correlations
    - Workload and team dynamics analysis
    """
    try:
        # Validate and extract JWT token
        token = jwt_auth_service.validate_token_format(authorization)

        # Extract user information from JWT
        user_info = jwt_auth_service.extract_user_info(token)
        user_id = user_info["user_id"]
        user_role = user_info["role"]
        region = user_info.get("region")  # Optional for safety_manager role

        # Convert to lowercase for consistency
        schema_type = schema_type.lower()

        # Generate insights using controller
        result = await ai_insights_controller.generate_insights(schema_type, user_role, user_id, db, region)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        raise HTTPException(
            status_code=500,
            detail={"message": f"Internal server error: {str(e)}"}
        )


@router.post("/insights/generate-more/{schema_type}", response_model=Dict[str, Any])
async def generate_more_ai_insights(
    schema_type: str,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate 5 additional AI-powered safety insights that are different from previously generated ones

    **Path Parameters:**
    - schema_type: srs, ei_tech, ni_tct, ni_tct_augmented

    **Headers:**
    - Authorization: Bearer <jwt_token>

    **JWT Token Requirements:**
    - Must contain 'user_id' and 'role' claims
    - Supported roles: safety_head, cxo, safety_manager
    - safety_manager role must also contain 'region' claim (NR 1, NR 2, SR 1, SR 2, WR 1, WR 2, INFRA/TRD)

    **Note:** Always generates exactly 5 additional insights
    **Enhanced for ni_tct_augmented:** Includes weather, employee, site risk, and workload correlations
    """
    try:
        # Validate and extract JWT token
        token = jwt_auth_service.validate_token_format(authorization)

        # Extract user information from JWT
        user_info = jwt_auth_service.extract_user_info(token)
        user_id = user_info["user_id"]
        user_role = user_info["role"]
        region = user_info.get("region")  # Optional for safety_manager role

        # Convert to lowercase for consistency
        schema_type = schema_type.lower()

        # Always generate 5 additional insights
        count = 5

        # Generate additional insights using controller
        result = await ai_insights_controller.generate_more_insights(
            schema_type, user_role, user_id, count, db, region
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating additional insights: {e}")
        raise HTTPException(
            status_code=500,
            detail={"message": f"Internal server error: {str(e)}"}
        )


@router.post("/auth/generate-test-token", response_model=Dict[str, Any])
async def generate_test_token(
    user_id: str,
    role: str = "safety_head",
    region: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a test JWT token for development/testing purposes

    **Query Parameters:**
    - user_id: User identifier (e.g., "user123")
    - role: User role (safety_head, cxo, safety_manager) - defaults to "safety_head"
    - region: Required for safety_manager role (NR 1, NR 2, SR 1, SR 2, WR 1, WR 2, INFRA/TRD)

    **Examples:**
    - Default role: POST /auth/generate-test-token?user_id=user123
    - Specific role: POST /auth/generate-test-token?user_id=head123&role=safety_head
    - Regional: POST /auth/generate-test-token?user_id=mgr_nr1&role=safety_manager&region=NR%201
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

        # Generate test token with region support
        token = jwt_auth_service.create_test_token(user_id, role, region)

        response_body = {
            "user_id": user_id,
            "role": role,
            "token": token,
            "authorization_header": f"Bearer {token}",
            "usage": "Include 'Authorization: Bearer <token>' in your request headers"
        }

        # Add region to response if provided
        if region:
            response_body["region"] = region

        return {
            "status_code": 200,
            "message": "Test JWT token generated successfully",
            "body": response_body
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating test token: {e}")
        raise HTTPException(
            status_code=500,
            detail={"message": f"Internal server error: {str(e)}"}
        )


@router.post("/insights/feedback", response_model=Dict[str, Any])
async def submit_insight_feedback(
    feedback: InsightFeedbackCreate = Body(...),
    authorization: Optional[str] = Header(None, alias="Authorization"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Submit like/dislike feedback for an AI-generated insight.

    **Body:**
    - schema_type: srs, ei_tech, ni_tct, ni_tct_augmented
    - insight_text: The text of the insight being rated
    - feedback: 'like' or 'dislike'

    **Headers:**
    - Authorization: Bearer <jwt_token>
    """
    try:
        # Validate and extract JWT token
        token = jwt_auth_service.validate_token_format(authorization)
        user_info = jwt_auth_service.extract_user_info(token)
        user_id = user_info["user_id"]
        # Store feedback
        result = ai_insights_controller.submit_insight_feedback(user_id, feedback.model_dump(), db)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail={"message": f"Internal server error: {str(e)}"}
        )


@router.post("/insights/generate-unified", response_model=Dict[str, Any])
async def generate_unified_ai_insights(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate AI-powered safety insights from ALL 3 data sources combined (SRS + EI Tech + NI TCT)

    This endpoint combines the most important KPIs from all 3 safety data sources to provide
    comprehensive insights while managing token limits by selecting only essential metrics.

    **Headers:**
    - Authorization: Bearer <jwt_token>

    **JWT Token Requirements:**
    - Must contain 'user_id' and 'role' claims
    - Supported roles: safety_head, cxo, safety_manager
    - safety_manager role must also contain 'region' claim (NR 1, NR 2, SR 1, SR 2, WR 1, WR 2, INFRA/TRD)

    **Data Sources Included:**
    - SRS (Safety Reporting System)
    - EI Tech (Equipment Installation Technology)
    - NI TCT (Non-Intrusive Testing)

    **Key Benefits:**
    - Comprehensive view across all safety data
    - Token-optimized by selecting only essential KPIs
    - No data loss of critical safety information
    - Cross-source pattern detection
    """
    try:
        # Validate and extract JWT token
        token = jwt_auth_service.validate_token_format(authorization)

        # Extract user information from JWT
        user_info = jwt_auth_service.extract_user_info(token)
        user_id = user_info["user_id"]
        user_role = user_info["role"]
        region = user_info.get("region")  # Optional for safety_manager role

        # Generate unified insights using controller
        result = await ai_insights_controller.generate_unified_insights(user_role, user_id, db, region)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating unified insights: {e}")
        raise HTTPException(
            status_code=500,
            detail={"message": f"Internal server error: {str(e)}"}
        )










