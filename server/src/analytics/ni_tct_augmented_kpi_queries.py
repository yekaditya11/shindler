"""
NI TCT Augmented KPI Queries Module
Enhanced KPI analytics for NI TCT Augmented unsafe events with weather, employee, site risk, and workload data
Author: AI Assistant
Date: 2025-07-22
"""

import logging
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.config.database import get_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NITCTAugmentedKPIQueries:
    """Enhanced SQL queries for NI TCT Augmented App KPIs with additional data sources"""
    
    def __init__(self):
        self.table_name = "unsafe_events_ni_tct_augmented"
    
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
    
    # ==================== ENHANCED EVENT VOLUME & FREQUENCY ====================
    
    def get_total_events_count(self) -> Dict[str, Any]:
        """Total events count with augmented data insights"""
        query = f"""
        SELECT 
            COUNT(*) as total_events,
            COUNT(DISTINCT reporting_id) as unique_events,
            COUNT(CASE WHEN status IS NOT NULL THEN 1 END) as events_with_status,
            COUNT(CASE WHEN weather_weather_condition IS NOT NULL THEN 1 END) as events_with_weather_data,
            COUNT(CASE WHEN employee_experience_level IS NOT NULL THEN 1 END) as events_with_employee_data,
            COUNT(CASE WHEN site_site_risk_category IS NOT NULL THEN 1 END) as events_with_site_risk_data,
            COUNT(CASE WHEN workload_workload_category IS NOT NULL THEN 1 END) as events_with_workload_data
        FROM {self.table_name}
        WHERE reporting_id IS NOT NULL
        """
        return self.execute_query(query)[0]
    
    # ==================== WEATHER IMPACT ANALYSIS ====================
    
    def get_weather_impact_analysis(self) -> List[Dict]:
        """Analyze safety incidents by weather conditions"""
        query = f"""
        SELECT 
            weather_weather_condition,
            COUNT(*) as incident_count,
            AVG(CAST(weather_temperature_celsius AS FLOAT)) as avg_temperature,
            AVG(CAST(weather_humidity_percent AS FLOAT)) as avg_humidity,
            AVG(weather_weather_severity_score) as avg_weather_severity,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stopped_incidents,
            COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) as high_risk_incidents,
            ROUND(COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 / 
                  NULLIF(COUNT(*), 0), 2) as work_stopped_rate,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage_of_total
        FROM {self.table_name}
        WHERE weather_weather_condition IS NOT NULL
        GROUP BY weather_weather_condition
        ORDER BY incident_count DESC
        """
        return self.execute_query(query)
    
    def get_weather_severity_correlation(self) -> List[Dict]:
        """Analyze correlation between weather severity and incident severity"""
        query = f"""
        SELECT 
            CASE 
                WHEN weather_weather_severity_score <= 3 THEN 'Low Severity (1-3)'
                WHEN weather_weather_severity_score <= 6 THEN 'Medium Severity (4-6)'
                WHEN weather_weather_severity_score <= 8 THEN 'High Severity (7-8)'
                ELSE 'Critical Severity (9-10)'
            END as weather_severity_category,
            COUNT(*) as incident_count,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stopped_incidents,
            COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) as high_risk_incidents,
            ROUND(COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 / 
                  NULLIF(COUNT(*), 0), 2) as work_stopped_rate,
            ROUND(COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) * 100.0 / 
                  NULLIF(COUNT(*), 0), 2) as high_risk_rate
        FROM {self.table_name}
        WHERE weather_weather_severity_score IS NOT NULL
        GROUP BY weather_weather_severity_score
        ORDER BY weather_weather_severity_score
        """
        return self.execute_query(query)
    
    def get_temperature_humidity_impact(self) -> List[Dict]:
        """Analyze impact of extreme temperature and humidity on incidents"""
        query = f"""
        SELECT
            CASE
                WHEN CAST(weather_temperature_celsius AS FLOAT) <= 10 THEN 'Cold (≤10°C)'
                WHEN CAST(weather_temperature_celsius AS FLOAT) BETWEEN 10 AND 25 THEN 'Moderate (10-25°C)'
                ELSE 'Hot (>25°C)'
            END as temperature_category,
            CASE
                WHEN CAST(weather_humidity_percent AS FLOAT) <= 40 THEN 'Low Humidity (≤40%)'
                WHEN CAST(weather_humidity_percent AS FLOAT) BETWEEN 40 AND 70 THEN 'Moderate Humidity (40-70%)'
                ELSE 'High Humidity (>70%)'
            END as humidity_category,
            COUNT(*) as incident_count,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stopped_incidents,
            ROUND(COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 / 
                  NULLIF(COUNT(*), 0), 2) as work_stopped_rate
        FROM {self.table_name}
        WHERE weather_temperature_celsius IS NOT NULL 
        AND weather_humidity_percent IS NOT NULL
        GROUP BY
            CASE
                WHEN CAST(weather_temperature_celsius AS FLOAT) <= 10 THEN 'Cold (≤10°C)'
                WHEN CAST(weather_temperature_celsius AS FLOAT) BETWEEN 10 AND 25 THEN 'Moderate (10-25°C)'
                ELSE 'Hot (>25°C)'
            END,
            CASE
                WHEN CAST(weather_humidity_percent AS FLOAT) <= 40 THEN 'Low Humidity (≤40%)'
                WHEN CAST(weather_humidity_percent AS FLOAT) BETWEEN 40 AND 70 THEN 'Moderate Humidity (40-70%)'
                ELSE 'High Humidity (>70%)'
            END
        ORDER BY incident_count DESC
        LIMIT 15
        """
        return self.execute_query(query)
    
    # ==================== EMPLOYEE EXPERIENCE & TRAINING ANALYSIS ====================
    
    def get_experience_level_analysis(self) -> List[Dict]:
        """Analyze incidents by employee experience level"""
        query = f"""
        SELECT 
            employee_experience_level,
            COUNT(*) as incident_count,
            AVG(employee_employee_age) as avg_age,
            AVG(CAST(employee_years_of_experience AS FLOAT)) as avg_years_experience,
            AVG(employee_safety_training_hours) as avg_training_hours,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stopped_incidents,
            COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) as high_risk_incidents,
            ROUND(COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 / 
                  NULLIF(COUNT(*), 0), 2) as work_stopped_rate,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage_of_total
        FROM {self.table_name}
        WHERE employee_experience_level IS NOT NULL
        GROUP BY employee_experience_level
        ORDER BY
            CASE
                WHEN employee_experience_level = 'Entry Level (0-2 years)' THEN 1
                WHEN employee_experience_level = 'Junior (2-5 years)' THEN 2
                WHEN employee_experience_level = 'Mid-Level (5-10 years)' THEN 3
                WHEN employee_experience_level = 'Senior (10-15 years)' THEN 4
                ELSE 5
            END
        """
        return self.execute_query(query)
    
    def get_training_effectiveness_analysis(self) -> List[Dict]:
        """Analyze relationship between training hours and incident rates"""
        query = f"""
        SELECT 
            CASE 
                WHEN employee_safety_training_hours < 20 THEN 'Minimal Training (<20 hrs)'
                WHEN employee_safety_training_hours BETWEEN 20 AND 40 THEN 'Basic Training (20-40 hrs)'
                WHEN employee_safety_training_hours BETWEEN 40 AND 80 THEN 'Standard Training (40-80 hrs)'
                ELSE 'Extensive Training (>80 hrs)'
            END as training_category,
            COUNT(*) as incident_count,
            AVG(employee_safety_training_hours) as avg_training_hours,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stopped_incidents,
            COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) as high_risk_incidents,
            ROUND(COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 / 
                  NULLIF(COUNT(*), 0), 2) as work_stopped_rate,
            ROUND(COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) * 100.0 / 
                  NULLIF(COUNT(*), 0), 2) as high_risk_rate
        FROM {self.table_name}
        WHERE employee_safety_training_hours IS NOT NULL
        GROUP BY employee_safety_training_hours
        ORDER BY employee_safety_training_hours
        """
        return self.execute_query(query)
    
    def get_shift_type_analysis(self) -> List[Dict]:
        """Analyze incidents by shift type"""
        query = f"""
        SELECT 
            employee_shift_type,
            COUNT(*) as incident_count,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stopped_incidents,
            COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) as high_risk_incidents,
            ROUND(COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 / 
                  NULLIF(COUNT(*), 0), 2) as work_stopped_rate,
            ROUND(COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) * 100.0 / 
                  NULLIF(COUNT(*), 0), 2) as high_risk_rate,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage_of_total
        FROM {self.table_name}
        WHERE employee_shift_type IS NOT NULL
        GROUP BY employee_shift_type
        ORDER BY incident_count DESC
        """
        return self.execute_query(query)
    
    # ==================== SITE RISK ASSESSMENT ANALYSIS ====================
    
    def get_site_risk_analysis(self) -> List[Dict]:
        """Analyze incidents by site risk category"""
        query = f"""
        SELECT 
            site_site_risk_category,
            COUNT(*) as incident_count,
            AVG(site_last_safety_audit_days) as avg_days_since_audit,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stopped_incidents,
            COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) as high_risk_incidents,
            ROUND(COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 / 
                  NULLIF(COUNT(*), 0), 2) as work_stopped_rate,
            ROUND(COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) * 100.0 / 
                  NULLIF(COUNT(*), 0), 2) as high_risk_rate,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage_of_total
        FROM {self.table_name}
        WHERE site_site_risk_category IS NOT NULL
        GROUP BY site_site_risk_category
        ORDER BY
            CASE
                WHEN site_site_risk_category = 'Low Risk' THEN 1
                WHEN site_site_risk_category = 'Medium Risk' THEN 2
                WHEN site_site_risk_category = 'High Risk' THEN 3
                ELSE 4
            END
        """
        return self.execute_query(query)
    
    def get_audit_frequency_impact(self) -> List[Dict]:
        """Analyze impact of safety audit frequency on incidents"""
        query = f"""
        SELECT 
            CASE 
                WHEN site_last_safety_audit_days <= 90 THEN 'Recent Audit (≤3 months)'
                WHEN site_last_safety_audit_days BETWEEN 91 AND 180 THEN 'Moderate Audit (3-6 months)'
                WHEN site_last_safety_audit_days BETWEEN 181 AND 365 THEN 'Delayed Audit (6-12 months)'
                ELSE 'Overdue Audit (>12 months)'
            END as audit_frequency_category,
            COUNT(*) as incident_count,
            AVG(site_last_safety_audit_days) as avg_days_since_audit,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stopped_incidents,
            COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) as high_risk_incidents,
            ROUND(COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 / 
                  NULLIF(COUNT(*), 0), 2) as work_stopped_rate,
            ROUND(COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) * 100.0 / 
                  NULLIF(COUNT(*), 0), 2) as high_risk_rate
        FROM {self.table_name}
        WHERE site_last_safety_audit_days IS NOT NULL
        GROUP BY
            CASE
                WHEN site_last_safety_audit_days <= 90 THEN 'Recent Audit (≤3 months)'
                WHEN site_last_safety_audit_days BETWEEN 91 AND 180 THEN 'Moderate Audit (3-6 months)'
                WHEN site_last_safety_audit_days BETWEEN 181 AND 365 THEN 'Delayed Audit (6-12 months)'
                ELSE 'Overdue Audit (>12 months)'
            END
        ORDER BY AVG(site_last_safety_audit_days)
        """
        return self.execute_query(query)

    # ==================== WORKLOAD & TEAM DYNAMICS ANALYSIS ====================

    def get_workload_impact_analysis(self) -> List[Dict]:
        """Analyze incidents by workload category"""
        query = f"""
        SELECT
            workload_workload_category,
            COUNT(*) as incident_count,
            AVG(workload_team_size) as avg_team_size,
            AVG(CAST(workload_work_duration_hours AS FLOAT)) as avg_work_duration,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stopped_incidents,
            COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) as high_risk_incidents,
            ROUND(COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as work_stopped_rate,
            ROUND(COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as high_risk_rate,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage_of_total
        FROM {self.table_name}
        WHERE workload_workload_category IS NOT NULL
        GROUP BY workload_workload_category
        ORDER BY
            CASE
                WHEN workload_workload_category = 'Low' THEN 1
                WHEN workload_workload_category = 'Normal' THEN 2
                ELSE 3
            END
        """
        return self.execute_query(query)

    def get_team_size_effectiveness(self) -> List[Dict]:
        """Analyze relationship between team size and incident rates"""
        query = f"""
        SELECT
            CASE
                WHEN workload_team_size <= 2 THEN 'Small Team (≤2)'
                WHEN workload_team_size BETWEEN 3 AND 4 THEN 'Medium Team (3-4)'
                WHEN workload_team_size BETWEEN 5 AND 6 THEN 'Large Team (5-6)'
                ELSE 'Extra Large Team (>6)'
            END as team_size_category,
            COUNT(*) as incident_count,
            AVG(workload_team_size) as avg_team_size,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stopped_incidents,
            COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) as high_risk_incidents,
            ROUND(COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as work_stopped_rate,
            ROUND(COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as high_risk_rate
        FROM {self.table_name}
        WHERE workload_team_size IS NOT NULL
        GROUP BY
            CASE
                WHEN workload_team_size <= 2 THEN 'Small Team (≤2)'
                WHEN workload_team_size BETWEEN 3 AND 4 THEN 'Medium Team (3-4)'
                WHEN workload_team_size BETWEEN 5 AND 6 THEN 'Large Team (5-6)'
                ELSE 'Extra Large Team (>6)'
            END
        ORDER BY AVG(workload_team_size)
        """
        return self.execute_query(query)

    def get_work_duration_fatigue_analysis(self) -> List[Dict]:
        """Analyze impact of work duration on incident rates (fatigue analysis)"""
        query = f"""
        SELECT
            CASE
                WHEN CAST(workload_work_duration_hours AS FLOAT) <= 4 THEN 'Short Duration (≤4 hrs)'
                WHEN CAST(workload_work_duration_hours AS FLOAT) BETWEEN 4.1 AND 8 THEN 'Standard Duration (4-8 hrs)'
                WHEN CAST(workload_work_duration_hours AS FLOAT) BETWEEN 8.1 AND 10 THEN 'Extended Duration (8-10 hrs)'
                ELSE 'Overtime Duration (>10 hrs)'
            END as work_duration_category,
            COUNT(*) as incident_count,
            AVG(CAST(workload_work_duration_hours AS FLOAT)) as avg_work_duration,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stopped_incidents,
            COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) as high_risk_incidents,
            ROUND(COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as work_stopped_rate,
            ROUND(COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as high_risk_rate
        FROM {self.table_name}
        WHERE workload_work_duration_hours IS NOT NULL
        GROUP BY
            CASE
                WHEN CAST(workload_work_duration_hours AS FLOAT) <= 4 THEN 'Short Duration (≤4 hrs)'
                WHEN CAST(workload_work_duration_hours AS FLOAT) BETWEEN 4.1 AND 8 THEN 'Standard Duration (4-8 hrs)'
                WHEN CAST(workload_work_duration_hours AS FLOAT) BETWEEN 8.1 AND 10 THEN 'Extended Duration (8-10 hrs)'
                ELSE 'Overtime Duration (>10 hrs)'
            END
        ORDER BY AVG(CAST(workload_work_duration_hours AS FLOAT))
        """
        return self.execute_query(query)

    # ==================== MULTI-FACTOR CORRELATION ANALYSIS ====================

    def get_weather_experience_correlation(self) -> List[Dict]:
        """Analyze correlation between weather conditions and employee experience"""
        query = f"""
        SELECT
            weather_weather_condition,
            employee_experience_level,
            COUNT(*) as incident_count,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stopped_incidents,
            ROUND(COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as work_stopped_rate
        FROM {self.table_name}
        WHERE weather_weather_condition IS NOT NULL
        AND employee_experience_level IS NOT NULL
        GROUP BY weather_weather_condition, employee_experience_level
        HAVING COUNT(*) >= 3
        ORDER BY incident_count DESC
        LIMIT 20
        """
        return self.execute_query(query)

    def get_site_risk_workload_correlation(self) -> List[Dict]:
        """Analyze correlation between site risk and workload"""
        query = f"""
        SELECT
            site_site_risk_category,
            workload_workload_category,
            COUNT(*) as incident_count,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stopped_incidents,
            COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) as high_risk_incidents,
            ROUND(COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as work_stopped_rate,
            ROUND(COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as high_risk_rate
        FROM {self.table_name}
        WHERE site_site_risk_category IS NOT NULL
        AND workload_workload_category IS NOT NULL
        GROUP BY site_site_risk_category, workload_workload_category
        ORDER BY incident_count DESC
        """
        return self.execute_query(query)

    def get_comprehensive_risk_score(self) -> List[Dict]:
        """Calculate comprehensive risk score based on all augmented factors"""
        query = f"""
        SELECT
            reporting_id,
            region,
            branch_name,
            type_of_unsafe_event,
            weather_weather_severity_score,
            employee_experience_level,
            site_site_risk_category,
            workload_workload_category,
            CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 ELSE 0 END as work_stopped,
            CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 ELSE 0 END as high_risk_action,
            -- Calculate composite risk score
            (
                COALESCE(weather_weather_severity_score, 5) * 0.2 +
                CASE employee_experience_level
                    WHEN 'Entry Level (0-2 years)' THEN 8
                    WHEN 'Junior (2-5 years)' THEN 6
                    WHEN 'Mid-Level (5-10 years)' THEN 4
                    WHEN 'Senior (10-15 years)' THEN 2
                    ELSE 1
                END * 0.25 +
                CASE site_site_risk_category
                    WHEN 'Critical Risk' THEN 10
                    WHEN 'High Risk' THEN 7
                    WHEN 'Medium Risk' THEN 4
                    ELSE 2
                END * 0.3 +
                CASE workload_workload_category
                    WHEN 'High' THEN 8
                    WHEN 'Normal' THEN 4
                    ELSE 2
                END * 0.25
            ) as composite_risk_score
        FROM {self.table_name}
        WHERE weather_weather_severity_score IS NOT NULL
        AND employee_experience_level IS NOT NULL
        AND site_site_risk_category IS NOT NULL
        AND workload_workload_category IS NOT NULL
        ORDER BY composite_risk_score DESC
        LIMIT 50
        """
        return self.execute_query(query)

    # ==================== ADVANCED OPERATIONAL INTELLIGENCE ====================

    def get_weather_based_operational_alerts(self, days_back: int = 30) -> List[Dict]:
        """Generate weather-based operational alerts for resource planning"""
        query = f"""
        WITH weather_impact AS (
            SELECT
                region,
                branch_name,
                weather_weather_condition,
                COUNT(*) as incidents,
                COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stoppages,
                AVG(CAST(workload_work_duration_hours AS FLOAT)) as avg_work_duration,
                COUNT(CASE WHEN workload_workload_category = 'High' THEN 1 END) as high_workload_incidents
            FROM {self.table_name}
            WHERE date_and_time_of_unsafe_event >= CURRENT_DATE - INTERVAL '{days_back} days'
            AND weather_weather_condition IS NOT NULL
            GROUP BY region, branch_name, weather_weather_condition
        )
        SELECT
            region,
            branch_name,
            weather_weather_condition,
            incidents,
            work_stoppages,
            ROUND(CAST(avg_work_duration AS NUMERIC), 2) as avg_work_duration_hours,
            high_workload_incidents,
            ROUND(CAST(work_stoppages * 100.0 / NULLIF(incidents, 0) AS NUMERIC), 2) as work_stoppage_rate,
            ROUND(CAST(high_workload_incidents * 100.0 / NULLIF(incidents, 0) AS NUMERIC), 2) as high_workload_rate,
            CASE
                WHEN work_stoppages * 100.0 / NULLIF(incidents, 0) > 40 THEN 'HIGH_WEATHER_IMPACT'
                WHEN high_workload_incidents * 100.0 / NULLIF(incidents, 0) > 60 THEN 'WORKLOAD_WEATHER_CORRELATION'
                WHEN avg_work_duration > 10 THEN 'EXTENDED_DURATION_RISK'
                ELSE 'NORMAL'
            END as alert_type
        FROM weather_impact
        WHERE incidents >= 3
        ORDER BY work_stoppage_rate DESC, high_workload_rate DESC
        """
        return self.execute_query(query)

    def get_experience_based_resource_optimization(self) -> List[Dict]:
        """Optimize resource allocation based on experience levels and performance"""
        query = f"""
        SELECT
            employee_experience_level,
            employee_shift_type,
            workload_team_size,
            COUNT(*) as total_incidents,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stoppages,
            COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) as high_risk_actions,
            AVG(CAST(workload_work_duration_hours AS FLOAT)) as avg_work_duration,
            AVG(employee_safety_training_hours) as avg_training_hours,
            ROUND(COUNT(CASE WHEN UPPER(work_was_stopped) = 'NO' OR work_was_stopped IS NULL THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as work_continuation_rate,
            STRING_AGG(DISTINCT
                CASE
                    WHEN additional_comments IS NOT NULL AND LENGTH(TRIM(additional_comments)) > 10
                    THEN SUBSTRING(additional_comments, 1, 100)
                END, ' | ') as performance_insights,
            CASE
                WHEN COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) = 0
                     AND AVG(employee_safety_training_hours) > 60 THEN 'OPTIMAL_RESOURCE'
                WHEN COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) < 20
                     AND workload_team_size BETWEEN 3 AND 5 THEN 'EFFICIENT_TEAM'
                WHEN AVG(CAST(workload_work_duration_hours AS FLOAT)) > 10
                     AND COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) > 0 THEN 'FATIGUE_RISK'
                ELSE 'STANDARD'
            END as resource_category
        FROM {self.table_name}
        WHERE employee_experience_level IS NOT NULL
        AND workload_team_size IS NOT NULL
        GROUP BY employee_experience_level, employee_shift_type, workload_team_size
        HAVING COUNT(*) >= 3
        ORDER BY work_continuation_rate DESC, avg_training_hours DESC
        """
        return self.execute_query(query)

    def get_site_risk_workload_optimization(self) -> List[Dict]:
        """Optimize workload based on site risk and audit frequency"""
        query = f"""
        SELECT
            site_site_risk_category,
            workload_workload_category,
            CASE
                WHEN site_last_safety_audit_days <= 90 THEN 'Recent Audit (≤3 months)'
                WHEN site_last_safety_audit_days BETWEEN 91 AND 180 THEN 'Moderate Audit (3-6 months)'
                ELSE 'Overdue Audit (>6 months)'
            END as audit_status,
            COUNT(*) as incidents,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stoppages,
            AVG(workload_team_size) as avg_team_size,
            AVG(CAST(workload_work_duration_hours AS FLOAT)) as avg_work_duration,
            ROUND(COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as work_stoppage_rate,
            STRING_AGG(DISTINCT
                CASE
                    WHEN unsafe_event_details IS NOT NULL AND LENGTH(TRIM(unsafe_event_details)) > 10
                    THEN SUBSTRING(unsafe_event_details, 1, 100)
                END, ' | ') as common_issues,
            CASE
                WHEN site_site_risk_category = 'High Risk' AND workload_workload_category = 'High'
                     THEN 'REDUCE_WORKLOAD_IMMEDIATELY'
                WHEN AVG(site_last_safety_audit_days) > 180 AND COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) > 0
                     THEN 'URGENT_AUDIT_REQUIRED'
                WHEN AVG(CAST(workload_work_duration_hours AS FLOAT)) > 8 AND site_site_risk_category = 'High Risk'
                     THEN 'LIMIT_WORK_HOURS'
                ELSE 'MONITOR'
            END as optimization_recommendation
        FROM {self.table_name}
        WHERE site_site_risk_category IS NOT NULL
        AND workload_workload_category IS NOT NULL
        AND site_last_safety_audit_days IS NOT NULL
        GROUP BY site_site_risk_category, workload_workload_category,
                 CASE
                     WHEN site_last_safety_audit_days <= 90 THEN 'Recent Audit (≤3 months)'
                     WHEN site_last_safety_audit_days BETWEEN 91 AND 180 THEN 'Moderate Audit (3-6 months)'
                     ELSE 'Overdue Audit (>6 months)'
                 END
        ORDER BY work_stoppage_rate DESC, incidents DESC
        """
        return self.execute_query(query)

    def get_staff_performance_with_context(self) -> List[Dict]:
        """Analyze staff performance with environmental and workload context"""
        query = f"""
        SELECT
            reporter_name,
            designation,
            employee_experience_level,
            employee_shift_type,
            COUNT(*) as total_reports,
            COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) as work_stoppages,
            COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) as high_risk_actions,
            AVG(employee_safety_training_hours) as avg_training_hours,
            AVG(weather_weather_severity_score) as avg_weather_severity,
            AVG(workload_team_size) as avg_team_size,
            ROUND(COUNT(CASE WHEN UPPER(work_was_stopped) = 'NO' OR work_was_stopped IS NULL THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as work_continuation_rate,
            ROUND(COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as proactive_action_rate,
            COUNT(DISTINCT location) as locations_worked,
            STRING_AGG(DISTINCT
                CASE
                    WHEN additional_comments IS NOT NULL AND LENGTH(TRIM(additional_comments)) > 10
                    THEN SUBSTRING(additional_comments, 1, 100)
                END, ' | ') as performance_notes,
            CASE
                WHEN COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) = 0
                     AND COUNT(CASE WHEN UPPER(action_related_to_high_risk_situation) = 'YES' THEN 1 END) > 0
                     THEN 'EXCELLENT_PERFORMER'
                WHEN COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) < 10
                     THEN 'GOOD_PERFORMER'
                WHEN COUNT(CASE WHEN UPPER(work_was_stopped) = 'YES' THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) > 30
                     THEN 'NEEDS_SUPPORT'
                ELSE 'AVERAGE_PERFORMER'
            END as performance_category
        FROM {self.table_name}
        WHERE reporter_name IS NOT NULL
        AND employee_experience_level IS NOT NULL
        GROUP BY reporter_name, designation, employee_experience_level, employee_shift_type
        HAVING COUNT(*) >= 3
        ORDER BY work_continuation_rate DESC, proactive_action_rate DESC
        LIMIT 30
        """
        return self.execute_query(query)

    # ==================== COMPREHENSIVE KPI EXECUTION ====================

    def get_all_augmented_kpis(self) -> Dict[str, Any]:
        """Execute optimized augmented KPI queries for LLM (includes standard + augmented KPIs)"""
        try:
            logger.info("Executing optimized NI TCT Augmented KPI queries for LLM...")

            # Get standard NI TCT KPIs first (using same table but standard queries)
            from src.analytics.ni_tct_kpi_queries import NITCTKPIQueries

            # Create standard KPI instance but point to augmented table
            standard_kpis = NITCTKPIQueries()
            standard_kpis.table_name = "unsafe_events_ni_tct_augmented"  # Use augmented table

            # Get essential standard KPIs (limited for LLM efficiency)
            standard_results = {
                # Event Volume & Frequency (core metrics)
                "total_events": standard_kpis.get_total_events_count(),
                "events_by_type": standard_kpis.get_events_by_unsafe_event_type()[:10],  # Top 10 types
                "events_monthly": standard_kpis.get_events_per_time_period('month')[-12:],  # Last 12 months
                "status_distribution": standard_kpis.get_event_status_distribution(),

                # Safety Severity (critical metrics)
                "high_risk_situation_analysis": standard_kpis.get_high_risk_situation_analysis(),
                "work_stopped": standard_kpis.get_work_stopped_incidents(),
                "work_stoppage_duration": standard_kpis.get_work_stoppage_duration_analysis(),

                # Geographic Distribution (top locations)
                "regional_distribution": standard_kpis.get_events_by_region(),
                "branch_distribution": standard_kpis.get_events_by_branch()[:10],  # Top 10 branches

                # Personnel Metrics (top performers)
                "top_reporters": standard_kpis.get_events_by_reporter()[:10],  # Top 10 reporters
                "designation_analysis": standard_kpis.get_events_by_designation()[:10],  # Top 10 designations

                # Operational Metrics (key categories)
                "product_types": standard_kpis.get_events_by_product_type()[:8],  # Top 8 products
                "business_details": standard_kpis.get_events_by_business_details()[:8],  # Top 8 business areas
            }

            # Get augmented KPIs (enhanced insights)
            augmented_results = {
                # Enhanced Event Volume & Frequency
                "total_events_augmented": self.get_total_events_count(),

                # Weather Impact Analysis (top 5 conditions only)
                "weather_impact_analysis": self.get_weather_impact_analysis()[:5],
                "weather_severity_correlation": self.get_weather_severity_correlation(),

                # Employee Experience & Training Analysis (core insights)
                "experience_level_analysis": self.get_experience_level_analysis(),
                "training_effectiveness": self.get_training_effectiveness_analysis()[:10],  # Top 20 training levels
                "shift_type_analysis": self.get_shift_type_analysis(),

                # Site Risk Assessment Analysis (categories only)
                "site_risk_analysis": self.get_site_risk_analysis(),

                # Workload & Team Dynamics Analysis (categories only)
                "workload_impact_analysis": self.get_workload_impact_analysis(),
                "team_size_effectiveness": self.get_team_size_effectiveness(),

                # Multi-Factor Correlation Analysis (top 10 correlations)
                "weather_experience_correlation": self.get_weather_experience_correlation()[:10],
                "site_risk_workload_correlation": self.get_site_risk_workload_correlation(),

                # ==================== ADVANCED OPERATIONAL INTELLIGENCE ====================
                "weather_based_operational_alerts": self.get_weather_based_operational_alerts(),
                "experience_based_resource_optimization": self.get_experience_based_resource_optimization(),
                "site_risk_workload_optimization": self.get_site_risk_workload_optimization(),
                "staff_performance_with_context": self.get_staff_performance_with_context(),
            }

            # Combine standard and augmented KPIs
            results = {**standard_results, **augmented_results}

            logger.info("Optimized NI TCT Augmented KPI queries (standard + augmented) executed successfully")
            return results

        except Exception as e:
            logger.error(f"Error executing optimized NI TCT Augmented KPIs: {e}")
            raise

    def get_all_augmented_kpis_full(self) -> Dict[str, Any]:
        """Execute ALL augmented KPI queries (full dataset for detailed analysis)"""
        try:
            logger.info("Executing ALL NI TCT Augmented KPI queries...")

            results = {
                # Enhanced Event Volume & Frequency
                "total_events_augmented": self.get_total_events_count(),

                # Weather Impact Analysis
                "weather_impact_analysis": self.get_weather_impact_analysis(),
                "weather_severity_correlation": self.get_weather_severity_correlation(),
                "temperature_humidity_impact": self.get_temperature_humidity_impact(),

                # Employee Experience & Training Analysis
                "experience_level_analysis": self.get_experience_level_analysis(),
                "training_effectiveness": self.get_training_effectiveness_analysis(),
                "shift_type_analysis": self.get_shift_type_analysis(),

                # Site Risk Assessment Analysis
                "site_risk_analysis": self.get_site_risk_analysis(),
                "audit_frequency_impact": self.get_audit_frequency_impact(),

                # Workload & Team Dynamics Analysis
                "workload_impact_analysis": self.get_workload_impact_analysis(),
                "team_size_effectiveness": self.get_team_size_effectiveness(),
                "work_duration_fatigue_analysis": self.get_work_duration_fatigue_analysis(),

                # Multi-Factor Correlation Analysis
                "weather_experience_correlation": self.get_weather_experience_correlation(),
                "site_risk_workload_correlation": self.get_site_risk_workload_correlation(),
                "comprehensive_risk_scores": self.get_comprehensive_risk_score(),
            }

            logger.info("All NI TCT Augmented KPI queries executed successfully")
            return results

        except Exception as e:
            logger.error(f"Error executing NI TCT Augmented KPIs: {e}")
            raise
