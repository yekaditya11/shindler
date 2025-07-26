# LLM-Enhanced Data Health Assessment System

## Overview

The LLM-Enhanced Data Health Assessment System is an intelligent data quality evaluation framework that uses Large Language Models (LLMs) to understand the semantic meaning of data columns and automatically determine which quality dimensions are relevant for assessment.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [How It Works](#how-it-works)
3. [API Endpoints](#api-endpoints)
4. [LLM Intelligence Features](#llm-intelligence-features)
5. [Performance & Parallel Processing](#performance--parallel-processing)
6. [Configuration Options](#configuration-options)
7. [Response Format](#response-format)
8. [Examples](#examples)
9. [Troubleshooting](#troubleshooting)

## System Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    LLM Data Health System                   │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────┐ │
│  │ Semantic Config │  │ LLM Dimension    │  │ Data Health │ │
│  │ Service         │  │ Selector         │  │ Service     │ │
│  │                 │  │                  │  │             │ │
│  │ • Load semantics│  │ • Analyze desc.  │  │ • Parallel  │ │
│  │ • Parse columns │  │ • Select dims    │  │   processing│ │
│  │ • Cache data    │  │ • Generate rules │  │ • Assessment│ │
│  └─────────────────┘  └──────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. Load Semantics → 2. LLM Analysis → 3. Parallel Assessment → 4. Enhanced Report
   
   semantics.json    Column descriptions    Multiple columns      Intelligent
   ↓                 ↓                      processed in          recommendations
   Column metadata   Dimension selection    parallel              with context
```

## How It Works

### Step 1: Semantic Configuration Loading

The system loads column metadata from `semantics/shinlder_semantics.json`:

```json
{
  "unsafe_events_ei_tech": {
    "event_id": {
      "description": "Unique identifier for each event record",
      "data_type": "integer",
      "min": "8513",
      "max": "17669"
    },
    "branch": {
      "description": "Branch location where the unsafe event occurred",
      "unique_values": ["North Delhi", "Thane & KDMC", "Mumbai 1"],
      "unique_count": 27
    }
  }
}
```

### Step 2: LLM Dimension Selection

For each column, the LLM analyzes the description and determines which quality dimensions to check:

**Example Analysis:**

| Column | Description | LLM Decision | Reasoning |
|--------|-------------|--------------|-----------|
| `event_id` | "Unique identifier for each event record" | Check: [completeness, uniqueness, validity] | Must be unique and complete |
| `subcontractor_city` | "City where subcontractor is located, if applicable" | Check: [validity] only | Optional field - nulls acceptable |
| `branch` | "Branch location where the unsafe event occurred" | Check: [completeness, consistency, validity] | Must match known branch list |

### Step 3: Parallel Assessment

The system processes multiple columns simultaneously:

```
Column 1: [Completeness ✓] [Uniqueness ✓] [Validity ✓]     } Parallel
Column 2: [Validity ✓]                                     } Processing  
Column 3: [Completeness ✓] [Consistency ✓] [Validity ✓]   } 
```

### Step 4: Intelligent Reporting

Results include LLM context and business-aware recommendations.

## API Endpoints

### Primary Endpoint

```http
GET /api/v1/data-health-llm/{schema_type}
```

**Supported Schema Types:**
- `ei_tech` - EI Tech App unsafe events
- `srs` - SRS (Safety Reporting System) events  
- `ni_tct` - NI TCT App unsafe events
- `ni_tct_augmented` - Enhanced NI TCT events

### Legacy Endpoint (Still Available)

```http
GET /api/v1/data-health/{schema_type}
```

*Note: This endpoint uses traditional assessment without LLM intelligence.*

## LLM Intelligence Features

### 1. Semantic Understanding

The LLM understands column meanings from natural language descriptions:

```python
# LLM Analysis Examples:

"Unique identifier for each event record"
→ LLM Decision: MUST check uniqueness (100% unique required)

"City where subcontractor is located, if applicable"  
→ LLM Decision: SKIP completeness check (nulls are acceptable)

"Branch location where the unsafe event occurred"
→ LLM Decision: CHECK against known branch list (controlled vocabulary)

"Date when the event was reported"
→ LLM Decision: CHECK date format + business logic (reporting timeliness)
```

### 2. Business Context Awareness

The LLM considers the safety incident management domain:

- **Critical Fields**: Event IDs, dates, safety classifications
- **Optional Fields**: Subcontractor details, additional comments
- **Controlled Vocabularies**: Branch names, event types, safety categories
- **Temporal Logic**: Reported date ≥ Event date

### 3. Intelligent Optimization

The LLM skips irrelevant validations:

```
Traditional Approach: 50 columns × 5 dimensions = 250 checks
LLM Approach: 50 columns × ~2.8 avg dimensions = 140 checks (44% reduction)
```

### 4. Context-Aware Recommendations

```json
{
  "recommendations": [
    "CRITICAL: completeness issue in event_id - Unique identifiers cannot be missing",
    "LLM intelligently skipped uniqueness for site_reference - repetition expected",
    "Branch values must match organizational structure - found 8 invalid entries"
  ]
}
```

## Performance & Parallel Processing

### Performance Improvements

| Columns | Traditional (Sequential) | LLM-Enhanced (Parallel) | Improvement |
|---------|-------------------------|-------------------------|-------------|
| 20      | ~60 seconds            | ~15 seconds             | **75% faster** |
| 50      | ~150 seconds           | ~35 seconds             | **77% faster** |
| 100     | ~300 seconds           | ~70 seconds             | **77% faster** |

### Parallel Processing Architecture

```
┌─────────────────────────────────────────────────────────┐
│                LLM Dimension Selection                  │
│  Column 1 → LLM → Rules                                │
│  Column 2 → LLM → Rules    } Parallel (max 10 concurrent) │
│  Column 3 → LLM → Rules                                │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                Column Assessment                        │
│  Column 1 → [Comp][Uniq][Valid] → Results             │
│  Column 2 → [Valid] → Results      } Parallel          │
│  Column 3 → [Comp][Cons][Valid] → Results             │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│            Dimension Checks (per column)               │
│  ├── Completeness (Thread 1)                          │
│  ├── Uniqueness (Thread 2)    } Parallel (max 5)     │
│  ├── Consistency (Thread 3)                           │
│  ├── Validity (Thread 4)                              │
│  └── Timeliness (Thread 5)                            │
└─────────────────────────────────────────────────────────┘
```

## Configuration Options

### Default Configuration

```python
DataHealthService(
    max_concurrent_llm_requests=10,    # LLM API calls in parallel
    max_concurrent_db_operations=5     # Database operations in parallel
)
```

### High-Performance Configuration

```python
DataHealthService(
    max_concurrent_llm_requests=20,    # More LLM calls (if API allows)
    max_concurrent_db_operations=10    # More DB operations (if server allows)
)
```

### Conservative Configuration

```python
DataHealthService(
    max_concurrent_llm_requests=5,     # Fewer LLM calls (for rate limits)
    max_concurrent_db_operations=3     # Fewer DB operations (for limited resources)
)
```

## Response Format

### Enhanced Response Structure

```json
{
  "status_code": 200,
  "message": "LLM-enhanced data health assessment completed for ei_tech",
  "body": {
    "health_report": {
      "schema_type": "ei_tech",
      "total_records": 15420,
      "assessment_timestamp": "2025-07-24T19:45:30.123456",
      "assessment_type": "llm_enhanced",
      
      "overall_health": {
        "score": 87.5,
        "grade": "Good",
        "dimensions": {
          "completeness": {"score": 92.1, "weight": 25, "columns_assessed": 35},
          "uniqueness": {"score": 85.0, "weight": 10, "columns_assessed": 12},
          "consistency": {"score": 91.2, "weight": 20, "columns_assessed": 28},
          "validity": {"score": 89.8, "weight": 20, "columns_assessed": 42},
          "timeliness": {"score": 88.0, "weight": 25, "columns_assessed": 8}
        }
      },
      
      "column_analysis": {
        "event_id": {
          "dimensions_checked": ["completeness", "uniqueness", "validity"],
          "dimensions_skipped": ["consistency", "timeliness"],
          "llm_reasoning": {
            "completeness": "Critical - unique IDs cannot be missing",
            "uniqueness": "Critical - must be 100% unique",
            "validity": "Important - check ID format and range",
            "consistency": "Skip - IDs don't need pattern consistency",
            "timeliness": "Skip - IDs are not time-based"
          },
          "priority": "critical",
          "completeness": {"score": 98.5, "null_count": 231, "null_percentage": 1.5},
          "uniqueness": {"score": 85.0, "duplicate_count": 187, "unique_percentage": 85.0},
          "validity": {"score": 95.0, "invalid_count": 23, "invalid_percentage": 0.15},
          "overall_column_score": 91.2,
          "issues": [
            "187 duplicate values violate unique identifier business rule",
            "23 values outside expected range 8513-17669"
          ],
          "recommendations": [
            "CRITICAL: Remove 187 duplicate event IDs - violates uniqueness requirement",
            "Validate event ID generation process to ensure proper range compliance"
          ]
        }
      },
      
      "summary": {
        "total_issues": 156,
        "critical_issues": 23,
        "recommendations": {
          "immediate": ["Fix critical event ID duplicates", "Validate branch names"],
          "short_term": ["Improve date validation", "Standardize naming conventions"],
          "long_term": ["Implement automated data validation", "Enhanced monitoring"]
        },
        "llm_insights": {
          "dimension_optimization": {
            "total_possible_checks": 245,
            "total_actual_checks": 140,
            "optimization_percentage": 42.9
          },
          "intelligent_skips": {
            "skip_counts": {
              "consistency": 15,
              "timeliness": 35,
              "uniqueness": 8
            }
          },
          "priority_distribution": {
            "critical": 8,
            "high": 12,
            "medium": 25,
            "low": 4
          }
        }
      },
      
      "performance_metrics": {
        "llm_selection_time_seconds": 24.89,
        "column_assessment_time_seconds": 14.78,
        "total_processing_time_seconds": 42.15,
        "parallel_processing_enabled": true,
        "max_concurrent_llm_requests": 10,
        "max_concurrent_db_operations": 5
      }
    }
  }
}
```

## Examples

### Example 1: Basic Usage

```bash
# Request
curl -X GET "http://localhost:8000/api/v1/data-health-llm/ei_tech" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Response Summary
{
  "overall_health": {"score": 87.5, "grade": "Good"},
  "performance_metrics": {
    "total_processing_time_seconds": 42.15,
    "optimization_percentage": 42.9
  }
}
```

### Example 2: Column-Specific Analysis

```json
{
  "event_id": {
    "dimensions_checked": ["completeness", "uniqueness", "validity"],
    "llm_reasoning": {
      "uniqueness": "Critical - must be 100% unique identifier"
    },
    "issues": ["187 duplicate values found"],
    "recommendations": ["Remove duplicate event IDs immediately"]
  },

  "subcontractor_city": {
    "dimensions_checked": ["validity"],
    "dimensions_skipped": ["completeness", "uniqueness", "consistency", "timeliness"],
    "llm_reasoning": {
      "completeness": "Skip - 'if applicable' means nulls are expected"
    },
    "recommendations": ["LLM intelligently skipped most checks - optional field"]
  }
}
```

### Example 3: Performance Comparison

```json
{
  "performance_metrics": {
    "llm_selection_time_seconds": 24.89,    // LLM analysis time
    "column_assessment_time_seconds": 14.78, // Parallel assessment time
    "total_processing_time_seconds": 42.15,  // Total time
    "optimization_percentage": 42.9          // Checks saved by LLM
  }
}
```

## LLM Prompt Engineering

### Column Analysis Prompt Template

The system uses sophisticated prompts to analyze columns:

```
Analyze this column from a safety incident reporting system:

COLUMN INFORMATION:
- Column Name: event_id
- Description: "Unique identifier for each event record"
- Data Type: integer
- Sample Values: [8513, 8514, 8515, ...]
- Value Range: 8513 to 17669

ANALYSIS INSTRUCTIONS:
- If description contains "unique identifier" → Check COMPLETENESS, UNIQUENESS, VALIDITY
- If description contains "if applicable" → Skip COMPLETENESS
- If description contains "date when" → Check TIMELINESS
- If field has limited unique_values → Check VALIDITY against allowed list

RESPONSE FORMAT:
{
  "dimensions_to_check": ["completeness", "uniqueness", "validity"],
  "dimensions_to_skip": ["consistency", "timeliness"],
  "reasoning": {
    "completeness": "Critical - unique IDs cannot be missing",
    "uniqueness": "Critical - must be 100% unique"
  },
  "priority": "critical"
}
```

## Data Quality Dimensions

### 1. Completeness (Weight: 25%)
- **What**: Percentage of non-null values
- **LLM Intelligence**: Understands when nulls are acceptable
- **Example**: "if applicable" fields allow nulls without penalty

### 2. Uniqueness (Weight: 10%)
- **What**: Percentage of unique values
- **LLM Intelligence**: Only checks when semantically required
- **Example**: Skips uniqueness for site names (repetition expected)

### 3. Consistency (Weight: 20%)
- **What**: Pattern and format compliance
- **LLM Intelligence**: Applies appropriate pattern rules
- **Example**: Date formats, naming conventions, controlled vocabularies

### 4. Validity (Weight: 20%)
- **What**: Business rule compliance
- **LLM Intelligence**: Validates against semantic constraints
- **Example**: Branch names must match organizational list

### 5. Timeliness (Weight: 25%)
- **What**: Data freshness and temporal logic
- **LLM Intelligence**: Only applies to time-sensitive fields
- **Example**: Reporting delays, date relationships

## Business Rules & Semantic Understanding

### Critical Field Identification

```python
# LLM automatically identifies critical fields:
"Unique identifier" → Critical priority
"Date when event occurred" → High priority
"Additional comments, if any" → Low priority
"City where subcontractor is located, if applicable" → Low priority
```

### Controlled Vocabulary Detection

```python
# LLM detects controlled vocabularies:
"Type of unsafe event: condition, act, or near miss" → Exact list validation
"Branch location where event occurred" → Known branch list validation
"Indicates whether work was stopped" → Boolean validation
```

### Temporal Logic Understanding

```python
# LLM understands date relationships:
"Date when event was reported" + "Date when event occurred"
→ Business rule: reported_date >= event_date
```

## Error Handling & Reliability

### Fallback Mechanisms

1. **LLM API Failure**: Falls back to default dimension selection
2. **Parallel Processing Error**: Falls back to sequential processing
3. **Individual Column Error**: Continues with other columns
4. **Timeout Protection**: 30-second timeout per dimension check

### Error Response Format

```json
{
  "column_name": {
    "error": "Assessment failed: Connection timeout",
    "dimensions_checked": [],
    "overall_column_score": 0,
    "fallback_applied": true
  }
}
```

## Configuration & Tuning

### Environment Variables

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Performance Tuning
MAX_CONCURRENT_LLM_REQUESTS=10
MAX_CONCURRENT_DB_OPERATIONS=5
```

### Performance Tuning Guidelines

| Scenario | LLM Concurrency | DB Concurrency | Expected Performance |
|----------|-----------------|-----------------|---------------------|
| Development | 5 | 3 | Moderate, safe |
| Production (Standard) | 10 | 5 | Good balance |
| Production (High-Load) | 15 | 8 | Maximum performance |
| Limited Resources | 3 | 2 | Conservative, stable |

## Troubleshooting

### Common Issues

#### 1. Slow Performance
```
Symptoms: Assessment takes > 2 minutes
Solutions:
- Increase max_concurrent_llm_requests (if API allows)
- Increase max_concurrent_db_operations (if DB allows)
- Check network latency to Azure OpenAI
```

#### 2. LLM API Rate Limits
```
Symptoms: "Rate limit exceeded" errors
Solutions:
- Reduce max_concurrent_llm_requests
- Implement exponential backoff
- Upgrade Azure OpenAI tier
```

#### 3. Database Connection Issues
```
Symptoms: "Connection pool exhausted" errors
Solutions:
- Reduce max_concurrent_db_operations
- Increase database connection pool size
- Monitor database CPU/memory usage
```

#### 4. Memory Issues
```
Symptoms: Out of memory errors with large datasets
Solutions:
- Process smaller batches
- Increase server memory
- Optimize database queries
```

### Debug Mode

Enable detailed logging:

```python
import logging
logging.getLogger('src.services.llm_dimension_selector').setLevel(logging.DEBUG)
logging.getLogger('src.services.data_health_service').setLevel(logging.DEBUG)
```

## Best Practices

### 1. Monitoring
- Monitor LLM API usage and costs
- Track performance metrics over time
- Set up alerts for failures

### 2. Semantic Configuration Management
- Keep semantics.json updated with new columns
- Version control semantic configurations
- Test changes in development first

### 3. Performance Optimization
- Start with default settings
- Gradually increase concurrency based on monitoring
- Balance speed vs resource usage

### 4. Error Handling
- Implement retry logic for transient failures
- Monitor error rates and patterns
- Have fallback strategies for critical assessments

## Future Enhancements

### Planned Features
1. **Adaptive Learning**: LLM learns from user feedback
2. **Custom Business Rules**: User-defined validation rules
3. **Real-time Monitoring**: Continuous data quality monitoring
4. **Advanced Analytics**: Trend analysis and predictions
5. **Multi-language Support**: Support for non-English descriptions

### Integration Opportunities
1. **Data Lineage**: Track data quality across pipelines
2. **Alerting Systems**: Automated quality alerts
3. **Dashboard Integration**: Real-time quality dashboards
4. **ML Pipeline Integration**: Quality gates in ML workflows

---

## Support & Contact

For technical support or questions about the LLM-Enhanced Data Health Assessment System:

- **Documentation**: This guide and API documentation
- **Logs**: Check application logs for detailed error information
- **Performance**: Use built-in performance metrics for optimization
- **Configuration**: Refer to configuration examples for tuning

---

*Last Updated: July 2025*
*Version: 1.0.0*
