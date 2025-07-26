# LLM Data Health - Quick Reference Guide

## 🚀 Quick Start

### Basic Usage
```bash
# LLM-Enhanced Assessment (Recommended)
GET /api/v1/data-health-llm/ei_tech

# Traditional Assessment (Legacy)
GET /api/v1/data-health/ei_tech
```

### Supported Schemas
- `ei_tech` - EI Tech App unsafe events
- `srs` - SRS (Safety Reporting System) events  
- `ni_tct` - NI TCT App unsafe events
- `ni_tct_augmented` - Enhanced NI TCT events

## 🧠 How LLM Intelligence Works

### Automatic Dimension Selection

| Column Description | LLM Decision | Reasoning |
|-------------------|--------------|-----------|
| "Unique identifier for each event record" | ✅ Completeness, Uniqueness, Validity | Must be unique and complete |
| "City where subcontractor is located, if applicable" | ✅ Validity only | Optional field - nulls OK |
| "Branch location where the unsafe event occurred" | ✅ Completeness, Consistency, Validity | Must match known branches |
| "Date when the event was reported" | ✅ Completeness, Consistency, Validity, Timeliness | Date validation + business logic |

### Smart Optimizations

```
Traditional: 50 columns × 5 dimensions = 250 checks
LLM-Enhanced: 50 columns × ~2.8 avg = 140 checks (44% faster)
```

## ⚡ Performance Improvements

| Columns | Traditional | LLM-Enhanced | Improvement |
|---------|-------------|--------------|-------------|
| 20      | ~60s        | ~15s         | **75% faster** |
| 50      | ~150s       | ~35s         | **77% faster** |
| 100     | ~300s       | ~70s         | **77% faster** |

## 📊 Response Structure

### Key Response Fields

```json
{
  "overall_health": {
    "score": 87.5,                    // Overall quality score
    "grade": "Good",                  // A+, A, B+, B, C+, C, D, F
    "dimensions": {...}               // Individual dimension scores
  },
  
  "column_analysis": {
    "event_id": {
      "dimensions_checked": [...],    // Which dimensions LLM selected
      "dimensions_skipped": [...],    // Which dimensions LLM skipped
      "llm_reasoning": {...},         // Why LLM made these decisions
      "priority": "critical",         // LLM-assigned priority
      "overall_column_score": 91.2,  // Column-specific score
      "issues": [...],                // Specific problems found
      "recommendations": [...]        // Actionable advice
    }
  },
  
  "performance_metrics": {
    "llm_selection_time_seconds": 24.89,     // Time for LLM analysis
    "column_assessment_time_seconds": 14.78, // Time for data assessment
    "total_processing_time_seconds": 42.15,  // Total time
    "optimization_percentage": 42.9          // % of checks saved by LLM
  }
}
```

## 🔧 Configuration Options

### Default (Recommended)
```python
DataHealthService(
    max_concurrent_llm_requests=10,    # LLM API calls in parallel
    max_concurrent_db_operations=5     # Database operations in parallel
)
```

### High Performance
```python
DataHealthService(
    max_concurrent_llm_requests=20,    # More LLM calls (if API allows)
    max_concurrent_db_operations=10    # More DB operations (if server allows)
)
```

### Conservative (Limited Resources)
```python
DataHealthService(
    max_concurrent_llm_requests=5,     # Fewer LLM calls
    max_concurrent_db_operations=3     # Fewer DB operations
)
```

## 🎯 Data Quality Dimensions

| Dimension | Weight | What It Checks | LLM Intelligence |
|-----------|--------|----------------|------------------|
| **Completeness** | 25% | Missing/null values | Understands when nulls are OK |
| **Uniqueness** | 10% | Duplicate values | Only checks when required |
| **Consistency** | 20% | Pattern compliance | Applies appropriate rules |
| **Validity** | 20% | Business rules | Validates against constraints |
| **Timeliness** | 25% | Data freshness | Only for time-sensitive fields |

## 🔍 LLM Decision Examples

### Critical Fields
```
"Unique identifier for each event record"
→ Priority: CRITICAL
→ Check: [Completeness, Uniqueness, Validity]
→ Skip: [Consistency, Timeliness]
→ Reason: "IDs must be unique and complete"
```

### Optional Fields
```
"City where subcontractor is located, if applicable"
→ Priority: LOW
→ Check: [Validity]
→ Skip: [Completeness, Uniqueness, Consistency, Timeliness]
→ Reason: "'if applicable' means nulls are expected"
```

### Controlled Vocabularies
```
"Branch location where the unsafe event occurred"
→ Priority: HIGH
→ Check: [Completeness, Consistency, Validity]
→ Skip: [Uniqueness, Timeliness]
→ Reason: "Must match known branch list"
```

### Date Fields
```
"Date when the event was reported"
→ Priority: HIGH
→ Check: [Completeness, Consistency, Validity, Timeliness]
→ Skip: [Uniqueness]
→ Reason: "Date validation + reporting timeliness rules"
```

## 🚨 Common Issues & Solutions

### Slow Performance
```
Problem: Assessment takes > 2 minutes
Solution: Increase max_concurrent_llm_requests (if API allows)
```

### LLM Rate Limits
```
Problem: "Rate limit exceeded" errors
Solution: Reduce max_concurrent_llm_requests to 5-8
```

### Database Errors
```
Problem: "Connection pool exhausted"
Solution: Reduce max_concurrent_db_operations to 3
```

### Memory Issues
```
Problem: Out of memory with large datasets
Solution: Process smaller batches or increase server memory
```

## 📈 Monitoring & Metrics

### Key Metrics to Track
- **Processing Time**: Should be < 1 minute for 50 columns
- **Optimization %**: Should be 30-50% (checks saved by LLM)
- **Error Rate**: Should be < 5%
- **LLM API Usage**: Monitor costs and rate limits

### Performance Benchmarks
```
Good Performance:
- LLM Selection: < 30s for 50 columns
- Column Assessment: < 20s for 50 columns
- Total Time: < 60s for 50 columns
- Optimization: > 30% checks saved
```

## 🛠️ Environment Setup

### Required Environment Variables
```bash
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### Optional Performance Tuning
```bash
MAX_CONCURRENT_LLM_REQUESTS=10
MAX_CONCURRENT_DB_OPERATIONS=5
```

## 🔄 Migration from Traditional Assessment

### API Changes
```bash
# Old way (still works)
GET /api/v1/data-health/ei_tech

# New way (recommended)
GET /api/v1/data-health-llm/ei_tech
```

### Response Differences
- ✅ Same overall structure
- ✅ Same dimension scores
- ➕ Added LLM reasoning
- ➕ Added optimization metrics
- ➕ Added priority levels
- ➕ Enhanced recommendations

### Benefits of Migration
- **75-80% faster** processing
- **Smarter validation** rules
- **Business-aware** recommendations
- **Reduced false positives**
- **Better resource utilization**

## 📚 Additional Resources

- **Full Documentation**: `docs/LLM_DATA_HEALTH_DOCUMENTATION.md`
- **Parallel Processing Guide**: `docs/PARALLEL_PROCESSING_GUIDE.md`
- **API Documentation**: Available at `/docs` endpoint
- **Performance Tuning**: See configuration examples above

---

*Quick Reference v1.0 - July 2025*
