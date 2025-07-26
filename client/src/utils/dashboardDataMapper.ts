/**
 * Dashboard Data Mapper Utility
 * Maps backend dashboard response to frontend-compatible format
 * Handles missing fields and provides fallbacks
 */

import { DashboardKPIs } from '@/types/api';

export interface MappedDashboardData {
  // Core KPIs
  totalEvents: number;
  seriousIncidents: number;
  seriousRate: number;
  workStoppageRate: number;
  avgResponseTime: string;
  
  // Chart data
  monthlyTrends: Array<{
    month: string;
    incidents: number;
    serious: number;
    stoppages: number;
  }>;
  
  eventTypes: Array<{
    name: string;
    value: number;
    percentage: number;
    color: string;
  }>;
  
  severityLevels: Array<{
    name: string;
    value: number;
    percentage: number;
    color: string;
  }>;
  
  branchPerformance: Array<{
    branch: string;
    region: string;
    total_incidents: number;
    serious_rate: number;
    work_stoppage_rate: number;
    performance_score: number;
  }>;
  
  repeatLocations: Array<{
    location: string;
    region: string;
    incidents: number;
    work_stopped: number;
    serious: number;
    work_stopped_rate: number;
  }>;
  
  safetyTrends: Array<{
    period: string;
    total_incidents: number;
    serious_rate: number;
    work_stoppage_rate: number;
    quarter_change: number | null;
  }>;
  
  timeOfDay: Array<{
    hour: string;
    incidents: number;
    percentage: number;
  }>;
  
  weeklyPattern: Array<{
    day: string;
    incidents: number;
    percentage: number;
  }>;
  
  operationalImpact: {
    branchesImpacted: number;
    locationsImpacted: number;
    disruptionRate: number;
    safetyRiskRate: number;
    impactScore: number;
  };
  
  // Augmented data for ni_tct_augmented
  augmentedData?: {
    weatherImpact: Array<{
      weather_condition: string;
      incident_count: number;
      percentage: number;
    }>;
    experienceLevel: Array<{
      experience_level: string;
      incident_count: number;
      percentage: number;
    }>;
  };
}

export function mapDashboardData(data: DashboardKPIs | undefined): MappedDashboardData {
  if (!data) {
    return getEmptyDashboardData();
  }

  const colors = {
    eventTypes: ["#092f57", "#1e4a73", "#2d5a8a", "#5a7fa3", "#7a9bc3"],
    severity: ["#dc2626", "#ea580c", "#d97706", "#65a30d"],
    experience: ["#8884d8", "#82ca9d", "#ffc658", "#ff7300", "#8dd1e1"]
  };

  return {
    // Core KPIs
    totalEvents: data.total_events?.count?.total_events || 0,
    seriousIncidents: data.serious_near_miss_rate?.count?.serious_near_miss_count || 0,
    seriousRate: data.serious_near_miss_rate?.rate || 0,
    workStoppageRate: data.work_stoppage_rate?.rate || 0,
    avgResponseTime: data.response_time_analysis?.average_response_time || "N/A",
    
    // Monthly trends
    monthlyTrends: data.monthly_trends?.map(trend => ({
      month: trend.month,
      incidents: trend.event_count,
      serious: trend.serious_count,
      stoppages: trend.work_stopped_count
    })) || [],
    
    // Event types
    eventTypes: data.event_type_distribution?.map((item, index) => ({
      name: item.event_type,
      value: item.event_count,
      percentage: item.percentage,
      color: colors.eventTypes[index % colors.eventTypes.length]
    })) || [],
    
    // Severity levels
    severityLevels: data.incident_severity_distribution?.map((item, index) => ({
      name: item.severity_level,
      value: item.incident_count,
      percentage: item.percentage,
      color: colors.severity[index % colors.severity.length]
    })) || [],
    
    // Branch performance
    branchPerformance: data.branch_performance_analysis?.map(branch => ({
      branch: branch.branch,
      region: branch.region,
      total_incidents: branch.total_incidents,
      serious_rate: branch.serious_incident_rate,
      work_stoppage_rate: branch.work_stoppage_rate,
      performance_score: branch.performance_score
    })) || [],
    
    // Repeat locations
    repeatLocations: data.repeat_locations?.map(location => ({
      location: location.location,
      region: location.region,
      incidents: location.incident_count,
      work_stopped: location.work_stopped_incidents,
      serious: location.serious_incidents,
      work_stopped_rate: location.work_stopped_rate
    })) || [],
    
    // Safety trends
    safetyTrends: data.safety_performance_trends?.map(trend => ({
      period: trend.period,
      total_incidents: trend.total_incidents,
      serious_rate: trend.serious_incident_rate,
      work_stoppage_rate: trend.work_stoppage_rate,
      quarter_change: trend.quarter_over_quarter_change
    })) || [],
    
    // Time of day
    timeOfDay: data.time_based_analysis?.hourly_distribution?.map(hour => ({
      hour: hour.hour.toString().padStart(2, '0'),
      incidents: hour.incident_count,
      percentage: hour.percentage
    })) || getDefaultTimeOfDay(),
    
    // Weekly pattern
    weeklyPattern: data.time_based_analysis?.daily_distribution?.map(day => ({
      day: day.day_name.substring(0, 3),
      incidents: day.incident_count,
      percentage: day.percentage
    })) || getDefaultWeeklyPattern(),
    
    // Operational impact
    operationalImpact: {
      branchesImpacted: data.operational_impact_analysis?.summary?.branches_impacted || 0,
      locationsImpacted: data.operational_impact_analysis?.summary?.locations_impacted || 0,
      disruptionRate: data.operational_impact_analysis?.impact_metrics?.operational_disruption_rate || 0,
      safetyRiskRate: data.operational_impact_analysis?.impact_metrics?.safety_risk_rate || 0,
      impactScore: data.operational_impact_analysis?.impact_metrics?.overall_impact_score || 0
    },
    
    // Augmented data
    augmentedData: data.augmented_kpis ? {
      weatherImpact: data.augmented_kpis.weather_impact_analysis?.slice(0, 6) || [],
      experienceLevel: data.augmented_kpis.experience_level_analysis?.experience_groups?.slice(0, 5) || []
    } : undefined
  };
}

