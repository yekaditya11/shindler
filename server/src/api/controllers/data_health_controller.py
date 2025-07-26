"""
Data Health Controller
Handles data health assessment API requests
"""

import logging
from typing import Dict, Any
from fastapi import HTTPException

from src.services.data_health_service import DataHealthService
from src.models.data_health_models import DataHealthReport
from src.utils.response_formatter import ResponseFormatter

logger = logging.getLogger(__name__)

class DataHealthController:
    """Controller for data health assessment endpoints"""
    
    def __init__(self):
        self.data_health_service = DataHealthService()
    
    async def get_data_health_report(self, schema_type: str) -> Dict[str, Any]:
        """
        Get comprehensive data health report for a schema type
        
        Args:
            schema_type: Schema type to assess (ei_tech, srs, ni_tct, ni_tct_augmented)
            
        Returns:
            Formatted API response with complete health assessment
        """
        try:
            logger.info(f"Data health assessment requested for schema: {schema_type}")
            
            # Validate schema type
            valid_schemas = ["ei_tech", "srs", "ni_tct", "ni_tct_augmented"]
            if schema_type not in valid_schemas:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid schema type. Must be one of: {', '.join(valid_schemas)}"
                )
            
            # Perform health assessment
            health_data = self.data_health_service.assess_data_health(schema_type)
            
            # Validate response structure
            try:
                health_report = DataHealthReport(**health_data)
                logger.info(f"Data health assessment completed for {schema_type}. Overall score: {health_report.overall_health.score}")
            except Exception as validation_error:
                logger.error(f"Health report validation failed: {validation_error}")
                # Continue with raw data if validation fails
                health_report = health_data
            
            # Return formatted response
            return ResponseFormatter.success_response(
                message=f"Data health assessment completed for {schema_type}",
                body={
                    "health_report": health_report.dict() if hasattr(health_report, 'dict') else health_report,
                    "assessment_summary": {
                        "schema_type": schema_type,
                        "total_records": health_data.get("total_records", 0),
                        "overall_score": health_data.get("overall_health", {}).get("score", 0),
                        "health_grade": health_data.get("overall_health", {}).get("grade", "N/A"),
                        "critical_issues": len([
                            issue for issue in health_data.get("summary", {}).get("top_issues", [])
                            if issue.get("severity") == "high"
                        ]),
                        "assessment_timestamp": health_data.get("assessment_timestamp")
                    }
                }
            )
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"Error in data health assessment for {schema_type}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error during health assessment: {str(e)}"
            )

    async def get_data_health_report_llm(self, schema_type: str) -> Dict[str, Any]:
        """
        Get LLM-enhanced data health report for a schema type

        Args:
            schema_type: Schema type to assess (ei_tech, srs, ni_tct, ni_tct_augmented)

        Returns:
            Formatted API response with LLM-enhanced health assessment
        """
        try:
            logger.info(f"LLM-enhanced data health assessment requested for schema: {schema_type}")

            # Validate schema type
            valid_schemas = ["ei_tech", "srs", "ni_tct", "ni_tct_augmented"]
            if schema_type not in valid_schemas:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid schema type. Must be one of: {', '.join(valid_schemas)}"
                )

            # Perform LLM-enhanced health assessment
            health_data = await self.data_health_service.assess_data_health_llm(schema_type)

            # Extract LLM insights
            llm_insights = health_data.get("llm_insights", {})

            # Return formatted response with LLM enhancements
            return ResponseFormatter.success_response(
                message=f"LLM-enhanced data health assessment completed for {schema_type}",
                body={
                    "health_report": health_data,
                    "assessment_summary": {
                        "schema_type": schema_type,
                        "assessment_type": "llm_enhanced",
                        "total_records": health_data.get("total_records", 0),
                        "overall_score": health_data.get("overall_health", {}).get("score", 0),
                        "health_grade": health_data.get("overall_health", {}).get("grade", "N/A"),
                        "columns_analyzed": llm_insights.get("total_columns_analyzed", 0),
                        "dimension_selections": llm_insights.get("dimension_selections_made", 0),
                        "assessment_timestamp": health_data.get("assessment_timestamp")
                    },
                    "llm_optimization": {
                        "optimization_applied": True,
                        "intelligent_dimension_selection": True,
                        "semantic_context_used": True
                    }
                }
            )

        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"Error in LLM-enhanced data health assessment for {schema_type}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error during LLM-enhanced health assessment: {str(e)}"
            )
    


