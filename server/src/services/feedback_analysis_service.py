"""
Feedback Analysis Service for analyzing user preferences from insight feedback
"""

import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from openai import AzureOpenAI
from src.config.settings import settings
from src.models.base_models import InsightFeedback
from src.prompts.feedback_prompts import (
    FEEDBACK_ANALYSIS_SYSTEM_PROMPT,
    FEEDBACK_ANALYSIS_USER_MESSAGE
)

logger = logging.getLogger(__name__)


class FeedbackAnalysisService:
    """Service for analyzing user feedback and extracting preferences"""

    def __init__(self):
        """Initialize the feedback analysis service with Azure OpenAI client"""
        try:
            self.client = AzureOpenAI(
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version,
                azure_endpoint=settings.azure_openai_endpoint
            )
            self.deployment_name = settings.azure_openai_deployment_name
            logger.info("Feedback Analysis Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Feedback Analysis Service: {e}")
            raise

    def get_user_preferences(self, user_id: str, schema_type: str, db: Session) -> Dict[str, Any]:
        """
        Get user preferences based on their feedback history
        
        Args:
            user_id: User identifier
            schema_type: Schema type (srs, ei_tech, ni_tct)
            db: Database session
            
        Returns:
            Dictionary containing user preferences
        """
        try:
            # Get user's feedback history
            feedback_records = db.query(InsightFeedback).filter_by(
                user_id=user_id,
                schema_type=schema_type
            ).all()
            
            if not feedback_records:
                return {"preferences": "No previous feedback available"}
            
            # Separate liked and disliked insights
            liked_insights = [record.insight_text for record in feedback_records if record.feedback == 'like']
            disliked_insights = [record.insight_text for record in feedback_records if record.feedback == 'dislike']
            
            # If we have enough feedback, analyze patterns using AI
            if len(feedback_records) >= 3:
                preferences = self._analyze_feedback_patterns(liked_insights, disliked_insights)
            else:
                # Basic preference extraction for limited feedback
                preferences = self._basic_preference_extraction(liked_insights, disliked_insights)
            
            return {
                "preferences": preferences,
                "total_feedback": len(feedback_records),
                "liked_count": len(liked_insights),
                "disliked_count": len(disliked_insights)
            }
            
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return {"preferences": "Error retrieving preferences"}

    def format_preferences_for_prompt(self, user_preferences: Dict[str, Any]) -> str:
        """
        Format user preferences for inclusion in AI prompts
        
        Args:
            user_preferences: Dictionary containing user preferences
            
        Returns:
            Formatted string for prompt inclusion
        """
        try:
            preferences = user_preferences.get("preferences", "")
            total_feedback = user_preferences.get("total_feedback", 0)
            
            if total_feedback == 0:
                return ""
            
            return f"""
            
            USER PREFERENCES (based on {total_feedback} previous feedback):
            {preferences}
            
            Please tailor your insights to match these user preferences while maintaining accuracy and relevance.
            """
            
        except Exception as e:
            logger.error(f"Error formatting preferences: {e}")
            return ""

    def _analyze_feedback_patterns(self, liked_insights: List[str], disliked_insights: List[str]) -> str:
        """
        Use AI to analyze feedback patterns and extract preferences
        
        Args:
            liked_insights: List of insights the user liked
            disliked_insights: List of insights the user disliked
            
        Returns:
            String describing user preferences
        """
        try:
            # Prepare feedback data for analysis
            liked_text = "\n".join([f"- {insight}" for insight in liked_insights]) if liked_insights else "None"
            disliked_text = "\n".join([f"- {insight}" for insight in disliked_insights]) if disliked_insights else "None"
            
            user_message = FEEDBACK_ANALYSIS_USER_MESSAGE.format(
                liked_insights=liked_text,
                disliked_insights=disliked_text
            )
            
            # Generate preference analysis using Azure OpenAI
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": FEEDBACK_ANALYSIS_SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,  # Lower temperature for more consistent analysis
                max_tokens=800
            )
            
            preferences = response.choices[0].message.content.strip()
            logger.info(f"Generated AI-powered preference analysis")
            return preferences
            
        except Exception as e:
            logger.error(f"Error analyzing feedback patterns: {e}")
            return self._basic_preference_extraction(liked_insights, disliked_insights)

    def _basic_preference_extraction(self, liked_insights: List[str], disliked_insights: List[str]) -> str:
        """
        Basic preference extraction without AI analysis
        
        Args:
            liked_insights: List of insights the user liked
            disliked_insights: List of insights the user disliked
            
        Returns:
            String describing basic user preferences
        """
        try:
            preferences = []
            
            if liked_insights:
                # Look for common patterns in liked insights
                if any("percentage" in insight.lower() or "%" in insight for insight in liked_insights):
                    preferences.append("User prefers insights with specific percentages and quantified data")
                
                if any("trend" in insight.lower() for insight in liked_insights):
                    preferences.append("User values trend analysis and temporal patterns")
                
                if any("risk" in insight.lower() for insight in liked_insights):
                    preferences.append("User is interested in risk-related insights")
                
                if any("action" in insight.lower() or "recommend" in insight.lower() for insight in liked_insights):
                    preferences.append("User appreciates actionable recommendations")
            
            if disliked_insights:
                # Look for patterns to avoid
                if any("general" in insight.lower() for insight in disliked_insights):
                    preferences.append("User dislikes general or vague insights")
            
            if not preferences:
                preferences.append("User feedback patterns are still being analyzed")
            
            return ". ".join(preferences) + "."
            
        except Exception as e:
            logger.error(f"Error in basic preference extraction: {e}")
            return "Unable to determine user preferences from current feedback"

    def analyze_feedback_trends(self, user_id: str, schema_type: str, db: Session) -> Dict[str, Any]:
        """
        Analyze feedback trends over time for a user
        
        Args:
            user_id: User identifier
            schema_type: Schema type (srs, ei_tech, ni_tct)
            db: Database session
            
        Returns:
            Dictionary containing trend analysis
        """
        try:
            # Get chronological feedback history
            feedback_records = db.query(InsightFeedback).filter_by(
                user_id=user_id,
                schema_type=schema_type
            ).order_by(InsightFeedback.timestamp).all()
            
            if len(feedback_records) < 5:
                return {"trends": "Insufficient data for trend analysis", "total_feedback": len(feedback_records)}
            
            # Calculate basic trends
            total_feedback = len(feedback_records)
            liked_count = sum(1 for record in feedback_records if record.feedback == 'like')
            disliked_count = total_feedback - liked_count
            
            like_rate = (liked_count / total_feedback) * 100 if total_feedback > 0 else 0
            
            # Recent vs older feedback comparison
            recent_feedback = feedback_records[-10:]  # Last 10 feedback items
            recent_like_rate = (sum(1 for record in recent_feedback if record.feedback == 'like') / len(recent_feedback)) * 100
            
            trend_direction = "improving" if recent_like_rate > like_rate else "declining" if recent_like_rate < like_rate else "stable"
            
            return {
                "trends": f"Overall satisfaction rate: {like_rate:.1f}%. Recent trend: {trend_direction} ({recent_like_rate:.1f}% in last 10 feedback items)",
                "total_feedback": total_feedback,
                "liked_count": liked_count,
                "disliked_count": disliked_count,
                "like_rate": like_rate,
                "recent_like_rate": recent_like_rate,
                "trend_direction": trend_direction
            }
            
        except Exception as e:
            logger.error(f"Error analyzing feedback trends: {e}")
            return {"trends": "Error analyzing feedback trends", "total_feedback": 0}






