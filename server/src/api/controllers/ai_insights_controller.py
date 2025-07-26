"""
AI Insights controller for role-based safety insights generation
"""

from fastapi import HTTPException
from typing import Dict, Any, List
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from src.models.base_models import InsightFeedback

from src.services.ai_insights_service import AIInsightsService
from src.services.feedback_analysis_service import FeedbackAnalysisService
from src.services.unified_kpi_service import UnifiedKPIService
from src.analytics.srs_kpi_queries import SRSKPIQueries
from src.analytics.ei_tech_kpi_queries import EITechKPIQueries
from src.analytics.ni_tct_kpi_queries import NITCTKPIQueries
from src.analytics.regional_kpi_queries import execute_regional_kpis

logger = logging.getLogger(__name__)


class AIInsightsController:
    """Controller for AI-powered safety insights generation"""

    def __init__(self):
        self.ai_service = AIInsightsService()
        self.feedback_service = FeedbackAnalysisService()
        self.unified_kpi_service = UnifiedKPIService()
        self.srs_analytics = SRSKPIQueries()
        self.ei_tech_analytics = EITechKPIQueries()
        self.ni_tct_analytics = NITCTKPIQueries()

    async def generate_insights(self, schema_type: str, user_role: str, user_id: str, db: Session, region: str = None) -> Dict[str, Any]:
        """Generate AI insights based on schema type and user role"""
        try:
            # Note: User role validation is now handled by JWT service

            # Validate schema type
            if schema_type not in ['srs', 'ei_tech', 'ni_tct', 'ni_tct_augmented']:
                raise HTTPException(
                    status_code=400,
                    detail={"message": f"Invalid schema type: {schema_type}"}
                )

            # Get analytics data (regional or global based on role)
            analytics_data = self._get_analytics_data(schema_type, user_role, region)

            if not analytics_data:
                error_msg = f"No analytics data found for schema type: {schema_type}"
                if region:
                    error_msg += f" in region: {region}"
                raise HTTPException(
                    status_code=404,
                    detail={"message": error_msg}
                )

            # Get user preferences from feedback history
            user_preferences = self.feedback_service.get_user_preferences(user_id, schema_type, db)
            preferences_prompt = self.feedback_service.format_preferences_for_prompt(user_preferences)

            # Generate AI insights with user preferences and regional context
            insights = self.ai_service.generate_insights(analytics_data, user_role, preferences_prompt, region)

            if not insights:
                raise HTTPException(
                    status_code=500,
                    detail={"message": "Failed to generate insights"}
                )

            # Return response
            return {
                "status_code": 200,
                "message": f"AI insights generated successfully for {user_role}",
                "body": {
                    "schema_type": schema_type,
                    "user_id": user_id,
                    "user_role": user_role,
                    "insights_count": len(insights),
                    "insights": insights,
                    "personalization_level": f"Based on {user_preferences.get('total_feedback', 0)} feedback items",
                    "generated_at": datetime.now().isoformat()
                }
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            raise HTTPException(
                status_code=500,
                detail={"message": f"Internal server error: {str(e)}"}
            )

    def submit_insight_feedback(self, user_id: str, feedback_data: dict, db: Session) -> dict:
        """Store feedback for an insight, preventing duplicates per user/insight/schema_type"""
        schema_type = feedback_data["schema_type"].lower()
        insight_text = feedback_data["insight_text"].strip()
        feedback = feedback_data["feedback"].lower()
        if feedback not in ("like", "dislike"):
            raise HTTPException(status_code=400, detail={"message": "Feedback must be 'like' or 'dislike'"})
        # Check for duplicate
        existing = db.query(InsightFeedback).filter_by(
            user_id=user_id,
            schema_type=schema_type,
            insight_text=insight_text
        ).first()
        if existing:
            # Update feedback if changed
            if existing.feedback != feedback:
                existing.feedback = feedback
                db.commit()
                db.refresh(existing)
            return {"status_code": 200, "message": "Feedback updated", "body": {"feedback_id": existing.id}}
        # Create new feedback
        new_feedback = InsightFeedback(
            user_id=user_id,
            schema_type=schema_type,
            insight_text=insight_text,
            feedback=feedback
        )
        db.add(new_feedback)
        db.commit()
        db.refresh(new_feedback)
        return {"status_code": 201, "message": "Feedback submitted", "body": {"feedback_id": new_feedback.id}}

    def _get_analytics_data(self, schema_type: str, user_role: str = None, region: str = None) -> Dict[str, Any]:
        """Get analytics data based on schema type, user role, and region"""
        try:
            # For safety_manager role, use regional queries
            if user_role == "safety_manager" and region:
                logger.info(f"Getting regional analytics data for {schema_type} in region {region}")
                return execute_regional_kpis(schema_type, region)

            # For global roles (safety_head, cxo), use global queries
            logger.info(f"Getting global analytics data for {schema_type}")
            if schema_type == 'srs':
                return self.srs_analytics.get_all_kpis()
            elif schema_type == 'ei_tech':
                return self.ei_tech_analytics.get_all_kpis()
            elif schema_type == 'ni_tct':
                return self.ni_tct_analytics.get_all_kpis()
            elif schema_type == 'ni_tct_augmented':
                # Use augmented KPI queries for enhanced insights
                from src.analytics.ni_tct_augmented_kpi_queries import NITCTAugmentedKPIQueries
                augmented_analytics = NITCTAugmentedKPIQueries()
                return augmented_analytics.get_all_augmented_kpis()
            else:
                return {}
        except Exception as e:
            logger.error(f"Error getting analytics data for {schema_type} (role: {user_role}, region: {region}): {e}")
            return {}

    async def generate_more_insights(self, schema_type: str, user_role: str, user_id: str,
                                   count: int, db: Session, region: str = None) -> Dict[str, Any]:
        """Generate additional insights using AI prompting to avoid common patterns"""
        try:
            # Validate schema type
            if schema_type not in ['srs', 'ei_tech', 'ni_tct', 'ni_tct_augmented']:
                raise HTTPException(
                    status_code=400,
                    detail={"message": f"Invalid schema type: {schema_type}"}
                )

            # Get analytics data (regional or global based on role)
            analytics_data = self._get_analytics_data(schema_type, user_role, region)

            if not analytics_data:
                error_msg = f"No analytics data found for schema type: {schema_type}"
                if region:
                    error_msg += f" in region: {region}"
                raise HTTPException(
                    status_code=404,
                    detail={"message": error_msg}
                )

            # Get insights from user's feedback history to understand their preferences
            # and use those as "existing insights" to avoid similar patterns
            feedback_based_insights = self._get_feedback_based_insights(user_id, schema_type, db)

            # Get user preferences from feedback history
            user_preferences = self.feedback_service.get_user_preferences(user_id, schema_type, db)
            preferences_prompt = self.feedback_service.format_preferences_for_prompt(user_preferences)

            # Generate additional insights using feedback history as reference
            new_insights = self.ai_service.generate_additional_insights(
                analytics_data, user_role, feedback_based_insights, count, preferences_prompt, region
            )

            if not new_insights:
                raise HTTPException(
                    status_code=500,
                    detail={"message": "Failed to generate additional insights"}
                )

            # Return response
            return {
                "status_code": 200,
                "message": f"Additional AI insights generated successfully for {user_role}",
                "body": {
                    "schema_type": schema_type,
                    "user_id": user_id,
                    "user_role": user_role,
                    "insights_count": len(new_insights),
                    "insights": new_insights,
                    "reference_insights_count": len(feedback_based_insights),
                    "generated_at": datetime.now().isoformat()
                }
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error generating additional insights: {e}")
            raise HTTPException(
                status_code=500,
                detail={"message": f"Internal server error: {str(e)}"}
            )

    def _get_feedback_based_insights(self, user_id: str, schema_type: str, db: Session) -> List[str]:
        """Get insights from user's feedback history to use as reference for avoiding similar patterns"""
        try:
            # Get insights that user has provided feedback on (both liked and disliked)
            # This gives us a reference of what they've seen before
            feedback_records = db.query(InsightFeedback).filter_by(
                user_id=user_id,
                schema_type=schema_type
            ).all()

            # Return the insight texts they've seen before
            return [record.insight_text for record in feedback_records]
        except Exception as e:
            logger.error(f"Error fetching feedback-based insights: {e}")
            return []

    async def generate_unified_insights(self, user_role: str, user_id: str, db: Session, region: str = None) -> Dict[str, Any]:
        """Generate AI insights from all 3 safety data sources combined"""
        try:
            logger.info(f"Generating unified insights for user_role: {user_role}, user_id: {user_id}")

            # Get essential KPIs from all 3 sources in parallel
            unified_data = await self.unified_kpi_service.get_essential_kpis_all_sources()

            # Add summary statistics in parallel
            summary_stats = await self.unified_kpi_service.get_summary_statistics()
            unified_data.update(summary_stats)

            if not unified_data:
                raise HTTPException(
                    status_code=404,
                    detail={"message": "No unified analytics data found"}
                )

            # Get user preferences from feedback history
            user_preferences = self.feedback_service.get_user_preferences(user_id, "unified", db)
            preferences_prompt = self.feedback_service.format_preferences_for_prompt(user_preferences)

            # Generate AI insights with unified data
            insights = self.ai_service.generate_insights(unified_data, user_role, preferences_prompt, region)

            if not insights:
                raise HTTPException(
                    status_code=500,
                    detail={"message": "Failed to generate unified insights"}
                )

            # Return response
            return {
                "status_code": 200,
                "message": f"Unified AI insights generated successfully for {user_role}",
                "body": {
                    "schema_type": "unified",
                    "data_sources": ["srs", "ei_tech", "ni_tct"],
                    "user_id": user_id,
                    "user_role": user_role,
                    "insights_count": len(insights),
                    "insights": insights,
                    "personalization_level": f"Based on {user_preferences.get('total_feedback', 0)} feedback items",
                    "generated_at": datetime.now().isoformat()
                }
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error generating unified insights: {e}")
            raise HTTPException(
                status_code=500,
                detail={"message": f"Internal server error: {str(e)}"}
            )



