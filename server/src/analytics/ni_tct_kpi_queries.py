"""
NI TCT KPI Queries Module
Comprehensive KPI analytics for NI TCT (Non-Intrusive Testing) unsafe events
Author: AI Assistant
Date: 2025-07-14
"""

import logging
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.config.database import get_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NITCTKPIQueries:
    """SQL queries for NI TCT App KPIs"""
    
    def __init__(self):
        self.table_name = "unsafe_events_ni_tct"
    
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
    
    # ==================== EVENT VOLUME & FREQUENCY ====================
    
    def get_total_events_count(self) -> Dict[str, Any]:
        """Total events count"""
        query = f"""
        SELECT 
            COUNT(*) as total_events,
            COUNT(DISTINCT reporting_id) as unique_events,
            COUNT(CASE WHEN status IS NOT NULL THEN 1 END) as events_with_status
        FROM {self.table_name}
        WHERE reporting_id IS NOT NULL
        """
        return self.execute_query(query)[0]
    
    def get_events_by_unsafe_event_type(self) -> List[Dict]:
        """Events by type_of_unsafe_event"""
        query = f"""
        SELECT 
            type_of_unsafe_event,
            COUNT(*) as event_count,
            CAST((COUNT(*) * 100.0 / SUM(COUNT(*)) OVER()) AS DECIMAL(10,2)) as percentage
        FROM {self.table_name}
        WHERE type_of_unsafe_event IS NOT NULL
        GROUP BY type_of_unsafe_event
        ORDER BY event_count DESC
        """
        return self.execute_query(query)
    
    def get_events_per_time_period(self, period: str = 'month') -> List[Dict]:
        """Events per time period (month/week/quarter)"""
        if period == 'month':
            date_part = "EXTRACT(YEAR FROM date_and_time_of_unsafe_event), EXTRACT(MONTH FROM date_and_time_of_unsafe_event)"
            date_format = "CONCAT(EXTRACT(YEAR FROM date_and_time_of_unsafe_event), '-', LPAD(EXTRACT(MONTH FROM date_and_time_of_unsafe_event)::text, 2, '0'))"
        elif period == 'week':
            date_part = "EXTRACT(YEAR FROM date_and_time_of_unsafe_event), EXTRACT(WEEK FROM date_and_time_of_unsafe_event)"
            date_format = "CONCAT(EXTRACT(YEAR FROM date_and_time_of_unsafe_event), '-W', LPAD(EXTRACT(WEEK FROM date_and_time_of_unsafe_event)::text, 2, '0'))"
        elif period == 'quarter':
            date_part = "EXTRACT(YEAR FROM date_and_time_of_unsafe_event), EXTRACT(QUARTER FROM date_and_time_of_unsafe_event)"
            date_format = "CONCAT(EXTRACT(YEAR FROM date_and_time_of_unsafe_event), '-Q', EXTRACT(QUARTER FROM date_and_time_of_unsafe_event))"
        else:
            raise ValueError("Period must be 'month', 'week', or 'quarter'")
        
        query = f"""
        SELECT 
            {date_format} as time_period,
            COUNT(*) as event_count,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stopped_count,
            COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) as high_risk_actions,
            CAST((COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as work_stopped_percentage
        FROM {self.table_name}
        WHERE date_and_time_of_unsafe_event IS NOT NULL
        GROUP BY {date_part}
        ORDER BY {date_part}
        """
        return self.execute_query(query)
    
    def get_event_status_distribution(self) -> List[Dict]:
        """Distribution of events by status"""
        query = f"""
        SELECT 
            status,
            COUNT(*) as event_count,
            CAST((COUNT(*) * 100.0 / SUM(COUNT(*)) OVER()) AS DECIMAL(10,2)) as percentage
        FROM {self.table_name}
        WHERE status IS NOT NULL
        GROUP BY status
        ORDER BY event_count DESC
        """
        return self.execute_query(query)
    
    # ==================== SAFETY SEVERITY ====================
    
    def get_high_risk_situation_analysis(self) -> Dict[str, Any]:
        """Analysis of high-risk situation actions"""
        query = f"""
        SELECT 
            COUNT(*) as total_events,
            COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) as high_risk_actions,
            COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'NO' THEN 1 END) as no_high_risk_actions,
            CAST((COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as high_risk_action_percentage
        FROM {self.table_name}
        WHERE action_related_to_high_risk_situation IS NOT NULL
        """
        return self.execute_query(query)[0]
    
    def get_work_stopped_incidents(self) -> Dict[str, Any]:
        """Work stoppage incidents analysis"""
        query = f"""
        SELECT 
            COUNT(*) as total_events,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stopped_events,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'NO' THEN 1 END) as work_not_stopped_events,
            CAST((COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as work_stopped_percentage,
            COUNT(CASE WHEN work_stopped_hours IS NOT NULL AND work_stopped_hours != '' THEN 1 END) as events_with_duration_data
        FROM {self.table_name}
        WHERE work_was_stopped IS NOT NULL
        """
        return self.execute_query(query)[0]
    
    def get_nogo_violations_count(self) -> Dict[str, Any]:
        """No-Go violations analysis"""
        query = f"""
        SELECT
            COUNT(*) as total_events,
            COUNT(CASE WHEN no_go_violation IS NOT NULL AND no_go_violation != '' THEN 1 END) as events_with_nogo_violations,
            CAST((COUNT(CASE WHEN no_go_violation IS NOT NULL AND no_go_violation != '' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as nogo_violation_percentage
        FROM {self.table_name}
        """
        return self.execute_query(query)[0]

    def get_work_stoppage_duration_analysis(self) -> List[Dict]:
        """Analysis of work stoppage durations"""
        query = f"""
        SELECT
            work_stopped_hours,
            COUNT(*) as event_count,
            CAST((COUNT(*) * 100.0 / SUM(COUNT(*)) OVER()) AS DECIMAL(10,2)) as percentage
        FROM {self.table_name}
        WHERE UPPER(work_was_stopped) = 'YES'
        AND work_stopped_hours IS NOT NULL
        AND work_stopped_hours != ''
        GROUP BY work_stopped_hours
        ORDER BY event_count DESC
        """
        return self.execute_query(query)

    # ==================== GEOGRAPHIC DISTRIBUTION ====================

    def get_events_by_region(self) -> List[Dict]:
        """Events by region"""
        query = f"""
        SELECT
            region,
            COUNT(*) as event_count,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stopped_events,
            COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) as high_risk_actions,
            CAST((COUNT(*) * 100.0 / SUM(COUNT(*)) OVER()) AS DECIMAL(10,2)) as percentage,
            CAST((COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as work_stopped_rate
        FROM {self.table_name}
        WHERE region IS NOT NULL
        GROUP BY region
        ORDER BY event_count DESC
        """
        return self.execute_query(query)

    def get_events_by_branch(self) -> List[Dict]:
        """Events by branch"""
        query = f"""
        SELECT
            branch_name,
            COUNT(*) as event_count,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stopped_events,
            COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) as high_risk_actions,
            CAST((COUNT(*) * 100.0 / SUM(COUNT(*)) OVER()) AS DECIMAL(10,2)) as percentage,
            CAST((COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as work_stopped_rate
        FROM {self.table_name}
        WHERE branch_name IS NOT NULL
        GROUP BY branch_name
        ORDER BY event_count DESC
        LIMIT 25
        """
        return self.execute_query(query)

    def get_events_by_location(self) -> List[Dict]:
        """Events by location"""
        query = f"""
        SELECT
            location,
            COUNT(*) as event_count,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stopped_events,
            COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) as high_risk_actions,
            CAST((COUNT(*) * 100.0 / SUM(COUNT(*)) OVER()) AS DECIMAL(10,2)) as percentage,
            CAST((COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as work_stopped_rate
        FROM {self.table_name}
        WHERE location IS NOT NULL
        GROUP BY location
        ORDER BY event_count DESC
        LIMIT 25
        """
        return self.execute_query(query)

    # ==================== PERSONNEL METRICS ====================

    def get_events_by_reporter(self) -> List[Dict]:
        """Events by reporter"""
        query = f"""
        SELECT
            reporter_name,
            reporter_sap_id,
            designation,
            COUNT(*) as event_count,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stopped_events,
            COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) as high_risk_actions,
            CAST((COUNT(*) * 100.0 / SUM(COUNT(*)) OVER()) AS DECIMAL(10,2)) as percentage
        FROM {self.table_name}
        WHERE reporter_name IS NOT NULL
        GROUP BY reporter_name, reporter_sap_id, designation
        ORDER BY event_count DESC
        LIMIT 25
        """
        return self.execute_query(query)

    def get_events_by_designation(self) -> List[Dict]:
        """Events by designation"""
        query = f"""
        SELECT
            designation,
            COUNT(*) as event_count,
            COUNT(DISTINCT reporter_name) as unique_reporters,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stopped_events,
            COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) as high_risk_actions,
            CAST((COUNT(*) * 100.0 / SUM(COUNT(*)) OVER()) AS DECIMAL(10,2)) as percentage,
            CAST((COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as work_stopped_rate
        FROM {self.table_name}
        WHERE designation IS NOT NULL
        GROUP BY designation
        ORDER BY event_count DESC
        """
        return self.execute_query(query)

    # ==================== HIERARCHICAL ANALYSIS ====================

    def get_gl_pe_hierarchy_analysis(self) -> List[Dict]:
        """Analysis of Group Leader (GL) and Project Engineer (PE) hierarchy"""
        query = f"""
        SELECT
            gl_id,
            pe_id,
            COUNT(*) as event_count,
            COUNT(DISTINCT reporter_name) as unique_reporters,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stopped_events,
            COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) as high_risk_actions,
            CAST((COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as work_stopped_rate,
            CAST((COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as high_risk_action_rate
        FROM {self.table_name}
        WHERE gl_id IS NOT NULL AND pe_id IS NOT NULL
        GROUP BY gl_id, pe_id
        ORDER BY event_count DESC
        LIMIT 25
        """
        return self.execute_query(query)

    def get_group_leader_performance(self) -> List[Dict]:
        """Performance analysis by Group Leader"""
        query = f"""
        SELECT
            gl_id,
            COUNT(*) as total_events,
            COUNT(DISTINCT pe_id) as unique_pes_managed,
            COUNT(DISTINCT reporter_name) as unique_reporters,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stopped_events,
            COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) as high_risk_actions,
            COUNT(CASE WHEN has_attachment = true THEN 1 END) as events_with_attachments,
            CAST((COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as work_stopped_rate,
            CAST((COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as high_risk_action_rate,
            CAST((COUNT(CASE WHEN has_attachment = true THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as attachment_rate
        FROM {self.table_name}
        WHERE gl_id IS NOT NULL
        GROUP BY gl_id
        ORDER BY total_events DESC
        LIMIT 20
        """
        return self.execute_query(query)

    def get_project_engineer_performance(self) -> List[Dict]:
        """Performance analysis by Project Engineer"""
        query = f"""
        SELECT
            pe_id,
            gl_id,
            COUNT(*) as total_events,
            COUNT(DISTINCT reporter_name) as unique_reporters,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stopped_events,
            COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) as high_risk_actions,
            COUNT(CASE WHEN has_attachment = true THEN 1 END) as events_with_attachments,
            CAST((COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as work_stopped_rate,
            CAST((COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as high_risk_action_rate,
            CAST((COUNT(CASE WHEN has_attachment = true THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as attachment_rate
        FROM {self.table_name}
        WHERE pe_id IS NOT NULL
        GROUP BY pe_id, gl_id
        ORDER BY total_events DESC
        LIMIT 20
        """
        return self.execute_query(query)

    # ==================== OPERATIONAL METRICS ====================

    def get_events_by_product_type(self) -> List[Dict]:
        """Events by product type"""
        query = f"""
        SELECT
            product_type,
            COUNT(*) as event_count,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stopped_events,
            COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) as high_risk_actions,
            CAST((COUNT(*) * 100.0 / SUM(COUNT(*)) OVER()) AS DECIMAL(10,2)) as percentage,
            CAST((COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as work_stopped_rate
        FROM {self.table_name}
        WHERE product_type IS NOT NULL
        GROUP BY product_type
        ORDER BY event_count DESC
        """
        return self.execute_query(query)

    def get_events_by_business_details(self) -> List[Dict]:
        """Events by business details"""
        query = f"""
        SELECT
            business_details,
            COUNT(*) as event_count,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stopped_events,
            COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) as high_risk_actions,
            CAST((COUNT(*) * 100.0 / SUM(COUNT(*)) OVER()) AS DECIMAL(10,2)) as percentage,
            CAST((COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as work_stopped_rate
        FROM {self.table_name}
        WHERE business_details IS NOT NULL
        GROUP BY business_details
        ORDER BY event_count DESC
        """
        return self.execute_query(query)

    def get_attachment_utilization_analysis(self) -> Dict[str, Any]:
        """Analysis of attachment utilization"""
        query = f"""
        SELECT
            COUNT(*) as total_events,
            COUNT(CASE WHEN has_attachment = true THEN 1 END) as events_with_attachments,
            COUNT(CASE WHEN has_attachment = false OR has_attachment IS NULL THEN 1 END) as events_without_attachments,
            CAST((COUNT(CASE WHEN has_attachment = true THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as attachment_utilization_rate,
            COUNT(CASE WHEN has_attachment IS NOT NULL THEN 1 END) as events_with_attachment_data
        FROM {self.table_name}
        """
        return self.execute_query(query)[0]

    def get_job_specific_analysis(self) -> List[Dict]:
        """Analysis by job number"""
        query = f"""
        SELECT
            job_no,
            COUNT(*) as event_count,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stopped_events,
            COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) as high_risk_actions,
            COUNT(CASE WHEN no_go_violation IS NOT NULL AND no_go_violation != '' THEN 1 END) as nogo_violations,
            CAST((COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as work_stopped_rate,
            CAST((COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as high_risk_action_rate
        FROM {self.table_name}
        WHERE job_no IS NOT NULL AND job_no != ''
        GROUP BY job_no
        HAVING COUNT(*) >= 2
        ORDER BY event_count DESC
        LIMIT 25
        """
        return self.execute_query(query)

    # ==================== ADVANCED ANALYTICS ====================

    def get_reporting_delay_analysis(self) -> Dict[str, Any]:
        """Analysis of reporting delays"""
        query = f"""
        SELECT
            COUNT(*) as total_events,
            COUNT(CASE WHEN DATE(created_on) = DATE(date_and_time_of_unsafe_event) THEN 1 END) as same_day_reports,
            COUNT(CASE WHEN DATE(created_on) - DATE(date_and_time_of_unsafe_event) BETWEEN 1 AND 3 THEN 1 END) as reports_1_3_days,
            COUNT(CASE WHEN DATE(created_on) - DATE(date_and_time_of_unsafe_event) BETWEEN 4 AND 7 THEN 1 END) as reports_4_7_days,
            COUNT(CASE WHEN DATE(created_on) - DATE(date_and_time_of_unsafe_event) > 7 THEN 1 END) as reports_over_7_days,
            CAST((AVG(DATE(created_on) - DATE(date_and_time_of_unsafe_event))) AS DECIMAL(10,2)) as avg_delay_days,
            CAST((COUNT(CASE WHEN DATE(created_on) = DATE(date_and_time_of_unsafe_event) THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as same_day_reporting_rate
        FROM {self.table_name}
        WHERE created_on IS NOT NULL AND date_and_time_of_unsafe_event IS NOT NULL
        """
        return self.execute_query(query)[0]

    def get_repeat_location_analysis(self) -> List[Dict]:
        """Analysis of repeat incidents at same locations"""
        query = f"""
        SELECT
            location,
            site_name,
            COUNT(*) as incident_count,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stopped_incidents,
            COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) as high_risk_actions,
            COUNT(DISTINCT reporter_name) as unique_reporters,
            COUNT(DISTINCT type_of_unsafe_event) as unique_event_types,
            CAST((COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as work_stopped_rate,
            CAST((COUNT(*) * 100.0 / SUM(COUNT(*)) OVER()) AS DECIMAL(10,2)) as percentage_of_total
        FROM {self.table_name}
        WHERE location IS NOT NULL
        GROUP BY location, site_name
        HAVING COUNT(*) >= 3
        ORDER BY incident_count DESC
        LIMIT 20
        """
        return self.execute_query(query)

    def get_high_risk_response_effectiveness(self) -> List[Dict]:
        """Analysis of high-risk situation response effectiveness"""
        query = f"""
        SELECT
            type_of_unsafe_event,
            COUNT(*) as total_events,
            COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) as high_risk_responses,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stopped_events,
            COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES'
                       AND UPPER(work_was_stopped) = 'YES' THEN 1 END) as high_risk_with_work_stop,
            CAST((COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as high_risk_response_rate,
            CAST((COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as work_stopped_rate,
            CAST((COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES'
                             AND UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END), 0)) AS DECIMAL(10,2)) as work_stop_effectiveness
        FROM {self.table_name}
        WHERE type_of_unsafe_event IS NOT NULL
        GROUP BY type_of_unsafe_event
        HAVING COUNT(*) >= 5
        ORDER BY total_events DESC
        """
        return self.execute_query(query)

    def get_documentation_quality_score(self) -> Dict[str, Any]:
        """Calculate documentation quality score"""
        query = f"""
        SELECT
            COUNT(*) as total_events,
            COUNT(CASE WHEN unsafe_event_details IS NOT NULL AND LENGTH(TRIM(unsafe_event_details)) > 10 THEN 1 END) as detailed_descriptions,
            COUNT(CASE WHEN additional_comments IS NOT NULL AND LENGTH(TRIM(additional_comments)) > 10 THEN 1 END) as events_with_comments,
            COUNT(CASE WHEN has_attachment = true THEN 1 END) as events_with_attachments,
            COUNT(CASE WHEN persons_involved IS NOT NULL AND LENGTH(TRIM(persons_involved)) > 0 THEN 1 END) as events_with_persons_involved,
            CAST((COUNT(CASE WHEN unsafe_event_details IS NOT NULL AND LENGTH(TRIM(unsafe_event_details)) > 10 THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as detailed_description_rate,
            CAST((COUNT(CASE WHEN additional_comments IS NOT NULL AND LENGTH(TRIM(additional_comments)) > 10 THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as comments_completion_rate,
            CAST((COUNT(CASE WHEN has_attachment = true THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as attachment_rate,
            CAST((COUNT(CASE WHEN persons_involved IS NOT NULL AND LENGTH(TRIM(persons_involved)) > 0 THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as persons_involved_completion_rate
        FROM {self.table_name}
        """
        result = self.execute_query(query)[0]

        # Calculate overall quality score (weighted average) - Convert to float to handle Decimal types
        detailed_rate = float(result['detailed_description_rate']) if result['detailed_description_rate'] is not None else 0.0
        comments_rate = float(result['comments_completion_rate']) if result['comments_completion_rate'] is not None else 0.0
        attachment_rate = float(result['attachment_rate']) if result['attachment_rate'] is not None else 0.0
        persons_rate = float(result['persons_involved_completion_rate']) if result['persons_involved_completion_rate'] is not None else 0.0

        quality_score = (
            detailed_rate * 0.3 +
            comments_rate * 0.2 +
            attachment_rate * 0.25 +
            persons_rate * 0.25
        )
        result['overall_quality_score'] = round(float(quality_score), 2)

        return result

    def get_seasonal_trend_analysis(self) -> List[Dict]:
        """Analyze seasonal trends in safety incidents"""
        query = f"""
        SELECT
            EXTRACT(QUARTER FROM date_and_time_of_unsafe_event) as quarter,
            EXTRACT(MONTH FROM date_and_time_of_unsafe_event) as month,
            TO_CHAR(date_and_time_of_unsafe_event, 'Month') as month_name,
            COUNT(*) as incident_count,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stoppages,
            COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) as high_risk_actions,
            CAST((COUNT(*) * 100.0 / SUM(COUNT(*)) OVER()) AS DECIMAL(10,2)) as percentage_of_total,
            CAST((COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as work_stopped_rate
        FROM {self.table_name}
        WHERE date_and_time_of_unsafe_event IS NOT NULL
        GROUP BY EXTRACT(QUARTER FROM date_and_time_of_unsafe_event),
                 EXTRACT(MONTH FROM date_and_time_of_unsafe_event),
                 TO_CHAR(date_and_time_of_unsafe_event, 'Month')
        ORDER BY quarter, month
        """
        return self.execute_query(query)

    # ==================== OPERATIONAL INTELLIGENCE ENHANCEMENTS ====================

    def get_job_performance_analysis(self) -> List[Dict]:
        """Analyze job performance with work completion rates and delays"""
        query = f"""
        SELECT
            job_no,
            location,
            branch_name,
            COUNT(*) as total_incidents,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stoppages,
            COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) as high_risk_actions,
            SUM(CASE
                WHEN work_stopped_hours IS NOT NULL AND work_stopped_hours != ''
                THEN CAST(REGEXP_REPLACE(work_stopped_hours, '[^0-9.]', '', 'g') AS FLOAT)
                ELSE 0
            END) as total_hours_lost,
            CAST((COUNT(CASE WHEN UPPER(work_was_stopped) = 'NO' OR work_was_stopped IS NULL THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as job_completion_rate,
            COUNT(DISTINCT reporter_name) as people_involved,
            STRING_AGG(DISTINCT
                CASE
                    WHEN additional_comments IS NOT NULL AND LENGTH(TRIM(additional_comments)) > 10
                    THEN SUBSTRING(additional_comments, 1, 100)
                END, ' | ') as job_issues,
            MAX(date_and_time_of_unsafe_event) as latest_incident,
            CASE
                WHEN COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) = 0 THEN 'EXCELLENT_JOB'
                WHEN COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) < 20 THEN 'GOOD_JOB'
                WHEN SUM(CASE WHEN work_stopped_hours IS NOT NULL THEN CAST(REGEXP_REPLACE(work_stopped_hours, '[^0-9.]', '', 'g') AS FLOAT) ELSE 0 END) > 8 THEN 'DELAYED_JOB'
                ELSE 'STANDARD_JOB'
            END as job_performance_category
        FROM {self.table_name}
        WHERE job_no IS NOT NULL AND job_no != ''
        GROUP BY job_no, location, branch_name
        HAVING COUNT(*) >= 2
        ORDER BY job_completion_rate DESC, total_hours_lost ASC
        LIMIT 30
        """
        return self.execute_query(query)

    def get_staff_performance_with_job_context(self) -> List[Dict]:
        """Analyze staff performance in context of job completion and efficiency"""
        query = f"""
        SELECT
            reporter_name,
            designation,
            branch_name,
            COUNT(*) as total_reports,
            COUNT(DISTINCT job_no) as jobs_worked,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stoppages,
            COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) as high_risk_actions,
            SUM(CASE
                WHEN work_stopped_hours IS NOT NULL AND work_stopped_hours != ''
                THEN CAST(REGEXP_REPLACE(work_stopped_hours, '[^0-9.]', '', 'g') AS FLOAT)
                ELSE 0
            END) as total_hours_lost,
            CAST((COUNT(CASE WHEN UPPER(work_was_stopped) = 'NO' OR work_was_stopped IS NULL THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as work_continuation_rate,
            CAST((COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as proactive_action_rate,
            COUNT(DISTINCT location) as locations_worked,
            AVG(CASE
                WHEN DATE(created_on) IS NOT NULL AND DATE(date_and_time_of_unsafe_event) IS NOT NULL
                THEN DATE(created_on) - DATE(date_and_time_of_unsafe_event)
            END) as avg_reporting_delay_days,
            STRING_AGG(DISTINCT
                CASE
                    WHEN additional_comments IS NOT NULL AND LENGTH(TRIM(additional_comments)) > 10
                    THEN SUBSTRING(additional_comments, 1, 100)
                END, ' | ') as performance_notes
        FROM {self.table_name}
        WHERE reporter_name IS NOT NULL
        GROUP BY reporter_name, designation, branch_name
        HAVING COUNT(*) >= 3
        ORDER BY work_continuation_rate DESC, proactive_action_rate DESC, total_hours_lost ASC
        LIMIT 25
        """
        return self.execute_query(query)

    def get_operational_efficiency_alerts(self, days_back: int = 14) -> List[Dict]:
        """Generate operational efficiency alerts based on recent performance"""
        query = f"""
        WITH recent_performance AS (
            SELECT
                branch_name,
                location,
                COUNT(*) as recent_incidents,
                COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stoppages,
                COUNT(DISTINCT job_no) as jobs_affected,
                SUM(CASE
                    WHEN work_stopped_hours IS NOT NULL AND work_stopped_hours != ''
                    THEN CAST(REGEXP_REPLACE(work_stopped_hours, '[^0-9.]', '', 'g') AS FLOAT)
                    ELSE 0
                END) as total_hours_lost,
                STRING_AGG(DISTINCT
                    CASE
                        WHEN additional_comments IS NOT NULL AND LENGTH(TRIM(additional_comments)) > 10
                        THEN SUBSTRING(additional_comments, 1, 100)
                    END, ' | ') as common_issues
            FROM {self.table_name}
            WHERE date_and_time_of_unsafe_event >= CURRENT_DATE - INTERVAL '{days_back} days'
            GROUP BY branch_name, location
        )
        SELECT
            branch_name,
            location,
            recent_incidents,
            work_stoppages,
            jobs_affected,
            total_hours_lost,
            common_issues,
            CAST((work_stoppages * 100.0 / NULLIF(recent_incidents, 0)) AS DECIMAL(10,2)) as work_stoppage_rate,
            CAST((total_hours_lost / NULLIF(jobs_affected, 0)) AS DECIMAL(10,2)) as avg_hours_lost_per_job,
            CASE
                WHEN work_stoppages * 100.0 / NULLIF(recent_incidents, 0) > 40 THEN 'HIGH_DISRUPTION_ALERT'
                WHEN total_hours_lost > 20 THEN 'PRODUCTIVITY_LOSS_ALERT'
                WHEN jobs_affected > recent_incidents * 0.8 THEN 'WIDESPREAD_IMPACT_ALERT'
                ELSE 'NORMAL'
            END as alert_type
        FROM recent_performance
        WHERE recent_incidents >= 3
        ORDER BY work_stoppage_rate DESC, total_hours_lost DESC
        """
        return self.execute_query(query)

    # ==================== TIME-BASED ANALYSIS ====================

    def get_incidents_by_time_of_day(self) -> List[Dict]:
        """Analyze incidents by time of day (morning, afternoon, night)"""
        query = f"""
        SELECT
            CASE
                WHEN EXTRACT(HOUR FROM date_and_time_of_unsafe_event) BETWEEN 6 AND 11 THEN 'Morning (6AM-12PM)'
                WHEN EXTRACT(HOUR FROM date_and_time_of_unsafe_event) BETWEEN 12 AND 17 THEN 'Afternoon (12PM-6PM)'
                WHEN EXTRACT(HOUR FROM date_and_time_of_unsafe_event) BETWEEN 18 AND 23 THEN 'Evening (6PM-12AM)'
                ELSE 'Night (12AM-6AM)'
            END as time_period,
            COUNT(*) as incident_count,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stopped_incidents,
            COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) as high_risk_actions,
            COUNT(CASE WHEN no_go_violation IS NOT NULL AND no_go_violation != '' THEN 1 END) as nogo_violations,
            CAST((COUNT(*) * 100.0 / SUM(COUNT(*)) OVER()) AS DECIMAL(10,2)) as percentage_of_total,
            CAST((COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as work_stopped_rate,
            CAST((COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as high_risk_action_rate
        FROM {self.table_name}
        WHERE date_and_time_of_unsafe_event IS NOT NULL
        GROUP BY
            CASE
                WHEN EXTRACT(HOUR FROM date_and_time_of_unsafe_event) BETWEEN 6 AND 11 THEN 'Morning (6AM-12PM)'
                WHEN EXTRACT(HOUR FROM date_and_time_of_unsafe_event) BETWEEN 12 AND 17 THEN 'Afternoon (12PM-6PM)'
                WHEN EXTRACT(HOUR FROM date_and_time_of_unsafe_event) BETWEEN 18 AND 23 THEN 'Evening (6PM-12AM)'
                ELSE 'Night (12AM-6AM)'
            END
        ORDER BY incident_count DESC
        """
        return self.execute_query(query)

    def get_hourly_incident_distribution(self) -> List[Dict]:
        """Detailed hourly breakdown of incidents"""
        query = f"""
        SELECT
            EXTRACT(HOUR FROM date_and_time_of_unsafe_event) as hour_of_day,
            COUNT(*) as incident_count,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stopped_incidents,
            COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) as high_risk_actions,
            CAST((COUNT(*) * 100.0 / SUM(COUNT(*)) OVER()) AS DECIMAL(10,2)) as percentage_of_total,
            CAST((COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0)) AS DECIMAL(10,2)) as work_stopped_rate
        FROM {self.table_name}
        WHERE date_and_time_of_unsafe_event IS NOT NULL
        GROUP BY EXTRACT(HOUR FROM date_and_time_of_unsafe_event)
        ORDER BY hour_of_day
        """
        return self.execute_query(query)

    def get_time_based_incident_trends(self) -> List[Dict]:
        """Analyze incident trends by time periods with additional context"""
        query = f"""
        SELECT
            CASE
                WHEN EXTRACT(HOUR FROM date_and_time_of_unsafe_event) BETWEEN 6 AND 11 THEN 'Morning'
                WHEN EXTRACT(HOUR FROM date_and_time_of_unsafe_event) BETWEEN 12 AND 17 THEN 'Afternoon'
                WHEN EXTRACT(HOUR FROM date_and_time_of_unsafe_event) BETWEEN 18 AND 23 THEN 'Evening'
                ELSE 'Night'
            END as time_period,
            type_of_unsafe_event,
            COUNT(*) as incident_count,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stopped_incidents,
            COUNT(DISTINCT location) as unique_locations,
            COUNT(DISTINCT reporter_name) as unique_reporters,
            CAST((COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(PARTITION BY
                CASE
                    WHEN EXTRACT(HOUR FROM date_and_time_of_unsafe_event) BETWEEN 6 AND 11 THEN 'Morning'
                    WHEN EXTRACT(HOUR FROM date_and_time_of_unsafe_event) BETWEEN 12 AND 17 THEN 'Afternoon'
                    WHEN EXTRACT(HOUR FROM date_and_time_of_unsafe_event) BETWEEN 18 AND 23 THEN 'Evening'
                    ELSE 'Night'
                END)) AS DECIMAL(10,2)) as percentage_within_time_period
        FROM {self.table_name}
        WHERE date_and_time_of_unsafe_event IS NOT NULL
        AND type_of_unsafe_event IS NOT NULL
        GROUP BY
            CASE
                WHEN EXTRACT(HOUR FROM date_and_time_of_unsafe_event) BETWEEN 6 AND 11 THEN 'Morning'
                WHEN EXTRACT(HOUR FROM date_and_time_of_unsafe_event) BETWEEN 12 AND 17 THEN 'Afternoon'
                WHEN EXTRACT(HOUR FROM date_and_time_of_unsafe_event) BETWEEN 18 AND 23 THEN 'Evening'
                ELSE 'Night'
            END,
            type_of_unsafe_event
        HAVING COUNT(*) >= 2
        ORDER BY time_period, incident_count DESC
        """
        return self.execute_query(query)

    def get_peak_incident_hours_analysis(self) -> Dict[str, Any]:
        """Identify peak incident hours and provide insights"""
        query = f"""
        WITH hourly_stats AS (
            SELECT
                EXTRACT(HOUR FROM date_and_time_of_unsafe_event) as hour_of_day,
                COUNT(*) as incident_count,
                COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stopped_incidents
            FROM {self.table_name}
            WHERE date_and_time_of_unsafe_event IS NOT NULL
            GROUP BY EXTRACT(HOUR FROM date_and_time_of_unsafe_event)
        ),
        peak_analysis AS (
            SELECT
                hour_of_day,
                incident_count,
                work_stopped_incidents,
                RANK() OVER (ORDER BY incident_count DESC) as incident_rank,
                RANK() OVER (ORDER BY work_stopped_incidents DESC) as work_stop_rank
            FROM hourly_stats
        )
        SELECT
            (SELECT hour_of_day FROM peak_analysis WHERE incident_rank = 1) as peak_incident_hour,
            (SELECT incident_count FROM peak_analysis WHERE incident_rank = 1) as peak_incident_count,
            (SELECT hour_of_day FROM peak_analysis WHERE work_stop_rank = 1) as peak_work_stop_hour,
            (SELECT work_stopped_incidents FROM peak_analysis WHERE work_stop_rank = 1) as peak_work_stop_count,
            (SELECT AVG(incident_count) FROM hourly_stats) as avg_incidents_per_hour,
            (SELECT COUNT(*) FROM hourly_stats WHERE incident_count > (SELECT AVG(incident_count) FROM hourly_stats)) as above_avg_hours
        """
        return self.execute_query(query)[0]

    # ==================== COMPREHENSIVE KPI EXECUTION ====================

    def get_all_kpis(self) -> Dict[str, Any]:
        """Execute all KPI queries and return comprehensive results"""
        try:
            logger.info("Executing all NI TCT KPI queries...")

            results = {
                # Event Volume & Frequency
                "total_events": self.get_total_events_count(),
                "events_by_type": self.get_events_by_unsafe_event_type(),
                "events_monthly": self.get_events_per_time_period('month'),
                "events_weekly": self.get_events_per_time_period('week'),
                "events_quarterly": self.get_events_per_time_period('quarter'),
                "status_distribution": self.get_event_status_distribution(),

                # Safety Severity
                "high_risk_situation_analysis": self.get_high_risk_situation_analysis(),
                "work_stopped": self.get_work_stopped_incidents(),
                "nogo_violations": self.get_nogo_violations_count(),
                "work_stoppage_duration": self.get_work_stoppage_duration_analysis(),

                # Geographic Distribution
                "regional_distribution": self.get_events_by_region(),
                "branch_distribution": self.get_events_by_branch(),
                "location_distribution": self.get_events_by_location(),

                # Personnel Metrics
                "top_reporters": self.get_events_by_reporter(),
                "designation_analysis": self.get_events_by_designation(),

                # Hierarchical Analysis (NI TCT Specific)
                "gl_pe_hierarchy": self.get_gl_pe_hierarchy_analysis(),
                "group_leader_performance": self.get_group_leader_performance(),
                "project_engineer_performance": self.get_project_engineer_performance(),

                # Operational Metrics
                "product_types": self.get_events_by_product_type(),
                "business_details": self.get_events_by_business_details(),
                "attachment_utilization": self.get_attachment_utilization_analysis(),
                "job_specific_analysis": self.get_job_specific_analysis(),

                # Advanced Analytics
                "reporting_delay_analysis": self.get_reporting_delay_analysis(),
                "repeat_location_analysis": self.get_repeat_location_analysis(),
                "high_risk_response_effectiveness": self.get_high_risk_response_effectiveness(),
                "documentation_quality": self.get_documentation_quality_score(),
                "seasonal_trends": self.get_seasonal_trend_analysis(),

                # ==================== ENHANCED OPERATIONAL INTELLIGENCE ====================
                "job_performance_analysis": self.get_job_performance_analysis(),
                "staff_performance_with_job_context": self.get_staff_performance_with_job_context(),
                "operational_efficiency_alerts": self.get_operational_efficiency_alerts(),

                # ==================== TIME-BASED ANALYSIS ====================
                "incidents_by_time_of_day": self.get_incidents_by_time_of_day(),
                "hourly_incident_distribution": self.get_hourly_incident_distribution(),
                "time_based_incident_trends": self.get_time_based_incident_trends(),
                "peak_incident_hours_analysis": self.get_peak_incident_hours_analysis(),
            }

            logger.info("All NI TCT KPI queries executed successfully")
            return results

        except Exception as e:
            logger.error(f"Error executing NI TCT KPIs: {e}")
            raise



