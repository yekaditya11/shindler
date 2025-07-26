"""
Data Health API Routes
Endpoints for comprehensive data quality assessment
"""

from fastapi import APIRouter, Path, HTTPException
from typing import Dict, Any
import logging

from src.api.controllers.data_health_controller import DataHealthController
from src.models.data_health_models import DataHealthReport

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize controller
data_health_controller = DataHealthController()

# Health check endpoint
@router.get("/data-health/status", response_model=Dict[str, Any])
async def health_check() -> Dict[str, Any]:
    """
    **Data Health Service Status**

    Check if the data health assessment service is operational.

    **Returns:**
    - Service status
    - Available schema types
    - Supported assessment dimensions
    - API version information
    """
    return {
        "status_code": 200,
        "message": "Data Health Service is operational",
        "body": {
            "service_status": "healthy",
            "available_schemas": ["ei_tech", "srs", "ni_tct", "ni_tct_augmented"],
            "assessment_dimensions": [
                "completeness", "uniqueness", "consistency", "validity", "timeliness"
            ],
            "dimension_weights": {
                "completeness": 25,
                "uniqueness": 10,
                "consistency": 20,
                "validity": 20,
                "timeliness": 25
            },
            "api_version": "1.0",
            "endpoint": "/data-health/{schema_type}"
        }
    }

@router.get("/data-health/{schema_type}", response_model=Dict[str, Any])
async def get_comprehensive_data_health(
    schema_type: str = Path(
        ..., 
        description="Schema type to assess",
        regex="^(ei_tech|srs|ni_tct|ni_tct_augmented)$"
    )
) -> Dict[str, Any]:
    """
    **Comprehensive Data Health Assessment**
    
    Get complete data quality analysis for a specific schema type including:
    
    **Overall Health Metrics:**
    - Overall health score (0-100) and descriptive grade (Excellent, Good, Poor, Bad)
    - Five dimension scores: Completeness, Uniqueness, Consistency, Validity, Timeliness
    - Weighted scoring based on dimension importance
    
    **Column-wise Analysis:**
    - Individual assessment for every column in the schema
    - Dimension scores per column (where applicable)
    - Critical vs non-critical field identification
    - Column-specific issues and recommendations
    
    **Summary & Insights:**
    - Critical fields health summary
    - Top 5 most important data quality issues
    - Categorized recommendations (immediate, short-term, long-term)
    - Impact assessment for each issue
    
    **Supported Schema Types:**
    - `ei_tech`: EI Tech unsafe events (54 columns)
    - `srs`: SRS safety reporting (47 columns) 
    - `ni_tct`: NI TCT tracking (43 columns)
    - `ni_tct_augmented`: Enhanced NI TCT with weather/employee data (58 columns)
    
    **Quality Dimensions Explained:**
    - **Completeness (25% weight)**: Percentage of non-null values
    - **Uniqueness (20% weight)**: Percentage of unique values for key fields
    - **Consistency (20% weight)**: Format and pattern compliance
    - **Validity (20% weight)**: Business rule compliance and data correctness
    - **Timeliness (15% weight)**: Data freshness and recency
    
    **Response Structure:**
    ```json
    {
      "status_code": 200,
      "message": "Data health assessment completed",
      "body": {
        "health_report": {
          "schema_type": "ei_tech",
          "total_records": 1250,
          "overall_health": {
            "score": 85.2,
            "grade": "B+",
            "dimensions": {...}
          },
          "column_analysis": {
            "event_id": {
              "completeness": {"score": 98.5, "null_count": 19},
              "uniqueness": {"score": 85.0, "duplicate_count": 187},
              "overall_column_score": 92.1,
              "issues": ["19 missing values", "187 duplicates"],
              "recommendations": ["Fix missing event IDs"]
            }
            // ... all other columns
          },
          "summary": {
            "critical_fields": {"total": 6, "healthy": 4, "warning": 2},
            "top_issues": [...],
            "recommendations": {...}
          }
        }
      }
    }
    ```
    """
    logger.info(f"Comprehensive data health assessment requested for: {schema_type}")
    return await data_health_controller.get_data_health_report(schema_type)


@router.get("/data-health-llm/{schema_type}", response_model=Dict[str, Any])
async def get_data_health_llm(
    schema_type: str = Path(..., description="Schema type to assess", regex="^(ei_tech|srs|ni_tct|ni_tct_augmented)$")
) -> Dict[str, Any]:
    """
    **LLM-Enhanced Data Health Assessment**

    Get comprehensive data health assessment with intelligent LLM-guided dimension selection.

    **Features:**
    - LLM analyzes column descriptions to determine relevant quality dimensions
    - Intelligent skipping of irrelevant validations (e.g., uniqueness for site names)
    - Semantic-aware scoring and recommendations
    - Business context understanding for safety incident data
    - Optimized performance by checking only relevant dimensions

    **Path Parameters:**
    - `schema_type`: Type of schema to assess
      - `ei_tech`: EI Tech App unsafe events
      - `srs`: SRS (Safety Reporting System) events
      - `ni_tct`: NI TCT App unsafe events
      - `ni_tct_augmented`: Enhanced NI TCT events

    **LLM Intelligence:**
    - Analyzes descriptions like "Unique identifier for each event record" → Checks uniqueness
    - Recognizes "if applicable" fields → Allows nulls without penalty
    - Understands "Branch location where event occurred" → Validates against known branches
    - Identifies date fields → Applies temporal validation logic

    **Enhanced Response:**
    ```json
    {
      "status_code": 200,
      "message": "LLM-enhanced data health assessment completed",
      "body": {
        "health_report": {
          "assessment_type": "llm_enhanced",
          "column_analysis": {
            "event_id": {
              "dimensions_checked": ["completeness", "uniqueness", "validity"],
              "dimensions_skipped": ["consistency", "timeliness"],
              "llm_reasoning": {
                "uniqueness": "Critical - must be unique identifier",
                "consistency": "Skip - IDs don't need pattern consistency"
              }
            }
          },
          "llm_insights": {
            "optimization_percentage": 35.2,
            "intelligent_skips": {...}
          }
        }
      }
    }
    ```
    """
    logger.info(f"LLM-enhanced data health assessment requested for: {schema_type}")
    return await data_health_controller.get_data_health_report_llm(schema_type)
