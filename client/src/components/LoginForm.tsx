import { useState } from "react";
import { Eye, EyeOff, Lock, User, Shield, Database, TrendingUp, BarChart3, LayoutDashboard, MessageSquare, Target, Lightbulb } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/contexts/AuthContext";
import { useToast } from "@/hooks/use-toast";
import { useLogin } from "@/hooks/useApi";
import { UserInfo } from "@/types/api";

interface LoginFormProps {
  onLogin: (username: string, password: string) => void;
}

export const LoginForm = ({ onLogin }: LoginFormProps) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const { login } = useAuth();
  const { toast } = useToast();
  const loginMutation = useLogin();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!username.trim() || !password.trim()) {
      toast({
        title: "Fields Required",
        description: "Please enter both username and password",
        variant: "destructive",
      });
      return;
    }

    try {
      const result = await loginMutation.mutateAsync({
        username,
        password,
      });

      // Login to auth context
      login(result.access_token, {
        user_id: result.user_id,
        role: result.role as UserInfo['role'],
        region: result.region,
      });

      toast({
        title: "Login Successful",
        description: `Welcome back, ${username}! Role: ${result.role}`,
      });

      onLogin(username, password);

    } catch (error) {
      toast({
        title: "Login Failed",
        description: error instanceof Error ? error.message : "Please check your credentials and try again",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 via-background to-primary/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 lg:py-16">
        {/* Header Section */}
        <div className="text-center space-y-2 sm:space-y-3 mb-8 sm:mb-12">
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-primary">SafetyConnect</h1>
          <div className="w-16 sm:w-20 lg:w-24 h-1 bg-primary mx-auto rounded-full"></div>
          <p className="text-sm sm:text-base lg:text-lg text-muted-foreground max-w-2xl mx-auto px-4">
            Advanced safety data analysis and business intelligence platform
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-16 items-start max-w-7xl mx-auto min-h-[calc(100vh-20rem)]">
          {/* Left Side - Feature Cards */}
          <div className="space-y-6 sm:space-y-8 order-2 lg:order-1">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
              <Card className="relative overflow-hidden border-0 shadow-lg hover:shadow-xl transition-all duration-300">
                <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary"></div>
                <CardContent className="p-3 sm:p-4">
                  <div className="flex items-start space-x-2 sm:space-x-3">
                    <div className="p-1.5 sm:p-2 bg-primary/10 rounded-lg flex-shrink-0">
                      <Shield className="h-4 w-4 sm:h-5 sm:w-5 text-primary" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <h3 className="text-xs sm:text-sm font-semibold text-foreground mb-1">Safety Analytics</h3>
                      <p className="text-xs text-muted-foreground leading-relaxed">Comprehensive safety data analysis and insights</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="relative overflow-hidden border-0 shadow-lg hover:shadow-xl transition-all duration-300">
                <div className="absolute left-0 top-0 bottom-0 w-1 bg-red-500"></div>
                <CardContent className="p-3 sm:p-4">
                  <div className="flex items-start space-x-2 sm:space-x-3">
                    <div className="p-1.5 sm:p-2 bg-red-500/10 rounded-lg flex-shrink-0">
                      <Database className="h-4 w-4 sm:h-5 sm:w-5 text-red-500" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <h3 className="text-xs sm:text-sm font-semibold text-foreground mb-1">Data Intelligence</h3>
                      <p className="text-xs text-muted-foreground leading-relaxed">AI-powered insights and recommendations</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="relative overflow-hidden border-0 shadow-lg hover:shadow-xl transition-all duration-300">
                <div className="absolute left-0 top-0 bottom-0 w-1 bg-green-500"></div>
                <CardContent className="p-3 sm:p-4">
                  <div className="flex items-start space-x-2 sm:space-x-3">
                    <div className="p-1.5 sm:p-2 bg-green-500/10 rounded-lg flex-shrink-0">
                      <LayoutDashboard className="h-4 w-4 sm:h-5 sm:w-5 text-green-500" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <h3 className="text-xs sm:text-sm font-semibold text-foreground mb-1">Interactive Dashboard</h3>
                      <p className="text-xs text-muted-foreground leading-relaxed">Real-time dashboards with interactive charts</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="relative overflow-hidden border-0 shadow-lg hover:shadow-xl transition-all duration-300">
                <div className="absolute left-0 top-0 bottom-0 w-1 bg-purple-500"></div>
                <CardContent className="p-3 sm:p-4">
                  <div className="flex items-start space-x-2 sm:space-x-3">
                    <div className="p-1.5 sm:p-2 bg-purple-500/10 rounded-lg flex-shrink-0">
                      <MessageSquare className="h-4 w-4 sm:h-5 sm:w-5 text-purple-500" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <h3 className="text-xs sm:text-sm font-semibold text-foreground mb-1">Conversational BI</h3>
                      <p className="text-xs text-muted-foreground leading-relaxed">Ask questions in natural language</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="relative overflow-hidden border-0 shadow-lg hover:shadow-xl transition-all duration-300">
                <div className="absolute left-0 top-0 bottom-0 w-1 bg-orange-500"></div>
                <CardContent className="p-3 sm:p-4">
                  <div className="flex items-start space-x-2 sm:space-x-3">
                    <div className="p-1.5 sm:p-2 bg-orange-500/10 rounded-lg flex-shrink-0">
                      <Target className="h-4 w-4 sm:h-5 sm:w-5 text-orange-500" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <h3 className="text-xs sm:text-sm font-semibold text-foreground mb-1">AI Insights</h3>
                      <p className="text-xs text-muted-foreground leading-relaxed">Automated insights and recommendations</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="relative overflow-hidden border-0 shadow-lg hover:shadow-xl transition-all duration-300">
                <div className="absolute left-0 top-0 bottom-0 w-1 bg-pink-500"></div>
                <CardContent className="p-3 sm:p-4">
                  <div className="flex items-start space-x-2 sm:space-x-3">
                    <div className="p-1.5 sm:p-2 bg-pink-500/10 rounded-lg flex-shrink-0">
                      <Lightbulb className="h-4 w-4 sm:h-5 sm:w-5 text-pink-500" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <h3 className="text-xs sm:text-sm font-semibold text-foreground mb-1">Smart Alerts</h3>
                      <p className="text-xs text-muted-foreground leading-relaxed">Proactive notifications and alerts</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="text-center space-y-2 sm:space-y-3 px-4">
              <h2 className="text-xl sm:text-2xl font-semibold text-foreground">Why SafetyConnect?</h2>
              <p className="text-sm sm:text-base text-muted-foreground max-w-md mx-auto leading-relaxed">
                Transform your safety data into actionable insights with our advanced analytics platform. 
                Get real-time visibility into safety performance across your organization with AI-powered 
                insights, interactive dashboards, and conversational BI capabilities.
              </p>
            </div>
          </div>

          {/* Right Side - Login Form */}
          <div className="flex justify-center lg:sticky lg:top-20 order-1 lg:order-2 lg:self-start">
            <div className="w-full max-w-sm sm:max-w-md">
            <Card className="shadow-2xl border-0 bg-white/80 backdrop-blur-sm">
              <CardHeader className="space-y-3 pb-4 sm:pb-6">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 sm:w-10 sm:h-10 bg-primary/10 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Shield className="h-4 w-4 sm:h-5 sm:w-5 text-primary" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <CardTitle className="text-lg sm:text-xl font-bold text-foreground">
                      Welcome Back
                    </CardTitle>
                    <CardDescription className="text-muted-foreground text-sm">
                      Sign in to access your safety insights dashboard
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4 sm:space-y-6">
                <form onSubmit={handleSubmit} className="space-y-3 sm:space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="username" className="text-sm font-medium text-foreground">
                      Username
                    </Label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="username"
                        type="text"
                        placeholder="Enter your username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        className="pl-10 h-10 sm:h-11 transition-all duration-200 focus:ring-2 focus:ring-primary/20 border-primary/20"
                        required
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="password" className="text-sm font-medium text-foreground">
                      Password
                    </Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="password"
                        type={showPassword ? "text" : "password"}
                        placeholder="Enter your password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="pl-10 pr-10 h-10 sm:h-11 transition-all duration-200 focus:ring-2 focus:ring-primary/20 border-primary/20"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                      >
                        {showPassword ? (
                          <EyeOff className="h-4 w-4" />
                        ) : (
                          <Eye className="h-4 w-4" />
                        )}
                      </button>
                    </div>
                  </div>

                  <Button
                    type="submit"
                    className="w-full bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70 text-primary-foreground shadow-lg hover:shadow-primary/25 transition-all duration-200 py-2.5 sm:py-3 h-10 sm:h-11 text-sm sm:text-base font-medium"
                    disabled={loginMutation.isPending}
                  >
                    {loginMutation.isPending ? (
                      <div className="flex items-center space-x-2">
                        <div className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin"></div>
                        <span>Signing in...</span>
                      </div>
                    ) : (
                      "Sign In"
                    )}
                  </Button>
                </form>

                <div className="text-center">
                  <p className="text-xs text-muted-foreground">
                    Secure access to your safety analytics platform
                  </p>
                </div>
              </CardContent>
            </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};