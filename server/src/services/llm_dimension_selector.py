"""
LLM Dimension Selector Service
Uses LLM to intelligently decide which data quality dimensions to check for each column
"""

import json
import logging
from typing import Dict, Any, List
from openai import AsyncAzureOpenAI

from src.config.settings import settings

logger = logging.getLogger(__name__)

class LLMDimensionSelector:
    """Service that uses LLM to select relevant data quality dimensions for each column"""
    
    def __init__(self, max_concurrent_requests: int = 10):
        self.client = AsyncAzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint
        )
        self.deployment_name = settings.azure_openai_deployment_name
        self.max_concurrent_requests = max_concurrent_requests
        
    async def select_dimensions(self, column_name: str, column_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use LLM to determine which data quality dimensions should be checked for a column
        
        Args:
            column_name: Name of the column
            column_data: Semantic data for the column from semantics JSON
            
        Returns:
            Dictionary with dimensions to check and reasoning
        """
        try:
            logger.info(f"LLM analyzing dimensions for column: {column_name}")
            
            prompt = self._build_dimension_selection_prompt(column_name, column_data)
            
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a data quality expert specializing in safety incident management systems. Analyze column definitions and determine which data quality dimensions are relevant."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent results
                max_tokens=800
            )
            
            llm_response = response.choices[0].message.content
            logger.debug(f"LLM response for {column_name}: {llm_response}")
            
            # Parse LLM response
            dimension_analysis = self._parse_llm_response(llm_response)
            
            logger.info(f"LLM selected dimensions for {column_name}: {dimension_analysis.get('dimensions_to_check', [])}")
            
            return dimension_analysis
            
        except Exception as e:
            logger.error(f"Error in LLM dimension selection for {column_name}: {e}")
            # Return default fallback
            return self._get_default_dimensions()
    
    def _build_dimension_selection_prompt(self, column_name: str, column_data: Dict[str, Any]) -> str:
        """
        Build the prompt for LLM to analyze dimension requirements
        """
        description = column_data.get('description', 'No description available')
        data_type = column_data.get('data_type', 'Unknown')
        unique_values = column_data.get('unique_values', [])
        unique_count = column_data.get('unique_count', 'Unknown')
        min_value = column_data.get('min', 'Not specified')
        max_value = column_data.get('max', 'Not specified')
        note = column_data.get('note', '')
        
        prompt = f"""
Analyze this column from a safety incident reporting system and determine which data quality dimensions should be checked:

COLUMN INFORMATION:
- Column Name: {column_name}
- Description: "{description}"
- Data Type: {data_type}
- Sample Values: {unique_values[:10] if unique_values else 'None available'}
- Unique Count: {unique_count}
- Value Range: {min_value} to {max_value}
- Additional Notes: {note}

DATA QUALITY DIMENSIONS TO CONSIDER:
1. COMPLETENESS: Check for missing/null values
2. UNIQUENESS: Check if values should be unique
3. CONSISTENCY: Check data patterns and formats
4. VALIDITY: Check against business rules and constraints
5. TIMELINESS: Check date freshness and recency

ANALYSIS INSTRUCTIONS:
For each dimension, determine if it should be checked based on the column's semantic meaning:

- If description contains "unique identifier" → Check COMPLETENESS, UNIQUENESS, VALIDITY
- If description contains "if applicable" or "optional" → Skip COMPLETENESS or reduce penalty
- If description contains "date when" or "timestamp" → Check COMPLETENESS, CONSISTENCY, VALIDITY, TIMELINESS
- If description contains "type of" or "indicates whether" → Check COMPLETENESS, CONSISTENCY, VALIDITY
- If description contains "name of" → Check COMPLETENESS, CONSISTENCY, VALIDITY
- If field has limited unique_values → Check VALIDITY against allowed list
- If field is free text with high unique_count → Focus on CONSISTENCY patterns

RESPONSE FORMAT:
Return a JSON object with this exact structure:
{{
  "dimensions_to_check": ["dimension1", "dimension2", ...],
  "dimensions_to_skip": ["dimension3", "dimension4", ...],
  "reasoning": {{
    "completeness": "reason for checking/skipping completeness",
    "uniqueness": "reason for checking/skipping uniqueness",
    "consistency": "reason for checking/skipping consistency",
    "validity": "reason for checking/skipping validity",
    "timeliness": "reason for checking/skipping timeliness"
  }},
  "priority": "critical|high|medium|low"
}}

Analyze the column and provide your assessment:
"""
        return prompt
    
    def _parse_llm_response(self, llm_response: str) -> Dict[str, Any]:
        """
        Parse LLM response and extract dimension selection
        """
        try:
            # Try to extract JSON from the response
            start_idx = llm_response.find('{')
            end_idx = llm_response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = llm_response[start_idx:end_idx]
                parsed_response = json.loads(json_str)
                
                # Validate required fields
                required_fields = ['dimensions_to_check', 'dimensions_to_skip', 'reasoning']
                if all(field in parsed_response for field in required_fields):
                    return parsed_response
            
            logger.warning("Could not parse LLM response as valid JSON, using default")
            return self._get_default_dimensions()
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return self._get_default_dimensions()
    
    def _get_default_dimensions(self) -> Dict[str, Any]:
        """
        Return default dimension selection when LLM fails
        """
        return {
            "dimensions_to_check": ["completeness", "uniqueness", "consistency", "validity", "timeliness"],
            "dimensions_to_skip": [],
            "reasoning": {
                "completeness": "Default check - all fields should have data",
                "uniqueness": "Default check - assess uniqueness patterns",
                "consistency": "Default check - validate data patterns",
                "validity": "Default check - ensure data meets basic rules",
                "timeliness": "Default check - assess data freshness"
            },
            "priority": "medium"
        }
    
    async def batch_select_dimensions(self, schema_columns: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Select dimensions for multiple columns in parallel batch processing with concurrency control

        Args:
            schema_columns: Dictionary of column_name -> column_data

        Returns:
            Dictionary of column_name -> dimension_analysis
        """
        import asyncio

        logger.info(f"Starting parallel dimension selection for {len(schema_columns)} columns with max {self.max_concurrent_requests} concurrent requests")

        # Create semaphore to limit concurrent LLM requests
        semaphore = asyncio.Semaphore(self.max_concurrent_requests)

        async def process_column_with_semaphore(column_name: str, column_data: Dict[str, Any]):
            async with semaphore:
                return await self.select_dimensions(column_name, column_data)

        # Create tasks for parallel processing with concurrency control
        tasks = []
        column_names = []

        for column_name, column_data in schema_columns.items():
            task = process_column_with_semaphore(column_name, column_data)
            tasks.append(task)
            column_names.append(column_name)

        # Execute all tasks in parallel with controlled concurrency
        try:
            results_list = await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error in parallel processing: {e}")
            # Fallback to sequential processing
            return await self._sequential_batch_select_dimensions(schema_columns)

        # Process results
        results = {}
        for column_name, result in zip(column_names, results_list):
            if isinstance(result, Exception):
                logger.error(f"Error processing column {column_name}: {result}")
                results[column_name] = self._get_default_dimensions()
            else:
                results[column_name] = result

        logger.info(f"Completed parallel dimension selection for {len(results)} columns")
        return results

    async def _sequential_batch_select_dimensions(self, schema_columns: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Fallback sequential processing if parallel fails
        """
        results = {}

        for column_name, column_data in schema_columns.items():
            try:
                dimension_analysis = await self.select_dimensions(column_name, column_data)
                results[column_name] = dimension_analysis
            except Exception as e:
                logger.error(f"Error processing column {column_name}: {e}")
                results[column_name] = self._get_default_dimensions()

        return results
