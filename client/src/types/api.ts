// API Types and Interfaces

export interface ApiResponse<T = any> {
  status_code: number;
  message: string;
  body: T;
}

export interface ErrorResponse {
  detail: string | { message: string };
}

// Authentication Types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user_id: string;
  role: string;
  region?: string;
}

export interface UserInfo {
  user_id: string;
  role: 'safety_head' | 'cxo' | 'safety_manager';
  region?: string;
}

// Data Ingestion Types
export interface S3FileIngestRequest {
  s3_key: string;
  filename: string;
  bucket_name?: string;
}

export interface DataIngestResponse {
  ingestion_id: string;
  schema_type: string;
  total_rows: number;
  processed_rows: number;
  failed_rows: number;
  operation_details: string;
}

// Chat Types
export interface ChatRequest {
  question: string;
}

export interface ChatResponse {
  status_code: number;
  message: string;
  body: {
    final_answer: string;
    visualization_data: any;
  };
}

// AI Insights Types
export interface AIInsight {
  id: string;
  text: string;
  category?: string;
  confidence?: number;
  timestamp?: string;
  liked?: boolean;
  disliked?: boolean;
}

export interface AIInsightsResponse {
  status_code?: number;
  message?: string;
  schema_type: string;
  user_id: string;
  user_role: string;
  insights_count: number;
  insights: string[]; // Backend returns array of strings
  personalization_level: string;
  generated_at: string;
  // Optional nested structure for compatibility
  body?: {
    schema_type: string;
    user_id: string;
    user_role: string;
    insights_count: number;
    insights: string[];
    personalization_level: string;
    generated_at: string;
  };
}

export interface InsightFeedback {
  schema_type: string;
  insight_text: string;
  feedback: 'like' | 'dislike';
}

// Dashboard Types - Updated to match backend response structure
export interface DashboardKPIs {
  total_events: {
    count: {
      total_events: number;
      unique_events: number;
    };
    description: string;
  };
  serious_near_miss_rate: {
    rate: number;
    count: {
      serious_near_miss_count: number;
      non_serious_count: number;
      total_events: number;
      serious_near_miss_percentage: string;
    };
    description: string;
  };
  work_stoppage_rate: {
    rate: number;
    count: number;
    total: {
      total_events: number;
      unique_events: number;
    };
    description: string;
  };
  // Monthly trends data
  monthly_trends: Array<{
    month: string;
    event_count: number;
    serious_count: number;
    work_stopped_count: number;
  }>;
  // Branch performance analysis with complete metrics
  branch_performance_analysis: Array<{
    branch: string;
    region: string;
    total_incidents: number;
    serious_incidents: number;
    work_stoppages: number;
    unique_locations: number;
    unique_event_types: number;
    serious_incident_rate: number;
    work_stoppage_rate: number;
    percentage_of_total_incidents: number;
    performance_score: number;
  }>;
  // Event type distribution
  event_type_distribution: Array<{
    event_type: string;
    event_count: number;
    percentage: number;
  }>;
  // Repeat locations analysis
  repeat_locations: Array<{
    location: string;
    region: string;
    incident_count: number;
    work_stopped_incidents: number;
    serious_incidents: number;
    work_stopped_rate: number;
    percentage_of_total: number;
  }>;
  // Response time analysis
  response_time_analysis: {
    average_response_time: string;
    median_response_time: string;
    events_analyzed: number;
    description: string;
  };
  // Safety performance trends (quarterly)
  safety_performance_trends: Array<{
    year: number;
    quarter: number;
    period: string;
    total_incidents: number;
    serious_incidents: number;
    work_stoppages: number;
    branches_affected: number;
    locations_affected: number;
    serious_incident_rate: number;
    work_stoppage_rate: number;
    previous_quarter_incidents: number | null;
    quarter_over_quarter_change: number | null;
  }>;
  // Incident severity distribution
  incident_severity_distribution: Array<{
    severity_level: string;
    incident_count: number;
    percentage: number;
    sort_order: number;
  }>;
  // Operational impact analysis
  operational_impact_analysis: {
    summary: {
      total_incidents: number;
      branches_impacted: number;
      locations_impacted: number;
      incident_types: number;
    };
    impact_metrics: {
      operational_disruption_rate: number;
      safety_risk_rate: number;
      overall_impact_score: number;
    };
    incident_breakdown: {
      work_stopped_incidents: number;
      serious_incidents: number;
    };
    description: string;
  };
  // Time-based analysis (hour of day, day of week)
  time_based_analysis?: {
    hourly_distribution: Array<{
      hour: number;
      incident_count: number;
      percentage: number;
    }>;
    daily_distribution: Array<{
      day_of_week: number;
      day_name: string;
      incident_count: number;
      percentage: number;
    }>;
    description: string;
  };
  // Augmented KPIs for ni_tct_augmented schema
  augmented_kpis?: {
    weather_impact_analysis: Array<{
      weather_condition: string;
      incident_count: number;
      percentage: number;
      severity_score: number;
    }>;
    experience_level_analysis: {
      experience_groups: Array<{
        experience_level: string;
        incident_count: number;
        percentage: number;
        avg_severity: number;
      }>;
      correlation_score: number;
    };
    site_risk_analysis: {
      risk_categories: Array<{
        risk_level: string;
        site_count: number;
        incident_count: number;
        incidents_per_site: number;
      }>;
      high_risk_sites: Array<{
        site_name: string;
        risk_score: number;
        incident_count: number;
      }>;
    };
    workload_impact_analysis: {
      workload_correlation: number;
      peak_hours: Array<{
        hour: number;
        incident_rate: number;
        workload_factor: number;
      }>;
    };
    weather_severity_correlation: {
      correlation_coefficient: number;
      weather_patterns: Array<{
        pattern: string;
        severity_impact: number;
        frequency: number;
      }>;
    };
    training_effectiveness: {
      effectiveness_score: number;
      training_impact: Array<{
        training_type: string;
        incident_reduction: number;
        effectiveness_rating: string;
      }>;
    };
  };
}

