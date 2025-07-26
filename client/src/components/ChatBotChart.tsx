import React, { useState } from 'react';
import ReactECharts from 'echarts-for-react';
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Save, Plus } from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";

interface ChatBotChartProps {
  chartData: Record<string, unknown>;
  className?: string;
  width?: string | number;
  height?: string | number;
  showSaveButton?: boolean;
  onSaveToDashboard?: (chartData: Record<string, unknown>, title: string, description: string) => Promise<void>;
}

export const ChatBotChart: React.FC<ChatBotChartProps> = ({ 
  chartData, 
  className, 
  width = '100%',
  height = '300px',
  showSaveButton = false,
  onSaveToDashboard
}) => {
  const [isSaveDialogOpen, setIsSaveDialogOpen] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const { toast } = useToast();
  // Default chart options if no data provided
  const defaultOptions = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      data: ['No Data']
    },
    series: [
      {
        name: 'No Data',
        type: 'pie',
        radius: '50%',
        data: [
          {
            value: 0,
            name: 'No Data'
          }
        ]
      }
    ]
  };

  // Use provided chart data or default
  const options = chartData && Object.keys(chartData).length > 0 ? chartData : defaultOptions;

  const handleSaveToDashboard = async () => {
    if (!title.trim()) {
      toast({
        title: "Error",
        description: "Please enter a title for the chart",
        variant: "destructive",
      });
      return;
    }

    if (!onSaveToDashboard) {
      toast({
        title: "Error",
        description: "Save functionality not available",
        variant: "destructive",
      });
      return;
    }

    setIsSaving(true);
    try {
      await onSaveToDashboard(chartData, title.trim(), description.trim());
      setIsSaveDialogOpen(false);
      setTitle('');
      setDescription('');
      toast({
        title: "Success",
        description: "Chart saved to dashboard successfully!",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save chart to dashboard",
        variant: "destructive",
      });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div 
      className={cn(
        "bg-white rounded-lg border border-gray-200 overflow-hidden",
        className
      )}
      style={{ width: typeof width === 'number' ? `${width}px` : width }}
    >
      <div className="p-3 bg-gray-50 border-b border-gray-200 flex items-center justify-between">
        <h4 className="text-sm font-medium text-gray-700">Chart Visualization</h4>
        {showSaveButton && (
          <Dialog open={isSaveDialogOpen} onOpenChange={setIsSaveDialogOpen}>
            <DialogTrigger asChild>
              <Button
                size="sm"
                variant="outline"
                className="h-7 px-2 text-xs"
                onClick={(e) => {
                  e.stopPropagation();
                  setIsSaveDialogOpen(true);
                }}
              >
                <Save className="h-3 w-3 mr-1" />
                Save to Dashboard
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
              <DialogHeader>
                <DialogTitle>Save Chart to Dashboard</DialogTitle>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid gap-2">
                  <Label htmlFor="title">Chart Title *</Label>
                  <Input
                    id="title"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="Enter chart title..."
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="description">Description (Optional)</Label>
                  <Textarea
                    id="description"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Enter chart description..."
                    rows={3}
                  />
                </div>
              </div>
              <div className="flex justify-end gap-2">
                <Button
                  variant="outline"
                  onClick={() => setIsSaveDialogOpen(false)}
                  disabled={isSaving}
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleSaveToDashboard}
                  disabled={isSaving || !title.trim()}
                >
                  {isSaving ? "Saving..." : "Save Chart"}
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        )}
      </div>
      <div className="p-4">
        <ReactECharts
          option={options}
          style={{ 
            height: typeof height === 'number' ? `${height}px` : height, 
            width: '100%' 
          }}
          opts={{ renderer: 'canvas' }}
        />
      </div>
    </div>
  );
}; 