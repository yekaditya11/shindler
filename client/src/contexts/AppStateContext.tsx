import React, { createContext, useContext, useState, ReactNode } from 'react';
import { SchemaType, DataIngestResponse } from '@/types/api';

interface AppStateContextType {
  uploadedFiles: File[];
  detectedSchema: SchemaType | null;
  setUploadedFiles: (files: File[]) => void;
  setDetectedSchema: (schema: SchemaType | null) => void;
  updateFromUploadResults: (files: File[], results?: DataIngestResponse[]) => void;
  clearState: () => void;
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

  const updateFromUploadResults = (files: File[], results?: DataIngestResponse[]) => {
    setUploadedFiles(files);

    // Extract the most recent schema type for dashboard display
    if (results && results.length > 0) {
      const lastResult = results[results.length - 1];
      if (lastResult.schema_type) {
        setDetectedSchema(lastResult.schema_type as SchemaType);
      }
    }
  };

  const clearState = () => {
    setUploadedFiles([]);
    setDetectedSchema(null);
  };

  const value: AppStateContextType = {
    uploadedFiles,
    detectedSchema,
    setUploadedFiles,
    setDetectedSchema,
    updateFromUploadResults,
    clearState,
  };

  return (
    <AppStateContext.Provider value={value}>
      {children}
    </AppStateContext.Provider>
  );
}; 