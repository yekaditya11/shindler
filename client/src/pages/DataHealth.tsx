import React, { useState, useEffect } from "react";
import { ArrowLeft, CheckCircle, AlertTriangle, XCircle, TrendingUp, RefreshCw, Database, Clock, Target, Shield, Zap, BarChart3, Brain, Info } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { dataHealthApi } from "@/services/api";
import { HealthReport, SchemaType } from "@/types/api";
import { useAppState } from "@/contexts/AppStateContext";

const DataHealth = () => {
  const navigate = useNavigate();
  const { detectedSchema } = useAppState();
  const [healthData, setHealthData] = useState<HealthReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchHealthData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Use detected schema from upload response, fallback to 'srs' if not available
      const schemaToUse: SchemaType = detectedSchema || 'srs';
      
      const response = await dataHealthApi.getDataHealthLLM(schemaToUse);
      // httpClient extracts the body, so response should contain health_report directly
      setHealthData(response.health_report);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch data health information");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealthData();
  }, [detectedSchema]); // Re-fetch when schema changes

  const getHealthGradeColor = (grade: string) => {
    switch (grade.toLowerCase()) {
      case "excellent": return "text-green-600 bg-green-100";
      case "good": return "text-blue-600 bg-blue-100";
      case "poor": return "text-yellow-600 bg-yellow-100";
      case "bad": return "text-red-600 bg-red-100";
      default: return "text-gray-600 bg-gray-100";
    }
  };

  const getHealthIcon = (grade: string) => {
    switch (grade.toLowerCase()) {
      case "excellent": return <CheckCircle className="h-5 w-5 text-green-600" />;
      case "good": return <CheckCircle className="h-5 w-5 text-blue-600" />;
      case "poor": return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
      case "bad": return <XCircle className="h-5 w-5 text-red-600" />;
      default: return <CheckCircle className="h-5 w-5 text-gray-600" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case "high": return "bg-red-100 text-red-800";
      case "medium": return "bg-yellow-100 text-yellow-800";
      case "low": return "bg-green-100 text-green-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const getDimensionIcon = (dimension: string) => {
    switch (dimension) {
      case "completeness": return <Database className="h-4 w-4" />;
      case "uniqueness": return <Target className="h-4 w-4" />;
      case "consistency": return <Shield className="h-4 w-4" />;
      case "validity": return <CheckCircle className="h-4 w-4" />;
      case "timeliness": return <Clock className="h-4 w-4" />;
      default: return <BarChart3 className="h-4 w-4" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case "critical": return "bg-red-100 text-red-800 border-red-200";
      case "high": return "bg-orange-100 text-orange-800 border-orange-200";
      case "medium": return "bg-blue-100 text-blue-800 border-blue-200";
      case "low": return "bg-gray-100 text-gray-800 border-gray-200";
      default: return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background p-4 md:p-6 lg:p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center gap-4 mb-6">
            <Button variant="ghost" size="sm" onClick={() => navigate("/dashboard")}>
              <ArrowLeft className="h-4 w-4" />
            </Button>
                      <div>
            <h1 className="text-2xl md:text-3xl font-bold">Data Health Assessment</h1>
            <p className="text-muted-foreground">
              Monitor and maintain data quality across your systems
              {detectedSchema && (
                <span className="ml-2">
                  • Schema: <span className="font-medium capitalize">{detectedSchema.replace('_', ' ')}</span>
                </span>
              )}
            </p>
            {!detectedSchema && (
              <p className="text-sm text-orange-600 mt-1">
                ⚠️ Using default schema (srs) - upload data to detect actual schema
              </p>
            )}
          </div>
          </div>
          
          <div className="flex items-center justify-center py-16">
            <div className="flex items-center gap-3">
              <Brain className="h-6 w-6 text-blue-600 animate-pulse" />
              <span className="text-lg text-muted-foreground">LLM is analyzing</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background p-4 md:p-6 lg:p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center gap-4 mb-6">
            <Button variant="ghost" size="sm" onClick={() => navigate("/dashboard")}>
              <ArrowLeft className="h-4 w-4" />
            </Button>
                      <div>
            <h1 className="text-2xl md:text-3xl font-bold">Data Health</h1>
            <p className="text-muted-foreground">
              Monitor and maintain data quality across your systems
              {detectedSchema && (
                <span className="ml-2">
                  • Schema: <span className="font-medium capitalize">{detectedSchema.replace('_', ' ')}</span>
                </span>
              )}
            </p>
            {!detectedSchema && (
              <p className="text-sm text-orange-600 mt-1">
                ⚠️ Using default schema (srs) - upload data to detect actual schema
              </p>
            )}
          </div>
          </div>
          <Alert className="border-red-200 bg-red-50">
            <XCircle className="h-4 w-4 text-red-600" />
            <AlertDescription className="text-red-800">
              Error loading data health information: {error}
            </AlertDescription>
          </Alert>
                     <div className="mt-4">
             <Button onClick={fetchHealthData} variant="outline">
               <RefreshCw className="h-4 w-4 mr-2" />
               Try Again
             </Button>
           </div>
        </div>
      </div>
    );
  }

  if (!healthData) return null;

  const criticalColumns = Object.entries(healthData.column_analysis).filter(
    ([, analysis]) => analysis.priority === "critical"
  );

  return (
    <div className="min-h-screen bg-background p-4 md:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/dashboard")}
            className="p-2"
          >
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-2xl md:text-3xl font-bold">Data Health Assessment</h1>
            <p className="text-muted-foreground">
              LLM-enhanced data quality monitoring • {healthData.total_records.toLocaleString()} records analyzed
              {detectedSchema && (
                <span className="ml-2">
                  • Schema: <span className="font-medium capitalize">{detectedSchema.replace('_', ' ')}</span>
                </span>
              )}
            </p>
            {!detectedSchema && (
              <p className="text-sm text-orange-600 mt-1">
                ⚠️ Using default schema (srs) - upload data to detect actual schema
              </p>
            )}
          </div>
        </div>

        {/* Overall Health Score */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-xl font-semibold">Overall Data Health Score</h2>
                <p className="text-muted-foreground">
                  LLM-enhanced assessment • {new Date(healthData.assessment_timestamp).toLocaleDateString()}
                </p>
              </div>
              <div className="flex items-center gap-3">
                {getHealthIcon(healthData.overall_health.grade)}
                <div className="text-right">
                  <div className="text-3xl font-bold">{healthData.overall_health.score}%</div>
                  <Badge className={getHealthGradeColor(healthData.overall_health.grade)}>
                    {healthData.overall_health.grade}
                  </Badge>
                </div>
              </div>
            </div>
            <Progress value={healthData.overall_health.score} className="h-3 mb-4" />
            
            {/* LLM Insights Summary */}
            {healthData.llm_insights && (
              <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-center gap-2 mb-2">
                  <Brain className="h-4 w-4 text-blue-600" />
                  <span className="font-medium text-blue-800">LLM Optimization Summary</span>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="text-blue-600">Columns Analyzed:</span>
                    <div className="font-semibold">{healthData.llm_insights.total_columns_analyzed}</div>
                  </div>
                  <div>
                    <span className="text-blue-600">Intelligent Selections:</span>
                    <div className="font-semibold">{healthData.llm_insights.dimension_selections_made}</div>
                  </div>
                  {healthData.performance_metrics && (
                    <>
                      <div>
                        <span className="text-blue-600">Processing Time:</span>
                        <div className="font-semibold">{healthData.performance_metrics.total_processing_time_seconds.toFixed(1)}s</div>
                      </div>
                      <div>
                        <span className="text-blue-600">Parallel Processing:</span>
                        <div className="font-semibold">{healthData.performance_metrics.parallel_processing_enabled ? "Enabled" : "Disabled"}</div>
                      </div>
                    </>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Dimension Scores */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
          {Object.entries(healthData.overall_health.dimensions).map(([dimension, data]) => (
            <Card key={dimension} className="shadow-card">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                                     <div className="flex items-center gap-2">
                     {getDimensionIcon(dimension)}
                     <CardTitle className="text-sm capitalize">{dimension}</CardTitle>
                   </div>
                </div>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="space-y-3">
                  <div className="text-2xl font-bold">{data.score}%</div>
                  <Progress value={data.score} className="h-2" />
                  {data.columns_assessed && (
                    <p className="text-xs text-muted-foreground">
                      {data.columns_assessed} columns assessed
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="columns">Column Analysis</TabsTrigger>
            <TabsTrigger value="issues">Issues & Recommendations</TabsTrigger>
            <TabsTrigger value="insights">LLM Insights</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {/* Critical Fields Summary */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="h-5 w-5" />
                  Critical Fields Summary
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">{healthData.summary.critical_fields.healthy}</div>
                    <div className="text-sm text-muted-foreground">Healthy (≥80%)</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-yellow-600">{healthData.summary.critical_fields.warning}</div>
                    <div className="text-sm text-muted-foreground">Warning (60-79%)</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-red-600">{healthData.summary.critical_fields.critical}</div>
                    <div className="text-sm text-muted-foreground">Critical (&lt;60%)</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold">{healthData.summary.critical_fields.avg_score.toFixed(1)}%</div>
                    <div className="text-sm text-muted-foreground">Average Score</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Top Issues */}
            <Card>
              <CardHeader>
                <CardTitle>Top Data Quality Issues</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {healthData.summary.top_issues.map((issue, index) => (
                    <div key={index} className="flex items-start gap-4 p-4 border border-border rounded-lg">
                      <Badge className={getSeverityColor(issue.severity)}>
                        {issue.severity}
                      </Badge>
                      <div className="flex-1">
                        <h4 className="font-medium">{issue.column}</h4>
                        <p className="text-sm text-muted-foreground mb-1">{issue.issue}</p>
                        <p className="text-xs text-muted-foreground">{issue.impact}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="columns" className="space-y-6">
            {/* Critical Columns */}
            {criticalColumns.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-red-600">
                    <AlertTriangle className="h-5 w-5" />
                    Critical Priority Columns
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-4">
                    {criticalColumns.map(([columnName, analysis]) => (
                      <div key={columnName} className="p-4 border border-red-200 rounded-lg bg-red-50">
                        <div className="flex items-center justify-between mb-3">
                          <h4 className="font-medium">{columnName}</h4>
                          <div className="flex items-center gap-2">
                            <Badge className={getPriorityColor(analysis.priority)}>
                              {analysis.priority}
                            </Badge>
                            <span className="text-sm font-medium">{analysis.overall_column_score}%</span>
                          </div>
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
                          <div>
                            <span className="text-muted-foreground">Checked:</span>
                            <div>{analysis.dimensions_checked.join(", ")}</div>
                          </div>
                          <div>
                            <span className="text-muted-foreground">Skipped:</span>
                            <div>{analysis.dimensions_skipped.join(", ") || "None"}</div>
                          </div>
                          <div>
                            <span className="text-muted-foreground">Issues:</span>
                            <div>{analysis.issues.length}</div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* All Columns */}
            <Card>
              <CardHeader>
                <CardTitle>All Column Analysis</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4 max-h-96 overflow-y-auto">
                  {Object.entries(healthData.column_analysis).map(([columnName, analysis]) => (
                    <div key={columnName} className="p-4 border border-border rounded-lg">
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="font-medium">{columnName}</h4>
                        <div className="flex items-center gap-2">
                          <Badge className={getPriorityColor(analysis.priority)}>
                            {analysis.priority}
                          </Badge>
                          <span className="text-sm font-medium">{analysis.overall_column_score}%</span>
                        </div>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-muted-foreground">Dimensions Checked:</span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {analysis.dimensions_checked.map((dim) => (
                              <Badge key={dim} variant="outline" className="text-xs">
                                {dim}
                              </Badge>
                            ))}
                          </div>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Dimensions Skipped:</span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {analysis.dimensions_skipped.map((dim) => (
                              <Badge key={dim} variant="outline" className="text-xs bg-gray-100">
                                {dim}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>
                      <Progress value={analysis.overall_column_score} className="h-2 mt-3" />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="issues" className="space-y-6">
            {/* Recommendations */}
            <div className="grid gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-red-600">Immediate Actions Required</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {healthData.summary.recommendations.immediate.map((recommendation, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <AlertTriangle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                        <span className="text-sm">{recommendation}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-yellow-600">Short-term Improvements</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {healthData.summary.recommendations.short_term.map((recommendation, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <TrendingUp className="h-4 w-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                        <span className="text-sm">{recommendation}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-blue-600">Long-term Strategic Actions</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {healthData.summary.recommendations.long_term.map((recommendation, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <Target className="h-4 w-4 text-blue-500 mt-0.5 flex-shrink-0" />
                        <span className="text-sm">{recommendation}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              {healthData.summary.recommendations.llm_recommendations && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-purple-600 flex items-center gap-2">
                      <Brain className="h-5 w-5" />
                      LLM-Enhanced Recommendations
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {healthData.summary.recommendations.llm_recommendations.map((recommendation, index) => (
                        <li key={index} className="flex items-start gap-2">
                          <Zap className="h-4 w-4 text-purple-500 mt-0.5 flex-shrink-0" />
                          <span className="text-sm">{recommendation}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          <TabsContent value="insights" className="space-y-6">
            {/* LLM Insights */}
            {healthData.summary.llm_insights && (
              <div className="grid gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Brain className="h-5 w-5" />
                      Dimension Optimization Analysis
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-600">
                          {healthData.summary.llm_insights.dimension_optimization.total_possible_checks}
                        </div>
                        <div className="text-sm text-muted-foreground">Possible Checks</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-600">
                          {healthData.summary.llm_insights.dimension_optimization.total_actual_checks}
                        </div>
                        <div className="text-sm text-muted-foreground">Actual Checks</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-orange-600">
                          {healthData.summary.llm_insights.dimension_optimization.checks_skipped}
                        </div>
                        <div className="text-sm text-muted-foreground">Checks Skipped</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-purple-600">
                          {healthData.summary.llm_insights.dimension_optimization.optimization_percentage.toFixed(1)}%
                        </div>
                        <div className="text-sm text-muted-foreground">Optimization</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Priority Distribution</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-3 gap-4">
                      {Object.entries(healthData.summary.llm_insights.priority_distribution).map(([priority, count]) => (
                        <div key={priority} className="text-center">
                          <div className="text-2xl font-bold">{count}</div>
                          <div className="text-sm text-muted-foreground capitalize">{priority} Priority</div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Intelligent Skip Analysis</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {Object.entries(healthData.summary.llm_insights.intelligent_skips.skip_counts).map(([dimension, count]) => (
                        <div key={dimension} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                          <span className="font-medium capitalize">{dimension}</span>
                          <Badge variant="outline">{count} columns skipped</Badge>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default DataHealth;