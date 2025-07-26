import React from 'react';
import { ChatBot, ChatBotFloatingIcon } from './ChatBot';
import { ChatBotChart } from './ChatBotChart';
import { AIDashboard } from './AIDashboard';
import { httpClient } from "@/lib/http-client";

// Sample ECharts configuration for testing
const sampleChartData = {
  tooltip: {
    trigger: "item"
  },
  legend: {
    data: ["Reported Events"]
  },
  series: [
    {
      name: "Reported Events",
      type: "pie",
      radius: "50%",
      data: [
        {
          value: 9161,
          name: "Reported Events"
        }
      ],
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: "rgba(0, 0, 0, 0.5)"
        }
      }
    }
  ]
};

export const ChatBotTest: React.FC = () => {
  const [isOpen, setIsOpen] = React.useState(false);
  const [aiDashboardOpen, setAiDashboardOpen] = React.useState(false);

  const handleSendMessage = async (message: string): Promise<{ text: string; visualizationData?: Record<string, unknown> }> => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Return sample response with chart data
    return {
      text: `You asked: "${message}". Here's a sample chart showing 9,161 reported events in the EI Tech dataset.`,
      visualizationData: sampleChartData
    };
  };

  const handleSaveToDashboard = async (chartData: Record<string, unknown>, title: string, description: string): Promise<void> => {
    try {
      const response = await httpClient.post('/api/v1/saved-charts/save-chart', {
        chart_data: chartData,
        title: title,
        description: description,
      });
      
      // Response should already be parsed by httpClient
      if (!response) {
        throw new Error('Failed to save chart');
      }
    } catch (error) {
      console.error('Error saving chart:', error);
      throw error;
    }
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">ChatBot Chart Integration Test</h1>
      <p className="mb-4">This is a test component to demonstrate chart visualization in the chatbot.</p>
      
      {/* Example of standalone ChatBotChart with custom width */}
      <div className="mb-6">
        <h2 className="text-lg font-semibold mb-3">Standalone Chart Example (Custom Width)</h2>
        <ChatBotChart 
          chartData={sampleChartData}
          width={350}
          height={200}
        />
      </div>
      
      <div className="mb-4">
        <button
          onClick={() => setAiDashboardOpen(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Open AI Dashboard
        </button>
      </div>
      
      <ChatBotFloatingIcon onToggle={() => setIsOpen(!isOpen)} isOpen={isOpen} />
      <ChatBot
        isOpen={isOpen}
        onToggle={() => setIsOpen(!isOpen)}
        onSendMessage={handleSendMessage}
        onSaveToDashboard={handleSaveToDashboard}
      />

      <AIDashboard
        isOpen={aiDashboardOpen}
        onClose={() => setAiDashboardOpen(false)}
      />
    </div>
  );
}; 