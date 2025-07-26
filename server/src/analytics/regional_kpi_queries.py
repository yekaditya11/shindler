"""
Regional KPI queries for safety manager role with region-specific data filtering
"""

from typing import Dict, List, Any
import logging
from abc import ABC
from src.analytics.srs_kpi_queries import SRSKPIQueries
from src.analytics.ei_tech_kpi_queries import EITechKPIQueries
from src.analytics.ni_tct_kpi_queries import NITCTKPIQueries
from src.analytics.ni_tct_augmented_kpi_queries import NITCTAugmentedKPIQueries

logger = logging.getLogger(__name__)

# Constants
VALID_REGIONS = ["NR 1", "NR 2", "SR 1", "SR 2", "WR 1", "WR 2", "INFRA/TRD"]
VALID_SCHEMA_TYPES = ["srs", "ei_tech", "ni_tct", "ni_tct_augmented"]


class BaseRegionalKPIQueries(ABC):
    """Base class for regional KPI queries with common functionality"""

    def __init__(self, parent_class, region: str = None):
        """
        Initialize regional KPI queries

        Args:
            parent_class: The parent KPI class to inherit from
            region: Region filter (optional)
        """
        self.parent_instance = parent_class()
        self.region = region
        self._validate_region()

    def _validate_region(self):
        """Validate the provided region"""
        if self.region and self.region not in VALID_REGIONS:
            raise ValueError(f"Invalid region: {self.region}. Valid regions: {VALID_REGIONS}")

    def _add_region_filter_to_query(self, query: str, params: Dict = None) -> tuple[str, Dict]:
        """
        Add region filter to SQL query using proper SQLAlchemy approach

        Args:
            query: Original SQL query
            params: Query parameters

        Returns:
            Tuple of (modified_query, updated_params)
        """
        if not self.region:
            return query, params or {}

        params = params or {}
        params["region"] = self.region

        # Use a more robust approach to add region filtering
        query_upper = query.upper().strip()

        # Find insertion point for WHERE clause
        if "WHERE" in query_upper:
            # Add to existing WHERE clause
            where_pos = query_upper.find("WHERE")
            actual_where_pos = query.upper().find("WHERE", where_pos)
            query = (query[:actual_where_pos + 5] +
                    " region = :region AND" +
                    query[actual_where_pos + 5:])
        else:
            # Add new WHERE clause before GROUP BY, ORDER BY, HAVING, or LIMIT
            insertion_keywords = ["GROUP BY", "ORDER BY", "HAVING", "LIMIT"]
            insertion_point = len(query)

            for keyword in insertion_keywords:
                pos = query_upper.find(keyword)
                if pos != -1:
                    insertion_point = min(insertion_point, pos)

            if insertion_point < len(query):
                query = (query[:insertion_point].rstrip() +
                        " WHERE region = :region " +
                        query[insertion_point:])
            else:
                query = query.rstrip() + " WHERE region = :region"

        return query, params

    def execute_query(self, query: str, params: Dict = None) -> List[Dict]:
        """Execute SQL query with regional filtering"""
        try:
            modified_query, updated_params = self._add_region_filter_to_query(query, params)
            return self.parent_instance.execute_query(modified_query, updated_params)
        except Exception as e:
            logger.error(f"Error executing regional query for region {self.region}: {e}")
            raise

    def get_all_kpis(self) -> Dict[str, Any]:
        """Get all KPIs with regional context"""
        try:
            results = self.parent_instance.get_all_kpis()

            # Add regional context to results
            if self.region:
                results["regional_context"] = {
                    "region": self.region,
                    "data_scope": "regional",
                    "valid_regions": VALID_REGIONS
                }

            return results
        except Exception as e:
            logger.error(f"Error getting regional KPIs for region {self.region}: {e}")
            raise

    def __getattr__(self, name):
        """Delegate attribute access to parent instance"""
        return getattr(self.parent_instance, name)


class RegionalSRSKPIQueries(BaseRegionalKPIQueries):
    """Regional SRS KPI queries with region filtering"""

    def __init__(self, region: str = None):
        super().__init__(SRSKPIQueries, region)


class RegionalEITechKPIQueries(BaseRegionalKPIQueries):
    """Regional EI Tech KPI queries with region filtering"""

    def __init__(self, region: str = None):
        super().__init__(EITechKPIQueries, region)


class RegionalNITCTKPIQueries(BaseRegionalKPIQueries):
    """Regional NI TCT KPI queries with region filtering"""

    def __init__(self, region: str = None):
        super().__init__(NITCTKPIQueries, region)


class RegionalNITCTAugmentedKPIQueries(BaseRegionalKPIQueries):
    """Regional NI TCT Augmented KPI queries with region filtering"""

    def __init__(self, region: str = None):
        super().__init__(NITCTAugmentedKPIQueries, region)


def get_regional_kpi_queries(schema_type: str, region: str = None):
    """
    Factory function to get regional KPI query instance

    Args:
        schema_type: Schema type (srs, ei_tech, ni_tct, ni_tct_augmented)
        region: Region filter (optional)

    Returns:
        Regional KPI query instance

    Raises:
        ValueError: If schema_type is invalid
    """
    if schema_type not in VALID_SCHEMA_TYPES:
        raise ValueError(f"Invalid schema type: {schema_type}. Valid types: {VALID_SCHEMA_TYPES}")

    schema_class_map = {
        "srs": RegionalSRSKPIQueries,
        "ei_tech": RegionalEITechKPIQueries,
        "ni_tct": RegionalNITCTKPIQueries,
        "ni_tct_augmented": RegionalNITCTAugmentedKPIQueries
    }

    return schema_class_map[schema_type](region)


def execute_regional_kpis(schema_type: str, region: str) -> Dict[str, Any]:
    """
    Execute regional KPI queries for a specific schema and region

    Args:
        schema_type: Schema type (srs, ei_tech, ni_tct, ni_tct_augmented)
        region: Region (NR 1, NR 2, SR 1, SR 2, WR 1, WR 2, INFRA/TRD)

    Returns:
        Regional KPI results with regional context

    Raises:
        ValueError: If schema_type or region is invalid
        Exception: If query execution fails
    """
    if not region:
        raise ValueError("Region is required for regional KPI execution")

    if region not in VALID_REGIONS:
        raise ValueError(f"Invalid region: {region}. Valid regions: {VALID_REGIONS}")

    try:
        logger.info(f"Executing regional KPI queries for {schema_type} in region {region}")

        regional_queries = get_regional_kpi_queries(schema_type, region)
        results = regional_queries.get_all_kpis()

        logger.info(f"Successfully executed regional KPI queries for {schema_type} in region {region}")
        return results

    except Exception as e:
        logger.error(f"Error executing regional KPI queries for {schema_type} in region {region}: {e}")
        raise





