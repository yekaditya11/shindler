"""
Data Health Assessment Service - Optimized Version
Comprehensive data quality analysis for all schema types with performance optimizations
"""

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, and_, extract, inspect, text, case, cast, String
from typing import Dict, Any, List, Tuple, Optional
import logging
from datetime import datetime, timedelta
from collections import defaultdict
import re
import asyncio
from concurrent.futures import ThreadPoolExecutor

from src.config.database import get_db
from src.models.unsafe_event_models import UnsafeEventEITech, UnsafeEventSRS, UnsafeEventNITCT, UnsafeEventNITCTAugmented
from src.services.semantic_config_service import SemanticConfigService
from src.services.llm_dimension_selector import LLMDimensionSelector

logger = logging.getLogger(__name__)

class DataHealthService:
    """Comprehensive data health assessment service"""
    
    # Model mapping
    MODEL_MAPPING = {
        "ei_tech": UnsafeEventEITech,
        "srs": UnsafeEventSRS,
        "ni_tct": UnsafeEventNITCT,
        "ni_tct_augmented": UnsafeEventNITCTAugmented
    }
    
    # Critical fields for each schema type
    CRITICAL_FIELDS = {
        "ei_tech": ["event_id", "reporter_name", "reported_date", "branch", "region", "unsafe_event_type"],
        "srs": ["event_id", "reporter_name", "reported_date", "branch", "region", "unsafe_event_type"],
        "ni_tct": ["reporting_id", "reporter_name", "created_on", "branch_name", "region", "type_of_unsafe_event"],
        "ni_tct_augmented": ["reporting_id", "reporter_name", "created_on", "branch_name", "region", "type_of_unsafe_event"]
    }
    
    # Data quality dimension weights
    DIMENSION_WEIGHTS = {
        "completeness": 25,
        "uniqueness": 10,
        "consistency": 20,
        "validity": 20,
        "timeliness": 25
    }
    
    def __init__(self, max_concurrent_llm_requests: int = 10, max_concurrent_db_operations: int = 5):
        self._session = None
        self.semantic_config = SemanticConfigService()
        self.llm_selector = LLMDimensionSelector(max_concurrent_requests=max_concurrent_llm_requests)
        self.max_concurrent_db_operations = max_concurrent_db_operations

    def get_session(self):
        """Get a database session"""
        return next(get_db())

    def assess_data_health(self, schema_type: str) -> Dict[str, Any]:
        """
        Optimized comprehensive data health assessment for a schema type

        Args:
            schema_type: Type of schema (ei_tech, srs, ni_tct, ni_tct_augmented)

        Returns:
            Complete health assessment including overall and column-wise analysis
        """
        try:
            logger.info(f"Starting optimized data health assessment for schema: {schema_type}")
            start_time = datetime.now()

            # Validate schema type
            if schema_type not in self.MODEL_MAPPING:
                raise ValueError(f"Unknown schema type: {schema_type}")

            model_class = self.MODEL_MAPPING[schema_type]
            db = self.get_session()

            # Get total record count
            total_records = db.query(model_class).count()

            if total_records == 0:
                return self._empty_health_report(schema_type)

            # Get all column information
            columns_info = self._get_column_info(model_class)

            # Filter out base model fields
            analysis_columns = {k: v for k, v in columns_info.items()
                              if k not in ['id', 'created_at', 'updated_at']}

            # Perform optimized batch analysis
            column_analysis = self._assess_all_columns_optimized(
                db, model_class, analysis_columns, schema_type, total_records
            )

            # Calculate overall health scores
            overall_scores = defaultdict(list)
            for column_health in column_analysis.values():
                for dimension in ['completeness', 'uniqueness', 'consistency', 'validity', 'timeliness']:
                    if dimension in column_health and 'score' in column_health[dimension]:
                        overall_scores[dimension].append(column_health[dimension]['score'])

            overall_dimensions = self._calculate_overall_dimensions(overall_scores)
            overall_score = self._calculate_weighted_score(overall_dimensions)
            health_grade = self._get_health_grade(overall_score)

            # Generate summary and recommendations
            summary = self._generate_summary(column_analysis, schema_type)

            # Build complete response
            health_report = {
                "schema_type": schema_type,
                "total_records": total_records,
                "assessment_timestamp": datetime.now().isoformat(),
                "overall_health": {
                    "score": round(overall_score, 1),
                    "grade": health_grade,
                    "dimensions": overall_dimensions
                },
                "column_analysis": column_analysis,
                "summary": summary
            }

            elapsed_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Data health assessment completed for {schema_type} in {elapsed_time:.2f}s. Overall score: {overall_score}")
            return health_report

        except Exception as e:
            logger.error(f"Error in data health assessment for {schema_type}: {e}")
            raise
        finally:
            if 'db' in locals():
                db.close()

    async def assess_data_health_llm(self, schema_type: str) -> Dict[str, Any]:
        """
        LLM-enhanced data health assessment that intelligently selects dimensions to check

        Args:
            schema_type: Type of schema (ei_tech, srs, ni_tct, ni_tct_augmented)

        Returns:
            Enhanced health assessment with LLM-guided dimension selection
        """
        try:
            logger.info(f"Starting LLM-enhanced data health assessment for schema: {schema_type}")
            start_time = datetime.now()
            llm_elapsed = 0
            assessment_elapsed = 0

            # Validate schema type
            if schema_type not in self.MODEL_MAPPING:
                raise ValueError(f"Unknown schema type: {schema_type}")

            model_class = self.MODEL_MAPPING[schema_type]
            db = self.get_session()

            # Get total record count
            total_records = db.query(model_class).count()

            if total_records == 0:
                return self._empty_health_report(schema_type)

            # Load semantic configuration
            schema_semantics = self.semantic_config.get_schema_semantics(schema_type)

            # Filter out base model fields
            analysis_columns = {k: v for k, v in schema_semantics.items()
                              if k not in ['id', 'created_at', 'updated_at']}

            # Get LLM dimension selection for all columns
            logger.info(f"Getting LLM dimension selection for {len(analysis_columns)} columns")
            llm_start_time = datetime.now()
            dimension_selections = await self.llm_selector.batch_select_dimensions(analysis_columns)
            llm_elapsed = (datetime.now() - llm_start_time).total_seconds()
            logger.info(f"LLM dimension selection completed in {llm_elapsed:.2f}s")

            # Perform LLM-guided analysis
            assessment_start_time = datetime.now()
            column_analysis = await self._assess_columns_with_llm_guidance(
                db, model_class, analysis_columns, dimension_selections, total_records
            )
            assessment_elapsed = (datetime.now() - assessment_start_time).total_seconds()
            logger.info(f"Parallel column assessment completed in {assessment_elapsed:.2f}s")

            # Calculate overall health scores using only checked dimensions
            overall_scores = self._calculate_llm_guided_overall_scores(column_analysis)
            overall_score = self._calculate_weighted_score(overall_scores)
            health_grade = self._get_health_grade(overall_score)

            # Calculate final elapsed time
            elapsed_time = (datetime.now() - start_time).total_seconds()

            # Generate LLM-enhanced summary and recommendations
            summary = self._generate_llm_enhanced_summary(column_analysis, schema_type, dimension_selections)

            # Build enhanced response
            health_report = {
                "schema_type": schema_type,
                "total_records": total_records,
                "assessment_timestamp": datetime.now().isoformat(),
                "assessment_type": "llm_enhanced",
                "overall_health": {
                    "score": round(overall_score, 1),
                    "grade": health_grade,
                    "dimensions": overall_scores
                },
                "column_analysis": column_analysis,
                "summary": summary,
                "llm_insights": {
                    "total_columns_analyzed": len(analysis_columns),
                    "dimension_selections_made": len(dimension_selections)
                },
                "performance_metrics": {
                    "llm_selection_time_seconds": llm_elapsed,
                    "column_assessment_time_seconds": assessment_elapsed,
                    "total_processing_time_seconds": elapsed_time,
                    "parallel_processing_enabled": True,
                    "max_concurrent_llm_requests": self.llm_selector.max_concurrent_requests,
                    "max_concurrent_db_operations": self.max_concurrent_db_operations
                }
            }

            logger.info(f"LLM-enhanced data health assessment completed for {schema_type} in {elapsed_time:.2f}s. Overall score: {overall_score}")
            return health_report

        except Exception as e:
            elapsed_time = (datetime.now() - start_time).total_seconds() if 'start_time' in locals() else 0
            logger.error(f"Error in LLM-enhanced data health assessment for {schema_type}: {e}")
            raise
        finally:
            if 'db' in locals():
                db.close()

    def _get_column_info(self, model_class) -> Dict[str, Dict[str, Any]]:
        """Get column information from SQLAlchemy model"""
        inspector = inspect(model_class)
        columns_info = {}
        
        for column in inspector.columns:
            columns_info[column.name] = {
                'type': str(column.type),
                'nullable': column.nullable,
                'primary_key': column.primary_key,
                'python_type': column.type.python_type if hasattr(column.type, 'python_type') else str
            }
        
        return columns_info

    def _assess_all_columns_optimized(self, db: Session, model_class, columns_info: Dict[str, Dict[str, Any]],
                                    schema_type: str, total_records: int) -> Dict[str, Any]:
        """
        Optimized batch assessment of all columns using minimal database queries
        """
        logger.info(f"Starting optimized batch assessment for {len(columns_info)} columns")

        # Get critical fields for this schema
        critical_fields = self.CRITICAL_FIELDS.get(schema_type, [])

        # Initialize results
        column_analysis = {}

        # Batch 1: Get completeness stats for all columns in one query
        completeness_stats = self._get_batch_completeness_stats(db, model_class, columns_info, total_records)

        # Batch 2: Get uniqueness stats for ID-like columns
        id_columns = {k: v for k, v in columns_info.items() if self._should_assess_uniqueness(k, v)}
        uniqueness_stats = self._get_batch_uniqueness_stats(db, model_class, id_columns, total_records)

        # Batch 3: Get date column stats
        date_columns = {k: v for k, v in columns_info.items() if self._is_date_column(v)}
        timeliness_stats = self._get_batch_timeliness_stats(db, model_class, date_columns)

        # Batch 4: Get sample data for pattern analysis (limited sample)
        sample_data = self._get_sample_data_for_patterns(db, model_class, columns_info)

        # Process each column with pre-computed stats
        for column_name, column_info in columns_info.items():
            is_critical = column_name in critical_fields

            column_health = {
                "data_type": column_info['type'],
                "is_critical": is_critical,
                "overall_column_score": 0.0,
                "issues": [],
                "recommendations": []
            }

            # Add completeness data
            if column_name in completeness_stats:
                column_health["completeness"] = completeness_stats[column_name]

            # Add uniqueness data for applicable columns
            if column_name in uniqueness_stats:
                column_health["uniqueness"] = uniqueness_stats[column_name]

            # Add timeliness data for date columns
            if column_name in timeliness_stats:
                column_health["timeliness"] = timeliness_stats[column_name]

            # Add consistency and validity based on sample data
            if column_name in sample_data:
                consistency = self._assess_consistency_from_sample(sample_data[column_name], column_info, column_name)
                validity = self._assess_validity_from_sample(sample_data[column_name], column_info, column_name)
                column_health["consistency"] = consistency
                column_health["validity"] = validity

            # Calculate overall column score
            column_health["overall_column_score"] = self._calculate_column_score(column_health)

            # Generate column-specific issues and recommendations
            self._generate_column_issues_and_recommendations(column_health, column_name, is_critical)

            column_analysis[column_name] = column_health

        logger.info(f"Completed optimized batch assessment for {len(columns_info)} columns")
        return column_analysis

    def _empty_health_report(self, schema_type: str) -> Dict[str, Any]:
        """Return empty health report when no data exists"""
        return {
            "schema_type": schema_type,
            "total_records": 0,
            "assessment_timestamp": datetime.now().isoformat(),
            "overall_health": {
                "score": 0.0,
                "grade": "N/A",
                "dimensions": {
                    "completeness": {"score": 0.0, "weight": 25},
                    "uniqueness": {"score": 0.0, "weight": 10},
                    "consistency": {"score": 0.0, "weight": 20},
                    "validity": {"score": 0.0, "weight": 20},
                    "timeliness": {"score": 0.0, "weight": 25}
                }
            },
            "column_analysis": {},
            "summary": {
                "critical_fields": {"total": 0, "healthy": 0, "warning": 0, "critical": 0, "avg_score": 0.0},
                "top_issues": [],
            }
        }

    def _get_batch_completeness_stats(self, db: Session, model_class, columns_info: Dict[str, Dict[str, Any]],
                                    total_records: int) -> Dict[str, Dict[str, Any]]:
        """Get completeness statistics for all columns in a single optimized query"""
        try:
            # Build a single query to count nulls for all columns
            null_counts = {}

            # Use a more efficient approach - count non-nulls instead of nulls
            for column_name in columns_info.keys():
                column_attr = getattr(model_class, column_name)
                non_null_count = db.query(func.count(column_attr)).scalar() or 0
                null_count = total_records - non_null_count

                completeness_percentage = (non_null_count / total_records) * 100 if total_records > 0 else 0

                null_counts[column_name] = {
                    "score": round(completeness_percentage, 1),
                    "null_count": null_count,
                    "non_null_count": non_null_count,
                    "null_percentage": round((null_count / total_records) * 100, 1) if total_records > 0 else 0
                }

            return null_counts

        except Exception as e:
            logger.warning(f"Error in batch completeness assessment: {e}")
            return {}

    def _get_batch_uniqueness_stats(self, db: Session, model_class, id_columns: Dict[str, Dict[str, Any]],
                                   total_records: int) -> Dict[str, Dict[str, Any]]:
        """Get uniqueness statistics for ID-like columns in optimized queries"""
        try:
            uniqueness_stats = {}

            for column_name in id_columns.keys():
                column_attr = getattr(model_class, column_name)

                # Get unique count and non-null count in a single query
                unique_count = db.query(func.count(distinct(column_attr))).filter(column_attr.isnot(None)).scalar() or 0
                non_null_count = db.query(func.count(column_attr)).scalar() or 0

                if non_null_count == 0:
                    uniqueness_percentage = 0
                    duplicate_count = 0
                else:
                    uniqueness_percentage = (unique_count / non_null_count) * 100
                    duplicate_count = non_null_count - unique_count

                uniqueness_stats[column_name] = {
                    "score": round(uniqueness_percentage, 1),
                    "unique_count": unique_count,
                    "duplicate_count": duplicate_count,
                    "total_non_null": non_null_count
                }

            return uniqueness_stats

        except Exception as e:
            logger.warning(f"Error in batch uniqueness assessment: {e}")
            return {}

    def _get_batch_timeliness_stats(self, db: Session, model_class, date_columns: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Get timeliness statistics for date columns in optimized queries"""
        try:
            timeliness_stats = {}
            current_date = datetime.now().date()

            for column_name in date_columns.keys():
                column_attr = getattr(model_class, column_name)

                # Get min and max dates in a single query
                result = db.query(func.min(column_attr), func.max(column_attr)).filter(column_attr.isnot(None)).first()

                if not result or not result[1]:  # No data
                    timeliness_stats[column_name] = {"score": 0.0, "days_since_latest": 0, "avg_age_days": 0}
                    continue

                oldest_date, latest_date = result

                # Convert to date if datetime
                if hasattr(latest_date, 'date'):
                    latest_date = latest_date.date()
                if hasattr(oldest_date, 'date'):
                    oldest_date = oldest_date.date()

                days_since_latest = (current_date - latest_date).days

                # Score based on freshness
                if days_since_latest <= 30:
                    freshness_score = 100
                elif days_since_latest <= 60:
                    freshness_score = 85
                elif days_since_latest <= 90:
                    freshness_score = 70
                elif days_since_latest <= 180:
                    freshness_score = 50
                else:
                    freshness_score = 25

                timeliness_stats[column_name] = {
                    "score": freshness_score,
                    "days_since_latest": days_since_latest,
                    "avg_age_days": days_since_latest,  # Simplified
                    "latest_date": latest_date.isoformat() if latest_date else None,
                    "oldest_date": oldest_date.isoformat() if oldest_date else None
                }

            return timeliness_stats

        except Exception as e:
            logger.warning(f"Error in batch timeliness assessment: {e}")
            return {}

    def _get_sample_data_for_patterns(self, db: Session, model_class, columns_info: Dict[str, Dict[str, Any]],
                                    sample_size: int = 500) -> Dict[str, List[str]]:
        """Get sample data for pattern analysis in a single query"""
        try:
            # Get a random sample of records (limit to reduce memory usage)
            sample_records = db.query(model_class).limit(sample_size).all()

            sample_data = {}
            for column_name in columns_info.keys():
                values = []
                for record in sample_records:
                    value = getattr(record, column_name, None)
                    if value is not None:
                        values.append(str(value))

                sample_data[column_name] = values[:100]  # Limit to 100 samples per column

            return sample_data

        except Exception as e:
            logger.warning(f"Error getting sample data: {e}")
            return {}

    def _assess_consistency_from_sample(self, sample_values: List[str], column_info: Dict[str, Any],
                                      column_name: str) -> Dict[str, Any]:
        """Assess consistency from pre-fetched sample data"""
        if not sample_values:
            return {
                "score": 0.0,
                "pattern_violations": 0,
                "total_checked": 0,
                "violation_percentage": 0.0
            }

        violations = 0
        total_checked = len(sample_values)

        # Pattern checks based on column type and name
        if 'date' in column_name.lower():
            violations = self._check_date_patterns(sample_values)
        elif 'id' in column_name.lower():
            violations = self._check_id_patterns(sample_values)
        else:
            violations = self._check_general_patterns(sample_values, column_info)

        consistency_percentage = ((total_checked - violations) / total_checked) * 100 if total_checked > 0 else 0
        violation_percentage = (violations / total_checked) * 100 if total_checked > 0 else 0.0

        return {
            "score": round(consistency_percentage, 1),
            "pattern_violations": violations,
            "total_checked": total_checked,
            "violation_percentage": round(violation_percentage, 1)
        }

    def _assess_validity_from_sample(self, sample_values: List[str], column_info: Dict[str, Any],
                                   column_name: str) -> Dict[str, Any]:
        """Assess validity from pre-fetched sample data"""
        if not sample_values:
            return {
                "score": 0.0,
                "invalid_count": 0,
                "total_checked": 0,
                "invalid_percentage": 0.0
            }

        invalid_count = 0
        total_checked = len(sample_values)

        # Business rule checks based on column name and type
        for value in sample_values:
            if 'date' in column_name.lower():
                # Basic date validity check
                if len(str(value).strip()) == 0:
                    invalid_count += 1
            elif 'id' in column_name.lower():
                # ID validity check
                if not re.match(r'^[a-zA-Z0-9_-]+$', str(value)) or len(str(value).strip()) == 0:
                    invalid_count += 1
            else:
                # General validity check
                if len(str(value).strip()) == 0 or len(str(value)) > 1000:
                    invalid_count += 1

        validity_percentage = ((total_checked - invalid_count) / total_checked) * 100 if total_checked > 0 else 0
        invalid_percentage = (invalid_count / total_checked) * 100 if total_checked > 0 else 0.0

        return {
            "score": round(validity_percentage, 1),
            "invalid_count": invalid_count,
            "total_checked": total_checked,
            "invalid_percentage": round(invalid_percentage, 1)
        }

    def _assess_column_health(self, db: Session, model_class, column_name: str,
                            column_info: Dict[str, Any], schema_type: str, total_records: int) -> Dict[str, Any]:
        """Assess health metrics for a single column"""

        column_attr = getattr(model_class, column_name)
        is_critical = column_name in self.CRITICAL_FIELDS.get(schema_type, [])

        # Initialize column health data
        column_health = {
            "data_type": column_info['type'],
            "is_critical": is_critical,
            "overall_column_score": 0.0,
            "issues": [],
            "recommendations": []
        }

        # 1. Completeness Assessment
        completeness = self._assess_completeness(db, model_class, column_attr, total_records)
        column_health["completeness"] = completeness

        # 2. Uniqueness Assessment (for applicable columns)
        if self._should_assess_uniqueness(column_name, column_info):
            uniqueness = self._assess_uniqueness(db, model_class, column_attr, total_records)
            column_health["uniqueness"] = uniqueness

        # 3. Consistency Assessment
        consistency = self._assess_consistency(db, model_class, column_attr, column_info, total_records)
        column_health["consistency"] = consistency

        # 4. Validity Assessment
        validity = self._assess_validity(db, model_class, column_attr, column_info, column_name, total_records)
        column_health["validity"] = validity

        # 5. Timeliness Assessment (for date/datetime columns)
        if self._is_date_column(column_info):
            timeliness = self._assess_timeliness(db, model_class, column_attr, total_records)
            column_health["timeliness"] = timeliness

        # Calculate overall column score
        column_health["overall_column_score"] = self._calculate_column_score(column_health)

        # Generate column-specific issues and recommendations
        self._generate_column_issues_and_recommendations(column_health, column_name, is_critical)

        return column_health

    def _assess_completeness(self, db: Session, model_class, column_attr, total_records: int) -> Dict[str, Any]:
        """Assess completeness (non-null percentage)"""
        try:
            # Use a fresh session for each query to avoid transaction issues
            fresh_db = self.get_session()
            try:
                null_count = fresh_db.query(model_class).filter(column_attr.is_(None)).count()
                non_null_count = total_records - null_count
                completeness_percentage = (non_null_count / total_records) * 100 if total_records > 0 else 0

                return {
                    "score": round(completeness_percentage, 1),
                    "null_count": null_count,
                    "non_null_count": non_null_count,
                    "null_percentage": round((null_count / total_records) * 100, 1) if total_records > 0 else 0
                }
            finally:
                fresh_db.close()
        except Exception as e:
            logger.warning(f"Error assessing completeness for column: {e}")
            return {"score": 0.0, "null_count": total_records, "non_null_count": 0, "null_percentage": 100.0}

    def _assess_uniqueness(self, db: Session, model_class, column_attr, total_records: int) -> Dict[str, Any]:
        """Assess uniqueness (unique values percentage)"""
        try:
            fresh_db = self.get_session()
            try:
                unique_count = fresh_db.query(func.count(distinct(column_attr))).filter(column_attr.isnot(None)).scalar() or 0
                non_null_count = fresh_db.query(model_class).filter(column_attr.isnot(None)).count()

                if non_null_count == 0:
                    uniqueness_percentage = 0
                    duplicate_count = 0
                else:
                    uniqueness_percentage = (unique_count / non_null_count) * 100
                    duplicate_count = non_null_count - unique_count

                return {
                    "score": round(uniqueness_percentage, 1),
                    "unique_count": unique_count,
                    "duplicate_count": duplicate_count,
                    "total_non_null": non_null_count
                }
            finally:
                fresh_db.close()
        except Exception as e:
            logger.warning(f"Error assessing uniqueness for column: {e}")
            return {"score": 0.0, "unique_count": 0, "duplicate_count": total_records, "total_non_null": total_records}

    def _assess_consistency(self, db: Session, model_class, column_attr, column_info: Dict[str, Any], total_records: int) -> Dict[str, Any]:
        """Assess consistency (format and pattern compliance)"""
        try:
            fresh_db = self.get_session()
            try:
                # Get sample of non-null values for pattern analysis
                sample_values = fresh_db.query(column_attr).filter(column_attr.isnot(None)).limit(1000).all()
                sample_values = [str(val[0]) for val in sample_values if val[0] is not None]

                if not sample_values:
                    return {"score": 0.0, "pattern_violations": 0, "total_checked": 0}

                violations = 0
                total_checked = len(sample_values)

                # Pattern checks based on column type and name
                if 'date' in column_attr.name.lower():
                    violations = self._check_date_patterns(sample_values)
                elif 'id' in column_attr.name.lower():
                    violations = self._check_id_patterns(sample_values)
                else:
                    violations = self._check_general_patterns(sample_values, column_info)

                consistency_percentage = ((total_checked - violations) / total_checked) * 100 if total_checked > 0 else 0

                return {
                    "score": round(consistency_percentage, 1),
                    "pattern_violations": violations,
                    "total_checked": total_checked,
                    "violation_percentage": round((violations / total_checked) * 100, 1) if total_checked > 0 else 0
                }
            finally:
                fresh_db.close()
        except Exception as e:
            logger.warning(f"Error assessing consistency for column: {e}")
            return {"score": 0.0, "pattern_violations": 0, "total_checked": 0}

    def _assess_validity(self, db: Session, model_class, column_attr, column_info: Dict[str, Any],
                        column_name: str, total_records: int) -> Dict[str, Any]:
        """Assess validity (business rule compliance)"""
        try:
            fresh_db = self.get_session()
            try:
                invalid_count = 0
                total_checked = fresh_db.query(model_class).filter(column_attr.isnot(None)).count()

                if total_checked == 0:
                    return {"score": 0.0, "invalid_count": 0, "total_checked": 0}

                # Business rule checks based on column name and type
                if 'date' in column_name.lower():
                    invalid_count = self._check_date_validity(fresh_db, model_class, column_attr)
                elif 'id' in column_name.lower():
                    invalid_count = self._check_id_validity(fresh_db, model_class, column_attr)
                elif column_name in ['status', 'region', 'branch']:
                    invalid_count = self._check_categorical_validity(fresh_db, model_class, column_attr, column_name)
                else:
                    invalid_count = self._check_general_validity(fresh_db, model_class, column_attr, column_info)

                validity_percentage = ((total_checked - invalid_count) / total_checked) * 100 if total_checked > 0 else 0

                return {
                    "score": round(validity_percentage, 1),
                    "invalid_count": invalid_count,
                    "total_checked": total_checked,
                    "invalid_percentage": round((invalid_count / total_checked) * 100, 1) if total_checked > 0 else 0
                }
            finally:
                fresh_db.close()
        except Exception as e:
            logger.warning(f"Error assessing validity for column: {e}")
            return {"score": 0.0, "invalid_count": 0, "total_checked": 0}

    def _assess_timeliness(self, db: Session, model_class, column_attr, total_records: int) -> Dict[str, Any]:
        """Assess timeliness (data freshness for date columns)"""
        try:
            fresh_db = self.get_session()
            try:
                current_date = datetime.now().date()

                # Get latest and oldest dates
                latest_date = fresh_db.query(func.max(column_attr)).filter(column_attr.isnot(None)).scalar()
                oldest_date = fresh_db.query(func.min(column_attr)).filter(column_attr.isnot(None)).scalar()

                if not latest_date:
                    return {"score": 0.0, "days_since_latest": 0, "avg_age_days": 0}

                # Convert to date if datetime
                if hasattr(latest_date, 'date'):
                    latest_date = latest_date.date()
                if hasattr(oldest_date, 'date'):
                    oldest_date = oldest_date.date()

                days_since_latest = (current_date - latest_date).days

                # Simplified average age calculation (avoid complex SQL functions that might fail)
                avg_age_days = days_since_latest  # Use latest date as proxy for average

                # Score based on freshness (fresher data gets higher score)
                if days_since_latest <= 30:
                    freshness_score = 100
                elif days_since_latest <= 60:
                    freshness_score = 85
                elif days_since_latest <= 90:
                    freshness_score = 70
                elif days_since_latest <= 180:
                    freshness_score = 50
                else:
                    freshness_score = 25

                return {
                    "score": freshness_score,
                    "days_since_latest": days_since_latest,
                    "avg_age_days": avg_age_days,
                    "latest_date": latest_date.isoformat() if latest_date else None,
                    "oldest_date": oldest_date.isoformat() if oldest_date else None
                }
            finally:
                fresh_db.close()
        except Exception as e:
            logger.warning(f"Error assessing timeliness for column: {e}")
            return {"score": 0.0, "days_since_latest": 0, "avg_age_days": 0}

    def _should_assess_uniqueness(self, column_name: str, column_info: Dict[str, Any]) -> bool:
        """Determine if uniqueness should be assessed for this column"""
        # Assess uniqueness for ID fields and key identifiers
        unique_indicators = ['id', 'key', 'number', 'no', 'reference']
        return any(indicator in column_name.lower() for indicator in unique_indicators)

    def _is_date_column(self, column_info: Dict[str, Any]) -> bool:
        """Check if column is a date/datetime column"""
        return 'date' in column_info['type'].lower() or 'time' in column_info['type'].lower()

    def _check_date_patterns(self, values: List[str]) -> int:
        """Check date format patterns"""
        violations = 0
        date_patterns = [
            r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
            r'^\d{2}/\d{2}/\d{4}$',  # MM/DD/YYYY
            r'^\d{2}-\d{2}-\d{4}$',  # MM-DD-YYYY
        ]

        for value in values:
            if not any(re.match(pattern, str(value)) for pattern in date_patterns):
                violations += 1

        return violations

    def _check_id_patterns(self, values: List[str]) -> int:
        """Check ID format patterns"""
        violations = 0
        for value in values:
            # IDs should be alphanumeric and not empty
            if not re.match(r'^[a-zA-Z0-9_-]+$', str(value)) or len(str(value).strip()) == 0:
                violations += 1
        return violations

    def _check_email_patterns(self, values: List[str]) -> int:
        """Check email format patterns"""
        violations = 0
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        for value in values:
            if not re.match(email_pattern, str(value)):
                violations += 1

        return violations

    def _check_general_patterns(self, values: List[str], column_info: Dict[str, Any]) -> int:
        """Check general format patterns"""
        violations = 0
        for value in values:
            # Basic checks: not just whitespace, reasonable length
            if len(str(value).strip()) == 0 or len(str(value)) > 1000:
                violations += 1
        return violations

    def _check_date_validity(self, db: Session, model_class, column_attr) -> int:
        """Check date validity (reasonable date ranges)"""
        try:
            current_date = datetime.now().date()
            future_date_count = db.query(model_class).filter(column_attr > current_date).count()
            very_old_date_count = db.query(model_class).filter(column_attr < datetime(1900, 1, 1).date()).count()
            return future_date_count + very_old_date_count
        except:
            return 0

    def _check_id_validity(self, db: Session, model_class, column_attr) -> int:
        """Check ID validity (non-empty, reasonable format)"""
        try:
            # Count empty or very short IDs
            invalid_count = db.query(model_class).filter(
                func.length(func.trim(column_attr)) < 1
            ).count()
            return invalid_count
        except:
            return 0

    def _check_categorical_validity(self, db: Session, model_class, column_attr, column_name: str) -> int:
        """Check categorical field validity"""
        try:
            # For now, just check for empty values
            invalid_count = db.query(model_class).filter(
                func.length(func.trim(column_attr)) < 1
            ).count()
            return invalid_count
        except:
            return 0

    def _check_general_validity(self, db: Session, model_class, column_attr, column_info: Dict[str, Any]) -> int:
        """Check general validity rules"""
        try:
            # Basic validity: non-empty strings, reasonable lengths
            invalid_count = 0
            if 'varchar' in column_info['type'].lower() or 'text' in column_info['type'].lower():
                invalid_count = db.query(model_class).filter(
                    func.length(func.trim(column_attr)) < 1
                ).count()
            return invalid_count
        except:
            return 0

    def _calculate_column_score(self, column_health: Dict[str, Any]) -> float:
        """Calculate overall score for a column based on available dimensions"""
        scores = []
        weights = []

        for dimension, weight in self.DIMENSION_WEIGHTS.items():
            if dimension in column_health and isinstance(column_health[dimension], dict):
                if 'score' in column_health[dimension]:
                    scores.append(column_health[dimension]['score'])
                    weights.append(weight)

        if not scores:
            return 0.0

        # Calculate weighted average
        total_weight = sum(weights)
        weighted_sum = sum(score * weight for score, weight in zip(scores, weights))

        return round(weighted_sum / total_weight, 1) if total_weight > 0 else 0.0

    def _generate_column_issues_and_recommendations(self, column_health: Dict[str, Any],
                                                  column_name: str, is_critical: bool):
        """Generate issues and recommendations for a column"""
        issues = []
        recommendations = []

        # Check completeness issues
        if 'completeness' in column_health:
            null_pct = column_health['completeness'].get('null_percentage', 0)
            if null_pct > 20:
                issues.append(f"{null_pct}% missing values")
                recommendations.append(f"Address {column_health['completeness'].get('null_count', 0)} missing {column_name} values")
            elif null_pct > 5:
                issues.append(f"{null_pct}% missing values")

        # Check uniqueness issues
        if 'uniqueness' in column_health:
            dup_count = column_health['uniqueness'].get('duplicate_count', 0)
            if dup_count > 0:
                issues.append(f"{dup_count} duplicate values")
                recommendations.append(f"Investigate {dup_count} duplicate {column_name} entries")

        # Check consistency issues
        if 'consistency' in column_health:
            violations = column_health['consistency'].get('pattern_violations', 0)
            if violations > 0:
                issues.append(f"{violations} format violations")
                recommendations.append(f"Standardize {column_name} format")

        # Check validity issues
        if 'validity' in column_health:
            invalid_count = column_health['validity'].get('invalid_count', 0)
            if invalid_count > 0:
                issues.append(f"{invalid_count} invalid values")
                recommendations.append(f"Fix {invalid_count} invalid {column_name} values")

        # Check timeliness issues
        if 'timeliness' in column_health:
            days_old = column_health['timeliness'].get('days_since_latest', 0)
            if days_old > 30:
                issues.append(f"Data is {days_old} days old")
                recommendations.append(f"Update {column_name} data (last update: {days_old} days ago)")

        column_health['issues'] = issues
        column_health['recommendations'] = recommendations

    def _calculate_overall_dimensions(self, overall_scores: Dict[str, List[float]]) -> Dict[str, Dict[str, Any]]:
        """Calculate overall dimension scores"""
        dimensions = {}

        for dimension, weight in self.DIMENSION_WEIGHTS.items():
            scores = overall_scores.get(dimension, [])
            avg_score = sum(scores) / len(scores) if scores else 0.0

            dimensions[dimension] = {
                "score": round(avg_score, 1),
                "weight": weight
            }

        return dimensions

    def _calculate_weighted_score(self, dimensions: Dict[str, Dict[str, Any]]) -> float:
        """Calculate weighted overall score"""
        total_weight = 0
        weighted_sum = 0

        for dimension_data in dimensions.values():
            score = dimension_data['score']
            weight = dimension_data['weight']
            weighted_sum += score * weight
            total_weight += weight

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def _get_health_grade(self, score: float) -> str:
        """Convert numeric score to descriptive grade"""
        if score >= 85:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 50:
            return "Poor"
        else:
            return "Bad"

    def _generate_summary(self, column_analysis: Dict[str, Any], schema_type: str) -> Dict[str, Any]:
        """Generate summary statistics and recommendations"""
        critical_fields = self.CRITICAL_FIELDS.get(schema_type, [])

        # Critical fields analysis
        critical_scores = []
        healthy_fields = 0
        warning_fields = 0
        critical_issues = 0

        all_issues = []

        for column_name, column_data in column_analysis.items():
            column_score = column_data.get('overall_column_score', 0)
            is_critical = column_name in critical_fields

            if is_critical:
                critical_scores.append(column_score)

                if column_score >= 80:
                    healthy_fields += 1
                elif column_score >= 60:
                    warning_fields += 1
                else:
                    critical_issues += 1

            # Collect issues for prioritization
            issues = column_data.get('issues', [])
            for issue in issues:
                severity = 'high' if is_critical and column_score < 60 else 'medium' if column_score < 70 else 'low'
                all_issues.append({
                    'severity': severity,
                    'column': column_name,
                    'issue': issue,
                    'impact': self._get_impact_description(column_name, issue, is_critical)
                })

        # Sort issues by severity
        severity_order = {'high': 0, 'medium': 1, 'low': 2}
        all_issues.sort(key=lambda x: severity_order.get(x['severity'], 3))

        # Generate recommendations
        recommendations = self._generate_recommendations(all_issues, column_analysis)

        return {
            "critical_fields": {
                "total": len(critical_fields),
                "healthy": healthy_fields,
                "warning": warning_fields,
                "critical": critical_issues,
                "avg_score": round(sum(critical_scores) / len(critical_scores), 1) if critical_scores else 0.0
            },
            "top_issues": all_issues[:5],  # Top 5 issues
            "recommendations": recommendations
        }

    def _get_impact_description(self, column_name: str, issue: str, is_critical: bool) -> str:
        """Generate impact description for an issue"""
        if is_critical:
            if 'missing' in issue.lower():
                return f"Critical field {column_name} missing values affects data reliability"
            elif 'duplicate' in issue.lower():
                return f"Duplicate {column_name} values may indicate data integration issues"
            elif 'invalid' in issue.lower():
                return f"Invalid {column_name} values compromise data quality"
            else:
                return f"Issues with critical field {column_name} affect overall data integrity"
        else:
            return f"Data quality issues in {column_name} may impact analysis accuracy"

    def _generate_recommendations(self, issues: List[Dict[str, Any]], column_analysis: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate categorized recommendations"""
        immediate = []
        short_term = []
        long_term = []

        # Immediate actions (high severity issues)
        high_severity_issues = [issue for issue in issues if issue['severity'] == 'high']
        for issue in high_severity_issues[:3]:  # Top 3 high severity
            immediate.append(f"Fix {issue['issue']} in {issue['column']}")

        # Short-term actions (medium severity and consistency issues)
        medium_issues = [issue for issue in issues if issue['severity'] == 'medium']
        for issue in medium_issues[:3]:  # Top 3 medium severity
            short_term.append(f"Address {issue['issue']} in {issue['column']}")

        # Long-term actions (systematic improvements)
        if any('format' in issue['issue'].lower() for issue in issues):
            long_term.append("Implement data validation rules at ingestion")

        if any('duplicate' in issue['issue'].lower() for issue in issues):
            long_term.append("Set up automated duplicate detection")

        if any('missing' in issue['issue'].lower() for issue in issues):
            long_term.append("Establish data completeness monitoring")

        long_term.append("Set up automated data quality monitoring")

        return {
            "immediate": immediate if immediate else ["No immediate actions required"],
            "short_term": short_term if short_term else ["Monitor data quality trends"],
            "long_term": long_term
        }

    async def _assess_columns_with_llm_guidance(self, db, model_class, analysis_columns: Dict[str, Any],
                                              dimension_selections: Dict[str, Dict[str, Any]],
                                              total_records: int) -> Dict[str, Any]:
        """
        Assess columns using LLM-guided dimension selection with parallel processing
        """
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        logger.info(f"Starting parallel column assessment for {len(analysis_columns)} columns")

        # Create tasks for parallel processing
        tasks = []
        column_names = []

        for column_name, column_data in analysis_columns.items():
            task = self._assess_single_column_with_llm_guidance(
                db, model_class, column_name, column_data,
                dimension_selections.get(column_name, self.llm_selector._get_default_dimensions()),
                total_records
            )
            tasks.append(task)
            column_names.append(column_name)

        # Execute all column assessments in parallel
        try:
            results_list = await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error in parallel column assessment: {e}")
            # Fallback to sequential processing
            return await self._sequential_assess_columns_with_llm_guidance(
                db, model_class, analysis_columns, dimension_selections, total_records
            )

        # Process results
        column_analysis = {}
        for column_name, result in zip(column_names, results_list):
            if isinstance(result, Exception):
                logger.error(f"Error assessing column {column_name}: {result}")
                column_analysis[column_name] = {
                    "error": f"Assessment failed: {str(result)}",
                    "dimensions_checked": [],
                    "overall_column_score": 0
                }
            else:
                column_analysis[column_name] = result

        logger.info(f"Completed parallel column assessment for {len(column_analysis)} columns")
        return column_analysis

    async def _assess_single_column_with_llm_guidance(self, db, model_class, column_name: str,
                                                    column_data: Dict[str, Any],
                                                    dimension_selection: Dict[str, Any],
                                                    total_records: int) -> Dict[str, Any]:
        """
        Assess a single column with LLM guidance - designed for parallel execution
        """
        try:
            logger.debug(f"Assessing column {column_name} with LLM guidance")

            dimensions_to_check = dimension_selection.get('dimensions_to_check', [])

            column_result = {
                "dimensions_checked": dimensions_to_check,
                "dimensions_skipped": dimension_selection.get('dimensions_to_skip', []),
                "llm_reasoning": dimension_selection.get('reasoning', {}),
                "priority": dimension_selection.get('priority', 'medium')
            }

            # Run dimension checks in parallel using ThreadPoolExecutor for DB operations
            with ThreadPoolExecutor(max_workers=self.max_concurrent_db_operations) as executor:
                dimension_tasks = {}

                if "completeness" in dimensions_to_check:
                    column_attr = getattr(model_class, column_name)
                    dimension_tasks["completeness"] = executor.submit(
                        self._assess_completeness, db, model_class, column_attr, total_records
                    )

                if "uniqueness" in dimensions_to_check:
                    column_attr = getattr(model_class, column_name)
                    dimension_tasks["uniqueness"] = executor.submit(
                        self._assess_uniqueness, db, model_class, column_attr, total_records
                    )

                if "consistency" in dimensions_to_check:
                    column_attr = getattr(model_class, column_name)
                    column_info = {"data_type": column_data.get("data_type", "string")}
                    dimension_tasks["consistency"] = executor.submit(
                        self._assess_consistency, db, model_class, column_attr, column_info, total_records
                    )

                if "validity" in dimensions_to_check:
                    column_attr = getattr(model_class, column_name)
                    column_info = {"data_type": column_data.get("data_type", "string")}
                    dimension_tasks["validity"] = executor.submit(
                        self._assess_validity, db, model_class, column_attr, column_info, column_name, total_records
                    )

                if "timeliness" in dimensions_to_check:
                    column_attr = getattr(model_class, column_name)
                    dimension_tasks["timeliness"] = executor.submit(
                        self._assess_timeliness, db, model_class, column_attr, total_records
                    )

                # Collect results from parallel dimension assessments
                for dimension, future in dimension_tasks.items():
                    try:
                        column_result[dimension] = future.result(timeout=30)  # 30 second timeout
                    except Exception as e:
                        logger.error(f"Error in {dimension} assessment for {column_name}: {e}")
                        column_result[dimension] = {"score": 0, "error": str(e)}

            # Calculate overall column score for checked dimensions only
            column_result["overall_column_score"] = self._calculate_column_score_llm_guided(
                column_result, dimensions_to_check
            )

            # Generate issues and recommendations
            issues, recommendations = self._generate_column_issues_and_recommendations_llm(
                column_result, column_name, dimension_selection
            )
            column_result["issues"] = issues
            column_result["recommendations"] = recommendations

            return column_result

        except Exception as e:
            logger.error(f"Error assessing column {column_name}: {e}")
            return {
                "error": f"Assessment failed: {str(e)}",
                "dimensions_checked": [],
                "overall_column_score": 0
            }

    async def _sequential_assess_columns_with_llm_guidance(self, db, model_class, analysis_columns: Dict[str, Any],
                                                         dimension_selections: Dict[str, Dict[str, Any]],
                                                         total_records: int) -> Dict[str, Any]:
        """
        Fallback sequential processing if parallel fails
        """
        column_analysis = {}

        for column_name, column_data in analysis_columns.items():
            try:
                dimension_selection = dimension_selections.get(column_name, self.llm_selector._get_default_dimensions())
                column_result = await self._assess_single_column_with_llm_guidance(
                    db, model_class, column_name, column_data, dimension_selection, total_records
                )
                column_analysis[column_name] = column_result

            except Exception as e:
                logger.error(f"Error assessing column {column_name}: {e}")
                column_analysis[column_name] = {
                    "error": f"Assessment failed: {str(e)}",
                    "dimensions_checked": [],
                    "overall_column_score": 0
                }

        return column_analysis

    def _calculate_column_score_llm_guided(self, column_result: Dict[str, Any], dimensions_checked: List[str]) -> float:
        """
        Calculate column score using only the dimensions that were checked
        """
        if not dimensions_checked:
            return 0.0

        # Get weights for checked dimensions only
        active_weights = {dim: self.DIMENSION_WEIGHTS[dim] for dim in dimensions_checked if dim in self.DIMENSION_WEIGHTS}

        if not active_weights:
            return 0.0

        # Normalize weights to 100%
        total_weight = sum(active_weights.values())
        normalized_weights = {dim: (weight/total_weight)*100 for dim, weight in active_weights.items()}

        # Calculate weighted score
        weighted_score = 0.0
        for dimension in dimensions_checked:
            if dimension in column_result and isinstance(column_result[dimension], dict):
                score = column_result[dimension].get('score', 0)
                weight = normalized_weights.get(dimension, 0)
                weighted_score += (score * weight / 100)

        return round(weighted_score, 1)

    def _calculate_llm_guided_overall_scores(self, column_analysis: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Calculate overall dimension scores considering only columns where each dimension was checked
        """
        dimension_scores = defaultdict(list)

        # Collect scores for each dimension from columns that checked it
        for column_name, column_data in column_analysis.items():
            if isinstance(column_data, dict) and 'dimensions_checked' in column_data:
                dimensions_checked = column_data.get('dimensions_checked', [])

                for dimension in dimensions_checked:
                    if dimension in column_data and isinstance(column_data[dimension], dict):
                        score = column_data[dimension].get('score')
                        if score is not None:
                            dimension_scores[dimension].append(score)

        # Calculate average scores for each dimension
        overall_dimensions = {}
        for dimension, scores in dimension_scores.items():
            if scores:
                avg_score = sum(scores) / len(scores)
                overall_dimensions[dimension] = {
                    "score": round(avg_score, 1),
                    "weight": self.DIMENSION_WEIGHTS.get(dimension, 0),
                    "columns_assessed": len(scores)
                }

        return overall_dimensions

    def _generate_llm_enhanced_summary(self, column_analysis: Dict[str, Any], schema_type: str,
                                     dimension_selections: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate enhanced summary with LLM insights
        """
        # Get basic summary
        basic_summary = self._generate_summary(column_analysis, schema_type)

        # Add LLM-specific insights
        llm_insights = {
            "dimension_optimization": self._analyze_dimension_optimization(dimension_selections),
            "intelligent_skips": self._analyze_intelligent_skips(dimension_selections),
            "priority_distribution": self._analyze_priority_distribution(dimension_selections)
        }

        # Enhance recommendations with LLM context
        enhanced_recommendations = self._enhance_recommendations_with_llm_context(
            basic_summary.get('recommendations', {}), dimension_selections
        )

        return {
            **basic_summary,
            "recommendations": enhanced_recommendations,
            "llm_insights": llm_insights
        }

    def _analyze_dimension_optimization(self, dimension_selections: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze how LLM optimized dimension selection"""
        total_possible_checks = len(dimension_selections) * 5  # 5 dimensions per column
        total_actual_checks = sum(len(selection.get('dimensions_to_check', [])) for selection in dimension_selections.values())

        optimization_percentage = ((total_possible_checks - total_actual_checks) / total_possible_checks) * 100

        return {
            "total_possible_checks": total_possible_checks,
            "total_actual_checks": total_actual_checks,
            "checks_skipped": total_possible_checks - total_actual_checks,
            "optimization_percentage": round(optimization_percentage, 1)
        }

    def _analyze_intelligent_skips(self, dimension_selections: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze which dimensions were intelligently skipped"""
        skip_analysis = defaultdict(int)
        skip_reasons = defaultdict(list)

        for column_name, selection in dimension_selections.items():
            skipped = selection.get('dimensions_to_skip', [])
            reasoning = selection.get('reasoning', {})

            for dimension in skipped:
                skip_analysis[dimension] += 1
                reason = reasoning.get(dimension, 'No reason provided')
                skip_reasons[dimension].append(f"{column_name}: {reason}")

        return {
            "skip_counts": dict(skip_analysis),
            "skip_reasons": dict(skip_reasons)
        }

    def _analyze_priority_distribution(self, dimension_selections: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze priority distribution of columns"""
        priority_counts = defaultdict(int)

        for selection in dimension_selections.values():
            priority = selection.get('priority', 'medium')
            priority_counts[priority] += 1

        return dict(priority_counts)

    def _enhance_recommendations_with_llm_context(self, basic_recommendations: Dict[str, Any],
                                                 dimension_selections: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Enhance recommendations with LLM context"""
        enhanced = basic_recommendations.copy()

        # Add LLM-specific recommendations
        llm_recommendations = []

        # Analyze high-priority issues
        critical_columns = [col for col, sel in dimension_selections.items() if sel.get('priority') == 'critical']
        if critical_columns:
            llm_recommendations.append(f"Focus on {len(critical_columns)} critical columns identified by semantic analysis: {', '.join(critical_columns[:5])}")

        # Analyze optimization opportunities
        optimization_analysis = self._analyze_dimension_optimization(dimension_selections)
        if optimization_analysis['optimization_percentage'] > 20:
            llm_recommendations.append(f"LLM optimization reduced validation overhead by {optimization_analysis['optimization_percentage']:.1f}% while maintaining quality focus")

        enhanced['llm_recommendations'] = llm_recommendations
        return enhanced

    def _generate_column_recommendations(self, column_result: Dict[str, Any], column_name: str,
                                       dimension_selection: Dict[str, Any]) -> List[str]:
        """Generate column-specific recommendations with LLM context"""
        recommendations = []

        # Get LLM reasoning for context
        reasoning = dimension_selection.get('reasoning', {})
        priority = dimension_selection.get('priority', 'medium')

        # Generate recommendations based on checked dimensions
        for dimension in column_result.get('dimensions_checked', []):
            if dimension in column_result and isinstance(column_result[dimension], dict):
                score = column_result[dimension].get('score', 0)

                if score < 70:  # Poor score
                    llm_context = reasoning.get(dimension, '')
                    if priority == 'critical':
                        recommendations.append(f"CRITICAL: {dimension} issue in {column_name} - {llm_context}")
                    else:
                        recommendations.append(f"Improve {dimension} for {column_name} - {llm_context}")

        # Add LLM-specific insights
        skipped_dimensions = column_result.get('dimensions_skipped', [])
        if skipped_dimensions:
            recommendations.append(f"LLM intelligently skipped {', '.join(skipped_dimensions)} - not relevant for this field type")

        return recommendations if recommendations else ["No specific recommendations - column meets quality standards"]

    def _generate_column_issues_and_recommendations_llm(self, column_result: Dict[str, Any],
                                                       column_name: str,
                                                       dimension_selection: Dict[str, Any]) -> tuple:
        """
        Generate issues and recommendations for a column with LLM context

        Returns:
            tuple: (issues_list, recommendations_list)
        """
        issues = []
        recommendations = []

        # Get LLM reasoning for context
        reasoning = dimension_selection.get('reasoning', {})
        priority = dimension_selection.get('priority', 'medium')
        dimensions_checked = column_result.get('dimensions_checked', [])

        # Generate issues based on checked dimensions
        for dimension in dimensions_checked:
            if dimension in column_result and isinstance(column_result[dimension], dict):
                score = column_result[dimension].get('score', 0)

                if score < 70:  # Poor score threshold
                    llm_context = reasoning.get(dimension, '')

                    if priority == 'critical':
                        issues.append(f"CRITICAL: {dimension} issue in {column_name} - {llm_context}")
                        recommendations.append(f"URGENT: Address {dimension} in {column_name} immediately - {llm_context}")
                    elif score < 50:  # Very poor
                        issues.append(f"Poor {dimension} in {column_name} (score: {score}) - {llm_context}")
                        recommendations.append(f"Improve {dimension} for {column_name} - {llm_context}")
                    else:  # Moderate issues
                        issues.append(f"Moderate {dimension} issues in {column_name} (score: {score})")
                        recommendations.append(f"Monitor and improve {dimension} for {column_name}")

        # Add LLM-specific insights
        skipped_dimensions = column_result.get('dimensions_skipped', [])
        if skipped_dimensions:
            recommendations.append(f"LLM intelligently skipped {', '.join(skipped_dimensions)} - not relevant for this field type")

        # Add priority-based recommendations
        if priority == 'critical' and not issues:
            recommendations.append(f"Critical field {column_name} is performing well - maintain current quality standards")
        elif priority == 'low' and issues:
            recommendations.append(f"Low priority field {column_name} has issues but can be addressed in maintenance cycles")

        # Default messages if no issues found
        if not issues:
            issues = ["No significant data quality issues detected"]

        if not recommendations:
            recommendations = ["Column meets quality standards - continue monitoring"]

        return issues, recommendations