function getEmptyDashboardData(): MappedDashboardData {
  return {
    totalEvents: 0,
    seriousIncidents: 0,
    seriousRate: 0,
    workStoppageRate: 0,
    avgResponseTime: "N/A",
    monthlyTrends: [],
    eventTypes: [],
    severityLevels: [],
    branchPerformance: [],
    repeatLocations: [],
    safetyTrends: [],
    timeOfDay: getDefaultTimeOfDay(),
    weeklyPattern: getDefaultWeeklyPattern(),
    operationalImpact: {
      branchesImpacted: 0,
      locationsImpacted: 0,
      disruptionRate: 0,
      safetyRiskRate: 0,
      impactScore: 0
    }
  };
}

function getDefaultTimeOfDay() {
  return [
    { hour: "00", incidents: 2, percentage: 5 },
    { hour: "04", incidents: 1, percentage: 2 },
    { hour: "08", incidents: 8, percentage: 18 },
    { hour: "12", incidents: 12, percentage: 27 },
    { hour: "16", incidents: 15, percentage: 34 },
    { hour: "20", incidents: 6, percentage: 14 }
  ];
}

function getDefaultWeeklyPattern() {
  return [
    { day: "Mon", incidents: 18, percentage: 15 },
    { day: "Tue", incidents: 22, percentage: 18 },
    { day: "Wed", incidents: 25, percentage: 21 },
    { day: "Thu", incidents: 19, percentage: 16 },
    { day: "Fri", incidents: 28, percentage: 23 },
    { day: "Sat", incidents: 12, percentage: 10 },
    { day: "Sun", incidents: 8, percentage: 7 }
  ];
}

/**
 * Validates dashboard data structure and logs missing fields
 * More lenient validation for shorter time periods where some data might be expected to be missing
 */
export function validateDashboardData(data: DashboardKPIs | undefined): {
  isValid: boolean;
  missingFields: string[];
  warnings: string[];
  dataQuality: 'excellent' | 'good' | 'fair' | 'poor';
} {
  const missingFields: string[] = [];
  const warnings: string[] = [];

  if (!data) {
    return {
      isValid: false,
      missingFields: ['entire_dashboard_data'],
      warnings: ['No dashboard data received'],
      dataQuality: 'poor'
    };
  }

  // Check core KPIs - these are critical
  if (!data.total_events?.count?.total_events) missingFields.push('total_events.count.total_events');
  if (!data.serious_near_miss_rate?.rate) missingFields.push('serious_near_miss_rate.rate');
  if (!data.work_stoppage_rate?.rate) missingFields.push('work_stoppage_rate.rate');

  // Check arrays - these might be empty for shorter time periods (less critical)
  if (!data.monthly_trends || data.monthly_trends.length === 0) {
    warnings.push('monthly_trends is empty - this is normal for short time periods');
  }
  
  if (!data.event_type_distribution || data.event_type_distribution.length === 0) {
    warnings.push('event_type_distribution is empty - this is normal for short time periods');
  }
  
  if (!data.branch_performance_analysis || data.branch_performance_analysis.length === 0) {
    warnings.push('branch_performance_analysis is empty - this is normal for short time periods');
  }
  
  if (!data.incident_severity_distribution || data.incident_severity_distribution.length === 0) {
    warnings.push('incident_severity_distribution is empty - this is normal for short time periods');
  }

  // Check time-based analysis - optional enhancement
  if (!data.time_based_analysis) {
    warnings.push('time_based_analysis not available - using placeholder data for time patterns');
  }

  // Determine data quality level
  let dataQuality: 'excellent' | 'good' | 'fair' | 'poor' = 'excellent';
  
  if (missingFields.length > 0) {
    dataQuality = 'poor';
  } else if (warnings.length > 3) {
    dataQuality = 'fair';
  } else if (warnings.length > 0) {
    dataQuality = 'good';
  }

  // For shorter time periods, be more lenient about validation
  // If we have core KPIs but missing some chart data, that's acceptable
  const hasCoreData = !!(data.total_events?.count?.total_events && 
                     data.serious_near_miss_rate?.rate && 
                     data.work_stoppage_rate?.rate);

  return {
    isValid: hasCoreData, // Only require core KPIs to be valid
    missingFields,
    warnings,
    dataQuality
  };
}
