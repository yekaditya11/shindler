"""
Unified Dashboard Service for providing standardized dashboard data across all schema types
Self-contained service with all SQL queries included for 9 common KPIs
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.config.database import get_db

logger = logging.getLogger(__name__)


class UnifiedDashboardService:
    """
    Clean and optimized unified dashboard service for 11 common KPIs:
    1. Total Events Count
    2. Serious Near Miss Rate
    3. Work Stoppage Rate
    4. Monthly Trends
    5. Branch Performance Analysis
    6. Event Type Distribution
    7. Repeat Locations
    8. Response Time Analysis
    9. Safety Performance Trends
    10. Incident Severity Distribution
    11. Operational Impact Analysis
    """

    def __init__(self):
        """Initialize the unified dashboard service with schema configurations"""
        self.schema_configs = {
            "ei_tech": {
                "table_name": "unsafe_events_ei_tech",
                "primary_key": "event_id",
                "event_date_field": "date_of_unsafe_event",
                "reported_date_field": "reported_date",
                "serious_field": "serious_near_miss",
                "work_stopped_field": "work_stopped",
                "event_type_field": "unsafe_event_type",
                "location_field": "unsafe_event_location",
                "branch_field": "branch",
                "region_field": "region"
            },
            "srs": {
                "table_name": "unsafe_events_srs",
                "primary_key": "event_id",
                "event_date_field": "date_of_unsafe_event",
                "reported_date_field": "reported_date",
                "serious_field": "serious_near_miss",
                "work_stopped_field": "work_stopped",
                "event_type_field": "unsafe_event_type",
                "location_field": "unsafe_event_location",
                "branch_field": "branch",
                "region_field": "region"
            },
            "ni_tct": {
                "table_name": "unsafe_events_ni_tct",
                "primary_key": "reporting_id",
                "event_date_field": "date_and_time_of_unsafe_event",
                "reported_date_field": "created_on",
                "serious_field": "action_related_to_high_risk_situation",
                "work_stopped_field": "work_was_stopped",
                "event_type_field": "type_of_unsafe_event",
                "location_field": "location",
                "branch_field": "branch_name",
                "region_field": "region"
            },
            "ni_tct_augmented": {
                "table_name": "unsafe_events_ni_tct_augmented",
                "primary_key": "reporting_id",
                "event_date_field": "date_and_time_of_unsafe_event",
                "reported_date_field": "created_on",
                "serious_field": "action_related_to_high_risk_situation",
                "work_stopped_field": "work_was_stopped",
                "event_type_field": "type_of_unsafe_event",
                "location_field": "location",
                "branch_field": "branch_name",
                "region_field": "region"
            }
        }

        self.valid_regions = ["NR 1", "NR 2", "SR 1", "SR 2", "WR 1", "WR 2", "INFRA/TRD"]

        logger.info("Unified Dashboard Service initialized successfully")

    def get_session(self) -> Session:
        """Get database session"""
        return next(get_db())

    def execute_query(self, query: str, params: Dict = None) -> List[Dict]:
        """Execute SQL query and return results"""
        session = self.get_session()
        try:
            result = session.execute(text(query), params or {})
            columns = result.keys()
            return [dict(zip(columns, row)) for row in result.fetchall()]
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise
        finally:
            session.close()

    def get_dashboard_data(self, schema_type: str, start_date: Optional[str] = None,
                          end_date: Optional[str] = None, user_role: str = None,
                          region: str = None) -> Dict[str, Any]:
        """
        Get unified dashboard data for specified schema type

        Args:
            schema_type: Schema type (ei_tech, srs, ni_tct)
            start_date: Start date for filtering (YYYY-MM-DD format)
            end_date: End date for filtering (YYYY-MM-DD format)
            user_role: User role (safety_head, cxo, safety_manager)
            region: Region for safety_manager role

        Returns:
            Dictionary containing unified dashboard data with 9 KPIs
        """
        try:
            # Validate inputs
            if schema_type not in self.schema_configs:
                raise ValueError(f"Invalid schema type: {schema_type}. Valid types: {list(self.schema_configs.keys())}")

            if user_role == "safety_manager" and region and region not in self.valid_regions:
                raise ValueError(f"Invalid region: {region}. Valid regions: {self.valid_regions}")

            # Set default date range (last 1 year)
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

            logger.info(f"Generating dashboard data for {schema_type} from {start_date} to {end_date}")
            if user_role == "safety_manager" and region:
                logger.info(f"Regional scope: {region}")

            # Get all KPI data
            kpi_data = self._get_all_kpis(schema_type, start_date, end_date, region)

            # Build response
            dashboard_data = {
                "schema_type": schema_type,
                "date_range": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "generated_at": datetime.now().isoformat(),
                "user_context": {
                    "user_role": user_role or "unknown",
                    "region": region,
                    "data_scope": "regional" if region else "global"
                },
                "dashboard_data": kpi_data
            }

            return dashboard_data

        except Exception as e:
            logger.error(f"Error generating dashboard data for {schema_type}: {e}")
            raise

    def _get_all_kpis(self, schema_type: str, start_date: str, end_date: str, region: str = None) -> Dict[str, Any]:
        """
        Get all KPIs for the dashboard (standard + augmented for ni_tct_augmented)

        Args:
            schema_type: Schema type (ei_tech, srs, ni_tct, ni_tct_augmented)
            start_date: Start date for filtering
            end_date: End date for filtering
            region: Optional region filter

        Returns:
            Dictionary containing all KPIs (standard + augmented if applicable)
        """
        try:
            config = self.schema_configs[schema_type]

            # Execute standard KPI queries
            total_events = self._get_total_events_count(config, start_date, end_date, region)
            serious_near_miss = self._get_serious_near_miss_rate(config, start_date, end_date, region)
            work_stoppage = self._get_work_stoppage_rate(config, start_date, end_date, region)
            monthly_trends = self._get_monthly_trends(config, start_date, end_date, region)
            branch_performance = self._get_branch_performance_analysis(config, start_date, end_date, region)
            event_types = self._get_event_type_distribution(config, start_date, end_date, region)
            repeat_locations = self._get_repeat_locations(config, start_date, end_date, region)
            response_time = self._get_response_time_analysis(config, start_date, end_date, region)
            safety_performance_trends = self._get_safety_performance_trends(config, start_date, end_date, region)
            incident_severity = self._get_incident_severity_distribution(config, start_date, end_date, region)
            operational_impact = self._get_operational_impact_analysis(config, start_date, end_date, region)
            time_based_analysis = self._get_time_based_analysis(config, start_date, end_date, region)

            # Standard KPIs
            kpi_data = {
                "total_events": total_events,
                "serious_near_miss_rate": serious_near_miss,
                "work_stoppage_rate": work_stoppage,
                "monthly_trends": monthly_trends,
                "branch_performance_analysis": branch_performance,
                "event_type_distribution": event_types,
                "repeat_locations": repeat_locations,
                "response_time_analysis": response_time,
                "safety_performance_trends": safety_performance_trends,
                "incident_severity_distribution": incident_severity,
                "operational_impact_analysis": operational_impact,
                "time_based_analysis": time_based_analysis
            }

            # Add augmented KPIs for ni_tct_augmented schema
            if schema_type == "ni_tct_augmented":
                augmented_kpis = self._get_augmented_kpis(config, start_date, end_date, region)
                kpi_data.update(augmented_kpis)

            return kpi_data

        except Exception as e:
            logger.error(f"Error getting KPIs for {schema_type}: {e}")
            return self._get_empty_dashboard_data()

    def _get_augmented_kpis(self, config: Dict, start_date: str, end_date: str, region: str = None) -> Dict[str, Any]:
        """Get augmented KPIs specific to ni_tct_augmented schema"""
        try:
            from src.analytics.ni_tct_augmented_kpi_queries import NITCTAugmentedKPIQueries

            # Initialize augmented KPI queries
            augmented_queries = NITCTAugmentedKPIQueries()

            # Get augmented KPIs (subset for dashboard)
            weather_impact = augmented_queries.get_weather_impact_analysis()
            experience_analysis = augmented_queries.get_experience_level_analysis()
            site_risk_analysis = augmented_queries.get_site_risk_analysis()
            workload_analysis = augmented_queries.get_workload_impact_analysis()
            weather_severity = augmented_queries.get_weather_severity_correlation()
            training_effectiveness = augmented_queries.get_training_effectiveness_analysis()

            return {
                "augmented_kpis": {
                    "weather_impact_analysis": weather_impact[:10],  # Top 10 weather conditions
                    "experience_level_analysis": experience_analysis,
                    "site_risk_analysis": site_risk_analysis,
                    "workload_impact_analysis": workload_analysis,
                    "weather_severity_correlation": weather_severity,
                    "training_effectiveness": training_effectiveness
                }
            }

        except Exception as e:
            logger.error(f"Error getting augmented KPIs: {e}")
            return {"augmented_kpis": {}}

    # ==================== KPI QUERY METHODS ====================

    def _get_total_events_count(self, config: Dict, start_date: str, end_date: str, region: str = None) -> Dict[str, Any]:
        """KPI 1: Total Events Count"""
        try:
            region_filter = f"AND {config['region_field']} = :region" if region else ""

            query = f"""
            SELECT
                COUNT(*) as total_events,
                COUNT(DISTINCT {config['primary_key']}) as unique_events
            FROM {config['table_name']}
            WHERE {config['primary_key']} IS NOT NULL
                AND {config['event_date_field']} BETWEEN :start_date AND :end_date
                {region_filter}
            """

            params = {"start_date": start_date, "end_date": end_date}
            if region:
                params["region"] = region

            result = self.execute_query(query, params)
            data = result[0] if result else {"total_events": 0, "unique_events": 0}

            return {
                "count": {
                    "total_events": data.get("total_events", 0),
                    "unique_events": data.get("unique_events", 0)
                },
                "description": f"Total unsafe events recorded in the system"
            }

        except Exception as e:
            logger.error(f"Error getting total events count: {e}")
            return {"count": {"total_events": 0, "unique_events": 0}, "description": "Error retrieving data"}

    def _get_serious_near_miss_rate(self, config: Dict, start_date: str, end_date: str, region: str = None) -> Dict[str, Any]:
        """KPI 2: Serious Near Miss Rate"""
        try:
            region_filter = f"AND {config['region_field']} = :region" if region else ""

            query = f"""
            SELECT
                COUNT(CASE WHEN UPPER({config['serious_field']}) = 'YES' THEN 1 END) as serious_count,
                COUNT(*) as total_events,
                ROUND(COUNT(CASE WHEN UPPER({config['serious_field']}) = 'YES' THEN 1 END) * 100.0 /
                      NULLIF(COUNT(*), 0), 2) as serious_percentage
            FROM {config['table_name']}
            WHERE {config['event_date_field']} BETWEEN :start_date AND :end_date
                {region_filter}
            """

            params = {"start_date": start_date, "end_date": end_date}
            if region:
                params["region"] = region

            result = self.execute_query(query, params)
            data = result[0] if result else {"serious_count": 0, "total_events": 0, "serious_percentage": 0.0}

            return {
                "rate": float(data.get("serious_percentage", 0.0)),
                "count": {
                    "serious_near_miss_count": data.get("serious_count", 0),
                    "non_serious_count": data.get("total_events", 0) - data.get("serious_count", 0),
                    "total_events": data.get("total_events", 0),
                    "serious_near_miss_percentage": str(data.get("serious_percentage", 0.0))
                },
                "description": "Percentage of events classified as serious near misses"
            }

        except Exception as e:
            logger.error(f"Error getting serious near miss rate: {e}")
            return {"rate": 0.0, "count": {"serious_near_miss_count": 0, "non_serious_count": 0, "total_events": 0, "serious_near_miss_percentage": "0.0"}, "description": "Error retrieving data"}

    def _get_work_stoppage_rate(self, config: Dict, start_date: str, end_date: str, region: str = None) -> Dict[str, Any]:
        """KPI 3: Work Stoppage Rate"""
        try:
            region_filter = f"AND {config['region_field']} = :region" if region else ""

            query = f"""
            SELECT
                COUNT(CASE WHEN UPPER({config['work_stopped_field']}) = 'YES' THEN 1 END) as work_stopped_count,
                COUNT(*) as total_events,
                ROUND(COUNT(CASE WHEN UPPER({config['work_stopped_field']}) = 'YES' THEN 1 END) * 100.0 /
                      NULLIF(COUNT(*), 0), 2) as work_stoppage_percentage
            FROM {config['table_name']}
            WHERE {config['event_date_field']} BETWEEN :start_date AND :end_date
                {region_filter}
            """

            params = {"start_date": start_date, "end_date": end_date}
            if region:
                params["region"] = region

            result = self.execute_query(query, params)
            data = result[0] if result else {"work_stopped_count": 0, "total_events": 0, "work_stoppage_percentage": 0.0}

            return {
                "rate": float(data.get("work_stoppage_percentage", 0.0)),
                "count": data.get("work_stopped_count", 0),
                "total": {
                    "total_events": data.get("total_events", 0),
                    "unique_events": data.get("total_events", 0)
                },
                "description": "Percentage of events that resulted in work stoppage"
            }

        except Exception as e:
            logger.error(f"Error getting work stoppage rate: {e}")
            return {"rate": 0.0, "count": 0, "total": {"total_events": 0, "unique_events": 0}, "description": "Error retrieving data"}

    def _get_monthly_trends(self, config: Dict, start_date: str, end_date: str, region: str = None) -> List[Dict]:
        """KPI 4: Monthly Trends"""
        try:
            region_filter = f"AND {config['region_field']} = :region" if region else ""

            query = f"""
            SELECT
                TO_CHAR({config['event_date_field']}, 'YYYY-MM') as month,
                COUNT(*) as event_count,
                COUNT(CASE WHEN UPPER({config['serious_field']}) = 'YES' THEN 1 END) as serious_count,
                COUNT(CASE WHEN UPPER({config['work_stopped_field']}) = 'YES' THEN 1 END) as work_stopped_count
            FROM {config['table_name']}
            WHERE {config['event_date_field']} BETWEEN :start_date AND :end_date
                {region_filter}
            GROUP BY TO_CHAR({config['event_date_field']}, 'YYYY-MM')
            ORDER BY month
            """

            params = {"start_date": start_date, "end_date": end_date}
            if region:
                params["region"] = region

            return self.execute_query(query, params)

        except Exception as e:
            logger.error(f"Error getting monthly trends: {e}")
            return []

    def _get_branch_performance_analysis(self, config: Dict, start_date: str, end_date: str, region: str = None) -> List[Dict]:
        """KPI 5: Branch Performance Analysis - Useful for both global and regional views"""
        try:
            region_filter = f"AND {config['region_field']} = :region" if region else ""

            query = f"""
            SELECT
                {config['branch_field']} as branch,
                {config['region_field']} as region,
                COUNT(*) as total_incidents,
                COUNT(CASE WHEN UPPER({config['serious_field']}) = 'YES' THEN 1 END) as serious_incidents,
                COUNT(CASE WHEN UPPER({config['work_stopped_field']}) = 'YES' THEN 1 END) as work_stoppages,
                COUNT(DISTINCT {config['location_field']}) as unique_locations,
                COUNT(DISTINCT {config['event_type_field']}) as unique_event_types,
                ROUND(COUNT(CASE WHEN UPPER({config['serious_field']}) = 'YES' THEN 1 END) * 100.0 /
                      NULLIF(COUNT(*), 0), 2) as serious_incident_rate,
                ROUND(COUNT(CASE WHEN UPPER({config['work_stopped_field']}) = 'YES' THEN 1 END) * 100.0 /
                      NULLIF(COUNT(*), 0), 2) as work_stoppage_rate,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage_of_total_incidents,
                ROUND(
                    (COUNT(CASE WHEN UPPER({config['serious_field']}) = 'YES' THEN 1 END) * 3 +
                     COUNT(CASE WHEN UPPER({config['work_stopped_field']}) = 'YES' THEN 1 END) * 2) * 100.0 /
                    NULLIF(COUNT(*), 0), 2
                ) as performance_score
            FROM {config['table_name']}
            WHERE {config['branch_field']} IS NOT NULL
                AND {config['event_date_field']} BETWEEN :start_date AND :end_date
                {region_filter}
            GROUP BY {config['branch_field']}, {config['region_field']}
            ORDER BY performance_score DESC, total_incidents DESC
            LIMIT 15
            """

            params = {"start_date": start_date, "end_date": end_date}
            if region:
                params["region"] = region

            return self.execute_query(query, params)

        except Exception as e:
            logger.error(f"Error getting branch performance analysis: {e}")
            return []



    def _get_event_type_distribution(self, config: Dict, start_date: str, end_date: str, region: str = None) -> List[Dict]:
        """KPI 7: Event Type Distribution"""
        try:
            region_filter = f"AND {config['region_field']} = :region" if region else ""

            query = f"""
            SELECT
                {config['event_type_field']} as event_type,
                COUNT(*) as event_count,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
            FROM {config['table_name']}
            WHERE {config['event_type_field']} IS NOT NULL
                AND {config['event_date_field']} BETWEEN :start_date AND :end_date
                {region_filter}
            GROUP BY {config['event_type_field']}
            ORDER BY event_count DESC
            LIMIT 10
            """

            params = {"start_date": start_date, "end_date": end_date}
            if region:
                params["region"] = region

            return self.execute_query(query, params)

        except Exception as e:
            logger.error(f"Error getting event type distribution: {e}")
            return []

    def _get_repeat_locations(self, config: Dict, start_date: str, end_date: str, region: str = None) -> List[Dict]:
        """KPI 8: Repeat Locations"""
        try:
            region_filter = f"AND {config['region_field']} = :region" if region else ""

            query = f"""
            SELECT
                {config['location_field']} as location,
                {config['region_field']} as region,
                COUNT(*) as incident_count,
                COUNT(CASE WHEN UPPER({config['work_stopped_field']}) = 'YES' THEN 1 END) as work_stopped_incidents,
                COUNT(CASE WHEN UPPER({config['serious_field']}) = 'YES' THEN 1 END) as serious_incidents,
                ROUND(COUNT(CASE WHEN UPPER({config['work_stopped_field']}) = 'YES' THEN 1 END) * 100.0 /
                      NULLIF(COUNT(*), 0), 2) as work_stopped_rate,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage_of_total
            FROM {config['table_name']}
            WHERE {config['location_field']} IS NOT NULL
                AND {config['event_date_field']} BETWEEN :start_date AND :end_date
                {region_filter}
            GROUP BY {config['location_field']}, {config['region_field']}
            HAVING COUNT(*) > 1
            ORDER BY incident_count DESC
            LIMIT 10
            """

            params = {"start_date": start_date, "end_date": end_date}
            if region:
                params["region"] = region

            return self.execute_query(query, params)

        except Exception as e:
            logger.error(f"Error getting repeat locations: {e}")
            return []

    def _get_response_time_analysis(self, config: Dict, start_date: str, end_date: str, region: str = None) -> Dict[str, Any]:
        """KPI 9: Response Time Analysis"""
        try:
            region_filter = f"AND {config['region_field']} = :region" if region else ""

            query = f"""
            SELECT
                AVG(CASE
                    WHEN {config['event_date_field']} IS NOT NULL AND {config['reported_date_field']} IS NOT NULL
                    THEN {config['reported_date_field']}::date - {config['event_date_field']}::date
                END) as avg_reporting_delay_days,
                COUNT(CASE
                    WHEN {config['event_date_field']} IS NOT NULL AND {config['reported_date_field']} IS NOT NULL
                    THEN 1
                END) as events_with_timing_data
            FROM {config['table_name']}
            WHERE {config['event_date_field']} BETWEEN :start_date AND :end_date
                {region_filter}
            """

            params = {"start_date": start_date, "end_date": end_date}
            if region:
                params["region"] = region

            result = self.execute_query(query, params)
            data = result[0] if result else {"avg_reporting_delay_days": None, "events_with_timing_data": 0}

            avg_delay = data.get("avg_reporting_delay_days")
            if avg_delay is not None:
                return {
                    "average_response_time": f"{float(avg_delay):.2f} days",
                    "median_response_time": "N/A",
                    "events_analyzed": data.get("events_with_timing_data", 0),
                    "description": "Average time between incident occurrence and reporting"
                }
            else:
                return {
                    "average_response_time": "N/A",
                    "median_response_time": "N/A",
                    "events_analyzed": 0,
                    "description": "Response time analysis not available - insufficient timing data"
                }

        except Exception as e:
            logger.error(f"Error getting response time analysis: {e}")
            return {
                "average_response_time": "N/A",
                "median_response_time": "N/A",
                "events_analyzed": 0,
                "description": "Error retrieving response time data"
            }

    def _get_safety_performance_trends(self, config: Dict, start_date: str, end_date: str, region: str = None) -> List[Dict]:
        """KPI 10: Safety Performance Trends - Quarterly performance comparison"""
        try:
            region_filter = f"AND {config['region_field']} = :region" if region else ""

            query = f"""
            SELECT
                EXTRACT(YEAR FROM {config['event_date_field']}) as year,
                EXTRACT(QUARTER FROM {config['event_date_field']}) as quarter,
                CONCAT(EXTRACT(YEAR FROM {config['event_date_field']}), '-Q', EXTRACT(QUARTER FROM {config['event_date_field']})) as period,
                COUNT(*) as total_incidents,
                COUNT(CASE WHEN UPPER({config['serious_field']}) = 'YES' THEN 1 END) as serious_incidents,
                COUNT(CASE WHEN UPPER({config['work_stopped_field']}) = 'YES' THEN 1 END) as work_stoppages,
                COUNT(DISTINCT {config['branch_field']}) as branches_affected,
                COUNT(DISTINCT {config['location_field']}) as locations_affected,
                ROUND(COUNT(CASE WHEN UPPER({config['serious_field']}) = 'YES' THEN 1 END) * 100.0 /
                      NULLIF(COUNT(*), 0), 2) as serious_incident_rate,
                ROUND(COUNT(CASE WHEN UPPER({config['work_stopped_field']}) = 'YES' THEN 1 END) * 100.0 /
                      NULLIF(COUNT(*), 0), 2) as work_stoppage_rate,
                LAG(COUNT(*)) OVER (ORDER BY EXTRACT(YEAR FROM {config['event_date_field']}), EXTRACT(QUARTER FROM {config['event_date_field']})) as previous_quarter_incidents,
                ROUND(
                    (COUNT(*) - LAG(COUNT(*)) OVER (ORDER BY EXTRACT(YEAR FROM {config['event_date_field']}), EXTRACT(QUARTER FROM {config['event_date_field']}))) * 100.0 /
                    NULLIF(LAG(COUNT(*)) OVER (ORDER BY EXTRACT(YEAR FROM {config['event_date_field']}), EXTRACT(QUARTER FROM {config['event_date_field']})), 0), 2
                ) as quarter_over_quarter_change
            FROM {config['table_name']}
            WHERE {config['event_date_field']} BETWEEN :start_date AND :end_date
                {region_filter}
            GROUP BY EXTRACT(YEAR FROM {config['event_date_field']}), EXTRACT(QUARTER FROM {config['event_date_field']})
            ORDER BY year DESC, quarter DESC
            LIMIT 8
            """

            params = {"start_date": start_date, "end_date": end_date}
            if region:
                params["region"] = region

            return self.execute_query(query, params)

        except Exception as e:
            logger.error(f"Error getting safety performance trends: {e}")
            return []

    def _get_incident_severity_distribution(self, config: Dict, start_date: str, end_date: str, region: str = None) -> List[Dict]:
        """KPI 11: Incident Severity Distribution - Analysis of incident severity levels"""
        try:
            region_filter = f"AND {config['region_field']} = :region" if region else ""

            # Robust approach - handles different value formats (YES/Yes/yes, NO/No/no, etc.)
            query = f"""
            WITH severity_data AS (
                SELECT
                    COUNT(*) as total_incidents,
                    COUNT(CASE WHEN UPPER(COALESCE({config['serious_field']}, '')) IN ('YES', 'Y', '1', 'TRUE')
                               AND UPPER(COALESCE({config['work_stopped_field']}, '')) IN ('YES', 'Y', '1', 'TRUE') THEN 1 END) as critical_count,
                    COUNT(CASE WHEN UPPER(COALESCE({config['serious_field']}, '')) IN ('YES', 'Y', '1', 'TRUE')
                               AND UPPER(COALESCE({config['work_stopped_field']}, '')) NOT IN ('YES', 'Y', '1', 'TRUE') THEN 1 END) as high_count,
                    COUNT(CASE WHEN UPPER(COALESCE({config['serious_field']}, '')) NOT IN ('YES', 'Y', '1', 'TRUE')
                               AND UPPER(COALESCE({config['work_stopped_field']}, '')) IN ('YES', 'Y', '1', 'TRUE') THEN 1 END) as medium_work_stopped,
                    COUNT(CASE WHEN UPPER(COALESCE({config['serious_field']}, '')) NOT IN ('YES', 'Y', '1', 'TRUE')
                               AND UPPER(COALESCE({config['work_stopped_field']}, '')) NOT IN ('YES', 'Y', '1', 'TRUE') THEN 1 END) as low_count
                FROM {config['table_name']}
                WHERE {config['event_date_field']} BETWEEN :start_date AND :end_date
                    {region_filter}
            )
            SELECT 'Critical' as severity_level, critical_count as incident_count,
                   ROUND(critical_count * 100.0 / NULLIF(total_incidents, 0), 2) as percentage,
                   1 as sort_order
            FROM severity_data WHERE critical_count > 0
            UNION ALL
            SELECT 'High' as severity_level, high_count as incident_count,
                   ROUND(high_count * 100.0 / NULLIF(total_incidents, 0), 2) as percentage,
                   2 as sort_order
            FROM severity_data WHERE high_count > 0
            UNION ALL
            SELECT 'Medium' as severity_level, medium_work_stopped as incident_count,
                   ROUND(medium_work_stopped * 100.0 / NULLIF(total_incidents, 0), 2) as percentage,
                   3 as sort_order
            FROM severity_data WHERE medium_work_stopped > 0
            UNION ALL
            SELECT 'Low' as severity_level, low_count as incident_count,
                   ROUND(low_count * 100.0 / NULLIF(total_incidents, 0), 2) as percentage,
                   4 as sort_order
            FROM severity_data WHERE low_count > 0
            ORDER BY sort_order
            """

            params = {"start_date": start_date, "end_date": end_date}
            if region:
                params["region"] = region

            result = self.execute_query(query, params)

            # If no results, return a basic structure showing all severity levels with 0 counts
            if not result:
                # Get total count to see if there's any data at all
                count_query = f"""
                SELECT COUNT(*) as total_count
                FROM {config['table_name']}
                WHERE {config['event_date_field']} BETWEEN :start_date AND :end_date
                    {region_filter}
                """
                count_result = self.execute_query(count_query, params)
                total_count = count_result[0].get('total_count', 0) if count_result else 0

                if total_count > 0:
                    # There is data, but all incidents are "Low" severity
                    return [{
                        'severity_level': 'Low',
                        'incident_count': total_count,
                        'percentage': 100.0,
                        'sort_order': 4
                    }]
                else:
                    # No data at all
                    return []

            return result

        except Exception as e:
            logger.error(f"Error getting incident severity distribution: {e}")
            return []

    def _get_operational_impact_analysis(self, config: Dict, start_date: str, end_date: str, region: str = None) -> Dict[str, Any]:
        """KPI 12: Operational Impact Analysis - Business impact assessment"""
        try:
            region_filter = f"AND {config['region_field']} = :region" if region else ""

            query = f"""
            SELECT
                COUNT(*) as total_incidents,
                COUNT(CASE WHEN UPPER({config['work_stopped_field']}) = 'YES' THEN 1 END) as work_stopped_incidents,
                COUNT(CASE WHEN UPPER({config['serious_field']}) = 'YES' THEN 1 END) as serious_incidents,
                COUNT(DISTINCT {config['branch_field']}) as branches_impacted,
                COUNT(DISTINCT {config['location_field']}) as locations_impacted,
                COUNT(DISTINCT {config['event_type_field']}) as incident_types,
                ROUND(COUNT(CASE WHEN UPPER({config['work_stopped_field']}) = 'YES' THEN 1 END) * 100.0 /
                      NULLIF(COUNT(*), 0), 2) as operational_disruption_rate,
                ROUND(COUNT(CASE WHEN UPPER({config['serious_field']}) = 'YES' THEN 1 END) * 100.0 /
                      NULLIF(COUNT(*), 0), 2) as safety_risk_rate,
                ROUND(
                    (COUNT(CASE WHEN UPPER({config['work_stopped_field']}) = 'YES' THEN 1 END) * 1.0 +
                     COUNT(CASE WHEN UPPER({config['serious_field']}) = 'YES' THEN 1 END) * 2.0) /
                    NULLIF(COUNT(*), 0), 2
                ) as overall_impact_score
            FROM {config['table_name']}
            WHERE {config['event_date_field']} BETWEEN :start_date AND :end_date
                {region_filter}
            """

            params = {"start_date": start_date, "end_date": end_date}
            if region:
                params["region"] = region

            result = self.execute_query(query, params)
            data = result[0] if result else {}

            return {
                "summary": {
                    "total_incidents": data.get("total_incidents", 0),
                    "branches_impacted": data.get("branches_impacted", 0),
                    "locations_impacted": data.get("locations_impacted", 0),
                    "incident_types": data.get("incident_types", 0)
                },
                "impact_metrics": {
                    "operational_disruption_rate": float(data.get("operational_disruption_rate", 0.0)),
                    "safety_risk_rate": float(data.get("safety_risk_rate", 0.0)),
                    "overall_impact_score": float(data.get("overall_impact_score", 0.0))
                },
                "incident_breakdown": {
                    "work_stopped_incidents": data.get("work_stopped_incidents", 0),
                    "serious_incidents": data.get("serious_incidents", 0)
                },
                "description": "Comprehensive analysis of operational and business impact from safety incidents"
            }

        except Exception as e:
            logger.error(f"Error getting operational impact analysis: {e}")
            return {
                "summary": {"total_incidents": 0, "branches_impacted": 0, "locations_impacted": 0, "incident_types": 0},
                "impact_metrics": {"operational_disruption_rate": 0.0, "safety_risk_rate": 0.0, "compliance_risk_rate": 0.0, "overall_impact_score": 0.0},
                "incident_breakdown": {"work_stopped_incidents": 0, "serious_incidents": 0, "compliance_violations": 0},
                "description": "Error retrieving operational impact data"
            }

    def _get_time_based_analysis(self, config: Dict, start_date: str, end_date: str, region: str = None) -> Dict[str, Any]:
        """KPI 12: Time-based Analysis - Incidents by time of day and day of week"""
        try:
            region_filter = f"AND {config['region_field']} = :region" if region else ""

            # Check if this schema has time information (ni_tct and ni_tct_augmented have DateTime fields)
            schema_type = None
            for schema, schema_config in self.schema_configs.items():
                if schema_config['table_name'] == config['table_name']:
                    schema_type = schema
                    break

            has_time_data = schema_type in ['ni_tct', 'ni_tct_augmented']

            if has_time_data:
                # For NI TCT schemas: Use DateTime field with hour extraction
                time_of_day_query = f"""
                SELECT
                    CASE
                        WHEN EXTRACT(HOUR FROM {config['event_date_field']}) BETWEEN 6 AND 11 THEN 'Morning (6AM-12PM)'
                        WHEN EXTRACT(HOUR FROM {config['event_date_field']}) BETWEEN 12 AND 17 THEN 'Afternoon (12PM-6PM)'
                        WHEN EXTRACT(HOUR FROM {config['event_date_field']}) BETWEEN 18 AND 23 THEN 'Evening (6PM-12AM)'
                        ELSE 'Night (12AM-6AM)'
                    END as time_period,
                    COUNT(*) as incident_count,
                    COUNT(CASE WHEN UPPER({config['serious_field']}) = 'YES' THEN 1 END) as serious_incidents,
                    COUNT(CASE WHEN UPPER({config['work_stopped_field']}) = 'YES' THEN 1 END) as work_stopped_incidents,
                    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
                FROM {config['table_name']}
                WHERE {config['event_date_field']} BETWEEN :start_date AND :end_date
                    AND EXTRACT(HOUR FROM {config['event_date_field']}) IS NOT NULL
                    {region_filter}
                GROUP BY
                    CASE
                        WHEN EXTRACT(HOUR FROM {config['event_date_field']}) BETWEEN 6 AND 11 THEN 'Morning (6AM-12PM)'
                        WHEN EXTRACT(HOUR FROM {config['event_date_field']}) BETWEEN 12 AND 17 THEN 'Afternoon (12PM-6PM)'
                        WHEN EXTRACT(HOUR FROM {config['event_date_field']}) BETWEEN 18 AND 23 THEN 'Evening (6PM-12AM)'
                        ELSE 'Night (12AM-6AM)'
                    END
                ORDER BY incident_count DESC
                """
            else:
                # For SRS and EI Tech schemas: Only date available, so provide a simplified analysis
                time_of_day_query = f"""
                SELECT
                    'All Day' as time_period,
                    COUNT(*) as incident_count,
                    COUNT(CASE WHEN UPPER({config['serious_field']}) = 'YES' THEN 1 END) as serious_incidents,
                    COUNT(CASE WHEN UPPER({config['work_stopped_field']}) = 'YES' THEN 1 END) as work_stopped_incidents,
                    100.0 as percentage
                FROM {config['table_name']}
                WHERE {config['event_date_field']} BETWEEN :start_date AND :end_date
                    {region_filter}
                """

            # Day of week analysis (works for both Date and DateTime fields)
            day_of_week_query = f"""
            SELECT
                TO_CHAR({config['event_date_field']}, 'Day') as day_of_week,
                EXTRACT(DOW FROM {config['event_date_field']}) as day_number,
                COUNT(*) as incident_count,
                COUNT(CASE WHEN UPPER({config['serious_field']}) = 'YES' THEN 1 END) as serious_incidents,
                COUNT(CASE WHEN UPPER({config['work_stopped_field']}) = 'YES' THEN 1 END) as work_stopped_incidents,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
            FROM {config['table_name']}
            WHERE {config['event_date_field']} BETWEEN :start_date AND :end_date
                {region_filter}
            GROUP BY TO_CHAR({config['event_date_field']}, 'Day'), EXTRACT(DOW FROM {config['event_date_field']})
            ORDER BY day_number
            """

            params = {"start_date": start_date, "end_date": end_date}
            if region:
                params["region"] = region

            time_of_day_results = self.execute_query(time_of_day_query, params)
            day_of_week_results = self.execute_query(day_of_week_query, params)

            # Calculate peak times
            peak_time_period = max(time_of_day_results, key=lambda x: x['incident_count'])['time_period'] if time_of_day_results else "N/A"
            peak_day = max(day_of_week_results, key=lambda x: x['incident_count'])['day_of_week'].strip() if day_of_week_results else "N/A"

            return {
                "time_of_day_analysis": time_of_day_results,
                "day_of_week_analysis": day_of_week_results,
                "peak_patterns": {
                    "peak_time_period": peak_time_period,
                    "peak_day_of_week": peak_day
                },
                "summary": {
                    "total_time_periods_analyzed": len(time_of_day_results),
                    "total_days_analyzed": len(day_of_week_results),
                    "description": f"Time-based incident pattern analysis ({'with hourly data' if has_time_data else 'date-only data'})",
                    "has_hourly_data": has_time_data
                }
            }

        except Exception as e:
            logger.error(f"Error getting time-based analysis: {e}")
            return {
                "time_of_day_analysis": [],
                "day_of_week_analysis": [],
                "peak_patterns": {
                    "peak_time_period": "N/A",
                    "peak_day_of_week": "N/A"
                },
                "summary": {
                    "total_time_periods_analyzed": 0,
                    "total_days_analyzed": 0,
                    "description": "Error retrieving time-based analysis data",
                    "has_hourly_data": False
                }
            }

    # ==================== UTILITY METHODS ====================

    def _get_empty_dashboard_data(self) -> Dict[str, Any]:
        """Return empty dashboard data structure for all 12 KPIs"""
        return {
            "total_events": {
                "count": {"total_events": 0, "unique_events": 0},
                "description": "No data available"
            },
            "serious_near_miss_rate": {
                "rate": 0.0,
                "count": {
                    "serious_near_miss_count": 0,
                    "non_serious_count": 0,
                    "total_events": 0,
                    "serious_near_miss_percentage": "0.0"
                },
                "description": "No data available"
            },
            "work_stoppage_rate": {
                "rate": 0.0,
                "count": 0,
                "total": {"total_events": 0, "unique_events": 0},
                "description": "No data available"
            },
            "monthly_trends": [],
            "branch_performance_analysis": [],
            "event_type_distribution": [],
            "repeat_locations": [],
            "response_time_analysis": {
                "average_response_time": "N/A",
                "median_response_time": "N/A",
                "events_analyzed": 0,
                "description": "No data available"
            },
            "safety_performance_trends": [],
            "incident_severity_distribution": [],
            "operational_impact_analysis": {
                "summary": {"total_incidents": 0, "branches_impacted": 0, "locations_impacted": 0, "incident_types": 0},
                "impact_metrics": {"operational_disruption_rate": 0.0, "safety_risk_rate": 0.0, "overall_impact_score": 0.0},
                "incident_breakdown": {"work_stopped_incidents": 0, "serious_incidents": 0},
                "description": "No data available"
            },
            "time_based_analysis": {
                "time_of_day_analysis": [],
                "day_of_week_analysis": [],
                "peak_patterns": {
                    "peak_time_period": "N/A",
                    "peak_day_of_week": "N/A"
                },
                "summary": {
                    "total_time_periods_analyzed": 0,
                    "total_days_analyzed": 0,
                    "description": "No data available",
                    "has_hourly_data": False
                }
            }
        }
