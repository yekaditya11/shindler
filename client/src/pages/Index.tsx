import { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import { LoginForm } from "@/components/LoginForm";
import { DocumentUpload } from "@/components/DocumentUpload";
import { MainLayout } from "@/components/MainLayout";
import { Header } from "@/components/Header";
import { SchemaType, DataIngestResponse } from "@/types/api";
import { useAuth } from "@/contexts/AuthContext";
import { useAppState } from "@/contexts/AppStateContext";

type AppState = "login" | "upload" | "main";

const Index = () => {
  const [appState, setAppState] = useState<AppState>("login");
  const [currentUser, setCurrentUser] = useState<string>("");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const { user } = useAuth();
  const { uploadedFiles, detectedSchema, updateFromUploadResults, clearState } = useAppState();

  // Check if user is logged in and accessing dashboard route
  useEffect(() => {
    if (user && location.pathname === "/dashboard") {
      setCurrentUser(user.user_id);
      setAppState("main");
    }
  }, [user, location.pathname]);

  const handleLogin = (username: string, password: string) => {
    // Simple validation - in real app, this would be API call
    if (username.trim() && password.trim()) {
      setCurrentUser(username);
      setAppState("upload");
    }
  };

  const handleUploadComplete = (files: File[], results?: DataIngestResponse[]) => {
    updateFromUploadResults(files, results);
    setAppState("main");
  };

  const handleLogout = () => {
    setAppState("login");
    clearState();
    setCurrentUser("");
  };

  const handleUploadMore = () => {
    setAppState("upload");
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  // Login page with header but no sidebar
  if (appState === "login") {
    return (
      <div className="min-h-screen bg-background">
        <Header
          currentUser=""
          onLogout={() => {}}
          onUploadMore={() => {}}
          onToggleSidebar={toggleSidebar}
          sidebarOpen={false}
          showUploadPage={false}
        />
        <LoginForm onLogin={handleLogin} />
      </div>
    );
  }

  // Use MainLayout for both upload and main states to maintain consistent header and sidebar
  return (
    <MainLayout
      onLogout={handleLogout}
      onUploadMore={handleUploadMore}
      currentUser={currentUser}
      detectedSchema={detectedSchema}
      showUploadPage={appState === "upload"}
      onUploadComplete={handleUploadComplete}
    />
  );
};

export default Index;
