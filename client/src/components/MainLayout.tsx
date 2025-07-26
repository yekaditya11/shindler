import { useState, useEffect } from "react";
import { CleanDashboard } from "./CleanDashboard";
import { DocumentUpload } from "./DocumentUpload";
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";
import { SimpleBulletInsights } from "./SimpleBulletInsights";
import { AIDashboard } from "./AIDashboard";
import { useAuth } from "@/contexts/AuthContext";
import { useDashboardData, useGenerateInsights, useGenerateMoreInsights, useInsightFeedback } from "@/hooks/useApi";
import { SchemaType, AIInsight, DataIngestResponse } from "@/types/api";
import { useToast } from "@/hooks/use-toast";
import { format, subDays } from "date-fns";

interface MainLayoutProps {
  onLogout: () => void;
  onUploadMore: () => void;
  currentUser: string;
  detectedSchema?: SchemaType | null;
  showUploadPage?: boolean;
  onUploadComplete?: (files: File[], results?: DataIngestResponse[]) => void;
}

export const MainLayout = ({ 
  onLogout, 
  onUploadMore, 
  currentUser, 
  detectedSchema,
  showUploadPage = false,
  onUploadComplete
}: MainLayoutProps) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [aiInsightsOpen, setAIInsightsOpen] = useState(false);
  const [currentView, setCurrentView] = useState<'main' | 'ai-dashboard'>('main');
  const [selectedSchema, setSelectedSchema] = useState<SchemaType>(detectedSchema || "srs");

  // Date filtering state - default to last 1 year
  const [startDate, setStartDate] = useState<string>(() =>
    format(subDays(new Date(), 365), 'yyyy-MM-dd')
  );
  const [endDate, setEndDate] = useState<string>(() =>
    format(new Date(), 'yyyy-MM-dd')
  );

  const { user, logout } = useAuth();

  // Update selected schema when detected schema changes
  useEffect(() => {
    if (detectedSchema) {
      setSelectedSchema(detectedSchema);
    }
  }, [detectedSchema]);

  // Clear insights when schema changes
  useEffect(() => {
    console.log('Schema changed to:', selectedSchema, 'clearing insights');
    setInsights([]);
  }, [selectedSchema]);

  // Fetch real dashboard data with date filtering
  const { data: dashboardData, isLoading: dashboardLoading, error: dashboardError } =
    useDashboardData(selectedSchema, startDate, endDate);

  // AI Insights state and hooks
  const [insights, setInsights] = useState<AIInsight[]>([]);
  const [isGeneratingInsights, setIsGeneratingInsights] = useState(false);
  const [isGeneratingMoreInsights, setIsGeneratingMoreInsights] = useState(false);
  const { toast } = useToast();

  // AI Insights API hooks
  const generateInsightsMutation = useGenerateInsights();
  const generateMoreInsightsMutation = useGenerateMoreInsights();
  const submitFeedbackMutation = useInsightFeedback();

  // Debug current insights state
  useEffect(() => {
    console.log('Current insights state:', insights.length, 'insights');
    if (insights.length > 0) {
      console.log('First insight:', insights[0]);
    }
  }, [insights]);

  const handleLogout = () => {
    logout();
    onLogout();
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const toggleAIInsights = () => {
    setAIInsightsOpen(!aiInsightsOpen);
    // Auto-generate insights when opening if none exist
    if (!aiInsightsOpen && insights.length === 0 && !isGeneratingInsights) {
      handleGenerateInsights();
    }
  };

  const toggleAIDashboard = () => {
    setCurrentView(currentView === 'ai-dashboard' ? 'main' : 'ai-dashboard');
  };

  // Generate insights for current schema
  const handleGenerateInsights = async () => {
    if (isGeneratingInsights) return;

    setIsGeneratingInsights(true);
    try {
      console.log('Generating insights for schema:', selectedSchema);
      console.log('User authenticated:', !!user);

      const response = await generateInsightsMutation.mutateAsync(selectedSchema);
      console.log('API Response:', response);

      // Handle both response formats
      const insightsData = response.body || response;
      
      if (insightsData.insights && Array.isArray(insightsData.insights)) {
        const formattedInsights: AIInsight[] = insightsData.insights.map((text: string, index: number) => ({
          id: `insight-${Date.now()}-${index}`,
          text: text,
          timestamp: new Date().toISOString(),
          liked: false,
          disliked: false
        }));

        setInsights(formattedInsights);
        console.log('Insights set successfully:', formattedInsights.length);
      } else {
        console.error('Invalid insights response format:', insightsData);
        toast({
          title: "Error",
          description: "Invalid insights response format",
          variant: "destructive",
        });
      }
    } catch (error: unknown) {
      console.error('Error generating insights:', error);
      const errorMessage = error instanceof Error ? error.message : "Failed to generate insights";
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsGeneratingInsights(false);
    }
  };

  // Generate more insights
  const handleGenerateMoreInsights = async () => {
    if (isGeneratingMoreInsights) return;

    setIsGeneratingMoreInsights(true);
    try {
      const response = await generateMoreInsightsMutation.mutateAsync({ schemaType: selectedSchema, count: 5 });
      
      // Handle both response formats
      const insightsData = response.body || response;
      
      if (insightsData.insights && Array.isArray(insightsData.insights)) {
        const newInsights: AIInsight[] = insightsData.insights.map((text: string, index: number) => ({
          id: `insight-${Date.now()}-${index}`,
          text: text,
          timestamp: new Date().toISOString(),
          liked: false,
          disliked: false
        }));

        setInsights(prev => [...prev, ...newInsights]);
        toast({
          title: "More Insights Generated",
          description: `Generated ${newInsights.length} additional insights`,
        });
      }
    } catch (error: unknown) {
      console.error('Error generating more insights:', error);
      const errorMessage = error instanceof Error ? error.message : "Failed to generate more insights";
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsGeneratingMoreInsights(false);
    }
  };

  // Handle insight feedback (like/dislike)
  const handleInsightAction = async (id: string, action: 'like' | 'dislike' | 'delete') => {
    const insight = insights.find(i => i.id === id);
    if (!insight) return;

    if (action === 'delete') {
      setInsights(prev => prev.filter(i => i.id !== id));
      toast({
        title: "Insight Removed",
        description: "Insight has been removed from the list",
      });
      return;
    }

    // Toggle the action state
    const currentState = insight[action === 'like' ? 'liked' : 'disliked'];
    const newState = !currentState;

    try {
      // Only submit feedback to backend if we're turning it on
      if (newState) {
        await submitFeedbackMutation.mutateAsync({
          schema_type: selectedSchema,
          insight_text: insight.text,
          feedback: action
        });
      }

      // Update local state to show feedback
      setInsights(prev => prev.map(i =>
        i.id === id
          ? {
              ...i,
              liked: action === 'like' ? newState : false,
              disliked: action === 'dislike' ? newState : false
            }
          : i
      ));

      // Show appropriate toast message
      if (newState) {
        toast({
          title: "Feedback Submitted",
          description: `Thank you for your ${action === 'like' ? 'positive' : 'negative'} feedback`,
        });
      } else {
        toast({
          title: "Feedback Removed",
          description: `${action === 'like' ? 'Like' : 'Dislike'} feedback has been removed`,
        });
      }
    } catch (error: unknown) {
      console.error('Error submitting feedback:', error);
      const errorMessage = error instanceof Error ? error.message : "Failed to submit feedback";
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    }
  };

  // Date change handler
  const handleDateRangeChange = (start: string, end: string) => {
    setStartDate(start);
    setEndDate(end);
  };

  return (
    <div className="min-h-screen bg-background">
      <Header
        currentUser={user?.user_id || currentUser}
        onLogout={handleLogout}
        onUploadMore={onUploadMore}
        onToggleSidebar={toggleSidebar}
        sidebarOpen={sidebarOpen}
        showUploadPage={showUploadPage}
      />

      <div className="flex min-h-[calc(100vh-3.5rem)] md:min-h-[calc(100vh-4rem)]">
        <Sidebar 
          isOpen={sidebarOpen} 
          currentView={currentView}
          onSwitchToMain={!showUploadPage ? () => setCurrentView('main') : undefined}
          onOpenAIDashboard={!showUploadPage ? toggleAIDashboard : undefined} 
        />

        {/* Main Content */}
        <main className="flex-1 p-3 md:p-6 lg:p-8">
          <div className="max-w-7xl mx-auto">
            {showUploadPage ? (
              <DocumentUpload onUploadComplete={onUploadComplete!} />
            ) : currentView === 'ai-dashboard' ? (
              <AIDashboard />
            ) : (
              <CleanDashboard
                data={dashboardData?.dashboard_data}
                isLoading={dashboardLoading}
                error={dashboardError}
                onToggleAI={toggleAIInsights}
                aiInsightsOpen={aiInsightsOpen}
                onSchemaChange={setSelectedSchema}
                selectedSchema={selectedSchema}
                startDate={startDate}
                endDate={endDate}
                onDateRangeChange={handleDateRangeChange}
              />
            )}
          </div>
        </main>
      </div>

      {/* AI Insights Modal */}
      <SimpleBulletInsights
        insights={insights.map(insight => ({
          id: insight.id,
          text: insight.text,
          liked: insight.liked,
          disliked: insight.disliked
        }))}
        isOpen={aiInsightsOpen}
        onClose={() => setAIInsightsOpen(false)}
        isLoading={isGeneratingInsights}
        isGeneratingMore={isGeneratingMoreInsights}
        onInsightAction={handleInsightAction}
        onGenerateMore={handleGenerateMoreInsights}
      />


    </div>
  );
};