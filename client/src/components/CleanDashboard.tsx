import { useState, useEffect } from "react";
import { Calendar, Activity, AlertTriangle, Zap, Clock, TrendingUp, BarChart3, Building2, Sun, CalendarDays } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { format, parseISO, subDays, startOfDay, endOfDay } from "date-fns";
import { DateRange } from "react-day-picker";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Calendar as CalendarComponent } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { cn } from "@/lib/utils";
import { AIFloatingIcon } from "./AIInsights";
import { ChatBot, ChatBotFloatingIcon } from "./ChatBot";
import { useSendChatMessage } from "@/hooks/useApi";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from "recharts";

import { DashboardKPIs, SchemaType } from "@/types/api";
import { mapDashboardData, validateDashboardData } from "@/utils/dashboardDataMapper";
import { httpClient } from "@/lib/http-client";

interface CleanDashboardProps {
  data?: DashboardKPIs;
  isLoading?: boolean;
  error?: Error | null;
  onToggleAI: () => void;
  aiInsightsOpen: boolean;
  onSchemaChange?: (schema: SchemaType) => void;
  selectedSchema?: SchemaType;
  startDate?: string;
  endDate?: string;
  onDateRangeChange?: (start: string, end: string) => void;
}

// Theme-based color palette
const themeColors = {
  primary: "hsl(212 81% 19%)", // Main primary color
  primaryLight: "hsl(212 65% 35%)", // Lighter primary
  primaryLighter: "hsl(212 45% 55%)", // Even lighter primary
  accent: "hsl(212 100% 85%)", // Accent color
  destructive: "hsl(0 84.2% 60.2%)", // Red for serious incidents
  success: "hsl(142 71% 45%)", // Green for success
  warning: "hsl(38 92% 50%)", // Orange for warnings
  muted: "hsl(212 25% 45%)", // Muted text
  chartColors: [
    "hsl(212 81% 19%)", // Primary dark blue
    "hsl(212 65% 35%)", // Primary light blue
    "hsl(212 45% 55%)", // Primary lighter blue
    "hsl(212 100% 85%)", // Accent blue
    "hsl(142 71% 45%)", // Success green
    "hsl(38 92% 50%)", // Warning orange
    "hsl(0 84.2% 60.2%)", // Destructive red
    "hsl(262 83% 58%)", // Purple
    "hsl(201 96% 32%)", // Dark blue
    "hsl(25 95% 53%)", // Orange
  ]
};

