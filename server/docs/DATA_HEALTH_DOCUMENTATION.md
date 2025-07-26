# Data Health Assessment System - Comprehensive Documentation

## Overview

The Data Health Assessment System is a comprehensive data quality analysis service designed to evaluate the health and quality of unsafe event data across multiple schema types. It provides detailed insights into data completeness, uniqueness, consistency, validity, and timeliness.

## System Architecture

### Core Components

1. **DataHealthService** - Main service class that orchestrates health assessments
2. **Model Mapping** - Maps schema types to their corresponding SQLAlchemy models
3. **Critical Fields Definition** - Identifies essential fields for each schema type
4. **Quality Dimensions** - Five key dimensions with weighted scoring

### Supported Schema Types

The system supports four main data schemas:

1. **`ei_tech`** - EI Tech App unsafe events (54 columns)
2. **`srs`** - SRS (Safety Reporting System) events (47 columns)  
3. **`ni_tct`** - NI TCT App unsafe events (43 columns)
4. **`ni_tct_augmented`** - Enhanced NI TCT events with additional data (58 columns)

## Data Quality Dimensions

### 1. Completeness (Weight: 25%)
**What it measures:** Percentage of non-null values in each column

**Assessment Process:**
- Counts null vs non-null values for each column
- Calculates completeness percentage: `(non_null_count / total_records) * 100`
- Uses optimized batch queries to minimize database load

**Scoring:**
- 100% = Perfect completeness (no missing values)
- 0% = Complete absence of data

**Critical Thresholds:**
- >95%: Excellent
- 80-95%: Good  
- 60-80%: Warning
- <60%: Critical

### 2. Uniqueness (Weight: 10%)
**What it measures:** Percentage of unique values in identifier columns

**Assessment Process:**
- Applied only to ID-like columns (containing 'id', 'key', 'number', 'no', 'reference')
- Counts distinct values vs total non-null values
- Calculates uniqueness percentage: `(unique_count / non_null_count) * 100`

**Scoring:**
- 100% = All values are unique (ideal for primary keys)
- Lower percentages indicate duplicate entries

### 3. Consistency (Weight: 20%)
**What it measures:** Adherence to expected data formats and patterns

**Assessment Process:**
- Analyzes sample data (up to 500 records) for pattern compliance
- Different validation rules based on column type:
  - **Date columns:** Validates against common date formats (YYYY-MM-DD, MM/DD/YYYY, MM-DD-YYYY)
  - **ID columns:** Checks for alphanumeric patterns with allowed special characters
  - **General columns:** Basic format validation

**Pattern Checks:**
- **Date formats:** YYYY-MM-DD, MM/DD/YYYY, MM-DD-YYYY
- **ID formats:** Alphanumeric characters with underscore/hyphen allowed
- **General formats:** Non-empty strings with reasonable length limits

### 4. Validity (Weight: 20%)
**What it measures:** Compliance with business rules and logical constraints

**Assessment Process:**
- Validates data against business logic rules
- Column-specific validation:
  - **Date columns:** Checks for reasonable date ranges (not future dates, not before 1900)
  - **ID columns:** Ensures non-empty, reasonable format
  - **Categorical fields:** Validates against expected values
  - **General fields:** Checks for empty strings, reasonable lengths

**Business Rules:**
- Dates should not be in the future
- Dates should not be before 1900
- IDs should not be empty or contain only whitespace
- Text fields should not exceed 1000 characters

### 5. Timeliness (Weight: 25%)
**What it measures:** Data freshness for date/datetime columns

**Assessment Process:**
- Calculates days since the most recent date entry
- Applies freshness scoring based on age thresholds

**Freshness Scoring:**
- ≤30 days: 100 points (Excellent)
- 31-60 days: 85 points (Good)
- 61-90 days: 70 points (Fair)
- 91-180 days: 50 points (Poor)
- >180 days: 25 points (Critical)

## Critical Fields by Schema

### EI Tech Schema
Essential fields: event_id, reporter_name, reported_date, branch, region, unsafe_event_type

### SRS Schema
Essential fields: event_id, reporter_name, reported_date, branch, region, unsafe_event_type

### NI TCT & NI TCT Augmented Schemas
Essential fields: reporting_id, reporter_name, created_on, branch_name, region, type_of_unsafe_event

## Assessment Process Flow

### 1. Initialization
The service validates the requested schema type and prepares for assessment

### 2. Data Validation
- Validates schema type against supported models
- Retrieves total record count
- Returns empty report if no data exists

### 3. Column Analysis (Optimized Batch Processing)
The system uses optimized batch queries to minimize database load:

**Batch 1: Completeness Statistics**
- Single query to count non-null values for all columns
- Calculates null percentages efficiently

**Batch 2: Uniqueness Statistics**  
- Processes only ID-like columns
- Gets unique counts and duplicate counts

**Batch 3: Timeliness Statistics**
- Processes only date/datetime columns
- Gets min/max dates for freshness calculation

