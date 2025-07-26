// API Service Functions

import { httpClient } from '@/lib/http-client';
import {
  LoginRequest,
  LoginResponse,
  S3FileIngestRequest,
  DataIngestResponse,
  AIInsightsResponse,
  InsightFeedback,
  DashboardResponse,
  DataHealthResponse,
  FileUploadResponse,
  SchemaType,
  ChatRequest,
  ChatResponse,
  HealthReport,
  AssessmentSummary,
  LLMOptimization,
} from '@/types/api';

// Authentication API
export const authApi = {
  // Generate test token using server endpoint
  generateTestToken: async (userId: string, role: string = "safety_head", region?: string): Promise<LoginResponse> => {
    const params = new URLSearchParams({
      user_id: userId,
      role: role,
    });

    if (region) {
      params.append('region', region);
    }

    const response = await httpClient.post<Record<string, unknown>>(`/api/v1/auth/generate-test-token?${params.toString()}`, undefined, false);

    return {
      access_token: response.token as string,
      token_type: "Bearer",
      user_id: response.user_id as string,
      role: response.role as string,
      region: response.region as string,
    };
  },

  // Simple login using username/password to generate token
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    // Use username as user_id and default role as safety_head
    return authApi.generateTestToken(credentials.username, "safety_head");
  },

  // Validate current token
  validateToken: async (): Promise<boolean> => {
    try {
      // Try to make an authenticated request to check token validity
      await httpClient.get('/api/v1/dashboard/srs');
      return true;
    } catch {
      return false;
    }
  },

  logout: () => {
    httpClient.clearToken();
  },
};

// Data Ingestion API
export const dataIngestApi = {
  // Ingest Excel file from S3
  ingestFile: async (request: S3FileIngestRequest): Promise<DataIngestResponse> => {
    return httpClient.post<DataIngestResponse>('/api/v1/dataingest', request);
  },
};

// AI Insights API
export const aiInsightsApi = {
  // Generate insights for specific schema type
  generateInsights: async (schemaType: SchemaType): Promise<AIInsightsResponse> => {
    return httpClient.post<AIInsightsResponse>(`/api/v1/insights/generate/${schemaType}`);
  },

  // Generate more insights for specific schema type
  generateMoreInsights: async (schemaType: SchemaType, count: number = 5): Promise<AIInsightsResponse> => {
    return httpClient.post<AIInsightsResponse>(`/api/v1/insights/generate-more/${schemaType}?count=${count}`);
  },

  // Generate unified insights from all data sources
  generateUnifiedInsights: async (): Promise<AIInsightsResponse> => {
    return httpClient.post<AIInsightsResponse>('/api/v1/insights/generate-unified');
  },

  // Submit feedback for insights
  submitFeedback: async (feedback: InsightFeedback): Promise<void> => {
    return httpClient.post<void>('/api/v1/insights/feedback', feedback);
  },
};

// Dashboard API
export const dashboardApi = {
  // Get dashboard data for specific schema type
  getDashboardData: async (
    schemaType: SchemaType,
    startDate?: string,
    endDate?: string
  ): Promise<DashboardResponse> => {
    let endpoint = `/api/v1/dashboard/${schemaType}`;
    
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    if (params.toString()) {
      endpoint += `?${params.toString()}`;
    }
    
    return httpClient.get<DashboardResponse>(endpoint);
  },
};

// Data Health API
export const dataHealthApi = {
  // Get LLM-enhanced data health assessment
  getDataHealthLLM: async (schemaType: SchemaType): Promise<{ health_report: HealthReport; assessment_summary: AssessmentSummary; llm_optimization: LLMOptimization }> => {
    return httpClient.get(`/api/v1/data-health-llm/${schemaType}`);
  },

  // Get comprehensive data health assessment
  getDataHealth: async (schemaType: SchemaType): Promise<DataHealthResponse> => {
    return httpClient.get<DataHealthResponse>(`/api/v1/data-health/${schemaType}`);
  },

  // Get data health service status
  getDataHealthStatus: async (): Promise<{ status_code: number; message: string; body: Record<string, unknown> }> => {
    return httpClient.get('/api/v1/data-health/status');
  },
};

// S3 File Upload API
export const s3Api = {
  // Get presigned URL for file upload
  getUploadUrl: async (): Promise<FileUploadResponse> => {
    return httpClient.get<FileUploadResponse>('/s3/generate-presigned-url', false);
  },

  // Upload file directly to S3 using presigned URL and fields
  uploadFile: async (url: string, fields: Record<string, string>, file: File): Promise<void> => {
    const formData = new FormData();

    // Add all the fields from presigned URL first
    Object.entries(fields).forEach(([key, value]) => {
      formData.append(key, value);
    });

    // Add the file last
    formData.append('file', file);

    const response = await fetch(url, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`S3 upload failed: ${response.status}`);
    }
  },
};

// Combined file upload and processing workflow
export const fileWorkflowApi = {
  // Complete file upload and processing workflow
  uploadAndProcess: async (file: File, onProgress?: (progress: number) => void): Promise<DataIngestResponse> => {
    try {
      onProgress?.(10);

      // Step 1: Get presigned URL
      const uploadResponse = await s3Api.getUploadUrl();
      onProgress?.(25);

      // Step 2: Upload file to S3
      await s3Api.uploadFile(uploadResponse.url, uploadResponse.fields, file);
      onProgress?.(60);

      // Step 3: Process the uploaded file
      const processResponse = await dataIngestApi.ingestFile({
        s3_key: uploadResponse.s3_key,
        filename: file.name,
      });

      onProgress?.(100);
      return processResponse;
    } catch (error) {
      throw new Error(`File upload and processing failed: ${error instanceof Error ? error.message : error}`);
    }
  },
};

// Chat API
export const chatApi = {
  // Send chat message
  sendMessage: async (question: string): Promise<{ text: string; visualizationData?: Record<string, unknown> }> => {
    const request: ChatRequest = { question };
    console.log('Sending chat request:', request);
    const response = await httpClient.post<{ final_answer: string; visualization_data?: Record<string, unknown> }>('/api/v1/conversationBI/chat-question', request);
    console.log('Received chat response:', response);
    return {
      text: response.final_answer,
      visualizationData: response.visualization_data
    };
  },
};

// Health check
export const healthApi = {
  // Check if server is running
  checkHealth: async () => {
    return httpClient.get('/', false);
  },
};
