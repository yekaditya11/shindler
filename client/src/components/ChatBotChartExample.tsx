import React from 'react';
import { ChatBotChart } from './ChatBotChart';

// Sample chart data for demonstration
const sampleBarChartData = {
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  xAxis: {
    type: 'category',
    data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      name: 'Events',
      type: 'bar',
      data: [770, 1511, 1647, 1814, 2328, 1910],
      itemStyle: {
        color: '#1e3a8a'
      }
    }
  ]
};

const samplePieChartData = {
  tooltip: {
    trigger: 'item'
  },
  legend: {
    orient: 'vertical',
    left: 'left'
  },
  series: [
    {
      name: 'Event Types',
      type: 'pie',
      radius: '50%',
      data: [
        { value: 1048, name: 'Safety Incidents' },
        { value: 735, name: 'Near Misses' },
        { value: 580, name: 'Equipment Issues' },
        { value: 484, name: 'Training Needs' }
      ],
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }
  ]
};

export const ChatBotChartExample: React.FC = () => {
  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold mb-6">ChatBotChart Width Examples</h1>
      
      {/* Full width chart */}
      <div>
        <h2 className="text-lg font-semibold mb-3">Full Width Chart (100%)</h2>
        <ChatBotChart 
          chartData={sampleBarChartData}
          width="100%"
          height={300}
        />
      </div>

      {/* Fixed width chart */}
      <div>
        <h2 className="text-lg font-semibold mb-3">Fixed Width Chart (400px)</h2>
        <ChatBotChart 
          chartData={sampleBarChartData}
          width={400}
          height={250}
        />
      </div>

      {/* Medium width chart */}
      <div>
        <h2 className="text-lg font-semibold mb-3">Medium Width Chart (60%)</h2>
        <ChatBotChart 
          chartData={samplePieChartData}
          width="60%"
          height={280}
        />
      </div>

      {/* Small width chart */}
      <div>
        <h2 className="text-lg font-semibold mb-3">Small Width Chart (300px)</h2>
        <ChatBotChart 
          chartData={samplePieChartData}
          width={300}
          height={200}
        />
      </div>

      {/* Responsive width with custom styling */}
      <div>
        <h2 className="text-lg font-semibold mb-3">Custom Styled Chart</h2>
        <div className="bg-gray-50 p-4 rounded-lg">
          <ChatBotChart 
            chartData={sampleBarChartData}
            width="80%"
            height={250}
            className="shadow-lg"
          />
        </div>
      </div>
    </div>
  );
}; 