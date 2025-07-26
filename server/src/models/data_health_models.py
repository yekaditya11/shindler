"""
Data Health Models
Pydantic models for data health API responses and SQLAlchemy models for storage
"""

from pydantic import BaseModel as PydanticBaseModel, Field
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, JSON
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.models.base_models import BaseModel

# Pydantic Models for API Responses

class DimensionScore(PydanticBaseModel):
    """Individual dimension score with weight"""
    score: float = Field(..., description="Score from 0-100")
    weight: int = Field(..., description="Weight percentage in overall calculation")

class OverallHealth(PydanticBaseModel):
    """Overall health summary"""
    score: float = Field(..., description="Overall weighted health score")
    grade: str = Field(..., description="Descriptive grade (Excellent, Good, Poor, Bad)")
    dimensions: Dict[str, DimensionScore] = Field(..., description="Individual dimension scores")

class CompletenessMetrics(PydanticBaseModel):
    """Completeness assessment metrics"""
    score: float = Field(..., description="Completeness score (0-100)")
    null_count: int = Field(..., description="Number of null/missing values")
    non_null_count: int = Field(..., description="Number of non-null values")
    null_percentage: float = Field(..., description="Percentage of null values")

class UniquenessMetrics(PydanticBaseModel):
    """Uniqueness assessment metrics"""
    score: float = Field(..., description="Uniqueness score (0-100)")
    unique_count: int = Field(..., description="Number of unique values")
    duplicate_count: int = Field(..., description="Number of duplicate values")
    total_non_null: int = Field(..., description="Total non-null values checked")

class ConsistencyMetrics(PydanticBaseModel):
    """Consistency assessment metrics"""
    score: float = Field(..., description="Consistency score (0-100)")
    pattern_violations: int = Field(..., description="Number of pattern violations")
    total_checked: int = Field(..., description="Total values checked")
    violation_percentage: float = Field(..., description="Percentage of violations")

class ValidityMetrics(PydanticBaseModel):
    """Validity assessment metrics"""
    score: float = Field(..., description="Validity score (0-100)")
    invalid_count: int = Field(..., description="Number of invalid values")
    total_checked: int = Field(..., description="Total values checked")
    invalid_percentage: float = Field(..., description="Percentage of invalid values")

class TimelinessMetrics(PydanticBaseModel):
    """Timeliness assessment metrics"""
    score: float = Field(..., description="Timeliness score (0-100)")
    days_since_latest: int = Field(..., description="Days since most recent data")
    avg_age_days: int = Field(..., description="Average age of data in days")
    latest_date: Optional[str] = Field(None, description="Most recent date in ISO format")
    oldest_date: Optional[str] = Field(None, description="Oldest date in ISO format")

class ColumnAnalysis(PydanticBaseModel):
    """Complete analysis for a single column"""
    data_type: str = Field(..., description="Column data type")
    is_critical: bool = Field(..., description="Whether this is a critical field")
    overall_column_score: float = Field(..., description="Overall score for this column")
    issues: List[str] = Field(..., description="List of identified issues")
    recommendations: List[str] = Field(..., description="List of recommendations")
    
    # Optional dimension metrics (not all columns have all dimensions)
    completeness: Optional[CompletenessMetrics] = None
    uniqueness: Optional[UniquenessMetrics] = None
    consistency: Optional[ConsistencyMetrics] = None
    validity: Optional[ValidityMetrics] = None
    timeliness: Optional[TimelinessMetrics] = None

class Issue(PydanticBaseModel):
    """Data quality issue"""
    severity: str = Field(..., description="Issue severity: high, medium, low")
    column: str = Field(..., description="Column name with the issue")
    issue: str = Field(..., description="Description of the issue")
    impact: str = Field(..., description="Impact description")

class CriticalFieldsSummary(PydanticBaseModel):
    """Summary of critical fields health"""
    total: int = Field(..., description="Total number of critical fields")
    healthy: int = Field(..., description="Number of healthy critical fields (score >= 80)")
    warning: int = Field(..., description="Number of warning critical fields (score 60-79)")
    critical: int = Field(..., description="Number of critical issues (score < 60)")
    avg_score: float = Field(..., description="Average score of critical fields")

class Recommendations(PydanticBaseModel):
    """Categorized recommendations"""
    immediate: List[str] = Field(..., description="Immediate actions required")
    short_term: List[str] = Field(..., description="Short-term improvements")
    long_term: List[str] = Field(..., description="Long-term strategic actions")

class Summary(PydanticBaseModel):
    """Health assessment summary"""
    critical_fields: CriticalFieldsSummary = Field(..., description="Critical fields analysis")
    top_issues: List[Issue] = Field(..., description="Top 5 most important issues")
    recommendations: Recommendations = Field(..., description="Categorized recommendations")

class DataHealthReport(PydanticBaseModel):
    """Complete data health assessment report"""
    schema_type: str = Field(..., description="Schema type assessed")
    total_records: int = Field(..., description="Total number of records analyzed")
    assessment_timestamp: str = Field(..., description="When assessment was performed")
    overall_health: OverallHealth = Field(..., description="Overall health summary")
    column_analysis: Dict[str, ColumnAnalysis] = Field(..., description="Column-by-column analysis")
    summary: Summary = Field(..., description="Summary and recommendations")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# SQLAlchemy Models for Storage

class DataHealthHistory(BaseModel):
    """Store data health assessment history"""
    __tablename__ = "data_health_history"

    schema_type = Column(String(50), nullable=False, index=True)
    overall_score = Column(Float, nullable=False)
    health_grade = Column(String(20), nullable=False)
    total_records = Column(Integer, nullable=False)
    
    # Store dimension scores
    completeness_score = Column(Float, nullable=True)
    uniqueness_score = Column(Float, nullable=True)
    consistency_score = Column(Float, nullable=True)
    validity_score = Column(Float, nullable=True)
    timeliness_score = Column(Float, nullable=True)
    
    # Store detailed analysis as JSON
    column_analysis = Column(JSON, nullable=True)
    summary_data = Column(JSON, nullable=True)
    
    # Assessment metadata
    assessment_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<DataHealthHistory(schema={self.schema_type}, score={self.overall_score}, date={self.assessment_timestamp})>"

class DataQualityAlert(BaseModel):
    """Store data quality alerts when thresholds are breached"""
    __tablename__ = "data_quality_alerts"
    
    schema_type = Column(String(50), nullable=False, index=True)
    column_name = Column(String(100), nullable=True)
    alert_type = Column(String(50), nullable=False)  # 'overall_score', 'completeness', etc.
    threshold_value = Column(Float, nullable=False)
    actual_value = Column(Float, nullable=False)
    severity = Column(String(20), nullable=False)  # 'high', 'medium', 'low'
    message = Column(Text, nullable=False)
    resolved = Column(String(10), nullable=False, default='false')
    resolved_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<DataQualityAlert(schema={self.schema_type}, type={self.alert_type}, severity={self.severity})>"
