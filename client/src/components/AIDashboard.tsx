import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Trash2, Edit3, BarChart3, Calendar } from "lucide-react";
import ReactECharts from 'echarts-for-react';
import { useToast } from "@/hooks/use-toast";
import { format } from 'date-fns';
import { httpClient } from "@/lib/http-client";

interface SavedChart {
  id: string;
  title: string;
  description: string;
  timestamp: string;
  chart_data: Record<string, unknown>;
}

export const AIDashboard: React.FC = () => {
  const [savedCharts, setSavedCharts] = useState<SavedChart[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [editingChart, setEditingChart] = useState<SavedChart | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [editDescription, setEditDescription] = useState('');
  const { toast } = useToast();

  // Fetch saved charts
  const fetchSavedCharts = async () => {
    setIsLoading(true);
    try {
      const data = await httpClient.get<SavedChart[]>('/api/v1/saved-charts/get-all-charts-with-data', false);
      setSavedCharts(data || []);
    } catch (error) {
      console.error('Error fetching saved charts:', error);
      toast({
        title: "Error",
        description: "Failed to load saved charts",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Delete chart
  const handleDeleteChart = async (chartId: string) => {
    try {
      await httpClient.delete(`/api/v1/saved-charts/delete-chart/${chartId}`, false);
      setSavedCharts(prev => prev.filter(chart => chart.id !== chartId));
      toast({
        title: "Success",
        description: "Chart deleted successfully",
      });
    } catch (error) {
      console.error('Error deleting chart:', error);
      toast({
        title: "Error",
        description: "Failed to delete chart",
        variant: "destructive",
      });
    }
  };

  // Update chart
  const handleUpdateChart = async () => {
    if (!editingChart || !editTitle.trim()) return;

    try {
      await httpClient.put(`/api/v1/saved-charts/update-chart/${editingChart.id}`, {
        title: editTitle.trim(),
        description: editDescription.trim(),
      }, false);
      
      setSavedCharts(prev => prev.map(chart => 
        chart.id === editingChart.id 
          ? { ...chart, title: editTitle.trim(), description: editDescription.trim() }
          : chart
      ));
      setEditingChart(null);
      setEditTitle('');
      setEditDescription('');
      toast({
        title: "Success",
        description: "Chart updated successfully",
      });
    } catch (error) {
      console.error('Error updating chart:', error);
      toast({
        title: "Error",
        description: "Failed to update chart",
        variant: "destructive",
      });
    }
  };

  // Load charts when component mounts
  useEffect(() => {
    fetchSavedCharts();
  }, []);

  // Handle edit dialog open
  const handleEditChart = (chart: SavedChart) => {
    setEditingChart(chart);
    setEditTitle(chart.title);
    setEditDescription(chart.description);
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="space-y-6">
        <h2 className="text-xl md:text-2xl font-bold">AI Dashboard</h2>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  // Error state or no data
  if (savedCharts.length === 0) {
    return (
      <div className="space-y-6">
        <h2 className="text-xl md:text-2xl font-bold">AI Dashboard</h2>
        <div className="text-center py-12 text-gray-500">
          <BarChart3 className="h-16 w-16 mx-auto mb-6 text-gray-300" />
          <p className="text-xl font-medium mb-2">No saved charts yet</p>
          <p className="text-base">Charts saved from the chatbot will appear here</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4 md:space-y-6">
      {/* Header - Same style as CleanDashboard */}
      <div>
        <h2 className="text-xl md:text-2xl font-bold">AI Dashboard</h2>
        <p className="text-sm text-muted-foreground mt-1">
          {savedCharts.length} saved chart{savedCharts.length !== 1 ? 's' : ''}
        </p>
      </div>

      {/* Charts Grid - Same as CleanDashboard */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 md:gap-6">
        {savedCharts.map((chart) => (
          <Card key={chart.id} className="shadow-card col-span-1 group hover:shadow-hover transition-all duration-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3 flex-1">
                  <BarChart3 className="h-4 w-4 text-primary" />
                  <CardTitle className="text-lg font-semibold text-gray-800">
                    {chart.title}
                  </CardTitle>
                </div>
                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleEditChart(chart)}
                    className="h-7 w-7 p-0"
                    title="Edit chart"
                  >
                    <Edit3 className="h-3 w-3" />
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleDeleteChart(chart.id)}
                    className="h-7 w-7 p-0 text-destructive hover:text-destructive"
                    title="Delete chart"
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </div>
              
              {chart.description && (
                <p className="text-sm text-gray-600 mb-4">
                  {chart.description}
                </p>
              )}
              
              <div className="flex items-center gap-2 text-xs text-gray-500 mb-4">
                <Calendar className="h-3 w-3" />
                {format(new Date(chart.timestamp), 'MMM dd, yyyy HH:mm')}
              </div>
              
              <div className="flex justify-center">
                <div className="w-full" style={{ height: '280px' }}>
                  <ReactECharts
                    option={chart.chart_data}
                    style={{ height: '100%', width: '100%' }}
                    opts={{ renderer: 'canvas' }}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Edit Chart Dialog */}
      {editingChart && (
        <Dialog open={!!editingChart} onOpenChange={() => setEditingChart(null)}>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>Edit Chart</DialogTitle>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="edit-title">Chart Title *</Label>
                <Input
                  id="edit-title"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  placeholder="Enter chart title..."
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="edit-description">Description (Optional)</Label>
                <Textarea
                  id="edit-description"
                  value={editDescription}
                  onChange={(e) => setEditDescription(e.target.value)}
                  placeholder="Enter chart description..."
                  rows={3}
                />
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                onClick={() => setEditingChart(null)}
              >
                Cancel
              </Button>
              <Button
                onClick={handleUpdateChart}
                disabled={!editTitle.trim()}
              >
                Update Chart
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}; 