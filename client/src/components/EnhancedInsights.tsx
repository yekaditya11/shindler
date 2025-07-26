/**
 * Enhanced AI Insights Component
 * Supports schema-specific insights generation and unified insights
 */

import { useState } from "react";
import { X, ThumbsUp, ThumbsDown, Trash2, Maximize2, Download, Sparkles, RefreshCw, Database, Zap } from "lucide-react";
import jsPDF from "jspdf";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { cn } from "@/lib/utils";
import { SchemaType, AIInsight } from "@/types/api";

interface EnhancedInsightsProps {
  insights: AIInsight[];
  isOpen: boolean;
  onClose: () => void;
  onInsightAction: (id: string, action: 'like' | 'dislike' | 'delete') => void;
  onGenerateInsights: (schemaType: SchemaType) => void;
  onGenerateMoreInsights: (schemaType: SchemaType, count?: number) => void;
  onGenerateUnifiedInsights: () => void;
  selectedSchema: SchemaType;
  onSchemaChange: (schema: SchemaType) => void;
  isGenerating: boolean;
}

export const EnhancedInsights = ({
  insights,
  isOpen,
  onClose,
  onInsightAction,
  onGenerateInsights,
  onGenerateMoreInsights,
  onGenerateUnifiedInsights,
  selectedSchema,
  onSchemaChange,
  isGenerating
}: EnhancedInsightsProps) => {
  const [hoveredInsight, setHoveredInsight] = useState<string | null>(null);
  const [isExpanded, setIsExpanded] = useState(false);

  if (!isOpen) return null;

  const handleAction = (id: string, action: 'like' | 'dislike' | 'delete') => {
    onInsightAction(id, action);
  };

  const downloadPDF = () => {
    const doc = new jsPDF();
    
    // Add title
    doc.setFontSize(20);
    doc.text("AI Insights Report", 20, 30);
    
    // Add metadata
    doc.setFontSize(12);
    doc.text(`Generated on: ${new Date().toLocaleDateString()}`, 20, 45);
    doc.text(`Schema: ${selectedSchema.toUpperCase()}`, 20, 55);
    doc.text(`Total Insights: ${insights.length}`, 20, 65);
    
    // Add insights
    let yPosition = 85;
    doc.setFontSize(14);
    
    insights.forEach((insight, index) => {
      // Check if we need a new page
      if (yPosition > 260) {
        doc.addPage();
        yPosition = 30;
      }
      
      // Add insight number
      doc.setFont(undefined, 'bold');
      doc.text(`Insight ${index + 1}:`, 20, yPosition);
      
      // Add insight text (wrap text)
      doc.setFont(undefined, 'normal');
      const splitText = doc.splitTextToSize(insight.text, 170);
      doc.text(splitText, 20, yPosition + 10);
      
      yPosition += 10 + (splitText.length * 5) + 10;
    });
    
    doc.save(`ai-insights-${selectedSchema}-${new Date().toISOString().split('T')[0]}.pdf`);
  };

  const getSchemaDisplayName = (schema: SchemaType) => {
    const names = {
      'srs': 'SRS',
      'ei_tech': 'EI Tech',
      'ni_tct': 'NI TCT',
      'ni_tct_augmented': 'NI TCT Augmented'
    };
    return names[schema] || schema.toUpperCase();
  };

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <Card className={cn(
        "w-full transition-all duration-300 shadow-2xl border-0",
        isExpanded 
          ? "max-w-7xl h-[95vh]" 
          : "max-w-2xl max-h-[85vh]"
      )}>
        <CardHeader className="pb-3 border-b bg-gradient-to-r from-primary/5 to-primary-light/5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-primary-light flex items-center justify-center">
                <Sparkles className="h-5 w-5 text-white" />
              </div>
              <div>
                <CardTitle className="text-xl flex items-center gap-2">
                  AI Insights
                  <Badge variant="secondary" className="bg-gradient-accent">
                    {insights.length} insights
                  </Badge>
                </CardTitle>
                <p className="text-sm text-muted-foreground">
                  Schema: {getSchemaDisplayName(selectedSchema)}
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              {/* Expand/Collapse Button */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsExpanded(!isExpanded)}
                className="hover:bg-primary/10 h-8 w-8 p-0"
              >
                <Maximize2 className="h-4 w-4" />
              </Button>
              
              {/* Download PDF Button */}
              <Button
                variant="ghost"
                size="sm"
                onClick={downloadPDF}
                disabled={insights.length === 0}
                className="hover:bg-primary/10 h-8 w-8 p-0"
              >
                <Download className="h-4 w-4" />
              </Button>
              
              {/* Close Button */}
              <Button
                variant="ghost"
                size="sm"
                onClick={onClose}
                className="hover:bg-destructive/10 hover:text-destructive h-8 w-8 p-0"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>

        <CardContent className="p-6">
          {/* Controls Section */}
          <div className="mb-6 space-y-4">
            {/* Schema Selection and Generation */}
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="flex-1">
                <label className="text-sm font-medium mb-2 block">Select Schema</label>
                <Select value={selectedSchema} onValueChange={onSchemaChange}>
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
              
              <div className="flex gap-2 sm:items-end">
                <Button
                  onClick={() => onGenerateInsights(selectedSchema)}
                  disabled={isGenerating}
                  className="flex items-center gap-2"
                >
                  {isGenerating ? (
                    <RefreshCw className="h-4 w-4 animate-spin" />
                  ) : (
                    <Database className="h-4 w-4" />
                  )}
                  Generate for {getSchemaDisplayName(selectedSchema)}
                </Button>
                
                <Button
                  onClick={onGenerateUnifiedInsights}
                  disabled={isGenerating}
                  variant="outline"
                  className="flex items-center gap-2"
                >
                  {isGenerating ? (
                    <RefreshCw className="h-4 w-4 animate-spin" />
                  ) : (
                    <Zap className="h-4 w-4" />
                  )}
                  Unified
                </Button>
              </div>
            </div>

            {/* Status */}
            {isGenerating && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <RefreshCw className="h-4 w-4 animate-spin" />
                Generating insights...
              </div>
            )}
          </div>

          {/* Insights List */}
          <div className={cn(
            "space-y-3 overflow-y-auto",
            isExpanded ? "max-h-[calc(95vh-300px)]" : "max-h-[calc(85vh-250px)]"
          )}>
            {insights.length === 0 ? (
              <div className="text-center py-12">
                <Sparkles className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium text-muted-foreground mb-2">No insights yet</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Generate insights for the selected schema to get started
                </p>
                <Button
                  onClick={() => onGenerateInsights(selectedSchema)}
                  disabled={isGenerating}
                  className="flex items-center gap-2"
                >
                  {isGenerating ? (
                    <RefreshCw className="h-4 w-4 animate-spin" />
                  ) : (
                    <Sparkles className="h-4 w-4" />
                  )}
                  Generate Insights
                </Button>
              </div>
            ) : (
              <div className={cn(
                "space-y-2 md:space-y-3",
                isExpanded && "grid grid-cols-1 lg:grid-cols-2 gap-4"
              )}>
                {insights.map((insight, index) => (
                  <div 
                    key={insight.id} 
                    className={cn(
                      "flex items-start gap-2 md:gap-3 p-3 md:p-4 rounded-lg hover:bg-muted/50 transition-colors border",
                      isExpanded && "border border-border"
                    )}
                    onMouseEnter={() => setHoveredInsight(insight.id)}
                    onMouseLeave={() => setHoveredInsight(null)}
                  >
                    <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mt-1">
                      <span className="text-xs font-medium text-primary">{index + 1}</span>
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <p className="text-sm leading-relaxed text-foreground">
                        {insight.text}
                      </p>
                      
                      {insight.category && (
                        <Badge variant="outline" className="mt-2 text-xs">
                          {insight.category}
                        </Badge>
                      )}
                    </div>
                    
                    {hoveredInsight === insight.id && (
                      <div className="flex items-center gap-1 animate-fade-in">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleAction(insight.id, 'like')}
                          className={cn(
                            "transition-colors h-8 w-8 p-0",
                            insight.liked ? 'text-success bg-success/10' : 'hover:text-success'
                          )}
                        >
                          <ThumbsUp className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleAction(insight.id, 'dislike')}
                          className={cn(
                            "transition-colors h-8 w-8 p-0",
                            insight.disliked ? 'text-destructive bg-destructive/10' : 'hover:text-destructive'
                          )}
                        >
                          <ThumbsDown className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleAction(insight.id, 'delete')}
                          className="hover:text-destructive h-8 w-8 p-0"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    )}
                  </div>
                ))}

                {/* Generate More Button */}
                {insights.length > 0 && (
                  <div className="flex justify-center pt-4">
                    <Button
                      onClick={() => onGenerateMoreInsights(selectedSchema, 5)}
                      disabled={isGenerating}
                      variant="outline"
                      className="flex items-center gap-2"
                    >
                      {isGenerating ? (
                        <RefreshCw className="h-4 w-4 animate-spin" />
                      ) : (
                        <Sparkles className="h-4 w-4" />
                      )}
                      Generate 5 More Insights
                    </Button>
                  </div>
                )}
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
