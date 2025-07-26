/**
 * Dashboard Debug Panel
 * Shows the complete JSON structure and identifies missing/available data
 */

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ChevronDown, ChevronRight, Database, AlertTriangle, CheckCircle } from "lucide-react";
import { DashboardKPIs } from "@/types/api";
import { validateDashboardData } from "@/utils/dashboardDataMapper";

interface DashboardDebugPanelProps {
  data?: DashboardKPIs;
  isVisible: boolean;
  onToggle: () => void;
}

export const DashboardDebugPanel = ({ data, isVisible, onToggle }: DashboardDebugPanelProps) => {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());
  
  const validation = validateDashboardData(data);

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  const renderJsonValue = (value: any, key: string, depth: number = 0): JSX.Element => {
    const indent = depth * 20;
    
    if (value === null || value === undefined) {
      return (
        <div style={{ marginLeft: indent }} className="text-gray-400">
          <span className="text-blue-600">"{key}"</span>: <span className="text-red-500">null</span>
        </div>
      );
    }
    
    if (typeof value === 'object' && !Array.isArray(value)) {
      const isExpanded = expandedSections.has(`${key}-${depth}`);
      return (
        <div style={{ marginLeft: indent }}>
          <div 
            className="flex items-center cursor-pointer hover:bg-gray-50 p-1 rounded"
            onClick={() => toggleSection(`${key}-${depth}`)}
          >
            {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            <span className="text-blue-600 ml-1">"{key}"</span>: {"{"}
          </div>
          {isExpanded && (
            <div>
              {Object.entries(value).map(([k, v]) => (
                <div key={k}>
                  {renderJsonValue(v, k, depth + 1)}
                </div>
              ))}
              <div style={{ marginLeft: indent }}>{"}"}</div>
            </div>
          )}
        </div>
      );
    }
    
    if (Array.isArray(value)) {
      const isExpanded = expandedSections.has(`${key}-${depth}`);
      return (
        <div style={{ marginLeft: indent }}>
          <div 
            className="flex items-center cursor-pointer hover:bg-gray-50 p-1 rounded"
            onClick={() => toggleSection(`${key}-${depth}`)}
          >
            {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            <span className="text-blue-600 ml-1">"{key}"</span>: [
            <Badge variant="secondary" className="ml-2 text-xs">
              {value.length} items
            </Badge>
          </div>
          {isExpanded && (
            <div>
              {value.slice(0, 3).map((item, index) => (
                <div key={index}>
                  {renderJsonValue(item, `[${index}]`, depth + 1)}
                </div>
              ))}
              {value.length > 3 && (
                <div style={{ marginLeft: (depth + 1) * 20 }} className="text-gray-500 italic">
                  ... and {value.length - 3} more items
                </div>
              )}
              <div style={{ marginLeft: indent }}>]</div>
            </div>
          )}
        </div>
      );
    }
    
    return (
      <div style={{ marginLeft: indent }}>
        <span className="text-blue-600">"{key}"</span>: 
        <span className={typeof value === 'string' ? 'text-green-600' : 'text-purple-600'}>
          {typeof value === 'string' ? `"${value}"` : String(value)}
        </span>
      </div>
    );
  };

  if (!isVisible) {
    return (
      <Button
        onClick={onToggle}
        variant="outline"
        size="sm"
        className="fixed bottom-4 right-4 z-50"
      >
        <Database className="w-4 h-4 mr-2" />
        Debug Dashboard
      </Button>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-4xl max-h-[90vh] overflow-hidden">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg flex items-center">
              <Database className="w-5 h-5 mr-2" />
              Dashboard Data Structure
            </CardTitle>
            <Button onClick={onToggle} variant="outline" size="sm">
              Close
            </Button>
          </div>
        </CardHeader>
        <CardContent className="overflow-y-auto max-h-[calc(90vh-120px)]">
          {/* Validation Summary */}
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold mb-3 flex items-center">
              {validation.isValid ? (
                <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
              ) : (
                <AlertTriangle className="w-5 h-5 text-red-500 mr-2" />
              )}
              Data Validation Summary
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-medium text-sm mb-2">Status</h4>
                <Badge variant={validation.isValid ? "default" : "destructive"}>
                  {validation.isValid ? "Valid" : "Issues Found"}
                </Badge>
              </div>
              
              {validation.missingFields.length > 0 && (
                <div>
                  <h4 className="font-medium text-sm mb-2">Missing Fields</h4>
                  <div className="space-y-1">
                    {validation.missingFields.map((field, index) => (
                      <Badge key={index} variant="destructive" className="text-xs mr-1">
                        {field}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
              
              {validation.warnings.length > 0 && (
                <div className="md:col-span-2">
                  <h4 className="font-medium text-sm mb-2">Warnings</h4>
                  <div className="space-y-1">
                    {validation.warnings.map((warning, index) => (
                      <Badge key={index} variant="secondary" className="text-xs mr-1">
                        {warning}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Data Structure */}
          <div className="mb-6">
            <h3 className="font-semibold mb-3">Complete Data Structure</h3>
            <div className="bg-gray-900 text-gray-100 p-4 rounded-lg font-mono text-sm overflow-x-auto">
              {data ? (
                <div>
                  <div className="text-gray-400 mb-2">// Dashboard KPIs Response</div>
                  {Object.entries(data).map(([key, value]) => (
                    <div key={key}>
                      {renderJsonValue(value, key)}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-red-400">No data available</div>
              )}
            </div>
          </div>

          {/* Available Charts */}
          <div className="mb-6">
            <h3 className="font-semibold mb-3">Available Chart Data</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[
                { name: "Monthly Trends", field: "monthly_trends", available: !!data?.monthly_trends?.length },
                { name: "Event Types", field: "event_type_distribution", available: !!data?.event_type_distribution?.length },
                { name: "Severity Levels", field: "incident_severity_distribution", available: !!data?.incident_severity_distribution?.length },
                { name: "Branch Performance", field: "branch_performance_analysis", available: !!data?.branch_performance_analysis?.length },
                { name: "Repeat Locations", field: "repeat_locations", available: !!data?.repeat_locations?.length },
                { name: "Safety Trends", field: "safety_performance_trends", available: !!data?.safety_performance_trends?.length },
                { name: "Time Analysis", field: "time_based_analysis", available: !!data?.time_based_analysis },
                { name: "Operational Impact", field: "operational_impact_analysis", available: !!data?.operational_impact_analysis },
                { name: "Weather Impact", field: "augmented_kpis.weather_impact_analysis", available: !!data?.augmented_kpis?.weather_impact_analysis?.length },
                { name: "Experience Analysis", field: "augmented_kpis.experience_level_analysis", available: !!data?.augmented_kpis?.experience_level_analysis }
              ].map((chart, index) => (
                <div key={index} className="flex items-center justify-between p-3 border rounded">
                  <span className="font-medium">{chart.name}</span>
                  <div className="flex items-center">
                    <Badge variant={chart.available ? "default" : "secondary"}>
                      {chart.available ? "Available" : "Missing"}
                    </Badge>
                    {chart.available ? (
                      <CheckCircle className="w-4 h-4 text-green-500 ml-2" />
                    ) : (
                      <AlertTriangle className="w-4 h-4 text-yellow-500 ml-2" />
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Raw JSON */}
          <div>
            <h3 className="font-semibold mb-3">Raw JSON Response</h3>
            <div className="bg-gray-100 p-4 rounded-lg">
              <pre className="text-xs overflow-x-auto whitespace-pre-wrap">
                {JSON.stringify(data, null, 2)}
              </pre>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
