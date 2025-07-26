import { useState } from "react";
import { BarChart3, Filter, TrendingUp, FileText, Clock, Target } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";

interface DashboardProps {
  data: {
    totalDocuments: number;
    insightsGenerated: number;
    accuracyScore: number;
    processingTime: string;
  };
}

export const Dashboard = ({ data }: DashboardProps) => {
  const [dateFilter, setDateFilter] = useState("7d");
  const [categoryFilter, setCategoryFilter] = useState("all");

  const kpis = [
    {
      title: "Total Documents",
      value: data.totalDocuments,
      icon: FileText,
      trend: "+12%",
      color: "text-primary"
    },
    {
      title: "Insights Generated",
      value: data.insightsGenerated,
      icon: TrendingUp,
      trend: "+23%",
      color: "text-success"
    },
    {
      title: "Accuracy Score",
      value: `${data.accuracyScore}%`,
      icon: Target,
      trend: "+5%",
      color: "text-primary-light"
    },
    {
      title: "Avg Processing Time",
      value: data.processingTime,
      icon: Clock,
      trend: "-8%",
      color: "text-primary-lighter"
    }
  ];

  const chartData = [
    { name: "Financial", value: 35, color: "hsl(212 81% 19%)" },
    { name: "Legal", value: 28, color: "hsl(212 65% 35%)" },
    { name: "Technical", value: 22, color: "hsl(212 45% 55%)" },
    { name: "Business", value: 15, color: "hsl(212 100% 85%)" }
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-primary" />
          <h2 className="text-2xl font-bold">Analytics Dashboard</h2>
        </div>
        <div className="flex items-center gap-3">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <Select value={dateFilter} onValueChange={setDateFilter}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1d">1 Day</SelectItem>
              <SelectItem value="7d">7 Days</SelectItem>
              <SelectItem value="30d">30 Days</SelectItem>
              <SelectItem value="90d">90 Days</SelectItem>
            </SelectContent>
          </Select>
          <Select value={categoryFilter} onValueChange={setCategoryFilter}>
            <SelectTrigger className="w-36">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Categories</SelectItem>
              <SelectItem value="financial">Financial</SelectItem>
              <SelectItem value="legal">Legal</SelectItem>
              <SelectItem value="technical">Technical</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map((kpi, index) => (
          <Card key={index} className="shadow-card hover:shadow-hover transition-all duration-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">{kpi.title}</p>
                  <p className="text-2xl font-bold">{kpi.value}</p>
                  <Badge variant="secondary" className="bg-success/20 text-success text-xs">
                    {kpi.trend} vs last period
                  </Badge>
                </div>
                <div className={`p-3 rounded-lg bg-gradient-card`}>
                  <kpi.icon className={`h-6 w-6 ${kpi.color}`} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="shadow-card">
          <CardHeader>
            <CardTitle>Document Categories</CardTitle>
            <CardDescription>Distribution of analyzed documents by category</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {chartData.map((item, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div 
                      className="w-3 h-3 rounded-full" 
                      style={{ backgroundColor: item.color }}
                    ></div>
                    <span className="text-sm font-medium">{item.name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-2 bg-muted rounded-full overflow-hidden">
                      <div 
                        className="h-full rounded-full transition-all duration-500"
                        style={{ 
                          width: `${item.value}%`,
                          backgroundColor: item.color 
                        }}
                      ></div>
                    </div>
                    <span className="text-sm text-muted-foreground w-8">{item.value}%</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-card">
          <CardHeader>
            <CardTitle>Processing Timeline</CardTitle>
            <CardDescription>Recent document analysis activity</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { time: "2 mins ago", action: "Financial report analyzed", status: "completed" },
                { time: "15 mins ago", action: "Legal contract processed", status: "completed" },
                { time: "1 hour ago", action: "Technical document uploaded", status: "processing" },
                { time: "2 hours ago", action: "Business plan reviewed", status: "completed" }
              ].map((activity, index) => (
                <div key={index} className="flex items-center gap-3 p-3 border rounded-lg bg-gradient-card">
                  <div className={`w-2 h-2 rounded-full ${
                    activity.status === 'completed' ? 'bg-success' : 'bg-yellow-500'
                  }`}></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">{activity.action}</p>
                    <p className="text-xs text-muted-foreground">{activity.time}</p>
                  </div>
                  <Badge 
                    variant={activity.status === 'completed' ? 'default' : 'secondary'}
                    className={activity.status === 'completed' ? 'bg-success/20 text-success' : ''}
                  >
                    {activity.status}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card className="shadow-card">
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Common tasks and operations</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-3">
            <Button variant="outline" className="hover:bg-primary/5">
              Export Report
            </Button>
            <Button variant="outline" className="hover:bg-primary/5">
              Schedule Analysis
            </Button>
            <Button variant="outline" className="hover:bg-primary/5">
              Configure Alerts
            </Button>
            <Button variant="outline" className="hover:bg-primary/5">
              Download Data
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};