export interface DashboardResponse {
  schema_type: string;
  date_range: {
    start_date: string;
    end_date: string;
  };
  generated_at: string;
  user_context: {
    user_role: string;
    region?: string;
    data_scope: string;
  };
  dashboard_data: DashboardKPIs;
}

// Data Health Types
export interface DimensionScore {
  score: number;
  weight: number;
  columns_assessed: number;
}

export interface OverallHealth {
  score: number;
  grade: string;
  dimensions: {
    completeness: DimensionScore;
    uniqueness: DimensionScore;
    validity: DimensionScore;
    consistency: DimensionScore;
    timeliness: DimensionScore;
  };
}

export interface ColumnAnalysisItem {
  dimensions_checked: string[];
  dimensions_skipped: string[];
  llm_reasoning: Record<string, string>;
  priority: string;
  completeness?: {
    score: number;
    null_count: number;
    non_null_count: number;
    null_percentage: number;
  };
  uniqueness?: {
    score: number;
    unique_count: number;
    duplicate_count: number;
    total_non_null: number;
  };
  consistency?: {
    score: number;
    pattern_violations: number;
    total_checked: number;
    violation_percentage: number;
  };
  validity?: {
    score: number;
    invalid_count: number;
    total_checked: number;
    invalid_percentage: number;
  };
  timeliness?: {
    score: number;
    days_since_latest?: number;
    avg_age_days?: number;
    latest_date?: string;
    oldest_date?: string;
  };
  overall_column_score: number;
  issues: string[];
  recommendations: string[];
}

export interface CriticalFields {
  total: number;
  healthy: number;
  warning: number;
  critical: number;
  avg_score: number;
}

export interface TopIssue {
  severity: string;
  column: string;
  issue: string;
  impact: string;
}

export interface LLMInsights {
  dimension_optimization: {
    total_possible_checks: number;
    total_actual_checks: number;
    checks_skipped: number;
    optimization_percentage: number;
  };
  intelligent_skips: {
    skip_counts: Record<string, number>;
    skip_reasons: Record<string, string[]>;
  };
  priority_distribution: {
    critical: number;
    high: number;
    medium: number;
  };
}

export interface HealthReportSummary {
  critical_fields: CriticalFields;
  top_issues: TopIssue[];
  recommendations: {
    immediate: string[];
    short_term: string[];
    long_term: string[];
    llm_recommendations: string[];
  };
  llm_insights: LLMInsights;
}

export interface HealthReport {
  schema_type: string;
  total_records: number;
  assessment_timestamp: string;
  assessment_type: string;
  overall_health: OverallHealth;
  column_analysis: Record<string, ColumnAnalysisItem>;
  summary: HealthReportSummary;
  llm_insights?: {
    total_columns_analyzed: number;
    dimension_selections_made: number;
  };
  performance_metrics?: {
    llm_selection_time_seconds: number;
    column_assessment_time_seconds: number;
    total_processing_time_seconds: number;
    parallel_processing_enabled: boolean;
    max_concurrent_llm_requests: number;
    max_concurrent_db_operations: number;
  };
}

export interface AssessmentSummary {
  schema_type: string;
  assessment_type: string;
  total_records: number;
  overall_score: number;
  health_grade: string;
  columns_analyzed: number;
  dimension_selections: number;
  assessment_timestamp: string;
}

export interface LLMOptimization {
  optimization_applied: boolean;
  intelligent_dimension_selection: boolean;
  semantic_context_used: boolean;
}

export interface DataHealthResponse {
  status_code: number;
  message: string;
  body: {
    health_report: HealthReport;
    assessment_summary: AssessmentSummary;
    llm_optimization: LLMOptimization;
  };
}

// Schema Types
export type SchemaType = 'ei_tech' | 'srs' | 'ni_tct' | 'ni_tct_augmented';

// File Upload Types
export interface FileUploadResponse {
  url: string;
  fields: Record<string, string>;
  s3_key: string;
}
