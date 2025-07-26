import React, { createContext, useContext, useState, ReactNode } from 'react';
import { SchemaType, DataIngestResponse, HealthReport } from '@/types/api';
import { dataHealthApi } from '@/services/api';

interface AppStateContextType {
  uploadedFiles: File[];
  detectedSchema: SchemaType | null;
  healthReport: HealthReport | null;
  isHealthReportLoading: boolean;
  setUploadedFiles: (files: File[]) => void;
  setDetectedSchema: (schema: SchemaType | null) => void;
  setHealthReport: (report: HealthReport | null) => void;
  updateFromUploadResults: (files: File[], results?: DataIngestResponse[]) => void;
  clearState: () => void;
  refreshHealthReport: () => Promise<void>;
}

const AppStateContext = createContext<AppStateContextType | undefined>(undefined);

export const useAppState = () => {
  const context = useContext(AppStateContext);
  if (context === undefined) {
    throw new Error('useAppState must be used within an AppStateProvider');
  }
  return context;
};

interface AppStateProviderProps {
  children: ReactNode;
}

export const AppStateProvider: React.FC<AppStateProviderProps> = ({ children }) => {
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [detectedSchema, setDetectedSchema] = useState<SchemaType | null>(null);
  const [healthReport, setHealthReport] = useState<HealthReport | null>(null);
  const [isHealthReportLoading, setIsHealthReportLoading] = useState(false);

  const triggerHealthAnalysis = async (schema: SchemaType) => {
    try {
      setIsHealthReportLoading(true);
      console.log(`🔍 Triggering automatic health analysis for schema: ${schema}`);
      
      const response = await dataHealthApi.getDataHealthLLM(schema);
      setHealthReport(response.health_report);
      
      console.log(`✅ Health analysis completed for schema: ${schema}`);
    } catch (error) {
      console.error('❌ Background health analysis failed:', error);
      // Don't show error to user since this is background operation
    } finally {
      setIsHealthReportLoading(false);
    }
  };

  const updateFromUploadResults = (files: File[], results?: DataIngestResponse[]) => {
    setUploadedFiles(files);

    // Extract the most recent schema type for dashboard display
    if (results && results.length > 0) {
      const lastResult = results[results.length - 1];
      if (lastResult.schema_type) {
        const newSchema = lastResult.schema_type as SchemaType;
        setDetectedSchema(newSchema);
        
        // Clear old health report when schema changes
        setHealthReport(null);
        
        // Trigger health analysis in background
        setTimeout(() => {
          triggerHealthAnalysis(newSchema);
        }, 1000); // Small delay to let the data ingestion complete properly
      }
    }
  };

  const refreshHealthReport = async () => {
    if (!detectedSchema) return;
    await triggerHealthAnalysis(detectedSchema);
  };

  const clearState = () => {
    setUploadedFiles([]);
    setDetectedSchema(null);
    setHealthReport(null);
    setIsHealthReportLoading(false);
  };

  const value: AppStateContextType = {
    uploadedFiles,
    detectedSchema,
    healthReport,
    isHealthReportLoading,
    setUploadedFiles,
    setDetectedSchema,
    setHealthReport,
    updateFromUploadResults,
    clearState,
    refreshHealthReport,
  };

  return (
    <AppStateContext.Provider value={value}>
      {children}
    </AppStateContext.Provider>
  );
}; 