**Batch 4: Sample Data Collection**
- Retrieves limited sample (500 records) for pattern analysis
- Used for consistency and validity assessments

### 4. Score Calculation
- **Column Score:** Weighted average of available dimension scores
- **Overall Score:** Weighted average across all columns
- **Health Grade:** Descriptive grade (Excellent, Good, Poor, Bad) based on overall score

### 5. Issue Detection and Recommendations
- Identifies data quality issues by severity (high/medium/low)
- Generates actionable recommendations categorized as:
  - **Immediate:** Critical issues requiring urgent attention
  - **Short-term:** Medium priority improvements
  - **Long-term:** Systematic enhancements


## Output Structure

### Health Report Format
```json
{
  "schema_type": "ei_tech",
  "total_records": 1500,
  "assessment_timestamp": "2024-01-15T10:30:00",
  "overall_health": {
    "score": 87.5,
    "grade": "Good",
    "dimensions": {
      "completeness": {"score": 92.1, "weight": 25},
      "uniqueness": {"score": 95.0, "weight": 10},
      "consistency": {"score": 78.5, "weight": 20},
      "validity": {"score": 89.2, "weight": 20},
      "timeliness": {"score": 85.0, "weight": 25}
    }
  },
  "column_analysis": {
    "event_id": {
      "data_type": "INTEGER",
      "is_critical": true,
      "overall_column_score": 95.2,
      "completeness": {"score": 98.5, "null_count": 23},
      "uniqueness": {"score": 100.0, "duplicate_count": 0},
      "issues": ["1.5% missing values"],
      "recommendations": ["Address 23 missing event_id values"]
    }
  },
  "summary": {
    "critical_fields": {
      "total": 6,
      "healthy": 4,
      "warning": 2,
      "critical": 0,
      "avg_score": 89.3
    },
    "top_issues": [
      {
        "severity": "high",
        "column": "reported_date",
        "issue": "15% missing values",
        "impact": "Critical field reported_date missing values affects data reliability"
      }
    ],
    "recommendations": {
      "immediate": ["Fix 15% missing values in reported_date"],
      "short_term": ["Address format violations in event_id"],
      "long_term": ["Implement data validation rules at ingestion"]
    }
  }
}
```

### Database Schema Models

#### EI Tech Model (54 columns)
Key fields include:
- **Core ID:** event_id, reporter_name, reported_date
- **Location:** branch, region, unsafe_event_location
- **Event Details:** unsafe_event_type, date_of_unsafe_event
- **Personnel:** employee_id, employee_name, subcontractor details
- **Safety:** serious_near_miss, unsafe_act, unsafe_condition
- **Actions:** work_stopped, stop_work_duration

#### SRS Model (47 columns)
Key fields include:
- **Core ID:** event_id, reporter_name, reported_date
- **Location:** branch, region, country_name, division
- **Event Details:** unsafe_event_type, business_details
- **Personnel:** employee_id, subcontractor details
- **Safety:** serious_near_miss, unsafe_act, unsafe_condition
- **Actions:** Multiple action_description fields

#### NI TCT Model (43 columns)
Key fields include:
- **Core ID:** reporting_id, reporter_name, created_on
- **Location:** branch_name, region, location
- **Event Details:** type_of_unsafe_event, unsafe_event_details
- **Personnel:** reporter_sap_id, designation, gl_id, pe_id
- **Safety:** action_related_to_high_risk_situation
- **Work Details:** work_was_stopped, no_go_violation

#### NI TCT Augmented Model (58 columns)
Includes all NI TCT columns plus 15 additional fields:
- **Weather Data (4):** condition, temperature, humidity, severity score
- **Employee Data (6):** age, experience, training hours, shift type
- **Site Risk Data (2):** risk category, last safety audit
- **Workload Data (3):** workload category, team size, work duration

## Quality Scoring Algorithm

### Individual Dimension Scoring

#### Completeness Score
Calculated as percentage of non-null values: (non_null_count / total_records) × 100

#### Uniqueness Score
Calculated as percentage of unique values: (unique_count / non_null_count) × 100

#### Consistency Score
Based on pattern compliance: ((total_checked - violations) / total_checked) × 100

#### Validity Score
Based on business rule compliance: ((total_checked - invalid_count) / total_checked) × 100

#### Timeliness Score
Based on data freshness with predefined thresholds:
- ≤30 days: 100 points
- 31-60 days: 85 points
- 61-90 days: 70 points
- 91-180 days: 50 points
- >180 days: 25 points

### Overall Score Calculation

#### Column-Level Score
Weighted average of available dimension scores using predefined weights

#### Overall Health Score
Weighted average across all column scores

### Health Grade Assignment
Descriptive grades based on overall score:
- **Excellent** (85-100): Outstanding data quality with minimal issues
- **Good** (70-84): Acceptable data quality with minor issues
- **Poor** (50-69): Below average data quality requiring attention
- **Bad** (<50): Critical data quality issues requiring immediate action
