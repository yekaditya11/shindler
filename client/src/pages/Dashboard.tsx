import { useAuth } from "@/contexts/AuthContext";
import { useAppState } from "@/contexts/AppStateContext";
import { MainLayout } from "@/components/MainLayout";
import { Navigate } from "react-router-dom";
import { DataIngestResponse } from "@/types/api";

const Dashboard = () => {
  const { user } = useAuth();
  const { uploadedFiles, detectedSchema } = useAppState();

  // If user is not logged in, redirect to login
  if (!user) {
    return <Navigate to="/" replace />;
  }

  const handleLogout = () => {
    // This will be handled by the parent component
    window.location.href = "/";
  };

  const handleUploadMore = () => {
    // Navigate to upload page
    window.location.href = "/";
  };

  const handleUploadComplete = (files: File[], results?: DataIngestResponse[]) => {
    // This will be handled by the context
  };

  return (
    <MainLayout
      onLogout={handleLogout}
      onUploadMore={handleUploadMore}
      currentUser={user.user_id}
      detectedSchema={detectedSchema}
      showUploadPage={false}
      onUploadComplete={handleUploadComplete}
    />
  );
};

export default Dashboard; 