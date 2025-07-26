"""
AI Insights Service for generating safety insights using Azure OpenAI
"""

import json
import logging
from typing import Dict, Any, List
from openai import AzureOpenAI
from src.config.settings import settings
from src.prompts.role_prompts import get_role_prompt, get_user_message
from src.prompts.generate_more_prompts import GENERATE_MORE_SYSTEM_PROMPT, get_generate_more_user_message

logger = logging.getLogger(__name__)


class AIInsightsService:
    """Service for generating AI-powered safety insights"""

    def __init__(self):
        """Initialize the AI service with Azure OpenAI client"""
        try:
            self.client = AzureOpenAI(
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version,
                azure_endpoint=settings.azure_openai_endpoint
            )
            self.deployment_name = settings.azure_openai_deployment_name
            logger.info("AI Insights Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI Insights Service: {e}")
            raise

    def generate_insights(self, analytics_data: Dict[str, Any], user_role: str, user_preferences: str = "", region: str = None) -> List[str]:
        """
        Generate AI insights based on analytics data and user role
        
        Args:
            analytics_data: Dictionary containing analytics KPIs
            user_role: User role (safety_head, cxo, safety_manager)
            user_preferences: User preference string for personalization
            region: Region for safety_manager role (NR 1, NR 2, SR 1, SR 2, WR 1, WR 2, INFRA/TRD)
            
        Returns:
            List of insight strings
        """
        try:
            # Get role-specific system prompt
            system_prompt = get_role_prompt(user_role)
            
            # Convert analytics data to JSON string
            analytics_json = json.dumps(analytics_data, indent=2, default=str)
            
            # Add regional context to user preferences if applicable
            enhanced_preferences = user_preferences
            if user_role == "safety_manager" and region:
                regional_context = f"\n\nREGIONAL CONTEXT: You are analyzing data specifically for {region} region. Focus on regional insights and comparisons."
                enhanced_preferences += regional_context

            # Get formatted user message
            user_message = get_user_message(analytics_json, enhanced_preferences)
            
            # Generate insights using Azure OpenAI
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            # Extract and parse insights
            insights_text = response.choices[0].message.content
            insights = self._parse_insights(insights_text)
            
            log_msg = f"Generated {len(insights)} insights for role: {user_role}"
            if region:
                log_msg += f" in region: {region}"
            logger.info(log_msg)
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return []

    def generate_additional_insights(self, analytics_data: Dict[str, Any], user_role: str,
                                   existing_insights: List[str], count: int = 5,
                                   user_preferences: str = "", region: str = None) -> List[str]:
        """
        Generate additional insights that are different from existing ones using sophisticated prompts

        Args:
            analytics_data: Dictionary containing analytics KPIs
            user_role: User role (safety_head, cxo, safety_manager)
            existing_insights: List of previously generated insights
            count: Number of additional insights to generate
            user_preferences: User preference string for personalization
            region: Region for safety_manager role (NR 1, NR 2, SR 1, SR 2, WR 1, WR 2, INFRA/TRD)

        Returns:
            List of new insight strings
        """
        try:
            # Convert analytics data to JSON string
            analytics_json = json.dumps(analytics_data, indent=2, default=str)

            # Add regional context to user preferences if applicable
            enhanced_preferences = user_preferences
            if user_role == "safety_manager" and region:
                regional_context = f"\n\nREGIONAL CONTEXT: You are analyzing data specifically for {region} region. Focus on regional insights and comparisons."
                enhanced_preferences += regional_context

            # Use sophisticated prompts from generate_more_prompts.py
            system_prompt = GENERATE_MORE_SYSTEM_PROMPT
            user_message = get_generate_more_user_message(
                analytics_json=analytics_json,
                existing_insights=existing_insights,
                count=count,
                user_preferences=enhanced_preferences
            )

            # Generate additional insights using Azure OpenAI with sophisticated prompts
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.8,  # Higher temperature for more creative and diverse insights
                max_tokens=1500
            )

            # Extract and parse insights
            insights_text = response.choices[0].message.content
            insights = self._parse_insights(insights_text)

            log_msg = f"Generated {len(insights)} sophisticated additional insights for role: {user_role}"
            if region:
                log_msg += f" in region: {region}"
            logger.info(log_msg)
            return insights

        except Exception as e:
            logger.error(f"Error generating additional insights: {e}")
            return []



    def _parse_insights(self, insights_text: str) -> List[str]:
        """
        Parse insights from AI response text
        
        Args:
            insights_text: Raw text response from AI
            
        Returns:
            List of cleaned insight strings
        """
        try:
            # Split by bullet points and clean up
            lines = insights_text.strip().split('\n')
            insights = []
            
            for line in lines:
                line = line.strip()
                # Remove bullet point symbols and clean up
                if line.startswith('•'):
                    line = line[1:].strip()
                elif line.startswith('-'):
                    line = line[1:].strip()
                elif line.startswith('*'):
                    line = line[1:].strip()
                
                # Skip empty lines and very short lines
                if len(line) > 10:
                    # Remove quotes and special characters
                    line = line.replace('"', '').replace("'", '').replace('/', ' ')
                    insights.append(line)
            
            return insights[:12]  # Limit to maximum 12 insights
            
        except Exception as e:
            logger.error(f"Error parsing insights: {e}")
            return []
