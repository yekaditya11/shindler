"""
Unified KPI Service for generating insights from all 3 safety data sources
Selects only the most important KPIs from each source to avoid token limits
Uses parallel execution to reduce response time from ~30s to ~10s
"""

import logging
import asyncio
from typing import Dict, Any
from src.analytics.srs_kpi_queries import SRSKPIQueries
from src.analytics.ei_tech_kpi_queries import EITechKPIQueries
from src.analytics.ni_tct_kpi_queries import NITCTKPIQueries

logger = logging.getLogger(__name__)


class UnifiedKPIService:
    """Service for getting essential KPIs from all 3 safety data sources"""

    def __init__(self):
        self.srs_analytics = SRSKPIQueries()
        self.ei_tech_analytics = EITechKPIQueries()
        self.ni_tct_analytics = NITCTKPIQueries()

    async def get_essential_kpis_all_sources(self) -> Dict[str, Any]:
        """
        Get only the most important KPIs from all 3 sources for comprehensive insights
        Uses parallel execution to reduce response time significantly

        Returns:
            Dictionary containing essential KPIs from SRS, EI Tech, and NI TCT
        """
        try:
            logger.info("Fetching essential KPIs from all 3 safety data sources in parallel...")
            start_time = asyncio.get_event_loop().time()

            # Execute all 3 data source queries in parallel using ThreadPoolExecutor
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                # Submit all tasks
                srs_future = executor.submit(self._get_essential_srs_kpis)
                ei_tech_future = executor.submit(self._get_essential_ei_tech_kpis)
                ni_tct_future = executor.submit(self._get_essential_ni_tct_kpis)

                # Wait for all tasks to complete
                srs_data = srs_future.result()
                ei_tech_data = ei_tech_future.result()
                ni_tct_data = ni_tct_future.result()

            unified_data = {
                "srs_data": srs_data,
                "ei_tech_data": ei_tech_data,
                "ni_tct_data": ni_tct_data
            }

            end_time = asyncio.get_event_loop().time()
            execution_time = end_time - start_time
            logger.info(f"Successfully fetched essential KPIs from all sources in {execution_time:.2f} seconds")
            return unified_data

        except Exception as e:
            logger.error(f"Error fetching unified KPIs: {e}")
            raise

    def get_essential_kpis_all_sources_sync(self) -> Dict[str, Any]:
        """
        Synchronous version for backward compatibility
        """
        try:
            logger.info("Fetching essential KPIs from all 3 safety data sources (sync)...")

            unified_data = {
                "srs_data": self._get_essential_srs_kpis(),
                "ei_tech_data": self._get_essential_ei_tech_kpis(),
                "ni_tct_data": self._get_essential_ni_tct_kpis()
            }

            logger.info("Successfully fetched essential KPIs from all sources")
            return unified_data

        except Exception as e:
            logger.error(f"Error fetching unified KPIs: {e}")
            raise

    def _get_essential_srs_kpis(self) -> Dict[str, Any]:
        """Get most important KPIs from SRS data with parallel execution"""
        try:
            logger.info("Fetching essential SRS KPIs...")

            # Define KPI functions to execute in parallel
            kpi_functions = {
                # Core Safety Metrics
                "total_events": lambda: self.srs_analytics.get_total_events_count(),
                "serious_near_misses": lambda: self.srs_analytics.get_serious_near_miss_count(),
                "work_stopped_incidents": lambda: self.srs_analytics.get_work_stopped_incidents(),
                "nogo_violations": lambda: self.srs_analytics.get_nogo_violations_count(),

                # Geographic Risk Analysis
                "events_by_branch": lambda: self.srs_analytics.get_events_by_branch(),
                "events_by_region": lambda: self.srs_analytics.get_events_by_region_country_division(),
                "at_risk_regions": lambda: self.srs_analytics.get_at_risk_regions(),

                # Behavioral Patterns
                "unsafe_behaviors": lambda: self.srs_analytics.get_common_unsafe_behaviors(),
                "unsafe_conditions": lambda: self.srs_analytics.get_common_unsafe_conditions(),

                # Response & Actions
                "action_compliance": lambda: self.srs_analytics.get_action_creation_and_compliance(),
                "reporting_delays": lambda: self.srs_analytics.get_average_time_between_event_and_reporting(),

                # Trends
                "monthly_trends": lambda: self.srs_analytics.get_events_per_time_period('month'),
                "branch_risk_index": lambda: self.srs_analytics.get_branch_risk_index()
            }

            # Execute all KPI queries in parallel
            essential_kpis = self._execute_kpis_parallel(kpi_functions, "SRS")
            return essential_kpis

        except Exception as e:
            logger.error(f"Error fetching SRS KPIs: {e}")
            return {}

    def _execute_kpis_parallel(self, kpi_functions: Dict[str, callable], source_name: str) -> Dict[str, Any]:
        """Execute KPI functions in parallel using ThreadPoolExecutor"""
        try:
            results = {}

            # Use ThreadPoolExecutor to run queries in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                # Submit all KPI functions
                future_to_kpi = {
                    executor.submit(func): kpi_name
                    for kpi_name, func in kpi_functions.items()
                }

                # Collect results as they complete
                for future in concurrent.futures.as_completed(future_to_kpi):
                    kpi_name = future_to_kpi[future]
                    try:
                        result = future.result(timeout=30)  # 30 second timeout per query
                        results[kpi_name] = result
                    except Exception as e:
                        logger.error(f"Error executing {source_name} KPI '{kpi_name}': {e}")
                        results[kpi_name] = {}  # Empty result for failed queries

            logger.info(f"Completed {len(results)}/{len(kpi_functions)} {source_name} KPIs")
            return results

        except Exception as e:
            logger.error(f"Error in parallel execution for {source_name}: {e}")
            return {}

    def _get_essential_ei_tech_kpis(self) -> Dict[str, Any]:
        """Get most important KPIs from EI Tech data with parallel execution"""
        try:
            logger.info("Fetching essential EI Tech KPIs...")

            # Define KPI functions to execute in parallel
            kpi_functions = {
                # Core Safety Metrics
                "total_events": lambda: self.ei_tech_analytics.get_total_events_count(),
                "serious_near_misses": lambda: self.ei_tech_analytics.get_serious_near_miss_count(),
                "nogo_violations": lambda: self.ei_tech_analytics.get_nogo_violations_count(),

                # Geographic Risk Analysis
                "events_by_branch": lambda: self.ei_tech_analytics.get_events_by_branch(),
                "events_by_region": lambda: self.ei_tech_analytics.get_events_by_region_country_division(),
                "high_risk_locations": lambda: self.ei_tech_analytics.get_high_risk_location_analysis(),

                # Behavioral & Operational Patterns
                "unsafe_behaviors": lambda: self.ei_tech_analytics.get_unsafe_acts_and_conditions_analysis(),
                "business_type_analysis": lambda: self.ei_tech_analytics.get_events_by_business_details(),
                "location_incidents": lambda: self.ei_tech_analytics.get_events_by_unsafe_event_location(),

                # Response Effectiveness
                "action_completion": lambda: self.ei_tech_analytics.get_action_completion_rate(),
                "reporting_delays": lambda: self.ei_tech_analytics.get_reporting_delay_analysis(),

                # Trends & Risk Analysis
                "monthly_trends": lambda: self.ei_tech_analytics.get_events_per_time_period('month'),
                "branch_risk_index": lambda: self.ei_tech_analytics.get_branch_risk_index(),
                "time_patterns": lambda: self.ei_tech_analytics.get_time_of_day_incident_patterns()
            }

            # Execute all KPI queries in parallel
            essential_kpis = self._execute_kpis_parallel(kpi_functions, "EI Tech")
            return essential_kpis

        except Exception as e:
            logger.error(f"Error fetching EI Tech KPIs: {e}")
            return {}

    def _get_essential_ni_tct_kpis(self) -> Dict[str, Any]:
        """Get most important KPIs from NI TCT data with parallel execution"""
        try:
            logger.info("Fetching essential NI TCT KPIs...")

            # Define KPI functions to execute in parallel
            kpi_functions = {
                # Core Safety Metrics
                "total_events": lambda: self.ni_tct_analytics.get_total_events_count(),
                "high_risk_situations": lambda: self.ni_tct_analytics.get_high_risk_situation_analysis(),
                "work_stopped_incidents": lambda: self.ni_tct_analytics.get_work_stopped_incidents(),
                "nogo_violations": lambda: self.ni_tct_analytics.get_nogo_violations_count(),

                # Geographic & Operational Risk
                "events_by_branch": lambda: self.ni_tct_analytics.get_events_by_branch(),
                "events_by_region": lambda: self.ni_tct_analytics.get_events_by_region(),
                "events_by_location": lambda: self.ni_tct_analytics.get_events_by_location(),
                "repeat_locations": lambda: self.ni_tct_analytics.get_repeat_location_analysis(),

                # Personnel & Management Analysis
                "group_leader_performance": lambda: self.ni_tct_analytics.get_group_leader_performance(),
                "project_engineer_performance": lambda: self.ni_tct_analytics.get_project_engineer_performance(),
                "events_by_designation": lambda: self.ni_tct_analytics.get_events_by_designation(),

                # Response & Documentation
                "high_risk_response": lambda: self.ni_tct_analytics.get_high_risk_response_effectiveness(),
                "documentation_quality": lambda: self.ni_tct_analytics.get_documentation_quality_score(),
                "reporting_delays": lambda: self.ni_tct_analytics.get_reporting_delay_analysis(),

                # Trends & Patterns
                "monthly_trends": lambda: self.ni_tct_analytics.get_events_per_time_period('month'),
                "seasonal_trends": lambda: self.ni_tct_analytics.get_seasonal_trend_analysis(),
                "business_analysis": lambda: self.ni_tct_analytics.get_events_by_business_details()
            }

            # Execute all KPI queries in parallel
            essential_kpis = self._execute_kpis_parallel(kpi_functions, "NI TCT")
            return essential_kpis

        except Exception as e:
            logger.error(f"Error fetching NI TCT KPIs: {e}")
            return {}

    async def get_summary_statistics(self) -> Dict[str, Any]:
        """Get high-level summary statistics across all 3 sources in parallel"""
        try:
            logger.info("Generating summary statistics across all sources...")

            # Get basic counts from each source in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                srs_future = executor.submit(self.srs_analytics.get_total_events_count)
                ei_tech_future = executor.submit(self.ei_tech_analytics.get_total_events_count)
                ni_tct_future = executor.submit(self.ni_tct_analytics.get_total_events_count)

                srs_total = srs_future.result()
                ei_tech_total = ei_tech_future.result()
                ni_tct_total = ni_tct_future.result()

            summary = {
                "cross_source_summary": {
                    "srs_total_events": srs_total.get('total_events', 0),
                    "ei_tech_total_events": ei_tech_total.get('total_events', 0),
                    "ni_tct_total_events": ni_tct_total.get('total_events', 0),
                    "combined_total_events": (
                        srs_total.get('total_events', 0) +
                        ei_tech_total.get('total_events', 0) +
                        ni_tct_total.get('total_events', 0)
                    )
                }
            }

            return summary

        except Exception as e:
            logger.error(f"Error generating summary statistics: {e}")
            return {}

    def get_summary_statistics_sync(self) -> Dict[str, Any]:
        """Synchronous version for backward compatibility"""
        try:
            logger.info("Generating summary statistics across all sources (sync)...")

            # Get basic counts from each source
            srs_total = self.srs_analytics.get_total_events_count()
            ei_tech_total = self.ei_tech_analytics.get_total_events_count()
            ni_tct_total = self.ni_tct_analytics.get_total_events_count()

            summary = {
                "cross_source_summary": {
                    "srs_total_events": srs_total.get('total_events', 0),
                    "ei_tech_total_events": ei_tech_total.get('total_events', 0),
                    "ni_tct_total_events": ni_tct_total.get('total_events', 0),
                    "combined_total_events": (
                        srs_total.get('total_events', 0) +
                        ei_tech_total.get('total_events', 0) +
                        ni_tct_total.get('total_events', 0)
                    )
                }
            }

            return summary

        except Exception as e:
            logger.error(f"Error generating summary statistics: {e}")
            return {}
