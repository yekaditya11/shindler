import { useState } from "react";
import { X, ThumbsUp, ThumbsDown, Trash2, Maximize2, Download } from "lucide-react";
import jsPDF from "jspdf";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface AIFloatingIconProps {
  onToggle: () => void;
  isOpen: boolean;
  isInline?: boolean;
}

export const AIFloatingIcon = ({ onToggle, isOpen, isInline = false }: AIFloatingIconProps) => {
  const containerClass = isInline 
    ? "relative" 
    : "fixed bottom-6 right-6 z-50";
  
  return (
    <div className={containerClass}>
      <Button
        onClick={onToggle}
        className={cn(
          "w-8 h-8 rounded-full relative overflow-hidden transition-all duration-500 transform hover:scale-110 border-0 p-0",
          "bg-gradient-to-br from-primary via-primary-light to-primary-lighter",
          "shadow-[0_0_30px_rgba(59,130,246,0.5)] hover:shadow-[0_0_40px_rgba(59,130,246,0.7)]",
          isOpen && "bg-gradient-to-br from-destructive to-destructive/80"
        )}
      >
        {/* Animated background circles */}
        <div className="absolute inset-0 rounded-full">
          <div className="absolute inset-2 rounded-full bg-white/10 animate-pulse"></div>
          <div className="absolute inset-3 rounded-full bg-white/20 animate-ping"></div>
        </div>
        
        {/* Icon */}
        <div className="relative z-10 flex items-center justify-center h-full">
          {isOpen ? (
            <X className="h-4 w-4 text-white drop-shadow-lg" />
          ) : (
            <div className="w-2 h-2 rounded-full bg-white/90 shadow-lg"></div>
          )}
        </div>
        
        {/* Ripple effect on hover */}
        <div className="absolute inset-0 rounded-full opacity-0 hover:opacity-100 transition-opacity duration-300">
          <div className="absolute inset-0 rounded-full bg-white/10 animate-ping"></div>
        </div>
      </Button>
    </div>
  );
};

interface SimpleInsightsProps {
  insights: Array<{
    id: string;
    text: string;
    liked?: boolean;
    disliked?: boolean;
  }>;
  isOpen: boolean;
  onClose: () => void;
  onInsightAction: (id: string, action: 'like' | 'dislike' | 'delete') => void;
}

export const SimpleInsights = ({ insights, isOpen, onClose, onInsightAction }: SimpleInsightsProps) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [hoveredInsight, setHoveredInsight] = useState<string | null>(null);
  
  if (!isOpen) return null;

  const handleAction = (id: string, action: 'like' | 'dislike' | 'delete') => {
    onInsightAction(id, action);
  };

  const downloadPDF = () => {
    const doc = new jsPDF();
    
    // Add title
    doc.setFontSize(20);
    doc.text("AI Insights Report", 20, 30);
    
    // Add date
    doc.setFontSize(12);
    doc.text(`Generated on: ${new Date().toLocaleDateString()}`, 20, 45);
    
    // Add insights
    let yPosition = 65;
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
      
      // Add insight text (with text wrapping)
      doc.setFont(undefined, 'normal');
      const textLines = doc.splitTextToSize(insight.text, 170);
      doc.text(textLines, 20, yPosition + 10);
      
      yPosition += 10 + (textLines.length * 7) + 10;
    });
    
    // Save the PDF
    doc.save("ai-insights-report.pdf");
  };

  return (
    <div 
      className="fixed inset-0 bg-black/50 z-40 flex items-center justify-center p-3 md:p-4"
      onClick={onClose}
    >
      <Card 
        className={cn(
          "w-full overflow-hidden shadow-hover animate-scale-in transition-all duration-300",
          isExpanded 
            ? "max-w-6xl max-h-[95vh]" 
            : "max-w-xs sm:max-w-md md:max-w-2xl max-h-[90vh] md:max-h-[80vh]"
        )}
        onClick={(e) => e.stopPropagation()}
      >
        <CardContent className="p-4 md:p-6">
          <div className="flex items-center justify-between mb-4 md:mb-6">
            <h2 className="text-lg md:text-xl font-bold text-foreground">AI Insights</h2>
            <div className="flex items-center gap-2">
              {/* Expand/Collapse Button */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsExpanded(!isExpanded)}
                className="hover:bg-muted h-8 w-8 p-0"
                title={isExpanded ? "Collapse" : "Expand"}
              >
                <Maximize2 className="h-4 w-4" />
              </Button>
              
              {/* Download PDF Button */}
              <Button
                variant="ghost"
                size="sm"
                onClick={downloadPDF}
                className="hover:bg-muted h-8 w-8 p-0"
                title="Download as PDF"
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
          
          <div className={cn(
            "space-y-3 md:space-y-4 overflow-y-auto",
            isExpanded ? "max-h-[75vh]" : "max-h-[60vh] md:max-h-[60vh]"
          )}>
            <div className={cn(
              "space-y-2 md:space-y-3",
              isExpanded && "grid grid-cols-1 lg:grid-cols-2 gap-4"
            )}>
              {insights.map((insight, index) => (
                <div 
                  key={insight.id} 
                  className={cn(
                    "flex items-start gap-2 md:gap-3 p-2 md:p-3 rounded-lg hover:bg-muted/50 transition-colors",
                    isExpanded && "border border-border"
                  )}
                  onMouseEnter={() => setHoveredInsight(insight.id)}
                  onMouseLeave={() => setHoveredInsight(null)}
                >
                  <div className={cn(
                    "w-2 h-2 rounded-full bg-primary flex-shrink-0",
                    isExpanded ? "mt-2" : "mt-1 md:mt-2"
                  )}></div>
                  <div className="flex-1">
                    {isExpanded && (
                      <div className="text-xs text-muted-foreground mb-1">
                        Insight #{index + 1}
                      </div>
                    )}
                    <p className={cn(
                      "text-foreground leading-relaxed",
                      isExpanded ? "text-sm md:text-base" : "text-sm md:text-base"
                    )}>
                      {insight.text}
                    </p>
                  </div>
                  
                  {hoveredInsight === insight.id && (
                    <div className="flex items-center gap-1 animate-fade-in">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleAction(insight.id, 'like')}
                        className="p-1 h-auto hover:bg-muted"
                      >
                        <ThumbsUp className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleAction(insight.id, 'dislike')}
                        className="p-1 h-auto hover:bg-muted"
                      >
                        <ThumbsDown className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleAction(insight.id, 'delete')}
                        className="p-1 h-auto hover:bg-muted"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};