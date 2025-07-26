"""
Semantic Configuration Service
Loads and manages semantic configurations from semantics folder
"""

import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class SemanticConfigService:
    """Service to load and manage semantic configurations"""
    
    def __init__(self):
        self.semantics_data: Optional[Dict[str, Any]] = None
        self.semantics_file_path = Path("semantics/shinlder_semantics.json")
        
    def load_semantics(self) -> Dict[str, Any]:
        """
        Load semantic configurations from JSON file
        
        Returns:
            Dictionary containing all semantic configurations
        """
        try:
            if self.semantics_data is None:
                logger.info(f"Loading semantics from {self.semantics_file_path}")
                
                if not self.semantics_file_path.exists():
                    raise FileNotFoundError(f"Semantics file not found: {self.semantics_file_path}")
                
                with open(self.semantics_file_path, 'r', encoding='utf-8') as file:
                    self.semantics_data = json.load(file)
                
                logger.info(f"Successfully loaded semantics for {len(self.semantics_data)} schemas")
            
            return self.semantics_data
            
        except Exception as e:
            logger.error(f"Error loading semantics file: {e}")
            raise
    
    def get_schema_semantics(self, schema_type: str) -> Dict[str, Any]:
        """
        Get semantic configuration for a specific schema type
        
        Args:
            schema_type: Schema type (ei_tech, srs, ni_tct, ni_tct_augmented)
            
        Returns:
            Dictionary containing column semantics for the schema
        """
        try:
            semantics = self.load_semantics()
            
            # Map schema types to semantic keys
            schema_mapping = {
                "ei_tech": "unsafe_events_ei_tech",
                "srs": "unsafe_events_srs",
                "ni_tct": "unsafe_events_ni_tct",
                "ni_tct_augmented": "unsafe_events_ni_tct_augmented"  # Use dedicated augmented schema
            }
            
            semantic_key = schema_mapping.get(schema_type)
            if not semantic_key:
                raise ValueError(f"Unknown schema type: {schema_type}")
            
            if semantic_key not in semantics:
                raise ValueError(f"Semantic configuration not found for: {semantic_key}")
            
            schema_semantics = semantics[semantic_key]
            logger.info(f"Retrieved semantics for {schema_type}: {len(schema_semantics)} columns")
            
            return schema_semantics
            
        except Exception as e:
            logger.error(f"Error getting schema semantics for {schema_type}: {e}")
            raise
    
    def get_column_semantics(self, schema_type: str, column_name: str) -> Dict[str, Any]:
        """
        Get semantic configuration for a specific column
        
        Args:
            schema_type: Schema type
            column_name: Name of the column
            
        Returns:
            Dictionary containing column semantic information
        """
        try:
            schema_semantics = self.get_schema_semantics(schema_type)
            
            if column_name not in schema_semantics:
                logger.warning(f"Column {column_name} not found in {schema_type} semantics")
                return {}
            
            column_semantics = schema_semantics[column_name]
            logger.debug(f"Retrieved semantics for {schema_type}.{column_name}")
            
            return column_semantics
            
        except Exception as e:
            logger.error(f"Error getting column semantics for {schema_type}.{column_name}: {e}")
            raise
    
    def get_available_schemas(self) -> list:
        """
        Get list of available schema types
        
        Returns:
            List of available schema type keys
        """
        try:
            semantics = self.load_semantics()
            return list(semantics.keys())
            
        except Exception as e:
            logger.error(f"Error getting available schemas: {e}")
            return []
    
    def reload_semantics(self) -> None:
        """
        Force reload of semantic configurations
        """
        logger.info("Forcing reload of semantic configurations")
        self.semantics_data = None
        self.load_semantics()
