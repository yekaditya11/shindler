import { useState } from "react";
import { ThumbsUp, ThumbsDown, Trash2, Plus, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface Insight {
  id: string;
  text: string;
  category: string;
  confidence: number;
  liked?: boolean;
  disliked?: boolean;
}

interface InsightsListProps {
  insights: Insight[];
  onInsightAction: (id: string, action: 'like' | 'dislike' | 'delete') => void;
  onGenerateMore: () => void;
}

export const InsightsList = ({ insights, onInsightAction, onGenerateMore }: InsightsListProps) => {
  const [hoveredInsight, setHoveredInsight] = useState<string | null>(null);

  const handleAction = (id: string, action: 'like' | 'dislike' | 'delete') => {
    onInsightAction(id, action);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-primary" />
          <h2 className="text-2xl font-bold">AI Insights</h2>
        </div>
        <Badge variant="secondary" className="bg-gradient-accent">
          {insights.length} insights found
        </Badge>
      </div>

      <div className="space-y-3">
        {insights.map((insight, index) => (
          <Card
            key={insight.id}
            className="transition-all duration-200 hover:shadow-card cursor-pointer"
            onMouseEnter={() => setHoveredInsight(insight.id)}
            onMouseLeave={() => setHoveredInsight(null)}
          >
            <CardContent className="p-4">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 space-y-2">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-primary"></div>
                    <Badge variant="outline" className="text-xs">
                      {insight.category}
                    </Badge>
                    <Badge 
                      variant="secondary" 
                      className={`text-xs ${
                        insight.confidence > 80 ? 'bg-success/20 text-success' : 
                        insight.confidence > 60 ? 'bg-yellow-500/20 text-yellow-700' : 
                        'bg-destructive/20 text-destructive'
                      }`}
                    >
                      {insight.confidence}% confidence
                    </Badge>
                  </div>
                  <p className="text-foreground leading-relaxed">{insight.text}</p>
                </div>

                {hoveredInsight === insight.id && (
                  <div className="flex items-center gap-1 animate-fade-in">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleAction(insight.id, 'like')}
                      className={`transition-colors ${
                        insight.liked ? 'text-success bg-success/10' : 'hover:text-success'
                      }`}
                    >
                      <ThumbsUp className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleAction(insight.id, 'dislike')}
                      className={`transition-colors ${
                        insight.disliked ? 'text-destructive bg-destructive/10' : 'hover:text-destructive'
                      }`}
                    >
                      <ThumbsDown className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleAction(insight.id, 'delete')}
                      className="hover:text-destructive"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}

        {/* Generate More Card */}
        <Card 
          className="border-dashed border-2 hover:border-primary/50 transition-all duration-200 cursor-pointer group"
          onClick={onGenerateMore}
        >
          <CardContent className="p-4">
            <div className="flex items-center justify-center gap-2 text-muted-foreground group-hover:text-primary transition-colors">
              <Plus className="h-4 w-4" />
              <span className="font-medium">Generate More Insights</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};