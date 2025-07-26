/**
 * Insights Test Panel
 * Component for testing insights functionality
 */

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { useGenerateInsights, useGenerateMoreInsights, useGenerateUnifiedInsights, useInsightFeedback } from "@/hooks/useApi";
import { SchemaType, AIInsight } from "@/types/api";
import { useToast } from "@/hooks/use-toast";
import { Sparkles, Database, Zap, RefreshCw, TestTube } from "lucide-react";

export const InsightsTestPanel = () => {
  const [selectedSchema, setSelectedSchema] = useState<SchemaType>("srs");
  const [insights, setInsights] = useState<AIInsight[]>([]);
  const [testResults, setTestResults] = useState<string[]>([]);
  const { toast } = useToast();

  // API hooks
  const generateInsightsMutation = useGenerateInsights();
  const generateMoreInsightsMutation = useGenerateMoreInsights();
  const generateUnifiedInsightsMutation = useGenerateUnifiedInsights();
  const submitFeedbackMutation = useInsightFeedback();

  const addTestResult = (result: string) => {
    setTestResults(prev => [...prev, `${new Date().toLocaleTimeString()}: ${result}`]);
  };

  const clearResults = () => {
    setTestResults([]);
    setInsights([]);
  };

  // Test 1: Generate insights for selected schema
  const testGenerateInsights = async () => {
    try {
      addTestResult(`Testing insights generation for ${selectedSchema}...`);
      const response = await generateInsightsMutation.mutateAsync(selectedSchema);
      setInsights(response.insights || []);
      addTestResult(`✅ Generated ${response.insights?.length || 0} insights for ${selectedSchema}`);
      toast({
        title: "Test Passed",
        description: `Generated insights for ${selectedSchema}`,
      });
    } catch (error: any) {
      addTestResult(`❌ Failed to generate insights: ${error.message}`);
      toast({
        title: "Test Failed",
        description: error.message,
        variant: "destructive",
      });
    }
  };

  // Test 2: Generate more insights
  const testGenerateMoreInsights = async () => {
    try {
      addTestResult(`Testing generate more insights for ${selectedSchema}...`);
      const response = await generateMoreInsightsMutation.mutateAsync({ 
        schemaType: selectedSchema, 
        count: 3 
      });
      setInsights(prev => [...prev, ...(response.insights || [])]);
      addTestResult(`✅ Generated ${response.insights?.length || 0} additional insights`);
      toast({
        title: "Test Passed",
        description: "Generated additional insights",
      });
    } catch (error: any) {
      addTestResult(`❌ Failed to generate more insights: ${error.message}`);
      toast({
        title: "Test Failed",
        description: error.message,
        variant: "destructive",
      });
    }
  };

  // Test 3: Generate unified insights
  const testGenerateUnifiedInsights = async () => {
    try {
      addTestResult("Testing unified insights generation...");
      const response = await generateUnifiedInsightsMutation.mutateAsync();
      setInsights(response.insights || []);
      addTestResult(`✅ Generated ${response.insights?.length || 0} unified insights`);
      toast({
        title: "Test Passed",
        description: "Generated unified insights",
      });
    } catch (error: any) {
      addTestResult(`❌ Failed to generate unified insights: ${error.message}`);
      toast({
        title: "Test Failed",
        description: error.message,
        variant: "destructive",
      });
    }
  };

  // Test 4: Submit feedback
  const testSubmitFeedback = async () => {
    if (insights.length === 0) {
      addTestResult("❌ No insights available for feedback test");
      return;
    }

    try {
      const insight = insights[0];
      addTestResult("Testing feedback submission...");
      await submitFeedbackMutation.mutateAsync({
        schema_type: selectedSchema,
        insight_text: insight.text,
        feedback: 'positive'
      });
      addTestResult("✅ Successfully submitted positive feedback");
      toast({
        title: "Test Passed",
        description: "Feedback submitted successfully",
      });
    } catch (error: any) {
      addTestResult(`❌ Failed to submit feedback: ${error.message}`);
      toast({
        title: "Test Failed",
        description: error.message,
        variant: "destructive",
      });
    }
  };

  // Run all tests
  const runAllTests = async () => {
    clearResults();
    addTestResult("🧪 Starting comprehensive insights test suite...");
    
    await testGenerateInsights();
    await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second
    
    await testGenerateMoreInsights();
    await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second
    
    await testSubmitFeedback();
    await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second
    
    await testGenerateUnifiedInsights();
    
    addTestResult("🎉 Test suite completed!");
  };

  const isLoading = generateInsightsMutation.isPending || 
                   generateMoreInsightsMutation.isPending || 
                   generateUnifiedInsightsMutation.isPending || 
                   submitFeedbackMutation.isPending;

  return (
    <div className="space-y-6 p-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TestTube className="h-5 w-5" />
            AI Insights Test Panel
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Schema Selection */}
          <div>
            <label className="text-sm font-medium mb-2 block">Test Schema</label>
            <Select value={selectedSchema} onValueChange={setSelectedSchema}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select Schema" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="srs">SRS</SelectItem>
                <SelectItem value="ei_tech">EI Tech</SelectItem>
                <SelectItem value="ni_tct">NI TCT</SelectItem>
                <SelectItem value="ni_tct_augmented">NI TCT Augmented</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Test Buttons */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            <Button
              onClick={testGenerateInsights}
              disabled={isLoading}
              className="flex items-center gap-2"
              size="sm"
            >
              {isLoading ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Database className="h-4 w-4" />}
              Generate
            </Button>
            
            <Button
              onClick={testGenerateMoreInsights}
              disabled={isLoading}
              variant="outline"
              size="sm"
            >
              {isLoading ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
              More
            </Button>
            
            <Button
              onClick={testGenerateUnifiedInsights}
              disabled={isLoading}
              variant="outline"
              size="sm"
            >
              {isLoading ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Zap className="h-4 w-4" />}
              Unified
            </Button>
            
            <Button
              onClick={testSubmitFeedback}
              disabled={isLoading || insights.length === 0}
              variant="outline"
              size="sm"
            >
              Feedback
            </Button>
          </div>

          {/* Run All Tests */}
          <div className="flex gap-2">
            <Button
              onClick={runAllTests}
              disabled={isLoading}
              className="flex-1"
            >
              {isLoading ? <RefreshCw className="h-4 w-4 animate-spin mr-2" /> : <TestTube className="h-4 w-4 mr-2" />}
              Run All Tests
            </Button>
            <Button onClick={clearResults} variant="outline">
              Clear
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Test Results */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            Test Results
            <Badge variant="secondary">{testResults.length} results</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Textarea
            value={testResults.join('\n')}
            readOnly
            className="min-h-[200px] font-mono text-sm"
            placeholder="Test results will appear here..."
          />
        </CardContent>
      </Card>

      {/* Generated Insights */}
      {insights.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              Generated Insights
              <Badge variant="secondary">{insights.length} insights</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-[400px] overflow-y-auto">
              {insights.map((insight, index) => (
                <div key={insight.id} className="p-3 border rounded-lg">
                  <div className="flex items-start gap-2">
                    <Badge variant="outline" className="text-xs">
                      {index + 1}
                    </Badge>
                    <p className="text-sm flex-1">{insight.text}</p>
                  </div>
                  {insight.category && (
                    <Badge variant="secondary" className="mt-2 text-xs">
                      {insight.category}
                    </Badge>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
