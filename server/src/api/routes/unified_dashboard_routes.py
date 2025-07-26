"""
Unified Dashboard API Routes
Single endpoint that serves dashboard data for all schema types (EI Tech, SRS, NI TCT, NI TCT Augmented)
with standardized JSON response format.
"""

from fastapi import APIRouter, HTTPException, Header, Query
from typing import Dict, Any, Optional
import logging

from src.services.unified_dashboard_service import UnifiedDashboardService
from src.services.jwt_auth_service import JWTAuthService
from src.config.settings import settings
from src.utils.response_formatter import ResponseFormatter

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize services
dashboard_service = UnifiedDashboardService()
jwt_auth_service = JWTAuthService(
    secret_key=settings.jwt_secret_key,
    algorithm=settings.jwt_algorithm
)


@router.get("/dashboard/{schema_type}", response_model=Dict[str, Any])
async def get_unified_dashboard(
    schema_type: str,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    start_date: Optional[str] = Query(None, description="Start date for filtering (YYYY-MM-DD format). Defaults to 1 year ago."),
    end_date: Optional[str] = Query(None, description="End date for filtering (YYYY-MM-DD format). Defaults to today.")
) -> Dict[str, Any]:
    """
    Get unified dashboard data for specified schema type with optional date filtering

    **Path Parameters:**
    - schema_type: ei_tech, srs, ni_tct, ni_tct_augmented

    **Query Parameters:**
    - start_date: Start date for filtering (YYYY-MM-DD format). Defaults to 1 year ago.
    - end_date: End date for filtering (YYYY-MM-DD format). Defaults to today.

    **Headers:**
    - Authorization: Bearer <jwt_token>

    **JWT Token Requirements:**
    - Must contain 'user_id' and 'role' claims

    **Enhanced Features for ni_tct_augmented:**
    - Standard safety KPIs plus augmented insights
    - Weather impact analysis on incident rates
    - Employee experience and training correlations
    - Site risk assessment effectiveness
    - Workload and team dynamics analysis
    - Supported roles: safety_head, cxo, safety_manager
    - safety_manager role must also contain 'region' claim (NR 1, NR 2, SR 1, SR 2, WR 1, WR 2, INFRA/TRD)
    - Regional filtering is automatically applied for safety_manager role

    **Response Format:**
    ```json
    {
        "status_code": 200,
        "message": "Dashboard data retrieved successfully",
        "body": {
            "schema_type": "ei_tech",
            "date_range": {
                "start_date": "2024-01-15",
                "end_date": "2025-01-15"
            },
            "generated_at": "2025-01-15T10:30:00",
            "dashboard_data": {
                "total_events": {...},
                "serious_near_miss_rate": {...},
                "work_stoppage_rate": {...},
                "monthly_trends": [...],
                "high_risk_regions": [...],
                "nogo_violation_rate": {...},
                "event_type_distribution": [...],
                "repeat_locations": [...],
                "response_time_analysis": {...}
            }
        }
    }
    ```
    """
    try:
        # Validate and extract JWT token
        token = jwt_auth_service.validate_token_format(authorization)
        user_info = jwt_auth_service.extract_user_info(token)
        user_id = user_info["user_id"]
        user_role = user_info["role"]
        region = user_info.get("region")  # Optional for safety_manager role
        
        # Validate schema type
        schema_type = schema_type.lower()
        valid_schemas = ["ei_tech", "srs", "ni_tct", "ni_tct_augmented"]

        if schema_type not in valid_schemas:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid schema type: {schema_type}. Valid options: {', '.join(valid_schemas)}"
            )
        
        log_msg = f"Generating dashboard data for schema: {schema_type}, user: {user_id}, role: {user_role}"
        if region:
            log_msg += f", region: {region}"
        log_msg += f", date range: {start_date} to {end_date}"
        logger.info(log_msg)

        # Get unified dashboard data with date filtering and regional filtering
        dashboard_data = dashboard_service.get_dashboard_data(schema_type, start_date, end_date, user_role, region)

        # Add user context to response
        user_context = {
            "user_id": user_id,
            "user_role": user_role
        }
        if region:
            user_context["region"] = region
            user_context["data_scope"] = "regional"
        else:
            user_context["data_scope"] = "global"

        dashboard_data["user_context"] = user_context
        
        return ResponseFormatter.success_response(
            message=f"Dashboard data retrieved successfully for {schema_type}",
            body=dashboard_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving dashboard data for {schema_type}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while retrieving dashboard data: {str(e)}"
        )