export const CleanDashboard = ({
  data,
  isLoading,
  error,
  onToggleAI,
  aiInsightsOpen,
  onSchemaChange,
  selectedSchema = "srs",
  startDate,
  endDate,
  onDateRangeChange
}: CleanDashboardProps) => {
  const [date, setDate] = useState<DateRange | undefined>();
  const [timePeriod, setTimePeriod] = useState<string>("365");
  const [chatBotOpen, setChatBotOpen] = useState(false);

  // Chat API hook
  const sendChatMessage = useSendChatMessage();

  // Sync local date state with parent props
  useEffect(() => {
    if (startDate && endDate) {
      setDate({
        from: parseISO(startDate),
        to: parseISO(endDate)
      });
    }
  }, [startDate, endDate]);

  // Quick date filter handler
  const handleQuickDateFilter = (days: number) => {
    if (onDateRangeChange) {
      const endDate = endOfDay(new Date());
      const startDate = startOfDay(subDays(endDate, days - 1));

      const startDateStr = format(startDate, 'yyyy-MM-dd');
      const endDateStr = format(endDate, 'yyyy-MM-dd');

      onDateRangeChange(startDateStr, endDateStr);
      setTimePeriod(days.toString());
    }
  };

  // Chat handlers
  const toggleChatBot = () => {
    setChatBotOpen(!chatBotOpen);
  };

  const handleSendChatMessage = async (message: string): Promise<{ text: string; visualizationData?: Record<string, unknown> }> => {
    try {
      const response = await sendChatMessage.mutateAsync(message);
      return response;
    } catch (error) {
      console.error('Chat error:', error);
      return {
        text: 'Sorry, I encountered an error processing your message. Please try again.'
      };
    }
  };

  const handleSaveToDashboard = async (chartData: Record<string, unknown>, title: string, description: string): Promise<void> => {
    try {
      const response = await httpClient.post('/api/v1/saved-charts/save-chart', {
        chart_data: chartData,
        title: title,
        description: description,
      });
      
      // Response should already be parsed by httpClient
      if (!response) {
        throw new Error('Failed to save chart');
      }
    } catch (error) {
      console.error('Error saving chart:', error);
      throw error;
    }
  };

  // Validate and map dashboard data
  const validation = validateDashboardData(data);
  const mappedData = mapDashboardData(data);

  // Handle loading state
  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">Safety Dashboard</h1>
          <div className="animate-pulse bg-gray-200 h-8 w-32 rounded"></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="animate-pulse">
              <div className="bg-gray-200 h-32 rounded-lg"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Handle error state
  if (error) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">Safety Dashboard</h1>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">Failed to load dashboard data: {error.message}</p>
          <details className="mt-2">
            <summary className="cursor-pointer text-sm">Error Details</summary>
            <pre className="text-xs mt-2 bg-gray-100 p-2 rounded overflow-auto">
              {JSON.stringify(error, null, 2)}
            </pre>
          </details>
        </div>
      </div>
    );
  }

  // Handle no data state
  if (!data) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">Safety Dashboard</h1>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-yellow-800">No dashboard data available. Please upload some files first.</p>
        </div>
      </div>
    );
  }

  // Transform real data for charts with theme colors
  const monthlyTrendsData = data?.monthly_trends?.map(trend => ({
    month: trend.month,
    incidents: trend.event_count,
    serious: trend.serious_count,
    stoppages: trend.work_stopped_count
  })) || [];

  const eventTypesData = data?.event_type_distribution?.map((item, index) => ({
    name: item.event_type,
    value: item.event_count,
    percentage: item.percentage,
    color: themeColors.chartColors[index % themeColors.chartColors.length]
  })) || [];

  const severityLevelsData = data?.incident_severity_distribution?.map((item, index) => ({
    name: item.severity_level,
    value: item.incident_count,
    percentage: item.percentage,
    color: [themeColors.destructive, themeColors.warning, "hsl(45 93% 47%)", themeColors.success][index % 4]
  })) || [];

  const branchPerformanceData = data?.branch_performance_analysis?.slice(0, 5).map(branch => ({
    branch: branch.branch,
    region: branch.region,
    total_incidents: branch.total_incidents,
    serious_incidents: Math.round(branch.total_incidents * (branch.serious_incident_rate / 100)),
    work_stoppages: Math.round(branch.total_incidents * (branch.work_stoppage_rate / 100))
  })) || [];

  const repeatLocationsData = data?.repeat_locations?.map(location => ({
    location: location.location,
    region: location.region,
    incidents: location.incident_count,
    work_stopped: location.work_stopped_incidents,
    serious: location.serious_incidents,
    work_stopped_rate: location.work_stopped_rate
  })) || [];

  // Time-based analysis data (use real data if available, fallback to placeholder)
  const timeOfDayData = data?.time_based_analysis?.hourly_distribution?.map(hour => ({
    hour: hour.hour.toString().padStart(2, '0'),
    incidents: hour.incident_count,
    percentage: hour.percentage
  })) || [
    { hour: "00", incidents: 2, percentage: 5 },
    { hour: "04", incidents: 1, percentage: 2 },
    { hour: "08", incidents: 8, percentage: 18 },
    { hour: "12", incidents: 12, percentage: 27 },
    { hour: "16", incidents: 15, percentage: 34 },
    { hour: "20", incidents: 6, percentage: 14 }
  ];

  const weeklyPatternData = data?.time_based_analysis?.daily_distribution?.map(day => ({
    day: day.day_name.substring(0, 3),
    incidents: day.incident_count,
    percentage: day.percentage
  })) || [
    { day: "Mon", incidents: 18, percentage: 15 },
    { day: "Tue", incidents: 22, percentage: 18 },
    { day: "Wed", incidents: 25, percentage: 21 },
    { day: "Thu", incidents: 19, percentage: 16 },
    { day: "Fri", incidents: 28, percentage: 23 },
    { day: "Sat", incidents: 12, percentage: 10 },
    { day: "Sun", incidents: 8, percentage: 7 }
  ];

  return (
    <div className="space-y-4 md:space-y-6">
      {/* Data Quality Status */}
      {validation.dataQuality !== 'excellent' && (
        <div className={`border rounded-lg p-4 ${
          validation.dataQuality === 'poor' 
            ? 'bg-red-50 border-red-200' 
            : validation.dataQuality === 'fair'
            ? 'bg-orange-50 border-orange-200'
            : 'bg-blue-50 border-blue-200'
        }`}>
          <div className="flex items-center justify-between">
            <div>
              <h3 className={`font-medium ${
                validation.dataQuality === 'poor' 
                  ? 'text-red-800' 
                  : validation.dataQuality === 'fair'
                  ? 'text-orange-800'
                  : 'text-blue-800'
              }`}>
                {validation.dataQuality === 'poor' && 'Data Quality Issues Detected'}
                {validation.dataQuality === 'fair' && 'Limited Data Available'}
                {validation.dataQuality === 'good' && 'Data Quality Notice'}
              </h3>
              <p className={`text-sm mt-1 ${
                validation.dataQuality === 'poor' 
                  ? 'text-red-700' 
                  : validation.dataQuality === 'fair'
                  ? 'text-orange-700'
                  : 'text-blue-700'
              }`}>
                {validation.dataQuality === 'poor' && 'Critical dashboard data is missing. Please check your data upload or try a different time period.'}
                {validation.dataQuality === 'fair' && 'Some dashboard data is missing or incomplete. Charts may show placeholder data for shorter time periods.'}
                {validation.dataQuality === 'good' && 'Dashboard data is available but some optional features may show placeholder data.'}
              </p>
              {validation.warnings.length > 0 && (
                <details className="mt-2">
                  <summary className="cursor-pointer text-sm font-medium">View Details</summary>
                  <ul className="text-xs mt-1 space-y-1">
                    {validation.warnings.map((warning, index) => (
                      <li key={index} className="flex items-start">
                        <span className="text-gray-500 mr-1">•</span>
                        <span>{warning}</span>
                      </li>
                    ))}
                  </ul>
                </details>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Header with Date Filters and AI Icon */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl md:text-2xl font-bold">Dashboard</h2>
          {startDate && endDate && (
            <p className="text-sm text-muted-foreground mt-1">
              {format(parseISO(startDate), 'MMM dd, yyyy')} - {format(parseISO(endDate), 'MMM dd, yyyy')}
            </p>
          )}
        </div>
        
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4">
          {/* Time Period Dropdown */}
          <Select
            value={timePeriod}
            onValueChange={(value) => {
              setTimePeriod(value);
              handleQuickDateFilter(parseInt(value));
            }}
          >
            <SelectTrigger className="w-full sm:w-[150px] h-9">
              <SelectValue placeholder="Time Period" />
            </SelectTrigger>
            <SelectContent>
              {/* 
              <SelectItem value="7">Past 7 days</SelectItem>
              <SelectItem value="30">Past 30 days</SelectItem>
              */}
              <SelectItem value="60">Past 60 days</SelectItem>
              <SelectItem value="90">Past 90 days</SelectItem>
              <SelectItem value="365">Past 1 year</SelectItem>
            </SelectContent>
          </Select>

          {/* Date Range Picker */}
          <Popover>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                size="sm"
                className="w-9 h-9 p-0"
              >
                <Calendar className="h-4 w-4" />
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <div className="p-3">
                <CalendarComponent
                  initialFocus
                  mode="range"
                  defaultMonth={date?.from}
                  selected={date}
                  onSelect={setDate}
                  numberOfMonths={2}
                  className={cn("pointer-events-auto")}
                />
                <div className="flex justify-end pt-3 border-t border-border">
                  <Button
                    size="sm"
                    onClick={() => {
                      if (date?.from && date?.to && onDateRangeChange) {
                        const startDateStr = format(date.from, 'yyyy-MM-dd');
                        const endDateStr = format(date.to, 'yyyy-MM-dd');
                        onDateRangeChange(startDateStr, endDateStr);
                      }
                    }}
                    className="bg-primary hover:bg-primary/90"
                    disabled={!date?.from || !date?.to}
                  >
                    Apply
                  </Button>
                </div>
              </div>
            </PopoverContent>
          </Popover>

          {/* AI Icon */}
          <div className="self-center sm:self-auto">
            <AIFloatingIcon 
              onToggle={onToggleAI} 
              isOpen={aiInsightsOpen}
              isInline={true}
            />
          </div>
        </div>
      </div>

      {/* KPI Summary Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
        <Card className="shadow-card relative group hover:shadow-hover transition-all duration-200">
          <CardContent className="p-3 md:p-4">
            <div className="absolute top-3 left-3">
              <Activity className="h-4 w-4 text-primary" />
            </div>
            <div className="text-center">
              <p className="text-lg md:text-2xl font-bold text-primary">
                {data?.total_events?.count?.total_events || 0}
              </p>
              <p className="text-xs md:text-sm text-muted-foreground">Total Events</p>
            </div>
          </CardContent>
        </Card>
        <Card className="shadow-card relative group hover:shadow-hover transition-all duration-200">
          <CardContent className="p-3 md:p-4">
            <div className="absolute top-3 left-3">
              <AlertTriangle className="h-4 w-4 text-red-500" />
            </div>
            <div className="text-center">
              <p className="text-lg md:text-2xl font-bold text-red-600">
                {data?.serious_near_miss_rate?.count?.serious_near_miss_count || 0}
              </p>
              <p className="text-xs md:text-sm text-muted-foreground">Serious Incidents</p>
            </div>
          </CardContent>
        </Card>
        <Card className="shadow-card relative group hover:shadow-hover transition-all duration-200">
          <CardContent className="p-3 md:p-4">
            <div className="absolute top-3 left-3">
              <Zap className="h-4 w-4 text-orange-500" />
            </div>
            <div className="text-center">
              <p className="text-lg md:text-2xl font-bold text-orange-600">
                {data?.work_stoppage_rate?.count || 0}
              </p>
              <p className="text-xs md:text-sm text-muted-foreground">Work Stoppages</p>
            </div>
          </CardContent>
        </Card>
        <Card className="shadow-card relative group hover:shadow-hover transition-all duration-200">
          <CardContent className="p-3 md:p-4">
            <div className="absolute top-3 left-3">
              <Clock className="h-4 w-4 text-green-500" />
            </div>
            <div className="text-center">
              <p className="text-lg md:text-2xl font-bold text-green-600">
                {data?.response_time_analysis?.average_response_time || "N/A"}
              </p>
              <p className="text-xs md:text-sm text-muted-foreground">Avg Response Time</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 md:gap-6">
        {/* Monthly Trends - Line Chart */}
        <Card className="shadow-card col-span-1 group hover:shadow-hover transition-all duration-200">
          <CardContent className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <TrendingUp className="h-4 w-4 text-primary" />
              <CardTitle className="text-lg font-semibold text-gray-800">Monthly Trends</CardTitle>
            </div>
            <div className="flex justify-center">
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={monthlyTrendsData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" opacity={0.6} />
                  <XAxis
                    dataKey="month"
                    fontSize={11}
                    tick={{ fontSize: 11, fill: '#6b7280' }}
                    axisLine={{ stroke: '#d1d5db' }}
                    tickLine={{ stroke: '#d1d5db' }}
                  />
                  <YAxis
                    fontSize={11}
                    tick={{ fontSize: 11, fill: '#6b7280' }}
                    axisLine={{ stroke: '#d1d5db' }}
                    tickLine={{ stroke: '#d1d5db' }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                    }}
                  />
                  <Legend
                    wrapperStyle={{ paddingTop: '20px', fontSize: '12px' }}
                    iconType="line"
                  />
                  <Line
                    type="monotone"
                    dataKey="incidents"
                    stroke={themeColors.primary}
                    strokeWidth={3}
                    name="Total Incidents"
                    dot={{ fill: themeColors.primary, strokeWidth: 2, r: 4 }}
                    activeDot={{ r: 6, stroke: themeColors.primary, strokeWidth: 2 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="serious"
                    stroke={themeColors.destructive}
                    strokeWidth={3}
                    name="Serious Incidents"
                    dot={{ fill: themeColors.destructive, strokeWidth: 2, r: 4 }}
                    activeDot={{ r: 6, stroke: themeColors.destructive, strokeWidth: 2 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="stoppages"
                    stroke={themeColors.warning}
                    strokeWidth={3}
                    name="Work Stoppages"
                    dot={{ fill: themeColors.warning, strokeWidth: 2, r: 4 }}
                    activeDot={{ r: 6, stroke: themeColors.warning, strokeWidth: 2 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Event Types - Doughnut Chart */}
        <Card className="shadow-card col-span-1 group hover:shadow-hover transition-all duration-200">
          <CardContent className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <BarChart3 className="h-4 w-4 text-primary" />
              <CardTitle className="text-lg font-semibold text-gray-800">Event Types</CardTitle>
            </div>
            <div className="flex justify-center">
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie
                    data={eventTypesData}
                    cx="50%"
                    cy="45%"
                    innerRadius={50}
                    outerRadius={90}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {eventTypesData.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={themeColors.chartColors[index % themeColors.chartColors.length]}
                        stroke="white"
                        strokeWidth={2}
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                    }}
                  />
                  <Legend
                    wrapperStyle={{ fontSize: '11px', paddingTop: '15px' }}
                    iconSize={10}
                    layout="horizontal"
                    align="center"
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Severity Levels - Pie Chart */}
        <Card className="shadow-card col-span-1 group hover:shadow-hover transition-all duration-200">
          <CardContent className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <AlertTriangle className="h-4 w-4 text-primary" />
              <CardTitle className="text-lg font-semibold text-gray-800">Severity Levels</CardTitle>
            </div>
            <div className="flex justify-center">
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie
                    data={severityLevelsData}
                    cx="50%"
                    cy="45%"
                    outerRadius={90}
                    dataKey="value"
                    label={({name, percent}) => `${(percent * 100).toFixed(0)}%`}
                    labelLine={false}
                  >
                    {severityLevelsData.map((entry, index) => {
                      const severityColors = [themeColors.destructive, themeColors.warning, "hsl(45 93% 47%)", themeColors.success];
                      return (
                        <Cell
                          key={`cell-${index}`}
                          fill={severityColors[index % severityColors.length]}
                          stroke="white"
                          strokeWidth={2}
                        />
                      );
                    })}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                    }}
                  />
                  <Legend
                    wrapperStyle={{ fontSize: '11px', paddingTop: '15px' }}
                    iconSize={10}
                    layout="horizontal"
                    align="center"
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Top 5 Branches - Multi Bar Chart */}
        <Card className="shadow-card col-span-1 group hover:shadow-hover transition-all duration-200">
          <CardContent className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <Building2 className="h-4 w-4 text-primary" />
              <CardTitle className="text-lg font-semibold text-gray-800">Top 5 Branches</CardTitle>
            </div>
            <div className="flex justify-center">
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={branchPerformanceData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" opacity={0.6} />
                  <XAxis
                    dataKey="branch"
                    fontSize={11}
                    tick={{ fontSize: 11, fill: '#6b7280' }}
                    axisLine={{ stroke: '#d1d5db' }}
                    tickLine={{ stroke: '#d1d5db' }}
                    angle={-45}
                    textAnchor="end"
                    height={60}
                  />
                  <YAxis
                    fontSize={11}
                    tick={{ fontSize: 11, fill: '#6b7280' }}
                    axisLine={{ stroke: '#d1d5db' }}
                    tickLine={{ stroke: '#d1d5db' }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                    }}
                  />
                  <Legend
                    wrapperStyle={{ paddingTop: '20px', fontSize: '12px' }}
                  />
                  <Bar
                    dataKey="total_incidents"
                    fill={themeColors.primary}
                    name="Total Incidents"
                    radius={[2, 2, 0, 0]}
                  />
                  <Bar
                    dataKey="serious_incidents"
                    fill={themeColors.destructive}
                    name="Serious Incidents"
                    radius={[2, 2, 0, 0]}
                  />
                  <Bar
                    dataKey="work_stoppages"
                    fill={themeColors.warning}
                    name="Work Stoppages"
                    radius={[2, 2, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Time of Day - Area Chart */}
        <Card className="shadow-card col-span-1 group hover:shadow-hover transition-all duration-200">
          <CardContent className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <Sun className="h-4 w-4 text-primary" />
              <CardTitle className="text-lg font-semibold text-gray-800">Time of Day Pattern</CardTitle>
            </div>
            <div className="flex justify-center">
              <ResponsiveContainer width="100%" height={280}>
                <AreaChart data={timeOfDayData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" opacity={0.6} />
                  <XAxis
                    dataKey="hour"
                    fontSize={11}
                    tick={{ fontSize: 11, fill: '#6b7280' }}
                    axisLine={{ stroke: '#d1d5db' }}
                    tickLine={{ stroke: '#d1d5db' }}
                  />
                  <YAxis
                    fontSize={11}
                    tick={{ fontSize: 11, fill: '#6b7280' }}
                    axisLine={{ stroke: '#d1d5db' }}
                    tickLine={{ stroke: '#d1d5db' }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="incidents"
                    stroke={themeColors.primary}
                    fill={themeColors.primary}
                    fillOpacity={0.3}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Weekly Pattern - Line Chart */}
        <Card className="shadow-card col-span-1 group hover:shadow-hover transition-all duration-200">
          <CardContent className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <CalendarDays className="h-4 w-4 text-primary" />
              <CardTitle className="text-lg font-semibold text-gray-800">Weekly Pattern</CardTitle>
            </div>
            <div className="flex justify-center">
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={weeklyPatternData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" opacity={0.6} />
                  <XAxis
                    dataKey="day"
                    fontSize={11}
                    tick={{ fontSize: 11, fill: '#6b7280' }}
                    axisLine={{ stroke: '#d1d5db' }}
                    tickLine={{ stroke: '#d1d5db' }}
                  />
                  <YAxis
                    fontSize={11}
                    tick={{ fontSize: 11, fill: '#6b7280' }}
                    axisLine={{ stroke: '#d1d5db' }}
                    tickLine={{ stroke: '#d1d5db' }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="incidents"
                    stroke={themeColors.primary}
                    strokeWidth={3}
                    dot={{ fill: themeColors.primary, strokeWidth: 2, r: 4 }}
                    activeDot={{ r: 6, stroke: themeColors.primary, strokeWidth: 2 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Additional Analytics Section */}
      <div className="grid grid-cols-1 xl:grid-cols-1 gap-4 md:gap-6 mt-6">
        {/* Repeat Locations */}
        <Card className="shadow-card col-span-1 group hover:shadow-hover transition-all duration-200">
          <CardHeader className="pb-3">
            <CardTitle className="text-base md:text-lg">High-Risk Locations</CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="space-y-3 max-h-[250px] overflow-y-auto">
              {repeatLocationsData.slice(0, 8).map((location, index) => (
                <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded hover:bg-gray-100 transition-colors duration-200">
                  <div>
                    <p className="font-medium text-sm">{location.location}</p>
                    <p className="text-xs text-gray-600">{location.region}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-sm">{location.incidents}</p>
                    <p className="text-xs text-gray-600">incidents</p>
                  </div>
                </div>
              ))}
              {repeatLocationsData.length === 0 && (
                <p className="text-center text-gray-500 py-8">No repeat locations data available</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Augmented Analytics for ni_tct_augmented schema */}
      {selectedSchema === "ni_tct_augmented" && data?.augmented_kpis && (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 md:gap-6 mt-6">
          {/* Weather Impact Analysis */}
          <Card className="shadow-card col-span-1 group hover:shadow-hover transition-all duration-200">
            <CardHeader className="pb-3">
              <CardTitle className="text-base md:text-lg">Weather Impact Analysis</CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <ResponsiveContainer width="100%" height={200} className="md:!h-[250px]">
                <BarChart data={data.augmented_kpis.weather_impact_analysis?.slice(0, 6)}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis
                    dataKey="weather_condition"
                    fontSize={12}
                    tick={{ fontSize: 12 }}
                    angle={-45}
                    textAnchor="end"
                    height={60}
                  />
                  <YAxis
                    fontSize={12}
                    tick={{ fontSize: 12 }}
                  />
                  <Tooltip />
                  <Bar dataKey="incident_count" fill={themeColors.primary} name="Incidents" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Experience Level Analysis */}
          <Card className="shadow-card col-span-1 group hover:shadow-hover transition-all duration-200">
            <CardHeader className="pb-3">
              <CardTitle className="text-base md:text-lg">Experience Level Impact</CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <ResponsiveContainer width="100%" height={200} className="md:!h-[250px]">
                <PieChart>
                  <Pie
                    data={data.augmented_kpis.experience_level_analysis?.experience_groups?.slice(0, 5)}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    dataKey="incident_count"
                    nameKey="experience_level"
                    label={({name, percent}) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  >
                    {data.augmented_kpis.experience_level_analysis?.experience_groups?.slice(0, 5).map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={themeColors.chartColors[index % themeColors.chartColors.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Chatbot Components */}
      <ChatBotFloatingIcon onToggle={toggleChatBot} isOpen={chatBotOpen} />
      <ChatBot
        isOpen={chatBotOpen}
        onToggle={toggleChatBot}
        onSendMessage={handleSendChatMessage}
        onSaveToDashboard={handleSaveToDashboard}
      />
    </div>
  );
};