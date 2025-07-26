/**
 * Simple Bullet Point Insights Component
 * Displays insights as clean bullet points with hover interactions for feedback
 */

import { useState } from "react";
import { X, Loader2, ThumbsUp, ThumbsDown, Trash2, Maximize2, Minimize2, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import jsPDF from "jspdf";

interface SimpleBulletInsightsProps {
  insights: Array<{
    id: string;
    text: string;
    liked?: boolean;
    disliked?: boolean;
  }>;
  isOpen: boolean;
  onClose: () => void;
  isLoading?: boolean;
  isGeneratingMore?: boolean;
  onInsightAction?: (id: string, action: 'like' | 'dislike' | 'delete') => void;
  onGenerateMore?: () => void;
}

export const SimpleBulletInsights = ({
  insights,
  isOpen,
  onClose,
  isLoading = false,
  isGeneratingMore = false,
  onInsightAction,
  onGenerateMore
}: SimpleBulletInsightsProps) => {
  const [hoveredInsight, setHoveredInsight] = useState<string | null>(null);
  const [isExpanded, setIsExpanded] = useState<boolean>(false);

  if (!isOpen) return null;

  // PDF Export function
  const downloadPDF = () => {
    const doc = new jsPDF();

    // Add title
    doc.setFontSize(20);
    doc.text("AI Insights Report", 20, 30);

    // Add metadata
    doc.setFontSize(12);
    doc.text(`Generated on: ${new Date().toLocaleDateString()}`, 20, 45);
    doc.text(`Total Insights: ${insights.length}`, 20, 55);

    // Add insights
    let yPosition = 75;
    doc.setFontSize(14);

    insights.forEach((insight, index) => {
      // Check if we need a new page
      if (yPosition > 260) {
        doc.addPage();
        yPosition = 30;
      }

      // Add insight number
      doc.setFont(undefined, 'bold');
      doc.text(`${index + 1}.`, 20, yPosition);

      // Add insight text (wrap text)
      doc.setFont(undefined, 'normal');
      const splitText = doc.splitTextToSize(insight.text, 170);
      doc.text(splitText, 30, yPosition);

      yPosition += 10 + (splitText.length * 5) + 5;
    });

    doc.save(`ai-insights-${new Date().toISOString().split('T')[0]}.pdf`);
  };

  // Debug logging
  console.log('SimpleBulletInsights render:', {
    isOpen,
    isLoading,
    insightsCount: insights.length,
    firstInsight: insights[0]?.text?.substring(0, 50) + '...'
  });

  const handleAction = (id: string, action: 'like' | 'dislike' | 'delete') => {
    if (onInsightAction) {
      onInsightAction(id, action);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 z-[70] flex items-center justify-center p-4">
      <div className={`bg-white rounded-lg shadow-xl w-full transition-all duration-300 flex flex-col ${
        isExpanded
          ? "max-w-7xl h-[95vh]"
          : "max-w-4xl max-h-[80vh]"
      }`}>
        {/* Simple Header with Controls */}
        <div className="flex items-center justify-between p-4 border-b bg-gray-50 flex-shrink-0">
          <div>
            <h2 className="text-lg font-semibold text-gray-800">AI Insights</h2>
      
          </div>

          <div className="flex items-center gap-2">
            {/* Expand/Collapse Button */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
              className="h-8 w-8 p-0 hover:bg-gray-200"
              title={isExpanded ? "Collapse" : "Expand"}
            >
              {isExpanded ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
            </Button>

            {/* PDF Export Button */}
            <Button
              variant="ghost"
              size="sm"
              onClick={downloadPDF}
              disabled={insights.length === 0}
              className="h-8 w-8 p-0 hover:bg-gray-200"
              title="Export as PDF"
            >
              <Download className="h-4 w-4" />
            </Button>

            {/* Close Button */}
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="h-8 w-8 p-0 hover:bg-red-100 hover:text-red-600"
              title="Close"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Insights Content */}
        <div className="flex-1 p-6 overflow-y-auto">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-blue-600 mr-3" />
              <span className="text-gray-600">Generating insights...</span>
            </div>
          ) : insights.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500 mb-2">No insights generated yet</p>
              <p className="text-sm text-gray-400">Insights will appear here when generated</p>
            </div>
          ) : (
            <div className="space-y-1">
              {insights.map((insight, index) => (
                <div
                  key={insight.id}
                  className="group flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors relative"
                  onMouseEnter={() => setHoveredInsight(insight.id)}
                  onMouseLeave={() => setHoveredInsight(null)}
                >
                  <span className="text-blue-600 mt-1 text-lg font-bold">•</span>
                  <div className="flex-1">
                    <span className="text-gray-800 leading-relaxed text-sm">
                      {insight.text}
                      {/* LinkedIn-style "...Generate More" at the end of last insight */}
                      {index === insights.length - 1 && onGenerateMore && (
                        <span className="ml-2">
                          <button
                            onClick={onGenerateMore}
                            disabled={isGeneratingMore}
                            className="text-blue-600 hover:text-blue-800 font-medium text-sm transition-colors disabled:opacity-50"
                          >
                            {isGeneratingMore ? (
                              <span className="inline-flex items-center gap-1">
                                <Loader2 className="h-3 w-3 animate-spin" />
                                generating...
                              </span>
                            ) : (
                              "...Generate More"
                            )}
                          </button>
                        </span>
                      )}
                    </span>
                  </div>

                  {/* Hover Actions */}
                  {hoveredInsight === insight.id && onInsightAction && (
                    <div className="flex items-center gap-1 ml-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleAction(insight.id, 'like')}
                        className={`h-7 w-7 p-0 transition-colors ${
                          insight.liked
                            ? 'text-green-600 bg-green-100 hover:bg-green-200 border border-green-300'
                            : 'text-gray-400 hover:text-green-600 hover:bg-green-50'
                        }`}
                        title="Like this insight"
                      >
                        <ThumbsUp className={`h-3 w-3 ${insight.liked ? 'fill-current' : ''}`} />
                      </Button>

                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleAction(insight.id, 'dislike')}
                        className={`h-7 w-7 p-0 transition-colors ${
                          insight.disliked
                            ? 'text-red-600 bg-red-100 hover:bg-red-200 border border-red-300'
                            : 'text-gray-400 hover:text-red-600 hover:bg-red-50'
                        }`}
                        title="Dislike this insight"
                      >
                        <ThumbsDown className={`h-3 w-3 ${insight.disliked ? 'fill-current' : ''}`} />
                      </Button>

                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleAction(insight.id, 'delete')}
                        className="h-7 w-7 p-0 text-gray-400 hover:text-red-600 hover:bg-red-50 transition-colors"
                        title="Remove this insight"
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
